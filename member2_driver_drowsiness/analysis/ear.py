# analysis/ear.py

import numpy as np


def euclidean_distance(point1, point2):

    point1 = np.array(point1)
    point2 = np.array(point2)

    return np.linalg.norm(point1 - point2)


def calculate_ear(eye_points):

    if len(eye_points) != 6:
        raise ValueError(
            "EAR requires exactly 6 eye points."
        )

    p1, p2, p3, p4, p5, p6 = eye_points

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

    ear = (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)

    return float(ear)