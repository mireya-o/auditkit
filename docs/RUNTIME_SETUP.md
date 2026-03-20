# Runtime Setup

AuditKit expects a local OpenAI-compatible endpoint on:

`http://127.0.0.1:1234/v1`

## Reference setup used for validation

The reference local setup used during validation was:

- runtime: LM Studio
- endpoint: `127.0.0.1:1234/v1`
- response profile: `openai/gpt-oss-20b`
- vector profile: `text-embedding-nomic-embed-text-v1.5-embedding`

Any local runtime exposing compatible `models`, `chat/completions`, and `embeddings` endpoints can be used instead.

## Verification

The endpoint should respond here:

```bash
curl -s http://127.0.0.1:1234/v1/models
```

## Environment

Copy overrides only if needed:

```bash
cp .env.example .env
```

## Local run sequence

```bash
make doctor
make index
make app
```

## Notes

- `make doctor` verifies the endpoint, configured profiles, source files, and local index state.
- `make index` builds the local index from `data/raw/`.
- `make app` launches the interface.
