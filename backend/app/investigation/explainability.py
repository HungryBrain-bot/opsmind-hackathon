from app.schemas.explainability import (
    EvidenceReference,
    HypothesisDecisionExplanation,
    InvestigationDecisionTrace,
)
from app.schemas.investigation import InvestigationResult


class DecisionTraceBuilder:
    """Builds user-facing decision explanations from persisted investigation facts."""

    def build(self, result: InvestigationResult) -> InvestigationDecisionTrace:
        if not result.hypotheses:
            return InvestigationDecisionTrace(
                investigation_id=result.investigation_id,
                verdict=result.verdict,
                stop_summary=result.stop_reason.summary,
            )

        selected = max(result.hypotheses, key=lambda item: item.confidence)
        evidence_by_id = {item.id: item for item in result.evidence}
        explanations = []

        for hypothesis in sorted(
            result.hypotheses, key=lambda item: item.confidence, reverse=True
        ):
            supporting = [
                self._reference(evidence_by_id[evidence_id])
                for evidence_id in hypothesis.supporting_evidence_ids
                if evidence_id in evidence_by_id
            ]
            contradicting = [
                self._reference(evidence_by_id[evidence_id])
                for evidence_id in hypothesis.contradicting_evidence_ids
                if evidence_id in evidence_by_id
            ]
            is_selected = hypothesis.id == selected.id
            summary = self._summary(
                confidence=hypothesis.confidence,
                support_count=len(supporting),
                contradiction_count=len(contradicting),
                selected=is_selected,
            )

            explanations.append(
                HypothesisDecisionExplanation(
                    hypothesis_id=hypothesis.id,
                    title=hypothesis.title,
                    selected=is_selected,
                    status=hypothesis.status.value,
                    confidence=hypothesis.confidence,
                    summary=summary,
                    supporting_evidence=supporting,
                    contradicting_evidence=contradicting,
                    missing_evidence=self._missing_evidence(result, hypothesis.id),
                    why_selected=self._why_selected(hypothesis.title, supporting)
                    if is_selected
                    else None,
                    why_not_selected=self._why_not_selected(
                        hypothesis.title,
                        hypothesis.rejection_reason,
                        supporting,
                        contradicting,
                        selected.title,
                        selected.confidence,
                        hypothesis.confidence,
                    )
                    if not is_selected
                    else None,
                )
            )

        return InvestigationDecisionTrace(
            investigation_id=result.investigation_id,
            selected_hypothesis_id=selected.id,
            verdict=result.verdict,
            stop_summary=result.stop_reason.summary,
            explanations=explanations,
        )

    @staticmethod
    def _reference(item):
        return EvidenceReference(
            id=item.id,
            title=item.title,
            source=item.source,
            reliability=item.reliability.value,
            current=item.current,
        )

    @staticmethod
    def _summary(
        confidence: float,
        support_count: int,
        contradiction_count: int,
        selected: bool,
    ) -> str:
        role = "Leading explanation" if selected else "Alternative explanation"
        return (
            f"{role} with {round(confidence * 100)}% confidence, "
            f"{support_count} supporting evidence item(s), and "
            f"{contradiction_count} contradicting evidence item(s)."
        )

    @staticmethod
    def _why_selected(title: str, supporting: list[EvidenceReference]) -> str:
        high_quality = [
            item.title for item in supporting if item.reliability == "high" and item.current
        ]
        if high_quality:
            return (
                f"{title} was selected because multiple current, high-reliability facts "
                f"corroborate it: {'; '.join(high_quality)}."
            )
        return (
            f"{title} was selected because it had the strongest evidence-backed confidence "
            "when the sufficiency rules were satisfied."
        )

    @staticmethod
    def _why_not_selected(
        title: str,
        rejection_reason: str | None,
        supporting: list[EvidenceReference],
        contradicting: list[EvidenceReference],
        selected_title: str,
        selected_confidence: float,
        confidence: float,
    ) -> str:
        if rejection_reason:
            return rejection_reason
        if contradicting:
            return (
                f"{title} was not selected because evidence contradicted it: "
                + "; ".join(item.title for item in contradicting)
                + "."
            )
        if not supporting:
            return (
                f"{title} was not selected because no collected evidence directly supported it, "
                f"while {selected_title} reached {round(selected_confidence * 100)}% confidence."
            )
        gap = max(0, round((selected_confidence - confidence) * 100))
        return (
            f"{title} had some support but remained {gap} confidence points below "
            f"{selected_title} and did not become the best-supported explanation."
        )

    @staticmethod
    def _missing_evidence(result: InvestigationResult, hypothesis_id: str) -> list[str]:
        missing = []
        used_tools = set(result.tools_used)
        for requirement in result.planned_evidence:
            if (
                hypothesis_id in requirement.get("hypothesis_ids", [])
                and requirement.get("preferred_tool") not in used_tools
            ):
                missing.append(requirement.get("description", "Uncollected evidence"))
        return missing
