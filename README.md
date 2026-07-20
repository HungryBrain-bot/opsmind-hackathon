
# OpsMind

> **AI Investigation Platform powered by OpenAI**

> **LLMs answer questions. OpsMind investigates enterprise incidents.**

![Banner](docs/images/hero-banner.png)

## Demo

![Demo](docs/images/demo.gif)

## Demo Highlights

| Metric | Value |
|---|---|
| Golden Demo | ~2 minute walkthrough |
| Multi-round reasoning | ✅ |
| Evidence-backed conclusions | ✅ |
| Confidence evolution | ✅ |
| Knowledge capture | ✅ |
| Investigation replay | ✅ |
| Powered by | OpenAI GPT-5.6 |

## The Problem

Engineers investigate incidents across multiple tools, manually correlating evidence and documenting findings.

## The Solution

OpsMind performs structured investigations by planning, collecting evidence, evolving hypotheses, producing resolutions, verifying recovery, and capturing knowledge.

## Why OpsMind?

| Traditional AI | OpsMind |
|---|---|
| Answers prompts | Conducts investigations |
| Static response | Multi-round reasoning |
| No replay | Replayable investigations |
| No knowledge memory | Knowledge capture |

## Product Images

Replace these placeholders:

- docs/images/dashboard.png
- docs/images/workspace.png
- docs/images/graph.png
- docs/images/timeline.png
- docs/images/confidence.png
- docs/images/hypothesis.png
- docs/images/resolution.png
- docs/images/verification.png
- docs/images/architecture.png
- docs/images/golden-demo.png

## Investigation Workflow

```text
Incident
 ↓
Planning
 ↓
Evidence
 ↓
Reasoning
 ↓
Hypothesis Evolution
 ↓
Confidence
 ↓
Resolution
 ↓
Verification
 ↓
Knowledge Capture
```

## Built with OpenAI

GPT-5.6 is used for:

- Investigation planning
- Evidence reasoning
- Hypothesis evolution
- Executive summaries

Codex was used throughout development for implementation, refactoring, testing, and documentation.

## Architecture

![Architecture](docs/images/architecture.png)

## Demo Metrics

| Metric | Demo |
|---|---:|
| Walkthrough | ~2 minutes |
| Evidence traceability | Visible |
| Replay | Yes |
| Knowledge capture | Automatic |

## Installation

```bash
git clone <repo>
cd opsmind-hackathon
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.6
OPSMIND_DEMO_MODE=true
```

## Run

```bash
uvicorn backend.app.main:app --reload
```

## Test

```bash
ruff check .
ruff format --check .
pytest -q
```

## API

- GET /health
- POST /investigations
- GET /investigations/{id}
- GET /investigations/{id}/workspace

## Judge Guide

1. Problem
2. Golden Demo
3. Investigation Workspace
4. GPT-5.6 reasoning
5. Knowledge Capture

## Roadmap

- Multi-agent investigations
- MCP integrations
- Cross-incident intelligence
- Autonomous remediation (human approval)

## Why We Built OpsMind

Engineers don't need another chatbot—they need an investigation partner that combines enterprise operational knowledge with OpenAI reasoning.

## License

MIT (recommended)
