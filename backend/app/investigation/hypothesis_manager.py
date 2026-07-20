from app.schemas.hypothesis import Hypothesis, HypothesisStatus
from app.schemas.lifecycle import HypothesisEvolution


class HypothesisManager:
    """Applies deterministic hypothesis lifecycle rules after each evidence round."""

    def evolve(
        self,
        hypotheses: list[Hypothesis],
        round_number: int,
        previous: dict[str, tuple[float, HypothesisStatus]],
    ) -> list[HypothesisEvolution]:
        changes: list[HypothesisEvolution] = []
        for hypothesis in hypotheses:
            previous_confidence, previous_status = previous[hypothesis.id]
            hypothesis.status = self._status_for(hypothesis)
            hypothesis.rejection_reason = self._rejection_reason(hypothesis)
            changes.append(
                HypothesisEvolution(
                    round_number=round_number,
                    hypothesis_id=hypothesis.id,
                    previous_status=previous_status.value,
                    current_status=hypothesis.status.value,
                    previous_confidence=previous_confidence,
                    current_confidence=hypothesis.confidence,
                    reason=self._reason(hypothesis, previous_confidence),
                )
            )
        return changes

    @staticmethod
    def _status_for(hypothesis: Hypothesis) -> HypothesisStatus:
        if hypothesis.confidence >= 0.8 and len(hypothesis.supporting_evidence_ids) >= 2:
            return HypothesisStatus.SUPPORTED
        if hypothesis.confidence <= 0.2 and hypothesis.contradicting_evidence_ids:
            return HypothesisStatus.REJECTED
        if not hypothesis.supporting_evidence_ids and not hypothesis.contradicting_evidence_ids:
            return HypothesisStatus.WAITING
        return HypothesisStatus.ACTIVE

    @staticmethod
    def _rejection_reason(hypothesis: Hypothesis) -> str | None:
        if hypothesis.status != HypothesisStatus.REJECTED:
            return None
        count = len(hypothesis.contradicting_evidence_ids)
        return f"Rejected after {count} contradicting evidence item(s) reduced confidence."

    @staticmethod
    def _reason(hypothesis: Hypothesis, previous_confidence: float) -> str:
        delta = hypothesis.confidence - previous_confidence
        if delta > 0:
            return f"Confidence increased by {delta:.2f} after supporting evidence was evaluated."
        if delta < 0:
            return f"Confidence decreased by {abs(delta):.2f} after contradictory evidence was evaluated."
        return "Confidence was unchanged because no new decisive evidence affected this hypothesis."
