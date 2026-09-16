from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from .contracts import AuditRequest


class RequestError(ValueError):
    pass


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def _mapping(loader: UniqueSafeLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise RequestError(f"duplicate frontmatter key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False
    raise RequestError("DEBUG must be true/false or 1/0")


def parse_request(path: Path, debug_override: bool | None = None) -> AuditRequest:
    path = path.resolve()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RequestError(f"cannot read request: {exc}") from exc
    if not text.startswith("---\n"):
        raise RequestError("request must start with YAML frontmatter delimited by ---")
    try:
        frontmatter, body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise RequestError("frontmatter closing delimiter is missing") from exc
    try:
        data = yaml.load(frontmatter, Loader=UniqueSafeLoader)
    except (yaml.YAMLError, RequestError) as exc:
        raise RequestError(f"invalid frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise RequestError("frontmatter must be a mapping")
    legacy = {"quorum_threshold", "reviewer_mode", "audit_target", "audit_type"} & data.keys()
    if legacy:
        raise RequestError(f"legacy field(s) {', '.join(sorted(legacy))} are unsupported; migrate to the v1 request format")
    base = path.parent
    for name in ("target", "spec", "output_dir"):
        if data.get(name) is not None:
            candidate = Path(data[name])
            data[name] = candidate if candidate.is_absolute() else (base / candidate).resolve()
    for name in ("sources", "inputs", "discovery_runs"):
        if data.get(name) is not None:
            if not isinstance(data[name], list):
                raise RequestError(f"{name} must be a list")
            data[name] = [(Path(p) if Path(p).is_absolute() else (base / p).resolve()) for p in data[name]]
    if data.get("output_dir") is None:
        data["output_dir"] = (base / "audits").resolve()
    if debug_override is not None:
        data["debug"] = debug_override
    elif data.get("debug") is None and "DEBUG" in os.environ:
        data["debug"] = parse_bool(os.environ["DEBUG"])
    elif data.get("debug") is None:
        data["debug"] = True
    data.update(task=body.strip(), request_path=path)
    try:
        return AuditRequest.model_validate(data)
    except Exception as exc:
        raise RequestError(str(exc)) from exc
