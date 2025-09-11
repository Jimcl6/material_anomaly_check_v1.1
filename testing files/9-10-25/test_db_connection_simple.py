import sys
import os

def main():
    output = []
    
    # Basic Python environment
    output.append("=== Python Environment ===")
    output.append(f"Python Version: {sys.version}")
    output.append(f"Executable: {sys.executable}")
    output.append(f"Working Directory: {os.getcwd()}")
    
    # Test file writing
    output.append("\n=== File System Test ===")
    try:
        with open('test_output.txt', 'w') as f:
            f.write('Test file content')
        output.append("✓ Successfully wrote to test_output.txt")
    except Exception as e:
        output.append(f"✗ Error writing to file: {e}")
    
    # Test database connection
    output.append("\n=== Database Connection Test ===")
    try:
        import mysql.connector
        output.append("✓ mysql.connector is installed")
        
        try:
            conn = mysql.connector.connect(
                host='192.168.2.148',
                user='hpi.python',
                password='hpi.python',
                database='fc_1_data_db',
                connection_timeout=5
            )
            output.append("✓ Successfully connected to database")
            
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE(), USER(), VERSION()")
            db_info = cursor.fetchone()
            output.append(f"  - Database: {db_info[0]}")
            output.append(f"  - User: {db_info[1]}")
            output.append(f"  - MySQL Version: {db_info[2]}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            output.append(f"✗ Database connection failed: {e}")
    
    except ImportError:
        output.append("✗ mysql.connector is not installed")
    
    # Write all output to file
    output_file = 'connection_test_results.txt'
    with open(output_file, 'w') as f:
        f.write("\n".join(output))
    
    print(f"Test complete. Results written to {output_file}")

if __name__ == "__main__":
    main()
