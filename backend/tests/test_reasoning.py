import pytest

from app.core.settings import Settings
from app.investigation.fixtures import heavy_forwarder_evidence, heavy_forwarder_hypotheses
from app.investigation.reasoning import EvidenceReasoner


@pytest.mark.asyncio
async def test_fixture_reasoner_produces_grounded_findings_and_decision() -> None:
    reasoner = EvidenceReasoner(Settings(reasoning_provider="fixture"), ["tool-a"])
    result = await reasoner.evaluate(
        round_number=1,
        hypotheses=heavy_forwarder_hypotheses(),
        evidence=heavy_forwarder_evidence(),
        deterministic_sufficient=True,
    )

    assert result.decision.evidence_sufficient is True
    assert result.decision.continue_investigation is False
    assert result.findings
    evidence_ids = {item.id for item in heavy_forwarder_evidence()}
    assert all(set(item.evidence_ids) <= evidence_ids for item in result.findings)


@pytest.mark.asyncio
async def test_fixture_reasoner_records_gap_when_policy_is_not_satisfied() -> None:
    reasoner = EvidenceReasoner(Settings(reasoning_provider="fixture"), [])
    result = await reasoner.evaluate(
        round_number=1,
        hypotheses=heavy_forwarder_hypotheses(),
        evidence=heavy_forwarder_evidence()[:1],
        deterministic_sufficient=False,
    )

    assert result.decision.continue_investigation is True
    assert result.gaps[0].priority == "high"
