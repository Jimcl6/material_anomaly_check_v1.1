import sys

def test_database_connection():
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
            
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT DATABASE(), USER(), VERSION()")
                db_info = cursor.fetchone()
                
                print("\n✓ Successfully connected to database")
                print(f"  - Database: {db_info[0]}")
                print(f"  - User: {db_info[1]}")
                print(f"  - MySQL Version: {db_info[2]}")
                
                # Check tables
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                print(f"\nFound {len(tables)} tables in the database")
                
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"\n✗ Database connection failed: {e}")
    
    except ImportError:
        print("✗ mysql.connector is not installed")

if __name__ == "__main__":
    # Redirect output to a file
    import os
    output_file = 'db_test_output.txt'
    with open(output_file, 'w') as f:
        sys.stdout = f
        test_database_connection()
    
    print(f"Database test complete. Check {output_file} for results.")
    
    # Also print to console
    with open(output_file, 'r') as f:
        print(f.read())
