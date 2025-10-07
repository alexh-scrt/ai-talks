#!/usr/bin/env python3
"""Test script to showcase the different panel configurations"""

import yaml
from pathlib import Path

def test_panels():
    """Test and display all panel configurations"""
    
    print("AI Talks Panel Configurations\n" + "="*50 + "\n")
    
    panels_dir = Path(__file__).parent / "src" / "config" / "panels"
    panel_files = sorted(panels_dir.glob("*.yml"))
    
    for panel_file in panel_files:
        panel_name = panel_file.stem
        
        with open(panel_file) as f:
            data = yaml.safe_load(f)
        
        print(f"\n📚 {data['panel_name'].upper()}")
        print("-" * 40)
        print(f"File: --panel {panel_name}")
        print(f"Description: {data['description']}")
        print(f"\nParticipants ({len(data['participants'])}):")
        
        for p in data['participants']:
            print(f"  • {p['name']} ({p['gender']}): {p['personality']} - {p['expertise']}")
        
        print(f"\nRecommended Topics:")
        for topic in data['recommended_topics'][:3]:
            print(f"  - {topic}")
        print(f"  ... and {len(data['recommended_topics']) - 3} more")
    
    print("\n" + "="*50)
    print("\n🎯 HOW TO USE PANELS:")
    print("-" * 40)
    print("1. Philosophy Panel:")
    print('   python main.py --panel philosophy --topic "What is consciousness?"')
    print("\n2. Technology Panel:")
    print('   python main.py --panel technology --topic "Is privacy dead?"')
    print("\n3. Popular Science Panel:")
    print('   python main.py --panel popular_science --topic "Are we alone?"')
    print("\n4. Science Panel:")
    print('   python main.py --panel science --topic "What is reality?"')
    print("\n5. General Panel:")
    print('   python main.py --panel general --topic "What is the meaning of life?"')
    print("\n6. AI Panel:")
    print('   python main.py --panel ai --topic "Can machines think?"')
    
    print("\n" + "="*50)
    print("✅ Panel configurations test complete!")
    print("\nEach panel provides:")
    print("• Expert participants with relevant backgrounds")
    print("• Tailored personalities for engaging discussions")
    print("• Recommended topics for that domain")
    print("• Easy selection via --panel flag")

if __name__ == "__main__":
    test_panels()