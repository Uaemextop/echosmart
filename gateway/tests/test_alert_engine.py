"""Tests del AlertEngine."""

from gateway.src.alert_engine import AlertEngine


def test_alert_engine_evaluate():
    """Verificar evaluación de reglas de alerta."""
    engine = AlertEngine()
    engine.add_rule({
        "name": "Temp Alta",
        "condition": "gt",
        "threshold": 30.0,
        "severity": "high",
    })

    reading = {"sensor_id": "s1", "value": 35.0}
    alerts = engine.evaluate(reading)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "high"


def test_alert_engine_no_alert():
    """Verificar que no se genera alerta cuando el valor está dentro del rango."""
    engine = AlertEngine()
    engine.add_rule({
        "name": "Temp Alta",
        "condition": "gt",
        "threshold": 30.0,
        "severity": "high",
    })

    reading = {"sensor_id": "s1", "value": 25.0}
    alerts = engine.evaluate(reading)
    assert len(alerts) == 0
