"""Motor de alertas local."""

import logging

logger = logging.getLogger(__name__)


class AlertEngine:
    """Evalúa reglas de alerta localmente en el gateway."""

    def __init__(self):
        self.rules = []
        logger.info("AlertEngine inicializado.")

    def add_rule(self, rule: dict):
        """Agregar una regla de alerta."""
        self.rules.append(rule)

    def evaluate(self, reading: dict) -> list:
        """Evaluar un reading contra todas las reglas."""
        alerts = []
        for rule in self.rules:
            if self._check_rule(rule, reading):
                alerts.append({
                    "rule_name": rule["name"],
                    "sensor_id": reading["sensor_id"],
                    "value": reading["value"],
                    "severity": rule["severity"],
                })
        return alerts

    def _check_rule(self, rule: dict, reading: dict) -> bool:
        """Verificar si un reading viola una regla."""
        value = reading["value"]
        condition = rule.get("condition")
        threshold = rule.get("threshold")

        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "eq":
            return value == threshold
        return False
