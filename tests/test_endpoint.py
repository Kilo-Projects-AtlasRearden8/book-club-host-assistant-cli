"""Tests for the LLM endpoint client with a mocked HTTP endpoint."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from book_club.endpoint import LLMClient, EndpointError


class _FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self._body = json.dumps(payload).encode("utf-8")
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class LLMClientTests(unittest.TestCase):
    def _patch_urlopen(self, response):
        return mock.patch(
            "book_club.endpoint.urllib.request.urlopen",
            return_value=response,
        )

    def test_chat_returns_content(self):
        payload = {
            "choices": [{"message": {"role": "assistant", "content": "Why did the chicken cross the road?"}}]
        }
        with self._patch_urlopen(_FakeResponse(payload)):
            client = LLMClient(base_url="http://localhost:11434/v1", model="llama3")
            text = client.chat([{"role": "user", "content": "Say something"}])
        self.assertEqual(text, "Why did the chicken cross the road?")

    def test_chat_sends_expected_payload(self):
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["method"] = req.method
            captured["url"] = req.full_url
            captured["body"] = req.data
            captured["headers"] = dict(req.header_items())
            captured["timeout"] = timeout
            return _FakeResponse({"choices": [{"message": {"content": "ok"}}]})

        with mock.patch("book_club.endpoint.urllib.request.urlopen", side_effect=fake_urlopen):
            client = LLMClient(base_url="http://example.local/v1", model="qwen2.5", timeout=12.5)
            client.chat(
                [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "hi"},
                ],
                temperature=0.2,
                max_tokens=100,
            )

        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["url"], "http://example.local/v1/chat/completions")
        self.assertEqual(captured["timeout"], 12.5)
        body = json.loads(captured["body"])
        self.assertEqual(body["model"], "qwen2.5")
        self.assertEqual(body["temperature"], 0.2)
        self.assertEqual(body["max_tokens"], 100)
        self.assertEqual(len(body["messages"]), 2)
        self.assertNotIn("Authorization", captured["headers"])

    def test_chat_includes_api_key_when_set(self):
        def fake_urlopen(req, timeout=None):
            return _FakeResponse({"choices": [{"message": {"content": "ok"}}]})

        with mock.patch("book_club.endpoint.urllib.request.urlopen", side_effect=fake_urlopen):
            client = LLMClient(api_key="test-key")
            client.chat([{"role": "user", "content": "hi"}])

    def test_http_error_raises_endpoint_error(self):
        import urllib.error

        class _FakeHTTPError(urllib.error.HTTPError):
            def __init__(self, code, body):
                self.code = code
                self._body = body.encode("utf-8")

            def read(self):
                return self._body

        def fake_urlopen(req, timeout=None):
            raise _FakeHTTPError(500, "model not found")

        with mock.patch("book_club.endpoint.urllib.request.urlopen", side_effect=fake_urlopen):
            client = LLMClient()
            with self.assertRaises(EndpointError):
                client.chat([{"role": "user", "content": "hi"}])

    def test_connection_error_raises_endpoint_error(self):
        import urllib.error

        def fake_urlopen(req, timeout=None):
            raise urllib.error.URLError("connection refused")

        with mock.patch("book_club.endpoint.urllib.request.urlopen", side_effect=fake_urlopen):
            client = LLMClient()
            with self.assertRaises(EndpointError):
                client.chat([{"role": "user", "content": "hi"}])


if __name__ == "__main__":
    unittest.main()
