import speech_recognition as sr
import subprocess
import time

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("[SYSTEM] Calibrating microphone for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("[SYSTEM] Calibration complete. Listening for wake word: 'good morning jenny'")

    while True:
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            command = recognizer.recognize_google(audio).lower()
            print(f"[HEARD]: {command}")

            if "good morning jenny" in command:
                print("\n[WAKE WORD DETECTED] Ignition sequence started. Spawning Web Command Console...")
                
                # Spawn headless streamlit
                ps_streamlit = 'Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoExit -Command streamlit run c:\\Users\\Pierre\\.openclaw\\workspace\\pierre-quant\\portfolio_dashboard.py --server.headless true"'
                subprocess.Popen(["powershell", "-Command", ps_streamlit], shell=True)
                
                print("[SYSTEM] Streamlit Server booting. Opening browser...")
                time.sleep(3) # Wait for Streamlit server to bind port
                
                # Open browser maximized
                ps_browser = 'Start-Process "http://localhost:8501" -WindowStyle Maximized'
                subprocess.Popen(["powershell", "-Command", ps_browser], shell=True)
                
                print("[SYSTEM] Console mapped. Background listener sleeping for 15 seconds to avoid double-triggers...")
                time.sleep(15)

        except sr.WaitTimeoutError:
            pass 
        except sr.UnknownValueError:
            pass 
        except sr.RequestError as e:
            print(f"[ERROR] Service unavailable: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Loop error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    print("--- PIERRE-QUANT VOICE IGNITION LAYER ---")
    listen_for_wake_word()
