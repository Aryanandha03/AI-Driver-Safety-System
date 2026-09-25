import cv2
import numpy as np
from insightface.app import FaceAnalysis

from config import (
    MODEL_NAME,
    DETECTION_SIZE,
    FACE_SIMILARITY_THRESHOLD
)


class FaceEngine:

    def __init__(self):
        print("Loading InsightFace...")

        self.app = FaceAnalysis(
            name=MODEL_NAME,
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=-1,
            det_size=DETECTION_SIZE
        )

        print("InsightFace loaded.")

    def get_faces(self, frame):
        return self.app.get(frame)

    def get_embedding(self, face):
        return face.embedding

    def compare_embeddings(self, embedding1, embedding2):

        embedding1 = np.asarray(embedding1)
        embedding2 = np.asarray(embedding2)

        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) *
            np.linalg.norm(embedding2)
        )

        return float(similarity)

    def is_match(self, similarity):
        return similarity >= FACE_SIMILARITY_THRESHOLD