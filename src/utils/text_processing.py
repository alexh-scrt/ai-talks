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
    
    # Clean up any resulting double spaces or extra newlines
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    cleaned = re.sub(r'  +', ' ', cleaned)
    
    return cleaned.strip()