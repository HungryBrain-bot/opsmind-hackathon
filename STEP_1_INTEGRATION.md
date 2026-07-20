# Sprint 1 — Step 1 Integration

This patch introduces the engine abstraction and orchestrator without changing the existing investigation behaviour.

## Files added

- `backend/app/investigation/base.py`
- `backend/app/investigation/demo_engine.py`
- `backend/app/investigation/orchestrator.py`
- `backend/tests/test_orchestrator.py`

## File changed

- `backend/app/api/investigations.py`

## Validation commands

```bash
source .venv/bin/activate
pip install -e ".[dev]"
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q
ruff check .
```

Expected result after this patch:

```text
24 passed
```

Do not commit or push unless both tests and Ruff pass.
