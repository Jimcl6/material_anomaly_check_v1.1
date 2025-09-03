#!/usr/bin/env python3
"""
Verify the ROD_BLK column mappings against actual database schema
"""

import mysql.connector
import pandas as pd
import re
from rod_blk_output import ROD_BLK_COLUMN_MAPPING, DB_CONFIG

def check_database_columns():
    """Check what Rod_Blk columns actually exist in database_data table"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("=== CHECKING DATABASE_DATA TABLE COLUMNS ===")
        
        # Get all columns from database_data table
        cursor.execute("DESCRIBE database_data")
        all_columns = [row[0] for row in cursor.fetchall()]
        
        # Find Rod_Blk related columns
        rod_blk_columns = [col for col in all_columns if 'Rod_Blk' in col]
        print(f"Found {len(rod_blk_columns)} Rod_Blk columns in database_data")
        
        # Categorize columns
        tesla_columns = [col for col in rod_blk_columns if 'Tesla' in col]
        inspection_columns = [col for col in rod_blk_columns if 'Inspection' in col]
        other_columns = [col for col in rod_blk_columns if col not in tesla_columns and col not in inspection_columns]
        
        print(f"  Tesla columns: {len(tesla_columns)}")
        print(f"  Inspection columns: {len(inspection_columns)}")
        print(f"  Other columns: {len(other_columns)}")
        
        # Show sample columns
        print("\nSample Tesla columns:")
        for col in tesla_columns[:5]:
            print(f"  {col}")
            
        print("\nSample Inspection columns:")
        for col in inspection_columns[:10]:
            print(f"  {col}")
        
        cursor.close()
        connection.close()
        
        return rod_blk_columns, tesla_columns, inspection_columns
        
    except Exception as e:
        print(f"Error checking database columns: {e}")
        return [], [], []

def check_inspection_table_columns():
    """Check what columns exist in rd05200200_inspection table"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("\n=== CHECKING rd05200200_inspection TABLE COLUMNS ===")
        
        # Get all columns from rd05200200_inspection table
        cursor.execute("DESCRIBE rd05200200_inspection")
        all_columns = [row[0] for row in cursor.fetchall()]
        
        # Find Inspection related columns
        inspection_columns = [col for col in all_columns if 'Inspection' in col]
        print(f"Found {len(inspection_columns)} Inspection columns in rd05200200_inspection")
        
        # Show all inspection columns
        print("Inspection columns:")
        for col in inspection_columns:
            print(f"  {col}")
        
        cursor.close()
        connection.close()
        
        return inspection_columns
        
    except Exception as e:
        print(f"Error checking inspection table columns: {e}")
        return []

def check_checksheet_table_columns():
    """Check what columns exist in rdb5200200_checksheet table"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("\n=== CHECKING rdb5200200_checksheet TABLE COLUMNS ===")
        
        # Get all columns from rdb5200200_checksheet table
        cursor.execute("DESCRIBE rdb5200200_checksheet")
        all_columns = [row[0] for row in cursor.fetchall()]
        
        # Find Tesla related columns
        tesla_columns = [col for col in all_columns if 'Tesla' in col]
        print(f"Found {len(tesla_columns)} Tesla columns in rdb5200200_checksheet")
        
        # Show all Tesla columns
        print("Tesla columns:")
        for col in tesla_columns:
            print(f"  {col}")
        
        cursor.close()
        connection.close()
        
        return tesla_columns
        
    except Exception as e:
        print(f"Error checking checksheet table columns: {e}")
        return []

def verify_mappings():
    """Verify the ROD_BLK_COLUMN_MAPPING against actual database columns"""
    print("\n=== VERIFYING COLUMN MAPPINGS ===")
    
    # Get actual database columns
    db_rod_blk_cols, db_tesla_cols, db_inspection_cols = check_database_columns()
    insp_table_cols = check_inspection_table_columns()
    checksheet_tesla_cols = check_checksheet_table_columns()
    
    if not db_rod_blk_cols:
        print("❌ Could not retrieve database columns")
        return False
    
    # Check mapping coverage
    mapped_db_cols = set(ROD_BLK_COLUMN_MAPPING.keys())
    actual_db_cols = set(db_rod_blk_cols)
    
    print(f"\nMapping coverage analysis:")
    print(f"  Columns in mapping: {len(mapped_db_cols)}")
    print(f"  Actual database columns: {len(actual_db_cols)}")
    
    # Find missing mappings
    missing_from_mapping = actual_db_cols - mapped_db_cols
    extra_in_mapping = mapped_db_cols - actual_db_cols
    
    if missing_from_mapping:
        print(f"  ⚠ Database columns not in mapping: {len(missing_from_mapping)}")
        for col in list(missing_from_mapping)[:5]:
            print(f"    {col}")
        if len(missing_from_mapping) > 5:
            print(f"    ... and {len(missing_from_mapping) - 5} more")
    
    if extra_in_mapping:
        print(f"  ⚠ Mapping entries not in database: {len(extra_in_mapping)}")
        for col in list(extra_in_mapping)[:5]:
            print(f"    {col}")
        if len(extra_in_mapping) > 5:
            print(f"    ... and {len(extra_in_mapping) - 5} more")
    
    # Check target column validity
    mapped_target_cols = set(ROD_BLK_COLUMN_MAPPING.values())
    actual_target_cols = set(insp_table_cols + checksheet_tesla_cols)
    
    print(f"\nTarget column analysis:")
    print(f"  Mapped target columns: {len(mapped_target_cols)}")
    print(f"  Actual target columns: {len(actual_target_cols)}")
    
    missing_targets = mapped_target_cols - actual_target_cols
    if missing_targets:
        print(f"  ⚠ Target columns not found in tables: {len(missing_targets)}")
        for col in list(missing_targets)[:5]:
            print(f"    {col}")
        if len(missing_targets) > 5:
            print(f"    ... and {len(missing_targets) - 5} more")
    
    # Summary
    coverage_percent = (len(mapped_db_cols & actual_db_cols) / len(actual_db_cols)) * 100 if actual_db_cols else 0
    print(f"\n=== VERIFICATION SUMMARY ===")
    print(f"Mapping coverage: {coverage_percent:.1f}%")
    print(f"Missing from mapping: {len(missing_from_mapping)}")
    print(f"Extra in mapping: {len(extra_in_mapping)}")
    print(f"Invalid target columns: {len(missing_targets)}")
    
    if coverage_percent > 90 and len(missing_targets) == 0:
        print("✅ Column mapping verification passed!")
        return True
    else:
        print("⚠ Column mapping needs adjustment")
        return False

if __name__ == "__main__":
    success = verify_mappings()
    exit(0 if success else 1)
