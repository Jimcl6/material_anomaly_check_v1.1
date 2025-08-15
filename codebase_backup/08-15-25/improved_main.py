#%% Imports and Constants
import os
import datetime
import pandas as pd
import mysql.connector
import re
import sys
import tkinter as tk
from tkinter import messagebox

NETWORK_DIR = fr"D:\AI_Team\AI Program\Outputs\PICompiled"
FILENAME = f"PICompiled2025-04-30.csv"
FILEPATH = os.path.join(NETWORK_DIR, FILENAME)
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}
EXCLUDE_SUBSTRINGS = ['REPAIRED AT PROCESS', 'NG AT', 'RE PI', 'MASTER PUMP']

#%% Functions
def load_csv(filepath):
    if not os.path.exists(filepath):
        print(f"No file found: {filepath}")
        return None

    df = pd.read_csv(filepath)
    if df.empty:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("No Data", "The file does not contain any data at all.")
        sys.exit()

    required_columns = {"MODEL CODE", "PROCESS S/N"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        print(f"Missing columns: {', '.join(missing)}")
        return None

    print("Last CSV Entry:")
    print(df[["MODEL CODE", "PROCESS S/N"]].tail(1))
    return df


def get_material_columns_from_table(db_config, table_name, process_num):
    """
    Get all material-related columns from a specific process table.
    Returns a dictionary with material codes as keys and column info as values.
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Get all columns from the table
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    
    material_columns = {}
    
    # Pattern to match material columns: Process_X_MaterialName (not ending with _Lot_No)
    material_pattern = rf"^Process_{process_num}_([A-Za-z][A-Za-z0-9_]*[A-Za-z0-9])$"
    lot_pattern = rf"^Process_{process_num}_([A-Za-z][A-Za-z0-9_]*[A-Za-z0-9])_Lot_No$"
    
    # Exclude standard columns that are not materials
    exclude_patterns = [
        rf"^Process_{process_num}_DATA_No$",
        rf"^Process_{process_num}_DateTime$",
        rf"^Process_{process_num}_DATE$",
        rf"^Process_{process_num}_TIME$",
        rf"^Process_{process_num}_Model_Code$",
        rf"^Process_{process_num}_S_N$",
        rf"^Process_{process_num}_ID$",
        rf"^Process_{process_num}_NAME$",
        rf"^Process_{process_num}_Regular_Contractual$",
        rf"^Process_{process_num}_ST$",
        rf"^Process_{process_num}_Actual_Time$",
        rf"^Process_{process_num}_NG_Cause$",
        rf"^Process_{process_num}_Repaired_Action$"
    ]
    
    for col_info in columns:
        col_name = col_info[0]
        
        # Skip if it's an excluded standard column
        if any(re.match(pattern, col_name) for pattern in exclude_patterns):
            continue
            
        # Check if it's a material column (not a lot number column)
        material_match = re.match(material_pattern, col_name)
        if material_match and not col_name.endswith('_Lot_No'):
            material_code = material_match.group(1)
            
            # Check if there's a corresponding lot number column
            lot_col_name = f"{col_name}_Lot_No"
            has_lot_column = any(col[0] == lot_col_name for col in columns)
            
            material_columns[material_code] = {
                'material_column': col_name,
                'lot_column': lot_col_name if has_lot_column else None
            }
    
    conn.close()
    return material_columns


def get_process_dataframes(db_config, num_processes=6, specific_material=None):
    """
    Connects to the database and loads each process#_data table into a DataFrame.
    Dynamically detects material columns and extracts material codes.
    
    Args:
        db_config: Database configuration
        num_processes: Number of process tables to query (default 6)
        specific_material: If specified, only extract data for this material code
    
    Returns:
        Dictionary of DataFrames keyed by process number, with material codes extracted
    """
    conn = mysql.connector.connect(**db_config)
    dataframes = {}
    
    for i in range(1, num_processes + 1):
        table_name = f"process{i}_data"
        
        # Get material columns for this process
        material_columns = get_material_columns_from_table(db_config, table_name, i)
        
        if not material_columns:
            print(f"No material columns found in {table_name}")
            continue
        
        # Filter by specific material if requested
        if specific_material:
            material_columns = {k: v for k, v in material_columns.items() 
                              if k.lower() == specific_material.lower()}
            if not material_columns:
                print(f"Material '{specific_material}' not found in {table_name}")
                continue
        
        # Build dynamic SELECT query
        select_columns = [
            f"Process_{i}_DATE",
            f"Process_{i}_Model_Code", 
            f"Process_{i}_S_N"
        ]
        
        # Add material columns with extracted material codes
        for material_code, col_info in material_columns.items():
            select_columns.append(f"{col_info['material_column']} AS Process_{i}_{material_code}")
            if col_info['lot_column']:
                select_columns.append(f"{col_info['lot_column']} AS Process_{i}_{material_code}_Lot_No")
        
        query = f"""
            SELECT {', '.join(select_columns)}
            FROM {table_name}
        """
        
        print(f"\nQuerying {table_name}:")
        print(f"Found materials: {list(material_columns.keys())}")
        
        df = pd.read_sql(query, conn)
        dataframes[f"process_{i}"] = df
    
    conn.close()
    return dataframes


def extract_material_codes_from_columns(df, process_num):
    """
    Extract material codes from DataFrame column names.
    Useful for post-processing DataFrames.
    
    Args:
        df: DataFrame with process columns
        process_num: Process number (1, 2, 3, etc.)
    
    Returns:
        List of material codes found in the DataFrame
    """
    material_codes = []
    pattern = rf"^Process_{process_num}_([A-Za-z][A-Za-z0-9_]*[A-Za-z0-9])$"
    
    for col in df.columns:
        if not col.endswith('_Lot_No'):  # Skip lot number columns
            match = re.match(pattern, col)
            if match:
                material_code = match.group(1)
                # Exclude standard non-material columns
                if material_code not in ['DATE', 'Model_Code', 'S_N', 'ID', 'NAME', 
                                       'Regular_Contractual', 'ST', 'Actual_Time', 
                                       'NG_Cause', 'Repaired_Action']:
                    material_codes.append(material_code)
    
    return material_codes


# Example usage:
if __name__ == "__main__":
    # Load CSV as before
    df_csv = load_csv(FILEPATH)
    if df_csv is not None:
        print("\nLoaded CSV DataFrame head:")
        print(df_csv.head())

    # Load all process tables into DataFrames with dynamic material detection
    print("\n" + "="*60)
    print("LOADING PROCESS DATA WITH DYNAMIC MATERIAL DETECTION")
    print("="*60)
    
    process_dfs = get_process_dataframes(DB_CONFIG)
    
    for proc, df in process_dfs.items():
        print(f"\n{proc} DataFrame:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("Sample data:")
        print(df.head(2))
        
        # Extract material codes from this process
        process_num = int(proc.split('_')[1])
        materials = extract_material_codes_from_columns(df, process_num)
        print(f"Material codes found: {materials}")
        print("-" * 40)
    
    # Example: Load data for a specific material only
    print("\n" + "="*60)
    print("EXAMPLE: LOADING DATA FOR SPECIFIC MATERIAL 'Em2p'")
    print("="*60)
    
    specific_material_dfs = get_process_dataframes(DB_CONFIG, specific_material="Em2p")
    for proc, df in specific_material_dfs.items():
        if not df.empty:
            print(f"\n{proc} DataFrame (Em2p only):")
            print(df.head())