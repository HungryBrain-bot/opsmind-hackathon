# OpsMind v1.6

**OpsMind is an evidence-first AI Investigation Engine for enterprise operations.**

> LLMs answer from what they know. OpsMind investigates what your enterprise knows.

OpsMind turns an operational incident into a structured investigation. It generates competing hypotheses, collects targeted enterprise evidence, records how confidence changes, rejects alternatives that do not fit the evidence, and stops only when the conclusion is defensible.

## What v1.6 showcases

The current hackathon release focuses on realistic Splunk Heavy Forwarder incidents. An operator opens an incident knowing only the symptom; OpsMind discovers the root cause during the investigation.

Example incident patterns include:

- Heavy Forwarder stopped forwarding logs
- No events reaching the indexer cluster
- Forwarding failure after a maintenance window
- Severe ingestion delay with growing queues

The underlying causes remain hidden until the investigation completes. The engine can distinguish between certificate expiry, network or firewall failure, forwarding configuration issues, and local storage or queue pressure.

## Core capabilities

- Evidence-first investigation planning
- Multiple competing hypotheses
- Targeted tool execution through an allow-listed registry
- MCP-ready tool boundary
- Live Server-Sent Events investigation updates
- Evidence ledger, notebook, and timeline
- Hypothesis confidence evolution
- Explicit rejection reasons and “why not” explanations
- Evidence sufficiency checks before reaching a verdict
- Decision trace and evidence graph
- Markdown and JSON investigation reports
- Persistent investigation history with reopen, search, filter, download, and delete actions
- Deterministic offline mode and optional OpenAI-assisted planning

## Quick start

Requirements:

- Python 3.11 or newer
- Linux, macOS, or Windows with a POSIX-compatible shell for the helper scripts

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"

pytest -q
./run-demo.sh
```

Open `http://127.0.0.1:8000`.

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --app-dir backend --reload
```

## Optional OpenAI planner

```bash
cp .env.example .env
# Add OPENAI_API_KEY to .env, then:
./run-ai.sh
```

The OpenAI planner may propose investigation steps. OpsMind still controls the allowed tools, evidence normalization, hypothesis state, sufficiency rules, verdict generation, and final audit trail.

## Demo flow

1. Open a production incident.
2. Start the investigation.
3. Watch OpsMind create and test competing hypotheses.
4. Inspect evidence, confidence changes, and rejected alternatives.
5. Review the evidence-backed verdict and recommended actions.
6. Download the report.
7. Reopen the completed case from Investigation History.
8. Run a second incident to show that the same engine reaches a different conclusion from different evidence.

See [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for the full presentation script.

## Architecture

```text
Enterprise Sources
        │
        ▼
MCP / Tool Adapters
        │
        ▼
Investigation Packs
        │
        ▼
Planner → Evidence Collection → Evidence Ledger
        │                         ├─ Timeline
        │                         ├─ Notebook
        │                         ├─ Confidence Evolution
        │                         └─ Evidence Graph
        ▼
Hypothesis Evaluation → Evidence Sufficiency → Verdict
        │
        ▼
Decision Trace → Reports → Investigation History
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design details.

## API

FastAPI exposes interactive documentation at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

The primary API prefix is `/api/v1`. See [docs/API.md](docs/API.md).

## Repository layout

```text
backend/app/
├── api/              # HTTP and SSE endpoints
├── core/             # Settings and logging
├── investigation/    # Planner, engine, tools, evaluation, reports
├── schemas/          # Pydantic models
└── storage/          # Investigation repository abstraction

backend/tests/         # Automated tests
frontend/              # Investigation workspace UI
data/investigations/   # Runtime history; ignored except .gitkeep
docs/                  # Architecture, API, and demo documentation
```

## Operating modes

### Offline fixture mode

The default hackathon mode is deterministic and works without external credentials. It is intended for repeatable demonstrations and automated tests.

### OpenAI-assisted mode

When configured, OpenAI can assist the planning stage. Tool access, evidence handling, sufficiency, and auditability remain enforced by OpsMind.

## Known limitations

This is a hackathon MVP, not a production deployment. Current limitations include:

- File-based persistence rather than a production database
- No authentication, authorization, or multitenant isolation
- Demo-oriented enterprise evidence adapters
- No automated remediation execution
- No Jira, email, or ticketing write-back
- Markdown report export only; PDF export is deferred
- No production secrets manager or hardened deployment configuration

## Development

```bash
ruff check .
pytest -q
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

## Security

Do not use this MVP to execute remediation against production systems. See [SECURITY.md](SECURITY.md) for reporting guidance and current security boundaries.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).
