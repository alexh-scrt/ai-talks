"""
CT Cleanup Module - Replace verbose Consequence Test blocks with one-line templates

This module implements the Phase 6A CT Cleanup enhancement to replace verbose
multi-paragraph Consequence Test blocks with concise one-line templates based on context.
"""

import re
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class ConsequenceTestCleanup:
    """
    Replaces verbose Consequence Test blocks with one-line templates
    
    Analyzes context to determine whether the discussion involves suspending action
    (CT-True template) or acting despite uncertainty (CT-False template).
    """
    
    # Template constants from design specification
    CT_TRUE = "Consequence Test: If radical doubt suspends action until certainty, then prediction: moral hesitation rates rise when uncertainty primes are shown."
    
    CT_FALSE = "Consequence Test: If doubt doesn't suspend action, example: agents still choose under ambiguity (e.g., Pascal-style commitments)."
    
    # Detection patterns for context analysis
    SUSPEND_PATTERNS = [
        r'\b(suspend|withhold|defer|wait|no action|halt)\b',
        r'\buntil\s+(certain|proof|evidence)\b',
        r'\bwait\s+for\b',
        r'\bmoral\s+hesitation\b',
        r'\bpostpone\b',
        r'\babstain\b'
    ]
    
    ACT_PATTERNS = [
        r'\b(choose|act|commit|proceed|despite)\b',
        r'\bcommitment\b',
        r'\bdecision\s+under\s+uncertainty\b',
        r'\bact\s+anyway\b',
        r'\bpascal\b',
        r'\bpragmatic\b',
        r'\bproceed\s+with\b',
        r'\bmove\s+forward\b'
    ]
    
    # Main regex for CT block detection - matches from "Consequence Test:" to next speaker or end
    CT_BLOCK_PATTERN = r'(?ms)^Consequence Test:.*?(?=\n\s*\n\*\*[A-Z][^*]*\*\*:|\n\s*\n|\Z)'
    
    def __init__(self, context_window: int = 1500):
        """
        Initialize CT cleanup processor
        
        Args:
            context_window: Number of characters to analyze before CT block for context
        """
        self.context_window = context_window
        
        # Compile patterns for efficiency
        self.suspend_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPEND_PATTERNS]
        self.act_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.ACT_PATTERNS]
        self.ct_block_regex = re.compile(self.CT_BLOCK_PATTERN)
        
        logger.info("📋 CT Cleanup processor initialized")
    
    def is_suspend_context(self, context: str) -> bool:
        """
        Determine if context suggests suspending action until certainty
        
        Args:
            context: Text to analyze for suspend vs act language
            
        Returns:
            True if context suggests suspension, False if suggests action
        """
        # Count matches for each pattern type
        suspend_matches = sum(len(regex.findall(context)) for regex in self.suspend_regex)
        act_matches = sum(len(regex.findall(context)) for regex in self.act_regex)
        
        logger.debug(f"Context analysis: {suspend_matches} suspend, {act_matches} act matches")
        
        # If tied or no matches, default to suspend (CT-True)
        return suspend_matches >= act_matches
    
    def choose_template(self, context: str) -> str:
        """
        Select appropriate template based on preceding context
        
        Args:
            context: Text preceding the CT block to analyze
            
        Returns:
            Either CT_TRUE or CT_FALSE template
        """
        if self.is_suspend_context(context):
            logger.debug("Selected CT-True template (suspend action)")
            return self.CT_TRUE
        else:
            logger.debug("Selected CT-False template (act despite uncertainty)")
            return self.CT_FALSE
    
    def replace_ct_blocks(self, document: str) -> str:
        """
        Main replacement logic: find CT blocks and replace with one-line templates
        
        Args:
            document: Full transcript with potentially verbose CT blocks
            
        Returns:
            Cleaned document with one-line CT templates
        """
        logger.info("🧹 Starting CT block cleanup")
        
        def replace_block(match):
            """Replace individual CT block with appropriate template"""
            start_pos = match.start()
            
            # Extract context before this CT block
            context_start = max(0, start_pos - self.context_window)
            context = document[context_start:start_pos]
            
            # Choose template based on context
            template = self.choose_template(context)
            
            logger.debug(f"Replacing CT block at position {start_pos}")
            return template
        
        # Find and replace all CT blocks
        original_count = len(self.ct_block_regex.findall(document))
        if original_count == 0:
            logger.info("No CT blocks found to clean")
            return document
        
        cleaned_document = self.ct_block_regex.sub(replace_block, document)
        
        # Verify results
        new_count = len(self.ct_block_regex.findall(cleaned_document))
        templates_count = cleaned_document.count("Consequence Test:")
        
        logger.info(f"✅ CT cleanup complete: {original_count} blocks → {templates_count} one-liners")
        
        # Sanity check: ensure we have proper one-line replacements
        if new_count != templates_count:
            logger.warning(f"Mismatch in CT count: {new_count} blocks vs {templates_count} templates")
        
        return cleaned_document
    
    def validate_cleanup(self, document: str) -> Dict[str, bool]:
        """
        Validate that CT cleanup was successful
        
        Args:
            document: Cleaned document to validate
            
        Returns:
            Dict with validation results
        """
        results = {
            'no_multiline_ct': True,
            'no_quoted_paragraphs': True,
            'proper_templates': True,
            'speaker_tags_preserved': True
        }
        
        # Check for multi-line CT blocks
        ct_lines = [line for line in document.split('\n') if line.startswith('Consequence Test:')]
        
        # Each CT should be exactly one line and match a template
        for line in ct_lines:
            if line not in [self.CT_TRUE, self.CT_FALSE]:
                results['proper_templates'] = False
            
            # Check for quoted paragraphs (shouldn't exist in one-liners)
            if '"' in line and len(line.split('"')) > 3:  # More than simple quoted phrases
                results['no_quoted_paragraphs'] = False
        
        # Check that speaker tags are preserved
        speaker_tags = re.findall(r'\*\*[A-Z][^*]*\*\*:', document)
        if not speaker_tags and '**' in document:  # Had speakers but now missing
            results['speaker_tags_preserved'] = False
        
        logger.info(f"Validation results: {results}")
        return results


def test_ct_cleanup():
    """Quick test function for CT cleanup functionality"""
    
    # Test document with verbose CT blocks
    test_doc = """
**Alice:** We should suspend judgment until more evidence arrives.

Consequence Test: This is a very long paragraph that restates 
the prior argument and adds unnecessary prose. It goes on and on
with redundant information about suspending action until we have
more certainty about the philosophical implications.

**Bob:** I agree with that approach.

**Charlie:** But sometimes we must act despite uncertainty.

Consequence Test: Another verbose block here that talks about
commitment and choice under ambiguity, referencing Pascal's
wager and pragmatic decision-making when certainty is impossible.
We should proceed with action even when metaphysical doubt persists.

**David:** That makes sense too.
"""
    
    # Test cleanup
    processor = ConsequenceTestCleanup()
    cleaned = processor.replace_ct_blocks(test_doc)
    
    print("Original CT blocks found:", test_doc.count("Consequence Test:"))
    print("Cleaned CT lines:", cleaned.count("Consequence Test:"))
    print("\nCleaned document:")
    print(cleaned)
    
    # Validate results
    validation = processor.validate_cleanup(cleaned)
    print(f"\nValidation: {validation}")
    
    return cleaned, validation


if __name__ == "__main__":
    # Run test when executed directly
    test_ct_cleanup()