#!/usr/bin/env python3
"""
Test script to display the filtered DataFrame from df_blk_output.py
"""
#%%
import sys
import os
import pandas as pd

# Add the current directory to Python path to import df_blk_output
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from df_blk_output import get_database_data_for_df_blk

def test_dataframe():
    """
    Test the get_database_data_for_df_blk() function and display DataFrame info
    """
    print("=" * 60)
    print("TESTING DF_BLK DATABASE DATAFRAME")
    print("=" * 60)
    
    # Call the function to get the filtered DataFrame
    df = get_database_data_for_df_blk()
    
    if df is not None and not df.empty:
        print(f"\n✅ DataFrame retrieved successfully!")
        print(f"📊 DataFrame Shape: {df.shape}")
        print(f"📋 Total Columns: {len(df.columns)}")
        
        # Show column names
        print(f"\n📝 Column Names (first 20):")
        for i, col in enumerate(df.columns[:20], 1):
            print(f"  {i:2d}. {col}")
        
        if len(df.columns) > 20:
            print(f"  ... and {len(df.columns) - 20} more columns")
        
        # Look for Df_Blk specific columns
        df_blk_columns = [col for col in df.columns if 'Df_Blk' in col or 'df_blk' in col.lower()]
        print(f"\n🎯 Df_Blk Related Columns ({len(df_blk_columns)}):")
        for i, col in enumerate(df_blk_columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Show data types
        print(f"\n📊 Data Types Summary:")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count} columns")
        
        # Show sample data (first 3 rows, first 10 columns)
        print(f"\n📋 Sample Data (first 3 rows, first 10 columns):")
        sample_cols = df.columns[:10]
        sample_data = df[sample_cols].head(3)
        print(sample_data.to_string())
        
        # Show date range if DATE column exists
        if 'DATE' in df.columns:
            dates = df['DATE'].dropna()
            if not dates.empty:
                print(f"\n📅 Date Range:")
                print(f"  Earliest: {dates.min()}")
                print(f"  Latest: {dates.max()}")
                print(f"  Total dates: {len(dates)}")
        
        # Show PASS_NG distribution
        if 'PASS_NG' in df.columns:
            pass_ng_counts = df['PASS_NG'].value_counts()
            print(f"\n✅ PASS_NG Distribution:")
            for value, count in pass_ng_counts.items():
                print(f"  {value}: {count} records")
        
        # Show Model_Code distribution if exists
        if 'Model_Code' in df.columns:
            model_counts = df['Model_Code'].value_counts()
            print(f"\n🏷️ Model_Code Distribution:")
            for model, count in model_counts.head(5).items():
                print(f"  {model}: {count} records")
            if len(model_counts) > 5:
                print(f"  ... and {len(model_counts) - 5} more models")
        
    else:
        print("❌ No DataFrame retrieved or DataFrame is empty")
        print("Check your database connection and filtering criteria")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_dataframe()
