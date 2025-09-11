import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        return mysql.connector.connect(
            host='192.168.2.148',
            user='hpi.python',
            password='hpi.python',
            database='fc_1_data_db',
            connection_timeout=5
        )
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def check_required_tables():
    required_tables = [
        'process1_data', 'process2_data', 'process3_data',
        'process4_data', 'process5_data', 'process6_data',
        'database_data', 'fm05000102_inspection', 'em0580106p_inspection',
        'em0580107p_inspection', 'csb6400802_inspection', 'rdb5200200_inspection',
        'dfb6600600_inspection'
    ]
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all tables in the database
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print("\n=== Database Schema Check ===")
        print(f"Found {len(tables)} tables in the database")
        
        # Check for required tables
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print("\n⚠️  Missing required tables:")
            for table in missing_tables:
                print(f"  - {table}")
        else:
            print("\n✓ All required tables are present")
        
        # Show table structure for required tables
        print("\n=== Table Structures ===")
        for table in required_tables:
            if table in tables:
                print(f"\nTable: {table}")
                print("-" * (len(table) + 8))
                try:
                    cursor.execute(f"DESCRIBE {table}")
                    columns = cursor.fetchall()
                    print(f"Columns ({len(columns)}):")
                    for col in columns:
                        print(f"  - {col[0]} ({col[1]})")
                except Error as e:
                    print(f"  Error describing table: {e}")
            
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    check_required_tables()
    input("\nPress Enter to exit...")
