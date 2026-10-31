# Book Club Host Assistant CLI

A local-first Python command-line tool for running a book club: track members,
keep a reading schedule, and generate discussion prompts with a local LLM.
Built by **Asdale Dynamics, LLC** — beginner-friendly AI tools and practical
apps for authors, small businesses, and everyday life.

## What it does

- **Members:** add and list club members (names and optional email addresses)
- **Books:** keep a catalog of books with title, author, and ISBN
- **Reading schedule:** schedule start/end dates and meeting dates per book,
  with an optional location and notes, and print a readable schedule
- **Discussion prompts:** generate warm, open-ended discussion questions for a
  book via an OpenAI-compatible endpoint (default: a local Ollama instance at
  `http://localhost:11434/v1`, model `llama3`). If the endpoint is unreachable,
  the tool falls back to built-in prompts so your meeting is never derailed.

All data lives in a single local JSON file (default `~/.book_club_host.json`).
No API keys are required, nothing is sent anywhere unless you point the tool at
an endpoint yourself, and it works offline out of the box.

## Install

```bash
git clone <this-repo>
cd book-club-host-assistant-cli
pip install -e .
```

Or run without installing:

```bash
PYTHONPATH=src python3 -m book_club.cli --help
```

## Usage

Add a member:

```bash
book-club add-member "Ada Lovelace" --email ada@example.com
```

List members:

```bash
book-club list-members
```

Add a book:

```bash
book-club add-book "The Hobbit" "J.R.R. Tolkien" --isbn 978-0-261-10221-7
```

List books (shows the ids you need for scheduling):

```bash
book-club list-books
```

Schedule a reading:

```bash
book-club schedule <book-id> 2026-11-01 2026-11-30 2026-12-05 \
  --location "The Library" --notes "Chapters 1-5"
```

Print the schedule:

```bash
book-club print-schedule
```

Generate discussion prompts for a book (hits your local Ollama by default):

```bash
book-club generate-prompts <book-id> --count 5
```

Use a different OpenAI-compatible endpoint or model:

```bash
book-club generate-prompts <book-id> \
  --endpoint http://localhost:11434/v1 --model llama3
```

Use a different storage file:

```bash
book-club --storage ./my-club.json ...
```

## Local-first by design

- Storage: one JSON file on your machine, nowhere else
- Default endpoint: Ollama running locally (no account, no key)
- Fallback: built-in discussion prompts if the endpoint is down
- No tracking, no telemetry, no secrets stored in files

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

All tests use mocked endpoints — no network and no API keys required.

## Credits

Created by **Asdale Dynamics, LLC** (Dylan Asdale, Indiana, formed October
2026), publisher of beginner-friendly AI education including *The Massive AI
Manual* and the hub site dylanasdale.github.io. AI explained "like a friend
would": plain English, step by step, never condescending.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
