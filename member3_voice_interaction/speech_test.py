import speech_recognition as sr

recognizer = sr.Recognizer()

print("Opening microphone 1...")

try:
    with sr.Microphone(device_index=1) as source:

        print("Microphone opened successfully.")
        print("Please speak loudly for 5 seconds.")
        print("Say: YES, I AM OKAY")

        audio = recognizer.record(source, duration=10)

    print("Recording finished.")

    # Save the recorded audio as a WAV file
    with open("mic_test.wav", "wb") as file:
        file.write(audio.get_wav_data())

    print("Audio saved as mic_test.wav")
    print("Please open this file and listen to it.")

except Exception as e:
    print("Error:", e)