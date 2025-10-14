#!/usr/bin/env python3
"""
Publish utility for AI Talks conversation logs.
Transforms raw conversation logs into publication-ready markdown format.

Usage:
    python publish.py <input_log_path> [--output <output_path>]
    
Example:
    python publish.py outputs/conversation_talks_abc123_20250113.md
    python publish.py outputs/conversation_talks_abc123_20250113.md --output published/discussion.md
"""

import re
import argparse
from pathlib import Path
from typing import List, Tuple, Dict


class ConversationPublisher:
    """Transforms conversation logs into publication-ready format"""
    
    def __init__(self, input_path: str):
        self.input_path = Path(input_path)
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        self.content = self.input_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.participants: Dict[str, str] = {}  # lowercase -> proper case mapping
    
    def extract_participants(self) -> None:
        """
        Extract all participants from XML tags in the document.
        Creates a mapping of lowercase names to proper case names.
        Example: <Fei-Fei>...</Fei-Fei> -> {'fei-fei': 'Fei-Fei'}
        """
        # Find all opening tags
        tag_pattern = r'<([^/>]+)>'
        matches = re.findall(tag_pattern, self.content)
        
        for name in matches:
            # Skip common non-participant tags
            if name.lower() in ['final_answer', 'synthesizer']:
                continue
            
            # Store mapping: lowercase -> proper case
            self.participants[name.lower()] = name
    
    def capitalize_participant_names(self, text: str) -> str:
        """
        Capitalize participant names in text and make them bold.
        Example: fei-fei -> **Fei-Fei**, hipatia -> **Hipatia**
        """
        # Sort by length (longest first) to avoid partial matches
        sorted_participants = sorted(self.participants.items(), 
                                    key=lambda x: len(x[0]), 
                                    reverse=True)
        
        for lowercase_name, proper_name in sorted_participants:
            # Match the lowercase name as a whole word (case-insensitive)
            # but not when already in markdown bold or in tags
            pattern = r'(?<!\*\*)(?<!<)(?<!/)' + re.escape(lowercase_name) + r'(?!>)(?!\*\*)'
            replacement = f'**{proper_name}**'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def clean_synthesis_content(self, text: str) -> str:
        """
        Clean synthesis block content by removing specific patterns:
        1. Remove **Synthesis:** or Synthesis: at the start
        2. Remove "What's at stake?" 
        3. Remove numbered patterns like "1. **What's at stake?**"
        4. Remove "2. **Where's the agreement?**" or similar
        5. Remove "3. **Next question?**" or similar (may be on separate line)
        6. Remove trailing parenthetical notes like "(4 sentences...)"
        """
        """
        Clean synthesis block content by removing specific patterns:
        1. Remove **Synthesis:** or Synthesis: at the start
        2. Remove numbered list markers and question prefixes
        3. Remove variations like "What's at stake?", "Where's the agreement?", etc.
        4. Remove trailing parenthetical notes like "(4 sentences...)"
        """
        # Remove **Synthesis:** or Synthesis: at the beginning
        text = re.sub(r'^\s*\*\*Synthesis:\*\*\s*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Synthesis:\s*\n?', '', text, flags=re.MULTILINE)
        
        # Remove numbered list items with question patterns - keep only the answer content
        # Pattern: "1. **What's at stake?** The answer..." -> "The answer..."
        text = re.sub(r'^\s*\d+\.\s*\*\*What\'?s at stake\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\d+\.\s*\*\*At [Ss]take\*\*:?\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove "Where's the agreement?" variations
        text = re.sub(r'^\s*\d+\.\s*\*\*Where\'?s the agreement\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\d+\.\s*\*\*Agreement\*\*:?\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove "Next question?" variations (including "What's the next question?")
        text = re.sub(r'^\s*\d+\.\s*\*\*Next question\*\*:?\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\d+\.\s*\*\*What\'?s the next question\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\*\*What\'?s the next question\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove standalone variations without numbers
        text = re.sub(r'^\s*\*\*What\'?s at stake\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\*\*Where\'?s the agreement\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\*\*Next question\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove other common synthesis headers
        text = re.sub(r'^\s*\*\*Actionable [Ff]ocus\*\*:?\s+', '', text, flags=re.MULTILINE)

        # Remove **Synthesis:** or Synthesis: at the beginning
        text = re.sub(r'^\s*\*\*Synthesis:\*\*\s*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Synthesis:\s*\n?', '', text, flags=re.MULTILINE)
        
        # Remove numbered items with "What's at stake?" - remove the prefix, keep content after
        text = re.sub(r'^\s*\d+\.\s*\*\*What\'s at stake\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*What\'s at stake\?\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove numbered items with "Where's the agreement?"
        text = re.sub(r'^\s*\d+\.\s*\*\*Where\'s the agreement\?\*\*\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*Where\'s the agreement\?\s+', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove "Next question?" - could be numbered or standalone, on same line or separate
        text = re.sub(r'^\s*\d+\.\s*\*\*Next question\?\*\*\s*\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\*\*Next question\?\*\*\s*\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*Next question\?\s*\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Also handle "The next question:" or "Next productive question:" variations
        text = re.sub(r'^\s*\d+\.\s*\*\*(?:The )?[Nn]ext (?:productive )?question\?\*\*\s*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\*\*(?:The )?[Nn]ext (?:productive )?question\?\*\*\s*\n?', '', text, flags=re.MULTILINE)
        
        # Remove trailing parenthetical notes before the end
        # Matches patterns like: (4 sentences, grounded in...) or (3 sentences...)
        text = re.sub(r'\n\s*\([^)]+\)\s*$', '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def clean_xml_tags(self, text: str, speaker: str) -> Tuple[str, str]:
        """
        Remove XML-style tags and extract speaker name.
        
        Args:
            text: Text with XML tags like <Speaker>content</Speaker>
            speaker: Current speaker name
            
        Returns:
            Tuple of (cleaned_text, speaker_name)
        """
        # Match opening tag
        opening_match = re.match(r'^<([^>]+)>(.*)$', text, re.DOTALL)
        if opening_match:
            speaker = opening_match.group(1)
            content = opening_match.group(2)
            
            # Remove closing tag if present
            closing_match = re.search(r'(.*)</[^>]+>$', content, re.DOTALL)
            if closing_match:
                content = closing_match.group(1)
            
            return content.strip(), speaker
        
        return text, speaker
    
    def clean_final_answer_tags(self, text: str) -> str:
        """Remove <final_answer> tags but keep content"""
        text = re.sub(r'<final_answer>\s*', '', text)
        text = re.sub(r'\s*</final_answer>', '', text)
        return text
    
    def format_speaker_block(self, speaker: str, content: str) -> str:
        """
        Format a speaker's content block.
        
        Args:
            speaker: Speaker name
            content: Speaker's content
            
        Returns:
            Formatted markdown block
        """
        # Clean the content
        content = content.strip()
        
        # Remove redundant speaker prefixes at the beginning
        content = re.sub(rf'^{re.escape(speaker)}:\s*', '', content)
        content = re.sub(rf'^\*\*{re.escape(speaker)}:\*\*\s*', '', content)
        content = re.sub(rf'^\*\*{re.escape(speaker)}\'s [Rr]esponse:\*\*\s*\n?', '', content)
        
        # Apply participant name capitalization and bolding
        content = self.capitalize_participant_names(content)
        
        return f"**{speaker}:**\n\n{content}\n\n---"
    
    def format_synthesis_block(self, content: str) -> str:
        """Format synthesis block with Voice of Reason styling"""
        # Clean synthesis-specific patterns
        content = self.clean_synthesis_content(content)
        
        # Apply participant name capitalization and bolding
        content = self.capitalize_participant_names(content)
        
        return f"**Voice of Reason:**\n\n{content}\n\n---"
    
    def process_section(self, section_lines: List[str], section_name: str) -> str:
        """
        Process a section of the conversation.
        
        Args:
            section_lines: Lines in this section
            section_name: Name of the section (Introduction, Discussion, etc.)
            
        Returns:
            Formatted section content
        """
        output = []
        current_speaker = None
        current_content = []
        
        i = 0
        while i < len(section_lines):
            line = section_lines[i]
            
            # Check for speaker tag
            if line.startswith('<'):
                # Save previous speaker's content
                if current_speaker and current_content:
                    content_text = '\n'.join(current_content).strip()
                    
                    # Special handling for Synthesizer
                    if current_speaker == "Synthesizer":
                        output.append(self.format_synthesis_block(content_text))
                    else:
                        output.append(self.format_speaker_block(current_speaker, content_text))
                    
                    output.append('')  # Add blank line between speakers
                
                # Extract new speaker and content
                cleaned, new_speaker = self.clean_xml_tags(line, current_speaker)
                current_speaker = new_speaker
                current_content = [cleaned] if cleaned else []
            else:
                # Continue accumulating current speaker's content
                if line.strip():  # Skip empty lines within a block
                    current_content.append(line)
            
            i += 1
        
        # Handle final speaker
        if current_speaker and current_content:
            content_text = '\n'.join(current_content).strip()
            
            if current_speaker == "Synthesizer":
                output.append(self.format_synthesis_block(content_text))
            else:
                output.append(self.format_speaker_block(current_speaker, content_text))
        
        return '\n'.join(output)
    
    def publish(self, output_path: str = None) -> str:
        """
        Transform the conversation log into publication format.
        
        Args:
            output_path: Optional output file path. If None, returns string.
            
        Returns:
            Published content as string
        """
        # First, extract all participants from the document
        self.extract_participants()
        
        sections = {
            'header': [],
            'introduction': [],
            'discussion': [],
            'closing': []
        }
        
        current_section = 'header'
        
        # Parse the document into sections
        for line in self.lines:
            # Detect section headers
            if line.startswith('## Introduction'):
                current_section = 'introduction'
                continue
            elif line.startswith('## Discussion'):
                current_section = 'discussion'
                continue
            elif line.startswith('## Synthesis'):
                # Keep synthesis in discussion flow (chronological order)
                current_section = 'discussion'
                continue
            elif line.startswith('## Closing'):
                current_section = 'closing'
                continue
            
            sections[current_section].append(line)
        
        # Build the published document
        output = []
        
        # Keep header as-is (but capitalize participant names in metadata)
        for line in sections['header']:
            output.append(self.capitalize_participant_names(line))
        output.append('')
        
        # Process Introduction
        if sections['introduction']:
            output.append('## Introduction')
            output.append('')
            intro_content = self.process_section(sections['introduction'], 'introduction')
            output.append(intro_content)
            output.append('')
        
        # Process Discussion (includes synthesis blocks in chronological order)
        if sections['discussion']:
            output.append('## Discussion')
            output.append('')
            discussion_content = self.process_section(sections['discussion'], 'discussion')
            output.append(discussion_content)
            output.append('')
        
        # Process Closing
        if sections['closing']:
            output.append('## Closing')
            output.append('')
            closing_content = self.process_section(sections['closing'], 'closing')
            # Clean final_answer tags from closing
            closing_content = self.clean_final_answer_tags(closing_content)
            output.append(closing_content)
        
        # Join and clean up excess blank lines
        published_text = '\n'.join(output)
        published_text = re.sub(r'\n{3,}', '\n\n', published_text)
        
        # Write to file if output path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(published_text, encoding='utf-8')
            print(f"✅ Published to: {output_file}")
        
        return published_text


def main():
    parser = argparse.ArgumentParser(
        description='Transform AI Talks conversation logs into publication-ready format'
    )
    parser.add_argument(
        'input',
        help='Path to input conversation log file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Path to output file (default: <input>_published.md)',
        default=None
    )
    parser.add_argument(
        '--print', '-p',
        action='store_true',
        help='Print to stdout instead of writing to file'
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = args.output
    elif not args.print:
        input_path = Path(args.input)
        output_path = input_path.parent / f"{input_path.stem}_published{input_path.suffix}"
    else:
        output_path = None
    
    # Process the log
    try:
        publisher = ConversationPublisher(args.input)
        published_content = publisher.publish(output_path if not args.print else None)
        
        if args.print:
            print(published_content)
        else:
            print(f"✅ Successfully published conversation log")
            print(f"   Input:  {args.input}")
            print(f"   Output: {output_path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())