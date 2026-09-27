# analysis/blink.py

import time

from config import (
    EAR_THRESHOLD,
    MIN_BLINK_DURATION,
    MAX_BLINK_DURATION
)


class BlinkMonitor:

    def __init__(self):

        self.eye_closed = False

        self.closed_start_time = None

        self.blink_count = 0

        self.last_blink_duration = 0.0

        self.prolonged_closure = False

    def update(self, ear):

        current_time = time.time()

        eyes_closed = ear < EAR_THRESHOLD

        # ------------------------------------------
        # Eyes just became closed
        # ------------------------------------------

        if eyes_closed and not self.eye_closed:

            self.eye_closed = True

            self.closed_start_time = current_time

            self.prolonged_closure = False

        # ------------------------------------------
        # Eyes remain closed
        # ------------------------------------------

        elif eyes_closed and self.eye_closed:

            duration = (
                current_time -
                self.closed_start_time
            )

            self.last_blink_duration = duration

            # Prolonged eye closure
            if duration >= 1.5:

                self.prolonged_closure = True

        # ------------------------------------------
        # Eyes opened again
        # ------------------------------------------

        elif not eyes_closed and self.eye_closed:

            duration = (
                current_time -
                self.closed_start_time
            )

            self.last_blink_duration = duration

            # Count normal blink
            if (
                duration >= MIN_BLINK_DURATION
                and duration <= MAX_BLINK_DURATION
            ):
                self.blink_count += 1

            self.eye_closed = False
            self.closed_start_time = None

        return {
            "ear": ear,
            "eyes_closed": eyes_closed,
            "blink_count": self.blink_count,
            "blink_duration": self.last_blink_duration,
            "prolonged_closure": self.prolonged_closure
        }