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
