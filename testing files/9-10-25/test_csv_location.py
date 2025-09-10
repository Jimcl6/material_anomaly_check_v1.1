print("Testing CSV file locations...\n")

# Test different possible locations for the PICompiled directory
base_paths = [
    r"\\\\192.168.2.19\\ai_team\\AI Program\\Outputs",
    r"\\\\192.168.2.19\\ai_team\\AI Program",
    r"\\\\192.168.2.19\\ai_team"
]

# Possible subdirectories where CSVs might be located
subdirs = [
    "PICompiled",
    "Outputs",
    "AI ANALYSIS DATA",
    "AI ANALYSIS RESULET"
]

def find_csv_files(path):
    """Find CSV files in the given path"""
    try:
        if not os.path.exists(path):
            return []
            
        items = os.listdir(path)
        csv_files = [f for f in items if f.lower().endswith('.csv')]
        
        # If no CSV files found, check subdirectories
        if not csv_files:
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    csv_files = find_csv_files(full_path)
                    if csv_files:
                        return csv_files
        
        return csv_files
    except Exception as e:
        print(f"  - Error searching {path}: {e}")
        return []

import os

print("Searching for CSV files in possible locations...\n")

found_csvs = False

for base_path in base_paths:
    print(f"Checking base path: {base_path}")
    
    # Check the base path first
    if os.path.exists(base_path):
        print(f"  - Path exists")
        
        # Check for CSV files directly in this directory
        csv_files = find_csv_files(base_path)
        if csv_files:
            print(f"  - Found {len(csv_files)} CSV files in this directory")
            for f in csv_files[:5]:  # Show first 5 files
                print(f"    - {f}")
            if len(csv_files) > 5:
                print(f"    - ... and {len(csv_files) - 5} more")
            found_csvs = True
        
        # Check subdirectories
        try:
            items = os.listdir(base_path)
            for item in items:
                full_path = os.path.join(base_path, item)
                if os.path.isdir(full_path):
                    print(f"\nChecking subdirectory: {full_path}")
                    csv_files = find_csv_files(full_path)
                    if csv_files:
                        print(f"  - Found {len(csv_files)} CSV files in this directory")
                        for f in csv_files[:5]:  # Show first 5 files
                            print(f"    - {f}")
                        if len(csv_files) > 5:
                            print(f"    - ... and {len(csv_files) - 5} more")
                        found_csvs = True
        except Exception as e:
            print(f"  - Error listing directory: {e}")
    else:
        print(f"  - Path does not exist or is not accessible")
    
    print("\n" + "-"*80 + "\n")

if not found_csvs:
    print("No CSV files found in any of the checked locations.")
    print("Please verify the correct path to the PICompiled directory.")

input("\nPress Enter to exit...")
