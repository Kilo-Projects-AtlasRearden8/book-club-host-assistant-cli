"""Client for generating discussion prompts via an OpenAI-compatible endpoint.

Default endpoint is a local Ollama instance (http://localhost:11434/v1), so the
tool works local-first with no API keys required. The endpoint, model, and
timeout are all configurable.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class EndpointError(Exception):
    """Raised when the LLM endpoint cannot be reached or returns an error."""


class LLMClient:
    """Minimal OpenAI-compatible chat completion client over urllib."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model: str = "llama3",
        timeout: float = 30.0,
        api_key: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.api_key = api_key

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        body = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/chat/completions"
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise EndpointError(
                f"Endpoint returned HTTP {exc.code}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise EndpointError(f"Unable to reach endpoint {url}: {exc}") from exc
        except OSError as exc:
            raise EndpointError(f"Unable to reach endpoint {url}: {exc}") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EndpointError(f"Endpoint returned invalid JSON: {raw!r}") from exc

        try:
            choices = data["choices"]
            message = choices[0]["message"]
            return message["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise EndpointError(f"Unexpected endpoint response shape: {data!r}") from exc


class DiscussionPromptGenerator:
    """Generates discussion prompts for a book, with a local template fallback."""

    FALLBACK_PROMPTS = [
        "What stood out to you most in this book, and why?",
        "Which character did you relate to the most, and what did you learn from them?",
        "What was the central theme, and how did it show up in the story?",
        "Were there any parts that surprised or challenged you?",
        "How does this book compare to others the group has read?",
        "What is one question you would ask the author if they were here?",
        "Would you recommend this book to a friend? Why or why not?",
    ]

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def generate(
        self,
        title: str,
        author: str,
        *,
        theme: str | None = None,
        count: int = 5,
        use_fallback: bool = True,
    ) -> list[str]:
        context = f"'{title}' by {author}"
        if theme:
            context += f", with a focus on {theme}"
        system = (
            "You are a warm, beginner-friendly book club host. "
            "Write short, open-ended discussion questions that anyone can answer, "
            "no literary degree required. Keep the tone friendly and encouraging."
        )
        user = (
            f"Generate {count} discussion prompts for a book club meeting about {context}. "
            "Return a simple numbered list, one question per line, nothing else."
        )

        try:
            text = self.client.chat(
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.7,
            )
            prompts = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]
            # Strip leading numbering like "1. "
            cleaned: list[str] = []
            for prompt in prompts:
                stripped = prompt
                if stripped[0].isdigit():
                    stripped = stripped.split(".", 1)[-1].strip() if "." in stripped else stripped
                if stripped:
                    cleaned.append(stripped)
            if cleaned:
                return cleaned[:count]
        except EndpointError:
            if not use_fallback:
                raise

        fallback = list(self.FALLBACK_PROMPTS)
        if theme:
            fallback.insert(0, f"How did the theme of {theme} show up in the book?")
        return fallback[:count]
