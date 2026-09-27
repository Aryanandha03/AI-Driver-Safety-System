import speech_recognition as sr

for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(i, name)

index = int(input("\nEnter your microphone index: "))

recognizer = sr.Recognizer()

with sr.Microphone(device_index=index) as source:
    print("\nSpeak now...")
    audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

print("Captured audio!")

with open("mic_test.wav", "wb") as f:
    f.write(audio.get_wav_data())

print("Saved mic_test.wav")