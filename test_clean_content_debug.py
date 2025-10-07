#!/usr/bin/env python3
"""Debug why content cleanup isn't working for Cynthia"""

def _clean_content(speaker: str, content: str) -> str:
    """Remove redundant speaker name from beginning of content"""
    if not content:
        return content
    
    # Trim whitespace
    cleaned = content.strip()
    
    # Check if content starts with speaker name followed by colon
    # Handle both exact match and variations with hyphens (e.g., Fei-Fei)
    prefix = f"{speaker}:"
    print(f"DEBUG: Checking if '{cleaned[:20]}...' starts with '{prefix}'")
    print(f"DEBUG: Lower comparison: '{cleaned.lower()[:20]}...' vs '{prefix.lower()}'")
    
    if cleaned.lower().startswith(prefix.lower()):
        # Remove the prefix and any following whitespace
        cleaned = cleaned[len(prefix):].lstrip()
        print(f"DEBUG: Removed prefix, result: '{cleaned[:50]}...'")
    else:
        print(f"DEBUG: No match, keeping original")
    
    return cleaned


def test_cases():
    """Test various cases"""
    
    test_data = [
        {
            "speaker": "Cynthia",
            "content": "Cynthia: Marvin, your focus on evolutionary trade-offs invites us to consider intelligence as a *social artifact*..."
        },
        {
            "speaker": "Fei-Fei",
            "content": "Fei-Fei: That's an interesting perspective on neural networks..."
        },
        {
            "speaker": "Marcus",
            "content": "Marcus: I believe we need to consider ethics here..."
        },
        {
            "speaker": "Bob",
            "content": "That's interesting, but what about consciousness?"
        }
    ]
    
    print("Testing Content Cleanup Debug")
    print("=" * 60)
    
    for i, test in enumerate(test_data, 1):
        print(f"\nTest {i}:")
        print("-" * 40)
        result = _clean_content(test["speaker"], test["content"])
        print(f"Original: {test['content'][:60]}...")
        print(f"Cleaned:  {result[:60]}...")
        print()


if __name__ == "__main__":
    test_cases()