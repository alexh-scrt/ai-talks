import re


def strip_reasoning(text: str) -> str:
    """
    Remove reasoning blocks from LLM response text.
    
    Strips content between <think> and </think> tags (case-insensitive).
    
    Args:
        text: The raw LLM response text
        
    Returns:
        The text with reasoning blocks removed
    """
    if not text:
        return text
    
    # Pattern to match <think>...</think> blocks (case-insensitive, with optional whitespace)
    # Using DOTALL flag to match across newlines
    pattern = r'<think\s*>.*?</think\s*>'
    
    # Remove the reasoning blocks and any extra whitespace they leave behind
    cleaned = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up any resulting multiple newlines and extra whitespace
    cleaned = re.sub(r'\n\s*\n+', '\n', cleaned)  # Multiple newlines to single
    cleaned = re.sub(r'  +', ' ', cleaned)        # Multiple spaces to single
    cleaned = re.sub(r'\n\s*"', '"', cleaned)     # Newline before quote
    cleaned = re.sub(r'"\s*\n', '"', cleaned)     # Newline after quote
    
    return cleaned.strip()


def strip_response_prefixes(text: str) -> str:
    """
    Remove common response prefixes from LLM output.
    
    Removes prefixes like "Adapted quote:", "Response:", "Quote:", etc.
    
    Args:
        text: The LLM response text
        
    Returns:
        The text with prefixes removed
    """
    if not text:
        return text
    
    # Common prefixes to remove (case-insensitive)
    prefixes = [
        r'adapted\s+quote\s*:\s*',
        r'response\s*:\s*',
        r'quote\s*:\s*',
        r'output\s*:\s*',
        r'result\s*:\s*',
        r'answer\s*:\s*'
    ]
    
    cleaned = text
    for prefix in prefixes:
        # Remove prefix at start of text (case-insensitive)
        pattern = rf'^\s*{prefix}'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()


def clean_quote_formatting(text: str) -> str:
    """
    Clean and normalize quote formatting.
    
    Handles various quote marks, removes extra formatting, and normalizes attribution.
    
    Args:
        text: The quote text to clean
        
    Returns:
        Cleaned quote text
    """
    if not text:
        return text
    
    cleaned = text
    
    # Remove explanatory text in parentheses or brackets at the end
    cleaned = re.sub(r'\s*\([^)]*\)\s*$', '', cleaned)
    cleaned = re.sub(r'\s*\[[^\]]*\]\s*$', '', cleaned)
    
    # Remove asterisked explanations like *(Note: ...)*
    cleaned = re.sub(r'\s*\*\([^)]*\)\*\s*', '', cleaned)
    
    # Clean up multiple quote marks and normalize
    cleaned = re.sub(r'["""]', '"', cleaned)  # Normalize smart quotes
    cleaned = re.sub(r"['']", "'", cleaned)   # Normalize smart apostrophes
    
    # Remove extra whitespace around quotes
    cleaned = re.sub(r'\s*"\s*', '"', cleaned)
    
    # Normalize attribution format (ensure proper spacing around em dash)
    cleaned = re.sub(r'\s*—\s*', ' — ', cleaned)
    cleaned = re.sub(r'\s*-\s*([A-Z][a-zA-Z\s]+)$', r' — \1', cleaned)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def extract_quote_pattern(text: str) -> str:
    """
    Extract quote using pattern matching as fallback.
    
    Looks for patterns like "Quote text" — Author or similar formats.
    
    Args:
        text: The text to extract quote from
        
    Returns:
        Extracted quote or original text if no pattern found
    """
    if not text:
        return text
    
    # Pattern to match: "quote text" — Author Name (stopping at punctuation or new clause)
    quote_pattern = r'"([^"]+)"\s*—\s*([A-Z][a-zA-Z\s.]+?)(?:\s+(?:and|but|or|,|\.|\n|$))'
    match = re.search(quote_pattern, text)
    
    if match:
        quote_text = match.group(1).strip()
        author = match.group(2).strip()
        return f'"{quote_text}" — {author}'
    
    # Fallback: simpler pattern that captures up to common stop words
    quote_pattern_simple = r'"([^"]+)"\s*—\s*([A-Z][a-zA-Z\s.]+?)(?:\s+(?:and|but|or|,|\.|\n)|\s*$)'
    match = re.search(quote_pattern_simple, text)
    
    if match:
        quote_text = match.group(1).strip()
        author = match.group(2).strip()
        return f'"{quote_text}" — {author}'
    
    # Pattern to match: "quote text" - Author Name (with hyphen)
    quote_pattern_hyphen = r'"([^"]+)"\s*-\s*([A-Z][a-zA-Z\s.]+?)(?:\s+(?:and|but|or|,|\.|\n)|\s*$)'
    match = re.search(quote_pattern_hyphen, text)
    
    if match:
        quote_text = match.group(1).strip()
        author = match.group(2).strip()
        return f'"{quote_text}" — {author}'
    
    # If no clear pattern, return original text
    return text


def clean_llm_response(text: str, is_quote: bool = False) -> str:
    """
    Comprehensive LLM response cleaning pipeline.
    
    Applies all cleaning operations in the correct order.
    
    Args:
        text: The raw LLM response
        is_quote: Whether this is a quote response (applies quote-specific cleaning)
        
    Returns:
        Cleaned response text
    """
    if not text:
        return text
    
    # Step 1: Remove reasoning blocks
    cleaned = strip_reasoning(text)
    
    # Step 2: Remove response prefixes
    cleaned = strip_response_prefixes(cleaned)
    
    # Step 3: Quote-specific cleaning
    if is_quote:
        # Try to extract quote pattern first
        quote_extracted = extract_quote_pattern(cleaned)
        if quote_extracted != cleaned:
            cleaned = quote_extracted
        else:
            # Apply general quote formatting cleanup
            cleaned = clean_quote_formatting(cleaned)
    
    # Step 4: Final cleanup
    cleaned = cleaned.strip()
    
    return cleaned