from datetime import UTC, datetime
from app.investigation.explainability import DecisionTraceBuilder
from app.schemas.investigation import InvestigationResult
from app.schemas.report import InvestigationReport, InvestigationReportEvidence

class InvestigationReportBuilder:
    def build(self, result: InvestigationResult) -> InvestigationReport:
        trace = DecisionTraceBuilder().build(result)
        leader = max(result.hypotheses, key=lambda item: item.confidence, default=None)
        return InvestigationReport(
            generated_at=datetime.now(UTC),
            investigation_id=result.investigation_id,
            problem=result.problem,
            environment=getattr(result, "environment", None),
            priority=getattr(result, "priority", None),
            status=result.status.value,
            verdict=result.verdict,
            confidence=leader.confidence if leader else 0.0,
            evidence_strength=result.evidence_strength,
            investigation_completeness=result.investigation_completeness,
            stop_reason=result.stop_reason.summary,
            decision_trace=trace,
            evidence=[
                InvestigationReportEvidence(
                    id=e.id, title=e.title, source=e.source,
                    category=e.category, reliability=e.reliability.value,
                    content=e.content,
                ) for e in result.evidence
            ],
            recommended_actions=result.recommended_actions,
            tools_used=result.tools_used,
            rounds=result.rounds,
            confidence_history=result.confidence_history,
            resolution_plan=result.resolution_plan,
            knowledge_pattern=result.knowledge_pattern,
        )

    def to_markdown(self, result: InvestigationResult) -> str:
        report = self.build(result)
        selected = next((x for x in report.decision_trace.explanations if x.selected), None)
        lines = [
            "# OpsMind Investigation Report", "",
            f"**Investigation ID:** `{report.investigation_id}`  ",
            f"**Generated:** {report.generated_at.isoformat()}  ",
            f"**Status:** {report.status}  ",
            f"**Environment:** {report.environment or 'Not specified'}  ",
            f"**Priority:** {report.priority or 'Not specified'}", "",
            "## Problem", "", report.problem, "",
            "## Verdict", "", report.verdict or "No verdict generated.", "",
            f"**Leading confidence:** {round(report.confidence * 100)}%  ",
            f"**Evidence strength:** {round(report.evidence_strength * 100)}%  ",
            f"**Investigation completeness:** {round(report.investigation_completeness * 100)}%", "",
            "## Why this verdict", "",
            selected.why_selected if selected and selected.why_selected else report.stop_reason, "",
            "## Decision trace", "",
        ]
        for item in report.decision_trace.explanations:
            marker = "SELECTED" if item.selected else "NOT SELECTED"
            lines += [f"### {item.title} — {round(item.confidence * 100)}% [{marker}]", "",
                      item.summary, "", item.why_selected or item.why_not_selected or "", ""]
            if item.supporting_evidence:
                lines += ["**Supporting evidence**", ""]
                lines += [f"- `{e.id}` — {e.title} ({e.source}, {e.reliability})"
                          for e in item.supporting_evidence]
                lines += [""]
            if item.contradicting_evidence:
                lines += ["**Contradicting evidence**", ""]
                lines += [f"- `{e.id}` — {e.title} ({e.source}, {e.reliability})"
                          for e in item.contradicting_evidence]
                lines += [""]
        lines += ["## Evidence ledger", ""]
        for e in report.evidence:
            lines += [f"### {e.id} — {e.title}", "", e.content, "",
                      f"- Source: {e.source}", f"- Category: {e.category}",
                      f"- Reliability: {e.reliability}", ""]
        lines += ["## Investigation rounds", ""]
        for item in report.rounds:
            lines += [
                f"### Round {item.number} — {item.decision.value}", "",
                f"- Objective: {item.objective}",
                f"- Leading hypothesis: {item.leading_hypothesis_id or 'None'}",
                f"- Confidence: {round(item.leading_confidence * 100)}%",
                f"- Decision: {item.decision_reason}", "",
            ]
        lines += ["## Resolution intelligence", ""]
        if report.resolution_plan:
            lines += [f"**Root cause:** {report.resolution_plan.root_cause}", ""]
            for action in report.resolution_plan.actions:
                lines += [
                    f"### {action.stage.value.title()} — {action.action}", "",
                    f"- Why: {action.rationale}",
                    f"- Expected outcome: {action.expected_outcome}",
                    f"- Risk: {action.risk.value}",
                    f"- Confidence: {round(action.confidence * 100)}%",
                    f"- Evidence: {', '.join(action.evidence_ids) or 'None'}",
                ]
                if action.rollback_action:
                    lines.append(f"- Rollback: {action.rollback_action}")
                lines.append("")
            lines += ["### Verification checklist", ""]
            lines += [
                f"- [ ] {item.metric}: {item.condition} — expected {item.expected_value}"
                for item in report.resolution_plan.verification_criteria
            ]
            lines.append("")
        else:
            lines += ["No resolution plan was generated.", ""]
        lines += ["## Recommended actions", ""]
        lines += ([f"{i}. {a}" for i, a in enumerate(report.recommended_actions, 1)]
                  or ["No automated recommendations were generated."])
        if report.knowledge_pattern:
            lines += ["", "## Knowledge capture", "",
                      f"Reusable pattern: **{report.knowledge_pattern.title}**", "",
                      f"Tags: {', '.join(report.knowledge_pattern.tags)}"]
        lines += ["", "## Tools used", ""]
        lines += ([f"- {t}" for t in report.tools_used] or ["- None"])
        lines += ["", "---", "",
                  "Generated by OpsMind. Review conclusions before production changes.", ""]
        return "\n".join(lines)
