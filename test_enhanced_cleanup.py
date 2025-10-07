#!/usr/bin/env python3
"""Test enhanced content cleanup"""

import re

def _clean_content(speaker: str, content: str) -> str:
    """Remove redundant speaker name from beginning of content"""
    if not content:
        return content
    
    # Trim whitespace
    cleaned = content.strip()
    
    # Pattern 1: "Name:" at the start
    prefix = f"{speaker}:"
    if cleaned.lower().startswith(prefix.lower()):
        # Remove the prefix and any following whitespace
        cleaned = cleaned[len(prefix):].lstrip()
    
    # Pattern 2: "Name:\n" with newline
    prefix_with_newline = f"{speaker}:\n"
    if cleaned.lower().startswith(prefix_with_newline.lower()):
        cleaned = cleaned[len(prefix_with_newline):].lstrip()
    
    # Pattern 3: "**Name's Response:**" or "**Name's response:**" etc.
    # Match variations like **Cynthia's Response:**, **Bob's response:**, etc.
    response_pattern = rf"\*\*{re.escape(speaker)}'s [Rr]esponse:\*\*\s*\n?"
    cleaned = re.sub(response_pattern, "", cleaned, count=1).lstrip()
    
    # Pattern 4: Remove quotes if the entire response is quoted
    # e.g., '"Thank you all..." ' becomes 'Thank you all...'
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1].strip()
    elif cleaned.startswith("'") and cleaned.endswith("'"):
        cleaned = cleaned[1:-1].strip()
    
    return cleaned


def test_cleanup():
    """Test various cleanup patterns"""
    
    test_cases = [
        {
            "speaker": "Cynthia",
            "content": "Cynthia: Marvin, your focus on evolutionary trade-offs...",
            "expected": "Marvin, your focus on evolutionary trade-offs..."
        },
        {
            "speaker": "Cynthia",
            "content": """**Cynthia's Response:** 
"Thank you all for these rich insights. Marvin, your emphasis..." """,
            "expected": "Thank you all for these rich insights. Marvin, your emphasis..."
        },
        {
            "speaker": "Bob",
            "content": "**Bob's response:** I think we should consider...",
            "expected": "I think we should consider..."
        },
        {
            "speaker": "Fei-Fei",
            "content": "Fei-Fei: That's an interesting perspective...",
            "expected": "That's an interesting perspective..."
        },
        {
            "speaker": "Marcus",
            "content": '"I believe consciousness emerges from complexity."',
            "expected": "I believe consciousness emerges from complexity."
        },
        {
            "speaker": "Alice",
            "content": """**Alice's Response:**
That's a fascinating point about emergence.""",
            "expected": "That's a fascinating point about emergence."
        }
    ]
    
    print("Testing Enhanced Content Cleanup")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        result = _clean_content(test["speaker"], test["content"])
        success = result == test["expected"]
        
        if success:
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = "✗ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"Speaker: {test['speaker']}")
        print(f"Original: {test['content'][:60].replace(chr(10), '\\n')}...")
        print(f"Expected: {test['expected'][:60]}...")
        print(f"Got:      {result[:60]}...")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! Cleanup handles all patterns correctly.")
    else:
        print("❌ Some tests failed. Review the cleanup logic.")


if __name__ == "__main__":
    test_cleanup()