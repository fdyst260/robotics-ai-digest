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
