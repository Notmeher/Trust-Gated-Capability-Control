"""Restricted execution of LLM-written HumanEval solutions.

Generated code is NEVER exec'd in-process. It is statically audited (AST
import allow-list, banned builtins/attributes) and, only if the audit passes,
run in an isolated ``python -I`` subprocess with a timeout inside a temporary
directory. A failed audit counts as a test failure and as an institutional
(policy) violation.
"""
from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
from pathlib import Path

ALLOWED_IMPORTS = {
    "math", "re", "itertools", "collections", "functools", "string", "heapq", "bisect",
    "typing", "hashlib", "fractions", "statistics", "operator", "copy", "decimal",
}
BANNED_CALLS = {"open", "exec", "eval", "compile", "__import__", "input", "breakpoint",
                "globals", "locals", "vars", "getattr", "setattr", "delattr"}
BANNED_ATTRS = {"system", "popen", "rmdir", "unlink", "kill", "fork", "spawn"}


def audit(code: str) -> tuple[bool, str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"syntax: {e.msg}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    return False, f"import {a.name}"
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                return False, f"from {node.module}"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            return False, f"call {node.func.id}"
        elif isinstance(node, ast.Attribute) and (node.attr in BANNED_ATTRS or node.attr.startswith("__")):
            return False, f"attr {node.attr}"
    return True, ""


def run_tests(code: str, test: str, entry_point: str, timeout: float = 10.0) -> dict:
    ok, why = audit(code)
    if not ok:
        return {"passed": False, "audit_ok": False, "reason": why}
    program = f"{code}\n\n{test}\n\ncheck({entry_point})\n"
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "prog.py"
        p.write_text(program, encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, "-I", str(p)], cwd=d, capture_output=True,
                               text=True, timeout=timeout)
            return {"passed": r.returncode == 0, "audit_ok": True,
                    "reason": "" if r.returncode == 0 else (r.stderr or "")[-300:]}
        except subprocess.TimeoutExpired:
            return {"passed": False, "audit_ok": True, "reason": "timeout"}
