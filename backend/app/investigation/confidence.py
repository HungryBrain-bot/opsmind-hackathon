from datetime import datetime, timezone

from app.schemas.confidence import ConfidenceChange, ConfidenceDirection
from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis


class ConfidenceEvolutionService:
    """Creates an auditable confidence history without exposing private model reasoning."""

    def initialize(self, hypothesis: Hypothesis) -> None:
        if hypothesis.confidence_history:
            return
        hypothesis.confidence_history.append(
            ConfidenceChange(
                sequence=1,
                hypothesis_id=hypothesis.id,
                previous_confidence=hypothesis.confidence,
                new_confidence=hypothesis.confidence,
                direction=ConfidenceDirection.INITIAL,
                reason="Initial confidence assigned by the investigation planner.",
                timestamp=datetime.now(timezone.utc),
            )
        )

    def record(
        self,
        hypothesis: Hypothesis,
        previous_confidence: float,
        previous_supporting_ids: set[str],
        previous_contradicting_ids: set[str],
        evidence_by_id: dict[str, Evidence],
    ) -> ConfidenceChange:
        new_supporting = [
            evidence_id
            for evidence_id in hypothesis.supporting_evidence_ids
            if evidence_id not in previous_supporting_ids
        ]
        new_contradicting = [
            evidence_id
            for evidence_id in hypothesis.contradicting_evidence_ids
            if evidence_id not in previous_contradicting_ids
        ]
        evidence_ids = new_supporting + new_contradicting

        if hypothesis.confidence > previous_confidence:
            direction = ConfidenceDirection.INCREASED
        elif hypothesis.confidence < previous_confidence:
            direction = ConfidenceDirection.DECREASED
        else:
            direction = ConfidenceDirection.UNCHANGED

        reason = self._reason(
            hypothesis=hypothesis,
            direction=direction,
            supporting_ids=new_supporting,
            contradicting_ids=new_contradicting,
            evidence_by_id=evidence_by_id,
        )
        change = ConfidenceChange(
            sequence=len(hypothesis.confidence_history) + 1,
            hypothesis_id=hypothesis.id,
            evidence_ids=evidence_ids,
            previous_confidence=previous_confidence,
            new_confidence=hypothesis.confidence,
            direction=direction,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
        )
        hypothesis.confidence_history.append(change)
        return change

    @staticmethod
    def _reason(
        hypothesis: Hypothesis,
        direction: ConfidenceDirection,
        supporting_ids: list[str],
        contradicting_ids: list[str],
        evidence_by_id: dict[str, Evidence],
    ) -> str:
        supporting_titles = [
            evidence_by_id[item].title for item in supporting_ids if item in evidence_by_id
        ]
        contradicting_titles = [
            evidence_by_id[item].title for item in contradicting_ids if item in evidence_by_id
        ]

        if direction == ConfidenceDirection.INCREASED:
            if supporting_titles:
                return (
                    "Confidence increased because new evidence supports this hypothesis: "
                    + "; ".join(supporting_titles)
                )
            return "Confidence increased because the accumulated evidence better supports this hypothesis."

        if direction == ConfidenceDirection.DECREASED:
            if contradicting_titles:
                return (
                    "Confidence decreased because current evidence contradicts this hypothesis: "
                    + "; ".join(contradicting_titles)
                )
            return "Confidence decreased because the accumulated evidence weakens this hypothesis."

        if supporting_titles or contradicting_titles:
            details = supporting_titles + contradicting_titles
            return "Confidence remained stable after evaluating: " + "; ".join(details)

        return f"No new evidence materially changed the assessment of {hypothesis.title}."
