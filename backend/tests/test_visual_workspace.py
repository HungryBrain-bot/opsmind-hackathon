from datetime import UTC, datetime

from app.investigation.workspace import InvestigationWorkspaceBuilder
from app.schemas.evidence import Evidence, EvidenceCategory, EvidenceReliability
from app.schemas.hypothesis import Hypothesis, HypothesisStatus
from app.schemas.investigation import InvestigationResult, InvestigationStatus, TimelineEvent
from app.schemas.lifecycle import InvestigationLifecyclePhase


def test_workspace_builder_creates_visual_models() -> None:
    result = InvestigationResult(
        investigation_id="INV-TEST",
        problem="Heavy Forwarder stopped forwarding logs",
        status=InvestigationStatus.COMPLETED,
        environment="Production",
        priority="High",
        current_phase="Complete",
        progress_percent=100,
        lifecycle_phase=InvestigationLifecyclePhase.COMPLETE,
        hypotheses=[
            Hypothesis(
                id="H-001",
                title="Certificate expired",
                rationale="TLS failure aligns with certificate status.",
                status=HypothesisStatus.SUPPORTED,
                confidence=0.94,
                supporting_evidence_ids=["E-001"],
            )
        ],
        evidence=[
            Evidence(
                id="E-001",
                title="Certificate status",
                content="Certificate expired before the outage.",
                category=EvidenceCategory.CONFIGURATION,
                source="certificate_tool",
                observed_at=datetime.now(UTC),
                reliability=EvidenceReliability.HIGH,
                supports=["H-001"],
                entities=["HF-PROD-02"],
            )
        ],
        confidence_history=[0.55, 0.94],
        timeline=[
            TimelineEvent(
                timestamp=datetime.now(UTC),
                phase="Evidence collection",
                title="Certificate evidence collected",
                detail="Certificate status confirms expiry.",
            )
        ],
        verdict="Certificate expiry caused the forwarding outage.",
    )

    workspace = InvestigationWorkspaceBuilder().build(result)

    assert workspace.leading_hypothesis_id == "H-001"
    assert workspace.overall_confidence == 0.94
    assert len(workspace.graph.nodes) == 4
    assert any(edge.edge_type.value == "supports" for edge in workspace.graph.edges)
    assert len(workspace.confidence_evolution) == 2
    assert workspace.playback_events[0]["type"] == "evidence"
