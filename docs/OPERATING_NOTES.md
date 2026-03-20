# Operating Notes

## Standard sequence

### 1. Grounded query

Example query:

`When do the high-risk AI rules fully apply under the EU AI Act?`

Expected behavior:
- explicit separation where ambiguity exists
- citation-backed output
- source traceability

### 2. Structured export

Expected output set:
- system card
- risk register
- control mapping
- timeline section
- Markdown export
- JSON export

### 3. Conservative failure behavior

Expected behavior:
- low-confidence requests do not invent unsupported statements
- out-of-scope requests terminate conservatively
- outputs remain bounded by indexed source material
