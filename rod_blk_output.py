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
# FILENAME = f"PICompiled{x.year}-{x.strftime("%m")}-{x.strftime('%d')}.csv"
FILENAME = f"PICompiled2025-08-20.csv"
FILEPATH = os.path.join(NETWORK_DIR, FILENAME)
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

# Define material patterns for inspection table mapping
# Updated mapping for Rod_Blk material inspection data with new column mappings

# Rod_Blk Column Mapping Dictionary
# Maps database_data columns to their corresponding inspection table columns
ROD_BLK_COLUMN_MAPPING = {
    # Tesla measurements from rdb5200200_checksheet table
    'Process_2_Rod_Blk_Tesla_1_Average_Data': 'Rod_Blk_Tesla_1_Avg_Data',
    'Process_2_Rod_Blk_Tesla_1_Maximum_Data': 'Rod_Blk_Tesla_1_Max_Data',
    'Process_2_Rod_Blk_Tesla_1_Minimum_Data': 'Rod_Blk_Tesla_1_Min_Data',
    'Process_2_Rod_Blk_Tesla_2_Average_Data': 'Rod_Blk_Tesla_2_Avg_Data',
    'Process_2_Rod_Blk_Tesla_2_Maximum_Data': 'Rod_Blk_Tesla_2_Max_Data',
    'Process_2_Rod_Blk_Tesla_2_Minimum_Data': 'Rod_Blk_Tesla_2_Min_Data',
    'Process_2_Rod_Blk_Tesla_3_Average_Data': 'Rod_Blk_Tesla_3_Avg_Data',
    'Process_2_Rod_Blk_Tesla_3_Maximum_Data': 'Rod_Blk_Tesla_3_Max_Data',
    'Process_2_Rod_Blk_Tesla_3_Minimum_Data': 'Rod_Blk_Tesla_3_Min_Data',
    'Process_2_Rod_Blk_Tesla_4_Average_Data': 'Rod_Blk_Tesla_4_Avg_Data',
    'Process_2_Rod_Blk_Tesla_4_Maximum_Data': 'Rod_Blk_Tesla_4_Max_Data',
    'Process_2_Rod_Blk_Tesla_4_Minimum_Data': 'Rod_Blk_Tesla_4_Min_Data',
    
    # Inspection measurements from rd05200200_inspection table
    'Process_2_Rod_Blk_Inspection_1_Average_Data': 'Inspection_1_Average',
    'Process_2_Rod_Blk_Inspection_1_Maximum_Data': 'Inspection_1_Maximum',
    'Process_2_Rod_Blk_Inspection_1_Minimum_Data': 'Inspection_1_Minimum',
    'Process_2_Rod_Blk_Inspection_2_Average_Data': 'Inspection_2_Average',
    'Process_2_Rod_Blk_Inspection_2_Maximum_Data': 'Inspection_2_Maximum',
    'Process_2_Rod_Blk_Inspection_2_Minimum_Data': 'Inspection_2_Minimum',
    'Process_2_Rod_Blk_Inspection_3_Average_Data': 'Inspection_3_Average',
    'Process_2_Rod_Blk_Inspection_3_Maximum_Data': 'Inspection_3_Maximum',
    'Process_2_Rod_Blk_Inspection_3_Minimum_Data': 'Inspection_3_Minimum',
    'Process_2_Rod_Blk_Inspection_4_Average_Data': 'Inspection_4_Average',
    'Process_2_Rod_Blk_Inspection_4_Maximum_Data': 'Inspection_4_Maximum',
    'Process_2_Rod_Blk_Inspection_4_Minimum_Data': 'Inspection_4_Minimum',
    'Process_2_Rod_Blk_Inspection_5_Average_Data': 'Inspection_5_Average',
    'Process_2_Rod_Blk_Inspection_5_Maximum_Data': 'Inspection_5_Maximum',
    'Process_2_Rod_Blk_Inspection_5_Minimum_Data': 'Inspection_5_Minimum',
    'Process_2_Rod_Blk_Inspection_6_Average_Data': 'Inspection_6_Average',
    'Process_2_Rod_Blk_Inspection_6_Maximum_Data': 'Inspection_6_Maximum',
    'Process_2_Rod_Blk_Inspection_6_Minimum_Data': 'Inspection_6_Minimum',
    'Process_2_Rod_Blk_Inspection_7_Average_Data': 'Inspection_7_Average',
    'Process_2_Rod_Blk_Inspection_7_Maximum_Data': 'Inspection_7_Maximum',
    'Process_2_Rod_Blk_Inspection_7_Minimum_Data': 'Inspection_7_Minimum',
    'Process_2_Rod_Blk_Inspection_8_Average_Data': 'Inspection_8_Breaking_Test_Average',
    'Process_2_Rod_Blk_Inspection_8_Maximum_Data': 'Inspection_8_Breaking_Test_Maximum',
    'Process_2_Rod_Blk_Inspection_8_Minimum_Data': 'Inspection_8_Breaking_Test_Minimum'
}
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
        'inspection_table': ['rdb5200200_checksheet', 'rd05200200_inspection'],
        'column_mapping': ROD_BLK_COLUMN_MAPPING
    },
    'Df_Blk': {
        'prefix': 'Df_Blk',
        'inspection_table': 'dfb6600600_inspection'
    }
}

