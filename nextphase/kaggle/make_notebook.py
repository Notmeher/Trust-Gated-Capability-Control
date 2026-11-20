#!/usr/bin/env python
"""Generate the Kaggle notebook that produces the open-weight (Qwen) data for the enhancement phase.

    uv run python nextphase/kaggle/make_notebook.py

The notebook is a thin driver (same pattern as the TALA robustness notebooks): it installs what
Kaggle lacks, clones this repository (branch ``enhancement``) with the ``github_token`` secret, and
runs the experiment modules with ``TGCC_LOCAL_BACKEND=transformers`` so open-weight models are
served by ``tgcc.nextphase.hf_backend``. Every generation is written to ``cache/llm/<model>/`` in the
same format as the API cache, so the experiments run unchanged (and offline) on a laptop afterwards.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "tgcc-openweight.ipynb"
REPO = "Notmeher/Trust-Gated-Capability-Control"
BRANCH = "enhancement"


def md(src: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": src.strip("\n")}


def code(src: str, tag: str) -> dict:
    return {"cell_type": "code", "metadata": {"tags": [tag]}, "execution_count": None,
            "outputs": [], "source": src.strip("\n")}


CELLS = [
    md(f"""
# TGCC enhancement: open-weight models (Qwen) on Kaggle (GPU T4 x2)

This notebook produces the open-weight data used by the IEEE revision experiments:

| step | what | used by |
|---|---|---|
| QA banks | Qwen3-4B, Qwen3-8B, Qwen2.5-7B answer 300 TriviaQA + 300 MedMCQA evaluation questions (honest and sleeper prompts) and a 120-question honest pilot per dataset | N25 (more model families and datasets), N22, N29 |
| Critic | Qwen3-8B as the reference-free judge, with and without the prompt-injection payloads | N23 (critic poisoning) |
| Evaluator | Qwen3-8B as the tone/focus evaluator on real failure replies, with and without payloads | N33 (evaluator poisoning) |

All generations are greedy (temperature 0), identical prompts to the API models, written to
`cache/llm/<model>/` in the API cache format. Download `tgcc_openweight_outputs.zip` from the Output
tab and unzip it at the repository root; the experiments then run offline.

**Before running**
1. *Settings -> Accelerator*: **GPU T4 x2**. *Settings -> Internet*: **on**.
2. *Add-ons -> Secrets*: attach `github_token` (read access to `{REPO}`).
3. Optional: attach `HF_TOKEN` (only speeds up downloads; the Qwen models are not gated).
4. *Run all* (or *Save Version -> Save & Run All*). Expected time: about 3-4 h; each step prints its duration.
"""),
    code('''
import importlib, os, subprocess, sys, time
from importlib import metadata
from pathlib import Path

os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

# Pin every compiled package Kaggle already ships, so pip never swaps one under the running kernel.
_PIN = ['numpy', 'scipy', 'torch', 'torchvision', 'torchaudio', 'pandas', 'scikit-learn', 'pyarrow', 'safetensors']

def _v(pkg):
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return None

_constraints = Path('/kaggle/working/.pip_constraints.txt')
_constraints.write_text('\\n'.join(f'{p}=={_v(p)}' for p in _PIN if _v(p)) + '\\n')
_need = []
if tuple(int(x) for x in (_v('transformers') or '0.0').split('.')[:2]) < (4, 51):   # Qwen3 needs >= 4.51
    _need.append('transformers>=4.51')
for _p in ('accelerate', 'python-dotenv', 'anthropic', 'openai', 'tenacity', 'pydantic', 'rich', 'tqdm', 'matplotlib'):
    if not _v(_p):
        _need.append(_p)
if _need:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '-c', str(_constraints), *_need])
    importlib.invalidate_caches()
print('installed:', _need or 'nothing')
print('transformers', _v('transformers'), '| torch', _v('torch'), '| accelerate', _v('accelerate'))
''', "install"),
    md("## 1. GPUs"),
    code('''
!nvidia-smi --query-gpu=index,name,memory.total --format=csv
import torch
assert torch.cuda.is_available(), 'No GPU visible: Settings -> Accelerator -> GPU T4 x2.'
print('GPUs:', torch.cuda.device_count())
''', "gpu"),
    md(f"## 2. Clone `{REPO}` @ `{BRANCH}` with the `github_token` secret\n\nThe token is never written to disk."),
    code(f'''
import shutil
from kaggle_secrets import UserSecretsClient

REPO = '{REPO}'
BRANCH = '{BRANCH}'
REPO_DIR = Path('/kaggle/working/tgcc')

def _secret(name):
    try:
        return UserSecretsClient().get_secret(name).strip()
    except Exception:
        return os.environ.get(name.upper(), '').strip()

token = _secret('github_token')
assert token, "Attach the github_token secret: Add-ons -> Secrets."
shutil.rmtree(REPO_DIR, ignore_errors=True)
res = subprocess.run(['git', 'clone', '--depth', '1', '--branch', BRANCH,
                      f'https://x-access-token:{{token}}@github.com/{{REPO}}.git', str(REPO_DIR)],
                     capture_output=True, text=True, env={{**os.environ, 'GIT_TERMINAL_PROMPT': '0'}})
if res.returncode:
    raise RuntimeError('git clone failed:\\n' + res.stderr.replace(token, '***'))
del token
hf = _secret('HF_TOKEN')
if hf:
    os.environ['HF_TOKEN'] = hf
print(subprocess.run(['git', '-C', str(REPO_DIR), 'log', '-1', '--format=%h %s'], capture_output=True, text=True).stdout)

ENV = {{**os.environ, 'PYTHONPATH': str(REPO_DIR / 'src'), 'TGCC_LOCAL_BACKEND': 'transformers',
       'TGCC_HF_BATCH': '32', 'TGCC_BUDGET_USD': '0'}}   # budget 0: an API call here would be a bug

def run(*args):
    """Run a module of the repo with the transformers backend; streams its output."""
    t0 = time.time()
    p = subprocess.Popen([sys.executable, '-m', *args], cwd=REPO_DIR, env=ENV,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        print(line, end='')
    if p.wait():
        raise RuntimeError(f'{{args}} failed')
    print(f'-- {{args[0]}} done in {{(time.time() - t0) / 60:.1f}} min')
''', "clone"),
    md("""
