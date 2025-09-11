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
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Convert process_sn_list to a set for faster lookups
        process_sn_set = set(process_sn_list)
        
        # Process each process table (process1_data through process6_data)
        for process_num in range(1, 7):
            table_name = f"process{process_num}_data"
            
            # Skip if the table doesn't exist
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            if not cursor.fetchone():
                print(f"Table {table_name} does not exist, skipping...")
                continue
                
            print(f"\nProcessing table: {table_name}")
            
            # Build placeholders for the IN clause
            placeholders = ', '.join(['%s'] * len(process_sn_list))
            
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
            
            # Try different date formats if csv_date is provided
            date_formats = []
            if csv_date:
                # Add original format
                date_formats.append(csv_date)
                # Add YYYY/MM/DD format if different
                if '-' in csv_date:
                    date_formats.append(csv_date.replace('-', '/'))
                # Add just date part if it's a timestamp
                if ' ' in csv_date:
                    date_formats.append(csv_date.split(' ')[0])
            
            # Try each date format until we get results
            rows = []
            for date_fmt in date_formats:
                query = f"""
                SELECT {columns_str}
                FROM {table_name}
                WHERE {sn_column} IN ({placeholders}) AND Process_{process_num}_DATE = %s
                """
                params = process_sn_list + [date_fmt]
                print(f"Trying query with date format: {date_fmt}")
                cursor.execute(query, params)
                rows = cursor.fetchall()
                if rows:
                    print(f"Found {len(rows)} rows with date format: {date_fmt}")
                    break
            
            # If no rows found with date filter, try without date
            if not rows:
                print(f"No rows found with date filter, trying without date")
                query = f"""
                SELECT {columns_str}
                FROM {table_name}
                WHERE {sn_column} IN ({placeholders})
                ORDER BY Process_{process_num}_DATE DESC
                """
                cursor.execute(query, process_sn_list)
                rows = cursor.fetchall()
                if rows:
                    print(f"Found {len(rows)} rows without date filter")
            
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
        
        # Use the exact limit requested for consistency with other scripts
        query_limit = limit
        
        # Keywords to filter out before querying
        keywords_to_filter = ['NG', 'TRIAL', 'MASTER PUMP', 'RUNNING', 'RE PI', 'REPAIRED', 'REPAIRED AT']
        
        # Build keyword filtering conditions for NG_Cause columns
        ng_cause_columns = [
            'Process_1_NG_Cause', 'Process_2_NG_Cause', 'Process_3_NG_Cause',
            'Process_4_NG_Cause', 'Process_5_NG_Cause', 'Process_6_NG_Cause'
        ]
        
        # Create WHERE conditions to exclude records with problematic keywords
        keyword_conditions = []
        for keyword in keywords_to_filter:
            for col in ng_cause_columns:
                keyword_conditions.append(f"{col} NOT LIKE '%{keyword}%'")
        
        # Add model code condition
        where_conditions = [f"Model_Code = '{model_code}'"]
        
        # Add keyword conditions if any
        if keyword_conditions:
            where_conditions.append(f"({' AND '.join(keyword_conditions)})")
        
        # Build the final WHERE clause
        where_clause = " AND ".join(where_conditions)
        
        # Query to get all column names
        cursor.execute("SHOW COLUMNS FROM database_data")
        columns = [col[0] for col in cursor.fetchall()]
        
        # Build the query with dynamic columns and filtering
        query = f"""
        SELECT * FROM database_data
        WHERE {where_clause}
        ORDER BY Date DESC
        LIMIT %s
        """
        
        print(f"Executing query with limit: {query_limit}")
        cursor.execute(query, (query_limit,))
        results = cursor.fetchall()
        
        if not results:
            print("No results found with current filters, trying without keyword filtering...")
            # Try again without keyword filtering if no results
            query = f"""
            SELECT * FROM database_data
            WHERE Model_Code = %s
            ORDER BY Date DESC
            LIMIT %s
            """
            cursor.execute(query, (model_code, query_limit))
            results = cursor.fetchall()
        
        print(f"Found {len(results)} records in database_data")
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        # Clean the data
        df = clean_database_data(df)
        
        cursor.close()
        connection.close()
        
        return df
        
    except Exception as e:
        print(f"Error querying database_data: {e}")
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
    
    print(f"\n=== CLEANING DATABASE DATA ===")
    print(f"Original shape: {df.shape}")
    
    # Make a copy to avoid SettingWithCopyWarning
    df_cleaned = df.copy()
    
    # Define keywords to filter out
    keywords_to_filter = ['NG', 'TRIAL', 'MASTER PUMP', 'RUNNING', 'RE PI', 'REPAIRED', 'REPAIRED AT']
    
    # Define critical columns that should never be dropped
    critical_columns = ['PASS_NG', 'DATE', 'Model_Code', 'Process_SN', 'SN']
    
    # 1. Filter out rows where any NG_Cause column contains keywords
    ng_cause_columns = [col for col in df_cleaned.columns if 'NG_Cause' in col]
    
    if ng_cause_columns:
        print(f"Found {len(ng_cause_columns)} NG_Cause columns")
        
        # Create a mask to filter out rows with problematic NG_Cause values
        mask = pd.Series([True] * len(df_cleaned))
        
        for col in ng_cause_columns:
            if col in df_cleaned.columns and df_cleaned[col].dtype == 'object':
                for keyword in keywords_to_filter:
                    mask = mask & (~df_cleaned[col].astype(str).str.contains(keyword, case=False, na=False))
        
        # Apply the mask to filter rows
        df_cleaned = df_cleaned[mask].copy()
        print(f"After filtering NG_Cause rows: {df_cleaned.shape}")
    
    # 2. Filter out columns that contain problematic keywords in their names
    # But preserve critical columns
    columns_to_drop = []
    for col in df_cleaned.columns:
        # Skip critical columns
        if col in critical_columns:
            continue
            
        # Check if column name contains any of the keywords
        if any(keyword.lower() in col.lower() for keyword in ['trial', 'test', 'temp', 'old']):
            columns_to_drop.append(col)
    
    if columns_to_drop:
        print(f"Dropping {len(columns_to_drop)} columns with problematic names")
        df_cleaned = df_cleaned.drop(columns=columns_to_drop)
    
    # 3. Filter out columns where all values are the same or mostly null
    columns_to_drop = []
    for col in df_cleaned.columns:
        # Skip critical columns
        if col in critical_columns:
            continue
            
        # Skip if not enough data to make a decision
        if len(df_cleaned) < 2:
            continue
            
        # Check if all values are the same
        if df_cleaned[col].nunique() == 1:
            columns_to_drop.append(col)
        # Check if more than 90% null
        elif df_cleaned[col].isnull().mean() > 0.9:
            columns_to_drop.append(col)
    
    if columns_to_drop:
        print(f"Dropping {len(columns_to_drop)} columns with no variation or mostly null values")
        df_cleaned = df_cleaned.drop(columns=columns_to_drop)
    
    print(f"Final cleaned shape: {df_cleaned.shape}")
    print(f"Columns preserved: {', '.join(df_cleaned.columns.tolist())}")
    
    return df_cleaned

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
    
    print("\n=== FILTERING INSPECTION COLUMNS ===")
    print(f"Original columns: {len(df.columns)}")
    
    # Define patterns for inspection columns
    inspection_patterns = [
        r'Inspection_\d+_',  # Inspection_1_, Inspection_2_, etc.
        r'Inspection_[A-Za-z]+_',  # Inspection_Minimum_, Inspection_Average_, etc.
        r'Process_\d+_Inspection',  # Process_1_Inspection, etc.
        r'Inspection_\d+_[A-Za-z]+_',  # Inspection_1_Minimum_, etc.
        r'Inspection[A-Za-z]+_\d+_',  # InspectionMin1_, InspectionMax1_, etc.
        r'Inspection[A-Za-z]+_',  # InspectionMin_, InspectionMax_, etc.
        r'Inspection_\d+$',  # Inspection_1, Inspection_2, etc.
        r'Inspection_[A-Za-z]+$',  # Inspection_Min, Inspection_Max, etc.
    ]
    
    # Also include common measurement columns
    measurement_keywords = [
        'Measurement', 'Value', 'Result', 'Data', 'Resistance',
        'Dimension', 'Pull', 'Force', 'Current', 'Voltage', 'Temp',
        'Min', 'Max', 'Avg', 'Average', 'Mean', 'Std', 'Deviation'
    ]
    
    # Create a regex pattern to match any of the inspection patterns or measurement keywords
    pattern = '|'.join(inspection_patterns + measurement_keywords)
    
    # Find columns that match any of the patterns (case insensitive)
    inspection_columns = [
        col for col in df.columns 
        if re.search(pattern, col, re.IGNORECASE) and 
           not any(keyword.lower() in col.lower() for keyword in ['NG', 'Cause', 'Comment', 'Note'])
    ]
    
    # Always include critical columns if they exist
    critical_columns = ['PASS_NG', 'DATE', 'Model_Code', 'Process_SN', 'SN', 'Lot_Number']
    for col in critical_columns:
        if col in df.columns and col not in inspection_columns:
            inspection_columns.append(col)
    
    # Filter the DataFrame to only include inspection columns
    filtered_df = df[inspection_columns].copy()
    
    print(f"Filtered columns: {len(filtered_df.columns)}")
    print(f"Inspection columns: {', '.join(filtered_df.columns.tolist())}")
    
    return filtered_df

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
    if pd.isna(value) or value is None or value == '':
        return None, False
    
    # If it's already a numeric type, return as is
    if isinstance(value, (int, float, np.number)):
        # Handle numpy numeric types that might have issues with JSON serialization
        return float(value), True
    
    # If it's a string, clean it up first
    if isinstance(value, str):
        # Remove any non-numeric characters except decimal point and negative sign
        cleaned = re.sub(r'[^\d.-]', '', value)
        
        # Handle cases where there are multiple decimal points or negative signs
        if cleaned.count('.') > 1:
            # If multiple decimal points, keep only the first one
            parts = cleaned.split('.')
            cleaned = f"{parts[0]}.{''.join(parts[1:])}"
        
        if '-' in cleaned[1:]:  # Negative sign not at the start
            # Keep only the first negative sign at the start if present
            if cleaned.startswith('-'):
                cleaned = f"-{cleaned[1:].replace('-', '')}"
            else:
                cleaned = cleaned.replace('-', '')
        
        # Handle empty string after cleaning
        if not cleaned or cleaned == '.' or cleaned == '-':
            return None, False
        
        try:
            return float(cleaned), True
        except (ValueError, TypeError) as e:
            if column_name:
                print(f"  [CONVERSION] Failed to convert value in column '{column_name}': '{value}' to float")
            return None, False
    
    # For any other type, try direct conversion
    try:
        return float(value), True
    except (ValueError, TypeError) as e:
        if column_name:
            print(f"  [CONVERSION] Failed to convert value in column '{column_name}': '{value}' to float")
        return None, False

