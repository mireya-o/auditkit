# Design Decisions

## 1. Local-first execution

The default operating mode minimizes unnecessary external exposure. Runtime, indexing, and exports can remain local.

## 2. Bounded source material

The system is exercised against a reviewable document set rather than an open-ended external surface.

## 3. Grounded outputs

Answers remain tied to retrieved material and expose source traceability directly.

## 4. Structured exports

The export path favors machine-readable and reviewable artifacts over free-form output alone.

## 5. Conservative failure mode

Low-confidence and out-of-scope requests terminate conservatively rather than fabricate unsupported claims.

## 6. Hostile-input validation

The repository includes hostile-input checks because correctness without abuse resistance is incomplete.
