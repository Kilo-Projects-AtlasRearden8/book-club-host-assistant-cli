"""Command-line interface for the Book Club Host Assistant."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from book_club.endpoint import LLMClient
from book_club.service import BookClubService
from book_club.storage import JSONStorage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="book-club",
        description="Local-first book club organizer: track members, reading "
        "schedules, and generate discussion prompts via a local LLM endpoint.",
    )
    parser.add_argument(
        "--storage",
        default=None,
        help="Path to the JSON storage file (default: ~/.book_club_host.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # member
    p_member = sub.add_parser("add-member", help="Add a club member")
    p_member.add_argument("name", help="Member's name")
    p_member.add_argument("--email", default="", help="Member's email address")

    p_list_members = sub.add_parser("list-members", help="List club members")

    # book
    p_book = sub.add_parser("add-book", help="Add a book to the club catalog")
    p_book.add_argument("title", help="Book title")
    p_book.add_argument("author", help="Book author")
    p_book.add_argument("--isbn", default="", help="ISBN (optional)")

    p_list_books = sub.add_parser("list-books", help="List books in the catalog")

    # schedule
    p_sched = sub.add_parser("schedule", help="Schedule a reading for a book")
    p_sched.add_argument("book_id", help="ID of the book (from list-books)")
    p_sched.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    p_sched.add_argument("end_date", help="End date (YYYY-MM-DD)")
    p_sched.add_argument("meeting_date", help="Meeting date (YYYY-MM-DD)")
    p_sched.add_argument("--location", default="", help="Meeting location (optional)")
    p_sched.add_argument("--notes", default="", help="Notes (optional)")

    p_list_sched = sub.add_parser("list-schedule", help="List the reading schedule")
    p_print = sub.add_parser("print-schedule", help="Print a readable schedule")

    # prompts
    p_prompts = sub.add_parser("generate-prompts", help="Generate discussion prompts for a book")
    p_prompts.add_argument("book_id", help="ID of the book (from list-books)")
    p_prompts.add_argument("--theme", default=None, help="Optional theme to focus on")
    p_prompts.add_argument("--count", type=int, default=5, help="Number of prompts (default: 5)")
    p_prompts.add_argument(
        "--endpoint",
        default=None,
        help="OpenAI-compatible endpoint base URL (default: http://localhost:11434/v1)",
    )
    p_prompts.add_argument("--model", default=None, help="Model name (default: llama3)")

    return parser


def _format_records(records: list, fields: list[str]) -> str:
    if not records:
        return "(none)"
    widths = {f: len(f) for f in fields}
    for record in records:
        for f in fields:
            widths[f] = max(widths[f], len(str(getattr(record, f, ""))))
    lines = []
    header = "  ".join(f.ljust(widths[f]) for f in fields)
    lines.append(header)
    lines.append("  ".join("-" * widths[f] for f in fields))
    for record in records:
        lines.append("  ".join(str(getattr(record, f, "")).ljust(widths[f]) for f in fields))
    return "\n".join(lines)


def print_schedule(service: BookClubService) -> None:
    rows = service.schedule_summary()
    if not rows:
        print("No readings scheduled yet.")
        return
    print("=== Book Club Reading Schedule ===\n")
    for row in rows:
        print(f"Book: {row['book']}")
        print(f"  Read: {row['start_date']} to {row['end_date']}")
        print(f"  Meeting: {row['meeting_date']}")
        if row["location"]:
            print(f"  Location: {row['location']}")
        if row["notes"]:
            print(f"  Notes: {row['notes']}")
        print()


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    storage = JSONStorage(args.storage or JSONStorage.default_path())
    service = BookClubService(storage)

    command = args.command

    if command == "add-member":
        member = service.add_member(args.name, args.email)
        print(f"Added member {member.name} (id: {member.id})")
    elif command == "list-members":
        members = service.list_members()
        print(_format_records(members, ["id", "name", "email", "joined_at"]))
    elif command == "add-book":
        book = service.add_book(args.title, args.author, args.isbn)
        print(f"Added book '{book.title}' by {book.author} (id: {book.id})")
    elif command == "list-books":
        books = service.list_books()
        print(_format_records(books, ["id", "title", "author", "isbn", "added_at"]))
    elif command == "schedule":
        entry = service.add_reading_entry(
            args.book_id,
            args.start_date,
            args.end_date,
            args.meeting_date,
            args.location,
            args.notes,
        )
        print(
            f"Scheduled reading for book {args.book_id}: "
            f"{args.start_date} to {args.end_date}, meeting {args.meeting_date} (id: {entry.id})"
        )
    elif command == "list-schedule":
        rows = service.schedule_summary()
        print(_format_records(
            [type("R", (), row)() for row in rows],
            ["id", "book", "start_date", "end_date", "meeting_date", "location", "notes"],
        ))
    elif command == "print-schedule":
        print_schedule(service)
    elif command == "generate-prompts":
        client = LLMClient(
            base_url=args.endpoint or "http://localhost:11434/v1",
            model=args.model or "llama3",
        )
        service.client = client
        try:
            prompts = service.generate_prompts(
                args.book_id, theme=args.theme, count=args.count
            )
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:  # noqa: BLE001 - surface endpoint errors to the user
            print(f"Error generating prompts: {exc}", file=sys.stderr)
            return 1
        book = service.get_book(args.book_id)
        print(f"Discussion prompts for '{book.title}' by {book.author}:\n")
        for i, prompt in enumerate(prompts, 1):
            print(f"{i}. {prompt}")
    else:  # pragma: no cover - argparse requires a subcommand
        parser.print_help()
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
