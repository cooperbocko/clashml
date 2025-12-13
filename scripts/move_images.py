import os
import shutil
from pathlib import Path

# --- Configuration ---
# Set the directory where the search should begin (recursively)
SOURCE_DIR = Path('./debug')

# Set the directory where the matching files will be moved
# This script will create this directory if it doesn't exist.
DESTINATION_DIR = Path('./export')

# Set the prefix string to look for
PREFIX = "elixr"

def move_files_by_prefix(source_dir: Path, destination_dir: Path, prefix: str):
    """
    Recursively searches a source directory for files whose names start with a
    given prefix, and moves them to the specified destination directory.
    """
    print(f"Starting file scan in: {source_dir.resolve()}")

    # 1. Ensure the destination directory exists
    try:
        destination_dir.mkdir(parents=True, exist_ok=True)
        print(f"Destination directory ensured: {destination_dir.resolve()}")
    except Exception as e:
        print(f"Error creating destination directory {destination_dir}: {e}")
        return

    # Counter for moved files
    moved_count = 0

    # 2. Walk through the source directory and its subdirectories
    # os.walk yields (dirpath, dirnames, filenames)
    for root, _, files in os.walk(source_dir):
        current_dir = Path(root)
        
        # Iterate over all files in the current directory
        for filename in files:
            # 3. Check if the filename starts with the specified prefix (case-insensitive)
            if filename.lower().startswith(prefix.lower()):
                source_file_path = current_dir / filename
                destination_file_path = destination_dir / filename
                
                print(f"\nFound match: {source_file_path}")

                # 4. Handle potential file conflicts in the destination
                if destination_file_path.exists():
                    print(f"File already exists in destination: {destination_file_path.name}. Skipping move.")
                    continue
                
                # 5. Move the file
                try:
                    shutil.move(source_file_path, destination_file_path)
                    moved_count += 1
                    print(f"SUCCESS: Moved to {destination_file_path.resolve()}")
                except Exception as e:
                    print(f"ERROR moving file {source_file_path.name}: {e}")

    print("\n--- Summary ---")
    print(f"Search completed.")
    print(f"Total files moved: {moved_count}")
    
move_files_by_prefix(SOURCE_DIR, DESTINATION_DIR, PREFIX)