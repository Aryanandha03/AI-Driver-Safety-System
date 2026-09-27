# Member 4 — Silent Emergency Hand Gesture + Emergency Response

This folder contains only Member 4's module for the **AI-Based Intelligent Driver Safety and Emergency Response System**. It detects either a deliberate, held **thumbs-up (👍)** or **open-palm (✋)** gesture and produces a confirmed silent-emergency alert without requiring the driver to speak.

Member 4 owns the project flow from **Signal → Alert**:

`Hand gesture / unresponsive-driver escalation → verification → silent emergency mode → emergency alert`

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-member4.txt
.\.venv\Scripts\python.exe member4_silent_emergency.py
```

Using the project virtual environment is important: it prevents unrelated
global TensorFlow/MediaPipe packages from interfering with this project.
If you need to refresh the project's packages, run:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade --force-reinstall -r requirements-member4.txt
```

Show either a clear thumbs-up (👍), with the other fingers folded, or an open palm (✋), with fingers spread, in the central camera area for roughly 24 frames (about 0.8 seconds). The preview displays the recognized gesture and confidence. Press `Q` or `Esc` to exit.

## Safeguards

- The gesture must remain visible for 24 consecutive frames.
- After an alert, the 30-second cooldown blocks duplicate alerts.
- It checks both gestures using palm-relative landmark distances, and ignores very small or off-centre hands.
- The default notifier prints the alert. Replace `notify` with your SMS, email, or control-room API call when integrating.

## Group integration contract

Members 1, 3 and 5 should provide `EmergencyContext` values: `driver_id`, `session_id`, `vehicle_id`, and `location`.

```python
from member4_silent_emergency import EmergencyContext, SilentEmergencyController

def notify_control_room(alert):
    print(alert.message())  # Replace with the agreed notification API

controller = SilentEmergencyController(notify=notify_control_room)
context = EmergencyContext("D001", "S001", "V001", "12.9716, 77.5946")
# In the shared camera loop:
annotated_frame, emergency_alert, gesture_seen = controller.process_frame(frame, context, hands)
```

## Emergency paths

1. **Silent emergency:** the driver holds either the thumbs-up (👍) or open-palm (✋) gesture to the camera. The system verifies the same gesture across 24 consecutive frames before alerting.
2. **Unresponsive driver:** Member 3 can escalate its failed response-verification result into the same emergency workflow:

```python
alert = controller.activate_emergency(
    context,
    reason="Driver did not respond after critical drowsiness warning",
)
```

The module returns an `EmergencyAlert` object to Member 5 for GPS/database/dashboard handling. Its alert format includes the emergency condition, driver/session and vehicle information, supplied GPS location, and incident time. It does not implement GPS collection, database storage, dashboard code, face recognition, drowsiness detection, or voice verification.
