from solution import parse_duration
import pytest


def test_seconds_only():
    assert parse_duration("90s") == 90


def test_minutes_only():
    assert parse_duration("5m") == 300


def test_hours_only():
    assert parse_duration("2h") == 7200


def test_combined_hours_minutes():
    assert parse_duration("1h30m") == 5400


def test_combined_all_units():
    assert parse_duration("2h15m10s") == 8110


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        parse_duration("")


def test_garbage_input_raises():
    with pytest.raises(ValueError):
        parse_duration("notaduration")
