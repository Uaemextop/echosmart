"""Caso de uso: Motor de alertas local."""
import logging
from typing import List

from ..domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)

CONDITION_GT = "gt"
CONDITION_LT = "lt"
CONDITION_EQ = "eq"


class AlertEngine:
    """Evalúa lecturas contra reglas configurables y genera alertas."""

    def __init__(self) -> None:
        self._rules: List[dict] = []
        logger.info("AlertEngine inicializado")

    def add_rule(self, rule: dict) -> None:
        """Agregar una regla de alerta."""
        self._rules.append(rule)

    def evaluate(self, reading: SensorReading) -> List[dict]:
        """Evaluar un reading contra todas las reglas registradas."""
        alerts = []
        for rule in self._rules:
            if self._matches(rule, reading.value):
                alerts.append({
                    "rule_name": rule["name"],
                    "sensor_id": reading.sensor_id,
                    "value": reading.value,
                    "severity": rule["severity"],
                })
        return alerts

    def _matches(self, rule: dict, value: float) -> bool:
        """Verificar si un valor viola una regla."""
        threshold = rule.get("threshold")
        condition = rule.get("condition")
        if condition == CONDITION_GT:
            return value > threshold
        if condition == CONDITION_LT:
            return value < threshold
        if condition == CONDITION_EQ:
            return value == threshold
        return False
