#!/usr/bin/env python3
"""
Test script to run debug analysis on material inspection tables
"""

import os
import sys
import pandas as pd
import mysql.connector
import re

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from main.py
from main import (
    create_db_connection, 
    get_material_inspection_data,
    normalize_inspection_columns
)

def test_inspection_table_analysis():
    """Test the inspection table analysis with debug logging"""
    print("🚀 Starting debug analysis of material inspection tables...")
    
    # Create a simple test case to trigger the inspection data retrieval
    # We'll simulate having some material results to query inspection tables
    
    # First, let's try to connect to the database and see what inspection tables exist
    connection = create_db_connection()
    if not connection:
        print("❌ Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        
        # Get all tables that end with '_inspection'
        print("\n🔍 Finding all inspection tables...")
        cursor.execute("SHOW TABLES LIKE '%_inspection'")
        inspection_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📊 Found {len(inspection_tables)} inspection tables:")
        for table in inspection_tables:
            print(f"  - {table}")
        
        # Let's examine a few key tables that are likely to exist
        key_tables = ['em0580106p_inspection', 'em0580107p_inspection', 'fm05000102_inspection']
        
        for table_name in key_tables:
            if table_name in inspection_tables:
                print(f"\n" + "="*60)
                print(f"🔍 ANALYZING TABLE: {table_name}")
                print("="*60)
                
                # Get table structure
                cursor.execute(f"DESCRIBE {table_name}")
                columns_info = cursor.fetchall()
                
                print(f"📊 Total columns: {len(columns_info)}")
                print(f"📋 Column details:")
                
                all_columns = []
                numeric_columns = []
                potential_inspection_columns = []
                
                for i, col in enumerate(columns_info, 1):
                    col_name = col[0]  # Column name
                    col_type = col[1]  # Column type
                    all_columns.append(col_name)
                    
                    print(f"  {i:2d}. {col_name:<30} | {col_type}")
                    
                    # Check if it's a numeric column
                    if any(num_type in col_type.lower() for num_type in ['int', 'float', 'double', 'decimal', 'numeric']):
                        numeric_columns.append(col_name)
                    
                    # Check if it might be an inspection-related column
                    inspection_keywords = ['inspection', 'test', 'measurement', 'value', 'result', 'data', 
                                         'resistance', 'dimension', 'pull', 'force', 'avg', 'average', 
                                         'min', 'minimum', 'max', 'maximum', '3', '4', '5', '10']
                    
                    if any(keyword in col_name.lower() for keyword in inspection_keywords):
                        potential_inspection_columns.append(col_name)
                
                print(f"\n📈 Numeric columns ({len(numeric_columns)}):")
                for col in numeric_columns:
                    print(f"  - {col}")
                
                print(f"\n🎯 Potential inspection columns ({len(potential_inspection_columns)}):")
                for col in potential_inspection_columns:
                    print(f"  - {col}")
                
                # Look for patterns that might indicate inspection numbers 3, 4, 5, 10
                target_inspections = ['3', '4', '5', '10']
                inspection_pattern_analysis = {}
                
                for inspection_num in target_inspections:
                    matching_columns = []
                    for col_name in all_columns:
                        # Look for the inspection number in various patterns
                        patterns = [
                            rf'.*_{inspection_num}_.*',           # Standard _#_ pattern
                            rf'.*inspection.*{inspection_num}.*', # inspection# pattern
                            rf'.*insp.*{inspection_num}.*',       # insp# pattern
                            rf'.*test.*{inspection_num}.*',       # test# pattern
                            rf'^{inspection_num}_.*',             # Starting with number
                            rf'.*_{inspection_num}$',             # Ending with number
                        ]
                        
                        for pattern in patterns:
                            if re.search(pattern, col_name.lower()):
                                matching_columns.append(col_name)
                                break
                    
                    if matching_columns:
                        inspection_pattern_analysis[inspection_num] = matching_columns
                        print(f"  ✅ Inspection {inspection_num} potential columns: {matching_columns}")
                    else:
                        print(f"  ❌ Inspection {inspection_num}: No matching columns found")
                
                # Try to get sample data
                print(f"\n📋 SAMPLE DATA FROM {table_name}:")
                try:
                    cursor.execute(f"SELECT * FROM {table_name} ORDER BY Lot_Number DESC LIMIT 2")
                    sample_data = cursor.fetchall()
                    
                    if sample_data:
                        print(f"Found {len(sample_data)} sample records:")
                        for i, record in enumerate(sample_data, 1):
                            print(f"\n  Record {i}:")
                            for j, value in enumerate(record):
                                col_name = columns_info[j][0]
                                if col_name.lower() not in ['id']:  # Skip ID columns
                                    print(f"    {col_name}: {value}")
                    else:
                        print("  No data found in table")
                        
                except Exception as e:
                    print(f"  ❌ Error getting sample data: {e}")
        
        cursor.close()
        connection.close()
        
        print(f"\n" + "="*80)
        print("💡 ANALYSIS COMPLETE")
        print("="*80)
        print("✅ Debug analysis completed successfully!")
        print("📝 Check the output above for detailed column information.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if connection:
            connection.close()

if __name__ == "__main__":
    test_inspection_table_analysis()