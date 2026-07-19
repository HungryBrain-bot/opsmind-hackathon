from app.core.settings import Settings
from app.investigation.engine import InvestigationEngine
from app.investigation.reporting import InvestigationReportBuilder
from app.investigation.store import InvestigationStore
from app.schemas.investigation import InvestigationRequest

async def _result():
    store=InvestigationStore()
    engine=InvestigationEngine(Settings(demo_stage_delay_seconds=0, sufficiency_threshold=0.8), store)
    created=await engine.create(InvestigationRequest(
        problem="Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?",
        environment="Production", priority="High"))
    await engine.run(created.investigation_id)
    return await store.get(created.investigation_id)

async def test_report_contains_verdict_and_evidence():
    result=await _result()
    report=InvestigationReportBuilder().build(result)
    assert report.verdict == result.verdict
    assert report.decision_trace.selected_hypothesis_id == "H-001"
    assert len(report.evidence) == len(result.evidence)

async def test_markdown_report_is_shareable():
    markdown=InvestigationReportBuilder().to_markdown(await _result())
    assert "# OpsMind Investigation Report" in markdown
    assert "## Decision trace" in markdown
    assert "## Evidence ledger" in markdown
    assert "E-001" in markdown
