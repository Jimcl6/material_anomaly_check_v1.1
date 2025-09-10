import mysql.connector

def test_query():
    try:
        # Database connection parameters
        db_config = {
            'host': '192.168.2.148',
            'user': 'hpi.python',
            'password': 'hpi.python',
            'database': 'fc_1_data_db'
        }
        
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Test query 1: Check for the specific S/N
        print("\n=== Testing with S/N = '43' ===")
        cursor.execute("""
            SELECT Process_1_S_N, Process_1_DATE, Process_1_Em2p, Process_1_Em3p 
            FROM process1_data 
            WHERE Process_1_S_N = '43' 
            LIMIT 5
        """)
        print(f"Found {cursor.rowcount} rows with S/N = '43'")
        for row in cursor.fetchall():
            print(row)
        
        # Test query 2: Check for the specific date
        print("\n=== Testing with DATE = '2025-09-10' ===")
        cursor.execute("""
            SELECT Process_1_S_N, Process_1_DATE, Process_1_Em2p, Process_1_Em3p 
            FROM process1_data 
            WHERE Process_1_DATE = '2025-09-10' 
            LIMIT 5
        """)
        print(f"Found {cursor.rowcount} rows with DATE = '2025-09-10'")
        for row in cursor.fetchall():
            print(row)
            
        # Test query 3: Check recent records to see the format
        print("\n=== Checking recent records ===")
        cursor.execute("""
            SELECT Process_1_S_N, Process_1_DATE, Process_1_Em2p, Process_1_Em3p 
            FROM process1_data 
            ORDER BY Process_1_DATE DESC, Process_1_DateTime DESC 
            LIMIT 5
        """)
        print("Most recent records:")
        for row in cursor.fetchall():
            print(row)
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_query()
