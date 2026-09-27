from datetime import datetime


def trigger_emergency(
    reason,
    response_status,
    driver_id="D001",
    session_id="S001"
):
    """
    Create a structured emergency event.

    This event can later be passed to:

    M4 - Emergency Response
    M5 - Dashboard / Database / Integration

    Driver ID and Session ID are temporary values.
    M5 can replace them with real values during integration.
    """

    emergency_event = {
        "driver_id": driver_id,
        "session_id": session_id,
        "emergency_trigger": True,
        "reason": reason,
        "response_status": response_status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    print("\n========== EMERGENCY EVENT ==========")

    print("Driver ID         :", emergency_event["driver_id"])
    print("Session ID        :", emergency_event["session_id"])
    print("Emergency Trigger :", emergency_event["emergency_trigger"])
    print("Reason            :", emergency_event["reason"])
    print("Response Status   :", emergency_event["response_status"])
    print("Timestamp         :", emergency_event["timestamp"])

    print("=====================================\n")

    return emergency_event