from __future__ import annotations

import logging

import mlflow

from app.config.settings import Settings

logger = logging.getLogger(__name__)


def configure_mlflow(settings: Settings) -> None:
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)
    logger.info("MLflow configured", extra={"tracking_uri": settings.mlflow_tracking_uri})
