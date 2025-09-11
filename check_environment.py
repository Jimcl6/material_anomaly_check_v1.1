import os
import sys
import platform
import subprocess
import importlib.util

def print_header(title):
    print("\n" + "="*80)
    print(f"{title.upper()}")
    print("="*80)

def check_python_environment():
    print_header("Python Environment")
    print(f"Python Version: {platform.python_version()}")
    print(f"Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Check required packages
    print("\nChecking required packages:")
    packages = [
        'pandas',
        'numpy',
        'mysql.connector',
        'sqlalchemy',
        'openpyxl',
        'xlrd'
    ]
    
    for pkg in packages:
        spec = importlib.util.find_spec(pkg)
        if spec is not None:
            version = importlib.import_module(pkg).__version__
            print(f"✓ {pkg}: {version}")
        else:
            print(f"✗ {pkg}: Not installed")

def check_network_resources():
    print_header("Network Resources")
    
    # Check CSV directory
    csv_dir = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
    print(f"Checking CSV directory: {csv_dir}")
    
    try:
        if os.path.exists(csv_dir):
            print("✓ Directory exists")
            try:
                files = os.listdir(csv_dir)
                csv_files = [f for f in files if f.lower().endswith('.csv')]
                print(f"Found {len(csv_files)} CSV files")
                
                if csv_files:
                    print("\nCSV files (first 5):")
                    for file in csv_files[:5]:
                        file_path = os.path.join(csv_dir, file)
                        size = os.path.getsize(file_path) / 1024  # KB
                        mtime = os.path.getmtime(file_path)
                        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"- {file} ({size:.2f} KB, Modified: {mtime_str})")
                    
                    # Try to read the most recent CSV
                    latest_csv = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(csv_dir, f)))
                    print(f"\nTesting read access to: {latest_csv}")
                    try:
                        import pandas as pd
                        df = pd.read_csv(os.path.join(csv_dir, latest_csv), nrows=5)
                        print("✓ Successfully read CSV file")
                        print("\nFirst 5 rows:")
                        print(df.head())
                    except Exception as e:
                        print(f"✗ Error reading CSV: {e}")
                
            except Exception as e:
                print(f"✗ Error listing directory: {e}")
        else:
            print("✗ Directory does not exist or is not accessible")
    except Exception as e:
        print(f"✗ Error accessing directory: {e}")

def check_database_connection():
    print_header("Database Connection Test")
    
    config = {
        'host': '192.168.2.148',
        'user': 'hpi.python',
        'password': 'hpi.python',
        'database': 'fc_1_data_db',
        'connection_timeout': 5
    }
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        print("Attempting to connect to database...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✓ Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            print(f"✓ Connected to database: {cursor.fetchone()[0]}")
            
            # Check required tables
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"\nFound {len(tables)} tables in the database")
            
            # Check for required tables
            required_tables = [
                'process1_data', 'process2_data', 'process3_data',
                'process4_data', 'process5_data', 'process6_data',
                'database_data', 'fm05000102_inspection', 'em0580106p_inspection',
                'em0580107p_inspection', 'csb6400802_inspection', 'rdb5200200_inspection',
                'dfb6600600_inspection'
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print("\n⚠️  Missing required tables:")
                for table in missing_tables:
                    print(f"  - {table}")
            else:
                print("\n✓ All required tables are present")
            
            cursor.close()
            connection.close()
            
    except ImportError:
        print("✗ mysql-connector-python is not installed")
    except Error as e:
        print(f"✗ Database connection failed: {e}")
        if e.errno == 2003:
            print("  - Could not connect to the database server")
            print("  - Check if the server is running and accessible")
        elif e.errno == 1045:
            print("  - Access denied for the provided credentials")
            print("  - Please verify the username and password")
        elif e.errno == 1049:
            print("  - The specified database does not exist")

if __name__ == "__main__":
    check_python_environment()
    check_network_resources()
    check_database_connection()
    
    print("\nEnvironment check complete. Please review the output above for any issues.")
    
    # Keep the window open if run directly on Windows
    if platform.system() == 'Windows':
        input("\nPress Enter to exit...")
