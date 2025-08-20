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
# FILENAME = f"PICompiled2025-07-11.csv"
FILEPATH = os.path.join(NETWORK_DIR, FILENAME)
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

# Define material patterns for inspection table mapping
# Fixed mapping for Frame material inspection data
FRAME_COLUMN_MAPPING = {
    'Inspection_1_Minimum ': 'Process_1_Frame_Inspection_1_Minimum_Data',
    'Inspection_1_Average ': 'Process_1_Frame_Inspection_1_Average_Data',
    'Inspection_1_Maximum ': 'Process_1_Frame_Inspection_1_Maximum_Data',
    'Inspection_2_Minimum ': 'Process_1_Frame_Inspection_2_Minimum_Data',
    'Inspection_2_Average ': 'Process_1_Frame_Inspection_2_Average_Data',
    'Inspection_2_Maximum ': 'Process_1_Frame_Inspection_2_Maximum_Data',
    'Inspection_3_Minimum ': 'Process_1_Frame_Inspection_3_Minimum_Data',
    'Inspection_3_Average ': 'Process_1_Frame_Inspection_3_Average_Data',
    'Inspection_3_Maximum ': 'Process_1_Frame_Inspection_3_Maximum_Data',
    'Inspection_4_Minimum ': 'Process_1_Frame_Inspection_4_Minimum_Data',
    'Inspection_4_Average ': 'Process_1_Frame_Inspection_4_Average_Data',
    'Inspection_4_Maximum ': 'Process_1_Frame_Inspection_4_Maximum_Data',
    'Inspection_5_Minimum ': 'Process_1_Frame_Inspection_5_Minimum_Data',
    'Inspection_5_Average ': 'Process_1_Frame_Inspection_5_Average_Data',
    'Inspection_5_Maximum ': 'Process_1_Frame_Inspection_5_Maximum_Data',
    'Inspection_6_Minimum ': 'Process_1_Frame_Inspection_6_Minimum_Data',
    'Inspection_6_Average ': 'Process_1_Frame_Inspection_6_Average_Data',
    'Inspection_6_Maximum ': 'Process_1_Frame_Inspection_6_Maximum_Data',
    'Inspection_7_Minimum ': 'Process_1_Frame_Inspection_7_Average_Data',  # Updated mapping
    'Inspection_7_Average ': 'Process_1_Frame_Inspection_6_Minimum_Data',  # Updated mapping
    'Inspection_7_Maximum ': 'Process_1_Frame_Inspection_7_Maximum_Data'
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
        'inspection_table': 'rdb5200200_inspection'
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

def get_process_data_for_materials(process_sn_list, target_materials, csv_date=None):
    """
    Access process1_data through process6_data tables and filter for specific materials
    
    Args:
        process_sn_list: List of Process S/N values from CSV
        target_materials: List of material names to filter for
        csv_date: Date from CSV to filter process data (optional)
    
    Returns:
        Dictionary with process table data for each material
    """
    connection = create_db_connection()
    if not connection:
        return None
    
    results = {}
    target_materials = ['Casing_Block']
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # First, check the structure of process1_data to understand column names
        print("Checking table structure...")
        columns = check_table_structure("process1_data")
        if columns:
            print("Available columns in process1_data:")
            for col in columns:
                print(f"  - {col['Field']} ({col['Type']})")
        
        # Loop through process1_data to process6_data tables
        for process_num in range(1, 7):
            table_name = f"process{process_num}_data"
            results[table_name] = []
            
            print(f"\nProcessing table: {table_name}")
            
            # Create placeholders for the IN clause
            placeholders = ','.join(['%s'] * len(process_sn_list))
            
            # The S/N column follows the pattern Process_{process_num}_S_N
            sn_column = f"Process_{process_num}_S_N"
            
            # Build the query to select the materials and their lot numbers
            # Based on the table structure, materials are stored as individual columns
            material_columns = []
            for material in target_materials:
                if material in ['Em2p', 'Em3p']:  # These materials exist in process1_data
                    material_columns.append(f"Process_{process_num}_{material}")
                    material_columns.append(f"Process_{process_num}_{material}_Lot_No")
                elif material == 'Casing_Block':
                    # Check if there's a Casing_Block column or similar
                    material_columns.append(f"Process_{process_num}_Casing_Block")
                    material_columns.append(f"Process_{process_num}_Casing_Block_Lot_No")
                elif material == 'Rod_Blk':
                    material_columns.append(f"Process_{process_num}_Rod_Blk")
                    material_columns.append(f"Process_{process_num}_Rod_Blk_Lot_No")
                elif material == 'Df_Blk':
                    material_columns.append(f"Process_{process_num}_Df_Blk")
                    material_columns.append(f"Process_{process_num}_Df_Blk_Lot_No")
            
            # Add basic columns
            select_columns = [sn_column, f"Process_{process_num}_Model_Code", f"Process_{process_num}_DateTime", f"Process_{process_num}_DATE"]
            select_columns.extend(material_columns)
            
            # Remove duplicates and filter out columns that might not exist
            select_columns = list(set(select_columns))
            
            # Test which columns actually exist
            existing_columns = []
            for col in select_columns:
                try:
                    test_query = f"SELECT {col} FROM {table_name} LIMIT 1"
                    cursor.execute(test_query)
                    cursor.fetchall()
                    existing_columns.append(col)
                except:
                    print(f"Column {col} does not exist in {table_name}")
                    continue
            
            if not existing_columns:
                print(f"No valid columns found in {table_name}")
                continue
            
            # Build the final query with existing columns
            columns_str = ', '.join(existing_columns)
            
            # Build query with date filter if csv_date is provided
            if csv_date:
                query = f"""
                SELECT {columns_str}
                FROM {table_name}
                WHERE {sn_column} IN ({placeholders}) AND Process_{process_num}_DATE = %s
                """
                # Execute query with both process_sn_list and csv_date
                params = process_sn_list + [csv_date]
                cursor.execute(query, params)
            else:
                query = f"""
                SELECT {columns_str}
                FROM {table_name}
                WHERE {sn_column} IN ({placeholders})
                """
                cursor.execute(query, process_sn_list)
            rows = cursor.fetchall()
            
            if rows:
                print(f"Found {len(rows)} matching records in {table_name}")
                
                # Process the results to extract material codes and lot numbers
                processed_results = []
                for row in rows:
                    base_info = {
                        'Process_SN': row.get(sn_column),
                        'Model_Code': row.get(f"Process_{process_num}_Model_Code"),
                        'DateTime': row.get(f"Process_{process_num}_DateTime"),
                        'Date': row.get(f"Process_{process_num}_DATE"),
                        'Source_Table': table_name
                    }
                    
                    # Extract material information
                    materials_found = {}
                    for material in target_materials:
                        material_col = f"Process_{process_num}_{material}"
                        lot_col = f"Process_{process_num}_{material}_Lot_No"
                        
                        if material_col in row and row[material_col]:
                            materials_found[material] = {
                                'Material_Code': row[material_col],
                                'Lot_Number': row.get(lot_col, 'N/A')
                            }
                    
                    if materials_found:
                        base_info['Materials'] = materials_found
                        processed_results.append(base_info)
                
                results[table_name] = processed_results
                
                # Display the results for this table
                if processed_results:
                    print("Processed results:")
                    for result in processed_results:
                        print(f"  Process S/N: {result['Process_SN']}")
                        print(f"  Model Code: {result['Model_Code']}")
                        print(f"  Date: {result['Date']}")
                        print(f"  DateTime: {result['DateTime']}")
                        print(f"  Materials found:")
                        for mat_name, mat_info in result['Materials'].items():
                            print(f"    {mat_name}: Code={mat_info['Material_Code']}, Lot={mat_info['Lot_Number']}")
                        print()
            else:
                print(f"No matching records found in {table_name}")
        
        cursor.close()
        connection.close()
        
        return results
        
    except Exception as e:
        print(f"Error querying process tables: {e}")
        if connection:
            connection.close()
        return None

def map_frame_inspection_columns(inspection_df):
    """
    Map frame inspection columns to the expected database column names.
    
    Args:
        inspection_df: DataFrame with inspection data from fm05000102_inspection table
        
    Returns:
        DataFrame with mapped column names
    """
    if inspection_df is None or inspection_df.empty:
        return inspection_df
        
    # Use the global FRAME_COLUMN_MAPPING
    
    # Create a new DataFrame with mapped columns
    mapped_df = inspection_df.copy()
    
    for old_col, new_col in FRAME_COLUMN_MAPPING.items():
        if old_col in mapped_df.columns:
            mapped_df[new_col] = mapped_df[old_col]
            mapped_df.drop(columns=[old_col], inplace=True)
            
    return mapped_df

def get_material_inspection_data(material_results):
    """
    Query material inspection tables using material codes and lot numbers.
    Each material is queried from its respective inspection table:
    - Frame material: fm05000102_inspection
    - Em2p material: em0580106p_inspection
    - Em3p material: em0580107p_inspection
    - Casing Block material: csb6400802_inspection
    - Rod Block material: rdb5200200_inspection
    - Df Block material: dfb6600600_inspection
    
    Args:
        material_results: Dictionary containing process table results with materials
    
    Returns:
        Dictionary with inspection data for each material and lot number
    """
    connection = create_db_connection()
    if not connection:
        return None
    
    inspection_results = {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Extract unique material codes and their lot numbers from process results
        material_lots = {}
        
        for table_name, records in material_results.items():
            for record in records:
                if 'Materials' in record:
                    for material_name, material_info in record['Materials'].items():
                        material_code = material_info['Material_Code']
                        lot_number = material_info['Lot_Number']
                        
                        if material_code not in material_lots:
                            material_lots[material_code] = set()
                        material_lots[material_code].add(lot_number)
        
        print(f"\n=== QUERYING MATERIAL INSPECTION TABLES ===")
        print(f"Found {len(material_lots)} unique material codes to process")
        
        # Process each material code
        for material_code, lot_numbers in material_lots.items():
            # Determine the correct inspection table based on material type
            processed_material_code = material_code
            if material_code.startswith('FM') and material_code.endswith('-01A'):
                # Frame material
                processed_material_code = material_code[:-4]  # Remove -01A suffix
                print(f"  [FRAME] Frame material code processed: {material_code} -> {processed_material_code}")
            elif material_code == 'EM0580106P':
                # Em2p material
                processed_material_code = 'em0580106p'
                print(f"  [EM2P] Em2p material code processed: {material_code}")
            elif material_code == 'EM0580107P':
                # Em3p material
                processed_material_code = 'em0580107p'
                print(f"  [EM3P] Em3p material code processed: {material_code}")
            elif material_code == 'CSB6400802':
                # Casing Block material
                processed_material_code = 'csb6400802'
                print(f"  [CASING] Casing Block material code processed: {material_code}")
            elif material_code == 'RDB5200200':
                # Rod Block material
                processed_material_code = 'rdb5200200'
                print(f"  [ROD] Rod Block material code processed: {material_code}")
            elif material_code == 'DFB6600600':
                # Df Block material
                processed_material_code = 'dfb6600600'
                print(f"  [DF] Df Block material code processed: {material_code}")
            
            # Convert processed material code to lowercase for table name
            table_name = f"{processed_material_code.lower()}_inspection"
            inspection_results[material_code] = {}
            
            print(f"\nProcessing material: {material_code}")
            print(f"Table name: {table_name}")
            print(f"Lot numbers to search: {list(lot_numbers)}")
            
            # Check if table exists
            try:
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                table_exists = cursor.fetchone()
                
                if not table_exists:
                    print(f"  [X] Table {table_name} does not exist")
                    continue
                
                print(f"  [OK] Table {table_name} exists")
                
                # Get table structure to identify date column and exclude ID column
                cursor.execute(f"DESCRIBE {table_name}")
                columns_info = cursor.fetchall()
                
                print(f"\n  [DEBUG] DETAILED COLUMN ANALYSIS FOR {table_name}")
                print(f"  [INFO] Total columns found: {len(columns_info)}")
                
                # Find date column (common names: date, Date, DATE, datetime, DateTime, etc.)
                date_column = None
                all_columns = []
                non_id_columns = []
                numeric_columns = []
                potential_inspection_columns = []
                
                print(f"  [DEBUG] All columns in {table_name}:")
                for i, col in enumerate(columns_info, 1):
                    col_name = col['Field']
                    col_type = col['Type']
                    all_columns.append(col_name)
                    
                    print(f"    {i:2d}. {col_name:<30} | {col_type}")
                    
                    # Skip ID columns
                    if col_name.lower() not in ['id', 'ID']:
                        non_id_columns.append(col_name)
                    
                    # Check if it's a numeric column
                    if any(num_type in col_type.lower() for num_type in ['int', 'float', 'double', 'decimal', 'numeric']):
                        numeric_columns.append(col_name)
                    
                    # Check for potential inspection columns
                    inspection_keywords = ['inspection', 'test', 'measurement', 'value', 'result', 'data',
                                         'resistance', 'dimension', 'pull', 'force', 'avg', 'average',
                                         'min', 'minimum', 'max', 'maximum', '3', '4', '5', '10']
                    
                    if any(keyword in col_name.lower() for keyword in inspection_keywords):
                        potential_inspection_columns.append(col_name)
                    
                    # Look for date column with more comprehensive pattern matching
                    if any(date_word in col_name.lower() for date_word in ['date', 'time', 'datetime', 'timestamp']):
                        date_column = col_name
                        print(f"  [DATE] Found date column: {date_column}")
                
                print(f"  [DEBUG] Numeric columns ({len(numeric_columns)}): {numeric_columns}")
                print(f"  [DEBUG] Potential inspection columns ({len(potential_inspection_columns)}): {potential_inspection_columns}")
                
                # Look for patterns that might indicate inspection numbers 3, 4, 5, 10
                target_inspections = ['1', '2', '3', '4', '5', '6', '7', '10']
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
                        print(f"  [DEBUG] Inspection {inspection_num} potential columns: {matching_columns}")
                    else:
                        print(f"  [DEBUG] Inspection {inspection_num}: No matching columns found")
                
                print(f"  [DEBUG] Inspection pattern analysis summary:")
                for inspection_num, columns in inspection_pattern_analysis.items():
                    print(f"    Inspection {inspection_num}: {len(columns)} columns")
                
                # If no date column found, try to find a column that might contain date-like information
                if not date_column:
                    for col in columns_info:
                        col_name = col['Field']
                        # Check if column name suggests it might contain date/time info
                        if any(keyword in col_name.lower() for keyword in ['created', 'modified', 'updated', 'entry']):
                            date_column = col_name
                            print(f"  [DATE] Found potential date column: {date_column}")
                            break
                
                # If still no date column found, use the first non-ID column but warn about it
                if not date_column:
                    print(f"  [WARN] No date column found, will use first available column for ordering")
                    date_column = non_id_columns[0] if non_id_columns else all_columns[0]
                    print(f"  [WARN] Using column '{date_column}' for ordering - this may not give expected results")
                
                print(f"  [INFO] Available columns: {all_columns}")
                print(f"  [INFO] Non-ID columns: {non_id_columns}")
                print(f"  [DATE] Ordering by column: {date_column}")
                
                # Query each lot number
                for lot_number in lot_numbers:
                    print(f"\n    [SEARCH] Searching for lot number: {lot_number}")
                    
                    # Create placeholders for non-ID columns
                    columns_str = ', '.join(non_id_columns)
                    
                    # Query with ORDER BY date DESC and LIMIT 1 to get latest record
                    # Ensure we're only getting data for the specific lot number
                    query = f"""
                    SELECT {columns_str}
                    FROM {table_name}
                    WHERE Lot_Number = %s
                    ORDER BY {date_column} DESC
                    """
                    
                    print(f"    [QUERY] Executing query: {query.strip()} with lot number: {lot_number}")
                    cursor.execute(query, (lot_number,))
                    results = cursor.fetchall()
                    
                    # Find the first result without NaN values
                    clean_result = None
                    if results:
                        for result in results:
                            # Check if this result has any NaN values
                            has_nan = False
                            for value in result.values():
                                if value is None or (isinstance(value, float) and str(value).lower() == 'nan'):
                                    has_nan = True
                                    break
                            
                            if not has_nan:
                                clean_result = result
                                break
                        
                        # If no clean result found, use the first one (latest by date)
                        if clean_result is None:
                            clean_result = results[0]
                            print(f"    [WARN] No clean result found for lot {lot_number}, using latest record")
                        
                        inspection_results[material_code][lot_number] = clean_result
                        print(f"    [OK] Found inspection data for lot {lot_number}")
                        print(f"    [DEBUG] Inspection data for {material_code} - Lot {lot_number}:")
                        for key, value in clean_result.items():
                            print(f"        {key}: {value}")
                    else:
                        print(f"    [X] No inspection data found for lot {lot_number}")
                        
            except Exception as e:
                print(f"  [ERROR] Error processing table {table_name}: {e}")
                continue
        
        
        
        cursor.close()
        connection.close()
        
        return inspection_results
        
    except Exception as e:
        print(f"Error querying inspection tables: {e}")
        if connection:
            connection.close()
        return None

def get_database_data_for_model(model_code, limit=100):
    """
    Query database_data table for all columns based on Model Code
    
    Args:
        model_code: The model code to filter by
        limit: Number of records to retrieve after cleaning (default 300)
    
    Returns:
        DataFrame with all database data columns
    """
    connection = create_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n=== QUERYING DATABASE_DATA TABLE FOR MODEL {model_code} ===")
        
        # Adaptive approach: Start with a higher multiplier and adjust if needed
        # Try to get at least the target number of records after cleaning
        query_limit = max(int(limit * 2), 500)  # Use at least 500 or 2x limit, whichever is higher
        
        # Query for all columns with the specific model code
        query = """
        SELECT *
        FROM database_data
        WHERE Model_Code = %s
        LIMIT %s
        """
        
        print(f"Executing query to retrieve all columns for model {model_code} (query limit: {query_limit}, target after cleaning: {limit})")
        cursor.execute(query, (model_code, query_limit))
        results = cursor.fetchall()
        
        if results:
            print(f"Retrieved {len(results)} raw records from database_data for model {model_code}")
            df = pd.DataFrame(results)
            print(f"Database DataFrame shape before cleaning: {df.shape}")
            print(f"Total columns retrieved: {len(df.columns)}")
            
            cursor.close()
            connection.close()
            
            # Clean the database data before returning
            print("Cleaning database data...")
            df_cleaned = clean_database_data(df)
            print(f"Database DataFrame shape after cleaning: {df_cleaned.shape}")
            print(f"Columns after cleaning: {len(df_cleaned.columns)}")
            
            # If we still don't have enough records after cleaning, provide detailed feedback
            if len(df_cleaned) < limit:
                print(f"WARNING: After cleaning, only {len(df_cleaned)} records remain (target was {limit})")
                print(f"Raw records retrieved: {len(results)}")
                print(f"Records lost during cleaning: {len(results) - len(df_cleaned)} ({((len(results) - len(df_cleaned))/len(results)*100):.1f}%)")
                print(f"To get {limit} clean records, you may need to query {int(limit * len(results) / len(df_cleaned))} raw records")
                print(f"Consider:")
                print(f"  1. Increasing the limit parameter to {int(limit * len(results) / len(df_cleaned))}")
                print(f"  2. Reviewing the cleaning criteria in clean_database_data()")
                print(f"  3. Using the current {len(df_cleaned)} records if acceptable")
            else:
                print(f"SUCCESS: Retrieved {len(df_cleaned)} clean records (target was {limit})")
            
            return df_cleaned
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

def clean_database_data(df):
    """
    Clean up database_data table rows and columns that contain specific keywords.
    
    Args:
        df: DataFrame with database data
        
    Returns:
        Cleaned DataFrame
    """
    if df is None or df.empty:
        return df
    
    # Keywords to filter out
    keywords = [
        "NG PRESSURE",
        "REPAIRED AT",
        "RE PI",
        "MASTER PUMP",
        "NG AT",
        "INSPECTION ONLY"
    ]
    
    print(f"Cleaning database data with {len(df)} rows and {len(df.columns)} columns")
    print(f"Filtering out rows and columns containing: {keywords}")
    
    # Filter out rows that contain any of the keywords in any column
    rows_to_keep = pd.Series([True] * len(df))
    for keyword in keywords:
        for col in df.columns:
            if df[col].dtype == 'object':  # Only check string columns
                rows_to_keep = rows_to_keep & (~df[col].astype(str).str.contains(keyword, case=False, na=False))
    
    df_filtered = df[rows_to_keep]
    print(f"Filtered rows from {len(df)} to {len(df_filtered)}")
    
    # Filter out columns that contain any of the keywords in their names or values
    columns_to_keep = []
    for col in df_filtered.columns:
        # Check if column name contains any of the keywords
        keep_column = True
        for keyword in keywords:
            if keyword in str(col):
                keep_column = False
                print(f"  Removing column '{col}' because name contains keyword '{keyword}'")
                break
        
        # If column name is okay, check if any values in the column contain keywords
        if keep_column:
            if df_filtered[col].dtype == 'object':  # Only check string columns
                # Check if any value in the column contains any of the keywords
                for keyword in keywords:
                    if df_filtered[col].astype(str).str.contains(keyword, case=False, na=False).any():
                        keep_column = False
                        print(f"  Removing column '{col}' because values contain keyword '{keyword}'")
                        break
        
        if keep_column:
            columns_to_keep.append(col)
    
    df_filtered = df_filtered[columns_to_keep]
    print(f"Filtered columns from {len(df.columns)} to {len(df_filtered.columns)}")
    
    print(f"Final cleaned data has {len(df_filtered)} rows and {len(df_filtered.columns)} columns")
    return df_filtered

def filter_inspection_columns(df):
    """
    Filter DataFrame to only include columns that match the inspection naming pattern
    
    Args:
        df: DataFrame to filter
    
    Returns:
        Filtered DataFrame with only inspection columns
    """
    if df is None or df.empty:
        return df
    
    # Pattern to match: Process_#_*material*_Inspection_#_(Maximum|Minimum|Average)_Data
    
    pattern = r'Process_\d+_[\w_]+_Inspection_\d+_(Maximum|Minimum|Average|Pull_Test)_[\w_]*'
    
    print(f"Filtering inspection columns from {len(df.columns)} total columns")
    print(f"Sample columns: {list(df.columns)[:10]}")
    
    # Find columns that match the pattern
    matching_columns = [col for col in df.columns if re.search(pattern, str(col))]
    
    # Always keep Model_Code and PASS_NG columns
    if 'Model_Code' not in matching_columns and 'Model_Code' in df.columns:
        matching_columns.append('Model_Code')
    if 'PASS_NG' not in matching_columns and 'PASS_NG' in df.columns:
        matching_columns.append('PASS_NG')
    
    # Count inspection columns (excluding identifier columns)
    identifier_cols = ['Model_Code', 'PASS_NG']
    inspection_cols_count = len([col for col in matching_columns if col not in identifier_cols])
    print(f"Found {inspection_cols_count} inspection data columns (excluding identifier columns)")
    print(f"Matching columns: {matching_columns[:10]}")  # Show first 10 matching columns
    print(f"Identifier columns included: {[col for col in identifier_cols if col in matching_columns]}")
    
    if matching_columns:
        filtered_df = df[matching_columns]
        print(f"Returning filtered DataFrame with shape: {filtered_df.shape}")
        return filtered_df
    else:
        print("No columns matched the inspection pattern")
        print(f"Pattern used: {pattern}")
        print("Sample of columns that didn't match:")
        for i, col in enumerate(df.columns[:10]):
            print(f"  {i+1}. {col}")
        return pd.DataFrame(columns=df.columns)  # Return an empty DataFrame with the same columns

def convert_to_numeric_safe(value, column_name=None):
    """
    Safely convert a value to numeric type with comprehensive error handling and logging.
    
{{ ... }}
    Args:
        value: The value to convert
        column_name: Optional column name for better error messages
        
    Returns:
        tuple: (converted_value, success_flag)
        - converted_value will be float or None if conversion fails
        - success_flag will be True if conversion succeeded
    """
    context = f"column '{column_name}'" if column_name else "value"
    print(f"  [CONVERT] Converting {context}: {value} (type: {type(value)})")
    
    try:
        # Handle pandas Series
        if isinstance(value, pd.Series):
            if value.empty:
                print(f"  [SKIP] Empty Series")
                return None, False
            value = value.iloc[0]  # Take first value if Series

        if pd.isna(value):
            print(f"  [SKIP] Value is NaN/None")
            return None, False

        # Try direct conversion first
        result = pd.to_numeric(value, errors='coerce')
        if not pd.isna(result):
            print(f"  [SUCCESS] Direct conversion: {result}")
            return float(result), True
            
        # If direct conversion fails, try cleaning string
        if isinstance(value, str):
            cleaned = value.strip().replace(',', '').replace(' ', '')
            result = pd.to_numeric(cleaned, errors='coerce')
            if not pd.isna(result):
                print(f"  [SUCCESS] Converted after cleaning: {result}")
                return float(result), True
            print(f"  [FAIL] Could not convert cleaned string: {cleaned}")
        else:
            print(f"  [FAIL] Could not convert value")
            
        return None, False
        
    except Exception as e:
        print(f"  [ERROR] Conversion failed: {str(e)}")
        return None, False

def perform_deviation_calculations(database_df, inspection_df, process_sn_list=None, sn_list=None):
    """
    Calculate deviation between database historical data and current inspection data for materials.
    
    This function converts database_data and material inspection tables into DataFrames,
    extracts specific columns for 6 major materials, takes 100 rows of historic data,
    calculates averages, then computes deviations using the formula:
    (Average of 100 historical database_data rows - Current material inspection data) / Average of 100 historical database_data rows
    
    Args:
        database_df: DataFrame with database data (should contain historic data for same model code)
        inspection_df: DataFrame with current inspection data
        
    Returns:
        DataFrame with deviation calculations in the format matching deviation_calculations.xlsx
    """
    if database_df is None or inspection_df is None:
        print("Cannot perform calculations with None DataFrames")
        return None
    
    if database_df.empty or inspection_df.empty:
        print("Cannot perform calculations with empty DataFrames")
        return None

    print("\n=== PERFORMING DEVIATION CALCULATIONS ===")
    print(f"Database DataFrame shape: {database_df.shape}")
    print(f"Database DataFrame columns (first 10): {list(database_df.columns)[:10]}")
    print(f"Inspection DataFrame shape: {inspection_df.shape}")
    print(f"Inspection DataFrame columns: {list(inspection_df.columns)}")
    print(f"Inspection DataFrame sample data:")
    print(inspection_df.head())
    
    # Define the 6 major materials
    major_materials = ['Casing_Block']
    
    # Use hardcoded list of known working inspections (only inspections that exist in both database AND inspection data)
    print("Using hardcoded list of available inspection types...")
    available_inspections = {'1', '2', '3', '4', '5', '6', '7', '10'}  # Only inspections that exist in both database AND inspection data
    
    # Convert to sorted list for consistent processing
    available_inspections = sorted(list(available_inspections))
    print(f"Using inspection types: {available_inspections}")
    
    # Define the database column patterns we need for the 10 major materials
    # Pattern: Process_#_[material]_Inspection_#_[Maximum|Minimum|Average]_Data (where # is process number 1-6)
    database_columns_needed = []
    for process_num in range(1, 11):  # Process numbers 1-10
        for material in major_materials:
            for inspection_num in available_inspections:  # Use comprehensive inspections 1-20
                database_columns_needed.extend([
                    f'Process_{process_num}_{material}_Inspection_{inspection_num}_Average_Data',
                    f'Process_{process_num}_{material}_Inspection_{inspection_num}_Minimum_Data',
                    f'Process_{process_num}_{material}_Inspection_{inspection_num}_Maximum_Data'
                ])
    
    print(f"[INFO] Generated {len(database_columns_needed)} potential database column patterns")
    print(f"[INFO] Covering {len(major_materials)} materials × {len(available_inspections)} inspections × 6 processes × 3 data types")
    
    # Take only first 100 rows as specified
    limited_database_df = database_df.head(100) if len(database_df) > 100 else database_df
    
    # Calculate average of 100 units of data from database_data table for each column
    database_averages = {}
    for col in database_columns_needed:
        if col in limited_database_df.columns:
            print(f"\n[DEBUG] Processing column: {col}")
            print(f"  Original dtype: {limited_database_df[col].dtype}")
            
            # Convert all values in column to numeric
            numeric_values = []
            try:
                for value in limited_database_df[col]:
                    converted, success = convert_to_numeric_safe(value, col)
                    if success:
                        numeric_values.append(converted)
            except Exception as e:
                print(f"  [ERROR] Error processing values: {str(e)}")
                continue
            
            if not numeric_values:
                print(f"  [FAIL] No valid numeric values in column")
                continue
                
            # Calculate statistics from valid numeric values
            try:
                numeric_series = pd.Series(numeric_values)
                col_mean = numeric_series.mean()
                database_averages[col] = col_mean
                print(f"  [SUCCESS] Calculated average: {col_mean}")
                print(f"  [STATS] Min: {numeric_series.min()}, Max: {numeric_series.max()}, Std: {numeric_series.std()}")
                print(f"  [INFO] Valid values: {len(numeric_values)}/{len(limited_database_df[col])} ({len(numeric_values)/len(limited_database_df[col])*100:.1f}%)")
            except Exception as e:
                print(f"  [ERROR] Statistics calculation failed: {str(e)}")
                continue
    
    print(f"Calculated averages for {len(database_averages)} database columns")
    if len(database_averages) > 0:
        print("Sample database averages:")
        for i, (col, avg) in enumerate(list(database_averages.items())[:5]):
            print(f"  {col}: {avg}")
    else:
        print("[WARN] No database averages calculated - checking available columns...")
        print(f"Expected column pattern: Process_#_[material]_Inspection_#_[type]_Data")
        print(f"Looking for these specific columns:")
        for i, col in enumerate(database_columns_needed[:10]):
            print(f"  {i+1}. {col}")
        print(f"...")
        
        print(f"\nActual database columns (first 20):")
        for i, col in enumerate(list(database_df.columns)[:20]):
            print(f"  {i+1}. {col}")
        
        # Check for columns that contain material names
        available_db_cols = [col for col in database_df.columns if any(mat in col for mat in major_materials)]
        print(f"\nDatabase columns containing material names ({len(available_db_cols)} found):")
        for i, col in enumerate(available_db_cols[:15]):
            print(f"  {i+1}. {col}")
        
        # Check for columns that contain "Process" and "Inspection"
        process_inspection_cols = [col for col in database_df.columns if 'Process' in col and 'Inspection' in col]
        print(f"\nDatabase columns containing 'Process' and 'Inspection' ({len(process_inspection_cols)} found):")
        for i, col in enumerate(process_inspection_cols[:15]):
            print(f"  {i+1}. {col}")
    
    # Extract current inspection values (assuming single row)
    inspection_values = {}
    if not inspection_df.empty:
        # Get all numeric columns from inspection data
        inspection_numeric_columns = inspection_df.select_dtypes(include=['number']).columns.tolist()
        print(f"Found {len(inspection_numeric_columns)} numeric columns in inspection data")
        print(f"All inspection columns: {list(inspection_df.columns)}")
        
        # Extract values from the first (and only) row of inspection data
        for col in inspection_numeric_columns:
            print(f"\n[DEBUG] Processing inspection column: {col}")
            print(f"  Original dtype: {inspection_df[col].dtypes}")
            
            if len(inspection_df) == 0:
                print(f"  [SKIP] Empty DataFrame")
                continue
            
            try:
                raw_value = inspection_df[col].iloc[0]
                converted, success = convert_to_numeric_safe(raw_value, col)
                
                if success:
                    inspection_values[col] = converted
                    print(f"  [SUCCESS] Final value: {converted} (type: {type(converted)})")
                else:
                    print(f"  [SKIP] Column {col} - conversion failed")
                    
            except (IndexError, TypeError) as e:
                print(f"  [ERROR] Failed to access value: {str(e)}")
                continue
        
        # Also try to extract non-numeric columns that might contain numeric data as strings
        non_numeric_columns = inspection_df.select_dtypes(exclude=['number']).columns.tolist()
        for col in non_numeric_columns:
            if col not in ['Lot_Number', 'Material_Code', 'Date']:  # Skip non-numeric identifier columns
                print(f"\n[DEBUG] Attempting string-to-numeric conversion for: {col}")
                
                # Extract raw value
                try:
                    raw_value = inspection_df[col].iloc[0]
                    print(f"  Original value: {raw_value} (type: {type(raw_value)})")
                except (IndexError, AttributeError) as e:
                    print(f"  [ERROR] Failed to access value: {str(e)}")
                    continue
                
                # Attempt numeric conversion
                try:
                    converted, success = convert_to_numeric_safe(raw_value, col)
                    if success:
                        inspection_values[col] = converted
                        print(f"  [SUCCESS] Final value: {converted} (type: {type(converted)})")
                    else:
                        print(f"  [SKIP] Column {col} - conversion failed")
                except Exception as e:
                    print(f"  [ERROR] Conversion failed: {str(e)}")
                    continue
    
    print(f"Retrieved {len(inspection_values)} inspection values")
    if len(inspection_values) > 0:
        print("Sample inspection values:")
        for i, (col, val) in enumerate(list(inspection_values.items())[:5]):
            print(f"  {col}: {val}")
    else:
        print("[WARN] No inspection values retrieved - checking available columns...")
        print(f"Inspection DataFrame dtypes:")
        print(inspection_df.dtypes)
    
    # Prepare results in the format matching deviation_calculations.xlsx
    results_data = []
    
    # Get lot number from inspection data if available
    lot_number = 'N/A'
    if 'Lot_Number' in inspection_df.columns and len(inspection_df) > 0:
        try:
            lot_number = inspection_df['Lot_Number'].iloc[0]
            if pd.isna(lot_number):
                lot_number = 'N/A'
        except (IndexError, TypeError):
            lot_number = 'N/A'
    
    # Add explicit mapping between inspection numbers and their types
    inspection_type_mapping = {
        '3': 'Resistance',
        '4': 'Dimension',
        '5': 'Dimension',
        '10': 'Pull_Test'
    }
    
    print(f"\n=== IMPROVED COLUMN MATCHING LOGIC ===")
    print(f"[INFO] Inspection type mapping: {inspection_type_mapping}")
    print(f"[INFO] Processing {len(database_averages)} database columns for correlation")
    print(f"[INFO] Available inspection values: {len(inspection_values)} columns")
    
    # For each database column, calculate deviation
    for db_col, db_avg in database_averages.items():
        if db_avg != 0:  # Avoid division by zero
            # Extract components from database column name to find matching inspection column
            # Pattern: Process_#_[material]_Inspection_#_[Maximum|Minimum|Average]_Data
            db_pattern = r'Process_(\d+)_([A-Za-z0-9_]+)_Inspection_(\d+)_(Maximum|Minimum|Average)_Data'
            db_match = re.search(db_pattern, db_col)
            
            if db_match:
                process_num, material, inspection_num, data_type = db_match.groups()
                
                # Initialize matching variables
                matched_inspection_value = None
                matched_column_name = None
                matching_strategy = None
                material_code = None
                material_name = None

                # Get material info from database column
                for mat_name, mat_info in material_patterns.items():
                    if mat_info['prefix'] in db_col:
                        material_name = mat_name
                        material_code = mat_info['inspection_table'].replace('_inspection', '').upper()
                        break

                if material_code and material_name:
                    # Get inspection data for this material
                    # First check if Material_Code column exists
                    if 'Material_Code' in inspection_df.columns:
                        material_inspection = inspection_df[inspection_df['Material_Code'] == material_code]
                    else:
                        # If no Material_Code column, use all inspection data
                        print(f"    [WARN] No Material_Code column found, using all inspection data")
                        material_inspection = inspection_df.copy()
                    
                    if not material_inspection.empty:
                        # Define inspection type based on inspection number
                        inspection_type = inspection_type_mapping.get(inspection_num, 'Dimension')
                        
                        # Build possible patterns based on material and inspection type
                        possible_patterns = []
                        
                        # Add material-specific patterns
                        if inspection_num == '10':
                            possible_patterns.extend([
                                f'Process_{process_num}_{material_name}_Inspection_{inspection_num}_Pull_Test',
                                f'Inspection_{inspection_num}_Pull_Test'
                            ])
                        else:
                            # Add standard patterns with data type
                            possible_patterns.extend([
                                f'Process_{process_num}_{material_name}_Inspection_{inspection_num}_{data_type}_Data',
                                f'Inspection_{inspection_num}_{inspection_type}_{data_type}',
                                f'Process_{process_num}_{material_name}_Inspection_{inspection_num}_Average_Data',
                                f'Inspection_{inspection_num}_{data_type}'
                            ])
                            
                            # Add material-specific measurement patterns
                            if inspection_type == 'Dimension':
                                possible_patterns.extend([
                                    f'Inspection_{inspection_num}_Length_{data_type}',
                                    f'Inspection_{inspection_num}_Width_{data_type}',
                                    f'Inspection_{inspection_num}_Height_{data_type}',
                                    f'Inspection_{inspection_num}_Thickness_{data_type}',
                                    f'Inspection_{inspection_num}_Depth_{data_type}'
                                ])
                            elif inspection_type == 'Resistance':
                                possible_patterns.extend([
                                    f'Inspection_{inspection_num}_Resistance_{data_type}',
                                    f'Inspection_{inspection_num}_Ohm_{data_type}'
                                ])
                        
                        # Try to find matching pattern in inspection data
                        for pattern in possible_patterns:
                            if pattern in material_inspection.columns:
                                try:
                                    value = material_inspection[pattern].iloc[0]
                                    if pd.notna(value):
                                        # Ensure value is numeric
                                        try:
                                            numeric_value = pd.to_numeric(value)
                                            matched_inspection_value = float(numeric_value)
                                            matched_column_name = pattern
                                            matching_strategy = "Direct Material Mapping"
                                            print(f"    [SUCCESS] Material-mapped match {db_col} -> {pattern} (value: {matched_inspection_value})")
                                            break
                                        except (ValueError, TypeError) as e:
                                            print(f"    [WARN] Could not convert value '{value}' to numeric: {e}")
                                            continue
                                except Exception as e:
                                    print(f"    [WARN] Error accessing value for pattern {pattern}: {e}")
                                    continue
                
                # Strategy 2: Flexible pattern matching if type mapping fails
                if matched_inspection_value is None:
                    print(f"    [INFO] Type mapping failed for {db_col}, trying flexible matching...")
                    
                    # Look for any column that contains the inspection number
                    for col_name in inspection_values.keys():
                        # Check if column contains the inspection number
                        if f'_{inspection_num}_' in col_name or col_name.endswith(f'_{inspection_num}'):
                            # Check data type compatibility
                            data_type_match = False
                            if data_type == 'Average':
                                data_type_match = ('avg' in col_name.lower() or 'average' in col_name.lower() or
                                                 not any(dt in col_name.lower() for dt in ['min', 'max']))
                            elif data_type == 'Minimum':
                                data_type_match = 'min' in col_name.lower()
                            elif data_type == 'Maximum':
                                data_type_match = 'max' in col_name.lower()
                            
                            if data_type_match:
                                try:
                                    value = inspection_values[col_name]
                                    numeric_value = pd.to_numeric(value)
                                    matched_inspection_value = float(numeric_value)
                                    matched_column_name = col_name
                                    matching_strategy = "Flexible Pattern Matching"
                                    print(f"    [SUCCESS] Flexible match {db_col} -> {col_name} (value: {matched_inspection_value})")
                                    break
                                except (ValueError, TypeError) as e:
                                    print(f"    [WARN] Could not convert value '{value}' to numeric: {e}")
                                    continue
                
                if matched_inspection_value is None:
                    print(f"    [FAIL] No match found for {db_col}")
                    print(f"        Available inspection columns: {list(inspection_values.keys())}")
                
                # If we found a matching inspection value, calculate deviation
                if matched_inspection_value is not None:
                    # Apply deviation formula: (Average of 100 historical database_data rows - Current material inspection data) / Average of 100 historical database_data rows
                    deviation = (db_avg - matched_inspection_value) / db_avg
                    deviation = round(deviation, 4)
                    
                    # Add row to results with detailed information
                    results_data.append({
                        'Column': db_col,
                        'Database_Average': db_avg,
                        'Inspection_Value': matched_inspection_value,
                        'Matched_Inspection_Column': matched_column_name,
                        'Matching_Strategy': matching_strategy,
                        'Lot_Number': lot_number,
                        'Deviation': deviation,
                        'Process_Number': process_num,
                        'Material': material,
                        'S/N': sn_list[0] if sn_list else 'N/A',
                        'Material_Code': material_code,
                        'Inspection_Number': inspection_num,
                        'Data_Type': data_type,
                        'Inspection_Table': material_patterns[material]['inspection_table'] if material in material_patterns else '',
                        'Absolute_Deviation': abs(deviation)  # New field
                    })
    
    # Create DataFrame with results in the format matching deviation_calculations.xlsx
    if results_data:
        results_df = pd.DataFrame(results_data)
        
        # Enhanced logging for final results
        print(f"\n=== DEVIATION CALCULATION RESULTS SUMMARY ===")
        print(f"[SUCCESS] Successfully created deviation results DataFrame with {len(results_data)} rows")
        print(f"[INFO] Result shape: {results_df.shape}")
        
        # Show breakdown by material and inspection type
        if 'Material' in results_df.columns and 'Inspection_Number' in results_df.columns:
            print(f"\n[BREAKDOWN] Results breakdown by material:")
            material_counts = results_df['Material'].value_counts()
            for material, count in material_counts.items():
                print(f"  - {material}: {count} deviation calculations")
            
            print(f"\n[BREAKDOWN] Results breakdown by inspection type:")
            inspection_counts = results_df['Inspection_Number'].value_counts().sort_index()
            for inspection, count in inspection_counts.items():
                inspection_type = inspection_type_mapping.get(inspection, 'Unknown')
                print(f"  - Inspection {inspection} ({inspection_type}): {count} deviation calculations")
        
        # Show breakdown by matching strategy
        if 'Matching_Strategy' in results_df.columns:
            print(f"\n[BREAKDOWN] Results breakdown by matching strategy:")
            strategy_counts = results_df['Matching_Strategy'].value_counts()
            for strategy, count in strategy_counts.items():
                print(f"  - {strategy}: {count} matches")
        
        # Show sample of successful correlations
        print(f"\n[SAMPLE] Sample of successful correlations:")
        sample_size = min(10, len(results_df))
        for i in range(sample_size):
            row = results_df.iloc[i]
            if 'Matched_Inspection_Column' in row:
                print(f"  {i+1}. {row['Column']} -> {row['Matched_Inspection_Column']} (deviation: {row['Deviation']:.6f})")
            else:
                print(f"  {i+1}. {row['Column']} (deviation: {row['Deviation']:.6f})")
        
        if len(results_df) > 10:
            print(f"  ... and {len(results_df) - 10} more correlations")
        
        # Show deviation statistics
        print(f"\n[STATS] Deviation statistics:")
        print(f"  - Mean deviation: {results_df['Deviation'].mean():.6f}")
        print(f"  - Std deviation: {results_df['Deviation'].std():.6f}")
        print(f"  - Min deviation: {results_df['Deviation'].min():.6f}")
        print(f"  - Max deviation: {results_df['Deviation'].max():.6f}")
        
        print(f"\n[SUCCESS] EXPECTED OUTCOME ACHIEVED:")
        print(f"   Enhanced Excel output with detailed column mapping information")
        print(f"   Covering materials: {list(results_df['Material'].unique()) if 'Material' in results_df.columns else 'Multiple'}")
        print(f"   Covering inspections: {sorted(list(results_df['Inspection_Number'].unique())) if 'Inspection_Number' in results_df.columns else 'Multiple'}")
        
        print(f"\n[SAMPLE] Sample of results DataFrame:")
        print(results_df.head())
        return results_df
    else:
        print("\n[FAIL] No deviation results calculated")
        print("[INFO] This indicates that the column matching logic needs further refinement")
        return pd.DataFrame()

def process_material_data():
    """
    Main function to process material data from CSV and database tables.
    Processes all materials and their respective inspection tables.
    """
    print("=== Starting Material Data Processing ===")
    
    # Step 1: Get Process S/N from CSV
    print("\n1. Reading CSV data...")
    csv_data = read_csv_with_pandas(FILEPATH)
    
    if csv_data is None or csv_data.empty:
        print("Failed to read CSV data or no data found")
        return None
    
    # Extract Process S/N values and actual S/N values
    process_sn_list = csv_data['PROCESS S/N'].tolist()
    sn_list = csv_data['S/N'].tolist()
    print(f"Process S/N values from CSV: {process_sn_list}")
    print(f"S/N values from CSV: {sn_list}")
    
    # Step 2: Define target materials
    target_materials = ['Casing_Block']
    print(f"Target materials: {target_materials}")
    
    # Step 3: Query process tables
    print("\n2. Querying process tables...")
    # Extract date from CSV data (assuming it's in the first row)
    csv_date = csv_data['DATE'].iloc[0] if not csv_data.empty and 'DATE' in csv_data.columns else None
    print(f"Date from CSV: {csv_date}")
    results = get_process_data_for_materials(process_sn_list, target_materials, csv_date)
    
    if results:
        print("\n=== SUMMARY OF RESULTS ===")
        total_records = 0
        for table_name, data in results.items():
            if data:
                print(f"{table_name}: {len(data)} records")
                total_records += len(data)
            else:
                print(f"{table_name}: No records")
        
        print(f"\nTotal records found across all tables: {total_records}")
        
        # Create a consolidated DataFrame for all results
        all_data = []
        for table_name, data in results.items():
            for record in data:
                record['Source_Table'] = table_name
                all_data.append(record)
        
        if all_data:
            consolidated_df = pd.DataFrame(all_data)
            print("\n=== CONSOLIDATED PROCESS RESULTS ===")
            print(consolidated_df)
            
            # Now query inspection tables for all materials
            print("\n" + "="*60)
            inspection_data = get_material_inspection_data(results)
            
            if inspection_data:
                print(f"\n=== INSPECTION DATA SUMMARY ===")
                total_inspections = 0
                for material_code, lots in inspection_data.items():
                    lot_count = len(lots)
                    total_inspections += lot_count
                    print(f"{material_code}: {lot_count} lot numbers with inspection data")
                
                print(f"\nTotal inspection records retrieved: {total_inspections}")
                
                # Create a DataFrame for inspection data
                inspection_data_list = []
                for material_code, lots in inspection_data.items():
                    for lot_number, data in lots.items():
                        # Check if this row has NaN values
                        has_nan = False
                        for value in data.values():
                            if value is None or (isinstance(value, float) and str(value).lower() == 'nan'):
                                has_nan = True
                                break
                        
                        # Only add rows without NaN values
                        if not has_nan:
                            data_row = {'Material_Code': material_code, 'Lot_Number': lot_number}
                            data_row.update(data)  # Add all inspection data fields
                            inspection_data_list.append(data_row)
                
                # Create DataFrame and map columns based on material type
                inspection_df = pd.DataFrame(inspection_data_list)
                
                # Apply material-specific column mappings
                mapped_dfs = []
                for material_code in inspection_df['Material_Code'].unique():
                    material_df = inspection_df[inspection_df['Material_Code'] == material_code].copy()
                    
                    # Apply appropriate mapping based on material type
                    if material_code.startswith('FM') and (material_code == 'FM05000102' or material_code.endswith('-01A')):
                        material_df = map_frame_inspection_columns(material_df)
                    # Add mappings for other materials here as needed
                    
                    mapped_dfs.append(material_df)
                
                # Combine all mapped DataFrames
                inspection_df = pd.concat(mapped_dfs, ignore_index=True)
                print(f"Created inspection DataFrame with {len(inspection_df)} rows and {len(inspection_df.columns)} columns")
                print(f"Processing ALL materials and lot numbers: {len(inspection_df)} total records")
                print(f"Inspection DataFrame columns: {list(inspection_df.columns)}")
                
                # Display summary of materials and lot numbers being processed
                if not inspection_df.empty:
                    material_summary = inspection_df.groupby('Material_Code')['Lot_Number'].count()
                    print(f"Materials being processed:")
                    for material, count in material_summary.items():
                        print(f"  - {material}: {count} lot number(s)")
                
                # Process all inspection data rows (removed artificial truncation)
                if not inspection_df.empty:
                    print(f"Processing all {len(inspection_df)} inspection data rows")
                
                print(f"\n=== INSPECTION DATA DATAFRAME ===")
                print(inspection_df)
                
                # Get the model code from the first record
                model_code = None
                for table_data in results.values():
                    if table_data and len(table_data) > 0:
                        if 'Model_Code' in table_data[0]:
                            model_code = table_data[0]['Model_Code']
                            break
                
                # If we have a model code, query database_data table
                database_df = None
                if model_code:
                    database_df = get_database_data_for_model(model_code, 100)
                
                # Perform deviation calculations if we have both database and inspection data
                deviation_df = None
                if database_df is not None and not database_df.empty:
                    # Filter database_df to only include Process_#_[material]_Inspection_#_[type]_Data columns
                    filtered_database_df = filter_inspection_columns(database_df)
                    
                    # Remove Material_Code and Lot_Number from inspection_df for deviation calculations
                    inspection_df_for_calc = inspection_df.drop(columns=['Material_Code', 'Lot_Number'], errors='ignore')
                    
                    print(f"\n=== FILTERED DATA FOR DEVIATION CALCULATIONS ===")
                    print(f"Filtered database shape: {filtered_database_df.shape}")
                    print(f"Filtered database columns (first 10): {list(filtered_database_df.columns)[:10]}")
                    print(f"Filtered inspection shape: {inspection_df_for_calc.shape}")
                    print(f"Filtered inspection columns: {list(inspection_df_for_calc.columns)}")
                    
                    deviation_df = perform_deviation_calculations(filtered_database_df, inspection_df_for_calc, process_sn_list, sn_list)
                
                return {
                    'process_data': consolidated_df,
                    'inspection_data': inspection_data,
                    'inspection_dataframe': inspection_df,
                    'database_data': database_df,
                    'deviation_data': deviation_df
                }
            else:
                print("No inspection data found")
                return {
                    'process_data': consolidated_df,
                    'inspection_data': None,
                    'inspection_dataframe': None
                }
        else:
            print("No data found in any process table")
            return None
    else:
        print("Failed to query process tables")
        return None

def extract_material_codes_from_inspection_data(inspection_df):
    """
    Extract unique material codes from inspection data to determine which sheets to create.
    
    Args:
        inspection_df: DataFrame with inspection data containing Material_Code column
        
    Returns:
        List of unique material codes
    """
    if inspection_df is None or inspection_df.empty:
        return []
    
    if 'Material_Code' not in inspection_df.columns:
        print("[WARN] No Material_Code column found in inspection data")
        return []
    
    material_codes = inspection_df['Material_Code'].dropna().unique().tolist()
    print(f"[INFO] Found {len(material_codes)} unique material codes: {material_codes}")
    return material_codes

def filter_deviation_data_by_material(deviation_df, material_code):
    """
    Filter deviation results to only include rows that match the specified material code.
    
    Args:
        deviation_df: DataFrame with deviation calculations
        material_code: Material code to filter by
        
    Returns:
        Filtered DataFrame containing only deviation data for the specified material
    """
    if deviation_df is None or deviation_df.empty:
        return pd.DataFrame()
    
    # Enhanced material pattern mapping based on the sample data
    material_patterns = {
        'EM0580106P': ['Em2p'],
        'EM0580107P': ['Em3p'],
        'FM05000102': ['Frame'],
        'FM05000102-01A': ['Frame'],  # Handle Frame with suffix
        'CSB6400802': ['Casing_Block'],
        'EM0660046P': ['Em2p', 'Em3p'],  # Could match multiple patterns
        'RDB5200200': ['Rod_Blk'],
        'DFB6600600': ['Df_Blk']
    }
    
    # Get patterns for this material code
    patterns = material_patterns.get(material_code, [])
    if not patterns:
        # If no specific pattern, try to infer from material code
        if material_code.startswith('EM'):
            # EM codes typically map to Em2p or Em3p
            if '0580106' in material_code:
                patterns = ['Em2p']
            elif '0580107' in material_code:
                patterns = ['Em3p']
            elif '0660046' in material_code:
                patterns = ['Em2p', 'Em3p']  # This material could match both
            else:
                patterns = ['Em2p', 'Em3p']  # Default for EM codes
        elif material_code.startswith('FM'):
            patterns = ['Frame']
        elif material_code.startswith('CSB'):
            patterns = ['Casing_Block']
        elif material_code.startswith('RDB'):
            patterns = ['Rod_Blk']
        elif material_code.startswith('DFB'):
            patterns = ['Df_Blk']
        else:
            # For unknown patterns, try to match the material code directly
            patterns = [material_code]
    
    # Filter rows where the Column contains any of the patterns
    filtered_rows = []
    for _, row in deviation_df.iterrows():
        column_name = str(row.get('Column', ''))
        material_from_row = str(row.get('Material', '')) if 'Material' in row else ''
        
        # First try to match based on column name
        match_found = any(pattern in column_name for pattern in patterns)
        
        # If no match found and Material field exists, try matching on that
        if not match_found and 'Material' in row:
            match_found = any(pattern in material_from_row for pattern in patterns)
        
        # If still no match, try matching based on material code in column name
        if not match_found:
            # Try to match material code pattern (e.g., FM05000102, EM0580106P)
            if material_code.startswith('FM') and ('FM' in column_name or 'Frame' in column_name):
                match_found = True
            elif material_code.startswith('EM'):
                if '0580106' in material_code and ('EM0580106P' in column_name or 'Em2p' in column_name):
                    match_found = True
                elif '0580107' in material_code and ('EM0580107P' in column_name or 'Em3p' in column_name):
                    match_found = True
            elif material_code.startswith('CSB') and ('CSB' in column_name or 'Casing' in column_name):
                match_found = True
            elif material_code.startswith('RDB') and ('RDB' in column_name or 'Rod' in column_name):
                match_found = True
            elif material_code.startswith('DFB') and ('DFB' in column_name or 'Df' in column_name):
                match_found = True
        
        if match_found:
            filtered_rows.append(row)
    
    if filtered_rows:
        filtered_df = pd.DataFrame(filtered_rows)
        print(f"[INFO] Filtered {len(filtered_df)} deviation rows for material {material_code} using patterns {patterns}")
        return filtered_df
    else:
        print(f"[WARN] No deviation data found for material {material_code} using patterns {patterns}")
        return pd.DataFrame()

def create_material_sheet_data(deviation_df, material_code, inspection_df):
    """
    Create material-specific sheet data with proper column naming.
    
    Args:
        deviation_df: Filtered deviation DataFrame for this material
        material_code: Material code for dynamic column naming
        inspection_df: DataFrame with inspection data from material's inspection table
        
    Returns:
        DataFrame formatted for material sheet
    """
    if deviation_df.empty:
        return pd.DataFrame()
    
    # Create the material sheet with renamed columns
    material_sheet_data = []
    
    # Get inspection data for this material
    material_inspection_data = None
    if not inspection_df.empty:
        if 'Material_Code' in inspection_df.columns:
            material_data = inspection_df[inspection_df['Material_Code'] == material_code]
            if not material_data.empty:
                material_inspection_data = material_data.iloc[0]
        else:
            # If no Material_Code column, use first row of inspection data
            print(f"[WARN] No Material_Code column found in inspection data, using first row")
            material_inspection_data = inspection_df.iloc[0]
    
    for _, row in deviation_df.iterrows():
        # Get the inspection value from the material's inspection data
        inspection_value = ''
        if material_inspection_data is not None:
            # For Frame material, use the exact mapping from fm05000102_inspection table
            if material_code.startswith('FM') and (material_code == 'FM05000102' or material_code.endswith('-01A')):
                # Get the original inspection column name
                db_col = row.get('Column', '')
                match = re.search(r'(Inspection_\d+_(?:Maximum|Minimum|Average))', db_col)
                if match:
                    inspection_col = match.group(1)
                    # Get the mapped column name from our global mapping
                    mapped_col = FRAME_COLUMN_MAPPING.get(inspection_col)
                    if mapped_col and mapped_col in material_inspection_data:
                        try:
                            value = material_inspection_data[mapped_col]


                            if pd.notna(value):
                                numeric_value = pd.to_numeric(value)
                                inspection_value = float(numeric_value)
                            else:
                                print(f"  [WARN] NaN value found for mapped column {mapped_col}")
                        except (ValueError, TypeError) as e:
                            print(f"  [WARN] Could not convert value '{value}' to numeric for mapped column {mapped_col}: {e}")
            else:
                # For other materials, use the matched column directly
                matched_col = row.get('Matched_Inspection_Column')
                if matched_col and matched_col in material_inspection_data:
                    try:
                        value = material_inspection_data[matched_col]
                        if pd.notna(value):
                            numeric_value = pd.to_numeric(value)
                            inspection_value = float(numeric_value)
                        else:
                            print(f"  [WARN] NaN value found for column {matched_col}")
                    except (ValueError, TypeError) as e:
                        print(f"  [WARN] Could not convert value '{value}' to numeric for column {matched_col}: {e}")
        
        # Convert database average to numeric
        db_avg = row.get('Database_Average', '')
        try:
            if pd.notna(db_avg):
                db_avg = float(pd.to_numeric(db_avg))
        except (ValueError, TypeError) as e:
            print(f"  [WARN] Could not convert database average '{db_avg}' to numeric: {e}")
            db_avg = ''

        # For Frame material, use the mapped column name in the output
        if material_code.startswith('FM') and (material_code == 'FM05000102' or material_code.endswith('-01A')):
            db_col = row.get('Column', '')
            match = re.search(r'Inspection_(\d+)_(Maximum|Minimum|Average)', db_col)
            if match:
                insp_num, data_type = match.groups()
                matched_col = f'Inspection_{insp_num}_{data_type}'
            else:
                matched_col = row.get('Matched_Inspection_Column', '')
        else:
            matched_col = row.get('Matched_Inspection_Column', '')

        material_row = {
            'Column': row.get('Column', ''),
            f'Database_Average_{material_code}_Value': db_avg,
            f'{material_code}_Value': inspection_value,
            'Deviation': float(row.get('Deviation', 0)) if pd.notna(row.get('Deviation')) else '',
            'Matched_Inspection_Column': matched_col,
            'Matching_Strategy': 'Direct Frame Mapping' if material_code.startswith('FM') else row.get('Matching_Strategy', '')
        }
        
        material_sheet_data.append(material_row)
    
    return pd.DataFrame(material_sheet_data)

def create_excel_output(process_df, inspection_df, database_df, deviation_df, filename="em_data_output.xlsx"):
    """
    Create an Excel file with material-based sheets, inspection data, and database data.
    
    New structure:
    - Each unique material code gets its own sheet with deviation data
    - Inspection_Data sheet with raw inspection data
    - Database_Data sheet with raw database data
    
    Args:
        process_df: DataFrame with process data (not used in new structure)
        inspection_df: DataFrame with inspection data
        database_df: DataFrame with database data
        deviation_df: DataFrame with deviation calculations
        filename: Name of the Excel file to create
    
    Returns:
        None
    """
    try:
        print(f"\n=== CREATING MATERIAL-BASED EXCEL OUTPUT ===")
        
        # Get all material codes from process data
        material_codes = []
        for _, records in process_df.iterrows():
            if 'Materials' in records and isinstance(records['Materials'], dict):
                # Materials is already a dictionary
                for material_name, material_info in records['Materials'].items():
                    material_codes.append(material_info['Material_Code'])
            elif 'Materials' in records and isinstance(records['Materials'], str):
                # Materials is a string representation of a dictionary
                try:
                    materials = eval(records['Materials'])
                    for material_name, material_info in materials.items():
                        material_codes.append(material_info['Material_Code'])
                except Exception as e:
                    print(f"[WARN] Could not parse Materials column: {e}")
        
        material_codes = list(set(material_codes))  # Remove duplicates
        
        if not material_codes:
            print("[ERROR] No material codes found. Cannot create material-based sheets.")
            return
        
        print(f"[INFO] Found {len(material_codes)} materials to process: {material_codes}")
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            sheets_created = 0
            
            # Create material-based sheets
            print(f"\n[INFO] Creating material-based sheets for {len(material_codes)} materials...")
            
            for material_code in material_codes:
                print(f"\n[PROCESS] Creating sheet for material: {material_code}")
                
                # Filter deviation data for this material
                material_deviation_df = filter_deviation_data_by_material(deviation_df, material_code)
                
                if not material_deviation_df.empty:
                    # Create properly formatted material sheet data
                    material_sheet_df = create_material_sheet_data(material_deviation_df, material_code, inspection_df)
                    
                    if not material_sheet_df.empty:
                        # Write to Excel sheet named after the material code
                        sheet_name = material_code
                        material_sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        sheets_created += 1
                        print(f"  [OK] Created sheet '{sheet_name}' with {len(material_sheet_df)} rows")
                    else:
                        print(f"  [WARN] No formatted data created for material {material_code}")
                else:
                    print(f"  [WARN] No deviation data found for material {material_code}")
            
            # Create Inspection_Data sheet
            if inspection_df is not None and not inspection_df.empty:
                inspection_df.to_excel(writer, sheet_name='Inspection_Data', index=False)
                sheets_created += 1
                print(f"  [OK] Created 'Inspection_Data' sheet with {len(inspection_df)} rows")
            
            # Create Database_Data sheet
            if database_df is not None and not database_df.empty:
                database_df.to_excel(writer, sheet_name='Database_Data', index=False)
                sheets_created += 1
                print(f"  [OK] Created 'Database_Data' sheet with {len(database_df)} rows")
            
            # Create Deviation_Data sheet with raw deviation calculations
            if deviation_df is not None and not deviation_df.empty:
                deviation_df.to_excel(writer, sheet_name='Deviation_Data', index=False)
                sheets_created += 1
                print(f"  [OK] Created 'Deviation_Data' sheet with {len(deviation_df)} rows")
            
            print(f"\n=== EXCEL FILE CREATED ===")
            print(f"Excel file '{filename}' created successfully!")
            print(f"Total sheets created: {sheets_created}")
            print(f"Material sheets: {len(material_codes)}")
            print(f"Data sheets: 3 (Inspection_Data, Database_Data, Deviation_Data)")
    
    except Exception as e:
        print(f"[ERROR] Error creating Excel file: {e}")
        import traceback
        traceback.print_exc()


#%%
# Execute the main processing function
if __name__ == "__main__":
    # Process data for all materials
    result = process_material_data()
    
    # Display the inspection data DataFrame if available
    if result and 'inspection_dataframe' in result and result['inspection_dataframe'] is not None:
        print("\n=== FINAL INSPECTION DATA OUTPUT ===")
        print(result['inspection_dataframe'])
        print("\nData shape:", result['inspection_dataframe'].shape)
        print("Columns:", list(result['inspection_dataframe'].columns))
        
        # DEBUG: Let's see what the real inspection data looks like
        print("\n=== DEBUG: REAL INSPECTION DATA ANALYSIS ===")
        inspection_df = result['inspection_dataframe']
        print("Sample values from inspection data:")
        for col in inspection_df.columns:
            if col not in ['Material_Code', 'Lot_Number']:
                try:
                    val = inspection_df[col].iloc[0]
                    print(f"  {col}: {val} (type: {type(val)})")
                except:
                    print(f"  {col}: <error reading value>")
    
    # Display the deviation data DataFrame if available
    if result and 'deviation_data' in result and result['deviation_data'] is not None:
        print("\n=== DEVIATION DATA OUTPUT ===")
        print(result['deviation_data'])
        print("\nData shape:", result['deviation_data'].shape)
        print("Columns:", list(result['deviation_data'].columns))
    else:
        print("\n=== NO DEVIATION DATA - DEBUGGING ===")
        if result and 'database_data' in result and result['database_data'] is not None:
            print("Database data is available")
            print(f"Database shape: {result['database_data'].shape}")
            print(f"Database columns (first 10): {list(result['database_data'].columns)[:10]}")
        else:
            print("No database data available")
            
        if result and 'inspection_dataframe' in result and result['inspection_dataframe'] is not None:
            print("Inspection data is available")
            print(f"Inspection shape: {result['inspection_dataframe'].shape}")
            print(f"Inspection columns: {list(result['inspection_dataframe'].columns)}")
        else:
            print("No inspection data available")
    
    # Create Excel file with all data
    if result:
        print("\n=== CREATING EXCEL OUTPUT ===")
        create_excel_output(
            process_df=result.get('process_data'),
            inspection_df=result.get('inspection_dataframe'),
            database_df=result.get('database_data'),
            deviation_df=result.get('deviation_data'),
            filename="em_data_output.xlsx"
        )
        
        # Additional confirmation
        
        if os.path.exists("em_data_output.xlsx"):
            file_size = os.path.getsize("em_data_output.xlsx")
            print(f"[OK] Excel file created successfully: em_data_output.xlsx ({file_size} bytes)")
        else:
            print("[X] Excel file was not created")


# %%

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