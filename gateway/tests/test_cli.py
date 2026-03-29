"""Tests de la CLI del EchoSmart Gateway."""
import json
import argparse
import pytest


def test_version_output(capsys):
    """La CLI debe mostrar la versión correcta."""
    from gateway.src.cli import cmd_version
    result = cmd_version(None)
    captured = capsys.readouterr()
    assert result == 0
    assert "echosmart-gateway" in captured.out
    assert "1.0.0" in captured.out


def test_status_output(capsys):
    """La CLI debe mostrar el estado en JSON."""
    from gateway.src.cli import cmd_status
    result = cmd_status(None)
    captured = capsys.readouterr()
    assert result == 0
    data = json.loads(captured.out)
    assert "gateway_id" in data
    assert "version" in data


def test_test_sensors_output(capsys):
    """test-sensors debe listar todos los sensores."""
    from gateway.src.cli import cmd_test_sensors
    result = cmd_test_sensors(None)
    captured = capsys.readouterr()
    assert result == 0
    assert "ds18b20" in captured.out
    assert "dht22" in captured.out
    assert "bh1750" in captured.out
    assert "mhz19c" in captured.out
    assert "soil" in captured.out


def test_build_parser():
    """El parser debe aceptar los subcomandos esperados."""
    from gateway.src.cli import build_parser
    parser = build_parser()
    args = parser.parse_args(["version"])
    assert args.command == "version"

    args = parser.parse_args(["run", "--simulate"])
    assert args.command == "run"
    assert args.simulate is True


def test_run_simulate(capsys):
    """El subcomando run --simulate debe arrancar sin errores."""
    from gateway.src.cli import cmd_run
    args = argparse.Namespace(simulate=True)
    result = cmd_run(args)
    assert result == 0
