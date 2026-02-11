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


def speak(text):
    """Reliable TTS using edge-tts. Non-crashing and cleans temp files."""
    try:
        print(f">>> JARVIS: {text}")
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
                    # If pygame fails to initialize, just print error and return
                    print("pygame init failed for TTS playback.")
                    return

            try:
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.music.unload()
            except Exception as e:
                print(f"TTS playback error: {e}")
    except subprocess.CalledProcessError as e:
        print(f"TTS generation error: {e}")
    except Exception as e:
        print(f"TTS Error: {e}")
    finally:
        # Ensure cleanup of temp file
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception:
            pass


def listen():
    """Deterministic listening with ambient calibration and robust error handling."""
    config = load_dna_config()

    if "device_index" not in config:
        return scan_for_neural_links()

    recognizer = sr.Recognizer()
    dev_idx = int(config.get("device_index"))
    rate = config.get("sample_rate", 16000)

    try:
        with sr.Microphone(device_index=dev_idx, sample_rate=rate) as source:
            # Calibrate to ambient noise right before listening:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.6
            recognizer.non_speaking_duration = 0.3

            print(f">>> (DNA) 🎤 Listening on Index {dev_idx} (calibrated)")
            try:
                audio = recognizer.listen(source, timeout=12, phrase_time_limit=20)
                try:
                    query = recognizer.recognize_google(audio)
                    print(f">>> USER: {query}")
                    return query
                except sr.UnknownValueError:
                    print(">>> (DNA) Sound detected but no speech recognized.")
                    return None
                except sr.RequestError as e:
                    print(f">>> (DNA) STT request error: {e}")
                    return None
            except sr.WaitTimeoutError:
                print(">>> (DNA) Timeout - no speech detected.")
                return None
    except (OSError, IOError) as e:
        print(f">>> (DNA) Hardware Link Dropped on {dev_idx}: {e}")
        # remove config and rescan once
        try:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
        except Exception:
            pass
        return scan_for_neural_links()


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
    """Placeholder for microphone diagnostic test."""
    pass
