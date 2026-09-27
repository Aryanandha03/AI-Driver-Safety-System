"""Collect emergency context and persist a dashboard-ready alert object."""
from __future__ import annotations

from database.db import Database


class EmergencyService:
    def __init__(self, db: Database):
        self.db = db

    def handle_emergency(self, reason: str, session_id: str | None = None,
                         driver_id: str | None = None, vehicle_id: str | None = None,
                         location: dict | None = None, details: dict | None = None) -> dict:
        session = None
        if session_id:
            for item in self.db.session_history(1000):
                if item["session_id"] == session_id:
                    session = item
                    break
        if session is None:
            session = self.db.get_active_session()
        sid = session_id or (session or {}).get("session_id")
        did = driver_id or (session or {}).get("driver_id")
        vid = vehicle_id or (session or {}).get("vehicle_id")
        driver = self.db.get_driver(did)
        vehicle = self.db.get_vehicle(vid)
        loc = location or self.db.latest_gps(sid)
        emergency = self.db.create_emergency(reason=reason or "Emergency signal", session_id=sid,
                                             driver_id=did, vehicle_id=vid, location=loc,
                                             details=details)
        return {**emergency, "driver_name": (driver or {}).get("name", "Unknown"),
                "vehicle_description": (vehicle or {}).get("description"), "driver": driver,
                "vehicle": vehicle}
