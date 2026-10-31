"""CLI tests with isolated storage and a mocked endpoint."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from book_club.cli import main


class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.tmp, "club.json")

    def _run(self, argv):
        full_argv = ["--storage", self.storage_path] + argv
        import io

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            code = main(full_argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def _book_id(self, title, author):
        code, out, _ = self._run(["add-book", title, author])
        self.assertEqual(code, 0)
        return out.split("(id: ")[-1].split(")")[0].strip()

    def test_add_member(self):
        code, out, _ = self._run(["add-member", "Ada Lovelace", "--email", "ada@example.com"])
        self.assertEqual(code, 0)
        self.assertIn("Added member Ada Lovelace", out)
        self.assertIn("id:", out)

    def test_list_members_empty(self):
        code, out, _ = self._run(["list-members"])
        self.assertEqual(code, 0)
        self.assertIn("(none)", out)

    def test_add_book_and_list_books(self):
        self._run(["add-book", "The Hobbit", "J.R.R. Tolkien", "--isbn", "978"])
        code, out, _ = self._run(["list-books"])
        self.assertEqual(code, 0)
        self.assertIn("The Hobbit", out)
        self.assertIn("J.R.R. Tolkien", out)

    def test_schedule_and_print_schedule(self):
        book_id = self._book_id("Dune", "Frank Herbert")

        code, out, _ = self._run(
            [
                "schedule",
                book_id,
                "2026-11-01",
                "2026-11-30",
                "2026-12-05",
                "--location",
                "Library",
                "--notes",
                "Chapters 1-5",
            ]
        )
        self.assertEqual(code, 0)

        code, out, _ = self._run(["print-schedule"])
        self.assertEqual(code, 0)
        self.assertIn("Dune", out)
        self.assertIn("Frank Herbert", out)
        self.assertIn("2026-12-05", out)
        self.assertIn("Library", out)

    def test_generate_prompts_with_mock_endpoint(self):
        book_id = self._book_id("The Hobbit", "J.R.R. Tolkien")

        def fake_chat(*args, **kwargs):
            return "1. What did you love most?\n2. Who was your favorite character?"

        with mock.patch("book_club.endpoint.LLMClient.chat", side_effect=fake_chat):
            code, out, _ = self._run(
                [
                    "generate-prompts",
                    book_id,
                    "--endpoint",
                    "http://localhost:11434/v1",
                    "--count",
                    "2",
                ]
            )

        self.assertEqual(code, 0)
        self.assertIn("What did you love most?", out)
        self.assertIn("Who was your favorite character?", out)


if __name__ == "__main__":
    unittest.main()
