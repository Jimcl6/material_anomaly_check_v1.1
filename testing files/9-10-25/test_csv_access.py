import os
import datetime
import glob

def test_csv_access():
    """Test access to CSV files in the PICompiled directory"""
    NETWORK_DIR = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
    
    # Check if directory exists
    if not os.path.exists(NETWORK_DIR):
        print(f"✗ Directory does not exist: {NETWORK_DIR}")
        print("Please verify the network path is correct and accessible.")
        return False
    
    print(f"✓ Directory exists: {NETWORK_DIR}")
    
    # List all CSV files in the directory
    csv_files = glob.glob(os.path.join(NETWORK_DIR, 'PICompiled*.csv'))
    
    if not csv_files:
        print("✗ No CSV files found matching pattern 'PICompiled*.csv'")
        print("\nPlease check if:")
        print("1. The CSV files exist in the directory")
        print("2. You have proper read permissions")
        print("3. The files follow the naming convention 'PICompiledYYYY-MM-DD.csv'")
        return False
    
    print(f"\nFound {len(csv_files)} CSV file(s):")
    for i, file in enumerate(csv_files, 1):
        file_size = os.path.getsize(file) / 1024  # Size in KB
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {os.path.basename(file)} (Size: {file_size:.2f} KB, Modified: {mod_time})")
    
    # Try to read the most recent file
    latest_file = max(csv_files, key=os.path.getmtime)
    print(f"\nAttempting to read the most recent file: {os.path.basename(latest_file)}")
    
    try:
        import pandas as pd
        df = pd.read_csv(latest_file, nrows=5)  # Read first 5 rows as sample
        print("\n✓ Successfully read CSV file. First few rows:")
        print(df.head())
        print("\nColumn names:", list(df.columns))
        return True
        
    except Exception as e:
        print(f"✗ Error reading CSV file: {str(e)}")
        print("\nPlease check if:")
        print("1. The file is not corrupted")
        print("2. The file is not open in another program")
        print("3. You have proper read permissions")
        return False

if __name__ == "__main__":
    test_csv_access()
