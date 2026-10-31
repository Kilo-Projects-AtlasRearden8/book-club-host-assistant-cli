"""Tests for the discussion prompt generator fallback behavior."""

from __future__ import annotations

import unittest
from unittest import mock

from book_club.endpoint import DiscussionPromptGenerator, EndpointError, LLMClient


class GeneratorTests(unittest.TestCase):
    def test_endpoint_success_returns_prompts(self):
        client = mock.Mock(spec=LLMClient)
        client.chat.return_value = "1. Did you like it?\n2. Who was your favorite?"
        gen = DiscussionPromptGenerator(client)
        prompts = gen.generate("The Hobbit", "J.R.R. Tolkien", count=2)
        self.assertEqual(prompts, ["Did you like it?", "Who was your favorite?"])

    def test_failure_falls_back_to_templates(self):
        client = mock.Mock(spec=LLMClient)
        client.chat.side_effect = EndpointError("down")
        gen = DiscussionPromptGenerator(client)
        prompts = gen.generate("Dune", "Frank Herbert", count=2)
        self.assertTrue(len(prompts) >= 1)
        self.assertLessEqual(len(prompts), 2)

    def test_failure_without_fallback_raises(self):
        client = mock.Mock(spec=LLMClient)
        client.chat.side_effect = EndpointError("down")
        gen = DiscussionPromptGenerator(client)
        with self.assertRaises(EndpointError):
            gen.generate("Dune", "Frank Herbert", use_fallback=False)

    def test_theme_inserts_theme_question(self):
        client = mock.Mock(spec=LLMClient)
        client.chat.side_effect = EndpointError("down")
        gen = DiscussionPromptGenerator(client)
        prompts = gen.generate("Dune", "Frank Herbert", theme="power", count=5)
        self.assertTrue(any("power" in p.lower() for p in prompts))


if __name__ == "__main__":
    unittest.main()
