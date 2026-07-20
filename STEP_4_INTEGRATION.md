# Step 4 Integration — Evidence Reasoning Engine

## Scope

Step 4 introduces a hybrid evidence reasoning layer. It adds structured evidence classification, evidence-cited findings, contradiction detection, gap analysis, decision history, a versioned Investigation SOP prompt, and an optional OpenAI Responses API adapter.

## Added files

- `backend/app/schemas/reasoning.py`
- `backend/app/investigation/reasoning.py`
- `backend/app/investigation/reasoning_prompt.py`
- `backend/app/investigation/openai_reasoning_client.py`
- `backend/app/investigation/contradictions.py`
- `backend/app/investigation/evidence_summary.py`
- `backend/tests/test_reasoning.py`
- `backend/tests/test_reasoning_prompt.py`
- `backend/tests/test_contradictions.py`
- `docs/INVESTIGATION_STANDARD.md`

## Modified files

- `backend/app/core/settings.py`
- `backend/app/schemas/investigation.py`
- `backend/app/investigation/engine.py`
- `README.md`
- `docs/ARCHITECTURE.md`
- `.env.example`
- `pyproject.toml`

## Runtime behavior

After each evidence round, deterministic hypothesis evaluation and sufficiency checks run first. The reasoner then creates structured assessments, findings, contradictions, gaps, and a decision record. The deterministic sufficiency result overwrites any model stop recommendation, ensuring the model cannot bypass policy.

## Configuration

```dotenv
OPSMIND_REASONING_PROVIDER=fixture
OPSMIND_REASONING_PROMPT_VERSION=reasoning-v1
OPSMIND_REASONING_FALLBACK_TO_FIXTURE=true
```

Set `OPSMIND_REASONING_PROVIDER=openai` to enable model-assisted reasoning. `OPSMIND_OPENAI_API_KEY` and `OPSMIND_OPENAI_MODEL` are shared with the planner.

## Validation

```bash
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q
ruff check .
ruff format --check backend/app/schemas/reasoning.py \
  backend/app/investigation/reasoning.py \
  backend/app/investigation/reasoning_prompt.py \
  backend/app/investigation/openai_reasoning_client.py \
  backend/app/investigation/contradictions.py \
  backend/app/investigation/evidence_summary.py \
  backend/tests/test_reasoning.py \
  backend/tests/test_reasoning_prompt.py \
  backend/tests/test_contradictions.py
```

Do not commit or push unless all tests and lint checks pass.
