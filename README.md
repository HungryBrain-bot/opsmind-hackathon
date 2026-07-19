# OpsMind v1.7

**OpsMind is an evidence-first AI Investigation Engine for enterprise operations.**

> LLMs answer from what they know. OpsMind investigates what your enterprise knows.

OpsMind turns an operational incident into a structured investigation. It generates competing hypotheses, collects targeted enterprise evidence, records how confidence changes, rejects alternatives that do not fit the evidence, and stops only when the conclusion is defensible.

## What v1.7 showcases

The current hackathon release adds a production-shaped, structured OpenAI planning boundary while preserving deterministic judge mode. It focuses on realistic Splunk Heavy Forwarder incidents. An operator opens an incident knowing only the symptom; OpsMind discovers the root cause during the investigation.

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
- Versioned planner prompts and strict Pydantic structured output
- Semantic plan validation, bounded retries, usage telemetry, and fixture fallback

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

OpsMind uses the OpenAI Responses API with a strict Pydantic `InvestigationPlan` output. The model proposes hypotheses and evidence requirements; it does not receive unrestricted execution authority.

```bash
cp .env.example .env
# Set OPSMIND_OPENAI_API_KEY in .env, then:
./run-ai.sh
```

Equivalent environment configuration:

```bash
export OPSMIND_PLANNER_PROVIDER=openai
export OPSMIND_OPENAI_API_KEY="your-key"
export OPSMIND_OPENAI_MODEL="gpt-5.6"
export OPSMIND_PLANNER_PROMPT_VERSION="planner-v1"
export OPSMIND_PLANNER_MAX_VALIDATION_ATTEMPTS=2
export OPSMIND_PLANNER_FALLBACK_TO_FIXTURE=true
python -m uvicorn app.main:app --app-dir backend --reload
```

The generated plan must pass both schema and semantic validation. OpsMind rejects unknown tools, non-sequential IDs, uncovered hypotheses, and round counts above the configured safety limit. Failed model or validation attempts are bounded, logged, and can fall back to the deterministic fixture planner.

OpsMind still controls the allowed tools, evidence normalization, hypothesis state, sufficiency rules, verdict generation, persistence, and final audit trail.

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
Engine Factory → Planner Provider
        │          ├─ Fixture Planner
        │          └─ OpenAI Planner → Versioned Prompt → Structured Output
        ▼
Semantic Plan Validation → Evidence Collection → Evidence Ledger
        │                                           ├─ Timeline
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

When configured, OpenAI assists only the planning stage through a dedicated adapter. The planner response is parsed directly into `InvestigationPlan`, then checked against runtime safety rules before the deterministic investigation loop can use it.

Planning flow:

```text
InvestigationRequest
  → versioned prompt builder
  → OpenAI Responses API structured output
  → Pydantic validation
  → semantic validation
  → accepted plan OR bounded retry
  → deterministic fixture fallback when enabled
```

Tool access, evidence handling, confidence updates, sufficiency, verdict generation, and auditability remain enforced by OpsMind.

## Planner configuration reference

| Variable | Default | Purpose |
|---|---:|---|
| `OPSMIND_PLANNER_PROVIDER` | `fixture` | Selects `fixture` or `openai`. |
| `OPSMIND_OPENAI_API_KEY` | empty | Required for live OpenAI planning unless fallback is enabled. |
| `OPSMIND_OPENAI_MODEL` | `gpt-5.6` | Model used by the structured planner. |
| `OPSMIND_PLANNER_PROMPT_VERSION` | `planner-v1` | Selects a registered prompt contract. Unknown versions fail fast. |
| `OPSMIND_PLANNER_MAX_VALIDATION_ATTEMPTS` | `2` | Maximum model/validation attempts before fallback or failure. |
| `OPSMIND_PLANNER_FALLBACK_TO_FIXTURE` | `true` | Uses deterministic planning when the model path fails. |
| `OPSMIND_MAX_INVESTIGATION_ROUNDS` | `3` | Hard runtime ceiling for the evidence loop. |
| `OPSMIND_MODEL_INPUT_COST_PER_MILLION` | `0` | Optional local cost-estimation input. |
| `OPSMIND_MODEL_OUTPUT_COST_PER_MILLION` | `0` | Optional local cost-estimation input. |

The application never calculates price from hard-coded current pricing. Configure the optional cost inputs explicitly for the account and model being used.

## Structured planner contract

The OpenAI planner returns:

- An investigation goal
- Two to eight competing hypotheses
- One to twenty evidence requirements
- Preferred read-only tools
- Hypothesis-to-evidence relationships
- Confidence and stopping parameters
- A bounded maximum-round count

A plan is rejected when it selects a tool outside the allow-list, uses malformed or non-sequential IDs, fails to plan evidence for every hypothesis, violates the Pydantic schema, or exceeds the engine's round limit.

## Planner observability

Each investigation stores planner metadata in `planner_usage`, including provider, model, prompt version, request count, token counts, estimated cost when configured, latency, validation attempts, and whether fixture fallback was used. API keys and raw secrets are never included in this metadata.

## Testing the OpenAI path without an API call

The OpenAI boundary is dependency-injected. Unit tests use a fake planner client and therefore do not require credentials or network access.

```bash
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q backend/tests/test_openai_planner.py
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q
ruff check .
```

## Extending planner prompts

Prompt versions live in `backend/app/investigation/planner_prompt.py`. Add a new registered version rather than editing the behavior of an existing version. This preserves reproducibility for saved investigations and demo runs.

The vendor-specific OpenAI call is isolated in `openai_planner_client.py`. Keep provider SDK logic out of the investigation engine and preserve the `PlannerModelClient` contract for testing or future providers.

## OpenAI troubleshooting

**Planner falls back immediately:** confirm `OPSMIND_OPENAI_API_KEY` is set in the same shell that starts the API and `OPSMIND_PLANNER_PROVIDER=openai`.

**Unknown prompt version:** use a registered value such as `planner-v1` or add a new version to the prompt registry.

**Plan repeatedly fails validation:** inspect `planner.validation_or_api_failure` logs. Common causes are unavailable tool names, broken ID sequences, uncovered hypotheses, or a requested round count above the runtime limit.

**Live API unavailable during the demo:** keep `OPSMIND_PLANNER_FALLBACK_TO_FIXTURE=true`. The investigation remains reproducible and records `fallback_used=true`.

## Known limitations

This is a hackathon MVP, not a production deployment. Current limitations include:

- File-based persistence rather than a production database
- No authentication, authorization, or multitenant isolation
- Demo-oriented enterprise evidence adapters
- OpenAI is currently used for planning, not final verdict synthesis
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
