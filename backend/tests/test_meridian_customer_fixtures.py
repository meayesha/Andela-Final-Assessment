"""Tests for Meridian assessment customer PIN fixture (no network)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "meridian_test_customers.json"


@pytest.fixture(scope="module")
def meridian_test_customers() -> list[dict[str, str]]:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, list)
    return raw


def test_fixture_file_exists() -> None:
    assert FIXTURE_PATH.is_file(), f"missing fixture: {FIXTURE_PATH}"


def test_customer_rows_have_email_and_four_digit_pin(meridian_test_customers: list[dict[str, str]]) -> None:
    assert len(meridian_test_customers) >= 1
    for row in meridian_test_customers:
        assert set(row.keys()) == {"email", "pin"}, row
        email = row["email"].strip().lower()
        pin = row["pin"].strip()
        assert "@" in email
        assert re.match(r"^[^@]+@[^@]+\.[^@]+$", email), f"unexpected email shape: {email!r}"
        assert pin.isdigit() and len(pin) == 4, f"PIN must be 4 digits: {pin!r}"


def test_fixture_emails_are_unique(meridian_test_customers: list[dict[str, str]]) -> None:
    emails = [r["email"].strip().lower() for r in meridian_test_customers]
    assert len(emails) == len(set(emails)), "duplicate emails in fixture"
