# Validation

## Current baseline

### Functional checks

- cases: 12
- errors: 0
- insufficient responses: 1
- pass_rate: 1.0
- citation_rate: 1.0
- avg_latency_s: 5.429
- retrieved_expected_avg: 1.0
- cited_expected_avg: 1.0

### Hostile-input checks

- cases: 7
- passed: 7
- failed: 0
- pass_rate: 1.0

## Reproduce

```bash
make eval
make adversarial
```

## Scope notes

- current snapshot under the reference local configuration
- baseline applies to bounded source material
- not a claim of universal robustness outside that operating scope
