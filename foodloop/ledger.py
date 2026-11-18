"""Append-only, hash-chained ledger.

Credit is issued only after: human review, donor confirmation and recipient
confirmation, in that order, with a final route other than "hold".
Editing or deleting an old row breaks the chain, which verify() detects.
This is a demo ledger: it detects tampering, it does not prevent a database
owner from rewriting the whole chain.
"""
import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone

GENESIS = "0" * 64
EVENTS = ("scan_proposed", "review_confirmed", "review_overridden",
          "donor_confirmed", "recipient_confirmed", "credit_issued")


class LedgerError(Exception):
    pass


def _digest(prev_hash: str, ts: str, batch_id: str, event: str, payload: str) -> str:
    raw = "|".join([prev_hash, ts, batch_id, event, payload])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        with self._conn() as c:
            c.execute(
                """CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    batch_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    hash TEXT NOT NULL)"""
            )

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _append(self, conn, batch_id: str, event: str, payload: dict) -> dict:
        if event not in EVENTS:
            raise LedgerError(f"unknown event {event}")
        last = conn.execute("SELECT hash FROM ledger ORDER BY id DESC LIMIT 1").fetchone()
        prev = last["hash"] if last else GENESIS
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        body = json.dumps(payload, sort_keys=True)
        h = _digest(prev, ts, batch_id, event, body)
        conn.execute(
            "INSERT INTO ledger (ts, batch_id, event, payload, prev_hash, hash) VALUES (?,?,?,?,?,?)",
            (ts, batch_id, event, body, prev, h),
        )
        return {"ts": ts, "batch_id": batch_id, "event": event, "payload": payload, "hash": h}

    def events(self, batch_id: str) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM ledger WHERE batch_id=? ORDER BY id", (batch_id,)).fetchall()
        return [dict(r) | {"payload": json.loads(r["payload"])} for r in rows]

    def all_entries(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM ledger ORDER BY id").fetchall()
        return [dict(r) | {"payload": json.loads(r["payload"])} for r in rows]

    def state(self, batch_id: str) -> dict:
        """Current state of a batch, derived only from its ledger events."""
        s = {"proposed": False, "reviewed": False, "final_route": None, "reviewer": None,
             "donor": None, "recipient": None, "credit": False}
        for e in self.events(batch_id):
            p = e["payload"]
            if e["event"] == "scan_proposed":
                s["proposed"] = True
            elif e["event"] in ("review_confirmed", "review_overridden"):
                s.update(reviewed=True, final_route=p["final_route"], reviewer=p["reviewer"],
                         overridden=e["event"] == "review_overridden")
            elif e["event"] == "donor_confirmed":
                s["donor"] = p["name"]
            elif e["event"] == "recipient_confirmed":
                s["recipient"] = p["name"]
            elif e["event"] == "credit_issued":
                s["credit"] = True
        return s

    # --- the only ways to add rows -------------------------------------
    def propose(self, batch_id: str, payload: dict) -> dict:
        with self._lock, self._conn() as c:
            return self._append(c, batch_id, "scan_proposed", payload)

    def review(self, batch_id: str, reviewer: str, final_route: str, proposed_route: str) -> dict:
        reviewer = (reviewer or "").strip()
        if not reviewer:
            raise LedgerError("A named reviewer is required.")
        with self._lock, self._conn() as c:
            st = self.state(batch_id)
            if not st["proposed"]:
                raise LedgerError("Unknown batch.")
            if st["reviewed"]:
                raise LedgerError("Batch already reviewed.")
            event = "review_confirmed" if final_route == proposed_route else "review_overridden"
            return self._append(c, batch_id, event,
                                {"reviewer": reviewer, "final_route": final_route,
                                 "proposed_route": proposed_route})

    def confirm(self, batch_id: str, role: str, name: str) -> dict:
        if role not in ("donor", "recipient"):
            raise LedgerError("role must be donor or recipient")
        name = (name or "").strip()
        if not name:
            raise LedgerError("A name is required.")
        with self._lock, self._conn() as c:
            st = self.state(batch_id)
            if not st["reviewed"]:
                raise LedgerError("A person must review the batch first.")
            if st["final_route"] == "hold":
                raise LedgerError("A held batch cannot be handed over.")
            if st[role]:
                raise LedgerError(f"The {role} already confirmed.")
            if role == "recipient" and not st["donor"]:
                raise LedgerError("The donor must confirm the handover first.")
            if role == "recipient" and name.lower() == (st["donor"] or "").lower():
                raise LedgerError("Donor and recipient must be different parties.")
            entry = self._append(c, batch_id, f"{role}_confirmed", {"name": name})
            if role == "recipient":
                self._append(c, batch_id, "credit_issued",
                             {"units": 1, "to": st["donor"], "route": st["final_route"],
                              "note": "demo credit, no monetary value"})
            return entry

    def verify(self) -> tuple[bool, str]:
        prev = GENESIS
        for e in self.all_entries():
            body = json.dumps(e["payload"], sort_keys=True)
            if e["prev_hash"] != prev:
                return False, f"Chain broken at row {e['id']} (previous hash does not match)."
            if _digest(prev, e["ts"], e["batch_id"], e["event"], body) != e["hash"]:
                return False, f"Row {e['id']} was changed after it was written."
            prev = e["hash"]
        return True, "Chain intact."
