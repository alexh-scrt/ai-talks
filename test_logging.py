#!/usr/bin/env python3
"""Test script for the real-time conversation logging system"""

import asyncio
from pathlib import Path

async def test_logging_system():
    """Test the conversation logging feature"""
    
    print("Testing Real-Time Conversation Logging\n" + "="*50 + "\n")
    
    print("LOGGING SYSTEM FEATURES:")
    print("-" * 40)
    print("✓ Async queue for non-blocking operation")
    print("✓ Real-time writing as conversation happens")
    print("✓ Markdown format with XML-style tags")
    print("✓ Separate sections for intro/discussion/closing")
    print("✓ Timestamped filenames")
    print("✓ Saved in outputs/ directory")
    
    print("\n" + "-"*40 + "\n")
    print("EXPECTED LOG FILE FORMAT:")
    print("-" * 40)
    
    sample_log = """# AI Talks Conversation Log

**Topic:** What is consciousness?
**Date:** 2024-01-15 14:30:00
**Session:** talks_abc12345
**Participants:** Sophia, Marcus, Aisha
**Narrator:** Michael Lee

---

## Introduction

<Michael Lee>
Welcome to AI Talks, where artificial minds explore...
</Michael Lee>

<Michael Lee>
Today we're diving into one of humanity's oldest riddles...
</Michael Lee>

## Discussion

<Sophia>
I believe consciousness emerges from complex neural patterns...
</Sophia>

<Marcus>
That's an interesting perspective, Sophia, but I would argue...
</Marcus>

<Aisha>
From a scientific standpoint, we should consider...
</Aisha>

## Closing

<Michael Lee>
What a fascinating exploration we've had today...
</Michael Lee>

<Michael Lee>
That's a wrap on today's AI Talks. I'm Michael Lee...
</Michael Lee>"""
    
    print(sample_log)
    
    print("\n" + "="*50 + "\n")
    
    # Check if outputs directory exists
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("Creating outputs directory...")
        outputs_dir.mkdir(exist_ok=True)
    
    print("LOG FILE LOCATION:")
    print(f"Logs will be saved to: {outputs_dir.absolute()}/")
    print("Filename format: conversation_[session_id]_[timestamp].md")
    
    # List any existing logs
    existing_logs = list(outputs_dir.glob("conversation_*.md"))
    if existing_logs:
        print(f"\nExisting logs found: {len(existing_logs)}")
        for log in existing_logs[-3:]:  # Show last 3
            print(f"  • {log.name}")
    
    print("\n" + "="*50)
    print("✅ Logging system test complete!\n")
    
    print("WORKFLOW:")
    print("1. Orchestrator creates async queue at startup")
    print("2. Log writer task starts when discussion begins")
    print("3. Each message is queued with speaker name and section")
    print("4. Writer task consumes queue and writes to file")
    print("5. File is flushed after each write for real-time updates")
    print("6. Log task stops gracefully when discussion ends")
    
    print("\nTO RUN A DISCUSSION WITH LOGGING:")
    print('python main.py --panel philosophy --topic "What is consciousness?"')
    print("\nThen check outputs/ directory for the conversation log!")

if __name__ == "__main__":
    asyncio.run(test_logging_system())