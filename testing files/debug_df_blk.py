#!/usr/bin/env python3
"""
Debug script for Df_Blk material processing workflow
Tests each step individually to identify where the process fails
"""

import os
import pandas as pd
import mysql.connector
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import df_blk_output functions
import df_blk_output

def debug_df_blk_workflow():
    """Debug the complete Df_Blk workflow step by step"""
    
    print("=== DEBUGGING DF_BLK WORKFLOW ===\n")
    
    # Step 1: Test CSV reading
    print("1. Testing CSV data extraction...")
    date, model_code, process_sn, sn = df_blk_output.read_csv_with_pandas(df_blk_output.FILEPATH)
    print(f"   DATE: {date}")
    print(f"   MODEL CODE: {model_code}")
    print(f"   PROCESS S/N: {process_sn}")
    print(f"   S/N: {sn}")
    
    if not all([date, model_code, process_sn]):
        print("   ❌ CSV data extraction failed")
        return
    print("   ✅ CSV data extraction successful\n")
    
    # Step 2: Test process2_data table structure and content
    print("2. Testing process2_data table...")
    try:
        connection = mysql.connector.connect(**df_blk_output.DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Check table structure
        cursor.execute("DESCRIBE process2_data")
        columns = cursor.fetchall()
        df_blk_columns = [col['Field'] for col in columns if 'Df_Blk' in col['Field']]
        print(f"   Df_Blk columns in process2_data: {df_blk_columns}")
        
        # Check if our specific data exists
        cursor.execute("SELECT COUNT(*) as count FROM process2_data WHERE Process_2_S_N = %s AND Process_2_DATE = %s", (process_sn, date))
        result = cursor.fetchone()
        print(f"   Records matching Process_2_S_N={process_sn}, Process_2_DATE={date}: {result['count']}")
        
        # Check if Df_Blk columns have data
        for col in df_blk_columns:
            cursor.execute(f"SELECT COUNT(*) as count FROM process2_data WHERE {col} IS NOT NULL AND {col} != ''")
            result = cursor.fetchone()
            print(f"   {col} non-null records: {result['count']}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"   ❌ Error checking process2_data: {e}")
        return
    
    # Step 3: Test actual process2_data query
    print("\n3. Testing process2_data query...")
    df_blk_value, df_blk_lot_no = df_blk_output.get_process2_data(process_sn, date)
    print(f"   Process_2_Df_Blk: {df_blk_value}")
    print(f"   Process_2_Df_Blk_Lot_No: {df_blk_lot_no}")
    
    if not df_blk_value and not df_blk_lot_no:
        print("   ❌ No Df_Blk data found in process2_data")
        
        # Check what data IS available for this Process_2_S_N and date
        try:
            connection = mysql.connector.connect(**df_blk_output.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM process2_data WHERE Process_2_S_N = %s AND Process_2_DATE = %s", (process_sn, date))
            result = cursor.fetchone()
            
            if result:
                print("   Available data for this Process_2_S_N and date:")
                for key, value in result.items():
                    if value is not None and value != '':
                        print(f"     {key}: {value}")
            else:
                print("   No records found for this Process_2_S_N and date combination")
                
                # Check what dates are available for this Process_2_S_N
                cursor.execute("SELECT DISTINCT Process_2_DATE FROM process2_data WHERE Process_2_S_N = %s", (process_sn,))
                dates = cursor.fetchall()
                if dates:
                    print(f"   Available dates for Process_2_S_N {process_sn}:")
                    for d in dates[:10]:  # Show first 10 dates
                        print(f"     {d['Process_2_DATE']}")
                else:
                    print(f"   No records found for Process_2_S_N {process_sn}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"   Error checking available data: {e}")
        
        return
    
    print("   ✅ Df_Blk data found in process2_data\n")
    
    # Step 4: Test dfb_snap_data table
    print("4. Testing dfb_snap_data table...")
    try:
        connection = mysql.connector.connect(**df_blk_output.DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'dfb_snap_data'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("   ❌ dfb_snap_data table does not exist")
            cursor.close()
            connection.close()
            return
        
        print("   ✅ dfb_snap_data table exists")
        
        # Check table structure
        cursor.execute("DESCRIBE dfb_snap_data")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        print(f"   Columns: {column_names}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"   ❌ Error checking dfb_snap_data: {e}")
        return
    
    # Step 5: Test dfb_snap_data query
    print("\n5. Testing dfb_snap_data query...")
    df_rubber = df_blk_output.get_dfb_snap_data(df_blk_value, df_blk_lot_no)
    print(f"   DF_RUBBER: {df_rubber}")
    
    if not df_rubber:
        print("   ❌ No DF_RUBBER found in dfb_snap_data")
        return
    
    print("   ✅ DF_RUBBER found\n")
    
    # Step 6: Test DF_RUBBER cleaning
    print("6. Testing DF_RUBBER cleaning...")
    cleaned_df_rubber = df_blk_output.clean_df_rubber_value(df_rubber)
    print(f"   Cleaned DF_RUBBER: {cleaned_df_rubber}")
    
    # Step 7: Test inspection tables
    print("\n7. Testing inspection tables...")
    
    # Test dfb_tensile_data
    print("   Testing dfb_tensile_data...")
    try:
        connection = mysql.connector.connect(**df_blk_output.DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SHOW TABLES LIKE 'dfb_tensile_data'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("   ✅ dfb_tensile_data table exists")
            dfb_tensile_df = df_blk_output.get_dfb_tensile_data(cleaned_df_rubber)
            print(f"   dfb_tensile_data rows: {len(dfb_tensile_df)}")
        else:
            print("   ❌ dfb_tensile_data table does not exist")
            dfb_tensile_df = pd.DataFrame()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"   ❌ Error with dfb_tensile_data: {e}")
        dfb_tensile_df = pd.DataFrame()
    
    # Test df06600600_inspection
    print("   Testing df06600600_inspection...")
    try:
        connection = mysql.connector.connect(**df_blk_output.DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SHOW TABLES LIKE 'df06600600_inspection'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("   ✅ df06600600_inspection table exists")
            df06600600_inspection_df = df_blk_output.get_df06600600_inspection_data(cleaned_df_rubber)
            print(f"   df06600600_inspection rows: {len(df06600600_inspection_df)}")
        else:
            print("   ❌ df06600600_inspection table does not exist")
            df06600600_inspection_df = pd.DataFrame()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"   ❌ Error with df06600600_inspection: {e}")
        df06600600_inspection_df = pd.DataFrame()
    
    # Step 8: Test data combination
    print("\n8. Testing data combination...")
    combined_df = df_blk_output.combine_inspection_data(dfb_tensile_df, df06600600_inspection_df)
    print(f"   Combined data rows: {len(combined_df)}")
    
    if combined_df.empty:
        print("   ❌ No combined inspection data available")
        return
    
    print("   ✅ Combined inspection data available")
    print(f"   Combined data columns: {list(combined_df.columns)}")
    
    # Step 9: Test database_data
    print("\n9. Testing database_data...")
    database_df = df_blk_output.get_database_data_for_df_blk()
    print(f"   Database data rows: {len(database_df)}")
    
    if database_df.empty:
        print("   ❌ No database data available")
        return
    
    print("   ✅ Database data available")
    print(f"   Database data columns: {len(database_df.columns)}")
    
    # Step 10: Test deviation calculation
    print("\n10. Testing deviation calculation...")
    deviation_df = df_blk_output.calculate_df_blk_deviations(database_df, combined_df, [process_sn], [sn])
    print(f"   Deviation calculations: {len(deviation_df)}")
    
    if deviation_df.empty:
        print("   ❌ No deviations calculated")
        
        # Debug why no deviations were calculated
        print("   Debugging deviation calculation...")
        database_numeric_cols = database_df.select_dtypes(include=['number']).columns.tolist()
        combined_numeric_cols = combined_df.select_dtypes(include=['number']).columns.tolist()
        
        print(f"   Database numeric columns: {len(database_numeric_cols)}")
        print(f"   Combined numeric columns: {len(combined_numeric_cols)}")
        
        # Check for column overlap
        common_cols = set(database_numeric_cols) & set(combined_numeric_cols)
        print(f"   Common numeric columns: {len(common_cols)}")
        if common_cols:
            print(f"   Common columns: {list(common_cols)[:10]}")  # Show first 10
        
        return
    
    print("   ✅ Deviations calculated successfully")
    print(f"   Deviation columns: {list(deviation_df.columns)}")
    
    print("\n=== DF_BLK WORKFLOW DEBUG COMPLETE ===")
    print(f"Final result: {len(deviation_df)} deviation calculations")

if __name__ == "__main__":
    debug_df_blk_workflow()
