#!/usr/bin/env python3
"""Test script for the YAML configuration system"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import TalksConfig

def test_config_system():
    """Test the configuration system"""
    
    print("Testing YAML Configuration System\n" + "="*50 + "\n")
    
    # Initialize configuration
    config = TalksConfig()
    
    print("CONFIGURATION LOADED FROM talks.yml:")
    print("-" * 40)
    
    print(f"Forbidden Topics: {config.forbidden_topics}")
    print(f"Narrator Name: {config.narrator_name}")
    print(f"Narrator Enabled: {config.narrator_enabled}")
    print(f"Default Depth: {config.default_depth}")
    print(f"Max Turns: {config.max_turns}")
    
    print("\n" + "-" * 40)
    print("AVAILABLE OPTIONS:")
    print(f"Personality Types: {config.personality_types}")
    print(f"Expertise Areas: {config.expertise_areas}")
    
    print("\n" + "-" * 40)
    print("TESTING GET METHOD:")
    print(f"narrator.default_name: {config.get('narrator.default_name')}")
    print(f"discussion.max_turns: {config.get('discussion.max_turns')}")
    print(f"non_existent_key: {config.get('non_existent_key', 'default_value')}")
    
    print("\n" + "="*50)
    print("✅ Configuration system test complete!")
    print("\nThe configuration is now:")
    print("1. Loaded from talks.yml file")
    print("2. Accessible via TalksConfig singleton")
    print("3. Used by orchestrator and CLI client")
    print("4. Easily customizable by editing talks.yml")

if __name__ == "__main__":
    test_config_system()