## 3. Settings

- `MODELS`: open-weight providers (keys of `tgcc.models.OPEN_MODELS`).
- `DTYPE`: `''` = float16 (the T4 has no bfloat16). If the smoke test shows garbage or NaN errors for a
  model, set `'float32'` (fits for Qwen3-4B; the 7-8B models then need both GPUs and run slower).
"""),
    code('''
MODELS = ['qwen3-4b', 'qwen3-8b', 'qwen2.5-7b']
DATASETS = ['triviaqa', 'medmcqa']
JUDGE = 'qwen3-8b'
DTYPE = ''
ENV['TGCC_HF_DTYPE'] = DTYPE
''', "settings"),
    md("## 4. Smoke test: 8 TriviaQA + 4 MedMCQA questions per model (these generations are reused by the run)"),
    code('''
SMOKE = r"""
import sys
from tgcc.models import LLMClient
from tgcc.data_qa import HONEST_SYSTEM_PROMPT
from tgcc.nextphase.responses import dataset_split, item_prompt, item_match, chat
from tgcc.probes import parse_answer
c = LLMClient(sys.argv[1])
for ds, n in (("triviaqa", 8), ("medmcqa", 4)):
    items, _ = dataset_split(ds, 300)
    ok = 0
    for it in items[:n]:
        r = chat(c, item_prompt(it), HONEST_SYSTEM_PROMPT)
        ok += item_match(parse_answer(r.text), it)
        print(f"  [{ds}] {r.text[:110]!r}")
    print(f"{sys.argv[1]} {ds}: {ok}/{n} correct")
"""
(REPO_DIR / '_smoke.py').write_text(SMOKE)
for m in MODELS:
    t0 = time.time()
    p = subprocess.run([sys.executable, '_smoke.py', m], cwd=REPO_DIR, env=ENV, capture_output=True, text=True)
    print(p.stdout[-3000:] or p.stderr[-3000:])
    print(f'{m}: {time.time() - t0:.0f}s (includes download and loading)')
''', "smoke"),
    md("## 5. QA banks (N25): every model x dataset"),
    code('''
for m in MODELS:
    for ds in DATASETS:
        run('tgcc.nextphase.responses', '--providers', m, '--dataset', ds, '--workers', '64')
''', "banks"),
    md("## 6. Critic poisoning (N23): Qwen3-8B as the judge"),
    code('''
run('tgcc.nextphase.n23_critic_poisoning', '--collect', JUDGE, '--collect-only', '--workers', '64')
''', "judge"),
    md("## 7. Evaluator poisoning (N33): Qwen3-8B as the tone/focus evaluator"),
    code('''
run('tgcc.nextphase.n33_evaluator_poisoning', '--collect', JUDGE, '--collect-only', '--workers', '64')
''', "evaluator"),
    md("## Save\n\nDownload `tgcc_openweight_outputs.zip` and unzip it at the repository root."),
    code('''
import zipfile
out = Path('/kaggle/working/tgcc_openweight_outputs.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for m in MODELS:
        for f in (REPO_DIR / 'cache' / 'llm' / m).rglob('*.json'):
            z.write(f, f.relative_to(REPO_DIR))
    for f in (REPO_DIR / 'nextphase' / '_data').glob('*'):
        if any(m in f.name for m in MODELS) or f.name.startswith('medmcqa_'):
            z.write(f, f.relative_to(REPO_DIR))
print(out, f'{out.stat().st_size / 1e6:.1f} MB')
for n in sorted(zipfile.ZipFile(out).namelist()):
    if not n.startswith('cache/'):
        print(' ', n)
''', "save"),
]


def main() -> None:
    nb = {"cells": CELLS, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                                      "name": "python3"},
                                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    OUT.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
