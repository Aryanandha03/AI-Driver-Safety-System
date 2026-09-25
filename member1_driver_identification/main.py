import os
import sys
import cv2
import numpy as np


# Project root path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from face_engine import FaceEngine
from driver_database import load_drivers
from session_manager import SessionManager
from config import CAMERA_INDEX, STABLE_FRAMES_REQUIRED
from shared.session_data import update_session

KNOWN_DRIVERS_PATH = os.path.join(
    os.path.dirname(__file__),
    "known_drivers"
)


def load_known_faces(face_engine, drivers):

    known_faces = {}

    print("\nLoading registered drivers...")

    for driver_id, driver_info in drivers.items():

        driver_name = driver_info["name"]

        folder_name = f"{driver_id}_{driver_name}"
        folder_path = os.path.join(
            KNOWN_DRIVERS_PATH,
            folder_name
        )

        if not os.path.exists(folder_path):
            print(f"Folder not found: {folder_path}")
            continue

        embeddings = []

        for filename in os.listdir(folder_path):

            if not filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            image_path = os.path.join(
                folder_path,
                filename
            )

            image = cv2.imread(image_path)

            if image is None:
                print(f"Could not read: {filename}")
                continue

            faces = face_engine.get_faces(image)

            if len(faces) == 0:
                print(f"No face found in: {filename}")
                continue

            face = max(
                faces,
                key=lambda f: (
                    f.bbox[2] - f.bbox[0]
                ) * (
                    f.bbox[3] - f.bbox[1]
                )
            )

            embedding = face_engine.get_embedding(face)

            embeddings.append(embedding)

            print(
                f"Loaded: {driver_id} - "
                f"{driver_name} - {filename}"
            )

        if embeddings:
            known_faces[driver_id] = {
                "name": driver_name,
                "vehicle_id": driver_info["vehicle_id"],
                "embeddings": embeddings
            }

    print("\nRegistered drivers loaded:")
    print(len(known_faces))

    return known_faces


def recognize_driver(face_engine, face, known_faces):

    current_embedding = face_engine.get_embedding(face)

    best_driver_id = "UNKNOWN"
    best_name = "UNKNOWN"
    best_vehicle_id = "UNKNOWN"
    best_similarity = -1.0

    for driver_id, driver_data in known_faces.items():

        for known_embedding in driver_data["embeddings"]:

            similarity = face_engine.compare_embeddings(
                current_embedding,
                known_embedding
            )

            if similarity > best_similarity:

                best_similarity = similarity
                best_driver_id = driver_id
                best_name = driver_data["name"]
                best_vehicle_id = driver_data["vehicle_id"]

    if not face_engine.is_match(best_similarity):

        return {
            "driver_id": "UNKNOWN",
            "driver_name": "UNKNOWN",
            "vehicle_id": "UNKNOWN",
            "similarity": best_similarity
        }

    return {
        "driver_id": best_driver_id,
        "driver_name": best_name,
        "vehicle_id": best_vehicle_id,
        "similarity": best_similarity
    }


