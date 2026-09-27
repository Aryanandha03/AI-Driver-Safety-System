import cv2
import numpy as np


class HeadPoseEstimator:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Approximate camera parameters
        focal_length = frame_width

        self.camera_matrix = np.array(
            [
                [focal_length, 0, frame_width / 2],
                [0, focal_length, frame_height / 2],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

        self.dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # Generic 3D face model points
        self.model_points = np.array(
            [
                (0.0, 0.0, 0.0),          # Nose
                (0.0, -330.0, -65.0),     # Chin
                (-225.0, 170.0, -135.0),  # Left eye
                (225.0, 170.0, -135.0),   # Right eye
                (-150.0, -150.0, -125.0), # Left mouth
                (150.0, -150.0, -125.0),  # Right mouth
            ],
            dtype=np.float64,
        )

    def estimate(self, landmarks):
        """
        Estimate head orientation from MediaPipe face landmarks.

        Returns:
            dict containing yaw, pitch and roll.
        """
        landmark_list = landmarks.landmark

        image_points = np.array(
            [
                [
                    landmark_list[1].x * self.frame_width,
                    landmark_list[1].y * self.frame_height,
                ],
                [
                    landmark_list[152].x * self.frame_width,
                    landmark_list[152].y * self.frame_height,
                ],
                [
                    landmark_list[33].x * self.frame_width,
                    landmark_list[33].y * self.frame_height,
                ],
                [
                    landmark_list[263].x * self.frame_width,
                    landmark_list[263].y * self.frame_height,
                ],
                [
                    landmark_list[61].x * self.frame_width,
                    landmark_list[61].y * self.frame_height,
                ],
                [
                    landmark_list[291].x * self.frame_width,
                    landmark_list[291].y * self.frame_height,
                ],
            ],
            dtype=np.float64,
        )

        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points,
            image_points,
            self.camera_matrix,
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            return {
                "yaw": 0.0,
                "pitch": 0.0,
                "roll": 0.0,
            }

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

        # Build projection matrix
        projection_matrix = np.hstack(
            (rotation_matrix, translation_vector)
        )

        # Extract Euler angles
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(
            projection_matrix
        )

        # OpenCV may return a (3, 1) array.
        # Flatten it before converting individual values to float.
        euler_angles = np.asarray(euler_angles).flatten()

        pitch = float(euler_angles[0])
        yaw = float(euler_angles[1])
        roll = float(euler_angles[2])

        return {
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll,
        }