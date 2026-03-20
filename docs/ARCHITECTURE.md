# Architecture

## Operating shape

- local-only runtime boundary
- bounded document intake
- indexed source material
- grounded answer generation
- structured export validation

## Processing path

1. intake
2. normalization
3. segmentation
4. indexing
5. retrieval
6. answer shaping
7. export validation

## Control points

- request sanitization
- attack-only request rejection
- low-relevance fail-closed behavior
- citation enforcement
- deterministic source rendering
- structured-output repair and schema validation
- partial-output patching for incomplete structured generations
- local-only network posture

## Constraints

- bounded source material
- no cloud dependency required
- outputs are limited by indexed material
- low-confidence and out-of-scope requests fail closed
