"""Core data models for the book club assistant."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any


def _new_id() -> str:
    return uuid.uuid4().hex


def _today() -> str:
    return date.today().isoformat()


@dataclass
class Member:
    id: str
    name: str
    email: str = ""
    joined_at: str = field(default_factory=_today)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Member":
        return Member(
            id=data.get("id", _new_id()),
            name=data.get("name", ""),
            email=data.get("email", ""),
            joined_at=data.get("joined_at", _today()),
        )

    @staticmethod
    def create(name: str, email: str = "") -> "Member":
        return Member(id=_new_id(), name=name, email=email)


@dataclass
class Book:
    id: str
    title: str
    author: str
    isbn: str = ""
    added_at: str = field(default_factory=_today)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Book":
        return Book(
            id=data.get("id", _new_id()),
            title=data.get("title", ""),
            author=data.get("author", ""),
            isbn=data.get("isbn", ""),
            added_at=data.get("added_at", _today()),
        )

    @staticmethod
    def create(title: str, author: str, isbn: str = "") -> "Book":
        return Book(id=_new_id(), title=title, author=author, isbn=isbn)


@dataclass
class ReadingEntry:
    id: str
    book_id: str
    start_date: str
    end_date: str
    meeting_date: str
    location: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ReadingEntry":
        return ReadingEntry(
            id=data.get("id", _new_id()),
            book_id=data.get("book_id", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            meeting_date=data.get("meeting_date", ""),
            location=data.get("location", ""),
            notes=data.get("notes", ""),
        )

    @staticmethod
    def create(
        book_id: str,
        start_date: str,
        end_date: str,
        meeting_date: str,
        location: str = "",
        notes: str = "",
    ) -> "ReadingEntry":
        return ReadingEntry(
            id=_new_id(),
            book_id=book_id,
            start_date=start_date,
            end_date=end_date,
            meeting_date=meeting_date,
            location=location,
            notes=notes,
        )


@dataclass
class DiscussionPrompt:
    id: str
    book_id: str
    prompt: str
    created_at: str = field(default_factory=_today)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "DiscussionPrompt":
        return DiscussionPrompt(
            id=data.get("id", _new_id()),
            book_id=data.get("book_id", ""),
            prompt=data.get("prompt", ""),
            created_at=data.get("created_at", _today()),
        )

    @staticmethod
    def create(book_id: str, prompt: str) -> "DiscussionPrompt":
        return DiscussionPrompt(id=_new_id(), book_id=book_id, prompt=prompt)


class ClubData:
    """In-memory collection of all book club records."""

    def __init__(self) -> None:
        self.members: dict[str, Member] = {}
        self.books: dict[str, Book] = {}
        self.reading_entries: dict[str, ReadingEntry] = {}
        self.discussion_prompts: dict[str, DiscussionPrompt] = {}

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "members": [m.to_dict() for m in self.members.values()],
            "books": [b.to_dict() for b in self.books.values()],
            "reading_entries": [r.to_dict() for r in self.reading_entries.values()],
            "discussion_prompts": [p.to_dict() for p in self.discussion_prompts.values()],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ClubData":
        club = ClubData()
        for item in data.get("members", []):
            m = Member.from_dict(item)
            club.members[m.id] = m
        for item in data.get("books", []):
            b = Book.from_dict(item)
            club.books[b.id] = b
        for item in data.get("reading_entries", []):
            r = ReadingEntry.from_dict(item)
            club.reading_entries[r.id] = r
        for item in data.get("discussion_prompts", []):
            p = DiscussionPrompt.from_dict(item)
            club.discussion_prompts[p.id] = p
        return club
