# emotibit_automation

This script automates EmotiBit data archiving by running the EmotiBit DataParser and then organizes the output into the standard folder structure with `Raw/` and `Parsed/` directories.

## How it works:
Run the script and enter:
- Source directory (where the raw files are)
- Output directory (where to save the organized files)
- Participant number (P#)
- EmotiBit number (E#)
- Week number (W#)
- Day number (D#)

Make sure to update the path to your local EmotiBit DataParser executable!

### File Handling
- Raw files include: `YYYY-MM-DD_HH-MM-SS-######.csv` and `*_info.json`
- Parsed files include: all other data streams and the LSL marker stream