def perform_deviation_calculations(database_df, inspection_df, process_sn_list=None, sn_list=None, csv_date=None):
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
    print("\n=== PERFORMING DEVIATION CALCULATIONS ===")
    
    if database_df is None or database_df.empty:
        print("  [ERROR] No database data provided for deviation calculations")
        return None
    
    if inspection_df is None or inspection_df.empty:
        print("  [ERROR] No inspection data provided for deviation calculations")
        return None
    
    print(f"  Database data shape: {database_df.shape}")
    print(f"  Inspection data shape: {inspection_df.shape}")
    
    # Make copies to avoid modifying the original DataFrames
    db_df = database_df.copy()
    insp_df = inspection_df.copy()
    
    # Convert all column names to strings to avoid any issues
    db_df.columns = db_df.columns.astype(str)
    insp_df.columns = insp_df.columns.astype(str)
    
    # Get the model code from the database data (should be the same for all rows)
    if 'Model_Code' in db_df.columns and not db_df.empty:
        model_code = db_df['Model_Code'].iloc[0]
        print(f"  Model code from database data: {model_code}")
    else:
        print("  [WARNING] No Model_Code found in database data")
        model_code = "UNKNOWN"
    
    # Get the process S/N and S/N from the inspection data if available
    process_sn = None
    sn = None
    
    if process_sn_list and len(process_sn_list) > 0:
        process_sn = process_sn_list[0]
        print(f"  Process S/N from input: {process_sn}")
    elif 'Process_SN' in insp_df.columns and not insp_df.empty:
        process_sn = insp_df['Process_SN'].iloc[0]
        print(f"  Process S/N from inspection data: {process_sn}")
    
    if sn_list and len(sn_list) > 0:
        sn = sn_list[0]
        print(f"  S/N from input: {sn}")
    elif 'SN' in insp_df.columns and not insp_df.empty:
        sn = insp_df['SN'].iloc[0]
        print(f"  S/N from inspection data: {sn}")
    
    # Get the date from the inspection data if available
    inspection_date = None
    if 'Date' in insp_df.columns and not insp_df.empty:
        inspection_date = insp_df['Date'].iloc[0]
        print(f"  Inspection date: {inspection_date}")
    elif csv_date:
        inspection_date = csv_date
        print(f"  Using CSV date: {inspection_date}")
    
    # Initialize the result DataFrame
    result_columns = [
        'Model_Code', 'Process_SN', 'SN', 'Date', 'Material', 'Inspection',
        'Parameter', 'Current_Value', 'Historic_Avg', 'Deviation_Percent', 'Status'
    ]
    result_data = []
    
    # Define the materials and their corresponding prefixes
    materials = {
        'Frame': 'Frame',
        'Em2p': 'Em2p',
        'Em3p': 'Em3p',
        'Casing_Block': 'Casing_Block',
        'Rod_Blk': 'Rod_Blk',
        'Df_Blk': 'Df_Blk'
    }
    
    # Process each material
    for material_name, material_prefix in materials.items():
        print(f"\n  Processing material: {material_name}")
        
        # Get the material-specific columns from the inspection data
        material_cols = [col for col in insp_df.columns if material_prefix.lower() in col.lower()]
        
        if not material_cols:
            print(f"    No columns found for material: {material_name}")
            continue
        
        print(f"    Found {len(material_cols)} columns for {material_name}")
        
        # Process each inspection column
        for col in material_cols:
            # Skip non-numeric columns
            if col in ['Material_Code', 'Lot_Number', 'Process_SN', 'SN', 'Date', 'Model_Code']:
                continue
            
            # Get the current value from inspection data
            if col not in insp_df.columns or insp_df[col].isna().all():
                print(f"    [SKIP] Column {col} not found in inspection data or all NaN")
                continue
                
            current_value = insp_df[col].iloc[0]
            
            # Skip if current value is not numeric or is NaN
            if pd.isna(current_value) or str(current_value).strip() in ['', 'NaN', 'nan', 'None']:
                print(f"    [SKIP] No valid current value for {col}")
                continue
            
            # Try to convert to float
            try:
                current_value_float = float(current_value)
            except (ValueError, TypeError):
                print(f"    [SKIP] Could not convert current value '{current_value}' to float for {col}")
                continue
            
            # Find matching columns in database data
            matching_db_cols = [db_col for db_col in db_df.columns if col.lower() in db_col.lower()]
            
            if not matching_db_cols:
                print(f"    [WARNING] No matching columns found in database data for {col}")
                continue
            
            # Use the first matching column (should be the most relevant)
            db_col = matching_db_cols[0]
            
            # Get historic values from database data
            historic_values = db_df[db_col].dropna()
            
            if len(historic_values) == 0:
                print(f"    [WARNING] No historic values found for {db_col}")
                continue
            
            # Convert to numeric, coercing errors to NaN
            historic_values = pd.to_numeric(historic_values, errors='coerce').dropna()
            
            if len(historic_values) == 0:
                print(f"    [WARNING] No valid numeric historic values for {db_col}")
                continue
            
            # Calculate historic average
            historic_avg = historic_values.mean()
            
            # Calculate deviation percentage
            if historic_avg != 0:
                deviation_pct = ((current_value_float - historic_avg) / abs(historic_avg)) * 100
            else:
                deviation_pct = float('inf') if current_value_float != 0 else 0.0
            
            # Determine status based on deviation threshold (e.g., ±5%)
            threshold = 5.0  # 5% threshold for warning
            if abs(deviation_pct) > threshold:
                status = 'Warning'
            else:
                status = 'Normal'
            
            # Extract inspection number and parameter name if possible
            inspection_num = '1'  # Default
            param_name = col
            
            # Try to extract inspection number from column name
            inspection_match = re.search(r'(?i)inspection[_-]?(\d+)', col)
            if inspection_match:
                inspection_num = inspection_match.group(1)
                param_name = col.replace(f'Inspection_{inspection_num}_', '').replace(f'Inspection{inspection_num}_', '')
            
            # Add to results
            result_data.append({
                'Model_Code': model_code,
                'Process_SN': process_sn,
                'SN': sn,
                'Date': inspection_date,
                'Material': material_name,
                'Inspection': f'Inspection {inspection_num}',
                'Parameter': param_name,
                'Current_Value': current_value_float,
                'Historic_Avg': historic_avg,
                'Deviation_Percent': deviation_pct,
                'Status': status
            })
    
    # Create the result DataFrame
    if not result_data:
        print("  [WARNING] No deviation calculations performed - no valid data found")
        return None
    
    result_df = pd.DataFrame(result_data, columns=result_columns)
    print(f"  Generated {len(result_df)} deviation calculations")
    
    return result_df

