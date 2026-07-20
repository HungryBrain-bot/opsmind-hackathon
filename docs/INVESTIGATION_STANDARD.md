# OpsMind Investigation Standard

## Purpose

This document defines how OpsMind conducts evidence-backed enterprise investigations. Code, prompts, tool adapters, and user interfaces should remain consistent with this standard.

## Core principles

- Evidence first; reasoning second; conclusion last.
- Never invent evidence or conceal uncertainty.
- Keep observations separate from interpretations and recommendations.
- Test competing hypotheses and actively seek disconfirming evidence.
- Reference evidence IDs for every material finding.
- Prefer independent corroboration over repeated evidence from one source.
- Human approval remains required for remediation or write actions.

## Evidence assessment

Each item is classified as supporting, contradicting, neutral, inconclusive, or duplicate. Quality is assessed from source reliability, recency, completeness, and independence. Low-quality evidence may guide the next collection step but should not independently justify a verdict.

## Contradictions

A contradiction exists when credible evidence supports and contradicts the same hypothesis. High-reliability contradictions remain unresolved until additional evidence explains the conflict. OpsMind must record the conflict instead of silently choosing one source.

## Confidence policy

Numerical confidence is controlled by deterministic code. Confidence can increase only when new supporting evidence is recorded and can decrease when credible contradicting evidence appears. Every change is stored with its previous value, new value, evidence IDs, reason, and timestamp.

## Stopping criteria

A verdict is defensible only when all configured sufficiency rules pass. The current MVP requires corroborating evidence, independent categories, a current operational observation, no unresolved high-reliability contradiction, and a leading hypothesis above the confidence threshold.

The structured reasoner may recommend stopping or continuing, but it cannot override the deterministic policy.

## Required investigation outputs

Each completed reasoning round should preserve:

- evidence assessments;
- evidence-cited findings;
- contradictions;
- missing evidence and expected impact;
- the leading hypothesis;
- the continue/stop recommendation;
- model usage and prompt version when a model is used.

## Failure and fallback

Invalid structured output, unknown evidence references, unavailable credentials, and model failures are rejected. When configured, OpsMind falls back to the fixture reasoner so the investigation remains bounded and demonstrable.
