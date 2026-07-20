from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis, HypothesisStatus


class HypothesisEvaluator:
    """Deterministically updates hypotheses from evidence relationships."""

    def evaluate(self, hypotheses: list[Hypothesis], evidence: list[Evidence]) -> None:
        evidence_by_id = {item.id: item for item in evidence}
        for hypothesis in hypotheses:
            supporting = [item.id for item in evidence if hypothesis.id in item.supports]
            contradicting = [item.id for item in evidence if hypothesis.id in item.contradicts]
            hypothesis.supporting_evidence_ids = supporting
            hypothesis.contradicting_evidence_ids = contradicting

            support_score = sum(self._weight(evidence_by_id[item]) for item in supporting)
            contradiction_score = sum(self._weight(evidence_by_id[item]) for item in contradicting)
            confidence = (
                hypothesis.confidence + (support_score * 0.20) - (contradiction_score * 0.28)
            )
            hypothesis.confidence = max(0.02, min(0.98, confidence))
            hypothesis.rejection_reason = None

            if contradiction_score >= 0.8 and support_score == 0:
                hypothesis.status = HypothesisStatus.REJECTED
                titles = [evidence_by_id[item].title for item in contradicting]
                hypothesis.rejection_reason = (
                    "Rejected because reliable evidence contradicts the hypothesis"
                    + (f": {'; '.join(titles)}." if titles else ".")
                )
            elif hypothesis.confidence >= 0.8 and len(supporting) >= 2:
                hypothesis.status = HypothesisStatus.SUPPORTED
            else:
                hypothesis.status = HypothesisStatus.ACTIVE

    @staticmethod
    def _weight(evidence: Evidence) -> float:
        reliability = {"high": 1.0, "medium": 0.65, "low": 0.35}[evidence.reliability.value]
        return reliability * (1.0 if evidence.current else 0.75)
