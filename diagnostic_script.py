import sys
import os
import platform
from datetime import datetime

def write_to_file(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to {filename}: {e}")
        return False

def check_python_environment():
    result = []
    result.append("=== Python Environment ===")
    result.append(f"Python Version: {sys.version}")
    result.append(f"Executable: {sys.executable}")
    result.append(f"Platform: {platform.platform()}")
    result.append(f"Current Directory: {os.getcwd()}")
    return "\n".join(result)

def check_file_access():
    result = ["\n=== File System Access ==="]
    test_paths = [
        r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled",
        os.path.join(os.getcwd(), 'test_file.txt')
    ]
    
    for path in test_paths:
        result.append(f"\nChecking: {path}")
        try:
            exists = os.path.exists(path)
            result.append(f"  Exists: {exists}")
            
            if exists:
                if os.path.isfile(path):
                    result.append(f"  Size: {os.path.getsize(path)} bytes")
                else:
                    files = os.listdir(path)
                    result.append(f"  Contains {len(files)} items")
                    if files:
                        result.append("  First 5 items:")
                        for f in files[:5]:
                            result.append(f"    - {f}")
        except Exception as e:
            result.append(f"  Error: {str(e)}")
    
    return "\n".join(result)

def check_database_connection():
    result = ["\n=== Database Connection Test ==="]
    
    # Test if mysql.connector is installed
    try:
        import mysql.connector
        result.append("✓ mysql.connector is installed")
        
        # Test database connection
        try:
            conn = mysql.connector.connect(
                host='192.168.2.148',
                user='hpi.python',
                password='hpi.python',
                database='fc_1_data_db',
                connection_timeout=5
            )
            
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT DATABASE(), USER(), VERSION()")
                db_info = cursor.fetchone()
                
                result.append("✓ Successfully connected to database")
                result.append(f"  - Database: {db_info[0]}")
                result.append(f"  - User: {db_info[1]}")
                result.append(f"  - MySQL Version: {db_info[2]}")
                
                # Check for required tables
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                result.append(f"\nFound {len(tables)} tables in the database")
                
                # Check for required tables
                required_tables = [
                    'process1_data', 'process2_data', 'process3_data',
                    'process4_data', 'process5_data', 'process6_data',
                    'database_data', 'fm05000102_inspection', 'em0580106p_inspection',
                    'em0580107p_inspection', 'csb6400802_inspection', 'rd05200200_inspection',
                    'df06600600_inspection'
                ]
                
                missing_tables = [t for t in required_tables if t not in tables]
                
                if missing_tables:
                    result.append("\n⚠️  Missing required tables:")
                    for table in missing_tables:
                        result.append(f"  - {table}")
                else:
                    result.append("\n✓ All required tables are present")
                
                cursor.close()
                conn.close()
                
        except Exception as e:
            result.append(f"✗ Database connection failed: {e}")
            
    except ImportError:
        result.append("✗ mysql.connector is not installed")
    
    return "\n".join(result)

def main():
    output = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output.append(f"Diagnostic Report - {timestamp}")
    output.append("=" * 80)
    
    # Run checks
    output.append(check_python_environment())
    output.append(check_file_access())
    output.append(check_database_connection())
    
    # Save to file
    output_file = 'diagnostic_report.txt'
    if write_to_file(output_file, "\n\n".join(output)):
        print(f"Diagnostic report saved to {output_file}")
    else:
        print("Error: Could not save diagnostic report")
    
    # Also print to console
    print("\n" + "\n".join(output))

if __name__ == "__main__":
    main()
