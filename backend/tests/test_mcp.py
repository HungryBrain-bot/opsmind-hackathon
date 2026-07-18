from app.core.settings import Settings
from app.investigation.tools import ToolRegistry


async def test_local_read_only_tool_contract() -> None:
    registry = ToolRegistry(Settings(tool_transport="local"))
    evidence = await registry.execute(
        "get_certificate_status",
        {"environment": "Production", "problem": "HF is not forwarding"},
    )
    assert evidence[0].id == "E-002"
    assert evidence[0].source == "get_certificate_status"
