# Robotics AI Digest

Portfolio project: a production-style Python CLI that ingests RSS feeds, stores and deduplicates articles, generates AI summaries, and renders a daily Markdown digest.

## Why This Project

This repository demonstrates practical software engineering skills for data workflows:

- clean Python package layout (`src/` + `pyproject.toml`)
- reliable persistence with SQLite + SQLAlchemy
- deterministic CLI workflows for ingestion, listing, summarization, and digest generation
- test coverage with `pytest`
- code quality gates with Ruff and CI (GitHub Actions)

## Core Features

- RSS ingestion from one or many feeds
- deduplication by link / guid
- SQLite storage layer with repository pattern
- AI summarization pipeline (OpenAI-backed, with mock fallback)
- cost estimation and dry-run mode before API calls
- Markdown digest rendering by date and source
- one-command PowerShell helper script for Windows

## Tech Stack

- Python 3.11+
- SQLAlchemy
- feedparser + requests
- OpenAI Python SDK
- pytest + Ruff
- GitHub Actions

## Project Structure

```text
src/robotics_ai_digest/
  cli.py
  feeds/
  storage/
  summarization/
  digest/
tests/
scripts/
```

## Quick Start (Windows PowerShell)

```powershell
cd robotics-ai-digest-main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
```

## CLI Usage

```powershell
python -m robotics_ai_digest --help
python -m robotics_ai_digest version
```

Ingest RSS feeds into SQLite:

```powershell
python -m robotics_ai_digest ingest `
  --db data/digest.db `
  --rss https://feeds.bbci.co.uk/news/technology/rss.xml https://hnrss.org/frontpage
```

List recent articles:

```powershell
python -m robotics_ai_digest list --db data/digest.db --limit 10
```

Generate AI summaries:

```powershell
python -m robotics_ai_digest summarize --db data/digest.db --limit 10
```

Estimate cost without API calls:

```powershell
python -m robotics_ai_digest summarize `
  --db data/digest.db `
  --limit 5 `
  --model gpt-4.1-mini `
  --dry-run
```

Generate a daily Markdown digest:

```powershell
python -m robotics_ai_digest digest `
  --db data/digest.db `
  --date 2025-02-10 `
  --out output
```

## OpenAI Configuration

Create a `.env` file at repository root:

```env
OPENAI_API_KEY=your_api_key_here
```

If `OPENAI_API_KEY` is not set, the summarization command automatically falls back to a local `MockSummarizer`.

## Windows Helper Script

Run ingest + list in one command:

```powershell
.\scripts\run_digest.ps1 -Rss "https://feeds.bbci.co.uk/news/technology/rss.xml"
```

Example with multiple feeds and filters:

```powershell
.\scripts\run_digest.ps1 `
  -Rss "https://feeds.bbci.co.uk/news/technology/rss.xml","https://hnrss.org/frontpage" `
  -DbPath "data/digest.db" `
  -Limit 15 `
  -Source "BBC News - Technology"
```

## Quality Checks

```powershell
ruff check .
ruff format .
pytest
```

## Current Status

- working ingestion and storage pipeline
- tested digest rendering and CLI flows
- AI summarization with fallback and cost guardrails
- CI pipeline enabled on push and pull request

## Roadmap

- richer article-content extraction (beyond RSS snippets)
- scheduled daily automation
- sample generated digest committed in `examples/`
- Docker packaging and release/versioning polish
