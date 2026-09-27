# analysis/distraction.py

import time

from config import (
    YAW_THRESHOLD,
    PITCH_THRESHOLD,
    LOOK_AWAY_DURATION
)


class DistractionDetector:

    def __init__(self):

        self.away_start_time = None

        self.looking_away = False

        self.distraction_level = "LOW"

    def update(self, yaw, pitch):

        current_time = time.time()

        head_away = (
            abs(yaw) > YAW_THRESHOLD
            or
            abs(pitch) > PITCH_THRESHOLD
        )

        # ------------------------------------------
        # Driver starts looking away
        # ------------------------------------------

        if head_away:

            if self.away_start_time is None:

                self.away_start_time = current_time

            duration = (
                current_time -
                self.away_start_time
            )

            if duration >= LOOK_AWAY_DURATION:

                self.looking_away = True
                self.distraction_level = "HIGH"

            else:

                self.looking_away = False
                self.distraction_level = "MEDIUM"

        # ------------------------------------------
        # Driver looks forward again
        # ------------------------------------------

        else:

            self.away_start_time = None

            self.looking_away = False

            self.distraction_level = "LOW"

        return {
            "yaw": yaw,
            "pitch": pitch,
            "looking_away": self.looking_away,
            "level": self.distraction_level
        }