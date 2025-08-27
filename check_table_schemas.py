#!/usr/bin/env python3
"""
Script to check database table schemas and identify new columns in rd05200200_inspection table
"""

import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def check_table_structure(table_name):
    """Check the structure of a table to see available columns"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        cursor.close()
        connection.close()
        return columns
    except Exception as e:
        print(f"Error checking table structure for {table_name}: {e}")
        return None

def get_sample_data(table_name, limit=3):
    """Get sample data from a table"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows
    except Exception as e:
        print(f"Error getting sample data from {table_name}: {e}")
        return None

def main():
    print("=== DATABASE TABLE SCHEMA ANALYSIS ===\n")
    
    # Tables to analyze
    tables_to_check = [
        'database_data',
        'rdb5200200_checksheet', 
        'rd05200200_inspection'
    ]
    
    for table_name in tables_to_check:
        print(f"=== {table_name.upper()} TABLE ===")
        
        # Get table structure
        columns = check_table_structure(table_name)
        if columns:
            print(f"Columns in {table_name}:")
            for i, col in enumerate(columns, 1):
                print(f"  {i:2d}. {col['Field']:35s} {col['Type']:20s} {col['Null']:5s} {col['Key']:5s}")
            
            # Get sample data
            print(f"\nSample data from {table_name}:")
            sample_data = get_sample_data(table_name, 1)
            if sample_data:
                for key, value in sample_data[0].items():
                    print(f"  {key}: {value}")
            else:
                print("  No sample data available")
        else:
            print(f"Failed to retrieve structure for {table_name}")
        
        print("\n" + "="*80 + "\n")
    
    # Focus on Rod_Blk related columns in database_data
    print("=== ROD_BLK RELATED COLUMNS IN DATABASE_DATA ===")
    columns = check_table_structure('database_data')
    if columns:
        rod_blk_columns = [col['Field'] for col in columns if 'Rod_Blk' in col['Field'] or 'rod' in col['Field'].lower()]
        print(f"Found {len(rod_blk_columns)} Rod_Blk related columns:")
        for i, col in enumerate(rod_blk_columns, 1):
            print(f"  {i:2d}. {col}")
    
    print("\n" + "="*80 + "\n")
    
    # Focus on inspection columns in rd05200200_inspection
    print("=== INSPECTION COLUMNS IN rd05200200_inspection ===")
    columns = check_table_structure('rd05200200_inspection')
    if columns:
        inspection_columns = [col['Field'] for col in columns if 'Inspection' in col['Field']]
        print(f"Found {len(inspection_columns)} Inspection related columns:")
        for i, col in enumerate(inspection_columns, 1):
            print(f"  {i:2d}. {col}")

if __name__ == "__main__":
    main()
