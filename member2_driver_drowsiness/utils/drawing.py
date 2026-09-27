# utils/drawing.py

import cv2


def draw_landmarks(frame, face_landmarks):

    height, width = frame.shape[:2]

    # Important facial landmarks
    indices = [
        1,      # Nose
        33,     # Left eye
        263,    # Right eye
        61,     # Mouth
        291,    # Mouth
        152     # Chin
    ]

    for index in indices:

        landmark = face_landmarks.landmark[index]

        x = int(landmark.x * width)
        y = int(landmark.y * height)

        cv2.circle(
            frame,
            (x, y),
            3,
            (0, 255, 0),
            -1
        )


def draw_text(
    frame,
    text,
    position,
    color=(255, 255, 255),
    scale=0.6
):

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        2,
        cv2.LINE_AA
    )


def draw_dashboard(frame, result):

    y = 30

    line_height = 28

    # ------------------------------------------
    # Title
    # ------------------------------------------

    draw_text(
        frame,
        "DRIVER MONITORING",
        (20, y),
        (0, 255, 255),
        0.8
    )

    y += 40

    # ------------------------------------------
    # Eyes
    # ------------------------------------------

    eyes = result["eyes"]

    draw_text(
        frame,
        f"EAR: {eyes['ear']}",
        (20, y)
    )

    y += line_height

    eye_state = (
        "CLOSED"
        if eyes["closed"]
        else "OPEN"
    )

    draw_text(
        frame,
        f"Eyes: {eye_state}",
        (20, y)
    )

    y += line_height

    draw_text(
        frame,
        f"Blink Count: {eyes['blink_count']}",
        (20, y)
    )

    y += line_height

    # ------------------------------------------
    # Mouth
    # ------------------------------------------

    mouth = result["mouth"]

    draw_text(
        frame,
        f"MAR: {mouth['mar']}",
        (20, y)
    )

    y += line_height

    draw_text(
        frame,
        f"Yawning: {mouth['yawning']}",
        (20, y)
    )

    y += line_height

    draw_text(
        frame,
        f"Yawns: {mouth['yawn_count']}",
        (20, y)
    )

    y += line_height

    # ------------------------------------------
    # Head
    # ------------------------------------------

    head = result["head_pose"]

    draw_text(
        frame,
        f"Yaw: {head['yaw']} deg",
        (20, y)
    )

    y += line_height

    draw_text(
        frame,
        f"Pitch: {head['pitch']} deg",
        (20, y)
    )

    y += line_height

    # ------------------------------------------
    # Distraction
    # ------------------------------------------

    distraction = result["distraction"]

    draw_text(
        frame,
        f"Distraction: {distraction['level']}",
        (20, y)
    )

    y += line_height

    draw_text(
        frame,
        f"Looking Away: {distraction['looking_away']}",
        (20, y)
    )

    y += line_height

    # ------------------------------------------
    # Drowsiness
    # ------------------------------------------

    drowsiness = result["drowsiness"]

    draw_text(
        frame,
        f"Drowsiness Score: {drowsiness['score']}",
        (20, y)
    )

    y += line_height

    draw_text(
        frame,
        f"Drowsiness: {drowsiness['level']}",
        (20, y)
    )