"""Voice engine module for speech recognition and synthesis."""

import os
import json
import time
import subprocess
import speech_recognition as sr
import pygame
from threading import Lock

# Configuration Persistence
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.json")
_TTS_LOCK = Lock()

# Track speaking state so we can support safe interruption and diagnostics
_IS_SPEAKING = False


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
    """Reliable TTS using edge-tts. Non-crashing and cleans temp files."""
    global _IS_SPEAKING
    try:
        print(f">>> NOVA: {text}")
        temp_file = f"tts_{int(time.time() * 1000)}.mp3"
        # Use lock so only one TTS subprocess plays at a time
        with _TTS_LOCK:
            subprocess.run(
                [
                    "edge-tts",
                    "--voice",
                    "en-US-GuyNeural",
                    "--text",
                    text,
                    "--write-media",
                    temp_file,
                ],
                capture_output=True,
                check=True,
            )

            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except Exception:
                    print("pygame init failed for TTS playback.")
                    return

            try:
                _IS_SPEAKING = True
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                # Stream words during playback
                if word_callback:
                    words = text.split()
                    total = len(words)
                    for i, word in enumerate(words):
                        word_callback(word, i, total)
                        time.sleep(0.15)  # Sync with speech pace
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.music.unload()
            except Exception as e:
                print(f"TTS playback error: {e}")
            finally:
                _IS_SPEAKING = False
    except subprocess.CalledProcessError as e:
        print(f"TTS generation error: {e}")
    except Exception as e:
        print(f"TTS Error: {e}")
    finally:
        _IS_SPEAKING = False
        # Ensure cleanup of temp file
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception:
            pass


def listen():
    """Listen until user finishes speaking, then return the recognized text.

    Behavior:
    - Keeps listening while the user is speaking
    - Treats ~1s of silence as the end of speech
    - Times out after several seconds of *total* silence
    """
    config = load_dna_config()

    # First-run: perform a deep scan, then immediately continue to listening
    if "device_index" not in config:
        scan_status = scan_for_neural_links()
        # If scan failed, abort cleanly
        if scan_status != "READY_STATUS":
            return None
        # Reload config written by scan_for_neural_links
        config = load_dna_config()
        if "device_index" not in config:
            return None

    recognizer = sr.Recognizer()
    dev_idx = int(config.get("device_index"))
    rate = config.get("sample_rate", 16000)

    # If we have a stored threshold from calibration, reuse it
    stored_threshold = config.get("threshold")
    if stored_threshold:
        recognizer.energy_threshold = float(stored_threshold)
        recognizer.dynamic_energy_threshold = False

    try:
        with sr.Microphone(device_index=dev_idx, sample_rate=rate) as source:
            # Very short calibration so we don't eat the user's first words
            recognizer.adjust_for_ambient_noise(source, duration=0.05)
            # Wait for a clear pause (~2 seconds) before ending speech
            recognizer.pause_threshold = 2.0
            recognizer.non_speaking_duration = 1.0
            recognizer.dynamic_energy_threshold = True
            recognizer.phrase_threshold = 0.1

            print(f">>> (DNA) 🎤 Listening on device {dev_idx} @ {rate}Hz...")
            try:
                # timeout: how long to wait for *any* speech
                # phrase_time_limit: hard cap so it doesn't listen forever
                audio = recognizer.listen(
                    source, timeout=8, phrase_time_limit=12
                )
                query = recognizer.recognize_google(audio, language="en-US")
                print(f">>> USER: {query}")
                return query
            except sr.UnknownValueError:
                print(">>> (DNA) No recognizable speech detected.")
                return None
            except sr.RequestError as e:
                print(f">>> (DNA) STT error: {e}")
                return None
            except sr.WaitTimeoutError:
                print(">>> (DNA) Listening timeout – no speech detected.")
                return None
    except (OSError, IOError) as e:
        print(f">>> (DNA) Mic error: {e}")
        # Reset config so next call will re-scan hardware
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        scan_for_neural_links()
        return None


def scan_for_neural_links():
    """Deep Hardware Scan: Prioritizes physical microphone devices."""
    print(">>> (DNA) Initiating Deep Hardware Scan...")
    speak("Synchronizing system audio. Please remain silent for neural calibration.")

    recognizer = sr.Recognizer()
    best_idx = None
    best_rate = 16000

    priority_indices = []
    secondary_indices = []

    try:
        import pyaudio

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
        print(f"DNA Device Search Error: {e}")
        priority_indices = [1, 5, 11]
        secondary_indices = [0]

    test_queue = priority_indices + secondary_indices
    print(f">>> (DNA) Testing Order: {test_queue}")

    for idx in test_queue:
        for rate in (16000, 44100):
            try:
                print(f">>> (DNA) Testing Link: [{idx}] @ {rate}Hz...")
                with sr.Microphone(device_index=idx, sample_rate=rate) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1.5)
                    # Acceptable energy threshold range
                    et = recognizer.energy_threshold
                    if 35 < et < 2000:
                        best_idx = idx
                        best_rate = rate
                        print(
                            f">>> (DNA) Link Validated: Index {idx} (Thresh: {int(et)})"
                        )
                        break
                    else:
                        print(
                            f"> (DNA) Index {idx} discarded: Unrealistic threshold ({int(et)})"
                        )
            except (OSError, IOError):
                continue
        if best_idx is not None:
            break

    if best_idx is not None:
        final_threshold = min(int(recognizer.energy_threshold) + 100, 400)
        new_config = {
            "device_index": best_idx,
            "sample_rate": best_rate,
            "threshold": final_threshold,
        }
        save_dna_config(new_config)
        speak(f"Neural link locked on Hardware Index {best_idx}. Ready.")
        return "READY_STATUS"

    speak("Hardware sync failed. No viable audio capture device detected.")
    return None


def diagnostic_mic_test():
    """Simple CLI diagnostic for microphone configuration."""
    print("=" * 60)
    print("NOVA MICROPHONE DIAGNOSTIC")
    print("=" * 60)

    config = load_dna_config()
    if config:
        print(f"Existing config: {config}")
    else:
        print("No existing mic configuration found.")

    result = scan_for_neural_links()
    if result == "READY_STATUS":
        new_config = load_dna_config()
        print(f"\n✅ Scan succeeded. Active configuration: {new_config}")
    else:
        print("\n❌ Scan failed. No suitable microphone detected.")


def is_speaking():
    """Return True if NOVA is currently speaking via TTS."""
    return _IS_SPEAKING and pygame.mixer.get_init() and pygame.mixer.music.get_busy()


def interrupt_speech():
    """Attempt to immediately stop any ongoing TTS playback."""
    global _IS_SPEAKING
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
    except Exception:
        # Best-effort interruption; avoid crashing the app
        pass
    finally:
        _IS_SPEAKING = False
