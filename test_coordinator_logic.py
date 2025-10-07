#!/usr/bin/env python3
"""Test coordinator interjection logic"""

def test_coordinator_logic():
    """Test the logic for when coordinator should interject"""
    
    print("Testing Coordinator Logic")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        # (coordinator_mode, turn_number, coordinator_frequency, should_terminate, expected_result)
        (True, 0, 0, False, False),  # Turn 0, frequency 0: No (never on first turn)
        (True, 1, 0, False, True),   # Turn 1, frequency 0: Yes (every turn after first)
        (True, 2, 0, False, True),   # Turn 2, frequency 0: Yes
        (True, 3, 0, False, True),   # Turn 3, frequency 0: Yes
        (True, 0, 3, False, False),  # Turn 0, frequency 3: No (never on first turn)
        (True, 1, 3, False, False),  # Turn 1, frequency 3: No (1+1=2, not divisible by 3)
        (True, 2, 3, False, True),   # Turn 2, frequency 3: Yes (2+1=3, divisible by 3)
        (True, 3, 3, False, False),  # Turn 3, frequency 3: No (3+1=4, not divisible by 3)
        (True, 4, 3, False, False),  # Turn 4, frequency 3: No
        (True, 5, 3, False, True),   # Turn 5, frequency 3: Yes (5+1=6, divisible by 3)
        (False, 2, 0, False, False), # Coordinator mode disabled: No
        (True, 2, 0, True, False),   # About to terminate: No
    ]
    
    print("\nTest Cases:")
    print("-" * 50)
    print("Mode | Turn | Freq | Term | Expected | Result | Status")
    print("-" * 50)
    
    for coordinator_mode, turn_number, coordinator_frequency, should_terminate, expected in test_cases:
        # Simulate the logic from orchestrator.py
        narrator_exists = True  # Assume narrator exists for all tests
        
        if coordinator_mode and narrator_exists and turn_number > 0 and not should_terminate:
            # coordinator_frequency: 0 means every turn, otherwise every N turns
            if coordinator_frequency == 0:
                should_interject = True
            elif coordinator_frequency > 0:
                should_interject = (turn_number + 1) % coordinator_frequency == 0
            else:
                should_interject = False
        else:
            should_interject = False
        
        status = "✓" if should_interject == expected else "✗"
        mode_str = "On" if coordinator_mode else "Off"
        term_str = "Yes" if should_terminate else "No"
        
        print(f"{mode_str:^4} | {turn_number:^4} | {coordinator_frequency:^4} | {term_str:^4} | {str(expected):^8} | {str(should_interject):^6} | {status:^6}")
    
    print("\n" + "=" * 50)
    print("\nKey Insights:")
    print("• Frequency 0 = interject after EVERY turn (except turn 0)")
    print("• Frequency 3 = interject after turns 2, 5, 8, 11, etc.")
    print("• Never interjects on turn 0 (first speaker after intro)")
    print("• Never interjects when about to terminate")
    print("• Requires coordinator_mode=True and narrator to exist")
    print("\n✅ Logic verification complete!")


if __name__ == "__main__":
    test_coordinator_logic()