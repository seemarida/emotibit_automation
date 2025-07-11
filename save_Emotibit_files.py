import os
import shutil
import subprocess
from datetime import datetime
import glob

class EmotiBitProcessor:
    def __init__(self, emotibit_num, participant_num, week_num, day_num, 
                 emotibit_parser_path, source_directory=".", output_directory="."):
        """
        Initialize the EmotiBit processor
        
        Args:
            emotibit_num (int): EmotiBit device number
            participant_num (int): Participant number
            week_num (int): Week number
            day_num (int): Day number
            emotibit_parser_path (str): Path to EmotiBit DataParser executable
            source_directory (str): Directory containing the raw files
            output_directory (str): Directory where all output will be saved
        """
        self.emotibit_num = emotibit_num
        self.participant_num = participant_num
        self.week_num = week_num
        self.day_num = day_num
        self.emotibit_parser_path = emotibit_parser_path
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.today_date = datetime.now().strftime("%m%d%Y")
        
        # Create folder structure names (directly in output directory)
        self.raw_folder_1 = os.path.join(output_directory, f"E{emotibit_num}P{participant_num}_W{week_num}D{day_num}_{self.today_date}_RAW_1")
        self.raw_folder_2 = os.path.join(output_directory, f"E{emotibit_num}P{participant_num}_W{week_num}D{day_num}_{self.today_date}_RAW_2")
        self.parsed_folder_1 = os.path.join(output_directory, f"E{emotibit_num}P{participant_num}_W{week_num}D{day_num}_{self.today_date}_PARSED_1")
        self.parsed_folder_2 = os.path.join(output_directory, f"E{emotibit_num}P{participant_num}_W{week_num}D{day_num}_{self.today_date}_PARSED_2")
    
    def create_folder_structure(self):
        """Create the raw and parsed folders directly in output directory"""
        # Create raw data folders
        os.makedirs(self.raw_folder_1, exist_ok=True)
        os.makedirs(self.raw_folder_2, exist_ok=True)
        print(f"Created raw folders: {os.path.basename(self.raw_folder_1)} and {os.path.basename(self.raw_folder_2)}")
        
        # Create parsed data folders
        os.makedirs(self.parsed_folder_1, exist_ok=True)
        os.makedirs(self.parsed_folder_2, exist_ok=True)
        print(f"Created parsed folders: {os.path.basename(self.parsed_folder_1)} and {os.path.basename(self.parsed_folder_2)}")
        
        return self.raw_folder_1, self.raw_folder_2, self.parsed_folder_1, self.parsed_folder_2
    
    def find_and_move_raw_files(self, raw_1_path, raw_2_path):
        """Find and move raw files to appropriate folders"""
        # Find RAW_1 files (CSV and JSON)
        raw_1_csv = glob.glob(os.path.join(self.source_directory, "*RAW_1*.csv"))
        raw_1_json = glob.glob(os.path.join(self.source_directory, "*RAW_1*.json"))
        
        # Find RAW_2 files (CSV and JSON)
        raw_2_csv = glob.glob(os.path.join(self.source_directory, "*RAW_2*.csv"))
        raw_2_json = glob.glob(os.path.join(self.source_directory, "*RAW_2*.json"))
        
        # Move RAW_1 files
        raw_1_files = []
        for file_list in [raw_1_csv, raw_1_json]:
            for file_path in file_list:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(raw_1_path, filename)
                shutil.copy2(file_path, dest_path)
                raw_1_files.append(dest_path)
                print(f"Moved {filename} to {os.path.basename(raw_1_path)}")
        
        # Move RAW_2 files
        raw_2_files = []
        for file_list in [raw_2_csv, raw_2_json]:
            for file_path in file_list:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(raw_2_path, filename)
                shutil.copy2(file_path, dest_path)
                raw_2_files.append(dest_path)
                print(f"Moved {filename} to {os.path.basename(raw_2_path)}")
        
        return raw_1_files, raw_2_files
    
    def create_renamed_csv_for_parsing(self, raw_files, temp_dir):
        """Create renamed CSV files for parsing (without RAW_# in filename)"""
        renamed_csv_files = []
        
        for file_path in raw_files:
            if file_path.endswith('.csv'):
                original_filename = os.path.basename(file_path)
                
                # Remove RAW_1 or RAW_2 from filename
                new_filename = original_filename.replace('_RAW_1', '').replace('_RAW_2', '')
                
                # Create renamed file in temp directory
                temp_file_path = os.path.join(temp_dir, new_filename)
                shutil.copy2(file_path, temp_file_path)
                renamed_csv_files.append(temp_file_path)
                print(f"Created renamed file for parsing: {new_filename}")
        
        return renamed_csv_files
    
    def run_emotibit_parser(self, raw_files, output_folder):
        """Run EmotiBit DataParser on renamed CSV files"""
        print(f"Running EmotiBit DataParser on files for {os.path.basename(output_folder)}")
        
        # Create temporary directory for renamed files
        temp_dir = os.path.join(os.path.dirname(output_folder), "temp_parsing")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Create renamed CSV files for parsing
            renamed_csv_files = self.create_renamed_csv_for_parsing(raw_files, temp_dir)
            
            for csv_file in renamed_csv_files:
                try:
                    print(f"Running parser command: {self.emotibit_parser_path} {csv_file} -o {output_folder}")
                    
                    # Run EmotiBit DataParser
                    # Adjust command based on your EmotiBit DataParser requirements
                    cmd = [self.emotibit_parser_path, csv_file, "-o", output_folder]
                    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                    
                    print(f"Parser output: {result.stdout}")
                    if result.stderr:
                        print(f"Parser errors: {result.stderr}")
                    
                    if result.returncode == 0:
                        print(f"Successfully parsed {os.path.basename(csv_file)}")
                        # List files in output folder to verify
                        if os.path.exists(output_folder):
                            files_created = os.listdir(output_folder)
                            print(f"Files in {os.path.basename(output_folder)}: {files_created}")
                    else:
                        print(f"Parser returned error code {result.returncode} for {os.path.basename(csv_file)}")
                        
                except Exception as e:
                    print(f"Error running parser on {csv_file}: {str(e)}")
        
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"Cleaned up temporary files")
    
    def process_all_files(self):
        """Main processing function"""
        print("Starting EmotiBit data processing...")
        print(f"Configuration: E{self.emotibit_num}P{self.participant_num}_W{self.week_num}D{self.day_num}")
        print(f"Date: {self.today_date}")
        
        # Create folder structure
        raw_1_path, raw_2_path, parsed_1_path, parsed_2_path = self.create_folder_structure()
        
        # Find and move raw files
        raw_1_files, raw_2_files = self.find_and_move_raw_files(raw_1_path, raw_2_path)
        
        # Run parser on RAW_1 files
        if raw_1_files:
            self.run_emotibit_parser(raw_1_files, parsed_1_path)
        else:
            print("No RAW_1 files found!")
        
        # Run parser on RAW_2 files
        if raw_2_files:
            self.run_emotibit_parser(raw_2_files, parsed_2_path)
        else:
            print("No RAW_2 files found!")
        
        print("Processing complete!")
        return self.output_directory


