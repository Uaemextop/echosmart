"""Tests for the EchoSmart Gateway CLI."""

import json

from gateway.src.cli import build_parser, cmd_status, cmd_test_sensors, cmd_version, main


# ── version ──────────────────────────────────────────────────────────────

def test_version_returns_zero():
    assert cmd_version(build_parser().parse_args(["version"])) == 0


def test_main_version(capsys):
    rc = main(["version"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "echosmart-gateway" in out


# ── status ───────────────────────────────────────────────────────────────

def test_status_returns_json(capsys):
    rc = main(["status"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "gateway_id" in data
    assert "version" in data


# ── test-sensors ─────────────────────────────────────────────────────────

def test_test_sensors_returns_zero(capsys):
    rc = main(["test-sensors"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "5 passed" in out


# ── run (simulate) ───────────────────────────────────────────────────────

def test_run_simulate_returns_zero():
    rc = main(["run", "--simulate"])
    assert rc == 0


# ── no command ───────────────────────────────────────────────────────────

def test_no_command_returns_one():
    rc = main([])
    assert rc == 1


# ── parser ───────────────────────────────────────────────────────────────

def test_parser_run_simulate():
    parser = build_parser()
    args = parser.parse_args(["run", "--simulate"])
    assert args.simulate is True


def test_parser_run_no_simulate():
    parser = build_parser()
    args = parser.parse_args(["run"])
    assert args.simulate is False


def test_parser_status():
    parser = build_parser()
    args = parser.parse_args(["status"])
    assert args.command == "status"


def test_parser_test_sensors():
    parser = build_parser()
    args = parser.parse_args(["test-sensors"])
    assert args.command == "test-sensors"
