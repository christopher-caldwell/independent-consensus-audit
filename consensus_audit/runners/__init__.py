from .base import InvocationResult, Runner
from .codex import CodexRunner

RUNNERS = {"codex": CodexRunner}

def create_runner(name: str):
    try: return RUNNERS[name]()
    except KeyError as exc: raise ValueError(f"unknown runner: {name}") from exc

__all__ = ["InvocationResult", "Runner", "CodexRunner", "create_runner"]
