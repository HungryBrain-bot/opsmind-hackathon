# OpsMind

```{=html}
<p align="center">
```
# LLMs answer from what they know.

# **OpsMind investigates what your enterprise knows.**

### AI-Powered Investigation Platform powered by OpenAI

```{=html}
<p align="center">
```
`<img src="docs/images/hero-banner.png" width="100%">`{=html}
```{=html}
</p>
```
```{=html}
<p align="center">
```
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.6-412991)
![Version](https://img.shields.io/badge/Version-v2.0.0-success)
![Tests](https://img.shields.io/badge/Tests-42%20Passing-brightgreen)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

```{=html}
</p>
```

------------------------------------------------------------------------

# 🎬 Demo

```{=html}
<p align="center">
```
`<img src="docs/images/demo.gif" width="900">`{=html}
```{=html}
</p>
```

------------------------------------------------------------------------

# 🚀 Demo Highlights

  Feature                   Value
  ------------------------- --------------------------------------
  ⚡ Golden Investigation   \~2 minute investigation walkthrough
  🧠 AI Investigation       Multi-round reasoning
  🔍 Evidence               Evidence-backed conclusions
  📈 Confidence             Confidence evolves every round
  📖 Replay                 Complete investigation playback
  🧩 Knowledge              Automatic knowledge capture
  🤖 AI                     Powered by OpenAI GPT-5.6

> **Demo metrics are measured using the bundled Golden Demo scenario.
> They demonstrate product capabilities rather than production
> benchmarks.**

------------------------------------------------------------------------

# Overview

OpsMind is an **AI-powered Investigation Platform** that helps platform
engineers investigate operational incidents using enterprise evidence
instead of assumptions.

Unlike traditional AI assistants that answer immediately, OpsMind
investigates your environment before reaching a conclusion.

It plans investigations, evaluates competing hypotheses, correlates
operational evidence, produces explainable conclusions, verifies
recovery, and captures knowledge for future investigations.

The result is not simply another chatbot.

It is an **AI Investigation Engine.**

------------------------------------------------------------------------

# The Problem

During production incidents engineers spend valuable time switching
between multiple systems before they can even begin reasoning about the
problem.

Typical investigation sources include:

-   Splunk
-   Microsoft Sentinel
-   Jira
-   Confluence
-   Configuration Files
-   Cloud Consoles
-   SSH Sessions
-   Dashboards
-   Historical Incidents
-   Internal Runbooks

The investigation---not the remediation---is usually the slowest part.

------------------------------------------------------------------------

# Why Not Just Use ChatGPT?

General-purpose LLMs answer from what they already know.

Production incidents are different.

The answer rarely exists inside the model.

It exists inside **your enterprise.**

OpsMind doesn't ask AI to guess.

OpsMind asks AI to investigate.

Instead of immediately producing an answer, OpsMind:

1.  Plans an investigation
2.  Generates competing hypotheses
3.  Collects enterprise evidence
4.  Correlates operational telemetry
5.  Rejects incorrect hypotheses
6.  Evolves confidence over multiple reasoning rounds
7.  Produces an evidence-backed verdict
8.  Generates a resolution
9.  Verifies recovery
10. Captures operational knowledge

The result is not simply an AI response.

It is a transparent, replayable investigation.

------------------------------------------------------------------------

# What Makes OpsMind Different?

  ----------------------------------------------------------------------------
  Traditional AI      Retrieval-Augmented Generation         OpsMind
  ------------------- -------------------------------------- -----------------
  Answers immediately Retrieves documents                    Plans
                                                             investigations

  Uses pretrained     Uses retrieved context                 Builds enterprise
  knowledge                                                  evidence

  Single response     Context-aware response                 Multi-round
                                                             reasoning

  No investigation    Limited memory                         Persistent
  state                                                      investigation
                                                             lifecycle

  Cannot reject       Returns retrieved information          Rejects incorrect
  hypotheses                                                 hypotheses

  No operational      Limited to retrieved context           Captures
  memory                                                     investigation
                                                             knowledge

  No replay           No replay                              Replayable
                                                             investigations

  No confidence       No confidence evolution                Evidence-driven
  evolution                                                  confidence
                                                             tracking
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

# Why This Matters

Traditional AI helps engineers answer questions.

OpsMind helps engineers answer the **right question**.

Instead of asking:

> "What caused this incident?"

OpsMind first determines:

-   What evidence exists?
-   Which hypotheses are possible?
-   Which evidence supports each hypothesis?
-   Which evidence rejects them?
-   Is there enough evidence to reach a verdict?

Only then does it produce a conclusion.

------------------------------------------------------------------------

# The OpsMind Philosophy

> **AI never invents evidence.**

OpsMind reasons only over evidence collected from enterprise systems.

Every conclusion must be explainable.

Every decision must be traceable.

Every investigation must be replayable.

Every investigation should make the next investigation faster.

------------------------------------------------------------------------

# Product Vision

Engineers don't need another chatbot.

They need an investigation partner capable of understanding enterprise
systems, collecting evidence, evolving hypotheses, and explaining every
decision.

OpsMind combines enterprise operational knowledge with OpenAI reasoning
to transform incident response from reactive troubleshooting into
evidence-driven investigations.

------------------------------------------------------------------------

# Example Investigation

``` text
INC-2026-0719-001

Heavy Forwarder stopped forwarding logs
```

Possible hidden causes:

-   Expired client certificate
-   Firewall block
-   outputs.conf misconfiguration
-   Disk full
-   Blocked forwarding queues
-   Network connectivity
-   Authentication failure

The engineer never selects the root cause.

OpsMind discovers it through investigation.

------------------------------------------------------------------------

# Investigation Lifecycle

``` text
Incident
    ↓
Investigation Planner
    ↓
Generate Competing Hypotheses
    ↓
Collect Enterprise Evidence
    ↓
Evaluate Evidence
    ↓
Confidence Evolution
    ↓
Enough Evidence?
 ├── No → Continue Investigation
 └── Yes
        ↓
Resolution Intelligence
        ↓
Verification
        ↓
Knowledge Capture
        ↓
Replayable Investigation Report
```

------------------------------------------------------------------------

# Investigation Engine

OpsMind continuously reasons across multiple rounds.

Every reasoning round:

-   Collects additional evidence
-   Refines hypotheses
-   Updates confidence
-   Rejects impossible explanations
-   Records the investigation state

Unlike traditional AI assistants, reasoning does not stop after the
first response.

The investigation continues until enough trustworthy evidence exists to
defend the final conclusion.
