# Sprint 1 — Step 2 Integration

This step adds runtime engine selection through the existing `OPSMIND_PLANNER_PROVIDER`
setting. It does not change the API contract or frontend behavior.

## Modes

- `fixture` builds `DemoInvestigationEngine`.
- `openai` builds `OpenAIInvestigationEngine`.
- OpenAI mode without an API key is allowed only when fixture fallback remains enabled.
- Unsupported provider values fail with a clear configuration error.

## Quality gates

```bash
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q
ruff check .
```

Expected against the Step 1 repository used to build this patch: `29 passed`.
