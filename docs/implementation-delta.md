# Implementation delta from `1959f6f`

| Baseline | Required correction | Smallest implementation | Evidence |
| --- | --- | --- | --- |
| Instructions only | Executable common path | Python package and CLI | end-to-end fixture |
| Quorum-centered synthesis | Evidence before counts | structured reconciliation/accounting | scorer tests |
| Prompt-only separation with shared files | Portable enforced boundary | fresh nonpersistent calls, no tools, and controller-embedded bounded packets | adapter argument and live smoke tests |
| Parent-chat synthesis | Fresh reconciler | sealed packet and separate invocation | call-order test |
| Deletable reports | Retained authority | digest-tracked run bundle | verification test |
| Mixed 1–10 confidence | Coarse scoped policy | pure `pilot-v1` scorer | adversarial fixtures |
| Configurable quorum/focused modes | Comparable v1 first passes | strict schema; legacy errors | parser tests |
| No import lineage | Preserve originals | byte copies, per-document extraction, aliases | import tests |
| Discovery exports treated as plain testimony | Reconcile finalized Discovery outputs without repeating Discovery | first-class `discovery_runs` verified-opinion importer, dedicated consensus scoring, no underlying run-artifact import or follow-up investigation | real-export validation and application tests |
| Rejected or minority proposals could depress Discovery consensus confidence | Score only the adopted consensus direction | controller-enforced strict-majority and supported-disposition invariants for decisive Discovery claims | semantic retry tests for rejected and one-report decisive claims |
| No finite runtime | Bounded follow-up | round/question/attempt limits | application invariants |

Deterministic fixtures validate machinery, not model correctness. Codex, Claude Code, and Cursor can host the installed skill and invoke the same uv-managed CLI. Codex is the only managed execution adapter in v1. Empirical calibration, additional execution adapters, recursive reconciler ensembles, runtime-command evidence, and interrupted-session resumption remain deferred.

## Resolved operational limitation

On 2026-09-16 with `codex-cli 0.154.0-alpha.6.2`, managed Codex invocations failed before analysis because `CodexRunner` set `-C` to an intentionally ephemeral, non-Git workspace without also passing `--skip-git-repo-check`. Changing the caller's working directory did not avoid the failure because the subprocess-level `-C` took precedence. The runner now passes `--skip-git-repo-check`, which permits the generated workspace while preserving the existing no-tools, bounded-packet, and `approval_policy="never"` isolation boundary. A regression test asserts the generated command supports a non-Git ephemeral workspace.
