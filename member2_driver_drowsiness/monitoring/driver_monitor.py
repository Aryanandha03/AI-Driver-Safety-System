# monitoring/driver_monitor.py

from detection.face_mesh import FaceMeshDetector
from detection.head_pose import HeadPoseEstimator
import config
from analysis.ear import calculate_ear
from analysis.blink import BlinkMonitor

from analysis.yawn import (
    calculate_mar,
    YawnDetector
)

from analysis.distraction import (
    DistractionDetector
)

from analysis.drowsiness import (
    DrowsinessAnalyzer
)

from models.result import create_result


class DriverMonitor:

    def __init__(self):

        # ------------------------------------------
        # Detection
        # ------------------------------------------

        self.face_detector = FaceMeshDetector()

        self.head_pose_detector = (
            HeadPoseEstimator(
                config.FRAME_WIDTH,
                config.FRAME_HEIGHT
            )
        )

        # ------------------------------------------
        # Analysis
        # ------------------------------------------

        self.blink_monitor = BlinkMonitor()

        self.yawn_detector = YawnDetector()

        self.distraction_detector = (
            DistractionDetector()
        )

        self.drowsiness_analyzer = (
            DrowsinessAnalyzer()
        )

    def get_eye_points(
        self,
        landmarks,
        frame_shape
    ):

        height, width = frame_shape[:2]

        # MediaPipe iris/refined landmarks

        # Left eye
        left_indices = [
            33,
            160,
            158,
            133,
            153,
            144
        ]

        # Right eye
        right_indices = [
            362,
            385,
            387,
            263,
            373,
            380
        ]

        left_eye = []

        right_eye = []

        for index in left_indices:

            landmark = landmarks.landmark[index]

            left_eye.append((
                landmark.x * width,
                landmark.y * height
            ))

        for index in right_indices:

            landmark = landmarks.landmark[index]

            right_eye.append((
                landmark.x * width,
                landmark.y * height
            ))

        return left_eye, right_eye

    def get_mouth_points(
        self,
        landmarks,
        frame_shape
    ):

        height, width = frame_shape[:2]

        mouth_indices = [
            61,
            13,
            14,
            291,
            17,
            0
        ]

        mouth_points = []

        for index in mouth_indices:

            landmark = landmarks.landmark[index]

            mouth_points.append((
                landmark.x * width,
                landmark.y * height
            ))

        return mouth_points

    def process_frame(self, frame):

        # ------------------------------------------
        # Face detection
        # ------------------------------------------

        landmarks = self.face_detector.process(
            frame
        )

        # No face detected
        if landmarks is None:

            return None, None

        # ------------------------------------------
        # Eye processing
        # ------------------------------------------

        left_eye, right_eye = self.get_eye_points(
            landmarks,
            frame.shape
        )

        left_ear = calculate_ear(left_eye)

        right_ear = calculate_ear(right_eye)

        average_ear = (
            left_ear +
            right_ear
        ) / 2.0

        eye_data = self.blink_monitor.update(
            average_ear
        )

        # ------------------------------------------
        # Mouth processing
        # ------------------------------------------

        mouth_points = self.get_mouth_points(
            landmarks,
            frame.shape
        )

        mar = calculate_mar(
            mouth_points
        )

        yawn_data = self.yawn_detector.update(
            mar
        )

        # ------------------------------------------
        # Head pose
        # ------------------------------------------

        pose_data = self.head_pose_detector.estimate(landmarks)

        # ------------------------------------------
        # Distraction
        # ------------------------------------------

        distraction_data = (
            self.distraction_detector.update(
                pose_data["yaw"],
                pose_data["pitch"]
            )
        )

        # ------------------------------------------
        # Drowsiness
        # ------------------------------------------

        drowsiness_data = (
            self.drowsiness_analyzer.analyze(

                eye_data["prolonged_closure"],

                eye_data["blink_count"],

                yawn_data["yawning"]
            )
        )

        # ------------------------------------------
        # Final result
        # ------------------------------------------

        result = create_result(

            eye_data,

            yawn_data,

            pose_data,

            distraction_data,

            drowsiness_data
        )

        return result, landmarks

    def close(self):

        self.face_detector.close()