"""Tests del AlertEngine."""
from gateway.src.application.alert_engine import AlertEngine
from gateway.src.domain.entities.sensor import SensorReading


def _make_reading(value: float, sensor_id: str = "s1") -> SensorReading:
    return SensorReading(sensor_id=sensor_id, sensor_type="temperature", value=value, unit="°C")


def test_alert_engine_evaluate():
    """Verificar que se genera alerta cuando el valor supera el umbral."""
    engine = AlertEngine()
    engine.add_rule({"name": "Temp Alta", "condition": "gt", "threshold": 30.0, "severity": "high"})
    alerts = engine.evaluate(_make_reading(35.0))
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "high"


def test_alert_engine_no_alert():
    """Verificar que no se genera alerta dentro del rango."""
    engine = AlertEngine()
    engine.add_rule({"name": "Temp Alta", "condition": "gt", "threshold": 30.0, "severity": "high"})
    alerts = engine.evaluate(_make_reading(25.0))
    assert len(alerts) == 0


def test_alert_condition_lt():
    """Verificar condición 'lt' (menor que)."""
    engine = AlertEngine()
    engine.add_rule({"name": "Temp Baja", "condition": "lt", "threshold": 10.0, "severity": "medium"})
    assert len(engine.evaluate(_make_reading(5.0))) == 1
    assert len(engine.evaluate(_make_reading(15.0))) == 0


def test_multiple_rules():
    """Verificar evaluación de múltiples reglas."""
    engine = AlertEngine()
    engine.add_rule({"name": "Temp Alta", "condition": "gt", "threshold": 30.0, "severity": "high"})
    engine.add_rule({"name": "Temp Muy Alta", "condition": "gt", "threshold": 40.0, "severity": "critical"})
    alerts = engine.evaluate(_make_reading(35.0))
    assert len(alerts) == 1
    alerts = engine.evaluate(_make_reading(45.0))
    assert len(alerts) == 2
