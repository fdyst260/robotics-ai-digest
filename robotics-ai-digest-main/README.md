# robotics-ai-digest

Projet Python orienté portfolio, structuré en `src/` avec packaging moderne (`pyproject.toml`).

## Prérequis

- Windows
- Python 3.11+ installé
- VS Code (optionnel mais recommandé)

## Installation (Windows PowerShell)

```powershell
cd robotics-ai-digest
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
```

## Commandes de qualité

```powershell
ruff check .
ruff format .
pytest
```

## CLI

```powershell
python -m robotics_ai_digest --help
python -m robotics_ai_digest version
python -m robotics_ai_digest summarize --db data/digest.db --limit 10
python -m robotics_ai_digest summarize --db data/digest.db --limit 10 --dry-run
python -m robotics_ai_digest digest --db data/digest.db --date 2025-02-10 --out output
```

## OpenAI Key

Create a `.env` file at project root:

```env
OPENAI_API_KEY=your_api_key_here
```

If `OPENAI_API_KEY` is missing, `summarize` automatically falls back to `MockSummarizer`.

## Cost Estimation (Before API Calls)

The `summarize` command estimates token usage and API cost before any OpenAI request.

```powershell
python -m robotics_ai_digest summarize --db data/digest.db --limit 5 --model gpt-4.1-mini --dry-run
```

Example CLI output:

```text
Estimated input tokens: 1830
Estimated output tokens: 1100
Estimated total tokens: 2930
Estimated cost (USD): $0.005860
Dry-run enabled: no API calls, no database writes.
```

## Run In One Command (Windows)

```powershell
.\scripts\run_digest.ps1 -Rss "https://feeds.bbci.co.uk/news/technology/rss.xml"
```

Options:

```powershell
.\scripts\run_digest.ps1 `
  -Rss "https://feeds.bbci.co.uk/news/technology/rss.xml","https://hnrss.org/frontpage" `
  -DbPath "data/digest.db" `
  -Limit 15 `
  -Source "BBC News - Technology"
```
