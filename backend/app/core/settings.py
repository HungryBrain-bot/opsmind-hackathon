from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OpsMind"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    max_investigation_rounds: int = 3
    sufficiency_threshold: float = 0.80
    demo_stage_delay_seconds: float = 0.8
    investigation_storage_path: str = "data/investigations"

    planner_provider: str = "fixture"  # fixture | openai
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6"
    planner_prompt_version: str = "planner-v1"
    planner_fallback_to_fixture: bool = True
    planner_max_validation_attempts: int = 2

    reasoning_provider: str = "fixture"  # fixture | openai
    reasoning_prompt_version: str = "reasoning-v1"
    reasoning_fallback_to_fixture: bool = True

    tool_transport: str = "local"  # local | mcp_stdio
    mcp_server_command: str = "python"
    mcp_server_module: str = "app.mcp.server"

    # Optional pricing inputs. Keep zero until current account pricing is configured.
    model_input_cost_per_million: float = 0.0
    model_output_cost_per_million: float = 0.0

    model_config = SettingsConfigDict(
        env_prefix="OPSMIND_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
