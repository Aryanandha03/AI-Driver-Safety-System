import pyttsx3

# Create the text-to-speech engine
engine = pyttsx3.init()

# Message for the driver
message = "Driver, are you okay?"

# Speak the message
engine.say(message)

# Wait until speaking is finished
engine.runAndWait()