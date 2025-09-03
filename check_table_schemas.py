#!/usr/bin/env python3
"""
Script to check database table schemas and identify new columns in inspection tables
"""

import mysql.connector
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'table_schema_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def check_table_structure(table_name):
    """
    Check the structure of a table to see available columns
    
    Args:
        table_name (str): Name of the table to check
        
    Returns:
        list: List of column information dictionaries or None if error occurs
    """
    logger.info(f"Checking structure for table: {table_name}")
    try:
        logger.debug(f"Connecting to database {DB_CONFIG['database']} on {DB_CONFIG['host']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        query = f"DESCRIBE {table_name}"
        logger.debug(f"Executing query: {query}")
        
        start_time = datetime.now()
        cursor.execute(query)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        columns = cursor.fetchall()
        logger.info(f"Retrieved {len(columns)} columns from {table_name} in {execution_time:.2f} seconds")
        
        cursor.close()
        connection.close()
        
        # Log column count and sample of column names
        if columns:
            sample_columns = [col['Field'] for col in columns[:5]]
            logger.debug(f"Sample columns: {sample_columns}" + 
                       ("..." if len(columns) > 5 else ""))
        
        return columns
        
    except mysql.connector.Error as e:
        logger.error(f"MySQL Error checking table {table_name}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error checking table {table_name}")
        return None

def get_sample_data(table_name, limit=3):
    """
    Get sample data from a table
    
    Args:
        table_name (str): Name of the table to query
        limit (int): Maximum number of rows to return
        
    Returns:
        list: List of row dictionaries or None if error occurs
    """
    logger.info(f"Fetching {limit} sample rows from table: {table_name}")
    try:
        logger.debug(f"Connecting to database {DB_CONFIG['database']} on {DB_CONFIG['host']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        logger.debug(f"Executing query: {query}")
        
        start_time = datetime.now()
        cursor.execute(query)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        rows = cursor.fetchall()
        logger.info(f"Retrieved {len(rows)} rows from {table_name} in {execution_time:.2f} seconds")
        
        cursor.close()
        connection.close()
        
        # Log sample data
        if rows:
            logger.debug(f"Sample data from {table_name}: {rows[0]}" + 
                       ("..." if len(rows) > 1 else ""))
        
        return rows
        
    except mysql.connector.Error as e:
        logger.error(f"MySQL Error fetching data from {table_name}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error fetching data from {table_name}")
        return None
        return rows

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
