from __future__ import annotations

from typing import Any, Sequence

import httpx


def _raise_for_status_with_details(r: httpx.Response) -> None:
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        detail: str
        try:
            j = r.json()
            detail = str(j)
        except Exception:
            detail = r.text

        # Avoid dumping extremely large payloads
        if len(detail) > 4000:
            detail = detail[:4000] + " ...<truncated>..."

        raise RuntimeError(
            f"LM Studio HTTP {r.status_code} for {r.request.method} {r.request.url}\n"
            f"Response body:\n{detail}"
        ) from e


class LMStudioClient:
    def __init__(self, base_url: str, timeout_s: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout_s, headers={"Accept": "application/json"})

    def close(self) -> None:
        self._client.close()

    def models(self) -> list[str]:
        r = self._client.get(f"{self.base_url}/models")
        _raise_for_status_with_details(r)
        data = r.json()
        out: list[str] = []
        for m in data.get("data", []):
            if isinstance(m, dict) and isinstance(m.get("id"), str):
                out.append(m["id"])
        return out

    def embeddings(self, model: str, inputs: Sequence[str]) -> list[list[float]]:
        payload = {"model": model, "input": list(inputs)}
        r = self._client.post(f"{self.base_url}/embeddings", json=payload)
        _raise_for_status_with_details(r)
        data = r.json()

        out: list[list[float]] = []
        for item in data.get("data", []):
            emb = item.get("embedding")
            if not isinstance(emb, list):
                raise RuntimeError(f"Unexpected embeddings response shape: {item!r}")
            out.append([float(x) for x in emb])

        if len(out) != len(inputs):
            raise RuntimeError(f"Embeddings count mismatch: expected {len(inputs)}, got {len(out)}")
        return out

    def chat(
        self,
        model: str,
        messages: Sequence[dict[str, Any]],
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str:
        payload = {
            "model": model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = self._client.post(f"{self.base_url}/chat/completions", json=payload)
        _raise_for_status_with_details(r)
        data = r.json()

        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"No choices returned from chat/completions. Full response: {data!r}")

        msg = (choices[0] or {}).get("message") or {}
        content = msg.get("content")
        if content is None:
            return ""
        if not isinstance(content, str):
            raise RuntimeError(f"Unexpected content type in chat response: {type(content)}")
        return content
