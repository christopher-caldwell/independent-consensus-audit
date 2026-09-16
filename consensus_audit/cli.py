from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from pydantic import ValidationError

from . import __version__
from .application import OperationalError, run_audit
from .contracts import Reconciliation
from .request import RequestError, parse_request
from .runners import create_runner
from .scoring import score
from .storage import atomic_json, load_bundle
from .validation import IntegrityError


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="consensus-audit", description="Run evidence-aware independent audits. Relative paths resolve from the request Markdown file.")
    root.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("guide", help="print the shared agent-neutral operating guide")
    run = sub.add_parser("run", help="run an audit from a Markdown request")
    run.add_argument("request", type=Path); debug = run.add_mutually_exclusive_group()
    debug.add_argument("--debug", action="store_true", default=None); debug.add_argument("--no-debug", action="store_false", dest="debug")
    inspect = sub.add_parser("inspect", help="inspect a retained run without model calls")
    inspect.add_argument("run_dir", type=Path); inspect.add_argument("--verify", action="store_true")
    rescore = sub.add_parser("rescore", help="recalculate confidence without model calls")
    rescore.add_argument("run_dir", type=Path); rescore.add_argument("--policy", required=True, choices=["pilot-v1"])
    return root


def _inspect(path: Path, verify: bool) -> int:
    bundle = load_bundle(path); manifest = bundle.manifest
    final_path = bundle.root / "final.md"; score_path = bundle.root / "score.json"
    score_value = json.loads(score_path.read_text())["final_score"] if score_path.exists() else None
    initial = manifest.get("cohorts", {}).get("initial", {})
    print(f"Status: {manifest.get('status')}\nConfidence: {score_value if score_value is not None else 'null'}")
    print(f"Participation: {initial.get('completed', 0)}/{initial.get('requested_or_supplied', 0)} completed")
    print(f"Final: {final_path if final_path.exists() else 'not committed'}\nRun: {bundle.root}")
    if verify:
        problems = bundle.verify()
        print("Integrity: " + ("verified" if not problems else "FAILED\n- " + "\n- ".join(problems)))
        return 0 if not problems else 4
    return 0


def _rescore(path: Path, policy: str) -> int:
    bundle = load_bundle(path); problems = bundle.verify()
    if problems: raise IntegrityError("; ".join(problems))
    passes = sorted((bundle.root / "reconciliation").glob("pass-*.json"))
    if not passes: raise IntegrityError("no accepted reconciliation exists")
    recon = Reconciliation.model_validate_json(passes[-1].read_text())
    initial = bundle.manifest["cohorts"]["initial"]
    request = json.loads((bundle.root / "request.resolved.json").read_text())
    result = score(recon, requested=initial["requested_or_supplied"], completed=initial["completed"], independence=request["input_independence"])
    destination = bundle.root / "rescoring" / f"{policy}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    atomic_json(destination, result.model_dump())
    print(f"Confidence: {result.final_score}/100 ({policy}, uncalibrated)\nNew score artifact: {destination}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "guide":
            from importlib import resources
            sys.stdout.write(resources.files("consensus_audit").joinpath("prompts/host-guide.md").read_text(encoding="utf-8"))
            return 0
        if args.command == "run":
            print("Resolving request and freezing inputs…", file=sys.stderr)
            request = parse_request(args.request, args.debug)
            run_dir = run_audit(args.request, create_runner(request.runner), args.debug)
            return _inspect(run_dir, False)
        if args.command == "inspect": return _inspect(args.run_dir, args.verify)
        if args.command == "rescore": return _rescore(args.run_dir, args.policy)
    except RequestError as exc:
        print(f"Invalid request: {exc}", file=sys.stderr); return 2
    except (OperationalError, RuntimeError, OSError) as exc:
        print(f"Operational failure: {exc}", file=sys.stderr); return 3
    except (IntegrityError, ValidationError, ValueError, json.JSONDecodeError) as exc:
        print(f"Integrity/schema failure: {exc}", file=sys.stderr); return 4
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
