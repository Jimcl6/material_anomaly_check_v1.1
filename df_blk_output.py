#%%
import os
import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
import re
import datetime

x = datetime.datetime.now()

pd.set_option('display.max_columns', None)  # Show all columns in DataFrame output

NETWORK_DIR = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
FILENAME = f"PICompiled{x.year}-{x.strftime("%m")}-{x.strftime('%d')}.csv"
# FILENAME = f"PICompiled2025-08-20.csv"
FILEPATH = os.path.join(NETWORK_DIR, FILENAME)
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

# Define material patterns for inspection table mapping
material_patterns = {
    'Em2p': {
        'prefix': 'Em2p',
        'inspection_table': 'em0580106p_inspection'
    },
    'Em3p': {
        'prefix': 'Em3p',
        'inspection_table': 'em0580107p_inspection'
    },
    'Frame': {
        'prefix': 'Frame',
        'inspection_table': 'fm05000102_inspection'
    },
    'Casing_Block': {
        'prefix': 'Casing_Block',
        'inspection_table': 'csb6400802_inspection'
    },
    'Rod_Blk': {
        'prefix': 'Rod_Blk',
        'inspection_table': ['rdb5200200_checksheet', 'rdb5200200_inspection']
    },
    'Df_Blk': {
        'prefix': 'Df_Blk',
        'inspection_table': 'dfb6600600_inspection'
    }
}

def read_csv_with_pandas(file_path):
    """
    Read CSV file and extract relevant data from the last row
    Returns: DATE, MODEL CODE, PROCESS S/N, and S/N from the last row
    """
    try:
        piCompiled = pd.read_csv(file_path)
        piCompiled["MODEL CODE"] = piCompiled["MODEL CODE"].astype(str).str.replace('"', '', regex=False)
        
        # Filter out rows with unwanted keywords
        unwanted_keywords = ['test', 'Test', 'TEST', 'dummy', 'Dummy', 'DUMMY']
        for keyword in unwanted_keywords:
            piCompiled = piCompiled[~piCompiled.astype(str).apply(lambda x: x.str.contains(keyword, na=False)).any(axis=1)]
        
        if piCompiled.empty:
            print("No valid data found in CSV after filtering.")
            return None, None, None, None
        
        # Get the last row
        last_row = piCompiled.iloc[-1]
        
        # Extract required fields
        date = last_row.get('DATE', None)
        model_code = last_row.get('MODEL CODE', None)
        process_sn = last_row.get('PROCESS S/N', None)
        sn = last_row.get('S/N', None)
        
        print(f"Extracted from CSV - DATE: {date}, MODEL CODE: {model_code}, PROCESS S/N: {process_sn}, S/N: {sn}")
        
        return date, model_code, process_sn, sn
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None, None, None, None

