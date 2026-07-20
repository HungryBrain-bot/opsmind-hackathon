from app.investigation.contradictions import ContradictionDetector
from app.investigation.fixtures import heavy_forwarder_evidence, heavy_forwarder_hypotheses
from app.schemas.evidence import Evidence


def test_detector_records_support_and_contradiction_for_same_hypothesis() -> None:
    evidence = heavy_forwarder_evidence()
    source = evidence[0]
    evidence.append(
        Evidence(
            id="E-999",
            title="Certificate remains valid",
            content="Independent certificate inspection reports a valid certificate.",
            category=source.category,
            source="independent_check",
            observed_at=source.observed_at,
            reliability=source.reliability,
            contradicts=["H-001"],
        )
    )

    contradictions = ContradictionDetector().detect(heavy_forwarder_hypotheses(), evidence)

    assert contradictions[0].hypothesis_id == "H-001"
    assert contradictions[0].severity == "high"
    assert "E-999" in contradictions[0].contradicting_evidence_ids
