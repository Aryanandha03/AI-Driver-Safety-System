"""SQLite storage API. This module has no Streamlit dependency."""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

SCHEMA = Path(__file__).with_name("schema.sql")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: str | Path = "member5.db"):
        self.path = str(path)
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        try:
            with self.connection() as conn:
                conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        except (OSError, sqlite3.Error) as exc:
            raise RuntimeError(f"Could not initialize database {self.path}: {exc}") from exc

    def upsert_driver(self, driver_id: str, name: str, metadata: dict | None = None) -> None:
        if not driver_id or not name:
            raise ValueError("driver_id and name are required")
        with self.connection() as c:
            c.execute("""INSERT INTO drivers VALUES (?, ?, ?, ?) ON CONFLICT(driver_id)
                         DO UPDATE SET name=excluded.name, metadata_json=excluded.metadata_json""",
                      (driver_id, name, json.dumps(metadata or {}), now_iso()))

    def upsert_vehicle(self, vehicle_id: str, description: str | None = None,
                       metadata: dict | None = None) -> None:
        if not vehicle_id:
            raise ValueError("vehicle_id is required")
        with self.connection() as c:
            c.execute("""INSERT INTO vehicles VALUES (?, ?, ?, ?) ON CONFLICT(vehicle_id)
                         DO UPDATE SET description=excluded.description, metadata_json=excluded.metadata_json""",
                      (vehicle_id, description, json.dumps(metadata or {}), now_iso()))

    def create_session(self, driver_id: str | None = None, vehicle_id: str | None = None,
                       session_id: str | None = None) -> str:
        sid = session_id or f"S-{uuid.uuid4().hex[:8].upper()}"
        with self.connection() as c:
            c.execute("INSERT INTO sessions(session_id,driver_id,vehicle_id,started_at,status) VALUES(?,?,?,?,?)",
                      (sid, driver_id, vehicle_id, now_iso(), "ACTIVE"))
        return sid

    def end_session(self, session_id: str) -> None:
        with self.connection() as c:
            c.execute("UPDATE sessions SET ended_at=?, status='ENDED' WHERE session_id=? AND status='ACTIVE'",
                      (now_iso(), session_id))

    def get_active_session(self) -> dict | None:
        with self.connection() as c:
            row = c.execute("SELECT * FROM sessions WHERE status='ACTIVE' ORDER BY started_at DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def get_driver(self, driver_id: str | None) -> dict | None:
        if not driver_id: return None
        with self.connection() as c:
            r = c.execute("SELECT * FROM drivers WHERE driver_id=?", (driver_id,)).fetchone()
        return dict(r) if r else None

    def get_vehicle(self, vehicle_id: str | None) -> dict | None:
        if not vehicle_id: return None
        with self.connection() as c:
            r = c.execute("SELECT * FROM vehicles WHERE vehicle_id=?", (vehicle_id,)).fetchone()
        return dict(r) if r else None

    def save_gps_location(self, latitude: float, longitude: float, timestamp: str | None = None,
                          session_id: str | None = None, source: str = "mock") -> int:
        lat, lon = float(latitude), float(longitude)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("GPS coordinates are out of range")
        with self.connection() as c:
            cur = c.execute("INSERT INTO gps_locations(session_id,latitude,longitude,timestamp,source) VALUES(?,?,?,?,?)",
                            (session_id, lat, lon, timestamp or now_iso(), source))
            return int(cur.lastrowid)

    def latest_gps(self, session_id: str | None = None) -> dict | None:
        with self.connection() as c:
            if session_id:
                r = c.execute("SELECT * FROM gps_locations WHERE session_id=? ORDER BY timestamp DESC,location_id DESC LIMIT 1", (session_id,)).fetchone()
            else:
                r = c.execute("SELECT * FROM gps_locations ORDER BY timestamp DESC,location_id DESC LIMIT 1").fetchone()
        return dict(r) if r else None

    def log_event(self, event_type: str, value: Any = None, session_id: str | None = None,
                  details: dict | None = None, timestamp: str | None = None) -> int:
        with self.connection() as c:
            cur = c.execute("INSERT INTO safety_events(session_id,event_type,value,details_json,timestamp) VALUES(?,?,?,?,?)",
                            (session_id, event_type.upper(), None if value is None else str(value),
                             json.dumps(details or {}, default=str), timestamp or now_iso()))
            return int(cur.lastrowid)

    def create_emergency(self, reason: str, session_id: str | None = None,
                         driver_id: str | None = None, vehicle_id: str | None = None,
                         location: dict | None = None, status: str = "ACTIVE",
                         details: dict | None = None) -> dict:
        eid = f"E-{uuid.uuid4().hex[:8].upper()}"
        loc = location or {}
        created = now_iso()
        with self.connection() as c:
            c.execute("""INSERT INTO emergencies(emergency_id,session_id,driver_id,vehicle_id,reason,latitude,longitude,
                      location_timestamp,created_at,status,details_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                      (eid, session_id, driver_id, vehicle_id, reason, loc.get("latitude"), loc.get("longitude"),
                       loc.get("timestamp"), created, status, json.dumps(details or {}, default=str)))
        return {"emergency_id": eid, "session_id": session_id, "driver_id": driver_id, "vehicle_id": vehicle_id,
                "reason": reason, "latitude": loc.get("latitude"), "longitude": loc.get("longitude"),
                "location_timestamp": loc.get("timestamp"), "created_at": created, "status": status}

    def _query(self, sql: str, params: tuple = ()) -> list[dict]:
        with self.connection() as c:
            return [dict(r) for r in c.execute(sql, params).fetchall()]

    def recent_events(self, limit: int = 50, session_id: str | None = None) -> list[dict]:
        if session_id:
            return self._query("SELECT * FROM safety_events WHERE session_id=? ORDER BY timestamp DESC LIMIT ?", (session_id, limit))
        return self._query("SELECT * FROM safety_events ORDER BY timestamp DESC LIMIT ?", (limit,))

    def session_history(self, limit: int = 100, driver_id: str | None = None) -> list[dict]:
        if driver_id:
            return self._query("SELECT s.*,d.name AS driver_name FROM sessions s LEFT JOIN drivers d USING(driver_id) WHERE s.driver_id=? ORDER BY s.started_at DESC LIMIT ?", (driver_id, limit))
        return self._query("SELECT s.*,d.name AS driver_name FROM sessions s LEFT JOIN drivers d USING(driver_id) ORDER BY s.started_at DESC LIMIT ?", (limit,))

    def emergency_history(self, limit: int = 100, driver_id: str | None = None) -> list[dict]:
        sql = "SELECT e.*,d.name AS driver_name FROM emergencies e LEFT JOIN drivers d USING(driver_id)"
        if driver_id:
            return self._query(sql + " WHERE e.driver_id=? ORDER BY e.created_at DESC LIMIT ?", (driver_id, limit))
        return self._query(sql + " ORDER BY e.created_at DESC LIMIT ?", (limit,))

    def gps_history(self, limit: int = 100, session_id: str | None = None) -> list[dict]:
        if session_id:
            return self._query("SELECT * FROM gps_locations WHERE session_id=? ORDER BY timestamp DESC LIMIT ?", (session_id, limit))
        return self._query("SELECT * FROM gps_locations ORDER BY timestamp DESC LIMIT ?", (limit,))

    def dashboard_state(self) -> dict:
        session = self.get_active_session()
        if not session:
            return {"session": None, "driver": None, "vehicle": None, "location": self.latest_gps(),
                    "statuses": {}, "emergency": self.emergency_history(1)[0] if self.emergency_history(1) else None}
        events = self.recent_events(100, session["session_id"])
        statuses = {}
        mapping = {"DROWSINESS": "drowsiness", "DISTRACTION": "distraction", "VOICE_RESPONSE": "voice_response", "GPS_STATUS": "gps_status"}
        for event in reversed(events):
            key = mapping.get(event["event_type"])
            if key: statuses[key] = event["value"]
        emergencies = self.emergency_history(1)
        return {"session": session, "driver": self.get_driver(session["driver_id"]),
                "vehicle": self.get_vehicle(session["vehicle_id"]), "location": self.latest_gps(session["session_id"]),
                "statuses": statuses, "emergency": emergencies[0] if emergencies and emergencies[0]["status"] == "ACTIVE" else None}
