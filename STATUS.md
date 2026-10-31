# Status

Built: `book-club-host-assistant-cli` v0.1.0 — a local-first Python CLI for
running a book club (members, book catalog, reading schedule, printable
schedule, and discussion-prompt generation via a configurable OpenAI-compatible
endpoint, defaulting to a local Ollama instance).

## What was built

```
.
├── pyproject.toml            # setuptools build, console script: book-club
├── README.md                 # usage, local-first, credits Asdale Dynamics, LLC
├── LICENSE                   # MIT, Copyright (c) 2026 Asdale Dynamics, LLC
├── .gitignore
├── src/book_club/
│   ├── __init__.py
│   ├── models.py             # Member, Book, ReadingEntry, DiscussionPrompt, ClubData
│   ├── storage.py            # JSONStorage — single local JSON file
│   ├── endpoint.py           # LLMClient (urllib, OpenAI-compatible) + DiscussionPromptGenerator
│   ├── service.py            # service layer over storage
│   └── cli.py                # argparse CLI: add-member/list-members/add-book/list-books/schedule/list-schedule/print-schedule/generate-prompts
└── tests/
    ├── test_storage.py
    ├── test_endpoint.py
    ├── test_service.py
    ├── test_cli.py
    └── test_prompts.py
```

Design notes:

- Stdlib only — no third-party dependencies.
- Local-first: data lives in `~/.book_club_host.json` (overridable with
  `--storage`); default endpoint is `http://localhost:11434/v1` (Ollama),
  model `llama3`; no API keys required.
- If the endpoint is unreachable, `DiscussionPromptGenerator` falls back to
  built-in prompts so a meeting is never derailed.
- No secrets, API keys, or personal data are stored in files.

## How to run it

Install (editable):

```bash
python3 -m venv venv
./venv/bin/pip install -e .
./venv/bin/book-club --help
```

Or run without installing:

```bash
PYTHONPATH=src python3 -m book_club.cli --help
```

Example flow:

```bash
book-club add-member "Ada Lovelace" --email ada@example.com
book-club add-book "The Hobbit" "J.R.R. Tolkien" --isbn 978-0-261-10221-7
book-club schedule <book-id> 2026-11-01 2026-11-30 2026-12-05 --location Library
book-club print-schedule
book-club generate-prompts <book-id> --count 5
```

## Verification results

- `pip install -e .` succeeds; console script `book-club --help` works.
- Test suite: `PYTHONPATH=src python3 -m unittest discover -s tests` →
  **24 tests, all passing** (storage round-trips, endpoint client with mocked
  HTTP, prompt-generator fallback behavior, service layer, full CLI flow).
- End-to-end run confirmed: add members, add books, schedule, print schedule
  (book title shown), and generate-prompts (falls back to built-in prompts when
  Ollama is not running).

## Known gaps

- No Ollama is running in this environment, so prompt generation exercises the
  fallback path; a real Ollama endpoint has not been exercised here.
- `generate-prompts` does not persist generated prompts to storage; they are
  printed only.
- `list-schedule` uses a plain table; no sorting/filtering options yet.
- No import/export, member editing, or deletion commands.
- PEP 668 externally-managed environment: prefer a venv (`python3 -m venv`)
  over `pip install` directly.