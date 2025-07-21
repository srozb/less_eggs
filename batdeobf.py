#!/usr/bin/env python3

import re
import sys
import argparse
from typing import Dict, Tuple


def extract_batch_variables(text: str) -> Dict[str, str]:
    """
    Extract batch variable assignments from 'set "var=value"' patterns.
    
    Args:
        text: Input batch text
        
    Returns:
        Dictionary of variable assignments
    """
    variables = {}
    
    # Match: set "variable=value" (with optional spaces and case insensitive)
    # Also match: set variable=value (without quotes)
    patterns = [
        r'(?i)[a-z]et\s+"([^"=]+)=([^"]*)"',  # set "var=value"
        r'(?i)[a-z]et\s+([^"=\s]+)=([^\s&]*)',  # set var=value (no quotes, stops at space or &)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for var_name, var_value in matches:
            variables[var_name.strip()] = var_value.strip()
    
    return variables

def adjust_for_loop_substitutions(text: str, variables: Dict[str, str]) -> Dict[str, str]:
    """
    Extract FOR loop patterns and adjust variable substitutions.
    """
    # Updated regex to handle quoted values and capture loop variable correctly
    for_pattern = r'(?i)\(for\s+%([a-z]+)\s+in\s+\("?([^"]*)"?\)\s+do\s+@set\s+"([a-z]+)=%~[a-z]+"\s?\)'
    matches = re.findall(for_pattern, text)
    
    for match in matches:
        if len(match) == 3:
            loop_var, value, target_var = match
            # Remove quotes from value if present
            value = value.strip('"')
            variables[loop_var] = value          # z = s
            variables[target_var] = value        # Outlip = s
        
    return variables

def extract_multi_assignment_for_loops(text: str, variables: Dict[str, str]) -> Dict[str, str]:
    """
    Extract FOR loops that set multiple variables like:
    (for %g in ("var1=val1" "var2=val2" ...) do @set %~g)
    """
    # Match FOR loops with multiple quoted assignments
    pattern = r'(?i)\(for\s+%[a-z]+\s+in\s+\(([^)]+)\)\s+do\s+@set\s+%~[a-z]+\)'
    matches = re.findall(pattern, text)
    
    for assignments_str in matches:
        # Extract all "var=value" patterns from the string
        assignment_pattern = r'"([^"=]+)=([^"]*)"'
        assignments = re.findall(assignment_pattern, assignments_str)
        
        for var_name, var_value in assignments:
            variables[var_name.strip()] = var_value.strip()
    
    return variables

def substitute_variables(text: str, variables: Dict[str, str]) -> Tuple[str, bool]:
    original_text = text
    
    def replace_var(match):
        var_name = match.group(1)
        return variables.get(var_name, match.group(0))
    
    # Process substitutions in the order they appear in text, not definition order
    result = re.sub(r'[!%](\w+)[!%]', replace_var, text)
    
    return result, result != original_text

def deobfuscate_batch(text: str, max_iterations: int = 50, verbose: bool = False) -> str:
    """
    Deobfuscate batch file with multiple passes until no more changes.
    
    Args:
        text: Input batch text
        max_iterations: Maximum number of deobfuscation passes
        verbose: Whether to show debug information
        
    Returns:
        Deobfuscated text
    """
    current_text = text
    iteration = 0
    
    if verbose:
        print(f"Starting deobfuscation...")
    
    while iteration < max_iterations:
        iteration += 1
        
        # Extract variables from current state
        variables = extract_batch_variables(current_text)

        # Adjust variables based on FOR loops
        variables = adjust_for_loop_substitutions(current_text, variables)

        
        # Extract multi-assignment FOR loops
        variables = extract_multi_assignment_for_loops(current_text, variables)

        if not variables:
            if verbose:
                print(f"No variables found in iteration {iteration}, stopping.")
            break
        
        if verbose:
            print(f"Iteration {iteration}: Found {len(variables)} variables")
            for var, val in list(variables.items())[:5]:  # Show first 5
                print(f"  {var} = {val}")
            if len(variables) > 5:
                print(f"  ... and {len(variables) - 5} more")
        
        # Perform substitution
        new_text, changed = substitute_variables(current_text, variables)
        
        if not changed:
            if verbose:
                print(f"No substitutions made in iteration {iteration}, stopping.")
            break
        
        current_text = new_text
        
        # Show a preview of changes
        if verbose:
            lines_changed = sum(1 for old, new in zip(text.split('\n'), current_text.split('\n')) if old != new)
            print(f"  Changed {lines_changed} lines")
    
    if verbose:
        if iteration >= max_iterations:
            print(f"Reached maximum iterations ({max_iterations}), stopping.")
        print(f"Deobfuscation completed in {iteration} iterations.")
    
    return current_text

def remove_variable_assignments(text: str) -> str:
    """Remove variable assignment lines from the text."""
    return re.sub(r'\s*[a-z]et\s+"[^"]+"\s*&&\s*', '', text, flags=re.IGNORECASE)

def clean_output(text: str) -> str:
    """
    Clean up the deobfuscated output for better readability.
    
    Args:
        text: Deobfuscated text
        
    Returns:
        Cleaned text
    """
    # Remove excessive && chains and normalize whitespace
    cleaned = re.sub(r'\s*&&\s*', ' && ', text)
    
    # Split long lines at && for better readability
    lines = []
    for line in cleaned.split('\n'):
        if len(line) > 120 and ' && ' in line:
            parts = line.split(' && ')
            for i, part in enumerate(parts):
                if i == 0:
                    lines.append(part + ' &&')
                elif i == len(parts) - 1:
                    lines.append('  ' + part)
                else:
                    lines.append('  ' + part + ' &&')
        else:
            lines.append(line)
    
    return '\n'.join(lines)

def main():
    """Main function with argument parsing and stdin support"""
    parser = argparse.ArgumentParser(description='Deobfuscate batch files with layered substitution')
    parser.add_argument('file', nargs='?', help='Path to file (if not provided, reads from stdin)')
    parser.add_argument('--max-iterations', '-m', type=int, default=50, 
                       help='Maximum number of deobfuscation passes (default: 50)')
    parser.add_argument('--raw', '-r', action='store_true',
                       help='Output raw result without line splitting/formatting')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose deobfuscation progress')
    parser.add_argument('--keep-vars', '-k', action='store_true',
                       help='Keep variable assignment lines in output')
    args = parser.parse_args()
    
    # Read content from file or stdin
    if args.file:
        with open(args.file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    # Deobfuscate
    deobfuscated = deobfuscate_batch(content, args.max_iterations, args.verbose)
    
    # Remove variable assignments unless requested to keep them
    if not args.keep_vars:
        deobfuscated = remove_variable_assignments(deobfuscated)
    
    # Clean output unless raw mode is requested
    if not args.raw:
        deobfuscated = clean_output(deobfuscated)
    
    # Only show header in verbose mode
    if args.verbose:
        print("\n" + "="*80)
        print("DEOBFUSCATED OUTPUT:")
        print("="*80)
    
    print(deobfuscated)

if __name__ == "__main__":
    main()
