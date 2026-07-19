# OpsMind v1.6 Demo Guide

## Goal

Demonstrate that OpsMind is an AI Investigation Engine, not another chatbot.

## Recommended length

Three to five minutes.

## Opening

> A production Splunk Heavy Forwarder has stopped sending logs. Normally, an engineer would move between Splunk, SSH, network tools, Jira, dashboards, and runbooks to determine what failed. OpsMind investigates the incident using the enterprise's own evidence.

## Demo sequence

### 1. Open an incident

Select a realistic incident from the Open Investigation control. Do not describe the hidden root cause.

Emphasize that OpsMind begins with only the symptom and operational context.

### 2. Enable Judge Mode briefly

Use the panel to explain the four differentiators:

- Competing hypotheses
- Targeted enterprise evidence
- Contradiction handling
- Evidence-sufficiency stopping criteria

Close the panel and return to the investigation.

### 3. Start the investigation

Point out the investigation stages and live updates.

Suggested narration:

> OpsMind first creates multiple plausible explanations. It does not commit to a root cause before collecting evidence.

### 4. Show live evidence collection

Highlight checks such as service health, forwarding configuration, connectivity, TLS, queue state, disk state, and historical Jira incidents.

### 5. Show confidence evolution

Explain that every confidence change is connected to evidence rather than being an unexplained model score.

### 6. Show rejected hypotheses

Use the Decision Trace or “Why not?” section.

Suggested narration:

> OpsMind explains not only why the selected hypothesis won, but why firewall, configuration, storage, or indexer explanations were rejected.

### 7. Show the verdict

Review:

- Root cause
- Confidence
- Supporting evidence
- Evidence strength and completeness
- Recommended actions

### 8. Download the report

Show that the investigation creates an auditable artifact containing the evidence, timeline, competing hypotheses, decision trace, verdict, and remediation recommendations.

### 9. Open Investigation History

Reopen the completed incident and demonstrate that the investigation survives beyond the current session.

### 10. Run a second incident

Open another incident and run the same investigation engine. A different evidence path should lead to a different verdict.

This proves the engine is not a single hardcoded certificate-expiry answer.

## Key message

> LLMs answer from what they know. OpsMind investigates what your enterprise knows.

## Avoid saying

- Dataset A, B, C, or D
- Mock data
- JSON fixture
- Hardcoded scenario
- Demo root cause

Use these terms instead:

- Incident
- Enterprise evidence
- Investigation Pack
- Evidence ledger
- Historical incident
- Decision trace
- Investigation history

## Backup plan

Before presenting:

```bash
OPSMIND_DEMO_STAGE_DELAY_SECONDS=0 pytest -q
./run-demo.sh
```

Run each incident once and confirm:

- The UI opens at `http://127.0.0.1:8000`
- Live events progress to a terminal state
- A verdict appears
- Reports download
- History persists and reopens