def process_material_data():
    """
    Main function to process material data from CSV and database tables.
    Processes all materials and their respective inspection tables.
    """
    print("\n" + "="*80)
    print("STARTING MATERIAL DATA PROCESSING")
    print("="*80)
    
    # Read the CSV file
    print("\n=== READING CSV FILE ===")
    csv_data = read_csv_with_pandas(FILEPATH)
    
    if csv_data is None or csv_data.empty:
        print("No data found in CSV or error reading CSV")
        return
    
    print("\nCSV Data:")
    print(csv_data)
    
    # Extract process serial number, model code, and date from CSV
    process_sn = csv_data['PROCESS S/N'].iloc[0]
    model_code = csv_data['MODEL CODE'].iloc[0]
    csv_date = csv_data['DATE'].iloc[0]
    sn = csv_data['S/N'].iloc[0]
    
    print(f"\nProcessing data for:")
    print(f"  Process S/N: {process_sn}")
    print(f"  Model Code: {model_code}")
    print(f"  Date: {csv_date}")
    print(f"  S/N: {sn}")
    
    # Define target materials to search for
    target_materials = ['Em2p', 'Em3p', 'Frame', 'Casing_Block', 'Rod_Blk', 'Df_Blk']
    
    # Get process data for all materials
    print("\n=== GETTING PROCESS DATA FOR MATERIALS ===")
    material_results = get_process_data_for_materials([process_sn], target_materials, csv_date)
    
    if not material_results:
        print("No material results found in process data")
        return
    
    # Get inspection data for all materials
    print("\n=== GETTING INSPECTION DATA FOR MATERIALS ===")
    inspection_data = get_material_inspection_data(material_results)
    
    if not inspection_data:
        print("No inspection data found for any materials")
        return
    
    # Get database data for the model
    print("\n=== GETTING DATABASE DATA FOR MODEL ===")
    database_data = get_database_data_for_model(model_code, limit=100)
    
    if database_data is None or database_data.empty:
        print("No database data found for model")
        return
    
    # Convert inspection data to DataFrame for deviation calculations
    inspection_dfs = []
    for material_code, lot_data in inspection_data.items():
        if not lot_data:
            continue
            
        # Get the first lot's data (for simplicity, or you could process all lots)
        lot_number, data = next(iter(lot_data.items()))
        
        # Convert to DataFrame and add material code and lot number
        df = pd.DataFrame([data])
        df['Material_Code'] = material_code
        df['Lot_Number'] = lot_number
        
        # Add Process_SN and SN if available
        if 'Process_SN' not in df.columns:
            df['Process_SN'] = process_sn
        if 'SN' not in df.columns:
            df['SN'] = sn
        if 'Date' not in df.columns:
            df['Date'] = csv_date
        
        inspection_dfs.append(df)
    
    if not inspection_dfs:
        print("No valid inspection data to process")
        return
    
    # Combine all inspection DataFrames
    inspection_df = pd.concat(inspection_dfs, ignore_index=True)
    
    # Perform deviation calculations
    print("\n=== PERFORMING DEVIATION CALCULATIONS ===")
    deviation_results = perform_deviation_calculations(
        database_data, 
        inspection_df,
        process_sn_list=[process_sn],
        sn_list=[sn],
        csv_date=csv_date
    )
    
    if deviation_results is None or deviation_results.empty:
        print("No deviation calculations performed")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"deviation_calculations_{timestamp}.xlsx")
    
    # Save results to Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Save deviation results
        deviation_results.to_excel(writer, sheet_name='Deviations', index=False)
        
        # Save inspection data
        inspection_df.to_excel(writer, sheet_name='Inspection_Data', index=False)
        
        # Save database data
        database_data.to_excel(writer, sheet_name='Database_Data', index=False)
    
    print(f"\n=== PROCESSING COMPLETE ===")
    print(f"Results saved to: {output_file}")

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
        return []
    
    # Get unique material codes
    material_codes = inspection_df['Material_Code'].dropna().unique().tolist()
    
    # Map to standard material names
    material_mapping = {
        'FM05000102-01A': 'Frame',
        'EM0580106P': 'Em2p',
        'EM0580107P': 'Em3p',
        'CSB6400802': 'Casing_Block',
        'RDB5200200': 'Rod_Blk',
        'DFB6600600': 'Df_Blk'
    }
    
    # Convert to standard names
    standard_materials = []
    for code in material_codes:
        standard_name = material_mapping.get(code, code)
        standard_materials.append(standard_name)
    
    return standard_materials

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
        return None
    
    # Define material code mapping (standard names to codes)
    material_mapping = {
        'Frame': 'FM05000102-01A',
        'Em2p': 'EM0580106P',
        'Em3p': 'EM0580107P',
        'Casing_Block': 'CSB6400802',
        'Rod_Blk': 'RDB5200200',
        'Df_Blk': 'DFB6600600'
    }
    
    # Get the material code if a standard name was provided
    material_code = material_mapping.get(material_code, material_code)
    
    # Filter by material code
    filtered_df = deviation_df[deviation_df['Material'] == material_code].copy()
    
    if filtered_df.empty:
        # Try filtering by material name if code didn't match
        material_name_mapping = {v: k for k, v in material_mapping.items()}
        material_name = material_name_mapping.get(material_code, material_code)
        filtered_df = deviation_df[deviation_df['Material'] == material_name].copy()
    
    return filtered_df

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
    if deviation_df is None or deviation_df.empty:
        return None
    
    # Define column mapping based on material
    column_mapping = {
        'Frame': 'Frame',
        'Em2p': 'Em2p',
        'Em3p': 'Em3p',
        'Casing_Block': 'Casing_Block',
        'Rod_Blk': 'Rod_Blk',
        'Df_Blk': 'Df_Blk'
    }
    
    # Get the material prefix
    material_prefix = column_mapping.get(material_code, material_code)
    
    # Create a copy of the deviation data
    sheet_df = deviation_df.copy()
    
    # Add a column for pass/fail status based on deviation percentage
    sheet_df['Status'] = sheet_df['Deviation_Percent'].apply(
        lambda x: 'PASS' if abs(x) <= 5.0 else 'FAIL'
    )
    
    # Rename columns to match expected format
    sheet_df = sheet_df.rename(columns={
        'Parameter': 'Inspection_Parameter',
        'Current_Value': 'Current_Measurement',
        'Historic_Avg': 'Historical_Average',
        'Deviation_Percent': 'Deviation_%',
        'Status': 'Pass_Fail'
    })
    
    # Reorder columns
    column_order = [
        'Model_Code', 'Process_SN', 'SN', 'Date', 'Material', 'Inspection',
        'Inspection_Parameter', 'Current_Measurement', 'Historical_Average',
        'Deviation_%', 'Pass_Fail'
    ]
    
    # Only include columns that exist in the DataFrame
    column_order = [col for col in column_order if col in sheet_df.columns]
    
    # Add any additional columns from the inspection data
    additional_columns = [col for col in inspection_df.columns if col not in column_order]
    column_order.extend(additional_columns)
    
    # Reorder the DataFrame
    sheet_df = sheet_df[column_order]
    
    return sheet_df

