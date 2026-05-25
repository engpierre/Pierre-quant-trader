import speech_recognition as sr
r = sr.Recognizer()
print("=== FORCED 3-SECOND MIC TEST ===")
with sr.Microphone(device_index=1, sample_rate=44100) as source:
    print("Recording started! Speak NOW for 3 seconds...")
    audio = r.record(source, duration=3) 
    print("Recording finished. Processing...")
    try:
        print(f"SUCCESS! Heard: '{r.recognize_google(audio)}'")
    except Exception as e:
        print(f"FAILED: {str(e)}")
    print("=== TEST COMPLETE ===")