def get_process2_data(process_sn, date):
    """
    Query process2_data table using PROCESS S/N and DATE to get Process_2_Df_Blk and Process_2_Df_Blk_Lot_No
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT Process_2_Df_Blk, Process_2_Df_Blk_Lot_No 
        FROM process2_data 
        WHERE Process_2_S_N = %s AND Process_2_DATE = %s
        """
        
        cursor.execute(query, (process_sn, date))
        result = cursor.fetchone()
        
        # Consume any remaining results to avoid "Unread result found" error
        try:
            # First consume any remaining rows from current result set
            cursor.fetchall()
        except:
            pass
        
        # Then consume any additional result sets
        try:
            while cursor.nextset():
                cursor.fetchall()
        except:
            pass
        
        if result:
            print(f"Found Process_2_Df_Blk: {result['Process_2_Df_Blk']}, Process_2_Df_Blk_Lot_No: {result['Process_2_Df_Blk_Lot_No']}")
            return result['Process_2_Df_Blk'], result['Process_2_Df_Blk_Lot_No']
        else:
            print(f"No process2_data found for PROCESS S/N: {process_sn}, DATE: {date}")
            return None, None
            
    except Exception as e:
        print(f"Error querying process2_data: {e}")
        return None, None
    finally:
        # Ensure proper cleanup
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_dfb_snap_data(df_blk_value, df_blk_lot_no):
    """
    Query dfb_snap_data table using Df_Blk lot info to get DF_RUBBER column
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # First, let's see what ITEM_BLOCK_CODE and DATE values are available in dfb_snap_data
        print(f"Looking for ITEM_BLOCK_CODE match with Df_Blk: {df_blk_value}")
        print(f"Also checking DATE match with Lot_No: {df_blk_lot_no}")
        cursor.execute("SELECT DISTINCT ITEM_BLOCK_CODE FROM dfb_snap_data ORDER BY ITEM_BLOCK_CODE LIMIT 20")
        available_codes = cursor.fetchall()
        print(f"Available ITEM_BLOCK_CODE values in dfb_snap_data: {[c['ITEM_BLOCK_CODE'] for c in available_codes]}")
        
        cursor.execute("SELECT DISTINCT DATE FROM dfb_snap_data ORDER BY DATE DESC LIMIT 20")
        available_dates = cursor.fetchall()
        print(f"Available DATE values in dfb_snap_data: {[d['DATE'] for d in available_dates]}")
        
        # Prioritize combined ITEM_BLOCK_CODE and DATE matching for accuracy
        queries = [
            ("SELECT DF_RUBBER, DATE FROM dfb_snap_data WHERE ITEM_BLOCK_CODE = %s AND DATE = %s", (df_blk_value, df_blk_lot_no)),
            ("SELECT DF_RUBBER, DATE FROM dfb_snap_data WHERE ITEM_BLOCK_CODE = %s", (df_blk_value,)),
            ("SELECT DF_RUBBER, DATE FROM dfb_snap_data WHERE ITEM_BLOCK_CODE LIKE %s", (f"%{df_blk_value}%",)),
            ("SELECT DF_RUBBER, DATE FROM dfb_snap_data WHERE DATE = %s", (df_blk_lot_no,)),
            ("SELECT DF_RUBBER, DATE FROM dfb_snap_data WHERE DATE LIKE %s", (f"%{df_blk_lot_no}%",)),
            ("SELECT DF_RUBBER, DATE FROM dfb_snap_data ORDER BY DATE DESC LIMIT 1", ())
        ]
        
        for i, (query, params) in enumerate(queries):
            print(f"Trying query {i+1}: {query} with params: {params}")
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            # Consume any remaining results to prevent "Unread result found" error
            try:
                # First consume any remaining rows from current result set
                cursor.fetchall()
            except:
                pass
            
            # Then consume any additional result sets
            try:
                while cursor.nextset():
                    cursor.fetchall()
            except:
                pass
            
            if result and result['DF_RUBBER']:
                date_info = result.get('DATE', 'Unknown')
                print(f"✅ Found DF_RUBBER: {result['DF_RUBBER']} (DATE: {date_info})")
                return result['DF_RUBBER']
        
        print(f"❌ No DF_RUBBER found in dfb_snap_data for Df_Blk: {df_blk_value}, Lot_No: {df_blk_lot_no}")
        return None
        
    except Exception as e:
        print(f"Error querying dfb_snap_data: {e}")
        return None
    finally:
        # Ensure proper cleanup
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def clean_df_rubber_value(df_rubber):
    """
    Clean DF_RUBBER values by removing characters from '-' onwards
    """
    if df_rubber is None:
        return None
    
    # Convert to string and remove characters from '-' onwards
    cleaned_value = str(df_rubber).split('-')[0].strip()
    print(f"Cleaned DF_RUBBER: {df_rubber} -> {cleaned_value}")
    return cleaned_value

def get_dfb_tensile_data(cleaned_df_rubber):
    """
    Query dfb_tensile_data table using cleaned DF_RUBBER value as Lot_Number reference
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM dfb_tensile_data WHERE DF_LOT_NO = %s"
        cursor.execute(query, (cleaned_df_rubber,))
        results = cursor.fetchall()
        
        # Consume any remaining results to avoid "Unread result found" error
        while cursor.nextset():
            pass
        
        if results:
            df = pd.DataFrame(results)
            print(f"Found {len(df)} rows in dfb_tensile_data for DF_LOT_NO: {cleaned_df_rubber}")
            return df
        else:
            print(f"No data found in dfb_tensile_data for DF_LOT_NO: {cleaned_df_rubber}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error querying dfb_tensile_data: {e}")
        return pd.DataFrame()
    finally:
        # Ensure proper cleanup
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_df06600600_inspection_data(cleaned_df_rubber):
    """
    Query df06600600_inspection table using cleaned DF_RUBBER value as Lot_Number reference
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM df06600600_inspection WHERE Lot_Number = %s"
        cursor.execute(query, (cleaned_df_rubber,))
        results = cursor.fetchall()
        
        # Consume any remaining results to avoid "Unread result found" error
        while cursor.nextset():
            pass
        
        if results:
            df = pd.DataFrame(results)
            print(f"Found {len(df)} rows in df06600600_inspection for Lot_Number: {cleaned_df_rubber}")
            return df
        else:
            print(f"No data found in df06600600_inspection for Lot_Number: {cleaned_df_rubber}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error querying df06600600_inspection: {e}")
        return pd.DataFrame()
    finally:
        # Ensure proper cleanup
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def combine_inspection_data(dfb_tensile_df, df06600600_inspection_df):
    """
    Combine dfb_tensile_data and df06600600_inspection data into one DataFrame
    """
    try:
        if dfb_tensile_df.empty and df06600600_inspection_df.empty:
            print("Both DataFrames are empty, cannot combine.")
            return pd.DataFrame()
        
        if dfb_tensile_df.empty:
            print("Using only df06600600_inspection data.")
            return df06600600_inspection_df
        
        if df06600600_inspection_df.empty:
            print("Using only dfb_tensile_data.")
            return dfb_tensile_df
        
        # Add source column to identify data origin
        dfb_tensile_df = dfb_tensile_df.copy()
        df06600600_inspection_df = df06600600_inspection_df.copy()
        
        dfb_tensile_df['data_source'] = 'dfb_tensile_data'
        df06600600_inspection_df['data_source'] = 'df06600600_inspection'
        
        # Combine the DataFrames
        combined_df = pd.concat([dfb_tensile_df, df06600600_inspection_df], ignore_index=True, sort=False)
        
        print(f"Combined DataFrame has {len(combined_df)} rows from both sources.")
        return combined_df
        
    except Exception as e:
        print(f"Error combining inspection data: {e}")
        return pd.DataFrame()

def get_database_data_for_df_blk(model_code):
    """
    Query database_data table for Df_Blk related columns and calculate averages.
    Applies keyword filtering before PASS_NG filter to ensure clean data.
    
    Args:
        model_code: The model code to filter by (e.g., '60CAT0212P')
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Keywords to filter out before applying PASS_NG filter
        keywords_to_filter = ['NG', 'TRIAL', 'MASTER PUMP', 'RUNNING', 'RE PI', 'REPAIRED', 'REPAIRED AT']
        
        # Build keyword filtering conditions for NG_Cause columns
        ng_cause_columns = [
            'Process_1_NG_Cause', 'Process_2_NG_Cause', 'Process_3_NG_Cause',
            'Process_4_NG_Cause', 'Process_5_NG_Cause', 'Process_6_NG_Cause'
        ]
        
        # Create WHERE conditions to exclude records with problematic keywords
        keyword_conditions = []
        for keyword in keywords_to_filter:
            for column in ng_cause_columns:
                keyword_conditions.append(f"{column} NOT LIKE '%{keyword}%'")
        
        keyword_filter = " AND ".join(keyword_conditions)
        
        # Query with keyword filtering and MODEL_CODE filter, then order by DATE DESC
        query = f"""
        SELECT *
        FROM database_data
        WHERE ({keyword_filter})
        AND Model_Code = %s
        ORDER BY DATE DESC
        LIMIT 100
        """
        
        print(f"Executing query with keyword filtering for: {keywords_to_filter}")
        print(f"Filtering by MODEL_CODE: {model_code}")
        cursor.execute(query, (model_code,))
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if results:
            df = pd.DataFrame(results)
            print(f"Retrieved {len(df)} clean rows from database_data table after keyword filtering.")
            
            # Additional DataFrame-level filtering for any remaining problematic data
            print("Applying additional DataFrame-level keyword filtering...")
            df_cleaned = clean_database_data_df(df, keywords_to_filter)
            
            # Filter for Df_Blk related columns
            df_blk_columns = [col for col in df_cleaned.columns if 'Df_Blk' in col or 'df_blk' in col.lower()]
            
            if df_blk_columns:
                print(f"Found Df_Blk related columns: {df_blk_columns}")
                return df_cleaned
            else:
                print("No Df_Blk related columns found in database_data.")
                return df_cleaned  # Return all clean data for comprehensive analysis
        else:
            print("No data found in database_data table after filtering.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error querying database_data: {e}")
        return pd.DataFrame()

