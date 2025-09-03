import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def create_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def debug_rod_blk_data():
    """Debug Rod_Blk data availability in the database"""
    connection = create_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== DEBUGGING ROD_BLK DATA AVAILABILITY ===")
        
        # 1. Check process2_data table structure
        print("\n1. Checking process2_data table structure...")
        cursor.execute("DESCRIBE process2_data")
        columns = cursor.fetchall()
        rod_blk_columns = [col['Field'] for col in columns if 'Rod_Blk' in col['Field'] or 'rod' in col['Field'].lower()]
        print(f"Rod_Blk related columns in process2_data: {rod_blk_columns}")
        
        # 2. Check for any Rod_Blk data in process2_data
        print("\n2. Checking for Rod_Blk data in process2_data...")
        for col in rod_blk_columns:
            cursor.execute(f"SELECT COUNT(*) as count FROM process2_data WHERE {col} IS NOT NULL AND {col} != ''")
            result = cursor.fetchone()
            print(f"  {col}: {result['count']} non-null records")
        
        # 3. Check specific Process S/N 96 data
        print("\n3. Checking Process S/N 96 data...")
        cursor.execute("SELECT * FROM process2_data WHERE Process_2_S_N = '96' LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            print(f"Found {len(rows)} records for Process S/N 96")
            for i, row in enumerate(rows):
                print(f"  Record {i+1}:")
                for key, value in row.items():
                    if 'Rod_Blk' in key or value is not None:
                        print(f"    {key}: {value}")
        else:
            print("No records found for Process S/N 96")
        
        # 4. Check date range in process2_data
        print("\n4. Checking date range in process2_data...")
        cursor.execute("SELECT MIN(Process_2_DATE) as min_date, MAX(Process_2_DATE) as max_date FROM process2_data")
        result = cursor.fetchone()
        print(f"Date range: {result['min_date']} to {result['max_date']}")
        
        # 5. Check for 2025-07-11 data
        print("\n5. Checking for 2025-07-11 data...")
        cursor.execute("SELECT Process_2_S_N, Process_2_DATE FROM process2_data WHERE Process_2_DATE = '2025-07-11' LIMIT 10")
        rows = cursor.fetchall()
        if rows:
            print(f"Found {len(rows)} records for 2025-07-11:")
            for row in rows:
                print(f"  Process S/N: {row['Process_2_S_N']}, Date: {row['Process_2_DATE']}")
        else:
            print("No records found for 2025-07-11")
        
        # 6. Check alternative approaches - look for Rod_Blk data in database_data
        print("\n6. Checking Rod_Blk data in database_data table...")
        cursor.execute("DESCRIBE database_data")
        columns = cursor.fetchall()
        rod_blk_db_columns = [col['Field'] for col in columns if 'Rod_Blk' in col['Field']]
        print(f"Rod_Blk columns in database_data: {len(rod_blk_db_columns)} columns")
        if rod_blk_db_columns:
            print(f"Sample Rod_Blk columns: {rod_blk_db_columns[:5]}")
        
        # 7. Check rdb5200200_checksheet table
        print("\n7. Checking rdb5200200_checksheet table...")
        cursor.execute("SELECT COUNT(*) as count FROM rdb5200200_checksheet")
        result = cursor.fetchone()
        print(f"Total records in rdb5200200_checksheet: {result['count']}")
        
        cursor.execute("SELECT DISTINCT Prod_Date FROM rdb5200200_checksheet ORDER BY Prod_Date DESC LIMIT 10")
        rows = cursor.fetchall()
        print(f"Recent Prod_Date values: {[row['Prod_Date'] for row in rows]}")
        
        # 8. Check rd05200200_inspection table
        print("\n8. Checking rd05200200_inspection table...")
        cursor.execute("SELECT COUNT(*) as count FROM rd05200200_inspection")
        result = cursor.fetchone()
        print(f"Total records in rd05200200_inspection: {result['count']}")
        
        cursor.execute("SELECT DISTINCT Date FROM rd05200200_inspection ORDER BY Date DESC LIMIT 10")
        rows = cursor.fetchall()
        print(f"Recent inspection dates: {[row['Date'] for row in rows]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error during debugging: {e}")
        if connection:
            connection.close()

if __name__ == "__main__":
    debug_rod_blk_data()
