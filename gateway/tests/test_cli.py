"""Tests for the echosmart-gateway CLI."""

import json

from gateway.src.cli import build_parser, main, VERSION


def test_build_parser():
    """Parser should have the expected subcommands."""
    parser = build_parser()
    # Parser should be created without error
    assert parser.prog == "echosmart-gateway"


def test_version_command(capsys):
    """'version' subcommand prints version string."""
    rc = main(["version"])
    assert rc == 0
    captured = capsys.readouterr()
    assert VERSION in captured.out


def test_status_command(capsys):
    """'status' subcommand prints JSON configuration."""
    rc = main(["status"])
    assert rc == 0
    captured = capsys.readouterr()
    info = json.loads(captured.out)
    assert "version" in info
    assert "gateway_id" in info
    assert info["version"] == VERSION


def test_no_command_shows_help(capsys):
    """Running without a subcommand returns exit code 1."""
    rc = main([])
    assert rc == 1


def test_test_sensors_command(capsys):
    """'test-sensors' subcommand runs sensor diagnostics."""
    rc = main(["test-sensors"])
    assert rc == 0
    captured = capsys.readouterr()
    # Output should be valid JSON (list of readings)
    readings = json.loads(captured.out)
    assert isinstance(readings, list)
    assert len(readings) == 5


def test_run_simulate_command():
    """'run --simulate' subcommand completes without error."""
    rc = main(["run", "--simulate"])
    assert rc == 0


def test_version_value():
    """VERSION should be a valid semver-like string."""
    parts = VERSION.split(".")
    assert len(parts) == 3
    for part in parts:
        assert part.isdigit()


def test_status_contains_expected_keys(capsys):
    """'status' output must contain all expected keys."""
    main(["status"])
    captured = capsys.readouterr()
    info = json.loads(captured.out)
    expected_keys = [
        "version",
        "gateway_id",
        "gateway_name",
        "cloud_api_url",
        "mqtt_broker",
        "polling_interval",
        "sync_interval",
        "simulation_mode",
        "log_level",
    ]
    for key in expected_keys:
        assert key in info, f"Missing key: {key}"


def test_parser_run_has_simulate_flag():
    """'run' subcommand should accept --simulate flag."""
    parser = build_parser()
    args = parser.parse_args(["run", "--simulate"])
    assert args.simulate is True
    assert args.command == "run"