def read_csv_with_pandas(file_path):

    try:
        piCompiled = pd.read_csv(file_path)
        piCompiled["MODEL CODE"]= piCompiled["MODEL CODE"].astype(str).str.replace('"', '', regex=False)
        
        # Filter out rows containing specific keywords
        keywords_to_remove = ['NG', 'TRIAL', 'MASTER PUMP', 'RUNNING', 'RE PI']
        print(f"Original CSV rows: {len(piCompiled)}")
        
        # Create a mask to filter out rows containing any of the keywords in any column
        mask = pd.Series([True] * len(piCompiled))
        for keyword in keywords_to_remove:
            for col in piCompiled.columns:
                if piCompiled[col].dtype == 'object':  # Only check string columns
                    mask = mask & (~piCompiled[col].astype(str).str.contains(keyword, case=False, na=False))
        
        piCompiled_filtered = piCompiled[mask]
        print(f"Filtered CSV rows: {len(piCompiled_filtered)} (removed {len(piCompiled) - len(piCompiled_filtered)} rows)")
        print(f"Keywords filtered: {keywords_to_remove}")
        
        # Take the last row after filtering
        piCompiled_final = piCompiled_filtered.tail(1)
        print("CSV successfully loaded and filtered!")
        
        # Include S/N column in the return
        return piCompiled_final[['DATE', 'MODEL CODE', 'PROCESS S/N', 'S/N']]
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def create_db_connection():
    """Create database connection using the DB_CONFIG"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Database connection established successfully!")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_table_structure(table_name):
    """Check the structure of a table to see available columns"""
    connection = create_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        cursor.close()
        connection.close()
        return columns
    except Exception as e:
        print(f"Error checking table structure for {table_name}: {e}")
        if connection:
            connection.close()
        return None


def get_rod_blk_lot_from_process_data(process_sn_list, csv_date):
    """
    Get Rod_Blk lot numbers from process2_data table using Process S/N and DATE.
    Uses .tail() to get the latest row for matching Process_2_S_N and Process_2_DATE.
    
    Args:
        process_sn_list: List of Process S/N values from CSV
        csv_date: Date from CSV to filter process data
        
    Returns:
        Dictionary with Process S/N as key and Rod_Blk lot number as value
    """
    connection = create_db_connection()
    if not connection:
        return None
    
    rod_blk_lot_mapping = {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== GETTING ROD_BLK LOT NUMBERS FROM PROCESS2_DATA ===")
        print(f"Filtering by CSV date: {csv_date}")
        print(f"Process S/N list: {process_sn_list}")
        
        # For each Process S/N, get the latest (tail) row matching both S/N and DATE
        for process_sn in process_sn_list:
            query = """
            SELECT Process_2_S_N, Process_2_Rod_Blk_Lot_No, Process_2_DATE
            FROM process2_data
            WHERE Process_2_S_N = %s
            AND Process_2_DATE = %s
            AND Process_2_Rod_Blk_Lot_No IS NOT NULL
            AND Process_2_Rod_Blk_Lot_No != ''
            LIMIT 1
            """
            
            cursor.execute(query, (process_sn, csv_date))
            row = cursor.fetchone()
            
            if row:
                lot_no = row['Process_2_Rod_Blk_Lot_No']
                rod_blk_lot_mapping[process_sn] = lot_no
                print(f"  Process S/N: {process_sn} -> Rod_Blk Lot: {lot_no}")
            else:
                print(f"  No Rod_Blk lot found for Process S/N: {process_sn}")
        
        cursor.close()
        connection.close()
        
        print(f"Found {len(rod_blk_lot_mapping)} Rod_Blk lot mappings")
        return rod_blk_lot_mapping
        
    except Exception as e:
        print(f"Error getting Rod_Blk lot numbers: {e}")
        if connection:
            connection.close()
        return None


def get_checksheet_data_by_prod_date(rod_blk_lot_mapping):
    """
    Get data from rdb5200200_checksheet table using Rod_Blk lot numbers as Prod_Date.
    
    Args:
        rod_blk_lot_mapping: Dictionary with Process S/N as key and Rod_Blk lot number as value
        
    Returns:
        DataFrame with checksheet data
    """
    connection = create_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== GETTING CHECKSHEET DATA FROM rdb5200200_checksheet ===")
        
        # Get unique lot numbers to use as Prod_Date
        lot_numbers = list(set(rod_blk_lot_mapping.values()))
        
        if not lot_numbers:
            print("No lot numbers to search for")
            return pd.DataFrame()
        
        print(f"Searching for Prod_Date values: {lot_numbers}")
        
        # Create placeholders for the IN clause
        placeholders = ','.join(['%s'] * len(lot_numbers))
        
        # Query rdb5200200_checksheet table
        query = f"""
        SELECT *
        FROM rdb5200200_checksheet
        WHERE Prod_Date IN ({placeholders})
        """
        
        cursor.execute(query, lot_numbers)
        rows = cursor.fetchall()
        
        if rows:
            print(f"Found {len(rows)} matching records in rdb5200200_checksheet")
            checksheet_df = pd.DataFrame(rows)
            print("Checksheet data columns:", list(checksheet_df.columns))
            print("Sample checksheet data:")
            print(checksheet_df.head())
            return checksheet_df
        else:
            print("No matching records found in rdb5200200_checksheet")
            return pd.DataFrame()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error getting checksheet data: {e}")
        if connection:
            connection.close()
        return pd.DataFrame()


def get_inspection_data_by_lot_number(checksheet_df, csv_date=None):
    """
    Get data from rd05200200_inspection table using Material_Lot_Number from checksheet as Lot_Number.
    Filter by CSV date to get only the inspection record matching the CSV date.
    
    Args:
        checksheet_df: DataFrame with checksheet data containing Material_Lot_Number column
        csv_date: CSV date string (e.g., "2025/07/11") to filter inspection records
        
    Returns:
        DataFrame with inspection data (filtered by date if provided)
    """
    connection = create_db_connection()
    if not connection:
        return pd.DataFrame()
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== GETTING INSPECTION DATA FROM rd05200200_inspection ===")
        
        if checksheet_df.empty or 'Material_Lot_Number' not in checksheet_df.columns:
            print("No Material_Lot_Number found in checksheet data")
            return pd.DataFrame()
        
        # Get unique material lot numbers
        material_lot_numbers = checksheet_df['Material_Lot_Number'].dropna().unique().tolist()
        
        if not material_lot_numbers:
            print("No material lot numbers to search for")
            return pd.DataFrame()
        
        print(f"Searching for inspection data with lot numbers: {material_lot_numbers}")
        
        # Strategy 1: Try exact lot number match first
        placeholders = ','.join(['%s'] * len(material_lot_numbers))
        query = f"""
        SELECT * FROM rd05200200_inspection
        WHERE Lot_Number IN ({placeholders})
        """
        
        cursor.execute(query, material_lot_numbers)
        rows = cursor.fetchall()
        
        # Strategy 2: If no exact matches and CSV date provided, prioritize date matching
        if not rows and csv_date:
            print("No exact lot number matches found, trying date-first approach...")
            
            # Convert CSV date format "2025/07/11" to inspection date format "2025-07-11"
            target_date = csv_date.replace('/', '-')
            print(f"Looking for inspection data on date: {target_date}")
            
            # Query for any inspection records on the target date
            date_query = """
            SELECT * FROM rd05200200_inspection
            WHERE Date = %s
            ORDER BY Lot_Number
            """
            
            cursor.execute(date_query, (target_date,))
            date_rows = cursor.fetchall()
            
            if date_rows:
                print(f"Found {len(date_rows)} inspection records on {target_date}")
                lot_numbers = [row['Lot_Number'] for row in date_rows]
                print(f"Available lot numbers on {target_date}: {lot_numbers}")
                # Use the first record from the target date
                rows = [date_rows[0]]
                print(f"Selected inspection record: {date_rows[0]['Lot_Number']} on {target_date}")
            else:
                print(f"No inspection data found for date {target_date}")
        
        # Strategy 3: If still no matches, try pattern matching (fallback)
        if not rows:
            print("No date matches found, trying lot number pattern matching as fallback...")
            all_rows = []
            for lot_number in material_lot_numbers:
                base_pattern = lot_number.split('-')[0] + '-'
                pattern_query = """
                SELECT * FROM rd05200200_inspection
                WHERE Lot_Number LIKE %s
                ORDER BY Date DESC
                """
                cursor.execute(pattern_query, (base_pattern + '%',))
                pattern_rows = cursor.fetchall()
                if pattern_rows:
                    print(f"Found {len(pattern_rows)} pattern matches for {lot_number}")
                    # Show available dates for debugging
                    dates = [row.get('Date', 'No Date') for row in pattern_rows]
                    print(f"Available inspection dates: {dates}")
                    # Use only the most recent record as fallback
                    all_rows = [pattern_rows[0]]
                    break
            rows = all_rows
        
        cursor.close()
        connection.close()
        
        if rows:
            df = pd.DataFrame(rows)
            print(f"Retrieved {len(df)} inspection rows before date filtering")
            
            # Filter by CSV date if provided
            if csv_date and 'Date' in df.columns:
                # Convert CSV date format "2025/07/11" to match inspection date format "2025-07-11"
                target_date = csv_date.replace('/', '-')
                print(f"Filtering inspection data for date: {target_date}")
                
                # Convert Date column to string for comparison
                df['Date'] = df['Date'].astype(str)
                
                # Filter to only include rows matching the target date
                date_filtered_df = df[df['Date'].str.contains(target_date, na=False)]
                
                if not date_filtered_df.empty:
                    print(f"Found {len(date_filtered_df)} inspection rows matching date {target_date}")
                    print(f"Filtered inspection data: {date_filtered_df[['Date', 'Lot_Number']].to_dict()}")
                    return date_filtered_df
                else:
                    print(f"No inspection rows found for date {target_date}")
                    print(f"Available dates in inspection data: {df['Date'].unique().tolist()}")
                    # Return the most recent inspection data as fallback
                    print("Using most recent inspection data as fallback")
                    return df.head(1)
            else:
                print("No CSV date provided or Date column not found, returning all inspection data")
                
            print(f"Inspection DataFrame columns: {list(df.columns)}")
            print(f"Sample inspection data: {df.head(1).to_dict()}")
            return df
        else:
            print("No inspection data found for the given lot numbers")
            # Debug: Check what lot numbers exist in the table
            connection = create_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT DISTINCT Lot_Number FROM rd05200200_inspection LIMIT 10")
            sample_lots = cursor.fetchall()
            print(f"Sample lot numbers in inspection table: {[row['Lot_Number'] for row in sample_lots]}")
            cursor.close()
            connection.close()
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error retrieving inspection data: {e}")
        if connection:
            connection.close()
        return pd.DataFrame()


def combine_checksheet_and_inspection_data(checksheet_df, inspection_df):
    """
    Combine checksheet and inspection data into one DataFrame.
    
    Args:
        checksheet_df: DataFrame with checksheet data
        inspection_df: DataFrame with inspection data
        
    Returns:
        Combined DataFrame
    """
    print("\n=== COMBINING CHECKSHEET AND INSPECTION DATA ===")
    
    if checksheet_df.empty and inspection_df.empty:
        print("Both checksheet and inspection DataFrames are empty")
        return pd.DataFrame()
    
    if checksheet_df.empty:
        print("Checksheet DataFrame is empty, returning inspection data only")
        print(f"Inspection DataFrame columns: {list(inspection_df.columns)}")
        return inspection_df
    
    if inspection_df.empty:
        print("Inspection DataFrame is empty, returning checksheet data only")
        print(f"Checksheet DataFrame columns: {list(checksheet_df.columns)}")
        return checksheet_df
    
    # Debug: Show column names from both tables
    print(f"Checksheet DataFrame columns: {list(checksheet_df.columns)}")
    print(f"Inspection DataFrame columns: {list(inspection_df.columns)}")
    
    # Debug: Check Tesla data in checksheet before merging
    tesla_cols_checksheet = [col for col in checksheet_df.columns if 'Tesla' in col]
    print(f"Tesla columns in checksheet: {tesla_cols_checksheet}")
    if tesla_cols_checksheet:
        print("Tesla data in checksheet (first row):")
        for col in tesla_cols_checksheet:
            print(f"  {col}: {checksheet_df[col].iloc[0]}")
    
    # Try to merge on Material_Lot_Number and Lot_Number
    if 'Material_Lot_Number' in checksheet_df.columns and 'Lot_Number' in inspection_df.columns:
        print("Merging on Material_Lot_Number (checksheet) and Lot_Number (inspection)")
        combined_df = pd.merge(
            checksheet_df, 
            inspection_df, 
            left_on='Material_Lot_Number', 
            right_on='Lot_Number', 
            how='outer',
            suffixes=('_checksheet', '_inspection')
        )
        print(f"Combined DataFrame shape: {combined_df.shape}")
        print("Combined DataFrame columns:", list(combined_df.columns))
        print("Sample combined data:")
        print(combined_df.head())
        return combined_df
    else:
        print("Cannot merge - required columns not found. Concatenating instead.")
        # Add source identifier
        checksheet_df_copy = checksheet_df.copy()
        inspection_df_copy = inspection_df.copy()
        checksheet_df_copy['Data_Source'] = 'checksheet'
        inspection_df_copy['Data_Source'] = 'inspection'
        
        combined_df = pd.concat([checksheet_df_copy, inspection_df_copy], ignore_index=True, sort=False)
        print(f"Concatenated DataFrame shape: {combined_df.shape}")
        return combined_df


def get_database_data_for_model(model_code, limit=100):
    """
    Query database_data table for 100 units of data based on Model Code.
    Only include records where PASS_NG = "1" (passing records) for accurate historical averages.
    Include dates for traceability.
    
    Args:
        model_code: The model code to filter by
        limit: Number of records to retrieve (default 100)
    
    Returns:
        DataFrame with database data (only passing records)
    """
    connection = create_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n=== QUERYING DATABASE_DATA TABLE FOR MODEL {model_code} ===")
        
        # Define problematic keywords to filter out
        problematic_keywords = [
            'NG PRESSURE',
            'REPAIRED AT', 
            'RE PI',
            'MASTER PUMP',
            'NG AT',
            'INSPECTION ONLY',
        ]
        
        # Build keyword filtering conditions for NG_Cause columns
        ng_cause_columns = [
            'Process_1_NG_Cause',
            'Process_2_NG_Cause', 
            'Process_3_NG_Cause',
            'Process_4_NG_Cause',
            'Process_5_NG_Cause',
            'Process_6_NG_Cause'
        ]
        
        # Create WHERE conditions to exclude records with problematic keywords
        keyword_conditions = []
        for keyword in problematic_keywords:
            for column in ng_cause_columns:
                keyword_conditions.append(f"{column} NOT LIKE '%{keyword}%'")
        
        keyword_filter = " AND ".join(keyword_conditions)
        
        # Query for data with the specific model code, excluding problematic keywords (keep all PASS_NG values)
        # Order by date descending to get the most recent clean records
        query = f"""
        SELECT *
        FROM database_data
        WHERE Model_Code = %s
        AND ({keyword_filter})
        ORDER BY DATE DESC
        LIMIT {limit}
        """
        
        print(f"Executing query for {limit} records (excluding problematic keywords, keeping all PASS_NG values)")
        print(f"Filtering out keywords: {problematic_keywords}")
        cursor.execute(query, (model_code,))
        results = cursor.fetchall()
        
        if results:
            print(f"Retrieved {len(results)} records from database_data for model {model_code}")
            df = pd.DataFrame(results)
            print(f"Database DataFrame shape: {df.shape}")
            print(f"Database DataFrame columns (first 10): {list(df.columns)[:10]}")
            
            # Show date range of historical data for traceability
            if 'DATE' in df.columns:
                dates = df['DATE'].dropna()
                if not dates.empty:
                    print(f"Historical data date range: {dates.min()} to {dates.max()}")
                    print(f"Sample dates: {dates.head(3).tolist()}")
            
            # Show PASS_NG distribution (now includes all values)
            if 'PASS_NG' in df.columns:
                pass_ng_counts = df['PASS_NG'].value_counts()
                print(f"PASS_NG distribution: {pass_ng_counts.to_dict()}")
            
            cursor.close()
            connection.close()
            return df
        else:
            print(f"No records found in database_data for model {model_code}")
            cursor.close()
            connection.close()
            return None
            
    except Exception as e:
        print(f"Error querying database_data table: {e}")
        if connection:
            connection.close()
        return None


def calculate_rod_blk_deviations(database_df, combined_df, process_sn_list=None, sn_list=None, csv_date=None):
    """
    Calculate deviations for Rod_Blk material using the formula:
    (Average of 100 historical database_data rows - Data from DataFrame) / Average of 100 historical database_data rows
    
    Args:
        database_df: DataFrame with database data (100 historical records)
        combined_df: Combined DataFrame with checksheet and inspection data
        process_sn_list: List of process S/N values from CSV
        
    Returns:
        DataFrame with deviation calculations
    """
    import re  # Import re at the top of the function
    
    print("\n=== CALCULATING ROD_BLK DEVIATIONS ===")
    
    if database_df is None or database_df.empty:
        print("Database DataFrame is empty")
        return None
    
    if combined_df.empty:
        print("Combined DataFrame is empty")
        return None
    
    print(f"Database DataFrame shape: {database_df.shape}")
    print(f"Combined DataFrame shape: {combined_df.shape}")
    
    # Find Rod_Blk related columns in database_data
    rod_blk_columns = [col for col in database_df.columns if 'Rod_Blk' in col or 'rod' in col.lower()]
    print(f"Found {len(rod_blk_columns)} Rod_Blk related columns in database_data:")
    for col in rod_blk_columns[:10]:  # Show first 10
        print(f"  - {col}")
    
    # Calculate averages for Rod_Blk columns from database_data
    database_averages = {}
    for col in rod_blk_columns:
        try:
            # Convert to numeric and calculate mean
            numeric_values = pd.to_numeric(database_df[col], errors='coerce')
            valid_values = numeric_values.dropna()
            
            if len(valid_values) > 0:
                avg_value = valid_values.mean()
                database_averages[col] = avg_value
                print(f"  {col}: {avg_value:.4f} (from {len(valid_values)} valid values)")
        except Exception as e:
            print(f"  Error processing {col}: {e}")
    
    print(f"Calculated averages for {len(database_averages)} database columns")
    
    # Find ALL columns in combined DataFrame and try to convert them to numeric
    print(f"All combined DataFrame columns: {list(combined_df.columns)}")
    
    # Try to convert all columns to numeric to find potential matches
    # Look across ALL rows to find the first non-null numeric value for each column
    combined_numeric_data = {}
    for col in combined_df.columns:
        if col not in ['Material_Lot_Number', 'Lot_Number', 'Prod_Date', 'QR_CODE', 'JO_NUMBER', 'Data_Source']:
            try:
                # Look for the first non-null value across all rows
                numeric_value = None
                for idx in range(len(combined_df)):
                    raw_value = combined_df[col].iloc[idx]
                    if pd.notna(raw_value):
                        numeric_value = pd.to_numeric(raw_value, errors='coerce')
                        if pd.notna(numeric_value):
                            combined_numeric_data[col] = numeric_value
                            print(f"  Found numeric data: {col} = {numeric_value} (row {idx})")
                            break
                
                if col not in combined_numeric_data:
                    print(f"  No numeric data found for: {col}")
            except Exception as e:
                print(f"  Could not convert {col}: {e}")
    
    print(f"Found {len(combined_numeric_data)} convertible numeric columns in combined DataFrame")
    print(f"All numeric column names: {list(combined_numeric_data.keys())}")
    
    # Calculate deviations using the enhanced column mapping
    all_columns = []
    all_database_averages = []
    all_inspection_values = []
    all_deviations = []
    all_materials = []
    all_sns = []
    
    print(f"\nUsing ROD_BLK_COLUMN_MAPPING with {len(ROD_BLK_COLUMN_MAPPING)} predefined mappings")
    
    for db_col, db_avg in database_averages.items():
        if db_avg != 0:  # Avoid division by zero
            matched_col = None
            combined_value = None
            
            # Strategy 1: Use predefined column mapping (PRIORITY)
            if db_col in ROD_BLK_COLUMN_MAPPING:
                expected_col = ROD_BLK_COLUMN_MAPPING[db_col]
                if expected_col in combined_numeric_data:
                    matched_col = expected_col
                    combined_value = combined_numeric_data[expected_col]
                    print(f"  ✓ Mapped match: {db_col} -> {matched_col}")
                else:
                    print(f"  ✗ Mapped column not found: {db_col} -> {expected_col}")
                    # Try alternative patterns for mapped columns
                    if 'Tesla' in expected_col:
                        # Try variations like Tesla_1_Avg_Data vs Tesla_1_Average_Data
                        alt_patterns = [
                            expected_col.replace('_Avg_', '_Average_'),
                            expected_col.replace('_Max_', '_Maximum_'),
                            expected_col.replace('_Min_', '_Minimum_'),
                            expected_col.replace('_Average_', '_Avg_'),
                            expected_col.replace('_Maximum_', '_Max_'),
                            expected_col.replace('_Minimum_', '_Min_')
                        ]
                        for alt_col in alt_patterns:
                            if alt_col in combined_numeric_data:
                                matched_col = alt_col
                                combined_value = combined_numeric_data[alt_col]
                                print(f"  ✓ Alternative mapped match: {db_col} -> {matched_col}")
                                break
            
            # Strategy 2: Tesla measurements fallback (if mapping failed)
            elif 'Tesla' in db_col:
                match = re.search(r'Process_2_Rod_Blk_Tesla_(\d+)_(\w+)_Data', db_col)
                if match:
                    tesla_num, data_type = match.groups()
                    
                    # Try multiple Tesla column name patterns
                    possible_cols = [
                        f'Rod_Blk_Tesla_{tesla_num}_{data_type}_Data',
                        f'Rod_Blk_Tesla_{tesla_num}_Max_Data' if data_type == 'Maximum' else f'Rod_Blk_Tesla_{tesla_num}_{data_type}_Data',
                        f'Rod_Blk_Tesla_{tesla_num}_Min_Data' if data_type == 'Minimum' else f'Rod_Blk_Tesla_{tesla_num}_{data_type}_Data',
                        f'Rod_Blk_Tesla_{tesla_num}_Avg_Data' if data_type == 'Average' else f'Rod_Blk_Tesla_{tesla_num}_{data_type}_Data'
                    ]
                    
                    for expected_col in possible_cols:
                        if expected_col in combined_numeric_data:
                            matched_col = expected_col
                            combined_value = combined_numeric_data[expected_col]
                            print(f"  ✓ Tesla fallback match: {db_col} -> {matched_col}")
                            break
            
            # Strategy 3: Inspection measurements fallback (if mapping failed)
            elif 'Inspection' in db_col:
                match = re.search(r'Process_2_Rod_Blk_Inspection_(\d+)_(\w+)_Data', db_col)
                if match:
                    insp_num, data_type = match.groups()
                    expected_col = f'Inspection_{insp_num}_{data_type}'
                    
                    if expected_col in combined_numeric_data:
                        matched_col = expected_col
                        combined_value = combined_numeric_data[expected_col]
                        print(f"  ✓ Inspection fallback match: {db_col} -> {matched_col}")
            
            # Strategy 4: Direct match for any other columns
            elif db_col in combined_numeric_data:
                matched_col = db_col
                combined_value = combined_numeric_data[db_col]
                print(f"  ✓ Direct match: {db_col} -> {matched_col}")
            
            # Strategy 5: Pattern matching fallback
            else:
                base_pattern = db_col.replace('Process_2_Rod_Blk_', '').replace('_Data', '')
                for comb_col, comb_val in combined_numeric_data.items():
                    if base_pattern in comb_col or comb_col in base_pattern:
                        matched_col = comb_col
                        combined_value = comb_val
                        print(f"  ✓ Pattern match: {db_col} -> {matched_col} (base: {base_pattern})")
                        break
                
                if not matched_col:
                    print(f"  ✗ No match found for: {db_col}")
            
            # If we found a match, calculate deviation
            if matched_col and combined_value is not None:
                try:
                    # Calculate deviation
                    deviation = (db_avg - combined_value) / db_avg
                    
                    all_columns.append(matched_col)
                    all_database_averages.append(db_avg)
                    all_inspection_values.append(combined_value)
                    all_deviations.append(deviation)
                    all_materials.append('Rod_Blk')
                    all_sns.append(sn_list[0] if sn_list else 'N/A')
                    
                    print(f"  → Deviation calculated: {deviation:.6f}")
                except Exception as e:
                    print(f"  ✗ Error calculating deviation for {db_col}: {e}")
    
    results_df = pd.DataFrame({
        'Matched Inspection Column': all_columns,
        'Database Average': all_database_averages,
        'Inspection Value': all_inspection_values,
        'Deviation': all_deviations,
        'Material': all_materials,
        'S/N': all_sns
    })
    
    # Add Date column from CSV if provided
    if csv_date:
        results_df['Date'] = csv_date
    else:
        results_df['Date'] = datetime.datetime.now().strftime('%Y/%m/%d')
    
    if not results_df.empty:
        print("\nCalculated deviations")
        print("Sample deviation results:")
        print(results_df.head())
        return results_df
    else:
        print("No deviations calculated")
        return pd.DataFrame()


def get_inspection_data_by_date_fallback(csv_date):
    """
    Fallback function to get inspection data directly by date when lot mapping fails.
    """
    connection = create_db_connection()
    if not connection:
        return pd.DataFrame()
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n=== FALLBACK: GETTING INSPECTION DATA BY DATE {csv_date} ===")
        
        # Convert CSV date format "2025/07/11" to inspection date format "2025-07-11"
        target_date = csv_date.replace('/', '-')
        
        # Query for inspection records on the target date
        query = """
        SELECT * FROM rd05200200_inspection
        WHERE Date = %s
        ORDER BY Lot_Number DESC
        LIMIT 1
        """
        
        cursor.execute(query, (target_date,))
        rows = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if rows:
            df = pd.DataFrame(rows)
            print(f"Found {len(df)} inspection record(s) for date {target_date}")
            return df
        else:
            print(f"No inspection data found for date {target_date}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error in date fallback: {e}")
        return pd.DataFrame()


def map_database_to_inspection_column(database_col):
    """
    Map database column names to their corresponding inspection table column names.
    This helps show what inspection columns the database columns correspond to.
    """
    # Remove Process_2_Rod_Blk_ prefix and _Data suffix to get the base pattern
    base_pattern = database_col.replace('Process_2_Rod_Blk_', '').replace('_Data', '')
    
    # Common mapping patterns for Rod Block inspection columns
    mapping_patterns = {
        # Inspection types based on common Rod Block measurements
        'Inspection_3_Maximum': 'Inspection_3_Resistance_Maximum',
        'Inspection_3_Minimum': 'Inspection_3_Resistance_Minimum', 
        'Inspection_3_Average': 'Inspection_3_Resistance_Average',
        'Inspection_4_Maximum': 'Inspection_4_Dimension_Maximum',
        'Inspection_4_Minimum': 'Inspection_4_Dimension_Minimum',
        'Inspection_4_Average': 'Inspection_4_Dimension_Average',
        'Inspection_5_Maximum': 'Inspection_5_Dimension_Maximum',
        'Inspection_5_Minimum': 'Inspection_5_Dimension_Minimum',
        'Inspection_5_Average': 'Inspection_5_Dimension_Average',
        'Inspection_10': 'Inspection_10_Pull_Test'
    }
    
    # Check if we have a direct mapping
    if base_pattern in mapping_patterns:
        return mapping_patterns[base_pattern]
    
    # If no direct mapping, return the base pattern (cleaned up database column name)
    return base_pattern


def create_database_only_deviations(database_df, process_sn_list, sn_list):
    """
    Create deviation calculations using only database data when inspection data is not available.
    This is a fallback approach for Rod_Blk material.
    """
    print("\n=== CREATING DATABASE-ONLY DEVIATIONS ===")
    
    if database_df is None or database_df.empty:
        print("No database data available")
        return pd.DataFrame()
    
    # Find Rod_Blk related columns in database_data
    rod_blk_columns = [col for col in database_df.columns if 'Rod_Blk' in col]
    print(f"Found {len(rod_blk_columns)} Rod_Blk columns in database")
    
    deviation_results = []
    
    for col in rod_blk_columns[:10]:  # Limit to first 10 to avoid too many results
        try:
            # Calculate average from database
            numeric_values = pd.to_numeric(database_df[col], errors='coerce')
            valid_values = numeric_values.dropna()
            
            if len(valid_values) > 0:
                avg_value = valid_values.mean()
                std_value = valid_values.std()
                
                # Create a "deviation" based on standard deviation (indicating variability)
                deviation = std_value / avg_value if avg_value != 0 else 0
                
                # Map database column name to inspection table column name
                inspection_col_name = map_database_to_inspection_column(col)
                
                deviation_results.append({
                    'Matched Inspection Column': inspection_col_name,
                    'Database Average': avg_value,
                    'Inspection Value': avg_value,  # Use average as inspection value
                    'Deviation': deviation,
                    'Material': 'Rod_Blk',
                    'S/N': sn_list[0] if sn_list else 'N/A',
                    'Process_Number': '2',
                    'Material_Code': 'RDB5200200',
                    'Note': 'Database-only calculation (no inspection data available)'
                })
                
                print(f"  {col}: avg={avg_value:.4f}, std_dev={std_value:.4f}, deviation={deviation:.6f}")
        
        except Exception as e:
            print(f"  Error processing {col}: {e}")
    
    if deviation_results:
        deviation_df = pd.DataFrame(deviation_results)
        print(f"Created {len(deviation_results)} database-only deviation records")
        return deviation_df
    else:
        print("No database-only deviations created")
        return pd.DataFrame()


def create_rod_blk_excel_output(combined_df, deviation_df, database_df, filename="rod_blk_output.xlsx"):
    """
    Create Excel output for Rod_Blk data following the format from frame.py.
    
    Args:
        combined_df: Combined DataFrame with checksheet and inspection data
        deviation_df: DataFrame with deviation calculations
        database_df: DataFrame with database data
        filename: Name of the Excel file to create
    """
    try:
        print(f"\n=== CREATING ROD_BLK EXCEL OUTPUT ===")
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            sheets_created = 0
            
            # Sheet 1: Rod_Blk Deviations
            if not deviation_df.empty:
                deviation_df.to_excel(writer, sheet_name='Rod_Blk_Deviations', index=False)
                sheets_created += 1
                print(f"  Created 'Rod_Blk_Deviations' sheet with {len(deviation_df)} rows")
            
            # Sheet 2: Combined Data (Checksheet + Inspection)
            if not combined_df.empty:
                combined_df.to_excel(writer, sheet_name='Combined_Data', index=False)
                sheets_created += 1
                print(f"  Created 'Combined_Data' sheet with {len(combined_df)} rows")
            
            # Sheet 3: Database Data
            if database_df is not None and not database_df.empty:
                database_df.to_excel(writer, sheet_name='Database_Data', index=False)
                sheets_created += 1
                print(f"  Created 'Database_Data' sheet with {len(database_df)} rows")
            
            print(f"\nExcel file '{filename}' created successfully with {sheets_created} sheets!")
    
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        import traceback
        traceback.print_exc()


def process_material_data():
    """
    Compatibility function for GUI integration - calls the main Rod_Blk processing function.
    """
    return process_rod_blk_material_data()


def process_rod_blk_material_data():
    """
    Main function to process Rod_Blk material data with fallback approach.
    If process2_data lookup fails, use direct inspection table approach.
    """
    print("=== STARTING ROD_BLK MATERIAL DATA PROCESSING ===")
    
    # Step 1: Read CSV data
    print("\n1. Reading CSV data...")
    csv_data = read_csv_with_pandas(FILEPATH)
    
    if csv_data is None or csv_data.empty:
        print("Failed to read CSV data or no data found")
        return None
    
    # Extract required values
    process_sn_list = csv_data['PROCESS S/N'].tolist()
    sn_list = csv_data['S/N'].tolist()
    model_code = csv_data['MODEL CODE'].iloc[0]
    csv_date = csv_data['DATE'].iloc[0]
    
    print(f"Process S/N list: {process_sn_list}")
    print(f"S/N list: {sn_list}")
    print(f"Model Code: {model_code}")
    print(f"CSV Date: {csv_date}")
    
    # Step 2: Try to get Rod_Blk lot numbers from process2_data
    print("\n2. Getting Rod_Blk lot numbers from process2_data...")
    rod_blk_lot_mapping = get_rod_blk_lot_from_process_data(process_sn_list, csv_date)
    
    combined_df = pd.DataFrame()
    
    if rod_blk_lot_mapping:
        # Original approach: Use process2_data -> checksheet -> inspection
        print("Found Rod_Blk lot mapping, using original approach...")
        
        # Step 3: Get checksheet data using Rod_Blk lot numbers as Prod_Date
        print("\n3. Getting checksheet data...")
        checksheet_df = get_checksheet_data_by_prod_date(rod_blk_lot_mapping)
        
        # Step 4: Get inspection data using Material_Lot_Number as Lot_Number, filtered by CSV date
        print("\n4. Getting inspection data...")
        inspection_df = get_inspection_data_by_lot_number(checksheet_df, csv_date)
        
        # Step 5: Combine checksheet and inspection data
        print("\n5. Combining checksheet and inspection data...")
        combined_df = combine_checksheet_and_inspection_data(checksheet_df, inspection_df)
    
    else:
        # Fallback approach: Direct inspection table lookup by date
        print("No Rod_Blk lot mapping found, using fallback approach...")
        print("\n3. Attempting direct inspection data lookup by date...")
        
        # Try to get inspection data directly by date
        inspection_df = get_inspection_data_by_date_fallback(csv_date)
        
        if not inspection_df.empty:
            print("Found inspection data using date fallback")
            combined_df = inspection_df
        else:
            print("No inspection data found with fallback approach")
    
    if combined_df.empty:
        print("No combined data available - trying database-only approach")
        # Last resort: Use database data only for deviation calculations
        database_df = get_database_data_for_model(model_code, 100)
        
        if database_df is not None and not database_df.empty:
            print("Using database-only approach for Rod_Blk processing")
            # Create minimal deviation data using database averages only
            deviation_df = create_database_only_deviations(database_df, process_sn_list, sn_list)
            
            if deviation_df is not None and not deviation_df.empty:
                print("\n=== ROD_BLK PROCESSING COMPLETED (DATABASE-ONLY) ===")
                return {
                    'combined_data': pd.DataFrame(),
                    'deviation_data': deviation_df,
                    'database_data': database_df
                }
        
        print("All approaches failed - no Rod_Blk data available")
        return None
    
    # Step 6: Get database data for model
    print("\n6. Getting database data...")
    database_df = get_database_data_for_model(model_code, 100)
    
    # Step 7: Calculate deviations
    print("\n7. Calculating deviations...")
    deviation_df = calculate_rod_blk_deviations(database_df, combined_df, process_sn_list, sn_list, csv_date)
    
    # Step 8: Create Excel output
    print("\n8. Creating Excel output...")
    create_rod_blk_excel_output(combined_df, deviation_df, database_df)
    
    print("\n=== ROD_BLK PROCESSING COMPLETED ===")
    return {
        'combined_data': combined_df,
        'deviation_data': deviation_df,
        'database_data': database_df
    }


# %%
# Simple execution cell - Run this after running all the function definitions above
result = process_rod_blk_material_data()

if result:
    print("\n=== PROCESSING RESULTS SUMMARY ===")
    print(f"Combined data shape: {result['combined_data'].shape}")
    if result['deviation_data'] is not None and not result['deviation_data'].empty:
        print(f"Deviation calculations: {len(result['deviation_data'])} deviations calculated")
    else:
        print("No deviation calculations performed")
    if result['database_data'] is not None:
        print(f"Database data shape: {result['database_data'].shape}")
    print("\nExcel file 'rod_blk_output.xlsx' has been created!")
else:
    print("Processing failed - no results generated")

# %%
# Alternative: Main execution with if __name__ check
if __name__ == "__main__":
    # Run the Rod_Blk material data processing
    result = process_rod_blk_material_data()
    
    if result:
        print("\n=== PROCESSING RESULTS SUMMARY ===")
        print(f"Combined data shape: {result['combined_data'].shape}")
        if result['deviation_data'] is not None and not result['deviation_data'].empty:
            print(f"Deviation calculations: {len(result['deviation_data'])} deviations calculated")
        else:
            print("No deviation calculations performed")
        if result['database_data'] is not None:
            print(f"Database data shape: {result['database_data'].shape}")
        print("\nExcel file 'rod_blk_output.xlsx' has been created!")
    else:
        print("Processing failed - no results generated")

#%% Test the perform_deviation_calculations function
# if __name__ == "__main__":
#     print("Testing new perform_deviation_calculations function...")
    
#     # Create sample data for testing
#     import pandas as pd
#     import numpy as np
    
#     # Create sample database DataFrame with the required columns (including multiple processes)
#     database_data = {
#         # Process 1 columns
#         'Process_1_Em2p_Inspection_3_Average_Data': np.random.normal(0.91, 0.05, 100),
#         'Process_1_Em2p_Inspection_4_Average_Data': np.random.normal(0.38, 0.05, 100),
#         'Process_1_Em2p_Inspection_5_Average_Data': np.random.normal(0.42, 0.05, 100),
#         'Process_1_Em2p_Inspection_10_Average_Data': np.random.normal(2.14, 0.2, 100),
#         'Process_1_Em2p_Inspection_3_Minimum_Data': np.random.normal(0.88, 0.05, 100),
#         'Process_1_Em2p_Inspection_4_Minimum_Data': np.random.normal(0.31, 0.05, 100),
#         'Process_1_Em2p_Inspection_5_Minimum_Data': np.random.normal(0.34, 0.05, 100),
#         'Process_1_Em2p_Inspection_3_Maximum_Data': np.random.normal(0.96, 0.05, 100),
#         'Process_1_Em2p_Inspection_4_Maximum_Data': np.random.normal(0.48, 0.05, 100),
#         'Process_1_Em2p_Inspection_5_Maximum_Data': np.random.normal(0.50, 0.05, 100),
#         # Process 2 columns (Rod_Blk and Df_Blk as shown in deviation_calculations.xlsx)
#         'Process_2_Rod_Blk_Inspection_3_Average_Data': np.random.normal(13.55, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_4_Average_Data': np.random.normal(7.94, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_5_Average_Data': np.random.normal(7.94, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_3_Minimum_Data': np.random.normal(13.50, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_4_Minimum_Data': np.random.normal(7.93, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_5_Minimum_Data': np.random.normal(7.92, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_3_Maximum_Data': np.random.normal(13.58, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_4_Maximum_Data': np.random.normal(7.96, 0.5, 100),
#         'Process_2_Rod_Blk_Inspection_5_Maximum_Data': np.random.normal(7.95, 0.5, 100),
#         'Process_2_Df_Blk_Inspection_3_Average_Data': np.random.normal(2.20, 0.1, 100),
#         'Process_2_Df_Blk_Inspection_4_Average_Data': np.random.normal(7.07, 0.5, 100),
#         'Process_2_Df_Blk_Inspection_3_Minimum_Data': np.random.normal(2.19, 0.1, 100),
#         'Process_2_Df_Blk_Inspection_4_Minimum_Data': np.random.normal(7.05, 0.5, 100),
#         'Process_2_Df_Blk_Inspection_3_Maximum_Data': np.random.normal(2.21, 0.1, 100),
#         'Process_2_Df_Blk_Inspection_4_Maximum_Data': np.random.normal(7.09, 0.5, 100),
#     }
    
#     database_df = pd.DataFrame(database_data)
    
#     # Create sample inspection DataFrame with dynamic column names
#     inspection_data = {
#         # Inspection 3 - Resistance type (Em2p material)
#         'Inspection_3_Resistance_Minimum': [0.91],
#         'Inspection_3_Resistance_Average': [0.91],
#         'Inspection_3_Resistance_Maximum': [0.92],
#         # Inspection 4 - Dimension type (Em2p material)
#         'Inspection_4_Dimension_Minimum': [0.32],
#         'Inspection_4_Dimension_Average': [0.36],
#         'Inspection_4_Dimension_Maximum': [0.41],
#         # Inspection 5 - Dimension type (Em2p material)
#         'Inspection_5_Dimension_Minimum': [0.32],
#         'Inspection_5_Dimension_Average': [0.37],
#         'Inspection_5_Dimension_Maximum': [0.41],
#         # Inspection 10 - Pull_Test type (Em2p material)
#         'Inspection_10_Pull_Test': [2.15],
#         # Additional dynamic columns for Rod_Blk material (different inspection types)
#         'Inspection_3_Thickness_Minimum': [13.50],
#         'Inspection_3_Thickness_Average': [13.55],
#         'Inspection_3_Thickness_Maximum': [13.58],
#         'Inspection_4_Width_Minimum': [7.93],
#         'Inspection_4_Width_Average': [7.94],
#         'Inspection_4_Width_Maximum': [7.96],
#         'Inspection_5_Length_Minimum': [7.92],
#         'Inspection_5_Length_Average': [7.94],
#         'Inspection_5_Length_Maximum': [7.95],
#         # Additional dynamic columns for Df_Blk material
#         'Inspection_3_Height_Minimum': [2.19],
#         'Inspection_3_Height_Average': [2.20],
#         'Inspection_3_Height_Maximum': [2.21],
#         'Inspection_4_Depth_Minimum': [7.05],
#         'Inspection_4_Depth_Average': [7.07],
#         'Inspection_4_Depth_Maximum': [7.09],
#         'Lot_Number': ['CAT-5D24DI']
#     }
    
#     inspection_df = pd.DataFrame(inspection_data)
    
#     # Test the function with filtered data (same as main execution)
#     filtered_database_df = filter_inspection_columns(database_df)
#     inspection_df_for_calc = inspection_df.drop(columns=['Material_Code', 'Lot_Number'], errors='ignore')
    
#     print(f"\n=== TEST: FILTERED DATA FOR DEVIATION CALCULATIONS ===")
#     print(f"Filtered database shape: {filtered_database_df.shape}")
#     print(f"Filtered database columns (first 10): {list(filtered_database_df.columns)[:10]}")
#     print(f"Filtered inspection shape: {inspection_df_for_calc.shape}")
#     print(f"Filtered inspection columns: {list(inspection_df_for_calc.columns)}")
    
#     result = perform_deviation_calculations(filtered_database_df, inspection_df_for_calc)
    
#     if result is not None and not result.empty:
#         print("\nTest successful! Sample of results:")
#         print(result.head())
#         print(f"\nResult shape: {result.shape}")
#     else:
#         print("\nTest failed - no results returned")
# # # %%