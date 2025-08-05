import mysql.connector
import pandas as pd

# Database configuration from main.py
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def explore_database_schema():
    """
    Explore the database schema to understand how material codes are stored
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== DATABASE EXPLORATION ===\n")
        
        # 1. List all tables
        print("1. Available Tables:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        print()
        
        # 2. Focus on process tables
        process_tables = [table[0] for table in tables if 'process' in table[0].lower()]
        print(f"2. Process Tables Found: {process_tables}\n")
        
        # 3. Examine schema for each process table
        for table_name in process_tables:
            print(f"3. Schema for {table_name}:")
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print("   Columns:")
            for col in columns:
                col_name, col_type, null, key, default, extra = col
                print(f"     - {col_name} ({col_type})")
            
            # 4. Sample data from each table
            print(f"\n   Sample data from {table_name}:")
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()
            
            if sample_data:
                # Get column names for display
                cursor.execute(f"DESCRIBE {table_name}")
                column_info = cursor.fetchall()
                column_names = [col[0] for col in column_info]
                
                # Display sample data
                for i, row in enumerate(sample_data):
                    print(f"     Row {i+1}:")
                    for j, value in enumerate(row):
                        if j < len(column_names):
                            print(f"       {column_names[j]}: {value}")
                    print()
            else:
                print("     No data found in this table")
            
            print("-" * 60)
        
        # 5. Look for columns that might contain material codes
        print("\n5. Analyzing Column Patterns:")
        for table_name in process_tables:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            material_related_columns = []
            for col in columns:
                col_name = col[0]
                if any(keyword in col_name.lower() for keyword in ['material', 'code', 'em', 'frame', 'rod', 'blk']):
                    material_related_columns.append(col_name)
            
            if material_related_columns:
                print(f"   {table_name} - Material-related columns:")
                for col in material_related_columns:
                    print(f"     - {col}")
            print()
        
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_database_schema()