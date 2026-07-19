# Sprint 1 — Step 3: Structured OpenAI Investigation Planner

Step 3 turns the OpenAI engine path into a testable, bounded planning integration while preserving the deterministic evidence loop.

## Added

- `planner_prompt.py`: versioned system/user prompt construction.
- `openai_planner_client.py`: isolated OpenAI Responses API adapter using Pydantic structured output.
- Dependency injection for the planner model client.
- Semantic plan validation beyond schema validation.
- Bounded retry and deterministic fixture fallback tests.
- README documentation for modes, configuration, architecture, tests, and troubleshooting.

## Safety boundaries

OpenAI may generate hypotheses and evidence requirements, but it cannot execute arbitrary actions. The deterministic engine still owns:

- Tool allow-list enforcement
- Read-only execution
- Evidence normalization
- Confidence updates
- Sufficiency checks
- Verdict generation
- Persistence and audit history

## Validation rules

A model-generated plan is accepted only when:

1. Every selected tool exists in the runtime allow-list.
2. Hypothesis IDs are sequential (`H-001`, `H-002`, ...).
3. Evidence requirement IDs are sequential (`R-001`, `R-002`, ...).
4. Every hypothesis is covered by at least one evidence requirement.
5. The model's maximum rounds do not exceed the runtime safety limit.
6. The Pydantic `InvestigationPlan` schema validates successfully.

## Quality gates

```bash
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q backend/tests/test_openai_planner.py
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q
ruff check .
```
