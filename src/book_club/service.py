"""Application logic: service layer over storage and the prompt generator."""

from __future__ import annotations

from typing import Any

from book_club.endpoint import DiscussionPromptGenerator, LLMClient
from book_club.models import Book, ClubData, Member, ReadingEntry
from book_club.storage import JSONStorage


class BookClubService:
    def __init__(self, storage: JSONStorage) -> None:
        self.storage = storage
        self.club = storage.load()
        self._client: LLMClient | None = None

    def save(self) -> None:
        self.storage.save(self.club)

    @property
    def client(self) -> LLMClient:
        if self._client is None:
            self._client = LLMClient()
        return self._client

    @client.setter
    def client(self, value: LLMClient) -> None:
        self._client = value

    # ---- members ----

    def add_member(self, name: str, email: str = "") -> Member:
        member = Member.create(name, email)
        self.club.members[member.id] = member
        self.save()
        return member

    def list_members(self) -> list[Member]:
        return sorted(self.club.members.values(), key=lambda m: m.name.lower())

    def get_member(self, member_id: str) -> Member | None:
        return self.club.members.get(member_id)

    # ---- books ----

    def add_book(self, title: str, author: str, isbn: str = "") -> Book:
        book = Book.create(title, author, isbn)
        self.club.books[book.id] = book
        self.save()
        return book

    def list_books(self) -> list[Book]:
        return sorted(self.club.books.values(), key=lambda b: b.title.lower())

    def get_book(self, book_id: str) -> Book | None:
        return self.club.books.get(book_id)

    # ---- schedule ----

    def add_reading_entry(
        self,
        book_id: str,
        start_date: str,
        end_date: str,
        meeting_date: str,
        location: str = "",
        notes: str = "",
    ) -> ReadingEntry:
        entry = ReadingEntry.create(book_id, start_date, end_date, meeting_date, location, notes)
        self.club.reading_entries[entry.id] = entry
        self.save()
        return entry

    def list_reading_entries(self) -> list[ReadingEntry]:
        return sorted(
            self.club.reading_entries.values(),
            key=lambda e: (e.start_date, e.meeting_date),
        )

    def get_reading_entry(self, entry_id: str) -> ReadingEntry | None:
        return self.club.reading_entries.get(entry_id)

    def schedule_summary(self) -> list[dict[str, Any]]:
        entries = self.list_reading_entries()
        rows: list[dict[str, Any]] = []
        for entry in entries:
            book = self.club.books.get(entry.book_id)
            rows.append(
                {
                    "id": entry.id,
                    "book": f"{book.title} by {book.author}" if book else "(unknown book)",
                    "start_date": entry.start_date,
                    "end_date": entry.end_date,
                    "meeting_date": entry.meeting_date,
                    "location": entry.location,
                    "notes": entry.notes,
                }
            )
        return rows

    # ---- prompts ----

    def generate_prompts(
        self,
        book_id: str,
        *,
        theme: str | None = None,
        count: int = 5,
        use_fallback: bool = True,
    ) -> list[str]:
        book = self.club.books.get(book_id)
        if book is None:
            raise KeyError(f"No book with id {book_id}")
        generator = DiscussionPromptGenerator(self.client)
        return generator.generate(
            book.title, book.author, theme=theme, count=count, use_fallback=use_fallback
        )
