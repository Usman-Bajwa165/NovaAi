"""Test script for enhanced voice engine with VAD and interruption handling."""

import time
from src.voice_engine import listen, speak, interrupt_speech, is_speaking

def test_vad_listening():
    """Test the VAD-enabled listening."""
    print("=== Testing VAD Listening ===")
    print("Speak something and pause for 1.5 seconds to test...")
    
    result = listen()
    if result:
        print(f"✅ Successfully recognized: {result}")
        return True
    else:
        print("❌ No speech detected")
        return False

def test_interruption():
    """Test speech interruption."""
    print("\n=== Testing Speech Interruption ===")
    print("Will start speaking, then interrupt after 2 seconds...")
    
    # Start speaking in a thread
    import threading
    speech_thread = threading.Thread(
        target=speak, 
        args=("This is a test speech that should be interrupted after about two seconds of talking to demonstrate the interruption functionality.",)
    )
    speech_thread.start()
    
    # Wait a bit then interrupt
    time.sleep(2)
    if is_speaking():
        print("🔊 Speech detected, interrupting...")
        interrupt_speech()
        time.sleep(0.5)
        
        if not is_speaking():
            print("✅ Successfully interrupted speech")
            return True
        else:
            print("❌ Failed to interrupt speech")
            return False
    else:
        print("❌ No speech was playing")
        return False

def test_full_conversation():
    """Test a full conversation cycle."""
    print("\n=== Testing Full Conversation ===")
    print("This will test: listen -> speak -> interrupt -> listen")
    
    try:
        # Step 1: Listen
        print("Step 1: Please say something...")
        user_input = listen()
        
        if user_input:
            print(f"✅ Heard: {user_input}")
            
            # Step 2: Respond
            response = f"I heard you say: {user_input}. This response will be interrupted."
            print("Step 2: Speaking response (interrupt me after 2 seconds)...")
            
            import threading
            speech_thread = threading.Thread(target=speak, args=(response,))
            speech_thread.start()
            
            # Step 3: Wait for interruption or completion
            time.sleep(5)  # Give time for interruption
            
            if not is_speaking():
                print("✅ Speech completed or interrupted")
                
                # Step 4: Listen again
                print("Step 4: Say something else...")
                user_input2 = listen()
                
                if user_input2:
                    print(f"✅ Final input: {user_input2}")
                    return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error in full conversation test: {e}")
        return False

if __name__ == "__main__":
    print("🎤 Testing Enhanced Voice Engine")
    print("=" * 50)
    
    tests = [
        ("VAD Listening", test_vad_listening),
        ("Speech Interruption", test_interruption),
        ("Full Conversation", test_full_conversation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")