def clean_database_data_df(df, keywords_to_filter):
    """
    Clean DataFrame by filtering out rows and columns containing specified keywords.
    Preserves critical columns like PASS_NG regardless of keyword matches.
    
    Args:
        df: DataFrame with database data
        keywords_to_filter: List of keywords to filter out
        
    Returns:
        Cleaned DataFrame
    """
    if df is None or df.empty:
        return df
    
    print(f"Cleaning database DataFrame with {len(df)} rows and {len(df.columns)} columns")
    print(f"Filtering out rows and columns containing: {keywords_to_filter}")
    
    # Define critical columns that should always be preserved
    critical_columns = ['PASS_NG', 'DATE', 'Model_Code', 'Process_SN', 'SN']
    
    # Filter out rows that contain any of the keywords in NG_Cause columns only
    ng_cause_columns = [col for col in df.columns if 'NG_Cause' in col]
    rows_to_keep = pd.Series([True] * len(df))
    
    for keyword in keywords_to_filter:
        for col in ng_cause_columns:  # Only check NG_Cause columns for row filtering
            if col in df.columns and df[col].dtype == 'object':
                rows_to_keep = rows_to_keep & (~df[col].astype(str).str.contains(keyword, case=False, na=False))
    
    df_filtered = df[rows_to_keep]
    print(f"Filtered rows from {len(df)} to {len(df_filtered)}")
    
    # Filter out columns that contain keywords, but preserve critical columns
    columns_to_keep = []
    for col in df_filtered.columns:
        # Always keep critical columns
        if col in critical_columns:
            columns_to_keep.append(col)
            print(f"  Preserving critical column '{col}'")
            continue
            
        # Check if column name contains any of the keywords
        keep_column = True
        for keyword in keywords_to_filter:
            if keyword in str(col):
                keep_column = False
                print(f"  Removing column '{col}' because name contains keyword '{keyword}'")
                break
        
        # If column name is okay, check if any values in the column contain keywords
        # But only for NG_Cause columns to avoid over-filtering
        if keep_column and 'NG_Cause' in col:
            if df_filtered[col].dtype == 'object':  # Only check string columns
                # Check if any value in the column contains any of the keywords
                for keyword in keywords_to_filter:
                    if df_filtered[col].astype(str).str.contains(keyword, case=False, na=False).any():
                        keep_column = False
                        print(f"  Removing column '{col}' because values contain keyword '{keyword}'")
                        break
        
        if keep_column:
            columns_to_keep.append(col)
    
    df_filtered = df_filtered[columns_to_keep]
    print(f"Filtered columns from {len(df.columns)} to {len(df_filtered.columns)}")
    
    # Verify PASS_NG column is present
    if 'PASS_NG' in df_filtered.columns:
        print("✓ PASS_NG column preserved in cleaned DataFrame")
    else:
        print("⚠ WARNING: PASS_NG column missing from cleaned DataFrame")
    
    print(f"Final cleaned data has {len(df_filtered)} rows and {len(df_filtered.columns)} columns")
    return df_filtered

