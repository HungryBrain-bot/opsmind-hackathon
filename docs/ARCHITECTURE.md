# OpsMind Architecture

## Purpose

OpsMind is an evidence-first investigation engine. Its job is not to generate the first plausible answer. Its job is to gather enough corroborated evidence to defend a conclusion and explain why competing explanations were rejected.

## High-level flow

```text
Incident
  │
  ▼
Investigation Pack
  │
  ▼
Planner
  │
  ▼
Tool Registry / MCP Boundary
  │
  ▼
Evidence Normalization
  │
  ▼
Evidence Ledger
  ├── Notebook
  ├── Timeline
  ├── Confidence Evolution
  └── Evidence Graph
  │
  ▼
Hypothesis Evaluator
  │
  ▼
Evidence Sufficiency
  │
  ▼
Verdict and Decision Trace
  │
  ▼
Reports and Persistent History
```

## Main components

### Investigation API

FastAPI exposes investigation creation, live SSE events, current state, timeline, notebook, decision trace, reports, and history endpoints.

### Investigation Engine

The engine coordinates the investigation lifecycle:

1. Create the initial incident state.
2. Generate competing hypotheses.
3. Produce an investigation plan.
4. Invoke allowed tools.
5. Normalize returned observations into evidence.
6. Update hypothesis confidence.
7. Evaluate contradictions and rejection conditions.
8. Apply evidence-sufficiency rules.
9. Produce a verdict or an inconclusive result.
10. Persist the terminal snapshot and report.

### Investigation Packs

Packs contain domain-specific knowledge while keeping the core engine reusable. The v1.6 release contains a Splunk Heavy Forwarder pack with multiple realistic incident paths.

A pack can define:

- Candidate hypotheses
- Investigation steps
- Allowed tools
- Evidence interpretation rules
- Domain-specific remediation recommendations

### Tool Registry and MCP boundary

Tools are allow-listed rather than called directly by unconstrained model output. This boundary supports deterministic local tools today and MCP-backed enterprise adapters later.

The intended production flow is:

```text
Planner request → validated tool name → validated arguments → adapter execution
→ normalized evidence → immutable event → hypothesis update
```

### Evidence ledger

Every meaningful observation is stored with source metadata and relationships to hypotheses. The ledger powers the notebook, evidence graph, decision trace, reports, and history.

### Confidence evolution

Confidence is not shown as an unexplained final percentage. Each update records why confidence changed and which evidence caused the change.

### Evidence sufficiency

The investigation stops when enough trustworthy and corroborated evidence exists to defend a conclusion, not when the first relevant document appears.

### Persistence

`FileInvestigationRepository` stores terminal investigations under:

```text
data/investigations/<investigation-id>/
├── investigation.json
└── report.md
```

The repository abstraction keeps the investigation engine independent from the file implementation so a database can replace it later.

## Runtime modes

### Deterministic offline mode

Uses repeatable local evidence paths for demonstrations and tests. No external API key is required.

### OpenAI-assisted planning mode

OpenAI can propose a plan, but the OpsMind engine remains responsible for tool authorization, evidence normalization, confidence updates, sufficiency checks, and the audit trail.

## Safety model

The MVP is read-only by design. Future remediation should require:

- Explicit human approval
- Approved runbooks
- Scoped credentials
- Complete audit logging
- Post-action verification

## Future production extensions

- Authenticated multi-user API
- Tenant-isolated persistence
- Real Splunk, Sentinel, Jira, Confluence, and cloud adapters
- Durable event bus
- Production database and object storage
- Secrets manager
- RBAC and approval workflows
- Observability and analytics

## Step 5: Multi-round lifecycle and resolution boundary

The investigation engine now owns a complete deterministic lifecycle:

```text
Planner
  ↓
Read-only evidence tools
  ↓
Hypothesis evaluator
  ↓
Hypothesis lifecycle manager
  ↓
Evidence sufficiency policy
  ├── insufficient → next evidence round
  └── sufficient   → resolution intelligence
                         ↓
                  verification plan
                         ↓
                   knowledge capture
```

### Deterministic ownership

The following decisions remain in code rather than unconstrained model output:

- maximum investigation rounds;
- evidence sufficiency and stop decisions;
- confidence calculation;
- hypothesis promotion, waiting, and rejection;
- lifecycle state transitions;
- human-approval requirements;
- event ordering and persisted audit state.

### Resolution intelligence

`ResolutionIntelligenceService` converts an evidence-backed verdict into structured actions. Each action carries its stage, rationale, expected outcome, evidence references, confidence, risk, approval requirement, and rollback guidance.

### Operational memory

`KnowledgeCaptureService` creates a reusable knowledge pattern from a completed investigation. It stores symptoms, root cause, resolution summary, verification targets, entities, evidence categories, tags, and confidence. The MVP stores the object in the investigation result; a future retrieval layer can index these patterns for case-based planning.
