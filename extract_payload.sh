#!/bin/bash

# A script to extract and deobfuscate command-line payloads from .lnk files
# in a given directory.

# --- Configuration ---
# Your Python deobfuscation script. Assumes it's in your PATH.
DEOBF_SCRIPT="batdeobf.py"

# --- Pre-flight Checks ---

# 1. Check for required command-line tools
for cmd in lnkparse jq "$DEOBF_SCRIPT"; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Error: Required command '$cmd' is not installed or not in your PATH."
    exit 1
  fi
done

# 2. Check for correct number of arguments
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /path/to/samples"
  exit 1
fi

# 3. Check if the provided argument is a directory
SAMPLES_DIR="$1"
if [ ! -d "$SAMPLES_DIR" ]; then
  echo "❌ Error: Directory not found at '$SAMPLES_DIR'"
  exit 1
fi

# --- Setup Output Directories ---
OUTPUT_DIR="payloads"
ORIGINAL_DIR="$OUTPUT_DIR/original"
DEOBFUSCATED_DIR="$OUTPUT_DIR/deobfuscated"

echo "Setting up output directories..."
mkdir -p "$ORIGINAL_DIR"
mkdir -p "$DEOBFUSCATED_DIR"
echo "  - $ORIGINAL_DIR"
echo "  - $DEOBFUSCATED_DIR"
echo "" # Newline for spacing

# --- Main Processing Loop ---
shopt -s nullglob # Prevent loop from running if no files match
file_count=0

for file in "$SAMPLES_DIR"/*; do
  # Ensure we are only processing files
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    echo "▶️  Processing: $filename"

    # Extract the original payload using lnkparse and jq
    # The '-r' flag for jq removes the surrounding quotes from the string
    original_payload=$(lnkparse -j "$file" | jq -r '.data.command_line_arguments')

    # Check if a payload was actually extracted
    if [ -z "$original_payload" ]; then
      echo "   ⚠️  Warning: No command_line_arguments found in $filename. Skipping."
      continue
    fi

    # Save the original payload
    echo "$original_payload" >"$ORIGINAL_DIR/$filename.txt"
    echo "   - Saved original payload."

    # Deobfuscate the payload by piping it to the Python script
    deobfuscated_payload=$(echo "$original_payload" | "$DEOBF_SCRIPT")

    # Save the deobfuscated result
    echo "$deobfuscated_payload" >"$DEOBFUSCATED_DIR/$filename.txt"
    echo "   - Saved deobfuscated payload."

    ((file_count++))
  fi
done

shopt -u nullglob # Unset nullglob

echo -e "\n✅ Done. Processed $file_count file(s)."
echo "   Results are in the '$OUTPUT_DIR/' directory."
