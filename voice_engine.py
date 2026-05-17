import threading
import sounddevice as sd
import subprocess
from kokoro import KPipeline

try:
    # Hardcode repo_id to silence warnings
    pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M') 
except Exception as e:
    print(f"[VOICE ENGINE INIT ERROR]: {e}")
    pipeline = None

def _play_audio(text):
    try:
        if pipeline is None:
            raise Exception("Pipeline not initialized")
            
        generator = pipeline(text, voice='af_heart', speed=1.0, split_pattern=r'\n+')
        
        for i, (gs, ps, audio) in enumerate(generator):
            sd.play(audio, samplerate=24000)
            sd.wait()
    except Exception as e:
        print(f"[KOKORO FALLBACK TRIGGERED]: VRAM/Initialization Error - {e}")
        # Native Windows SAPI Fallback via PowerShell
        # Escape single quotes in text for powershell
        safe_text = text.replace("'", "''")
        ps_command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_text}')"
        subprocess.run(["powershell", "-Command", ps_command], shell=True)

def speak(text):
    t = threading.Thread(target=_play_audio, args=(text,), daemon=True)
    t.start()

if __name__ == "__main__":
    speak("Hello, this is Jenny. The vocal framework is active.")
    import time
    time.sleep(4)
