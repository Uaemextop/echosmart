"""Tests para el CLI del EchoSmart Gateway."""

import json
import sys
import pytest

from gateway.src.cli import build_parser, cmd_version, cmd_status, cmd_test_sensors, main


# ── Helpers ───────────────────────────────────────────────────────────────


class _Namespace:
    """Namespace mínimo para tests unitarios de sub-comandos."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# ── Tests del parser ──────────────────────────────────────────────────────


def test_parser_requires_command():
    """El parser debe fallar si no se pasa ningún sub-comando."""
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_run_defaults():
    """'run' sin flags debe tener simulate=False."""
    parser = build_parser()
    args = parser.parse_args(["run"])
    assert args.command == "run"
    assert args.simulate is False


def test_parser_run_simulate_flag():
    """'run --simulate' debe activar el flag."""
    parser = build_parser()
    args = parser.parse_args(["run", "--simulate"])
    assert args.simulate is True


def test_parser_status():
    """'status' debe parsearse correctamente."""
    parser = build_parser()
    args = parser.parse_args(["status"])
    assert args.command == "status"


def test_parser_test_sensors():
    """'test-sensors' debe parsearse correctamente."""
    parser = build_parser()
    args = parser.parse_args(["test-sensors"])
    assert args.command == "test-sensors"


def test_parser_test_sensors_simulate():
    """'test-sensors --simulate' debe activar el flag."""
    parser = build_parser()
    args = parser.parse_args(["test-sensors", "--simulate"])
    assert args.simulate is True


def test_parser_version():
    """'version' debe parsearse correctamente."""
    parser = build_parser()
    args = parser.parse_args(["version"])
    assert args.command == "version"


# ── Tests de sub-comandos ─────────────────────────────────────────────────


def test_cmd_version_prints_version(capsys):
    """'version' debe imprimir la versión y devolver 0."""
    args = _Namespace(log_level="ERROR")
    ret = cmd_version(args)
    captured = capsys.readouterr()
    assert ret == 0
    assert "echosmart-gateway" in captured.out
    # Debe contener un número de versión X.Y.Z
    import re
    assert re.search(r"\d+\.\d+\.\d+", captured.out)


def test_cmd_status_returns_json(capsys):
    """'status' debe imprimir JSON válido con las claves esperadas."""
    args = _Namespace(log_level="ERROR")
    ret = cmd_status(args)
    captured = capsys.readouterr()
    assert ret == 0
    data = json.loads(captured.out)
    assert "version" in data
    assert "gateway_id" in data
    assert "simulation_mode" in data


def test_cmd_test_sensors_no_sensors(capsys):
    """'test-sensors --simulate' sin sensores configurados debe devolver 0."""
    args = _Namespace(log_level="ERROR", simulate=True)
    ret = cmd_test_sensors(args)
    captured = capsys.readouterr()
    assert ret == 0
    assert "No hay sensores" in captured.out or "sensores" in captured.out.lower()


def test_main_version(capsys):
    """main(['version']) debe devolver 0 e imprimir la versión."""
    ret = main(["version"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "echosmart-gateway" in captured.out


def test_main_status_returns_zero(capsys):
    """main(['status']) debe devolver 0."""
    ret = main(["status"])
    assert ret == 0


def test_main_test_sensors_simulate(capsys):
    """main(['test-sensors', '--simulate']) debe devolver 0."""
    ret = main(["test-sensors", "--simulate"])
    assert ret == 0
