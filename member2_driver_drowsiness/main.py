# main.py

import cv2

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT
)

from monitoring.driver_monitor import (
    DriverMonitor
)

from utils.drawing import (
    draw_landmarks,
    draw_dashboard
)


def main():

    # ------------------------------------------
    # Camera
    # ------------------------------------------

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    if not camera.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        return

    # ------------------------------------------
    # Driver Monitor
    # ------------------------------------------

    monitor = DriverMonitor()

    print("--------------------------------")
    print(" Driver Monitoring Started")
    print("--------------------------------")
    print("Press Q to quit.")

    # ------------------------------------------
    # Main loop
    # ------------------------------------------

    while True:

        success, frame = camera.read()

        if not success:

            print(
                "ERROR: Could not read frame."
            )

            break

        # Optional mirror effect
        frame = cv2.flip(
            frame,
            1
        )

        # --------------------------------------
        # Process
        # --------------------------------------

        result, landmarks = (
            monitor.process_frame(frame)
        )

        # --------------------------------------
        # Draw results
        # --------------------------------------

        if landmarks is not None:

            draw_landmarks(
                frame,
                landmarks
            )

            draw_dashboard(
                frame,
                result
            )

        else:

            cv2.putText(
                frame,
                "NO FACE DETECTED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # --------------------------------------
        # Display
        # --------------------------------------

        cv2.imshow(
            "Driver Monitoring",
            frame
        )

        # --------------------------------------
        # Quit
        # --------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break

    # ------------------------------------------
    # Cleanup
    # ------------------------------------------

    monitor.close()

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()