def get_user_input():
    """Get configuration from user input"""
    print("EmotiBit Data Processing Configuration")
    print("=" * 40)
    
    while True:
        try:
            emotibit_num = int(input("Enter EmotiBit device number: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            participant_num = int(input("Enter Participant number: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            week_num = int(input("Enter Week number: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            day_num = int(input("Enter Day number: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Use default path for EmotiBit DataParser executable
    parser_path = r"C:\path\to\emotibit\dataparser.exe"  # UPDATE THIS DEFAULT PATH
    
    # Directory containing your raw files
    source_dir = input("Enter source directory for raw files (or press Enter for current directory): ").strip()
    if not source_dir:
        source_dir = "."
    
    # Output directory where everything will be saved
    output_dir = input("Enter output directory where you want everything saved (or press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."
    
    return emotibit_num, participant_num, week_num, day_num, parser_path, source_dir, output_dir


def main():
    """
    Main function - Gets configuration from user input
    """
    # Get configuration from user
    emotibit_num, participant_num, week_num, day_num, parser_path, source_dir, output_dir = get_user_input()
    
    # Display configuration
    print("\n" + "=" * 40)
    print("Configuration Summary:")
    print(f"EmotiBit Number: {emotibit_num}")
    print(f"Participant Number: {participant_num}")
    print(f"Week Number: {week_num}")
    print(f"Day Number: {day_num}")
    print(f"Parser Path: {parser_path}")
    print(f"Source Directory: {source_dir}")
    print(f"Output Directory: {output_dir}")
    print("=" * 40)
    
    # Confirm before proceeding
    confirm = input("\nProceed with these settings? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Create processor instance
    processor = EmotiBitProcessor(
        emotibit_num=emotibit_num,
        participant_num=participant_num,
        week_num=week_num,
        day_num=day_num,
        emotibit_parser_path=parser_path,
        source_directory=source_dir,
        output_directory=output_dir
    )
    
    # Process all files
    output_folder = processor.process_all_files()
    print(f"\nAll files processed and saved to: {output_folder}")


if __name__ == "__main__":
    main()
