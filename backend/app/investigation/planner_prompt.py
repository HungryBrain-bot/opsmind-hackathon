from __future__ import annotations

from dataclasses import dataclass

from app.schemas.investigation import InvestigationRequest


@dataclass(frozen=True, slots=True)
class PlannerPrompt:
    version: str
    system: str
    user: str


_SYSTEM_PROMPTS = {
    "planner-v1": """You are the planning layer of OpsMind, an enterprise investigation engine.
Create a bounded, evidence-first investigation plan. Do not produce a verdict. Do not recommend
write actions. Use only the available read-only tool names. Hypotheses must be mutually useful,
prioritized through their confidence values, and falsifiable. Every evidence requirement must say
which hypothesis it helps test. Return only data conforming to the supplied schema.""",
}


def build_planner_prompt(
    *,
    version: str,
    request: InvestigationRequest,
    available_tools: list[str],
) -> PlannerPrompt:
    """Build a versioned planner prompt from validated runtime inputs."""

    try:
        system_prompt = _SYSTEM_PROMPTS[version]
    except KeyError as exc:
        supported = ", ".join(sorted(_SYSTEM_PROMPTS))
        raise ValueError(
            f"Unsupported planner prompt version {version!r}. Supported versions: {supported}."
        ) from exc

    tools = ", ".join(sorted(available_tools))
    user_prompt = (
        f"Prompt version: {version}\n"
        f"Problem: {request.problem}\n"
        f"Environment: {request.environment}\n"
        f"Priority: {request.priority}\n"
        f"Scenario: {request.scenario_id}\n"
        f"Available read-only tools: {tools}\n"
        "Use sequential IDs H-001 onward for hypotheses and R-001 onward for evidence "
        "requirements. Keep the plan within the supplied maximum-rounds schema constraint."
    )
    return PlannerPrompt(version=version, system=system_prompt, user=user_prompt)
