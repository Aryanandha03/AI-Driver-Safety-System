# models/result.py

import time


def create_result(
    ear_data,
    yawn_data,
    pose_data,
    distraction_data,
    drowsiness_data
):

    return {

        "timestamp": time.time(),

        "eyes": {

            "ear": round(
                ear_data["ear"],
                3
            ),

            "closed":
                ear_data["eyes_closed"],

            "blink_count":
                ear_data["blink_count"],

            "blink_duration":
                round(
                    ear_data["blink_duration"],
                    2
                ),

            "prolonged_closure":
                ear_data["prolonged_closure"]
        },

        "mouth": {

            "mar": round(
                yawn_data["mar"],
                3
            ),

            "yawning":
                yawn_data["yawning"],

            "yawn_count":
                yawn_data["yawn_count"]
        },

        "head_pose": {

            "yaw":
                round(
                    pose_data["yaw"],
                    2
                ),

            "pitch":
                round(
                    pose_data["pitch"],
                    2
                ),

            "roll":
                round(
                    pose_data["roll"],
                    2
                )
        },

        "distraction": {

            "looking_away":
                distraction_data["looking_away"],

            "level":
                distraction_data["level"]
        },

        "drowsiness": {

            "score":
                drowsiness_data["score"],

            "level":
                drowsiness_data["level"]
        }
    }