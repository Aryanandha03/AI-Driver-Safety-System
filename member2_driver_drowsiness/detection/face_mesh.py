# detection/face_mesh.py

import cv2
import mediapipe as mp


class FaceMeshDetector:

    def __init__(
        self,
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ):
        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process(self, frame):

        # MediaPipe expects RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None

        return results.multi_face_landmarks[0]

    def close(self):
        self.face_mesh.close()