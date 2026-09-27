"""Streamlit dashboard entry renderer."""
import pandas as pd
import streamlit as st

from database.db import Database


def render_dashboard(db: Database) -> None:
    st.set_page_config(page_title="Driver Safety Dashboard", page_icon="🚗", layout="wide")
    st.title("🚗 DRIVER SAFETY DASHBOARD")
    state = db.dashboard_state()
    session, driver, vehicle = state["session"], state["driver"], state["vehicle"]
    statuses, location = state["statuses"], state["location"]
    cols = st.columns(4)
    cols[0].metric("Driver Name", (driver or {}).get("name", "—"))
    cols[1].metric("Driver ID", (driver or {}).get("driver_id", "—"))
    cols[2].metric("Vehicle ID", (session or {}).get("vehicle_id", "—"))
    cols[3].metric("Session ID", (session or {}).get("session_id", "No active session"))
    cols = st.columns(4)
    cols[0].metric("Drowsiness Status", statuses.get("drowsiness", "UNKNOWN"))
    cols[1].metric("Distraction Status", statuses.get("distraction", "UNKNOWN"))
    cols[2].metric("Voice Response", statuses.get("voice_response", "—"))
    cols[3].metric("GPS Status", statuses.get("gps_status", "Active" if location else "Unavailable"))
    st.divider()
    alert = state["emergency"]
    if alert:
        st.error("🚨 EMERGENCY MODE")
        st.write(f"**Reason:** {alert['reason']}  ·  **Driver:** {alert.get('driver_name') or 'Unknown'}  ·  **Vehicle:** {alert.get('vehicle_id') or 'Unknown'}")
        st.write(f"**Session:** {alert.get('session_id') or '—'}  ·  **GPS:** {alert.get('latitude')}, {alert.get('longitude')}  ·  **Time:** {alert.get('created_at')}  ·  **Status:** {alert.get('status')}")
    else:
        st.success("Emergency Status: NO ACTIVE EMERGENCY")
    if location:
        st.caption(f"Latest location · {location['latitude']:.6f}, {location['longitude']:.6f} · {location['timestamp']} · {location.get('source', 'stored')}")
        st.map(pd.DataFrame([{"lat": location["latitude"], "lon": location["longitude"]}]))
    st.subheader("History")
    drivers = db._query("SELECT driver_id,name FROM drivers ORDER BY name")
    driver_options = ["All drivers"] + [f"{d['name']} ({d['driver_id']})" for d in drivers]
    selected = st.selectbox("Filter by driver", driver_options)
    did = drivers[driver_options.index(selected)-1]["driver_id"] if selected != "All drivers" else None
    a, b = st.columns(2)
    a.markdown("**Session history**")
    a.dataframe(pd.DataFrame(db.session_history(100, did)), width="stretch", hide_index=True)
    b.markdown("**Emergency history**")
    b.dataframe(pd.DataFrame(db.emergency_history(100, did)), width="stretch", hide_index=True)
    c, d = st.columns(2)
    c.markdown("**GPS history**")
    c.dataframe(pd.DataFrame(db.gps_history(100, (session or {}).get("session_id"))), width="stretch", hide_index=True)
    d.markdown("**Recent safety events**")
    cands = db.session_history(100, did)
    selected_session = st.selectbox("Filter events by session", ["All sessions"] + [x["session_id"] for x in cands])
    events = db.recent_events(100, selected_session if selected_session != "All sessions" else None)
    d.dataframe(pd.DataFrame(events), width="stretch", hide_index=True)
