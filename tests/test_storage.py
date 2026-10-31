"""Tests for JSON storage round-trips."""

from __future__ import annotations

import os
import tempfile
import unittest

from book_club.models import Book, ClubData, Member, ReadingEntry
from book_club.storage import JSONStorage


class JSONStorageTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "club.json")
            storage = JSONStorage(path)

            club = ClubData()
            member = Member.create("Ada Lovelace", "ada@example.com")
            book = Book.create("The Hobbit", "J.R.R. Tolkien", "978-0-261-10221-7")
            entry = ReadingEntry.create(book.id, "2026-11-01", "2026-11-30", "2026-12-05", "Library")

            club.members[member.id] = member
            club.books[book.id] = book
            club.reading_entries[entry.id] = entry

            storage.save(club)
            loaded = storage.load()

        self.assertEqual(len(loaded.members), 1)
        loaded_member = next(iter(loaded.members.values()))
        self.assertEqual(loaded_member.name, "Ada Lovelace")
        self.assertEqual(loaded_member.email, "ada@example.com")

        self.assertEqual(len(loaded.books), 1)
        loaded_book = next(iter(loaded.books.values()))
        self.assertEqual(loaded_book.title, "The Hobbit")
        self.assertEqual(loaded_book.isbn, "978-0-261-10221-7")

        self.assertEqual(len(loaded.reading_entries), 1)
        loaded_entry = next(iter(loaded.reading_entries.values()))
        self.assertEqual(loaded_entry.meeting_date, "2026-12-05")

    def test_missing_file_returns_empty_club(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "does-not-exist.json")
            storage = JSONStorage(path)
            club = storage.load()
        self.assertEqual(len(club.members), 0)
        self.assertEqual(len(club.books), 0)

    def test_invalid_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("{not json")
            storage = JSONStorage(path)
            with self.assertRaises(Exception):
                storage.load()


if __name__ == "__main__":
    unittest.main()
