# less_eggs

Analysis tools and samples from FIN6/Skeleton Spider LNK campaign research targeting HR departments and recruiters.

## Overview

This repository contains deobfuscation tools and 108+ malicious LNK payloads analyzed from May 2024 through July 2025, demonstrating consistent use of `ie4uinit.exe` LOLBin abuse and more_eggs backdoor delivery.

## Tools

### `batdeobf.py`

Python script for deobfuscating batch command variable substitutions commonly used in LNK payloads.

```bash
python3 batdeobf.py <obfuscated_command>
```

### `infdeobf.py` 

Python script for deobfuscating INF files with variable substitution patterns.

```bash
python3 infdeobf.py <inf_file>
```

### `extract_payload.sh`

Bash script to extract and deobfuscate command-line arguments from LNK files in a directory.

```bash
./extract_payload.sh <directory_containing_lnk_files>
```

## Sample Data

### `payloads/original/`

Raw malicious LNK payloads extracted from the LNK samples.

### `payloads/deobfuscated/`

Deobfuscated payloads using the provided tools.

## Detection Signatures

- **LNK CreationTime**: `2024-05-16T05:57:35.249121Z`

## Research Context

This research supports comprehensive threat analysis of FIN6/Skeleton Spider's sustained campaign targeting recruitment processes. For detailed technical analysis and detection methodologies, refer to the associated threat intelligence report.

## License

Tools and analysis provided for cybersecurity research and defense purposes.
