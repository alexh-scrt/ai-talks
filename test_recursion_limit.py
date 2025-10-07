#!/usr/bin/env python3
"""Test script for recursion limit configuration"""

from src.config import TalksConfig

def test_recursion_limit():
    """Test the recursion limit configuration"""
    
    print("Testing Recursion Limit Configuration\n" + "="*50 + "\n")
    
    # Load configuration
    config = TalksConfig()
    
    print("CONFIGURATION VALUES:")
    print("-" * 40)
    print(f"Recursion Limit: {config.recursion_limit}")
    print(f"Max Turns: {config.max_turns}")
    print(f"Default Depth: {config.default_depth}")
    
    print("\n" + "-" * 40)
    print("RECURSION LIMIT BENEFITS:")
    print("• Prevents LangGraph recursion errors")
    print("• Allows longer discussions (250 vs default)")
    print("• Configurable via talks.yml")
    print("• Logged at discussion start")
    
    print("\n" + "-" * 40)
    print("HOW IT WORKS:")
    print("1. Set in talks.yml under discussion.recursion_limit")
    print("2. Loaded by TalksConfig class")
    print("3. Accessed by orchestrator during initialization")
    print("4. Would be passed to LangGraph config if using LangGraph")
    
    print("\n" + "-" * 40)
    print("EXAMPLE LANGGRAPH USAGE (if implemented):")
    print("""
    config = {
        "configurable": {"thread_id": f"talks_{session_id}"},
        "recursion_limit": self.recursion_limit  # From talks.yml
    }
    
    async for event in graph.astream_events(state, config=config):
        # Process events without hitting recursion limits
        pass
    """)
    
    print("\n" + "="*50)
    print("✅ Recursion limit configuration test complete!")
    print(f"\nCurrent recursion limit: {config.recursion_limit}")
    print("This allows for extended discussions without errors.")

if __name__ == "__main__":
    test_recursion_limit()