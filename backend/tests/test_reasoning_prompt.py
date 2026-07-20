from app.investigation.fixtures import heavy_forwarder_evidence, heavy_forwarder_hypotheses
from app.investigation.reasoning_prompt import build_reasoning_prompt


def test_reasoning_prompt_encodes_investigation_sop() -> None:
    prompt = build_reasoning_prompt(
        version="reasoning-v1",
        round_number=1,
        hypotheses=heavy_forwarder_hypotheses(),
        evidence=heavy_forwarder_evidence(),
        available_tools=["query_splunk_internal_logs"],
    )

    assert "Evidence first" in prompt.system
    assert "Never invent evidence" in prompt.system
    assert "disconfirming evidence" in prompt.system
    assert '"round_number": 1' in prompt.user