def main():

    print("====================================")
    print(" AI DRIVER IDENTIFICATION SYSTEM")
    print("====================================")

    face_engine = FaceEngine()

    drivers = load_drivers()

    known_faces = load_known_faces(
        face_engine,
        drivers
    )

    if not known_faces:

        print("\nERROR: No registered driver faces found.")
        print("Check the known_drivers folders.")
        return

    # Session manager
    session_manager = SessionManager()

    # Stable recognition variables
    candidate_driver_id = None
    candidate_count = 0

    confirmed_driver_id = None
    confirmed_driver_name = None
    confirmed_vehicle_id = None
    confirmed_similarity = 0.0

    print("\nStarting camera...")

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")
        return

    print("Camera started.")
    print("Waiting for stable driver identification...")
    print(f"Required stable frames: {STABLE_FRAMES_REQUIRED}")
    print("Press Q to quit.")

    while True:

        success, frame = camera.read()

        if not success:

            print("ERROR: Could not read camera frame.")
            break

        faces = face_engine.get_faces(frame)

        for face in faces:

            x1, y1, x2, y2 = face.bbox.astype(int)

            result = recognize_driver(
                face_engine,
                face,
                known_faces
            )

            current_driver_id = result["driver_id"]

            # -----------------------------------
            # STABLE RECOGNITION
            # -----------------------------------

            if current_driver_id == candidate_driver_id:

                candidate_count += 1

            else:

                candidate_driver_id = current_driver_id
                candidate_count = 1

            # -----------------------------------
            # CONFIRM IDENTITY
            # -----------------------------------

            if (
                candidate_count >= STABLE_FRAMES_REQUIRED
                and confirmed_driver_id != current_driver_id
            ):

                confirmed_driver_id = current_driver_id
                confirmed_driver_name = result["driver_name"]
                confirmed_vehicle_id = result["vehicle_id"]
                confirmed_similarity = result["similarity"]

                # Create session
                session = session_manager.create_session(
                    confirmed_driver_id,
                    confirmed_driver_name,
                    confirmed_vehicle_id
                )
                update_session(
                    confirmed_driver_id,
                    confirmed_driver_name,
                    confirmed_vehicle_id,
                    session["session_id"],
                    session["status"]
                )

                print("\n====================================")
                print(" DRIVER IDENTITY CONFIRMED")
                print("====================================")

                print(
                    f"Driver ID   : {confirmed_driver_id}"
                )

                print(
                    f"Driver Name : {confirmed_driver_name}"
                )

                print(
                    f"Vehicle ID  : {confirmed_vehicle_id}"
                )

                print(
                    f"Session ID  : {session['session_id']}"
                )

                print(
                    f"Status      : {session['status']}"
                )

                print(
                    f"Start Time  : {session['start_time']}"
                )

                print("====================================\n")

            # -----------------------------------
            # DISPLAY
            # -----------------------------------

            if confirmed_driver_id is None:

                label = "IDENTIFYING..."

            elif confirmed_driver_id == "UNKNOWN":

                label = "UNKNOWN DRIVER"

            else:

                label = (
                    f"{confirmed_driver_id} - "
                    f"{confirmed_driver_name}"
                )

            # Face rectangle
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Driver label
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            # Similarity
            cv2.putText(
                frame,
                f"Similarity: {result['similarity']:.2f}",
                (x1, y2 + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2
            )

            # Stability counter
            cv2.putText(
                frame,
                f"Stable: {candidate_count}/{STABLE_FRAMES_REQUIRED}",
                (x1, y2 + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            # Session information
            active_session = session_manager.get_active_session()

            if active_session is not None:

                cv2.putText(
                    frame,
                    f"Session: {active_session['session_id']}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    "Status: ACTIVE",
                    (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        cv2.imshow(
            "Member 1 - Driver Identification",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    # -----------------------------------
    # END SESSION
    # -----------------------------------

    ended_session = session_manager.end_session()

    if ended_session:


        update_session(
        ended_session["driver_id"],
        ended_session["driver_name"],
        ended_session["vehicle_id"],
        ended_session["session_id"],
        ended_session["status"]
        )

        

        print("\n====================================")
        print(" DRIVING SESSION ENDED")
        print("====================================")

        print(
            f"Session ID  : {ended_session['session_id']}"
        )

        print(
            f"Driver ID   : {ended_session['driver_id']}"
        )

        print(
            f"Driver Name : {ended_session['driver_name']}"
        )

        print(
            f"Vehicle ID  : {ended_session['vehicle_id']}"
        )

        print(
            f"Status      : {ended_session['status']}"
        )

        print(
            f"Start Time  : {ended_session['start_time']}"
        )

        print(
            f"End Time    : {ended_session['end_time']}"
        )

        print("====================================")

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()