def calculate_df_blk_deviations(database_df, combined_df, process_sn_list=None, sn_list=None):
    """
    Calculate deviations using database_data as both historical and current data source
    when inspection tables are empty
    """
    deviation_results = []
    
    try:
        if database_df.empty:
            print("Cannot calculate deviations: missing database data.")
            return pd.DataFrame()
        
        # If inspection data is empty, use database_data for both historical and current
        if combined_df.empty:
            print("Using database_data for both historical averages and current values (inspection tables empty).")
            return calculate_df_blk_deviations_from_database_only(database_df, process_sn_list, sn_list)
        
        # Convert inspection columns to numeric before processing
        print("Converting inspection data columns to numeric...")
        numeric_columns = ['RATE_OF_CHANGE_MIN', 'RATE_OF_CHANGE_AVE', 'RATE_OF_CHANGE_MAX',
                          'START_FORCE_MIN', 'START_FORCE_AVE', 'START_FORCE_MAX',
                          'TERMINATING_FORCE_MIN', 'TERMINATING_FORCE_AVE', 'TERMINATING_FORCE_MAX',
                          'Inspection_1_Minimum', 'Inspection_1_Average', 'Inspection_1_Maximum',
                          'Inspection_2_Minimum', 'Inspection_2_Average', 'Inspection_2_Maximum',
                          'Inspection_3_Minimum', 'Inspection_3_Average', 'Inspection_3_Maximum',
                          'Inspection_4_Minimum', 'Inspection_4_Average', 'Inspection_4_Maximum',
                          'Inspection_6_Hardness_Test']
        
        for col in numeric_columns:
            if col in combined_df.columns:
                combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        
        # Convert database Df_Blk columns to numeric first
        print("Converting database Df_Blk columns to numeric...")
        df_blk_columns = [col for col in database_df.columns if 'Df_Blk' in col and 'Process_2' in col]
        
        for col in df_blk_columns:
            if col in database_df.columns:
                database_df[col] = pd.to_numeric(database_df[col], errors='coerce')
                print(f"Converted {col} to numeric")
        
        # Get numeric columns from both DataFrames
        database_numeric_cols = database_df.select_dtypes(include=['number']).columns.tolist()
        combined_numeric_cols = combined_df.select_dtypes(include=['number']).columns.tolist()
        
        print(f"Database numeric columns after conversion: {len(database_numeric_cols)}")
        print(f"Combined numeric columns after conversion: {len(combined_numeric_cols)}")
        print(f"Database Df_Blk columns converted: {len(df_blk_columns)}")
        
        # Calculate averages for database data (last 100 rows)
        database_averages = database_df[database_numeric_cols].mean()
        
        # Create column mapping between inspection and database columns
        column_mapping = {
            'Inspection_1_Average': 'Process_2_Df_Blk_Inspection_1_Average_Data',
            'Inspection_1_Minimum': 'Process_2_Df_Blk_Inspection_1_Minimum_Data', 
            'Inspection_1_Maximum': 'Process_2_Df_Blk_Inspection_1_Maximum_Data',
            'Inspection_2_Average': 'Process_2_Df_Blk_Inspection_2_Average_Data',
            'Inspection_2_Minimum': 'Process_2_Df_Blk_Inspection_2_Minimum_Data',
            'Inspection_2_Maximum': 'Process_2_Df_Blk_Inspection_2_Maximum_Data',
            'Inspection_3_Average': 'Process_2_Df_Blk_Inspection_3_Average_Data',
            'Inspection_3_Minimum': 'Process_2_Df_Blk_Inspection_3_Minimum_Data',
            'Inspection_3_Maximum': 'Process_2_Df_Blk_Inspection_3_Maximum_Data',
            'Inspection_4_Average': 'Process_2_Df_Blk_Inspection_4_Average_Data',
            'Inspection_4_Minimum': 'Process_2_Df_Blk_Inspection_4_Minimum_Data',
            'Inspection_4_Maximum': 'Process_2_Df_Blk_Inspection_4_Maximum_Data',
            'START_FORCE_AVE': 'Process_2_Df_Blk_Tensile_Start_Force_Average',
            'START_FORCE_MIN': 'Process_2_Df_Blk_Tensile_Start_Force_Minimum',
            'START_FORCE_MAX': 'Process_2_Df_Blk_Tensile_Start_Force_Maximum',
            'TERMINATING_FORCE_AVE': 'Process_2_Df_Blk_Tensile_Terminating_Force_Average',
            'TERMINATING_FORCE_MIN': 'Process_2_Df_Blk_Tensile_Terminating_Force_Minimum',
            'TERMINATING_FORCE_MAX': 'Process_2_Df_Blk_Tensile_Terminating_Force_Maximum',
            'RATE_OF_CHANGE_AVE': 'Process_2_Df_Blk_Tensile_Rate_Of_Change_Average',
            'RATE_OF_CHANGE_MIN': 'Process_2_Df_Blk_Tensile_Rate_Of_Change_Minimum',
            'RATE_OF_CHANGE_MAX': 'Process_2_Df_Blk_Tensile_Rate_Of_Change_Maximum'
        }
        
        print(f"Column mapping created with {len(column_mapping)} pairs")
        
        # Process each row in combined inspection data
        for idx, row in combined_df.iterrows():
            for inspection_col in combined_numeric_cols:
                # Check if this inspection column has a corresponding database column
                database_col = column_mapping.get(inspection_col)
                
                if database_col and database_col in database_averages.index:
                    if pd.notna(row[inspection_col]) and pd.notna(database_averages[database_col]):
                        if database_averages[database_col] != 0:  # Avoid division by zero
                            deviation = (database_averages[database_col] - row[inspection_col]) / database_averages[database_col]
                            
                            deviation_results.append({
                                'Material': 'Df_Blk',
                                'Material_Code': 'Df_Blk',
                                'S/N': sn_list[0] if sn_list else 'N/A',
                                'Column': database_col,
                                'Database Average': database_averages[database_col],
                                'Inspection Value': row[inspection_col],
                                'Deviation': deviation,
                                'Data_Source': row.get('data_source', 'Unknown'),
                                'Matched Inspection Column': inspection_col
                            })
                            print(f"✅ Calculated deviation for {inspection_col} -> {database_col}: {deviation:.4f}")
        
        if deviation_results:
            results_df = pd.DataFrame(deviation_results)
            print(f"Calculated {len(results_df)} deviations for Df_Blk material.")
            return results_df
        else:
            print("No valid deviations calculated.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error calculating deviations: {e}")
        return pd.DataFrame()

