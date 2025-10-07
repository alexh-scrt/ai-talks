#!/usr/bin/env python3
"""Check if recent logs have cleanup applied"""

import re
from pathlib import Path

def check_logs():
    """Check recent logs for redundant speaker prefixes"""
    
    outputs_dir = Path("outputs")
    
    # Get most recent conversation logs
    logs = sorted(outputs_dir.glob("conversation_talks_*.md"), key=lambda f: f.stat().st_mtime)
    
    print("Checking Recent Logs for Redundant Speaker Prefixes")
    print("=" * 60)
    
    # Check last 3 logs
    for log_file in logs[-3:]:
        print(f"\nChecking: {log_file.name}")
        print(f"Modified: {log_file.stat().st_mtime}")
        print("-" * 40)
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Look for pattern: <Name>\nName: 
        pattern = r'<([A-Za-z-]+)>\n\1:'
        matches = re.findall(pattern, content)
        
        if matches:
            print(f"❌ Found {len(matches)} redundant prefixes for: {', '.join(set(matches))}")
            
            # Show first example
            first_match = re.search(pattern, content)
            if first_match:
                start = max(0, first_match.start() - 20)
                end = min(len(content), first_match.end() + 100)
                snippet = content[start:end].replace('\n', '\\n')
                print(f"Example: ...{snippet}...")
        else:
            print("✅ No redundant prefixes found")
    
    print("\n" + "=" * 60)
    print("\nConclusion:")
    print("If redundant prefixes are found, the cleanup might not be applied")
    print("or the LLM is generating them in a different format.")


if __name__ == "__main__":
    check_logs()