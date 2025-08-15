import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def check_table_columns():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)
    
    # Check rd05200200_inspection table structure
    print("=== rd05200200_inspection table columns ===")
    cursor.execute("DESCRIBE rd05200200_inspection")
    inspection_columns = cursor.fetchall()
    for col in inspection_columns:
        print(f"  {col['Field']} ({col['Type']})")
    
    # Check rdb5200200_checksheet table structure  
    print("\n=== rdb5200200_checksheet table columns ===")
    cursor.execute("DESCRIBE rdb5200200_checksheet")
    checksheet_columns = cursor.fetchall()
    for col in checksheet_columns:
        print(f"  {col['Field']} ({col['Type']})")
    
    # Get sample data to see actual column names
    print("\n=== Sample data from rd05200200_inspection ===")
    cursor.execute("SELECT * FROM rd05200200_inspection LIMIT 1")
    sample_inspection = cursor.fetchall()
    if sample_inspection:
        print(f"Sample row columns: {list(sample_inspection[0].keys())}")
    
    print("\n=== Sample data from rdb5200200_checksheet ===")
    cursor.execute("SELECT * FROM rdb5200200_checksheet LIMIT 1")
    sample_checksheet = cursor.fetchall()
    if sample_checksheet:
        print(f"Sample row columns: {list(sample_checksheet[0].keys())}")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    check_table_columns()
