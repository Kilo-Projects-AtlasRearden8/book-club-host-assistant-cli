# Book Club Host Assistant CLI

A friendly, local-first command-line tool for running a book club. Keep track of
your members, your reading schedule, and generate warm discussion prompts — all
on your own computer, with no API keys required.

Built by **Asdale Dynamics, LLC** — beginner-friendly AI tools, books, and
guides for authors, small businesses, and everyday life. AI explained "like a
friend would": plain English, step by step, never condescending.

## What it does

- **Members:** add members and see who's in the club
- **Books:** keep a catalog of books with title, author, and ISBN
- **Reading schedule:** set start/end dates and a meeting date for each book,
  with an optional location and notes
- **Printable schedule:** print a clean, readable schedule for your meetings
- **Discussion prompts:** generate open-ended, beginner-friendly discussion
  questions for any book via a local LLM endpoint (defaults to Ollama at
  `http://localhost:11434/v1`, model `llama3`). If the endpoint is down, the
  tool falls back to built-in prompts so your meeting is never derailed.

All of your data lives in a single JSON file on your computer
(default `~/.book_club_host.json`). Nothing is sent anywhere unless you choose
to point the tool at an endpoint yourself, and everything works offline out of
the box.

## Install

You'll need Python 3.9 or newer.

```bash
git clone <this-repo>
cd book-club-host-assistant-cli
python3 -m venv venv
./venv/bin/pip install -e .
```

This creates a `book-club` command you can run anywhere:

```bash
book-club --help
```

If you'd rather not install, you can run it straight from the folder:

```bash
PYTHONPATH=src python3 -m book_club.cli --help
```

*(On some systems `pip install` needs a virtual environment — that's why we
create `venv` first.)*

## Walkthrough

### Add a member

```bash
book-club add-member "Ada Lovelace" --email ada@example.com
book-club add-member "Dylan Asdale"
```

### List members

```bash
book-club list-members
```

### Add a book

```bash
book-club add-book "The Hobbit" "J.R.R. Tolkien" --isbn 978-0-261-10221-7
```

### List books (gives you the IDs you need for scheduling)

```bash
book-club list-books
```

### Schedule a reading

```bash
book-club schedule <book-id> 2026-11-01 2026-11-30 2026-12-05 \
  --location "The Library" --notes "Chapters 1-5"
```

### Print the schedule

```bash
book-club print-schedule
```

### Generate discussion prompts

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

- **Storage:** one JSON file on your machine, nowhere else
- **Default endpoint:** Ollama running locally (no account, no key)
- **Fallback:** built-in discussion prompts if the endpoint is unreachable
- **No tracking, no telemetry, no secrets stored in files**

## Tests

All tests use mocked endpoints — no network and no API keys needed:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Credits

Created by **Asdale Dynamics, LLC** (Dylan Asdale, Indiana, formed October
2026), publisher of beginner-friendly AI education including *The Massive AI
Manual* and the hub site dylanasdale.github.io.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
