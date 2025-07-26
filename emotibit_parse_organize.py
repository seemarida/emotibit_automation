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
    """Find ALL CSV and JSON files sorted by timestamp"""
    # Updated to match 6-digit microseconds format like: 2025-07-21_16-51-58-669857.csv
    csv_files = sorted([f for f in os.listdir(source_dir) if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\.csv', f)])
    json_files = sorted([f for f in os.listdir(source_dir) if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}_info\.json', f)])
   
    print(f"Found {len(csv_files)} CSV files: {csv_files}")
    print(f"Found {len(json_files)} JSON files: {json_files}")
   
    # Return ALL files, not just first 2
    return csv_files, json_files




def setup_folders(output_dir):
    """Create Raw and Parsed folders if they don't exist"""
    raw_folder = os.path.join(output_dir, "Raw")
    parsed_folder = os.path.join(output_dir, "Parsed")
    os.makedirs(raw_folder, exist_ok=True)
    os.makedirs(parsed_folder, exist_ok=True)
    return raw_folder, parsed_folder




def copy_raw_files(source_dir, raw_folder, csv_files, json_files):
    """Copy original files to Raw folder WITHOUT renaming them"""
    copied_files = []
   
    print("Copying raw files to Raw folder (preserving original names)...")
   
    for csv_file in csv_files:
        # Copy CSV file with original name
        shutil.copy2(os.path.join(source_dir, csv_file), os.path.join(raw_folder, csv_file))
        print(f"  Copied: {csv_file}")
        copied_files.append(os.path.join(raw_folder, csv_file))
   
    for json_file in json_files:
        # Copy JSON file with original name  
        shutil.copy2(os.path.join(source_dir, json_file), os.path.join(raw_folder, json_file))
        print(f"  Copied: {json_file}")
   
    return copied_files




def create_recording_folders(parsed_folder, csv_files, participant_num, emotibit_num, week_num, day_num):
    """Create recording folders based on actual number of CSV files found"""
    recording_folders = []
   
    for i, csv_file in enumerate(csv_files, 1):
        # Extract date from filename (YYYY-MM-DD format)
        iso_date = csv_file[:10]  # First 10 characters are YYYY-MM-DD
        folder_name = f"P{participant_num}E{emotibit_num}_W{week_num}D{day_num}_REC{i}-{len(csv_files)}_{iso_date}"
       
        folder_path = os.path.join(parsed_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
       
        recording_folders.append((folder_path, csv_file, folder_name))
        print(f"Created recording folder: {folder_name}")
   
    return recording_folders




def run_parser(parser_exe_path, csv_file_path, output_folder):
    """Run EmotiBit DataParser.exe on a CSV file with output directory"""
    if not os.path.exists(parser_exe_path):
        print(f"ERROR: Parser executable not found at {parser_exe_path}")
        return False
   
    csv_filename = os.path.basename(csv_file_path)
    print(f"Running parser on: {csv_filename}")
    print(f"Output folder: {output_folder}")
   
    try:
        # Use string format with shell=True and quotes for paths with spaces
        cmd = f'"{parser_exe_path}" "{csv_file_path}" -o "{output_folder}"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=300)
       
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
       
        if result.returncode == 0:
            print(f"✓ Successfully parsed {csv_filename}")
            return True
        else:
            print(f"✗ Parser failed with return code {result.returncode}")
            return False
           
    except Exception as e:
        print(f"Exception running parser: {str(e)}")
        return False




def organize_parsed_files(recording_folder, raw_folder, expected_csv_name):
    """Move parsed datastream files from Raw folder to the correct Parsed recording folder"""
    print(f"Looking for parsed files to move to: {os.path.basename(recording_folder)}")
   
    # Check both the raw folder and the recording folder for parsed files
    locations_to_check = [raw_folder, recording_folder]
   
    moved_files = []
   
    for location in locations_to_check:
        if not os.path.exists(location):
            continue
           
        files_in_location = os.listdir(location)
        print(f"Files in {os.path.basename(location)}: {files_in_location}")
       
        # Look for parsed files: anything that ends with _LETTERS.csv
        for file in files_in_location:
            if re.match(r'.*_.*\.csv$', file) and not re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\.csv$', file):
                expected_timestamp = expected_csv_name[:19] # Get YYYY-MM-DD_HH-MM-SS part
                if file.startswith(expected_timestamp):
                    source_path = os.path.join(location, file)
                    dest_path = os.path.join(recording_folder, file)
               
                # Only move if it's not already in the recording folder
                if location != recording_folder:
                    print(f"Moving parsed file: {file}")
                    print(f"  From: {location}")
                    print(f"  To: {recording_folder}")
                    shutil.move(source_path, dest_path)
                    moved_files.append(file)
                else:
                    print(f"Parsed file already in correct location: {file}")
                    moved_files.append(file)
   
    if moved_files:
        print(f"Found/moved {len(moved_files)} parsed datastream files: {moved_files}")
    else:
        print("No parsed datastream files found")
       
        # Debug: List all files in raw folder to see what the parser actually created
        print("DEBUG: All files in Raw folder after parsing:")
        if os.path.exists(raw_folder):
            all_raw_files = os.listdir(raw_folder)
            for file in all_raw_files:
                print(f"  {file}")
       
        # Debug: List all files in recording folder
        print("DEBUG: All files in recording folder:")
        if os.path.exists(recording_folder):
            all_recording_files = os.listdir(recording_folder)
            for file in all_recording_files:
                print(f"  {file}")
   
    return moved_files




def main():
    print("=== EmotiBit File Processor (Fixed Version) ===\n")
   
    # Directory containing your raw files
    source_dir = input("Enter source directory for raw files (or press Enter for current directory): ").strip()
    if not source_dir:
        source_dir = "."
   
    # Output directory where everything will be saved
    output_dir = input("Enter output directory where you want everything saved (or press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."
   
    parser_exe_path = r"C:\Program Files\EmotiBit\EmotiBit DataParser\EmotiBitDataParser.exe"
   
    # Get user input for numbers
    participant_num, emotibit_num, week_num, day_num = get_user_input()
   
    # Find raw files and setup folders
    csv_files, json_files = find_raw_files(source_dir)
   
    if not csv_files:
        print("ERROR: No CSV files found!")
        return
   
    if len(csv_files) != len(json_files):
        print(f"WARNING: Found {len(csv_files)} CSV files but {len(json_files)} JSON files")
   
    raw_folder, parsed_folder = setup_folders(output_dir)
   
    # Step 1: Copy original files to Raw folder (preserve names)
    copied_csv_files = copy_raw_files(source_dir, raw_folder, csv_files, json_files)
   
    # Step 2: Create recording folders in Parsed folder
    recording_folders = create_recording_folders(parsed_folder, csv_files, participant_num, emotibit_num, week_num, day_num)
   
    # Step 3: Run parser for each CSV file
    for (recording_folder, original_csv_name, folder_name), copied_csv_path in zip(recording_folders, copied_csv_files):
        print(f"\n{'='*50}")
        print(f"Processing: {folder_name}")
        print(f"{'='*50}")
       
        # Run parser with output going directly to the recording folder
        success = run_parser(parser_exe_path, copied_csv_path, recording_folder)
       
        if success:
            # Move parsed files from Raw folder to recording folder
            moved_files = organize_parsed_files(recording_folder, raw_folder, original_csv_name)
            if moved_files:
                print(f"Successfully processed {original_csv_name} - moved {len(moved_files)} parsed files")
            else:
                print(f"Parser ran successfully for {original_csv_name}, but no parsed files found to move")
        else:
            print(f"Failed to process {original_csv_name}")
   
    print(f"\n{'='*50}")
    print("SUMMARY:")
    print(f"{'='*50}")
    print(f"Raw files (original names): {raw_folder}")
    print(f"Parsed files (by recording): {parsed_folder}")
    for _, _, folder_name in recording_folders:
        print(f"  - {folder_name}")




if __name__ == "__main__":
    main()








