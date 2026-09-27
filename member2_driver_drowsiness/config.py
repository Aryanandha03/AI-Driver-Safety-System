# config.py

# --------------------------------------------------
# Camera
# --------------------------------------------------

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720


# --------------------------------------------------
# Eye / EAR
# --------------------------------------------------

# Initial EAR threshold.
# You will probably need to tune this for your camera.
EAR_THRESHOLD = 0.21

# How long eyes must remain closed before
# considering it prolonged eye closure.
EYE_CLOSED_DURATION = 1.5


# --------------------------------------------------
# Blink
# --------------------------------------------------

# Minimum duration of a closed-eye event
# to count as a blink.
MIN_BLINK_DURATION = 0.08

# Maximum duration considered a normal blink.
MAX_BLINK_DURATION = 0.6


# --------------------------------------------------
# Mouth / MAR
# --------------------------------------------------

# Initial yawn threshold.
MAR_THRESHOLD = 0.60

# Minimum time mouth must remain open
# before considering it a yawn.
YAWN_DURATION = 0.8


# --------------------------------------------------
# Head pose
# --------------------------------------------------

# Looking-away thresholds in degrees.
YAW_THRESHOLD = 25.0
PITCH_THRESHOLD = 20.0

# How long driver needs to look away
# before distraction is considered significant.
LOOK_AWAY_DURATION = 1.5


# --------------------------------------------------
# Drowsiness score
# --------------------------------------------------

DROWSINESS_MEDIUM_SCORE = 30
DROWSINESS_HIGH_SCORE = 60


# --------------------------------------------------
# Distraction score
# --------------------------------------------------

DISTRACTION_MEDIUM_SCORE = 30
DISTRACTION_HIGH_SCORE = 60