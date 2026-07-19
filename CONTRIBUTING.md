# Contributing to OpsMind

Thank you for helping improve OpsMind.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Branch workflow

Use the existing workflow:

```text
main
└── develop
    └── feature/<short-description>
```

Create changes on a feature branch, open a pull request into `develop`, and merge only after checks pass.

## Required checks

```bash
ruff check .
pytest -q
```

For frontend changes, also verify JavaScript syntax and test the full browser flow manually.

## Design principles

Changes should preserve these constraints:

- Evidence before diagnosis
- Competing hypotheses rather than a single unchallenged answer
- Read-only collection by default
- Explicit approval before future write actions
- Structured, traceable investigation events
- Separation between the core engine and Investigation Packs
- No hardcoded customer-specific logic in the core engine

## Pull requests

A pull request should include:

- What changed and why
- Screenshots for UI changes
- Tests added or updated
- Any known limitations
- Confirmation that no secrets, runtime histories, caches, or generated files are included

## Commit style

Use clear imperative messages, for example:

```text
feat: add incident queue metadata
fix: preserve report download after reopening history
chore: remove generated investigation snapshots
```
