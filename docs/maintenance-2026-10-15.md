# Public catalog maintenance — 2026-10-15

## Scope

Refresh the existing 16 public skills, add json-validate, log-triage and
markdown-link-check, and synchronize README / registry / catalog. No marketplace
onboarding, private skill synchronization, deployment or merge is included.

## Source checks

- [Gemini lifecycle](https://ai.google.dev/gemini-api/docs/deprecations): checked
  2026-10-15. Retired image preview endpoints removed from runnable instructions;
  default is gemini-nano-banana-2.1 with an environment override.
- [Claude Code skills](https://code.claude.com/docs/en/skills): skill directories
  live under .claude/skills; host capabilities still vary.
- [DuckDB security](https://duckdb.org/docs/stable/operations_manual/securing_duckdb/overview):
  read-only database mode is not a security sandbox; external-access settings
  and configuration locking provide additional controls.

## Changes

- Image API: environment-only key, header authentication, prompt files, MIME-aware
  output, no overwrites, bounded request timeout and no raw provider-body dumps.
- Charts: SQL aggregation before plotting, invalid-row reporting, chronological
  sorting, negative-pie checks and disclosed scatter sampling.
- Database: existing-file URI handling, outer limits, engine read-only modes,
  SQLite authorizer/progress timeout and DuckDB restricted settings.
- Diagram: fix WSL command quoting/conversion, retain editable source, local fonts.
- Writing/evaluation: preserve attribution, actual responsibility, evidence and
  uncertainty; remove unsupported numerical and vendor-size heuristics.
- New workflows: strict JSON/JSONL checker, bounded log triage and local Markdown
  link/anchor inspection with explicit parser/renderer limitations.
- Metadata: reject non-mapping frontmatter and wrong required-field types before
  downstream operations can crash.

## Verification and limits

Implementation was prepared through GitHub tools because the local execution
service was unavailable. Do not treat static source review as a test run.

Required executable checks are documented in README. Existing CI runs metadata
validation only; the regression suite must be run in an approved Python
environment (PyYAML, plus DuckDB to exercise optional integration tests).
Matplotlib rendering, WeasyPrint/native dependencies, draw.io Desktop/WSL
exports and a billed Gemini request require separate environment-specific smoke
checks. No paid API request is necessary for mocked image-parser unit tests.

The PR must record the actual check results and remain unmerged until reviewed.
