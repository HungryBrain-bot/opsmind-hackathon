# OpsMind Investigation Lifecycle

## Purpose

OpsMind investigates until it can defend a conclusion or until its bounded evidence budget is exhausted. A relevant observation is not automatically sufficient evidence.

## Lifecycle

1. **Intake** — normalize the incident problem, environment, priority, and scenario.
2. **Planning** — create hypotheses and prioritized evidence requirements.
3. **Evidence collection** — execute allow-listed, read-only tools.
4. **Reasoning** — attach supporting and contradicting evidence and recalculate confidence.
5. **Hypothesis evolution** — promote, reject, wait, or retain hypotheses.
6. **Sufficiency decision** — resolve, continue, or stop inconclusive.
7. **Resolution intelligence** — create evidence-backed remediation guidance.
8. **Verification planning** — define measurable recovery checks.
9. **Knowledge capture** — create a reusable incident pattern.
10. **Complete** — expose the verdict, resolution, timeline, and audit trail.

## Round contract

Every round records:

- round number and timestamps;
- objective and evidence requirement IDs;
- evidence collected during that round;
- leading hypothesis and confidence;
- remaining evidence gaps;
- decision and decision reason.

## Hypothesis lifecycle

- **Supported:** confidence is at least 0.80 with corroborating evidence.
- **Rejected:** confidence is at most 0.20 and contradictory evidence exists.
- **Waiting:** no evidence currently supports or contradicts the hypothesis.
- **Active:** the hypothesis remains plausible but not yet defensible.

## Stopping policy

The engine stops successfully only when the configured evidence sufficiency policy passes. Otherwise it continues while evidence rounds remain. When the round budget is exhausted, the investigation becomes inconclusive rather than inventing a conclusion.

## Resolution contract

Each resolution action includes:

- action stage;
- action statement;
- evidence-backed rationale;
- expected outcome;
- referenced evidence IDs;
- confidence;
- risk;
- approval requirement;
- rollback guidance where applicable.

The standard stages are containment, recovery, verification, rollback, and prevention. The MVP may represent rollback guidance directly on the relevant recovery action.

## Verification

A recommendation is not treated as a confirmed recovery. OpsMind produces pending verification criteria that an engineer or future approved automation must evaluate after remediation.

## Knowledge capture

Completed investigations generate a reusable `KnowledgePattern`. This is the foundation for retrieving similar prior incidents, runbooks, and known fixes in later versions.