def calculate_df_blk_deviations_from_database_only(database_df, process_sn_list=None, sn_list=None):
    """
    Calculate deviations using only database_data when inspection tables are empty
    Uses current CSV Process S/N row vs historical averages
    """
    deviation_results = []
    
    try:
        # Filter for Df_Blk columns only
        df_blk_columns = [col for col in database_df.columns if 'Df_Blk' in col and 'Process_2' in col]
        
        if not df_blk_columns:
            print("No Df_Blk columns found in database_data.")
            return pd.DataFrame()
        
        print(f"Found {len(df_blk_columns)} Df_Blk columns for deviation calculation.")
        
        # Get current row data (matching Process S/N from CSV)
        current_process_sn = process_sn_list[0] if process_sn_list else None
        if current_process_sn:
            current_row = database_df[database_df.get('Process_2_S_N') == current_process_sn]
            if current_row.empty:
                print(f"No current data found for Process S/N: {current_process_sn}")
                return pd.DataFrame()
            current_row = current_row.iloc[0]
        else:
            # Use most recent row as fallback
            current_row = database_df.iloc[0]
            print("Using most recent database row as current data.")
        
        # Calculate historical averages (exclude current row)
        historical_df = database_df[database_df.index != current_row.name] if current_process_sn else database_df.iloc[1:]
        
        for col in df_blk_columns:
            try:
                # Get current value and historical average
                current_value = pd.to_numeric(current_row[col], errors='coerce')
                historical_avg = pd.to_numeric(historical_df[col], errors='coerce').mean()
                
                if pd.notna(current_value) and pd.notna(historical_avg) and historical_avg != 0:
                    deviation = (historical_avg - current_value) / historical_avg
                    
                    deviation_results.append({
                        'Material': 'Df_Blk',
                        'Material_Code': 'Df_Blk',
                        'S/N': sn_list[0] if sn_list else 'N/A',
                        'Column': col,
                        'Database Average': historical_avg,
                        'Inspection Value': current_value,
                        'Deviation': deviation,
                        'Data_Source': 'database_data',
                        'Matched Inspection Column': col
                    })
            except Exception as e:
                print(f"Error processing column {col}: {e}")
                continue
        
        if deviation_results:
            results_df = pd.DataFrame(deviation_results)
            print(f"Calculated {len(results_df)} Df_Blk deviations from database_data only.")
            return results_df
        else:
            print("No valid Df_Blk deviations calculated from database_data.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error calculating Df_Blk deviations from database only: {e}")
        return pd.DataFrame()

