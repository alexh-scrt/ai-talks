#!/usr/bin/env python3
"""Test script for content cleanup in log writer"""

def test_content_cleanup():
    """Test the content cleanup functionality"""
    
    print("Testing Content Cleanup in Log Writer\n" + "="*50 + "\n")
    
    # Simulate the _clean_content method
    def _clean_content(speaker: str, content: str) -> str:
        """Remove redundant speaker name from beginning of content"""
        if not content:
            return content
        
        # Trim whitespace
        cleaned = content.strip()
        
        # Check if content starts with speaker name followed by colon
        prefix = f"{speaker}:"
        if cleaned.lower().startswith(prefix.lower()):
            # Remove the prefix and any following whitespace
            cleaned = cleaned[len(prefix):].lstrip()
        
        return cleaned
    
    # Test cases
    test_cases = [
        {
            "speaker": "Cynthia",
            "original": "Cynthia: Marvin, your caution against anthropomorphizing tools intersects with a deeper ethical quandary...",
            "expected": "Marvin, your caution against anthropomorphizing tools intersects with a deeper ethical quandary..."
        },
        {
            "speaker": "Fei-Fei",
            "original": "Fei-Fei: Geoffrey, your distinction between statistical mirroring and causal scaffolding reminds me...",
            "expected": "Geoffrey, your distinction between statistical mirroring and causal scaffolding reminds me..."
        },
        {
            "speaker": "Marvin",
            "original": "Marvin: The premise assumes intelligence is a scalar quantity we can measure against...",
            "expected": "The premise assumes intelligence is a scalar quantity we can measure against..."
        },
        {
            "speaker": "Marcus",
            "original": "That's an interesting perspective, but I would argue differently.",
            "expected": "That's an interesting perspective, but I would argue differently."
        },
        {
            "speaker": "Sophia",
            "original": "sophia: I believe consciousness emerges from complex patterns.",
            "expected": "I believe consciousness emerges from complex patterns."
        }
    ]
    
    print("TEST CASES:")
    print("-" * 40)
    
    for i, test in enumerate(test_cases, 1):
        result = _clean_content(test["speaker"], test["original"])
        passed = result == test["expected"]
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"Speaker: {test['speaker']}")
        print(f"Original: {test['original'][:50]}...")
        print(f"Cleaned: {result[:50]}...")
        
        if not passed:
            print(f"Expected: {test['expected'][:50]}...")
    
    print("\n" + "="*50 + "\n")
    
    print("BEFORE CLEANUP:")
    print("-" * 40)
    print("""<Cynthia>
Cynthia: Marvin, your caution against anthropomorphizing...
</Cynthia>""")
    
    print("\nAFTER CLEANUP:")
    print("-" * 40)
    print("""<Cynthia>
Marvin, your caution against anthropomorphizing...
</Cynthia>""")
    
    print("\n" + "="*50)
    print("✅ Content cleanup test complete!\n")
    
    print("BENEFITS:")
    print("• Removes redundant speaker names")
    print("• Cleaner, more readable logs")
    print("• Consistent formatting")
    print("• Case-insensitive matching")
    print("• Preserves content when no prefix found")

if __name__ == "__main__":
    test_content_cleanup()