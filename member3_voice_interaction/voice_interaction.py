import pyttsx3
import msvcrt
import time

from response_verification import verify_response
from emergency_trigger import trigger_emergency


# --------------------------------------------------
# DRIVER / SESSION INFORMATION
# --------------------------------------------------

DRIVER_ID = "D001"
SESSION_ID = "S001"


# --------------------------------------------------
# TEXT-TO-SPEECH
# --------------------------------------------------

engine = pyttsx3.init()


def speak(message):
    """
    Make the computer speak the message.

    If TTS is not working, the message is still
    displayed in the terminal.
    """

    print("SYSTEM:", message)

    try:
        engine.say(message)
        engine.runAndWait()
    except Exception as error:
        print("TTS Warning:", error)


# --------------------------------------------------
# TEMPORARY KEYBOARD INPUT
# --------------------------------------------------

def get_response_with_timeout(timeout=5):
    """
    Temporary replacement for microphone input.

    The driver can type a response within the
    specified number of seconds.

    Later this function can be replaced with
    Speech Recognition without changing the
    response verification system.
    """

    print(
        f"Driver response ({timeout} seconds): ",
        end="",
        flush=True
    )

    response = ""
    start_time = time.time()

    while time.time() - start_time < timeout:

        if msvcrt.kbhit():

            character = msvcrt.getwch()

            # Enter key
            if character in ("\r", "\n"):
                print()
                return response

            # Backspace
            elif character == "\b":

                if response:
                    response = response[:-1]
                    print("\b \b", end="", flush=True)

            # Normal character
            else:
                response += character
                print(character, end="", flush=True)

        time.sleep(0.05)

    print("\nNo response detected.")

    return ""


# --------------------------------------------------
# EMERGENCY HANDLER
# --------------------------------------------------

def handle_emergency(status):

    """
    Handle abnormal or no-response conditions.
    """

    if status == "ABNORMAL":

        speak("Driver may need assistance.")

        return trigger_emergency(
            reason="Driver reported an abnormal condition",
            response_status="ABNORMAL",
            driver_id=DRIVER_ID,
            session_id=SESSION_ID
        )

    elif status == "NO_RESPONSE":

        speak("No response detected.")

        return trigger_emergency(
            reason="Driver is unresponsive",
            response_status="NO_RESPONSE",
            driver_id=DRIVER_ID,
            session_id=SESSION_ID
        )

    return None


# --------------------------------------------------
# MAIN VOICE INTERACTION
# --------------------------------------------------

def start_voice_interaction():

    print("\n===================================")
    print(" AI DRIVER SAFETY - VOICE MODULE ")
    print("===================================")

    print("Driver ID :", DRIVER_ID)
    print("Session ID:", SESSION_ID)

    # ----------------------------------------------
    # INITIAL WARNING
    # ----------------------------------------------

    speak("Warning! Driver attention required.")

    # ----------------------------------------------
    # MAXIMUM TWO ATTEMPTS
    # ----------------------------------------------

    for attempt in range(1, 3):

        print(f"\nAttempt {attempt} of 2")

        speak("Driver, are you okay?")

        response = get_response_with_timeout(5)

        status = verify_response(response)

        print("Response Status:", status)

        # ------------------------------------------
        # NORMAL
        # ------------------------------------------

        if status == "NORMAL":

            speak(
                "Response verified. Continuing monitoring."
            )

            return {
                "driver_id": DRIVER_ID,
                "session_id": SESSION_ID,
                "emergency_trigger": False,
                "reason": "Driver response verified",
                "response_status": "NORMAL"
            }

        # ------------------------------------------
        # ABNORMAL
        # ------------------------------------------

        elif status == "ABNORMAL":

            return handle_emergency(status)

        # ------------------------------------------
        # NO RESPONSE
        # ------------------------------------------

        elif status == "NO_RESPONSE":

            if attempt == 1:

                speak(
                    "No response detected. Please respond."
                )

            else:

                return handle_emergency(status)

        # ------------------------------------------
        # UNCLEAR
        # ------------------------------------------

        elif status == "UNCLEAR":

            if attempt == 1:

                speak(
                    "Sorry, I could not understand your response."
                )

            else:

                speak(
                    "Response is still unclear."
                )

                return trigger_emergency(
                    reason="Driver response could not be verified",
                    response_status="UNCLEAR",
                    driver_id=DRIVER_ID,
                    session_id=SESSION_ID
                )

    return None


# --------------------------------------------------
# PROGRAM START
# --------------------------------------------------

if __name__ == "__main__":

    result = start_voice_interaction()

    print("\n========== M3 RESULT ==========")
    print(result)
    print("===============================\n")