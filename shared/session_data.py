current_session = {
    "driver_id": "UNKNOWN",
    "driver_name": "UNKNOWN",
    "vehicle_id": "UNKNOWN",
    "session_id": None,
    "status": "NOT_STARTED"
}


def update_session(
    driver_id,
    driver_name,
    vehicle_id,
    session_id,
    status
):
    current_session["driver_id"] = driver_id
    current_session["driver_name"] = driver_name
    current_session["vehicle_id"] = vehicle_id
    current_session["session_id"] = session_id
    current_session["status"] = status


def get_session():
    return current_session.copy()