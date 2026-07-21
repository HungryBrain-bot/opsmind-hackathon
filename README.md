# OpsMind

<p align="center">

### **AI-Powered Investigation Platform**

## **LLMs answer from what they know.**

# **OpsMind investigates what your enterprise knows.**

<img src="docs/images/hero-banner.png" width="100%" alt="OpsMind Banner"/>

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.6-412991)
![Version](https://img.shields.io/badge/Version-v2.0.0-success)
![Tests](https://img.shields.io/badge/Tests-42%20Passing-brightgreen)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

</p>

---

## 🎬 Golden Demo

### Demo Mode

<p align="center">
<img src="docs/images/demo.gif" width="900" alt="OpsMind Demo"/>
</p>

### Open AI Planner Mode

<p align="center">
<img src="docs/images/demo1.gif" width="900" alt="OpsMind AI Demo"/>
</p>

| Capability | Demo |
|------------|------|
| ⚡ Investigation | Multi-round AI reasoning |
| 🔍 Evidence | Enterprise evidence collection |
| 📈 Confidence | Confidence evolves each round |
| 📖 Replay | Replayable investigations |
| 🧠 Knowledge | Automatic knowledge capture |
| 🤖 AI | OpenAI GPT-5.6 reasoning |

> **Demo metrics represent the bundled Golden Demo and are intended to demonstrate capabilities—not production benchmarks.**

---

## Production incidents don't fail because engineers can't solve problems.

### They fail because engineers spend too much time finding the problem.

OpsMind is an **AI Investigation Platform** built for operational engineering teams.

Instead of producing an immediate answer, OpsMind investigates your enterprise, gathers evidence, evaluates competing hypotheses, and reaches an explainable conclusion.

It combines deterministic engineering with OpenAI reasoning to make investigations transparent, repeatable, and evidence-backed.

---

## The Problem

A modern production investigation often looks like this:

```text
Incident
   │
   ├── Splunk
   ├── Microsoft Sentinel
   ├── Jira
   ├── Confluence
   ├── Configuration Files
   ├── SSH Sessions
   ├── Dashboards
   └── Historical Incidents

        ↓

Hours spent collecting context before solving the issue
```

The investigation—not the remediation—is usually the slowest phase.

---

## Why Not Just Use ChatGPT?

| General AI | OpsMind |
|------------|----------|
| Answers questions | Investigates systems |
| Uses pretrained knowledge | Collects enterprise evidence |
| One response | Multi-round investigation |
| No investigation history | Replayable investigations |
| Cannot reject hypotheses | Rejects weak hypotheses with evidence |

General-purpose LLMs answer from what they already know.

Production incidents are different.

The answer usually exists inside **your enterprise**, not inside the model.

---

## How OpsMind Thinks

Instead of immediately responding, OpsMind:

1. Plans an investigation
2. Generates competing hypotheses
3. Collects enterprise evidence
4. Correlates telemetry
5. Rejects unsupported hypotheses
6. Updates confidence after every reasoning round
7. Produces an evidence-backed verdict
8. Generates remediation guidance
9. Verifies recovery
10. Captures reusable operational knowledge

> ### AI never invents evidence.
>
> Every conclusion must be supported by evidence collected from enterprise systems.

---

## Investigation Lifecycle

```mermaid
flowchart TD
    A[Incident] --> B[Investigation Planner]
    B --> C[Generate Hypotheses]
    C --> D[Collect Enterprise Evidence]
    D --> E[Evaluate Evidence]
    E --> F{Enough Evidence?}
    F -- No --> C
    F -- Yes --> G[Resolution Intelligence]
    G --> H[Verification]
    H --> I[Knowledge Capture]
    I --> J[Replayable Investigation Report]
```

---

## Example Investigation

```text
INC-2026-0719-001

Heavy Forwarder stopped forwarding logs
```

Possible causes:

- Expired certificate
- Firewall block
- outputs.conf misconfiguration
- Disk full
- Blocked forwarding queues
- Authentication failure

The engineer never selects the root cause.

**OpsMind discovers it through investigation.**

---

## Investigation Engine

OpsMind separates **AI planning** from **deterministic investigation execution**.

The investigation begins with an AI-generated investigation plan that identifies the most likely hypotheses and the evidence required to validate or reject them.

OpsMind then executes that plan deterministically by:

- Collecting enterprise evidence
- Correlating findings across sources
- Tracking investigation confidence
- Rejecting unsupported hypotheses
- Preserving a complete investigation trace

The investigation continues until sufficient trustworthy evidence exists to defend the final conclusion.

---

## Product Vision

Engineers don't need another chatbot.

They need an investigation partner that understands enterprise systems, reasons over evidence, explains every decision, and makes every future investigation faster.

**OpsMind is building that future.**

## 🖥️ Visual Investigation Workspace

OpsMind is built around a **visual investigation workspace**, not a chat window.

Every investigation becomes a living workspace where evidence, hypotheses, confidence, and decisions evolve together.

---

## Workspace Overview

```mermaid
flowchart LR
    A[Incident] --> B[Timeline]
    B --> C[Evidence Graph]
    C --> D[Hypothesis Board]
    D --> E[Confidence Evolution]
    E --> F[Resolution Intelligence]
    F --> G[Verification]
    G --> H[Knowledge Capture]
```

---

## Workspace Components

| Component | Purpose |
|-----------|---------|
| 🕒 Timeline | Shows every investigation step chronologically |
| 🕸️ Evidence Graph | Visualizes relationships between evidence |
| 🧠 Hypothesis Board | Tracks competing root-cause theories |
| 📈 Confidence Evolution | Shows confidence changing over time |
| 🛠️ Resolution Intelligence | AI-assisted remediation guidance |
| ✅ Verification Dashboard | Confirms the incident is actually resolved |

Together these views allow engineers to understand **how** OpsMind reached a conclusion—not just **what** the conclusion was.

---

# Workspace Preview

### Dashboard

![Dashboard](docs/images/dashboard.png)

---

### Investigation Workspace

![Workspace](docs/images/workspace.png)

---

### Evidence Graph

![Evidence Graph](docs/images/graph.png)

---

### Investigation Timeline

![Timeline](docs/images/timeline.png)

---

### Confidence Evolution

![Confidence](docs/images/confidence.png)

---

### Hypothesis Board

![Hypothesis Board](docs/images/hypothesis.png)

---

### Resolution Intelligence

![Resolution](docs/images/resolution.png)

---

### Verification Dashboard

![Verification](docs/images/verification.png)

---

## AI-Planned Investigation Engine

Unlike traditional assistants that immediately produce an answer, OpsMind first generates a structured investigation plan using OpenAI. The investigation engine then executes that plan through deterministic evidence collection, correlation, confidence tracking, and sufficiency evaluation.

```mermaid
flowchart TD

A[Engineer Starts Investigation]
--> B[OpenAI Generates Investigation Plan]
--> C[OpsMind Investigation Engine]
--> D[Collect Enterprise Evidence]
--> E[Correlate Findings]
--> F[Update Confidence]
--> G{Enough Evidence?}

G -- No --> D
G -- Yes --> H[Evidence-backed Investigation Report]
```

Each investigation round can:

- Collect additional enterprise evidence
- Correlate findings from multiple sources
- Reject unsupported hypotheses
- Update investigation confidence
- Record every investigation step for replay and auditing

---

## Resolution Intelligence

Finding the root cause is only part of the investigation.

OpsMind also produces structured remediation guidance.

```mermaid
flowchart LR
RootCause --> Resolution
Resolution --> Validation
Validation --> Verification
Verification --> Knowledge
```

Every recommendation is linked back to the evidence that justified it.

---

## Verification

OpsMind treats verification as a first-class investigation stage.

Before an incident is considered resolved it can verify:

- Service health
- Data ingestion
- Alert recovery
- Queue status
- Connectivity
- Platform health

This helps reduce false recoveries.

---

## Knowledge Capture

Every completed investigation becomes organizational knowledge.

Captured artifacts include:

- Incident summary
- Evidence collected
- Final verdict
- Resolution
- Verification results
- Lessons learned

Future investigations benefit from everything learned previously.

---

## Investigation Playback

Every investigation is replayable from start to finish.

Benefits include:

- Explainability
- Auditability
- Training
- Incident reviews
- Faster onboarding

No reasoning step is hidden.

---

## Built with OpenAI

OpsMind combines deterministic engineering with OpenAI reasoning.

| Deterministic Platform | OpenAI Reasoning |
|------------------------|------------------|
| Evidence collection | Investigation planning |
| Connector execution | Hypothesis generation |
| Configuration parsing | Evidence interpretation |
| Log & telemetry retrieval | Root cause reasoning |
| Verification | Executive summaries |

> OpenAI never invents evidence. It reasons only over enterprise evidence collected by OpsMind.

---

## High-Level Architecture

```mermaid
flowchart LR

subgraph Enterprise
A[Splunk]
B[Microsoft Sentinel]
C[Jira]
D[Runbooks]
E[Configuration Files]
F[Cloud APIs]
end

subgraph OpenAI
L[OpenAI Planner]
end

subgraph OpsMind
G[Investigation Engine]
H[Evidence Store]
J[Visual Workspace]
K[Knowledge Base]
end

L --> G

A --> G
B --> G
C --> G
D --> G
E --> G
F --> G

G --> H
H --> J
J --> K
```

---

## Investigation Pipeline

```mermaid
sequenceDiagram

participant Engineer
participant OpsMind
participant Enterprise
participant OpenAI

Engineer->>OpsMind: Start Investigation
OpsMind->>OpenAI: Generate Investigation Plan
OpenAI-->>OpsMind: Structured Investigation Plan

loop Investigation Rounds
OpsMind->>Enterprise: Collect Evidence
Enterprise-->>OpsMind: Logs, Telemetry & Configuration
OpsMind->>OpsMind: Correlate Findings
OpsMind->>OpsMind: Update Confidence
OpsMind->>OpsMind: Evaluate Sufficiency
end

OpsMind-->>Engineer: Evidence-backed Investigation Report
```

---

## Why This Workspace Matters

Traditional tools show data.

Traditional chatbots generate answers.

**OpsMind visualizes the entire investigation.**

Engineers can inspect every hypothesis, every piece of evidence, every confidence update, and every reasoning step before accepting the final verdict.

## 🚀 Quick Start

### Clone the Repository

```bash
git clone git@github.com:HungryBrain-bot/opsmind-hackathon.git
cd opsmind-hackathon
```

### Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### Run the Test Suite

```bash
pytest -q
```

Expected output:

```text
42 passed
```

## ▶️ Running OpsMind

OpsMind supports two execution modes.

---

### 1. Golden Demo (Recommended)

Runs the bundled investigation without requiring an OpenAI API key.

```bash
./run-demo.sh
```

Open:

```text
http://127.0.0.1:8000
```

This mode is ideal for:

- Demo recordings
- GitHub evaluation
- Offline demonstrations
- Predictable investigations

---

### 2. AI Investigation Mode

Runs OpsMind using OpenAI reasoning models.

First configure your API key:

```bash
export OPENAI_API_KEY="sk-your-api-key"
```

or 

```bash
export OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
./run-ai.sh
```

Then start AI mode:

```bash
./run-ai.sh
```

Open:

```text
http://127.0.0.1:8000
```

This mode enables:

- AI investigation planning
- Multi-round reasoning
- Evidence interpretation
- Executive summaries
- GPT-powered root cause analysis
```

---

## 📂 Repository Structure

```text
backend/
├── api/
├── core/
├── investigation/
├── knowledge/
├── schemas/

frontend/
docs/
tests/
data/

README.md
LICENSE
CHANGELOG.md
```

---

## 🧪 Features

### Investigation

- Multi-round reasoning
- Competing hypotheses
- Confidence evolution
- Evidence-backed verdicts
- Replayable investigations

### Workspace

- Dashboard
- Timeline
- Evidence Graph
- Hypothesis Board
- Resolution Intelligence
- Verification Dashboard

### AI

- GPT-5.6 reasoning
- Structured investigation planning
- Executive summaries
- Explainable AI

### Knowledge

- Investigation history
- Knowledge capture
- Lessons learned
- Reusable operational memory

---

## 🌐 REST API

| Endpoint | Description |
|----------|-------------|
| `/health` | Health check |
| `/investigations` | Create investigation |
| `/investigations/{id}` | Investigation details |
| `/workspace/{id}` | Workspace data |
| `/knowledge` | Investigation knowledge |
| `/docs` | Interactive API documentation |

---

## 🎯 Golden Demo Walkthrough

1. Select the bundled incident.
2. Start the investigation.
3. Observe hypotheses being generated.
4. Watch evidence collection.
5. Review confidence evolution.
6. Open the Evidence Graph.
7. Inspect Resolution Intelligence.
8. Verify recovery.
9. Replay the investigation.
10. Review captured knowledge.

---

## 🏆 Judge Guide (5 Minutes)

| Time | Demonstration |
|------|---------------|
| 0:00–0:45 | Problem statement |
| 0:45–1:30 | Start investigation |
| 1:30–2:30 | Workspace & reasoning |
| 2:30–3:30 | Evidence graph & confidence |
| 3:30–4:30 | Resolution & verification |
| 4:30–5:00 | Knowledge capture & vision |

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `ARCHITECTURE.md` | Technical architecture |
| `API.md` | REST API reference |
| `DEMO_GUIDE.md` | Demo walkthrough |
| `CONTRIBUTING.md` | Contribution guide |
| `SECURITY.md` | Security policy |

---

## 🛣️ Roadmap

### v2.0.0 (Current)

- ✅ AI Investigation Engine
- ✅ Visual Investigation Workspace
- ✅ Multi-round reasoning
- ✅ Resolution Intelligence
- ✅ Knowledge Capture
- ✅ Investigation Playback
- ✅ Golden Demo

### Next

- Splunk Connector
- Microsoft Sentinel Connector
- Jira Connector
- Confluence Connector
- Kubernetes Connector

### Future Vision

- MCP integration
- Knowledge Graph
- Multi-agent investigations
- Autonomous remediation
- Continuous operational learning

---

## 🤝 Contributing

Contributions are welcome.

Please read **CONTRIBUTING.md** before submitting issues or pull requests.

---

## 🔒 Security

Please refer to **SECURITY.md** for responsible disclosure guidelines.

---

## 📄 License

Licensed under the **Apache License 2.0**.

---

## ❤️ Why We Built OpsMind

Modern AI is excellent at answering questions.

We believe the next generation of AI should investigate before it answers.

OpsMind is our vision for an AI partner that helps engineers understand complex systems, reason over evidence, explain every decision, and continuously learn from every incident.

---

## 📊 Repository Status

| Item | Status |
|------|--------|
| Version | **v2.0.0** |
| Status | **OpenAI Hackathon MVP** |
| Tests | **42 Passing** |
| Python | **3.11+** |
| License | **Apache 2.0** |

---

<p align="center">

**LLMs answer from what they know.**

**OpsMind investigates what your enterprise knows.**

Made with ❤️ using Python, FastAPI and OpenAI.

</p>

