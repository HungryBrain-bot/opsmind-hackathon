from __future__ import annotations

from collections.abc import Awaitable, Callable
import os
import sys

from app.core.settings import Settings
from app.investigation.fixtures import heavy_forwarder_evidence
from app.schemas.evidence import Evidence

ToolHandler = Callable[[dict], Awaitable[list[Evidence]]]


class ToolRegistry:
    """Read-only tool boundary with local and real MCP stdio transports."""

    TOOL_NAMES = [
        "query_splunk_internal_logs",
        "get_certificate_status",
        "search_historical_incidents",
        "get_component_relationships",
        "get_heavy_forwarder_health",
    ]

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        evidence = {item.id: item for item in heavy_forwarder_evidence()}
        self._handlers: dict[str, ToolHandler] = {
            "query_splunk_internal_logs": self._static([evidence["E-001"]]),
            "get_certificate_status": self._static([evidence["E-002"]]),
            "search_historical_incidents": self._static([evidence["E-003"]]),
            "get_component_relationships": self._static([evidence["E-004"]]),
            "get_heavy_forwarder_health": self._static([evidence["E-005"], evidence["E-006"]]),
        }

    def names(self) -> list[str]:
        return sorted(self.TOOL_NAMES)

    async def execute(self, name: str, arguments: dict | None = None) -> list[Evidence]:
        if name not in self.TOOL_NAMES:
            raise ValueError(f"Unknown read-only tool: {name}")
        if self.settings.tool_transport.lower() == "mcp_stdio":
            return await self._execute_mcp(name, arguments or {})
        return await self._handlers[name](arguments or {})

    async def _execute_mcp(self, name: str, arguments: dict) -> list[Evidence]:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        command = self.settings.mcp_server_command
        if command == "python":
            command = sys.executable
        server = StdioServerParameters(
            command=command,
            args=["-m", self.settings.mcp_server_module],
            env={**os.environ, "PYTHONPATH": os.environ.get("PYTHONPATH", "backend")},
        )
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments=arguments)

        payload = result.structuredContent
        if payload is None:
            texts = [getattr(item, "text", "") for item in result.content]
            import json

            payload = json.loads(next(text for text in texts if text))
        if isinstance(payload, dict):
            payload = payload.get("result", payload.get("items", payload))
        if not isinstance(payload, list):
            raise ValueError(f"Unexpected MCP result for {name}: {type(payload).__name__}")
        return [Evidence.model_validate(item) for item in payload]

    @staticmethod
    def _static(items: list[Evidence]) -> ToolHandler:
        async def handler(_: dict) -> list[Evidence]:
            return [item.model_copy(deep=True) for item in items]

        return handler
