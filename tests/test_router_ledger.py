import sqlite3

import pytest

from foodloop.ledger import Ledger, LedgerError
from foodloop.router import propose_route


def test_router_rules():
    assert propose_route("fresh", 0.95, False).route == "people"
    assert propose_route("rotten", 0.95, False).route == "energy_or_compost"
    assert propose_route("fresh", 0.50, False).route == "hold"
    assert propose_route("fresh", 0.99, True).route == "hold"
    assert propose_route("???", 0.99, False).route == "hold"


@pytest.fixture
def led(tmp_path):
    return Ledger(str(tmp_path / "l.db"))


def _prop(led, b="b1"):
    led.propose(b, {"proposed_route": "people"})


def test_full_flow_issues_one_credit(led):
    _prop(led)
    led.review("b1", "Sam", "people", "people")
    led.confirm("b1", "donor", "Farm A")
    led.confirm("b1", "recipient", "Food Bank")
    s = led.state("b1")
    assert s["credit"] and s["donor"] == "Farm A"
    assert led.verify()[0]


def test_no_credit_without_review(led):
    _prop(led)
    with pytest.raises(LedgerError):
        led.confirm("b1", "donor", "Farm A")


def test_hold_cannot_be_confirmed(led):
    _prop(led)
    led.review("b1", "Sam", "hold", "people")
    with pytest.raises(LedgerError):
        led.confirm("b1", "donor", "Farm A")


def test_donor_and_recipient_must_differ_and_order(led):
    _prop(led)
    led.review("b1", "Sam", "people", "people")
    with pytest.raises(LedgerError):
        led.confirm("b1", "recipient", "X")
    led.confirm("b1", "donor", "X")
    with pytest.raises(LedgerError):
        led.confirm("b1", "recipient", "X")


def test_single_review(led):
    _prop(led)
    led.review("b1", "Sam", "people", "people")
    with pytest.raises(LedgerError):
        led.review("b1", "Sam", "hold", "people")


def test_tamper_detected(led, tmp_path):
    _prop(led)
    led.review("b1", "Sam", "people", "people")
    assert led.verify()[0]
    con = sqlite3.connect(str(tmp_path / "l.db"))
    con.execute("UPDATE ledger SET payload = REPLACE(payload,'people','animals') WHERE id = 1")
    con.commit()
    con.close()
    ok, _ = led.verify()
    assert not ok
