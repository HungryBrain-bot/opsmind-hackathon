from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.schemas.reasoning import InvestigationFinding


class EvidenceSummaryService:
    def build(
        self, hypotheses: list[Hypothesis], evidence: list[Evidence]
    ) -> list[InvestigationFinding]:
        findings: list[InvestigationFinding] = []
        for hypothesis in hypotheses:
            supporting = [item for item in evidence if hypothesis.id in item.supports]
            if not supporting:
                continue
            findings.append(
                InvestigationFinding(
                    id=f"F-{len(findings) + 1:03d}",
                    statement=(
                        f"{hypothesis.title} is supported by {len(supporting)} evidence item(s): "
                        + "; ".join(item.title for item in supporting)
                    ),
                    evidence_ids=[item.id for item in supporting],
                    hypothesis_ids=[hypothesis.id],
                )
            )
        return findings
