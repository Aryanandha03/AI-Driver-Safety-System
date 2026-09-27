"""Simple event interface. Call process_event(type, payload) from team modules."""
from __future__ import annotations

from database.db import Database
from emergency.emergency_service import EmergencyService

SUPPORTED_EVENTS = {"DRIVER_IDENTIFIED", "SESSION_STARTED", "DROWSINESS", "DISTRACTION",
                    "VOICE_RESPONSE", "HAND_GESTURE", "EMERGENCY", "SESSION_ENDED"}


class EventProcessor:
    def __init__(self, db: Database):
        self.db = db
        self.emergencies = EmergencyService(db)

    def process_event(self, event_type: str, payload: dict | None = None) -> dict:
        kind = event_type.upper()
        data = payload or {}
        if kind not in SUPPORTED_EVENTS:
            raise ValueError(f"Unsupported event type: {kind}")
        result: dict = {"event_type": kind, "ok": True}
        sid = data.get("session_id") or (self.db.get_active_session() or {}).get("session_id")
        if kind == "DRIVER_IDENTIFIED":
            did = data.get("driver_id")
            name = data.get("name") or data.get("driver_name")
            if not did or not name: raise ValueError("DRIVER_IDENTIFIED requires driver_id and name")
            self.db.upsert_driver(did, name, data.get("metadata"))
            if data.get("vehicle_id"): self.db.upsert_vehicle(data["vehicle_id"], data.get("vehicle_description"))
        elif kind == "SESSION_STARTED":
            did, vid = data.get("driver_id"), data.get("vehicle_id")
            if did and data.get("driver_name"): self.db.upsert_driver(did, data["driver_name"])
            if vid: self.db.upsert_vehicle(vid, data.get("vehicle_description"))
            result["session_id"] = self.db.create_session(did, vid, data.get("session_id"))
            sid = result["session_id"]
        elif kind == "SESSION_ENDED":
            if sid: self.db.end_session(sid)
            else: raise ValueError("SESSION_ENDED requires an active session")
        elif kind == "EMERGENCY":
            if data.get("location"):
                loc = data["location"]
                self.db.save_gps_location(loc["latitude"], loc["longitude"], loc.get("timestamp"), sid, loc.get("source", "event"))
            alert = self.emergencies.handle_emergency(data.get("reason", "Emergency signal"), sid,
                    data.get("driver_id"), data.get("vehicle_id"), data.get("location"), data)
            result["emergency"] = alert
        else:
            if kind == "HAND_GESTURE" and data.get("emergency"):
                result["emergency"] = self.emergencies.handle_emergency(
                    data.get("reason", "Silent Hand Gesture"), sid, data.get("driver_id"),
                    data.get("vehicle_id"), data.get("location"), data)
            value = data.get("value", data.get("status", data.get("result")))
            result["event_id"] = self.db.log_event(kind, value, sid, data)
        return result

    __call__ = process_event
