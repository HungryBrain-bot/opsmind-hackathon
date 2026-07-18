"""Read-only OpsMind MCP server for the Heavy Forwarder golden path.

Run manually:
    python -m app.mcp.server
"""
from mcp.server.fastmcp import FastMCP

from app.investigation.fixtures import heavy_forwarder_evidence

mcp = FastMCP("OpsMind Splunk Evidence", json_response=True)


def _items(*ids: str) -> list[dict]:
    evidence = {item.id: item for item in heavy_forwarder_evidence()}
    return [evidence[item_id].model_dump(mode="json") for item_id in ids]


@mcp.tool()
def query_splunk_internal_logs(environment: str, problem: str) -> list[dict]:
    """Read current Splunk internal log observations relevant to the symptom."""
    return _items("E-001")


@mcp.tool()
def get_certificate_status(environment: str, problem: str) -> list[dict]:
    """Read Heavy Forwarder certificate metadata and expiry status."""
    return _items("E-002")


@mcp.tool()
def search_historical_incidents(environment: str, problem: str) -> list[dict]:
    """Search prior incidents with similar symptoms and error signatures."""
    return _items("E-003")


@mcp.tool()
def get_component_relationships(environment: str, problem: str) -> list[dict]:
    """Read configured Heavy Forwarder to indexer relationships."""
    return _items("E-004")


@mcp.tool()
def get_heavy_forwarder_health(environment: str, problem: str) -> list[dict]:
    """Read reachability, resources, service state, and queue observations."""
    return _items("E-005", "E-006")


if __name__ == "__main__":
    mcp.run(transport="stdio")
