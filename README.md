# AuditKit

Grounded answers, control mapping, and audit-ready exports from bounded source material.

## Scope

AuditKit is a local-first review surface for bounded document sets. It answers with citations, produces structured exports, and fails closed on low-confidence or out-of-scope requests.

## Fastest inspection path

```bash
make smoke
```

This checks syntax and validates shipped examples without requiring a local runtime.

## Fastest local run

See `docs/RUNTIME_SETUP.md`, then run:

```bash
make doctor
make index
make app
```

## Included in this repository

- runnable interface
- CLI entrypoints
- bounded reference source set
- bounded evaluation set
- hostile-input checks
- sample inputs and outputs
- executable tests
- architecture, design, failure-mode, validation, and security notes

## Validation snapshot

- functional checks: 12/12 pass, 0 errors
- hostile-input checks: 7/7 pass

## Repository map

- `app/` operator interface
- `src/` implementation
- `scripts/` local validation helpers
- `docs/` architecture, runtime, security, validation, and design notes
- `examples/` representative inputs and outputs
- `data/raw/` bounded reference source set
- `data/eval/` bounded evaluation set

## Constraint

Outputs are structured operational artifacts, not legal advice.
