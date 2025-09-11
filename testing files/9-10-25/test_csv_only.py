print("Testing CSV file access...")
test_path = r"\\\\192.168.2.19\\ai_team\\AI Program\\Outputs\\PICompiled"

try:
    import os
    exists = os.path.exists(test_path)
    print(f"Path exists: {exists}")
    
    if exists:
        files = os.listdir(test_path)
        csv_files = [f for f in files if f.lower().endswith('.csv')]
        print(f"Found {len(csv_files)} CSV files")
        
        if csv_files:
            # Sort files by modification time (newest first)
            csv_files.sort(key=lambda f: os.path.getmtime(os.path.join(test_path, f)), reverse=True)
            
            print("\nLatest 5 CSV files:")
            for i, f in enumerate(csv_files[:5], 1):
                file_path = os.path.join(test_path, f)
                mtime = os.path.getmtime(file_path)
                from datetime import datetime
                print(f"{i}. {f} (Modified: {datetime.fromtimestamp(mtime)})")
        else:
            print("No CSV files found in the directory")
    else:
        print("CSV directory does not exist or is not accessible")
        
except Exception as e:
    print(f"Error accessing CSV directory: {e}")

input("\nPress Enter to exit...")
