import os
import sys

def test_database():
    print("Testing database connection...")
    try:
        import mysql.connector
        print("✓ mysql.connector is installed")
        
        try:
            conn = mysql.connector.connect(
                host='192.168.2.148',
                user='hpi.python',
                password='hpi.python',
                database='fc_1_data_db',
                connection_timeout=5
            )
            print("✓ Successfully connected to database")
            
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE(), USER(), VERSION()")
            db_info = cursor.fetchone()
            print(f"  - Database: {db_info[0]}")
            print(f"  - User: {db_info[1]}")
            print(f"  - MySQL Version: {db_info[2]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
            
    except ImportError:
        print("✗ mysql.connector is not installed")
        return False

def test_csv_access():
    print("\nTesting CSV file access...")
    test_path = r"\\\\192.168.2.19\\ai_team\\AI Program\\Outputs\\PICompiled"
    
    try:
        exists = os.path.exists(test_path)
        print(f"Path exists: {exists}")
        
        if exists:
            files = os.listdir(test_path)
            csv_files = [f for f in files if f.lower().endswith('.csv')]
            print(f"Found {len(csv_files)} CSV files")
            
            if csv_files:
                latest_csv = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(test_path, f)))
                print(f"Latest CSV file: {latest_csv}")
                return True
            else:
                print("No CSV files found in the directory")
                return False
        else:
            print("CSV directory does not exist or is not accessible")
            return False
            
    except Exception as e:
        print(f"Error accessing CSV directory: {e}")
        return False

def save_results():
    # Redirect stdout to capture all output
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        db_success = test_database()
        csv_success = test_csv_access()
    
    # Get the captured output
    output = f.getvalue()
    
    # Write to file
    with open('test_results.txt', 'w') as f:
        f.write("=== Test Results ===\n")
        f.write(output)
        f.write("\n=== Summary ===\n")
        f.write(f"Database connection: {'SUCCESS' if db_success else 'FAILED'}\n")
        f.write(f"CSV access: {'SUCCESS' if csv_success else 'FAILED'}\n")
    
    # Also print to console
    print("\n=== Test Complete ===")
    print("Results have been saved to test_results.txt")
    print("=== Summary ===")
    print(f"Database connection: {'SUCCESS' if db_success else 'FAILED'}")
    print(f"CSV access: {'SUCCESS' if csv_success else 'FAILED'}")

if __name__ == "__main__":
    save_results()
