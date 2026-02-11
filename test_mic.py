"""
Quick test script to verify microphone detection after fixes.
Run this to see which microphone index will be used.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice_engine import diagnostic_mic_test, scan_for_neural_links

if __name__ == "__main__":
    print("=" * 60)
    print("NOVA MICROPHONE DIAGNOSTIC TEST")
    print("=" * 60)

    # Run diagnostic
    diagnostic_mic_test()

    print("\n" + "=" * 60)
    print("TESTING MICROPHONE SCAN")
    print("=" * 60)

    # Test the scan
    result = scan_for_neural_links()

    if result:
        print(f"\n✅ SUCCESS: Microphone scan completed!")
        print("Your microphone is ready for use.")
    else:
        print(f"\n❌ ERROR: Microphone scan failed!")
        print("Please check your microphone connection.")

    print("=" * 60)
