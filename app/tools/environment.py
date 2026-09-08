from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import Settings


@dataclass
class SimulatedEnvironment:
    database_healthy: bool
    service_healthy: bool
    logs_normal: bool
    restart_succeeds: bool
    validation_healthy: bool

    @classmethod
    def from_settings(cls, settings: Settings) -> SimulatedEnvironment:
        return cls(
            database_healthy=settings.sim_database_healthy,
            service_healthy=settings.sim_service_healthy,
            logs_normal=settings.sim_logs_normal,
            restart_succeeds=settings.sim_restart_succeeds,
            validation_healthy=settings.sim_validation_healthy,
        )
