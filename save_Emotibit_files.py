import os
import shutil
import subprocess
import glob
import re
from datetime import datetime

def get_user_input():
    """Get P#, E#, W#, D# from user"""
    participant_num = int(input("Enter participant number (P#): "))
    emotibit_num = int(input("Enter emotibit number (E#): "))
    week_num = int(input("Enter week number (W#): "))
    day_num = int(input("Enter day number (D#): "))
    return participant_num, emotibit_num, week_num, day_num

def find_raw_files(source_dir):
    """Find first 2 CSV and JSON files sorted by timestamp"""
    csv_files = sorted([f for f in os.listdir(source_dir) if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{3}\.csv', f)])
    json_files = sorted([f for f in os.listdir(source_dir) if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{3}_info\.json', f)])
    return csv_files[:2], json_files[:2]

def setup_folders(output_dir):
    """Create Raw and Parsed folders if they don't exist"""
    raw_folder = os.path.join(output_dir, "Raw")
    parsed_folder = os.path.join(output_dir, "Parsed")
    os.makedirs(raw_folder, exist_ok=True)
    os.makedirs(parsed_folder, exist_ok=True)
    return raw_folder, parsed_folder

def rename_and_move_files(source_dir, raw_folder, csv_files, json_files, participant_num, emotibit_num, week_num, day_num):
    """Rename files to P#E#_W#D#_REC#-2_iso format and move to Raw folder"""
    moved_files = []
    
    for i, (csv_file, json_file) in enumerate(zip(csv_files, json_files), 1):
        # Extract date from filename (YYYY-MM-DD format)
        iso_date = csv_file[:10]  # First 10 characters are YYYY-MM-DD
        new_name = f"P{participant_num}E{emotibit_num}_W{week_num}D{day_num}_REC{i}-2_{iso_date}"
        
        # Copy and rename CSV and JSON files
        shutil.copy2(os.path.join(source_dir, csv_file), os.path.join(raw_folder, f"{new_name}.csv"))
        shutil.copy2(os.path.join(source_dir, json_file), os.path.join(raw_folder, f"{new_name}_info.json"))
        
        moved_files.append((os.path.join(raw_folder, f"{new_name}.csv"), new_name))
    
    return moved_files

def run_parser(parser_exe_path, csv_file_path, output_folder):
    """Run EmotiBit DataParser.exe on a CSV file with output directory"""
    csv_filename = os.path.basename(csv_file_path)
    print(f"Running parser on: {csv_filename}")
    
    # Use the command format from your working code
    cmd = [parser_exe_path, csv_file_path, "-o", output_folder]
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    print(f"Parser output: {result.stdout}")
    if result.stderr:
        print(f"Parser errors: {result.stderr}")
    
    if result.returncode == 0:
        print(f"Successfully parsed {csv_filename}")
    else:
        print(f"Parser returned error code {result.returncode}")

def organize_parsed_files(raw_folder, parsed_folder, rec_name):
    """Move parsed datastream files to Parsed/rec_name/ subfolder"""
    rec_parsed_folder = os.path.join(parsed_folder, rec_name)
    os.makedirs(rec_parsed_folder, exist_ok=True)
    
    # Move all parsed files (timestamp_DATASTREAM.csv pattern) to rec subfolder
    for file in os.listdir(raw_folder):
        if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d+_[A-Z]+\.csv', file):
            shutil.move(os.path.join(raw_folder, file), os.path.join(rec_parsed_folder, file))

def main():
    # Directory containing your raw files
    source_dir = input("Enter source directory for raw files (or press Enter for current directory): ").strip()
    if not source_dir:
        source_dir = "."
    
    # Output directory where everything will be saved
    output_dir = input("Enter output directory where you want everything saved (or press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."
    
    parser_exe_path = "C:/Path/To/EmotiBit/DataParser.exe"  # Update this path
    
    # Get user input for numbers
    participant_num, emotibit_num, week_num, day_num = get_user_input()
    
    # Find raw files and setup folders
    csv_files, json_files = find_raw_files(source_dir)
    raw_folder, parsed_folder = setup_folders(output_dir)
    
    # Process files: rename, move, parse, organize
    moved_files = rename_and_move_files(source_dir, raw_folder, csv_files, json_files, 
                                      participant_num, emotibit_num, week_num, day_num)
    
    for csv_path, rec_name in moved_files:
        # Create subfolder for this recording's parsed files
        rec_parsed_folder = os.path.join(parsed_folder, rec_name)
        os.makedirs(rec_parsed_folder, exist_ok=True)
        
        # Run parser with output going directly to the subfolder
        run_parser(parser_exe_path, csv_path, rec_parsed_folder)

if __name__ == "__main__":
    main()
