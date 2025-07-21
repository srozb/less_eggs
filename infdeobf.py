#!/usr/bin/env python3

import re
from typing import Dict, Tuple

def extract_substitutions(buffer: str) -> Tuple[Dict[str, str], str]:
    """
    Extract substitutions using regex and return modified buffer without them.
    
    Args:
        buffer: Input text buffer
        
    Returns:
        Tuple of (substitutions dict, modified buffer)
    """
    lines = buffer.split('\n')
    substitutions = {}
    modified_lines = []
    
    # Regex pattern: optional spaces, word, optional spaces, =, optional spaces, any chars
    pattern = r'^\s*(\w+)\s*=\s*(.*)$'
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            key, value = match.groups()
            # Clean up the value (remove quotes and extra whitespace)
            substitutions[key] = value.strip().strip('\'"')
        else:
            modified_lines.append(line)
    
    return substitutions, '\n'.join(modified_lines)

def deobfuscate(buffer: str, substitutions: Dict[str, str]) -> str:
    """
    Deobfuscate buffer by replacing %variable% patterns with their values.
    
    Args:
        buffer: Text buffer with %variable% patterns
        substitutions: Dictionary mapping variable names to their values
        
    Returns:
        Deobfuscated text
    """
    result = buffer
    
    # Replace each %variable% with its substitution value
    for key, value in substitutions.items():
        pattern = f'%{key}%'
        result = result.replace(pattern, value)
    
    return result

def main():
    """Main function with argument parsing and stdin support"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Deobfuscate SCT files with simple substitution')
    parser.add_argument('file', nargs='?', help='Path to file (if not provided, reads from stdin)')
    args = parser.parse_args()
    
    # Read content from file or stdin
    if args.file:
        with open(args.file, 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    # Extract substitutions and get cleaned buffer
    substitutions, cleaned_buffer = extract_substitutions(content)
    
    # Deobfuscate the cleaned buffer
    deobfuscated = deobfuscate(cleaned_buffer, substitutions)
    
    #print("Substitutions found:")
    #for k, v in substitutions.items():
    #    print(f"  {k} = {v}")
    
    print(deobfuscated)

if __name__ == "__main__":
    main()
