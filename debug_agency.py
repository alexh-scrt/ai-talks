#!/usr/bin/env python3
"""Debug agency signal extraction"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.signal_extractors import SignalExtractor


def debug_agency_extraction():
    """Debug agency extraction step by step"""
    
    # Test exchanges with clear agency patterns
    test_exchanges = [
        {'content': 'We should act with courage.'},  # A_ought + A_decis
        {'content': 'I choose to proceed despite doubt.'},  # A_decis + A_stance  
        {'content': 'Therefore, this implies that X.'},  # A_conseq
        {'content': 'We must take responsibility.'},  # A_ought
        {'content': 'I decide to commit to this path.'},  # A_decis
        {'content': 'Therefore we should act under ambiguity. <!-- decision_rule -->'},  # Tagged decision rule
    ]
    
    extractor = SignalExtractor()
    
    print("Debug: Testing individual pattern detection...")
    
    # Test each exchange
    for i, exchange in enumerate(test_exchanges):
        content = exchange['content']
        print(f"\nExchange {i}: '{content}'")
        
        # Test ought patterns
        ought_patterns = extractor.agency_patterns['ought']
        ought_matches = 0
        for pattern_str in ought_patterns:
            import re
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = list(pattern.finditer(content))
            if matches:
                print(f"  A_ought match: '{pattern_str}' -> {[m.group() for m in matches]}")
                ought_matches += len(matches)
        
        # Test decis patterns  
        decis_patterns = extractor.agency_patterns['decis']
        decis_matches = 0
        for pattern_str in decis_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = list(pattern.finditer(content))
            if matches:
                print(f"  A_decis match: '{pattern_str}' -> {[m.group() for m in matches]}")
                decis_matches += len(matches)
        
        # Check decision rule tag
        if '<!-- decision_rule -->' in content:
            print(f"  Decision rule tag detected!")
            decis_matches += 1
            
        print(f"  Total: ought={ought_matches}, decis={decis_matches}")
    
    # Test the full computation
    print("\n" + "="*50)
    result = extractor.compute_agency_score(test_exchanges, window_size=8)
    
    print(f"Final Results:")
    print(f"  Overall A: {result['A']:.3f}")
    print(f"  A_ought: {result['A_ought']:.3f}")
    print(f"  A_decis: {result['A_decis']:.3f}")
    print(f"  A_conseq: {result['A_conseq']:.3f}")
    print(f"  A_stance: {result['A_stance']:.3f}")
    
    # Test raw extraction
    print(f"\nDebug: Raw extraction results...")
    A_ought = extractor._extract_agency_subsignal('ought', test_exchanges)
    A_decis = extractor._extract_decision_language(test_exchanges)
    A_conseq = extractor._extract_agency_subsignal('conse', test_exchanges)
    A_stance = extractor._extract_agency_subsignal('stanc', test_exchanges)
    
    print(f"  Raw A_ought: {A_ought}")
    print(f"  Raw A_decis: {A_decis}")
    print(f"  Raw A_conseq: {A_conseq}")
    print(f"  Raw A_stance: {A_stance}")
    
    turns = len(test_exchanges)
    print(f"  Turns: {turns}")
    
    # Test subscore function
    print(f"\nSubscore calculations:")
    print(f"  A_ought subscore: {extractor._subscore(A_ought, turns):.3f}")
    print(f"  A_decis subscore: {extractor._subscore(A_decis, turns):.3f}")
    print(f"  A_conseq subscore: {extractor._subscore(A_conseq, turns):.3f}")
    print(f"  A_stance subscore: {extractor._subscore(A_stance, turns):.3f}")
    
    return result


if __name__ == "__main__":
    debug_agency_extraction()