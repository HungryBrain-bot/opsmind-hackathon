from app.investigation.engine import InvestigationEngine


class OpenAIInvestigationEngine(InvestigationEngine):
    """Investigation engine configured to use the model-backed planner.

    The bounded evidence loop, read-only tools, persistence and safety rules remain
    deterministic. OpenAI is used only through the planner selected by Settings.
    """
