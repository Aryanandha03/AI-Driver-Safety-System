# analysis/drowsiness.py

from config import (
    DROWSINESS_MEDIUM_SCORE,
    DROWSINESS_HIGH_SCORE
)


class DrowsinessAnalyzer:

    def __init__(self):
        pass

    def analyze(
        self,
        prolonged_eye_closure,
        blink_count,
        yawning
    ):

        score = 0

        # ------------------------------------------
        # Prolonged eye closure
        # ------------------------------------------

        if prolonged_eye_closure:
            score += 50

        # ------------------------------------------
        # Yawning
        # ------------------------------------------

        if yawning:
            score += 25

        # ------------------------------------------
        # Blink behaviour
        #
        # This is only a basic experimental rule.
        # ------------------------------------------

        if blink_count >= 20:
            score += 10

        # Limit score
        score = min(score, 100)

        # ------------------------------------------
        # Determine level
        # ------------------------------------------

        if score >= DROWSINESS_HIGH_SCORE:

            level = "HIGH"

        elif score >= DROWSINESS_MEDIUM_SCORE:

            level = "MEDIUM"

        else:

            level = "LOW"

        return {
            "score": score,
            "level": level
        }