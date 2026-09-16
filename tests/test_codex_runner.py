from consensus_audit.contracts import InvestigatorReport
from consensus_audit.runners.codex import CodexRunner


def test_output_schema_requires_every_property_for_strict_runner_format() -> None:
    schema = CodexRunner._strict_schema(InvestigatorReport.model_json_schema())
    assert set(schema["required"]) == set(schema["properties"])
    check = schema["$defs"]["Check"]
    assert set(check["required"]) == set(check["properties"])
    assert check["additionalProperties"] is False
