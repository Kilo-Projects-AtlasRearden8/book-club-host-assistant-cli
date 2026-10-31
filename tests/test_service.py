"""Tests for the service layer, including fallback prompt generation."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from book_club.endpoint import EndpointError, LLMClient
from book_club.models import Book
from book_club.service import BookClubService
from book_club.storage import JSONStorage


class ServiceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.mkdtemp()
        self.storage = JSONStorage(os.path.join(tmp, "club.json"))
        self.service = BookClubService(self.storage)

    def test_add_member_and_list(self):
        member = self.service.add_member("Ada Lovelace", "ada@example.com")
        self.assertIsNotNone(member.id)
        self.assertEqual(member.name, "Ada Lovelace")
        self.assertEqual(member.email, "ada@example.com")

        members = self.service.list_members()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].name, "Ada Lovelace")

    def test_add_book_and_list(self):
        book = self.service.add_book("The Hobbit", "J.R.R. Tolkien", "978-0-261-10221-7")
        books = self.service.list_books()
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].author, "J.R.R. Tolkien")

    def test_schedule_reading(self):
        book = self.service.add_book("Dune", "Frank Herbert")
        entry = self.service.add_reading_entry(
            book.id, "2026-11-01", "2026-11-30", "2026-12-05", "Library", "Chapters 1-5"
        )
        entries = self.service.list_reading_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].meeting_date, "2026-12-05")

        summary = self.service.schedule_summary()
        self.assertEqual(len(summary), 1)
        self.assertIn("Dune", summary[0]["book"])

    def test_generate_prompts_uses_endpoint(self):
        self.service.add_book("The Hobbit", "J.R.R. Tolkien")

        def fake_chat(messages, **kwargs):
            return (
                "1. What did you think of Bilbo's journey?\n"
                "2. Would you take the ring?\n"
            )

        client = mock.Mock(spec=LLMClient)
        client.chat.side_effect = fake_chat
        self.service.client = client

        prompts = self.service.generate_prompts(
            next(iter(self.service.club.books)), count=2
        )
        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[0], "What did you think of Bilbo's journey?")
        client.chat.assert_called_once()

    def test_generate_prompts_falls_back_when_endpoint_fails(self):
        self.service.add_book("The Hobbit", "J.R.R. Tolkien")
        book_id = next(iter(self.service.club.books))

        failing_client = mock.Mock(spec=LLMClient)
        failing_client.chat.side_effect = EndpointError("endpoint down")
        self.service.client = failing_client

        prompts = self.service.generate_prompts(book_id, count=3)
        self.assertTrue(len(prompts) >= 1)
        self.assertLessEqual(len(prompts), 3)

    def test_generate_prompts_unknown_book_raises(self):
        with self.assertRaises(KeyError):
            self.service.generate_prompts("no-such-id")

    def test_persistence_across_service_instances(self):
        self.service.add_member("Ada Lovelace")
        book = self.service.add_book("Dune", "Frank Herbert")

        new_service = BookClubService(JSONStorage(self.storage.path))
        self.assertEqual(len(new_service.list_members()), 1)
        loaded_book = new_service.get_book(book.id)
        self.assertIsNotNone(loaded_book)
        self.assertEqual(loaded_book.title, "Dune")


if __name__ == "__main__":
    unittest.main()
