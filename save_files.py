import os
import shutil
import subprocess
import glob
import re

def find_week_day_numbers(base_path):
    """Extract week number from largest W# folder and day number from D# folders within it"""
    week_folders = glob.glob(os.path.join(base_path, "W*"))
    week_numbers = [(int(re.search(r'W(\d+)', os.path.basename(f)).group(1)), f) for f in week_folders]
    largest_week_num, largest_week_folder = max(week_numbers)
    
    day_folders = glob.glob(os.path.join(largest_week_folder, "D*"))
    day_numbers = [int(re.search(r'D(\d+)', os.path.basename(f)).group(1)) for f in day_folders]
    
    return largest_week_num, max(day_numbers)

def get_user_input():
    """Get P#, E#, and ISO number from user"""
    participant_num = int(input("Enter participant number (P#): "))
    emotibit_num = int(input("Enter emotibit number (E#): "))
    iso_number = input("Enter ISO number: ")
    return participant_num, emotibit_num, iso_number

def find_raw_files(microsd_path):
    """Find first 2 CSV and JSON files sorted by timestamp"""
    csv_files = sorted([f for f in os.listdir(microsd_path) if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{3}\.csv', f)])
    json_files = sorted([f for f in os.listdir(microsd_path) if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{3}_info\.json', f)])
    return csv_files[:2], json_files[:2]

def setup_folders(base_path, week_num, day_num):
    """Create Raw and Parsed folders if they don't exist"""
    raw_folder = os.path.join(base_path, f"W{week_num}", f"D{day_num}", "Raw")
    parsed_folder = os.path.join(base_path, f"W{week_num}", f"D{day_num}", "Parsed")
    os.makedirs(raw_folder, exist_ok=True)
    os.makedirs(parsed_folder, exist_ok=True)
    return raw_folder, parsed_folder

def rename_and_move_files(microsd_path, raw_folder, csv_files, json_files, participant_num, emotibit_num, week_num, day_num, iso_number):
    """Rename files to P#E#_W#D#_REC#-2_iso format and move to Raw folder"""
    moved_files = []
    
    for i, (csv_file, json_file) in enumerate(zip(csv_files, json_files), 1):
        new_name = f"P{participant_num}E{emotibit_num}_W{week_num}D{day_num}_REC{i}-2_{iso_number}"
        
        # Copy and rename CSV and JSON files
        shutil.copy2(os.path.join(microsd_path, csv_file), os.path.join(raw_folder, f"{new_name}.csv"))
        shutil.copy2(os.path.join(microsd_path, json_file), os.path.join(raw_folder, f"{new_name}_info.json"))
        
        moved_files.append((os.path.join(raw_folder, f"{new_name}.csv"), new_name))
    
    return moved_files

def run_parser(parser_exe_path, csv_file_path):
    """Run EmotiBit DataParser.exe on a CSV file"""
    csv_dir = os.path.dirname(csv_file_path)
    csv_filename = os.path.basename(csv_file_path)
    subprocess.run([parser_exe_path, csv_filename], cwd=csv_dir)

def organize_parsed_files(raw_folder, parsed_folder, rec_name):
    """Move parsed datastream files to Parsed/rec_name/ subfolder"""
    rec_parsed_folder = os.path.join(parsed_folder, rec_name)
    os.makedirs(rec_parsed_folder, exist_ok=True)
    
    # Move all parsed files (timestamp_DATASTREAM.csv pattern) to rec subfolder
    for file in os.listdir(raw_folder):
        if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d+_[A-Z]+\.csv', file):
            shutil.move(os.path.join(raw_folder, file), os.path.join(rec_parsed_folder, file))

def main():
    # Get paths from user
    microsd_path = input("Enter microSD card path: ").strip()
    base_path = input("Enter base path (where W# folders are): ").strip()
    parser_exe_path = "C:/Path/To/EmotiBit/DataParser.exe"  # Update this path
    
    # Find week/day numbers and get user input
    week_num, day_num = find_week_day_numbers(base_path)
    participant_num, emotibit_num, iso_number = get_user_input()
    
    # Find raw files and setup folders
    csv_files, json_files = find_raw_files(microsd_path)
    raw_folder, parsed_folder = setup_folders(base_path, week_num, day_num)
    
    # Process files: rename, move, parse, organize
    moved_files = rename_and_move_files(microsd_path, raw_folder, csv_files, json_files, 
                                      participant_num, emotibit_num, week_num, day_num, iso_number)
    
    for csv_path, rec_name in moved_files:
        run_parser(parser_exe_path, csv_path)
        organize_parsed_files(raw_folder, parsed_folder, rec_name)

if __name__ == "__main__":
    main()