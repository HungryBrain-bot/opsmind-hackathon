from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.schemas.reasoning import EvidenceContradiction


class ContradictionDetector:
    """Deterministically identifies hypothesis-level evidence conflicts."""

    def detect(
        self, hypotheses: list[Hypothesis], evidence: list[Evidence]
    ) -> list[EvidenceContradiction]:
        results: list[EvidenceContradiction] = []
        for hypothesis in hypotheses:
            supporting = [item for item in evidence if hypothesis.id in item.supports]
            contradicting = [item for item in evidence if hypothesis.id in item.contradicts]
            if not supporting or not contradicting:
                continue
            severity = (
                "high"
                if any(item.reliability.value == "high" for item in contradicting)
                else "medium"
            )
            results.append(
                EvidenceContradiction(
                    id=f"C-{len(results) + 1:03d}",
                    hypothesis_id=hypothesis.id,
                    supporting_evidence_ids=[item.id for item in supporting],
                    contradicting_evidence_ids=[item.id for item in contradicting],
                    summary=(
                        f"Evidence both supports and contradicts {hypothesis.title}; "
                        "the conflict must be resolved before a defensible verdict."
                    ),
                    severity=severity,
                    resolved=False,
                )
            )
        return results
