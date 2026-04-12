import os
from faster_whisper import WhisperModel
import speech_recognition as sr

class VoiceInterface:
    def __init__(self, model_size="base.en"):
        print(f"[Sensory] Initializing {model_size} Whisper model on RTX 5060 Ti...")
        # Running on CUDA with float16 to minimize latency and VRAM
        self.model = WhisperModel(model_size, device="cuda", compute_type="float16", local_files_only=True)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen_for_command(self):
        """Captures audio and returns localized transcription."""
        with self.microphone as source:
            print("\n[LISTENING] MWO, standing by for orders...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            # Save temporary audio for Whisper to process
            with open("temp_cmd.wav", "wb") as f:
                f.write(audio.get_wav_data())

            segments, _ = self.model.transcribe("temp_cmd.wav", beam_size=5)
            text = "".join([segment.text for segment in segments]).strip()
            
            os.remove("temp_cmd.wav")
            
            # --- WAKE WORD STRATEGY ---
            wake_word = "xo"
            # Removing punctuation if present right after wake word (e.g. "XO, buy NVDA")
            clean_text = text.lower().replace(",", "").replace(".", "")
            if clean_text.startswith(wake_word):
                print(f"[Sensory] Wake word acknowledged.")
                # Return the command without the wake word
                return text[len(wake_word):].strip(" ,.")
            else:
                print(f"[Sensory] Ignored background chatter. (Wake word '{wake_word.upper()}' missing)")
                return None
        except Exception as e:
            print(f"[Error] Sensory Failure: {e}")
            return None
