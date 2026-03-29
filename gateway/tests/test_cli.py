"""Tests for the gateway CLI entry point."""

from gateway.src.cli import build_parser, cmd_status, cmd_test_sensors, __version__


def test_cli_version():
    """Verify the version string is set."""
    assert __version__ == "1.0.0"


def test_cli_parser_run():
    """Verify 'run' sub-command is parsed."""
    parser = build_parser()
    args = parser.parse_args(["run"])
    assert args.command == "run"
    assert args.simulate is False


def test_cli_parser_run_simulate():
    """Verify 'run --simulate' flag is parsed."""
    parser = build_parser()
    args = parser.parse_args(["run", "--simulate"])
    assert args.command == "run"
    assert args.simulate is True


def test_cli_parser_status():
    """Verify 'status' sub-command is parsed."""
    parser = build_parser()
    args = parser.parse_args(["status"])
    assert args.command == "status"


def test_cli_parser_test_sensors():
    """Verify 'test-sensors' sub-command is parsed."""
    parser = build_parser()
    args = parser.parse_args(["test-sensors"])
    assert args.command == "test-sensors"


def test_cli_parser_no_command():
    """Verify no sub-command defaults to None."""
    parser = build_parser()
    args = parser.parse_args([])
    assert args.command is None


def test_cmd_status(capsys):
    """Verify status command outputs configuration."""
    import argparse
    cmd_status(argparse.Namespace())
    captured = capsys.readouterr()
    assert "EchoSmart Gateway" in captured.out
    assert "Gateway ID" in captured.out


def test_cmd_test_sensors(capsys):
    """Verify test-sensors command reads all sensors."""
    import argparse
    cmd_test_sensors(argparse.Namespace())
    captured = capsys.readouterr()
    assert "All sensors OK" in captured.out
    assert "DS18B20" in captured.out
    assert "DHT22" in captured.out
    assert "BH1750" in captured.out
    assert "SoilMoisture" in captured.out
    assert "MHZ-19C" in captured.out
