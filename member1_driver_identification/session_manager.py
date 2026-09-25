from datetime import datetime


class SessionManager:

    def __init__(self):
        self.session_counter = 0
        self.active_session = None

    def create_session(
        self,
        driver_id,
        driver_name,
        vehicle_id
    ):

        self.session_counter += 1

        session_id = f"S{self.session_counter:03d}"

        self.active_session = {
            "session_id": session_id,
            "driver_id": driver_id,
            "driver_name": driver_name,
            "vehicle_id": vehicle_id,
            "status": "ACTIVE",
            "start_time": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        return self.active_session

    def end_session(self):

        if self.active_session is None:
            return None

        self.active_session["status"] = "ENDED"

        self.active_session["end_time"] = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        ended_session = self.active_session

        self.active_session = None

        return ended_session

    def get_active_session(self):
        return self.active_session