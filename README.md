# OpsMind

<p align="center">

# LLMs answer from what they know.
# **OpsMind investigates what your enterprise knows.**

AI-Powered Incident Investigation Engine

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)

</p>

---

## Overview

OpsMind is an AI-powered Incident Investigation Engine that helps platform engineers investigate operational incidents by collecting enterprise evidence, evaluating competing hypotheses, and producing evidence-backed conclusions.

Unlike traditional AI assistants that answer immediately, OpsMind investigates your enterprise before reaching a conclusion.

---

## 🎥 Demo

![OpsMind Demo](docs/images/demo.gif)

---

# Why OpsMind?

During production incidents engineers often spend 30–90 minutes switching between:

- Splunk
- Microsoft Sentinel
- SSH Sessions
- Jira
- Runbooks
- Internal Documentation
- Historical Incidents

The investigation—not the remediation—is usually the slowest part.

OpsMind automates the investigation.

---

# What OpsMind Does

Instead of generating an answer immediately, OpsMind:

- Creates multiple competing hypotheses
- Collects enterprise evidence
- Eliminates incorrect hypotheses
- Explains why hypotheses were rejected
- Produces an evidence-backed verdict
- Generates investigation reports
- Stores investigation history

---

# Demo Scenario

Example Incident

```
INC-2026-0719-001

Heavy Forwarder stopped forwarding logs
```

Possible hidden root causes

- Expired client certificate
- Firewall block
- outputs.conf misconfiguration
- Disk full / blocked queues

The user never selects the root cause.

OpsMind discovers it through investigation.

---

# Features

✅ AI Investigation Engine

✅ Multiple Competing Hypotheses

✅ Enterprise Evidence Collection

✅ Explainable AI

✅ Confidence Evolution

✅ Decision Trace

✅ Investigation History

✅ Report Generation

✅ Scenario Engine

✅ Modern Incident Dashboard

---

# Architecture

```
                   Incident

                       │

                       ▼

            Investigation Planner

                       │

       ┌───────────────┼───────────────┐

       ▼               ▼               ▼

 Configuration     Connectivity     Runtime

       ▼               ▼               ▼

             Enterprise Evidence

                       │

                       ▼

          Hypothesis Evaluation

                       │

                       ▼

           Confidence Evolution

                       │

                       ▼

                Final Verdict

                       │

                       ▼

            Investigation Report
```

---

# Tech Stack

## Backend

- Python
- FastAPI

## Frontend

- HTML
- CSS
- JavaScript

## Testing

- pytest

## Code Quality

- Ruff
- Black

---

# Repository Structure

```
backend/
frontend/
docs/
tests/
data/

README.md
CHANGELOG.md
LICENSE
```

---

# Quick Start

## Clone

```bash
git clone git@github.com:HungryBrain-bot/opsmind-hackathon.git
cd opsmind-hackathon
```

## Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Upgrade pip

```bash
python -m pip install --upgrade pip
```

## Install dependencies

```bash
pip install -e ".[dev]"
```

## Make scripts executable (Linux/macOS)

```bash
chmod +x run-demo.sh

find . -type f -name "*.sh" -exec chmod +x {} \;
```

## Run tests

```bash
pytest -q
```

Expected

```
23 passed
```

## Start OpsMind

```bash
./run-demo.sh
```

Open

```
http://127.0.0.1:8000
```

---

# Demo Walkthrough

1. Open an incident
2. Start Investigation
3. Watch evidence collection
4. Observe competing hypotheses
5. Review rejected hypotheses
6. Review final verdict
7. Download report
8. View Investigation History

---

# Screenshots

## Dashboard

![Dashboard](docs/images/dashboard.png)

---

## Investigation

![Investigation](docs/images/investigation.png)

---

## Final Verdict

![Verdict](docs/images/verdict.png)

---

## Investigation History

![History](docs/images/history.png)

---

# Documentation

| Document | Description |
|-----------|-------------|
| Architecture | System Design |
| Demo Guide | Step-by-step demo |
| API | REST API Reference |
| CONTRIBUTING | Contribution Guide |
| SECURITY | Security Policy |

---

# Troubleshooting

## Permission denied when running run-demo.sh

```bash
chmod +x run-demo.sh
```

---

## pytest not found

Activate the virtual environment

```bash
source .venv/bin/activate
```

---

## ModuleNotFoundError

```bash
pip install -e ".[dev]"
```

---

## Port 8000 already in use

```bash
lsof -i :8000
kill <PID>
```

---

# Roadmap

## Current (v1.6)

- Investigation Engine
- Scenario Engine
- Reports
- Investigation History

## Planned

- Splunk Integration
- Microsoft Sentinel Integration
- Jira Integration
- MCP Support
- Knowledge Graph
- OpenAI Agents SDK
- Multi-Agent Investigation

---

# Traditional AI vs OpsMind

| Traditional AI | OpsMind |
|----------------|----------|
| Answers immediately | Investigates first |
| General knowledge | Enterprise knowledge |
| Single response | Evidence-backed reasoning |
| No investigation | Multi-step investigation |
| Doesn't explain rejected hypotheses | Shows rejected hypotheses |
| Limited operational memory | Investigation History |

---

# Contributing

Contributions are welcome.

Please read **CONTRIBUTING.md**

---

# Security

Please read **SECURITY.md**

---

# License

Licensed under the Apache 2.0 License.

---

# Repository Status

Version

```
v1.6.0
```

Status

```
Hackathon MVP
```

Tests

```
Passing
```

License

```
Apache 2.0
```
