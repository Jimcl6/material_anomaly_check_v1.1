import mysql.connector
import pandas as pd
from datetime import datetime, timedelta

def test_model_code():
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
        
        # Test 1: Check process1_data for the specific Process S/N '43'
        print("\n=== Checking process1_data for Process S/N '43' ===")
        cursor.execute("""
            SELECT Process_1_S_N, Process_1_Model_Code, Process_1_DATE, Process_1_Em2p, Process_1_Em3p 
            FROM process1_data 
            WHERE Process_1_S_N = '43'
            ORDER BY Process_1_DATE DESC, Process_1_DateTime DESC
            LIMIT 5
        """)
        print(f"Found {cursor.rowcount} rows with Process S/N = '43'")
        for row in cursor.fetchall():
            print(row)
        
        # Test 2: Check recent records in process1_data to see the format
        print("\n=== Checking recent records in process1_data ===")
        cursor.execute("""
            SELECT Process_1_S_N, Process_1_Model_Code, Process_1_DATE, Process_1_Em2p, Process_1_Em3p 
            FROM process1_data 
            ORDER BY Process_1_DATE DESC, Process_1_DateTime DESC
            LIMIT 5
        """)
        print("Most recent records in process1_data:")
        for row in cursor.fetchall():
            print(row)
        
        # Test 3: Check database_data for the model code '60CAT0213P' (from CSV)
        print("\n=== Checking database_data for Model_Code '60CAT0213P' ===")
        cursor.execute("""
            SELECT DISTINCT Model_Code, COUNT(*) as count 
            FROM database_data 
            WHERE Model_Code LIKE '%60CAT0213P%' 
            GROUP BY Model_Code
        """)
        print("Matching model codes in database_data:")
        for row in cursor.fetchall():
            print(f"Model Code: {row['Model_Code']}, Count: {row['count']}")
        
        # Test 4: Check for any records with similar model codes
        print("\n=== Checking for similar model codes in database_data ===")
        cursor.execute("""
            SELECT DISTINCT Model_Code, COUNT(*) as count 
            FROM database_data 
            WHERE Model_Code LIKE '%60CAT%' 
            GROUP BY Model_Code
            ORDER BY count DESC
            LIMIT 10
        """)
        print("Similar model codes in database_data:")
        for row in cursor.fetchall():
            print(f"Model Code: {row['Model_Code']}, Count: {row['count']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model_code()
