"""Member 4: silent thumbs-up emergency gesture and alert preparation.

Run this file with a webcam after installing requirements.  The module exposes
``SilentEmergencyController.process_frame`` for the group's final integration.
It deliberately receives driver/session/vehicle data from the other modules
and uses injected GPS/notification functions instead of owning their systems.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Callable, Optional
import time

try:
    import cv2
    import mediapipe as mp
except ImportError:  # Keeps imports useful for non-camera integration tests.
    cv2 = None
    mp = None


@dataclass(frozen=True)
class EmergencyContext:
    """Information supplied by the integration layer (Members 1, 3 and 5)."""

    driver_id: str = "UNKNOWN"
    session_id: str = "UNKNOWN"
    vehicle_id: str = "UNKNOWN"
    location: str = "GPS unavailable"


@dataclass(frozen=True)
class EmergencyAlert:
    reason: str
    driver_id: str
    session_id: str
    vehicle_id: str
    location: str
    timestamp_utc: str

    def message(self) -> str:
        return (
            "SILENT EMERGENCY\n"
            f"Reason: {self.reason}\nDriver: {self.driver_id}\n"
            f"Session: {self.session_id}\nVehicle: {self.vehicle_id}\n"
            f"Location: {self.location}\nTime (UTC): {self.timestamp_utc}\n"
            "Assistance required."
        )


class SilentEmergencyController:
    """Detects held thumbs-up or open-palm gestures and raises one alert.

    A gesture must appear in ``confirmation_frames`` consecutive frames.  Once
    triggered, it cannot trigger again until ``cooldown_seconds`` has elapsed.
    This avoids accidental or repeated notifications.
    """

    # MediaPipe hand-landmark indexes.
    FINGER_TIPS = (8, 12, 16, 20)
    FINGER_PIPS = (6, 10, 14, 18)

    def __init__(
        self,
        confirmation_frames: int = 24,
        cooldown_seconds: float = 30.0,
        notify: Optional[Callable[[EmergencyAlert], None]] = None,
    ) -> None:
        if confirmation_frames < 1 or cooldown_seconds < 0:
            raise ValueError("confirmation_frames must be >= 1 and cooldown_seconds >= 0")
        self.confirmation_frames = confirmation_frames
        self.cooldown_seconds = cooldown_seconds
        self.notify = notify or self._console_notify
        self._consecutive_matches = 0
        self._pending_gesture: Optional[str] = None
        self._last_trigger_at = float("-inf")

    @staticmethod
    def _console_notify(alert: EmergencyAlert) -> None:
        """Default safe notification hook. Replace during deployment."""
        print("\n--- ALERT READY FOR CONTACT/CONTROL ROOM ---")
        print(alert.message())

    @staticmethod
    def _distance(first, second) -> float:
        """2-D normalized landmark distance; independent of image resolution."""
        return ((first.x - second.x) ** 2 + (first.y - second.y) ** 2) ** 0.5

    @classmethod
    def _gesture_scores(cls, hand_landmarks) -> tuple[float, float]:
        """Return (thumbs-up, open-palm) confidence scores from 0.0 to 1.0."""
        points = hand_landmarks.landmark
        wrist, index_mcp, pinky_mcp = points[0], points[5], points[17]
        palm_width = cls._distance(index_mcp, pinky_mcp)
        if palm_width < 0.035:  # Ignore distant/background hands.
            return 0.0, 0.0

        extended_fingers = 0
        folded_fingers = 0
        for tip_index, pip_index in zip(cls.FINGER_TIPS, cls.FINGER_PIPS):
            tip_distance = cls._distance(points[tip_index], wrist)
            pip_distance = cls._distance(points[pip_index], wrist)
            ratio = tip_distance / max(pip_distance, 0.001)
            if ratio > 1.08:
                extended_fingers += 1
            if ratio < 1.12:
                folded_fingers += 1

        thumb_tip, thumb_ip = points[4], points[3]
        thumb_extension = cls._distance(thumb_tip, wrist) / max(cls._distance(thumb_ip, wrist), 0.001)
        thumb_spread = cls._distance(thumb_tip, index_mcp) / palm_width
        # No up/down test: tilted hands and mirrored webcams remain valid.
        thumb_raised = min(1.0, max(0.0, (thumb_extension - 1.03) / 0.42))
        thumb_spread_score = min(1.0, max(0.0, thumb_spread / 0.85))
        thumbs_up_score = (
            0.65 * (folded_fingers / 4.0)
            + 0.25 * thumb_raised
            + 0.10 * thumb_spread_score
        )
        open_palm_score = 0.75 * (extended_fingers / 4.0) + 0.25 * thumb_spread_score
        return thumbs_up_score, open_palm_score

    @classmethod
    def classify_gesture(cls, hand_landmarks) -> tuple[Optional[str], float]:
        """Return gesture name and confidence, or None if neither matches."""
        thumb_score, palm_score = cls._gesture_scores(hand_landmarks)
        if thumb_score >= 0.72 and thumb_score > palm_score:
            return "thumbs-up", thumb_score
        if palm_score >= 0.72:
            return "open-palm", palm_score
        return None, max(thumb_score, palm_score)

    @classmethod
    def is_open_palm(cls, hand_landmarks) -> bool:
        """Compatibility helper: true when either emergency gesture matches."""
        return cls.classify_gesture(hand_landmarks)[0] is not None

    is_thumbs_up = is_open_palm

    @staticmethod
    def _in_driver_zone(hand_landmarks) -> bool:
        """Accept hands only in the central driver-facing part of the frame."""
        points = hand_landmarks.landmark
        center_x = sum(point.x for point in points) / len(points)
        center_y = sum(point.y for point in points) / len(points)
        return 0.12 <= center_x <= 0.88 and 0.08 <= center_y <= 0.92

    def observe(self, gesture: Optional[str] | bool, context: EmergencyContext) -> Optional[EmergencyAlert]:
        """Alert only when the same recognized gesture stays stable."""
        current = "thumbs-up" if gesture is True else gesture if isinstance(gesture, str) else None
        if current and current == self._pending_gesture:
            self._consecutive_matches += 1
        elif current:
            self._pending_gesture = current
            self._consecutive_matches = 1
        else:
            self._pending_gesture = None
            self._consecutive_matches = 0
        if self._consecutive_matches < self.confirmation_frames:
            return None
        confirmed_gesture = self._pending_gesture or "hand gesture"
        self._consecutive_matches = 0
        self._pending_gesture = None
        return self.activate_emergency(context, f"Confirmed silent {confirmed_gesture} gesture")

    def activate_emergency(self, context: EmergencyContext, reason: str) -> Optional[EmergencyAlert]:
        """Create one emergency alert for gesture or Member 3 escalation.

        Member 3 should call this method after its response-verification step
        decides that an unsafe driver is unresponsive.  The same cooldown is
        applied to both paths so one incident does not create repeated alerts.
        """
        now = time.monotonic()
        if now - self._last_trigger_at < self.cooldown_seconds:
            return None
        self._last_trigger_at = now
        alert = EmergencyAlert(
            reason=reason,
            **asdict(context),
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        )
        self.notify(alert)
        return alert

    def process_frame(self, frame, context: EmergencyContext, hands) -> tuple[object, Optional[EmergencyAlert], Optional[str]]:
        """Process a frame; return annotated frame, alert, and gesture name."""
        if cv2 is None:
            raise RuntimeError("Install opencv-python and mediapipe to process camera frames.")
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detected_hands = result.multi_hand_landmarks or []
        gesture, confidence = None, 0.0
        for hand in detected_hands:
            if self._in_driver_zone(hand):
                candidate, score = self.classify_gesture(hand)
                if score > confidence:
                    gesture, confidence = candidate, score
        alert = self.observe(gesture, context)
        if alert:
            status = "EMERGENCY SENT"
        elif gesture:
            status = f"{gesture}: {self._consecutive_matches}/{self.confirmation_frames} ({confidence:.0%})"
        else:
            status = f"Show thumbs-up or open palm ({confidence:.0%})"
        color = (0, 0, 255) if alert else (0, 200, 255) if gesture else (0, 200, 0)
        cv2.putText(frame, status, (18, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        if detected_hands:
            drawer = mp.solutions.drawing_utils
            for hand in detected_hands:
                drawer.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
        return frame, alert, gesture


def run_demo() -> None:
    if cv2 is None or mp is None:
        raise SystemExit("Install dependencies first: pip install -r requirements-member4.txt")
    if not hasattr(mp, "solutions") or not hasattr(mp.solutions, "hands"):
        raise SystemExit(
            "Incompatible MediaPipe installation detected. Run this project with:\n"
            ".\\.venv\\Scripts\\python.exe member4_silent_emergency.py"
        )
    context = EmergencyContext(driver_id="D001", session_id="S001", vehicle_id="V001", location="Provided by GPS module")
    controller = SilentEmergencyController()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise SystemExit("Camera could not be opened.")
    with mp.solutions.hands.Hands(
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.60,
        min_tracking_confidence=0.60,
    ) as hands:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame, _, _ = controller.process_frame(cv2.flip(frame, 1), context, hands)
            cv2.imshow("Member 4 - Silent Emergency", frame)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_demo()
