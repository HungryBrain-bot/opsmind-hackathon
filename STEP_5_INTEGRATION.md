# Step 5 Integration Guide

## Release

Step 5 upgrades OpsMind to v1.7.0 and adds multi-round investigation state, hypothesis evolution, resolution intelligence, verification planning, and knowledge capture.

## New modules

```text
backend/app/investigation/hypothesis_manager.py
backend/app/investigation/resolution.py
backend/app/investigation/knowledge_capture.py
backend/app/schemas/lifecycle.py
backend/app/schemas/resolution.py
backend/app/schemas/knowledge.py
backend/tests/test_step5_lifecycle.py
```

## Updated modules

```text
backend/app/investigation/engine.py
backend/app/investigation/reporting.py
backend/app/schemas/investigation.py
backend/app/schemas/report.py
README.md
docs/ARCHITECTURE.md
pyproject.toml
```

## Validate

```bash
python -m pip install -e ".[dev]"
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q
ruff check backend
python -m compileall backend/app
```

## API compatibility

Existing investigation fields and endpoints remain available. Step 5 adds fields to `InvestigationResult`; clients that ignore unknown JSON fields remain compatible.

New event types:

```text
round_completed
resolution_generated
verification_planned
knowledge_captured
```

## Safety

Resolution actions are recommendations only. `human_approval_required` and action-level `approval_required` default to `true`. No production write tool is introduced in Step 5.

## Expected golden-path result

The deterministic certificate-expiry scenario should:

- complete after two evidence rounds;
- produce a supported leading hypothesis;
- generate containment, recovery, verification, and prevention actions;
- expose at least three verification criteria;
- capture one reusable knowledge pattern;
- persist a replayable event trail.
