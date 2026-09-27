# analysis/yawn.py

import time
import numpy as np


def euclidean_distance(point1, point2):

    point1 = np.array(point1)
    point2 = np.array(point2)

    return np.linalg.norm(point1 - point2)


def calculate_mar(mouth_points):

    if len(mouth_points) != 6:
        raise ValueError(
            "MAR requires exactly 6 mouth points."
        )

    p1, p2, p3, p4, p5, p6 = mouth_points

    vertical_1 = euclidean_distance(
        p2,
        p6
    )

    vertical_2 = euclidean_distance(
        p3,
        p5
    )

    horizontal = euclidean_distance(
        p1,
        p4
    )

    if horizontal == 0:
        return 0.0

    mar = (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)

    return float(mar)


class YawnDetector:

    def __init__(
        self,
        threshold=0.60,
        duration=0.8
    ):

        self.threshold = threshold
        self.duration = duration

        self.mouth_open = False
        self.open_start_time = None

        self.yawn_count = 0
        self.yawning = False

    def update(self, mar):

        current_time = time.time()

        mouth_open = mar > self.threshold

        # Mouth just opened
        if mouth_open and not self.mouth_open:

            self.mouth_open = True

            self.open_start_time = current_time

            self.yawning = False

        # Mouth remains open
        elif mouth_open and self.mouth_open:

            duration = (
                current_time -
                self.open_start_time
            )

            if duration >= self.duration:

                if not self.yawning:
                    self.yawn_count += 1

                self.yawning = True

        # Mouth closed
        elif not mouth_open and self.mouth_open:

            self.mouth_open = False
            self.open_start_time = None
            self.yawning = False

        return {
            "mar": mar,
            "mouth_open": mouth_open,
            "yawning": self.yawning,
            "yawn_count": self.yawn_count
        }