def create_excel_output(process_df, inspection_df, database_df, deviation_df, filename="csb_data_output.xlsx"):
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
    print(f"\n=== CREATING EXCEL OUTPUT: {filename} ===")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath(filename))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a Pandas Excel writer using openpyxl as the engine
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Write each material's deviation data to a separate sheet
        if deviation_df is not None and not deviation_df.empty:
            # Get unique material codes
            material_codes = deviation_df['Material'].unique()
            
            for material_code in material_codes:
                # Filter deviation data for this material
                material_deviations = filter_deviation_data_by_material(deviation_df, material_code)
                
                if material_deviations is None or material_deviations.empty:
                    print(f"  [WARNING] No deviation data for material: {material_code}")
                    continue
                
                # Create material-specific sheet data
                sheet_data = create_material_sheet_data(
                    material_deviations, 
                    material_code, 
                    inspection_df
                )
                
                if sheet_data is None or sheet_data.empty:
                    print(f"  [WARNING] Could not create sheet data for material: {material_code}")
                    continue
                
                # Write to Excel
                sheet_name = f"{material_code}_Deviations"[:31]  # Excel sheet name limit
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  Created sheet: {sheet_name} with {len(sheet_data)} rows")
        
        # Write inspection data to a sheet
        if inspection_df is not None and not inspection_df.empty:
            inspection_df.to_excel(writer, sheet_name='Inspection_Data', index=False)
            print(f"  Created sheet: Inspection_Data with {len(inspection_df)} rows")
        
        # Write database data to a sheet
        if database_df is not None and not database_df.empty:
            database_df.to_excel(writer, sheet_name='Database_Data', index=False)
            print(f"  Created sheet: Database_Data with {len(database_df)} rows")
    
    print(f"Excel file created successfully: {os.path.abspath(filename)}")


#%%
# Execute the main processing function
if __name__ == "__main__":
    # Check if running in interactive mode (like Jupyter notebook)
    try:
        get_ipython()
        INTERACTIVE = True
    except:
        INTERACTIVE = False
    
    if INTERACTIVE:
        print("Running in interactive mode. Call process_material_data() to start processing.")
    else:
        # Run the main processing function
        process_material_data()