def create_excel_output(database_df, combined_df, deviation_df, process_sn, sn):
    """
    Create Excel output following rod_blk_output.py format
    """
    try:
        output_filename = f"df_blk_output.xlsx"
        
        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            # Write deviation data sheet
            if not deviation_df.empty:
                deviation_df.to_excel(writer, sheet_name='Df_Blk_Deviations', index=False)
                print("Created 'Df_Blk_Deviations' sheet.")
            
            # Write database data sheet
            if not database_df.empty:
                database_df.to_excel(writer, sheet_name='Database_Data', index=False)
                print("Created 'Database_Data' sheet.")
            
            # Write combined inspection data sheet
            if not combined_df.empty:
                combined_df.to_excel(writer, sheet_name='Inspection_Data', index=False)
                print("Created 'Inspection_Data' sheet.")
            
            # Create material-specific sheets if deviation data exists
            if not deviation_df.empty:
                unique_materials = deviation_df['Material_Code'].unique()
                for material in unique_materials:
                    material_data = deviation_df[deviation_df['Material_Code'] == material]
                    if not material_data.empty:
                        sheet_name = f"{material}_Data"
                        material_data.to_excel(writer, sheet_name=sheet_name, index=False)
                        print(f"Created '{sheet_name}' sheet.")
            
            # Create summary sheet
            summary_data = {
                'Process_SN': [process_sn],
                'SN': [sn],
                'Total_Deviations': [len(deviation_df) if not deviation_df.empty else 0],
                'Processing_Date': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            print("Created 'Summary' sheet.")
        
        print(f"Excel file '{output_filename}' created successfully.")
        return output_filename
        
    except Exception as e:
        print(f"Error creating Excel output: {e}")
        return None

def process_material_data():
    """
    GUI-compatible function to process Df_Blk material data
    Returns: dict with 'deviation_data' key containing the deviation DataFrame
    """
    try:
        print("Starting Df_Blk material processing workflow...")
        
        # Step 1: Read CSV data
        print("\n1. Reading CSV data...")
        date, model_code, process_sn, sn = read_csv_with_pandas(FILEPATH)
        
        if not all([date, model_code, process_sn]):
            print(f"DEBUG: Missing CSV data - DATE: {date}, MODEL CODE: {model_code}, PROCESS S/N: {process_sn}")
            print("Failed to extract required data from CSV. Exiting.")
            return {'deviation_data': pd.DataFrame()}
        
        print(f"DEBUG: CSV data extracted successfully - DATE: {date}, MODEL CODE: {model_code}, PROCESS S/N: {process_sn}")
        
        # Step 2: Query process2_data table
        print("\n2. Querying process2_data table...")
        df_blk_value, df_blk_lot_no = get_process2_data(process_sn, date)
        
        if not df_blk_value and not df_blk_lot_no:
            print(f"DEBUG: No Df_Blk data found in process2_data for PROCESS S/N: {process_sn}, DATE: {date}")
            print("Failed to get Df_Blk data from process2_data. Exiting.")
            return {'deviation_data': pd.DataFrame()}
        
        print(f"DEBUG: Found Df_Blk data - Value: {df_blk_value}, Lot_No: {df_blk_lot_no}")
        
        # Step 3: Query dfb_snap_data table
        print("\n3. Querying dfb_snap_data table...")
        df_rubber = get_dfb_snap_data(df_blk_value, df_blk_lot_no)
        
        if not df_rubber:
            print(f"DEBUG: No DF_RUBBER found in dfb_snap_data for Df_Blk: {df_blk_value}, Lot_No: {df_blk_lot_no}")
            print("Failed to get DF_RUBBER from dfb_snap_data. Exiting.")
            return {'deviation_data': pd.DataFrame()}
        
        print(f"DEBUG: Found DF_RUBBER: {df_rubber}")
        
        # Step 4: Clean DF_RUBBER value
        print("\n4. Cleaning DF_RUBBER value...")
        cleaned_df_rubber = clean_df_rubber_value(df_rubber)
        print(f"DEBUG: Cleaned DF_RUBBER: {cleaned_df_rubber}")
        
        # Step 5: Query dfb_tensile_data table
        print("\n5. Querying dfb_tensile_data table...")
        dfb_tensile_df = get_dfb_tensile_data(cleaned_df_rubber)
        print(f"DEBUG: dfb_tensile_data rows: {len(dfb_tensile_df)}")
        
        # Step 6: Query df06600600_inspection table
        print("\n6. Querying df06600600_inspection table...")
        df06600600_inspection_df = get_df06600600_inspection_data(cleaned_df_rubber)
        print(f"DEBUG: df06600600_inspection rows: {len(df06600600_inspection_df)}")
        
        # Step 7: Combine inspection data
        print("\n7. Combining inspection data...")
        combined_df = combine_inspection_data(dfb_tensile_df, df06600600_inspection_df)
        print(f"DEBUG: Combined inspection data rows: {len(combined_df)}")
        
        # Step 8: Query database_data table
        print("\n8. Querying database_data table...")
        database_df = get_database_data_for_df_blk(model_code)
        print(f"DEBUG: Database data rows: {len(database_df)}")
        
        # Step 9: Calculate deviations
        print("\n9. Calculating deviations...")
        deviation_df = calculate_df_blk_deviations(database_df, combined_df, [process_sn], [sn])
        print(f"DEBUG: Calculated deviations: {len(deviation_df)}")
        
        # Step 10: Create Excel output
        print("\n10. Creating Excel output...")
        output_file = create_excel_output(database_df, combined_df, deviation_df, process_sn, sn)
        
        print(f"\nDf_Blk material processing completed. Output file: {output_file}")
        print(f"DEBUG: Final deviation_df shape: {deviation_df.shape}")
        print(f"DEBUG: Final deviation_df columns: {list(deviation_df.columns) if not deviation_df.empty else 'Empty DataFrame'}")
        
        # Return deviation data in expected format for GUI
        return {'deviation_data': deviation_df}
        
    except Exception as e:
        print(f"Error in Df_Blk material processing: {e}")
        import traceback
        traceback.print_exc()
        return {'deviation_data': pd.DataFrame()}
#%%
def main():
    """
    Main function to execute the complete Df_Blk material processing workflow
    """
    result = process_material_data()
    return result['deviation_data'] if result and 'deviation_data' in result else pd.DataFrame()
#%%
if __name__ == "__main__":
    deviation_data = main()
# %%
