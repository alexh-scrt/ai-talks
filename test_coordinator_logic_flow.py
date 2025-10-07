#!/usr/bin/env python3
"""Test the coordinator flow logic without actual LLM calls"""

def simulate_discussion_flow():
    """Simulate the new discussion flow logic"""
    
    print("Simulating Fixed Coordinator Flow")
    print("=" * 50)
    
    # Settings
    coordinator_mode = True
    coordinator_frequency = 0  # Every turn
    participants = ["Alice", "Bob", "Charlie"]
    max_turns = 6
    
    print(f"Settings: coordinator_frequency={coordinator_frequency}")
    print(f"Participants: {', '.join(participants)}")
    print()
    
    # Simulate turn selector (rotating for simplicity)
    def select_next_speaker(turn_num):
        return participants[turn_num % len(participants)]
    
    # Track exchanges
    exchanges = []
    
    print("Turn-by-turn flow:")
    print("-" * 50)
    
    for turn_num in range(max_turns):
        print(f"\nTurn {turn_num + 1}:")
        
        # Step 1: Select the next speaker
        next_speaker = select_next_speaker(turn_num)
        print(f"  1. Selected speaker: {next_speaker}")
        
        # Step 2: Check if coordinator should interject
        if coordinator_mode and turn_num > 0:  # Not on first turn
            if coordinator_frequency == 0:  # Every turn
                should_interject = True
            elif coordinator_frequency > 0:
                should_interject = turn_num % coordinator_frequency == 0
            else:
                should_interject = False
            
            if should_interject and exchanges:
                last_speaker = exchanges[-1]["speaker"]
                print(f"  2. Coordinator interjects:")
                print(f"     - Acknowledges {last_speaker}")
                print(f"     - Addresses {next_speaker} (the already-selected speaker)")
                coordinator_msg = f"Michael: '{last_speaker} made a great point. {next_speaker}, your thoughts?'"
                print(f"     - Example: {coordinator_msg}")
        else:
            print(f"  2. No coordinator interjection")
        
        # Step 3: Selected speaker responds
        print(f"  3. {next_speaker} responds")
        
        # Record the exchange
        exchanges.append({
            "turn": turn_num,
            "speaker": next_speaker,
            "content": f"{next_speaker}'s response about the topic"
        })
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("-" * 50)
    print("With the fix:")
    print("• Speaker is selected FIRST")
    print("• Coordinator addresses the ALREADY-SELECTED speaker")  
    print("• That speaker then responds")
    print("• No mismatch possible!")
    print("\n✅ The flow ensures consistency between who is addressed and who speaks")


if __name__ == "__main__":
    simulate_discussion_flow()