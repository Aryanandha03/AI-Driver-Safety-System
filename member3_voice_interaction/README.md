# AI Driver Safety System - Member 3

## Voice Interaction & Driver Response Verification

This module is part of an AI-based Driver Safety and Emergency Response System.

The responsibility of Member 3 is to handle voice interaction with the driver and verify the driver's response during an unsafe driving condition.

---

## Module Responsibility

The Member 3 module performs:

- Voice warning
- Driver status questioning
- Driver response verification
- Normal response detection
- Abnormal response detection
- Unclear response handling
- No-response detection
- Retry mechanism
- Emergency event generation
- Driver ID and Session ID handling

---

## Workflow

```text
Unsafe Condition
       |
       v
Voice Warning
       |
       v
"Driver, are you okay?"
       |
       v
Driver Response
       |
       v
Response Verification
       |
   +---+---+---+
   |   |   |   |
   v   v   v   v
NORMAL ABNORMAL UNCLEAR NO_RESPONSE
   |       |       |       |
   v       v       v       v
Continue Emergency Retry   Retry
Monitoring                 |
              |            v
              |         Verify
              |            |
              v            v
           Emergency    Emergency


---

## Response Categories

Status	Meaning	Action

NORMAL	Driver indicates they are okay	Continue monitoring
ABNORMAL	Driver indicates they need assistance	Trigger emergency event
UNCLEAR	Response cannot be verified	Retry, then trigger emergency if still unclear
NO_RESPONSE	Driver does not respond	Retry, then trigger emergency



---

## Retry Mechanism

The system allows a maximum of two attempts.

Attempt 1

The system asks:

Driver, are you okay?

If the response is unclear or there is no response, the system asks again.

Attempt 2

If the second response is:

NORMAL → Continue monitoring

ABNORMAL → Trigger emergency

UNCLEAR → Trigger emergency

NO_RESPONSE → Trigger emergency



---

## Current Input Method

The main voice interaction module currently uses keyboard input as a temporary replacement for live speech input.

This allows the response verification and emergency logic to be developed and tested independently of speech recognition.

The microphone has also been tested separately using speech_test.py and test.py.


---

## Emergency Event

When an emergency condition is detected, the module creates a structured event containing:

Driver ID
Session ID
Emergency Trigger
Reason
Response Status
Timestamp

Example:

{
    "driver_id": "D001",
    "session_id": "S001",
    "emergency_trigger": true,
    "reason": "Driver reported an abnormal condition",
    "response_status": "ABNORMAL",
    "timestamp": "YYYY-MM-DD HH:MM:SS"
}

This event can later be passed to the Emergency Response module and the overall system integration module.


---

## Project Files

DriverSafety_Member3/
│
├── .gitignore
├── emergency_trigger.py
├── README.md
├── requirements.txt
├── response_verification.py
├── speech_test.py
├── test.py
├── voice_interaction.py
└── voice_test.py


---

## File Description

voice_interaction.py

Main Member 3 module.

Handles:

Voice warnings

Driver questioning

Response collection

Retry mechanism

Response verification

Emergency triggering


response_verification.py

Classifies driver responses into:

NORMAL
ABNORMAL
UNCLEAR
NO_RESPONSE

emergency_trigger.py

Creates a structured emergency event containing driver/session information, reason, response status, and timestamp.

voice_test.py

Tests the text-to-speech functionality using pyttsx3.

speech_test.py

Tests microphone recording using SpeechRecognition and PyAudio.

test.py

Lists available microphones and allows a microphone index to be selected for recording tests.


---

## Technologies Used

Python

pyttsx3

SpeechRecognition

PyAudio

msvcrt

datetime



---

## Requirements

Install the required Python packages using:

pip install -r requirements.txt


---

## Testing

The Member 3 response verification module has been tested with the following cases:

Test Case	Input	Result

Normal Response	yes	NORMAL
Abnormal Response	no	ABNORMAL
No Response	Blank input	NO_RESPONSE
Unclear Response	hello	UNCLEAR


The text-to-speech system was also tested successfully.

The microphone recording test was successfully completed and produced a test WAV recording.


---

## Integration

The Member 3 module is designed to work with the other project modules.

Input

The module receives an unsafe-condition event from the driver monitoring system.

Output

The module produces a structured result containing:

driver_id
session_id
emergency_trigger
reason
response_status
timestamp

This output can be used by:

Member 4 for emergency response handling

Member 5 for database, dashboard, GPS, and overall system integration



---

## Future Improvement

The current keyboard-based response input can be replaced with real-time speech recognition.

The existing response verification and emergency logic can remain unchanged when live speech recognition is integrated.


---

## Member 3 Responsibility

Module: Voice Interaction & Driver Response Verification

Member: Member 3

Main Responsibilities:

Driver voice interaction

Response classification

Retry handling

Emergency event generation

Module testing

Integration-ready output