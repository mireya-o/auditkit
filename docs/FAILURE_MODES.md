# Failure Modes

## Retrieval miss

### Symptom
Relevant material is present but not surfaced in the top-ranked context.

### Current mitigation
- bounded source material
- multi-query retrieval where needed
- evaluation coverage tracking

## Ambiguous question handling

### Symptom
A single question maps to multiple valid interpretations.

### Current mitigation
- explicit ambiguity branching
- citation-backed split answers for distinct interpretations

## Structured export degradation

### Symptom
Structured output may arrive malformed or incomplete.

### Current mitigation
- deterministic repair
- schema validation
- section-level patching

## Runtime instability

### Symptom
Large prompt budgets can degrade latency or reliability.

### Current mitigation
- conservative prompt budgets
- bounded context windows
- low-friction rerun path

## Hostile input

### Symptom
Input attempts to override format, reveal internals, or force unsupported output.

### Current mitigation
- request sanitization
- attack-only rejection
- hostile-input checks
