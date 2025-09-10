import mysql.connector
from mysql.connector import Error

def check_table_structure():
    """Check the structure of specific tables"""
    tables_to_check = [
        'rdb5200200_inspection',
        'dfb6600600_inspection'
    ]
    
    conn = None
    try:
        conn = mysql.connector.connect(
            host='192.168.2.148',
            user='hpi.python',
            password='hpi.python',
            database='fc_1_data_db',
            connection_timeout=5
        )
        
        cursor = conn.cursor()
        
        for table in tables_to_check:
            print(f"\nChecking table: {table}")
            print("=" * (len(table) + 12))
            
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if not cursor.fetchone():
                print(f"Table {table} does not exist")
                continue
                
            # Get table structure
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            
            print(f"Table structure ({len(columns)} columns):")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"\nRow count: {count:,}")
            
            # Show first few rows if table is not empty
            if count > 0:
                print("\nFirst 3 rows (first 5 columns):")
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"  - {row[:5]}{'...' if len(row) > 5 else ''}")
        
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    check_table_structure()
    input("\nPress Enter to exit...")
