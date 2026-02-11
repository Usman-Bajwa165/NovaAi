"""
Raw microphone test - captures what the mic is actually hearing
This will help diagnose if your microphone is picking up noise
"""

import time
import speech_recognition as sr


def test_raw_audio():
    """Test microphone with different thresholds."""
    print("=" * 60)
    print("RAW MICROPHONE DIAGNOSTIC")
    print("=" * 60)

    recognizer = sr.Recognizer()

    # Use Index 5 (your Conexant microphone)
    mic_index = 5

    # Test different thresholds
    thresholds = [400, 800, 1200, 1600, 2000]

    for threshold in thresholds:
        print(f"\n{'=' * 60}")
        print(f"TESTING WITH THRESHOLD: {threshold}")
        print(f"{'=' * 60}")

        recognizer.energy_threshold = threshold
        recognizer.dynamic_energy_threshold = False
        recognizer.pause_threshold = 0.5

        try:
            with sr.Microphone(device_index=mic_index, sample_rate=16000) as source:
                print(f"\n🎤 LISTENING (Threshold {threshold})...")
                print("BE SILENT FOR 3 SECONDS")
                print("Then count: 1, 2, 3, 4, 5")
                print("-" * 60)

                start_time = time.time()

                try:
                    # Listen with 10 second timeout
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                    capture_time = time.time() - start_time

                    print(f"\n✅ CAPTURED audio after {capture_time:.2f} seconds")
                    print(f"   Audio length: {len(audio.frame_data)} bytes")

                    # Try to recognize
                    print("   Sending to Google Speech Recognition...")
                    try:
                        text = recognizer.recognize_google(audio)
                        print(f"   ✅ RECOGNIZED: '{text}'")
                    except sr.UnknownValueError:
                        print("   ⚠️ Could not understand audio (likely noise)")
                    except sr.RequestError as e:
                        print(f"   ❌ API Error: {e}")

                except sr.WaitTimeoutError:
                    print("\n⏱️ TIMEOUT - No audio detected in 10 seconds")
                    print("   This is GOOD if you were silent!")

        except sr.UnknownValueError as e:
            print(f"\n❌ ERROR: {e}")
        except sr.RequestError as e:
            print(f"\n❌ ERROR: {e}")

        if threshold < thresholds[-1]:
            print("\n" + "=" * 60)
            input("Press ENTER to test next threshold...")

    print("\n" * 2)
    print("=" * 60)
    print("DIAGNOSIS:")
    print("=" * 60)
    print("If audio was captured IMMEDIATELY (< 1 second) while you were SILENT:")
    print("  → Your microphone is picking up background noise")
    print("  → Possible causes:")
    print("     1. Computer fan noise")
    print("     2. JARVIS speaking through speakers (feedback loop)")
    print("     3. Keyboard/mouse sounds")
    print("     4. Room noise (AC, traffic, etc.)")
    print("     5. Microphone too sensitive (needs Windows adjustment)")
    print("\nIf audio was captured AFTER you counted (good timing):")
    print("  → Microphone works! Issue is with threshold settings")
    print("\nIf you got TIMEOUTS on all thresholds:")
    print("  → Microphone too quiet or wrong device")
    print("=" * 60)


if __name__ == "__main__":
    test_raw_audio()
