#!/usr/bin/env python3
"""Test suite for enhanced text processing utilities"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.text_processing import (
    strip_reasoning, 
    strip_response_prefixes, 
    clean_quote_formatting,
    extract_quote_pattern,
    clean_llm_response
)


def test_strip_reasoning():
    """Test removal of <think> blocks"""
    print("Testing strip_reasoning()...")
    
    # Test basic reasoning block removal
    text_with_reasoning = '''<think>
This is my reasoning about the quote adaptation.
Let me think through this carefully...
</think>

"The mind is everything. What you think you become." — Buddha'''
    
    expected = '''"The mind is everything. What you think you become." — Buddha'''
    result = strip_reasoning(text_with_reasoning)
    assert result.strip() == expected.strip(), f"Expected: {expected}, Got: {result}"
    print("✅ Basic reasoning block removal works")
    
    # Test case insensitive
    text_case_insensitive = '''<Think>Some reasoning</Think>Final result'''
    result = strip_reasoning(text_case_insensitive)
    assert result.strip() == "Final result", f"Expected: 'Final result', Got: {result}"
    print("✅ Case insensitive reasoning removal works")
    
    # Test multiple blocks
    text_multiple = '''<think>First</think>Middle<think>Second</think>End'''
    result = strip_reasoning(text_multiple)
    assert result.strip() == "MiddleEnd", f"Expected: 'MiddleEnd', Got: {result}"
    print("✅ Multiple reasoning block removal works")
    
    # Test no reasoning blocks
    text_no_reasoning = '''"Just a normal quote" — Author'''
    result = strip_reasoning(text_no_reasoning)
    assert result == text_no_reasoning, f"Expected: {text_no_reasoning}, Got: {result}"
    print("✅ Text without reasoning blocks unchanged")


def test_strip_response_prefixes():
    """Test removal of response prefixes"""
    print("\nTesting strip_response_prefixes()...")
    
    # Test adapted quote prefix
    text_with_prefix = '''Adapted quote: "The mind is everything." — Buddha'''
    expected = '''"The mind is everything." — Buddha'''
    result = strip_response_prefixes(text_with_prefix)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ 'Adapted quote:' prefix removal works")
    
    # Test other prefixes
    prefixes_to_test = [
        ("Response: Some text", "Some text"),
        ("Quote: Some text", "Some text"),
        ("Output: Some text", "Some text"),
        ("Answer: Some text", "Some text"),
    ]
    
    for text, expected in prefixes_to_test:
        result = strip_response_prefixes(text)
        assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Various response prefixes removal works")
    
    # Test case insensitive
    text_case = '''ADAPTED QUOTE: "Some quote" — Author'''
    expected = '''"Some quote" — Author'''
    result = strip_response_prefixes(text_case)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Case insensitive prefix removal works")


def test_clean_quote_formatting():
    """Test quote formatting cleanup"""
    print("\nTesting clean_quote_formatting()...")
    
    # Test parenthetical explanations removal
    text_with_explanation = '''"Quote text" — Author (This explains the quote context)'''
    expected = '''"Quote text" — Author'''
    result = clean_quote_formatting(text_with_explanation)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Parenthetical explanations removal works")
    
    # Test asterisked notes removal
    text_with_notes = '''"Quote text" — Author *(Note: This adapts the original)*'''
    expected = '''"Quote text" — Author'''
    result = clean_quote_formatting(text_with_notes)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Asterisked notes removal works")
    
    # Test smart quotes normalization
    text_smart_quotes = '''"Quote text" — Author'''  # Smart quotes
    expected = '''"Quote text" — Author'''  # Regular quotes
    result = clean_quote_formatting(text_smart_quotes)
    assert '"' in result, f"Smart quotes should be normalized: {result}"
    print("✅ Smart quotes normalization works")
    
    # Test attribution format normalization
    text_hyphen = '''"Quote text" - Author Name'''
    expected = '''"Quote text" — Author Name'''
    result = clean_quote_formatting(text_hyphen)
    assert " — " in result, f"Expected em dash, got: {result}"
    print("✅ Attribution format normalization works")


def test_extract_quote_pattern():
    """Test quote pattern extraction"""
    print("\nTesting extract_quote_pattern()...")
    
    # Test with messy text containing quote
    messy_text = '''Here's some explanation and then "The quote text" — Philosopher Name and more text after.'''
    expected = '''"The quote text" — Philosopher Name'''
    result = extract_quote_pattern(messy_text)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Quote pattern extraction from messy text works")
    
    # Test with hyphen instead of em dash
    text_hyphen = '''Blah blah "Quote with hyphen" - Author Name and more text'''
    expected = '''"Quote with hyphen" — Author Name'''
    result = extract_quote_pattern(text_hyphen)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Quote pattern extraction with hyphen works")
    
    # Test with no clear pattern
    text_no_pattern = '''Just some random text without quotes'''
    result = extract_quote_pattern(text_no_pattern)
    assert result == text_no_pattern, f"Expected original text when no pattern found"
    print("✅ No pattern found returns original text")


def test_clean_llm_response():
    """Test comprehensive response cleaning"""
    print("\nTesting clean_llm_response()...")
    
    # Test full pipeline with reasoning, prefix, and quote formatting
    messy_response = '''<think>
I need to adapt this quote carefully...
Let me consider the speaker's personality...
</think>

Adapted quote: "When we wrestle with the forces that pervert the rational order, let us ensure our own souls remain uncorrupted by the very shadows we seek to dispel." — Friedrich Nietzsche 

*(This phrasing mirrors the philosophical emphasis on harmony while using collaborative language)*'''
    
    expected = '''"When we wrestle with the forces that pervert the rational order, let us ensure our own souls remain uncorrupted by the very shadows we seek to dispel." — Friedrich Nietzsche'''
    
    result = clean_llm_response(messy_response, is_quote=True)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Full pipeline cleaning works")
    
    # Test non-quote response (should not apply quote-specific cleaning)
    non_quote_response = '''<think>Some reasoning</think>Response: Here is my analysis of the topic.'''
    expected = '''Here is my analysis of the topic.'''
    result = clean_llm_response(non_quote_response, is_quote=False)
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✅ Non-quote response cleaning works")
    
    # Test empty/whitespace handling
    empty_response = '''<think>reasoning</think>Adapted quote:   '''
    result = clean_llm_response(empty_response, is_quote=True)
    assert result == "", f"Expected empty string, got: '{result}'"
    print("✅ Empty response handling works")


def test_system_wide_cleaning():
    """Test system-wide response cleaning integration"""
    print("\nTesting system-wide LLM response cleaning...")
    
    # Test LLM client with reasoning block removal
    from src.utils.llm_client import LLMClient
    
    # Test that LLM client can be initialized with cleaning enabled (default)
    client_with_cleaning = LLMClient(clean_responses=True)
    assert client_with_cleaning.clean_responses == True, "LLM client should enable cleaning by default"
    print("✅ LLM client initializes with response cleaning enabled")
    
    # Test that LLM client can be initialized with cleaning disabled
    client_without_cleaning = LLMClient(clean_responses=False)
    assert client_without_cleaning.clean_responses == False, "LLM client should allow disabling cleaning"
    print("✅ LLM client can disable response cleaning")
    
    # Test that consequence test generator imports work
    try:
        from src.agents.consequence_test_generator import ConsequenceTestGenerator, ConsequenceTestContext
        print("✅ Consequence test generator imports successfully")
    except ImportError as e:
        print(f"❌ Consequence test generator import failed: {e}")
        raise
    
    # Test that base agent imports work
    try:
        from src.utils.text_processing import strip_reasoning
        # Test the strip_reasoning function works on consequence test style content
        messy_consequence = '''<think>
I need to create a consequence test for this philosophical tension.
Let me think about the implications...
</think>

Consequence Test: What evidence would distinguish between the objective vs subjective nature of mathematical truths?'''
        
        expected = '''Consequence Test: What evidence would distinguish between the objective vs subjective nature of mathematical truths?'''
        result = strip_reasoning(messy_consequence)
        assert result.strip() == expected.strip(), f"Expected clean consequence test, got: {result}"
        print("✅ Base agent response cleaning works for consequence tests")
        
    except Exception as e:
        print(f"❌ Base agent cleaning test failed: {e}")
        raise


def run_all_tests():
    """Run all text processing tests"""
    print("🧪 Starting Text Processing Test Suite")
    print("=" * 50)
    
    try:
        test_strip_reasoning()
        test_strip_response_prefixes()
        test_clean_quote_formatting()
        test_extract_quote_pattern()
        test_clean_llm_response()
        test_system_wide_cleaning()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TEXT PROCESSING TESTS PASSED!")
        print("✅ Enhanced response parsing is ready system-wide")
        print("✅ Duplicate prefixes and reasoning blocks should be eliminated")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)