"""Run with: streamlit run app.py"""
import os
import sys
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from dashboard.dashboard import render_dashboard
from database.db import Database
from gps.gps_service import GPSService
from integration.event_processor import EventProcessor

DB_PATH = os.getenv("MEMBER5_DB_PATH", str(BASE / "member5.db"))
db = Database(DB_PATH)
gps = GPSService()
processor = EventProcessor(db)


def demo_seed() -> None:
    """Idempotent, one-click demo setup."""
    active = db.get_active_session()
    if active:
        sid = active["session_id"]
    else:
        processor.process_event("DRIVER_IDENTIFIED", {"driver_id": "D001", "name": "Arun"})
        sid = processor.process_event("SESSION_STARTED", {"driver_id": "D001", "vehicle_id": "V001",
                    "vehicle_description": "Demo vehicle"})["session_id"]
    loc = gps.get_current_location()
    if loc:
        db.save_gps_location(loc.latitude, loc.longitude, loc.timestamp, sid, loc.source)
    processor.process_event("DROWSINESS", {"session_id": sid, "value": "LOW"})
    processor.process_event("DISTRACTION", {"session_id": sid, "value": "NONE"})
    processor.process_event("VOICE_RESPONSE", {"session_id": sid, "value": "NORMAL"})


if __name__ == "__main__":
    st.sidebar.header("Demo controls")
    if st.sidebar.button("Load / refresh demo data"):
        demo_seed()
        st.sidebar.success("Demo session and GPS location saved.")
    if st.sidebar.button("Simulate silent gesture emergency"):
        loc = gps.get_current_location()
        payload = {"reason": "Silent Hand Gesture", "location": loc.__dict__ if loc else None}
        payload["location"] = ({"latitude": loc.latitude, "longitude": loc.longitude,
                                 "timestamp": loc.timestamp, "source": loc.source} if loc else None)
        result = processor.process_event("EMERGENCY", payload)
        st.sidebar.success(f"Logged {result['emergency']['emergency_id']}")
    st.sidebar.caption(f"GPS mode: {gps.mode}. GPS gracefully falls back to unavailable on provider errors.")
    render_dashboard(db)
