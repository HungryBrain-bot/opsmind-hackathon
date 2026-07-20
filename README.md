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

<p align="center">
<img src="docs/images/demo.gif" width="900" alt="OpsMind Demo"/>
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

Every reasoning round:

- Collects new evidence
- Refines hypotheses
- Rejects weak explanations
- Updates confidence
- Preserves a complete reasoning trace

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

## Multi-Round Investigation Engine

Unlike traditional assistants that stop after one answer, OpsMind reasons iteratively.

```mermaid
flowchart TD
A[Collect Evidence]
-->B[Generate Hypotheses]
-->C[Evaluate Evidence]
-->D{Enough Evidence?}

D -- No --> A
D -- Yes --> E[Evidence-backed Verdict]
```

Each reasoning round can:

- Collect additional telemetry
- Refine hypotheses
- Reject weak explanations
- Increase or decrease confidence
- Record every decision for replay

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

subgraph OpsMind
G[Investigation Engine]
H[Evidence Store]
I[Reasoning Engine]
J[Visual Workspace]
K[Knowledge Base]
end

subgraph OpenAI
L[GPT-5.6]
end

A --> G
B --> G
C --> G
D --> G
E --> G
F --> G

G --> H
H --> L
L --> I
I --> J
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
OpsMind->>Enterprise: Collect evidence
Enterprise-->>OpsMind: Logs & telemetry
OpsMind->>OpenAI: Reason over evidence
OpenAI-->>OpsMind: Updated hypotheses
OpsMind->>Enterprise: Gather additional evidence
Enterprise-->>OpsMind: New findings
OpsMind->>OpenAI: Final reasoning
OpenAI-->>OpsMind: Evidence-backed verdict
OpsMind-->>Engineer: Investigation report
```

---

## Why This Workspace Matters

Traditional tools show data.

Traditional chatbots generate answers.

**OpsMind visualizes the entire investigation.**

Engineers can inspect every hypothesis, every piece of evidence, every confidence update, and every reasoning step before accepting the final verdict.

