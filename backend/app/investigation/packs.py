from app.schemas.pack import InvestigationPack


SPLUNK_HEAVY_FORWARDER_PACK = InvestigationPack(
    id="splunk-heavy-forwarder",
    name="Splunk Heavy Forwarder Investigation",
    version="1.0.0",
    domain="splunk",
    description=(
        "Investigates forwarding failures using operational logs, certificate status, "
        "historical incidents, component relationships and Heavy Forwarder health."
    ),
    supported_problem_types=[
        "not_forwarding",
        "ingestion_gap",
        "tls_failure",
        "queue_growth",
    ],
    allowed_tools=[
        "query_splunk_internal_logs",
        "get_certificate_status",
        "search_historical_incidents",
        "get_component_relationships",
        "get_heavy_forwarder_health",
    ],
    stop_confidence=0.8,
    minimum_categories=2,
    maximum_rounds=3,
)


_PACKS = {SPLUNK_HEAVY_FORWARDER_PACK.id: SPLUNK_HEAVY_FORWARDER_PACK}


def list_packs() -> list[InvestigationPack]:
    return list(_PACKS.values())


def get_pack(pack_id: str) -> InvestigationPack:
    try:
        return _PACKS[pack_id]
    except KeyError as exc:
        raise ValueError(f"Unknown investigation pack: {pack_id}") from exc
