"""Voice engine module for speech recognition and synthesis."""

import os
import json
import time
import subprocess
from threading import Lock
import speech_recognition as sr
import pygame
import pyaudio

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.json")
_TTS_LOCK = Lock()
_IS_SPEAKING = False


def _play_beep():
    """Play a short beep sound to indicate listening started."""
    try:
        import winsound
        winsound.Beep(800, 150)  # 800Hz for 150ms
    except Exception:
        pass  # Silently fail if beep doesn't work


def load_dna_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
    return {}


def save_dna_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f)


def speak(text, word_callback=None):
    """Text-to-speech with word streaming callback."""
    global _IS_SPEAKING
    temp_file = f"tts_{int(time.time() * 1000)}.mp3"
    
    try:
        print(f">>> NOVA: {text}")
        
        with _TTS_LOCK:
            subprocess.run(
                ["edge-tts", "--voice", "en-US-GuyNeural", "--text", text, "--write-media", temp_file],
                capture_output=True,
                check=True,
            )

            if not pygame.mixer.get_init():
                pygame.mixer.init()

            _IS_SPEAKING = True
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()

            if word_callback:
                words = text.split()
                for i, word in enumerate(words):
                    word_callback(word, i, len(words))
                    time.sleep(0.15)

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            
    except Exception as e:
        print(f"TTS Error: {e}")
    finally:
        _IS_SPEAKING = False
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass


def listen_for_wake_word():
    """Listen continuously for wake word 'Nova'."""
    config = load_dna_config()

    if "device_index" not in config:
        if scan_for_neural_links() != "READY_STATUS":
            return False
        config = load_dna_config()

    recognizer = sr.Recognizer()
    dev_idx = int(config.get("device_index"))
    rate = config.get("sample_rate", 16000)

    if config.get("threshold"):
        recognizer.energy_threshold = float(config["threshold"])
        recognizer.dynamic_energy_threshold = False

    try:
        with sr.Microphone(device_index=dev_idx, sample_rate=rate) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.05)
            recognizer.pause_threshold = 1.0
            recognizer.dynamic_energy_threshold = True

            print(">>> 👂 Listening for wake word 'Nova'...")
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
            text = recognizer.recognize_google(audio, language="en-US").lower()
            
            if "nova" in text:
                print(">>> Wake word detected!")
                _play_beep()  # Play beep when wake word detected
                return True
            return False
            
    except (sr.UnknownValueError, sr.WaitTimeoutError):
        return False
    except (OSError, IOError) as e:
        print(f">>> Mic error: {e}")
        return False


def listen(skip_wake_word=False):
    """Capture voice input and convert to text."""
    if not skip_wake_word:
        # Wait for wake word first
        if not listen_for_wake_word():
            return None
    
    config = load_dna_config()

    if "device_index" not in config:
        if scan_for_neural_links() != "READY_STATUS":
            return None
        config = load_dna_config()

    recognizer = sr.Recognizer()
    dev_idx = int(config.get("device_index"))
    rate = config.get("sample_rate", 16000)

    if config.get("threshold"):
        recognizer.energy_threshold = float(config["threshold"])
        recognizer.dynamic_energy_threshold = False

    try:
        with sr.Microphone(device_index=dev_idx, sample_rate=rate) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.05)
            recognizer.pause_threshold = 2.0
            recognizer.dynamic_energy_threshold = True

            print(f">>> 🎤 Listening on device {dev_idx}...")
            _play_beep()  # Play beep when starting to listen
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=12)
            query = recognizer.recognize_google(audio, language="en-US")
            print(f">>> USER: {query}")
            return query
            
    except sr.UnknownValueError:
        print(">>> No speech detected.")
        return None
    except sr.WaitTimeoutError:
        print(">>> Listening timeout.")
        return None
    except (OSError, IOError) as e:
        print(f">>> Mic error: {e}")
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        scan_for_neural_links()
        return None


def scan_for_neural_links():
    """Auto-detect and configure best microphone."""
    print(">>> Scanning audio devices...")
    speak("Calibrating microphone. Please remain silent.")

    recognizer = sr.Recognizer()
    priority_indices = []
    secondary_indices = []

    try:
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            name = info.get("name", "").lower()
            channels = info.get("maxInputChannels", 0)

            if channels > 0:
                if "microphone array" in name or "conexant" in name:
                    priority_indices.append(i)
                elif "sound mapper" in name or "primary" in name:
                    secondary_indices.append(i)
                else:
                    priority_indices.append(i)
        p.terminate()
    except Exception as e:
        print(f"Device search error: {e}")
        priority_indices = [1, 5, 11]
        secondary_indices = [0]

    test_queue = priority_indices + secondary_indices
    best_idx = None
    best_rate = 16000

    for idx in test_queue:
        for rate in (16000, 44100):
            try:
                with sr.Microphone(device_index=idx, sample_rate=rate) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1.5)
                    et = recognizer.energy_threshold
                    if 35 < et < 2000:
                        best_idx = idx
                        best_rate = rate
                        print(f">>> Device {idx} validated (threshold: {int(et)})")
                        break
            except (OSError, IOError):
                continue
        if best_idx is not None:
            break

    if best_idx is not None:
        final_threshold = min(int(recognizer.energy_threshold) + 100, 400)
        save_dna_config({"device_index": best_idx, "sample_rate": best_rate, "threshold": final_threshold})
        speak("Microphone configured successfully.")
        return "READY_STATUS"

    speak("No microphone detected.")
    return None
