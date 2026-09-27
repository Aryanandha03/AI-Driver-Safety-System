# Member 5 — Driver Safety Data, GPS & Dashboard

This package owns GPS data capture, SQLite storage, emergency context aggregation, event integration, and a Streamlit dashboard. It does not implement face/hand recognition, drowsiness, distraction, or voice recognition; those modules send events through `EventProcessor`.

## Setup and run

```bash
cd member5_dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app creates `member5.db` beside `app.py`. Set `MEMBER5_DB_PATH` to choose another database. GPS defaults to a deterministic mock location (Googleplex coordinates); real GPS is provided by injecting an object implementing `get_location()` into `GPSService`. Provider errors are caught and reported in `last_error`, and the last valid fix is retained.

## Demo

Use **Load / refresh demo data** in the sidebar to create a demo driver/session, store a mock GPS fix, and add sample safety events. Use **Simulate silent gesture emergency** to create an emergency record and display its context. Both actions write to the same SQLite database as the dashboard.

## Integration contract

```python
from database.db import Database
from integration.event_processor import EventProcessor

events = EventProcessor(Database("member5.db"))
events.process_event("DRIVER_IDENTIFIED", {"driver_id": "D001", "name": "Arun"})
events.process_event("SESSION_STARTED", {"session_id": "S001", "driver_id": "D001", "vehicle_id": "V001"})
events.process_event("DROWSINESS", {"session_id": "S001", "value": "HIGH"})
events.process_event("EMERGENCY", {"session_id": "S001", "reason": "Silent Hand Gesture"})
```

Supported event names: `DRIVER_IDENTIFIED`, `SESSION_STARTED`, `DROWSINESS`, `DISTRACTION`, `VOICE_RESPONSE`, `HAND_GESTURE`, `EMERGENCY`, `SESSION_ENDED`. Events use a payload dictionary; values can be supplied as `value`, `status`, or `result`. An emergency may include `location` with `latitude`, `longitude`, optional `timestamp` and `source`. A hand gesture is logged as an event; set `emergency: true` to create its emergency record too. `EMERGENCY` always persists an emergency and collects the active session, driver, vehicle, and latest GPS fix when omitted.

Storage functions are exposed on `Database`: `create_session`, `end_session`, `save_gps_location`, `log_event`, `create_emergency`, `recent_events`, `session_history`, `emergency_history`, and `gps_history`.
