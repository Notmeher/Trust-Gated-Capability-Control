"""Capability tokens for TGCC grants: issuance, enforcement and revocation (used by N24).

A grant is materialised as a short-lived, signed capability token:

    token = base64(payload) "." base64(HMAC-SHA256(key, payload))
    payload = {agent, capability, step, epoch, exp}

* The controller (issuer) signs a token for (agent, capability) only when the grant rule holds.
* A tool gateway executes an action only if the token's signature is valid, it has not expired
  (``exp`` is a wall-clock deadline), and its ``epoch`` is not older than the agent's revocation
  epoch at that gateway.
* Revocation bumps the agent's epoch at the issuer and broadcasts it to every gateway, so a token
  issued before the revocation is rejected immediately even if it has not expired.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import threading
import time
from dataclasses import dataclass, field


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


@dataclass
class Issuer:
    key: bytes = field(default_factory=lambda: os.urandom(32))
    ttl_s: float = 2.0
    epochs: dict[str, int] = field(default_factory=dict)

    def issue(self, agent: str, capability: str, step: int) -> str:
        payload = json.dumps({"a": agent, "c": capability, "s": step, "e": self.epochs.get(agent, 0),
                              "x": time.time() + self.ttl_s}, separators=(",", ":")).encode()
        sig = hmac.new(self.key, payload, hashlib.sha256).digest()
        return f"{_b64(payload)}.{_b64(sig)}"

    def revoke(self, agent: str) -> int:
        self.epochs[agent] = self.epochs.get(agent, 0) + 1
        return self.epochs[agent]


@dataclass
class Gateway:
    key: bytes
    epochs: dict[str, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def on_revoke(self, agent: str, epoch: int) -> None:
        with self._lock:
            if epoch > self.epochs.get(agent, 0):
                self.epochs[agent] = epoch

    def authorize(self, token: str, agent: str, capability: str) -> bool:
        try:
            p64, s64 = token.split(".")
            payload = _unb64(p64)
            if not hmac.compare_digest(hmac.new(self.key, payload, hashlib.sha256).digest(), _unb64(s64)):
                return False
            d = json.loads(payload)
        except (ValueError, json.JSONDecodeError):
            return False
        return (d["a"] == agent and d["c"] == capability and d["x"] >= time.time()
                and d["e"] >= self.epochs.get(agent, 0))


@dataclass
class Bus:
    """In-process broadcast of revocations to every registered gateway."""
    gateways: list[Gateway] = field(default_factory=list)

    def publish(self, agent: str, epoch: int) -> None:
        for g in self.gateways:
            g.on_revoke(agent, epoch)
