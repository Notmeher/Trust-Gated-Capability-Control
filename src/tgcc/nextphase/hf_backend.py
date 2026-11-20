"""Batched transformers backend for open-weight models (used on Kaggle GPUs).

``LLMClient`` routes open-weight providers here when ``TGCC_LOCAL_BACKEND=transformers``.
Experiment drivers call ``chat`` from many threads (as they do for the APIs); a single
worker thread collects queued requests and decodes them in batches, so the drivers
need no changes. Decoding is greedy at temperature 0 and sampled otherwise.
"""
from __future__ import annotations

import os
import queue
import threading
import time
from concurrent.futures import Future
from typing import Optional

_ENGINES: dict[str, "BatchedHFEngine"] = {}
_LOCK = threading.Lock()


def get_engine(model_id: str) -> "BatchedHFEngine":
    with _LOCK:
        if model_id not in _ENGINES:
            # One model in GPU memory at a time.
            for other in list(_ENGINES):
                _ENGINES.pop(other).close()
            _ENGINES[model_id] = BatchedHFEngine(model_id)
        return _ENGINES[model_id]


class BatchedHFEngine:
    def __init__(self, model_id: str, max_batch: Optional[int] = None, wait_s: float = 0.05) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_id = model_id
        self.max_batch = max_batch or int(os.getenv("TGCC_HF_BATCH", "32"))
        self.wait_s = wait_s
        dtype = {"float32": torch.float32, "bfloat16": torch.bfloat16}.get(
            os.getenv("TGCC_HF_DTYPE", ""), torch.float16 if torch.cuda.is_available() else torch.float32)
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        kw = dict(device_map="auto" if torch.cuda.is_available() else None)
        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype, **kw)
        except TypeError:  # transformers < 4.56 only knows torch_dtype
            self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype, **kw)
        self.model.eval()
        self._torch = torch
        self._q: "queue.Queue[tuple[str, str, int, Optional[float], Future]]" = queue.Queue()
        self._stop = False
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    # ---------------------------------------------------------------- API
    def generate(self, system: str, prompt: str, max_tokens: int,
                 temperature: Optional[float]) -> tuple[str, dict]:
        fut: Future = Future()
        self._q.put((system, prompt, max_tokens, temperature, fut))
        return fut.result()

    def close(self) -> None:
        self._stop = True
        self._worker.join(timeout=5)
        del self.model
        if self._torch.cuda.is_available():
            self._torch.cuda.empty_cache()

    # ----------------------------------------------------------- internals
    def _render(self, system: str, prompt: str) -> str:
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
        # enable_thinking=False turns off Qwen3's hidden reasoning; other templates ignore it.
        return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                            enable_thinking=False)

    def _loop(self) -> None:
        while not self._stop:
            try:
                first = self._q.get(timeout=0.2)
            except queue.Empty:
                continue
            batch = [first]
            deadline = time.time() + self.wait_s
            while len(batch) < self.max_batch and time.time() < deadline:
                try:
                    batch.append(self._q.get(timeout=max(0.0, deadline - time.time())))
                except queue.Empty:
                    break
            # Requests with different sampling settings are decoded separately.
            groups: dict[tuple[bool, float], list] = {}
            for req in batch:
                t = req[3] or 0.0
                groups.setdefault((t > 0, round(t, 3)), []).append(req)
            for (sample, temp), reqs in groups.items():
                try:
                    self._run(reqs, sample, temp)
                except Exception as e:  # noqa: BLE001 - surface to every waiting caller
                    for r in reqs:
                        if not r[4].done():
                            r[4].set_exception(e)

    def _run(self, reqs: list, sample: bool, temp: float) -> None:
        torch = self._torch
        texts = [self._render(r[0], r[1]) for r in reqs]
        enc = self.tok(texts, return_tensors="pt", padding=True).to(self.model.device)
        max_new = max(r[2] for r in reqs)
        t0 = time.perf_counter()
        with torch.inference_mode():
            out = self.model.generate(
                **enc, max_new_tokens=max_new, do_sample=sample,
                temperature=temp if sample else None, top_p=1.0 if sample else None,
                top_k=None, pad_token_id=self.tok.pad_token_id)
        dt = (time.perf_counter() - t0) * 1000.0 / len(reqs)
        n_in = enc["input_ids"].shape[1]
        for i, r in enumerate(reqs):
            gen = out[i, n_in:]
            # Each request is truncated to its own max_tokens budget.
            gen = gen[: r[2]]
            text = self.tok.decode(gen, skip_special_tokens=True).strip()
            n_out = int((gen != self.tok.pad_token_id).sum())
            r[4].set_result((text, {
                "input_tokens": int(enc["attention_mask"][i].sum()),
                "output_tokens": n_out,
                "batch_size": len(reqs),
                "gpu_ms_per_item": dt,
            }))
