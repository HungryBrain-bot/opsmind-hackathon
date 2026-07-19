from fastapi import APIRouter

from app.core.settings import get_settings

router = APIRouter(tags=["runtime"])


@router.get("/runtime")
def runtime() -> dict[str, object]:
    settings = get_settings()
    provider = settings.planner_provider.lower()
    return {
        "mode": "openai" if provider == "openai" else "offline",
        "planner_provider": provider,
        "tool_transport": settings.tool_transport,
        "model": settings.openai_model if provider == "openai" else None,
        "api_key_configured": bool(settings.openai_api_key),
        "version": "1.3.0",
    }
