# OpsMind v1.0

OpsMind is an evidence-first AI Investigation Engine for enterprise operations.

> LLMs answer from what they know. OpsMind investigates what your enterprise knows.

This release uses the original Sprint 5 Investigation Workspace as the source of truth.
It extends that interface rather than replacing it.

## What is preserved

- Original sidebar, cards, colors, spacing and responsive design
- Investigation progress stages
- Live SSE updates
- Competing hypothesis panel
- Enterprise evidence panel
- Live investigation notebook
- Evidence-strength and completeness rings
- Offline fixture and optional OpenAI planner modes

## What is added

- Evidence sufficiency rule panel
- Read-only tool and investigation-plan panel
- Evidence graph modal
- Judge mode
- Investigation Pack API
- Timeline API
- Notebook API
- Clearer frontend failure reporting
- Version 1.0 release packaging

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest -q
./run-demo.sh
```

Open `http://127.0.0.1:8000`.

## Demo root cause

The deterministic Heavy Forwarder scenario resolves to an expired client certificate
after OpsMind gathers current logs, certificate state, historical incident knowledge,
component relationships and Heavy Forwarder health evidence.

## Optional OpenAI planner

```bash
OPENAI_API_KEY=sk-... ./run-ai.sh
```

The OpenAI planner may propose the investigation plan. OpsMind still controls allowed
tools, evidence normalization, hypothesis state, sufficiency rules and the final audit trail.
