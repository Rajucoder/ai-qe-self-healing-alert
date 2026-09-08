from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    log_level: str
    mlflow_tracking_uri: str
    mlflow_experiment_name: str
    llm_provider: str
    groq_api_key: str | None
    groq_model: str
    sim_database_healthy: bool
    sim_service_healthy: bool
    sim_logs_normal: bool
    sim_restart_succeeds: bool
    sim_validation_healthy: bool

    @classmethod
    def from_environment(cls) -> Settings:
        return cls(
            app_name=os.getenv("APP_NAME", "ai-qe-self-healing-agent"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            mlflow_tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
            mlflow_experiment_name=os.getenv("MLFLOW_EXPERIMENT_NAME", "self-healing-agent"),
            llm_provider=os.getenv("LLM_PROVIDER", "deterministic").lower(),
            groq_api_key=os.getenv("GROQ_API_KEY") or None,
            groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            sim_database_healthy=_read_bool("SIM_DATABASE_HEALTHY", True),
            sim_service_healthy=_read_bool("SIM_SERVICE_HEALTHY", True),
            sim_logs_normal=_read_bool("SIM_LOGS_NORMAL", True),
            sim_restart_succeeds=_read_bool("SIM_RESTART_SUCCEEDS", True),
            sim_validation_healthy=_read_bool("SIM_VALIDATION_HEALTHY", True),
        )


settings = Settings.from_environment()
