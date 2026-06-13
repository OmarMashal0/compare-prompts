# Contributing to promptdiff

Thank you for considering contributing!

## Setup

```bash
git clone https://github.com/OmarMashal0/promptdiff
cd promptdiff
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/ -v
```

Tests do not require any API keys — all LiteLLM calls are mocked.

## Adding a new metric

1. Add the analysis logic to `promptdiff/metrics.py` inside the `measure()` function
2. Add the metric to the aggregation in `promptdiff/display.py` -> `aggregate()` function
3. Add a new row in `promptdiff/display.py` -> `print_table()` function
4. Add at least 2 tests in `tests/test_metrics.py`
5. Update the "What it measures" table in `README.md`

## Code style

- Follow the existing code patterns
- Use type hints for function signatures
- Write clear docstrings for public functions
- Keep functions focused and small

## Submitting a PR

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Commit: `git commit -m "add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request on GitHub
8. Update `CHANGELOG.md` with your change
