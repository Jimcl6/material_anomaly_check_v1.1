import sys
import os

def main():
    print("Simple Environment Check")
    print("======================")
    
    # Python info
    print(f"\nPython Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Check required packages
    packages = ['pandas', 'numpy', 'mysql.connector', 'sqlalchemy', 'openpyxl', 'xlrd']
    
    print("\nChecking installed packages:")
    for pkg in packages:
        try:
            __import__(pkg)
            version = sys.modules[pkg].__version__
            print(f"✓ {pkg}: {version}")
        except ImportError:
            print(f"✗ {pkg}: Not installed")
        except AttributeError:
            print(f"✓ {pkg}: Installed (version unknown)")
    
    # Check file access
    print("\nChecking file access:")
    test_dir = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
    try:
        if os.path.exists(test_dir):
            print(f"✓ Directory exists: {test_dir}")
            files = os.listdir(test_dir)
            csv_files = [f for f in files if f.lower().endswith('.csv')]
            print(f"  Found {len(csv_files)} CSV files")
            if csv_files:
                print(f"  First file: {csv_files[0]}")
        else:
            print(f"✗ Directory not found: {test_dir}")
    except Exception as e:
        print(f"✗ Error accessing directory: {e}")
    
    # Check database connection
    print("\nTesting database connection...")
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='192.168.2.148',
            user='hpi.python',
            password='hpi.python',
            database='fc_1_data_db',
            connection_timeout=5
        )
        print("✓ Successfully connected to database")
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"  Found {len(tables)} tables")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
