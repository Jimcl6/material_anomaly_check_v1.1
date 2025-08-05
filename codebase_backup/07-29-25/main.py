#%% Imports and Constants
import os
import datetime
import pandas as pd
import mysql.connector
import re
import sys
import tkinter as tk
from tkinter import messagebox

NETWORK_DIR = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
FILENAME = f"PICompiled2025-07-11.csv"
FILEPATH = os.path.join(NETWORK_DIR, FILENAME)
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}
EXCLUDE_SUBSTRINGS = ['REPAIRED AT PROCESS', 'NG AT', 'RE PI', 'MASTER PUMP']

#  Functions
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

    last_model_code = df["MODEL CODE"].iloc[-1]
    last_process_sn = df["PROCESS S/N"].iloc[-1]
    last_date = df["DATE"].iloc[-1] if "DATE" in df.columns else None

    print("Last CSV Entry:")
    print(df[["MODEL CODE", "PROCESS S/N"]].tail(1))
    return last_model_code, last_process_sn, last_date

def query_process_data(cursor, table_index, process_sn):
    table_name = f"process{table_index}_data"
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = [row[0] for row in cursor.fetchall()]
    
    material_cols = [col for col in columns if re.match(f"Process_{table_index}_.+", col) and not col.endswith(("_S_N", "_Lot_No"))]
    sn_col = f"Process_{table_index}_S_N" if f"Process_{table_index}_S_N" in columns else None
    lot_no_cols = [col for col in columns if col.endswith("_Lot_No")]
    date_col = f"Process_{table_index}_DATE" if f"Process_{table_index}_DATE" in columns else None
    time_col = f"Process_{table_index}_TIME" if f"Process_{table_index}_TIME" in columns else None

    # Dynamically find model code column
    model_code_col = "MODEL_CODE" if "MODEL_CODE" in columns else f"Process_{table_index}_Model_Code" if f"Process_{table_index}_Model_Code" in columns else None
    
    select_cols = [col for col in [date_col, model_code_col, sn_col] if col] + material_cols + lot_no_cols


    exclude = [
        f"Process_{table_index}_DATA_NO", f"Process_{table_index}_DateTime",
        f"Process_{table_index}_TIME", f"Process_{table_index}_ID",
        f"Process_{table_index}_NAME", f"Process_{table_index}_Regular_Contractual"
    ]
    select_cols = [col for col in select_cols if col not in exclude]

    where_clause = f"WHERE {sn_col} = %s" if sn_col and process_sn else ""
    order_clause = " ORDER BY " + ", ".join(filter(None, [f"{date_col} DESC", f"{time_col} DESC"]))
    query = f"SELECT {', '.join(select_cols)} FROM {table_name} {where_clause} {order_clause} LIMIT 1"

    cursor.execute(query, (process_sn,) if process_sn else ())
    rows = cursor.fetchall()
    return [dict(zip(select_cols, row)) for row in rows]

def query_database_data(cursor, process_index, model_code):
    cursor.execute("SHOW COLUMNS FROM database_data")
    db_cols = [row[0] for row in cursor.fetchall()]

    # Match columns like: Process_[1-6]_<Material>_Inspection_[3|4|5|10]_(Minimum|Average|Maximum)_Data
    pattern = re.compile(
        r'^Process_[1-6]_.+_Inspection_(3|4|5|10)_(Minimum|Average|Maximum)_Data$'
    )
    matching_cols = [col for col in db_cols if pattern.match(col)]

    if not matching_cols:
        print(f"No matching inspection columns found for Process {process_index}")
        return []

    # Also add a DATE column if present
    date_col = next((col for col in db_cols if col.lower() == 'date'), None)
    if date_col and date_col not in matching_cols:
        matching_cols = [date_col] + matching_cols

    # Normalize model code column name
    model_code_col = None
    for col in db_cols:
        if col.lower() == 'model_code':
            model_code_col = col
            break

    if not model_code_col:
        print("No 'Model_Code' column found in database_data.")
        return []

    query = f"SELECT {', '.join(matching_cols)} FROM database_data WHERE {model_code_col} = %s"
    cursor.execute(query, (model_code,))
    rows = cursor.fetchall()

    filtered = [
        dict(zip(matching_cols, row))
        for row in rows
        if not any(sub in str(cell) for sub in EXCLUDE_SUBSTRINGS for cell in row)
    ]

    return filtered

def query_em0580106p_inspection(cursor, lot_number):
    """Query em0580106p_inspection table using lot number"""
    if not lot_number:
        return None
    
    # Define the columns we want to extract
    target_columns = [
        'Lot_Number',
        'Inspection_3_Resistance_Maximum', 'Inspection_3_Resistance_Average', 'Inspection_3_Resistance_Minimum',
        'Inspection_4_Dimension_Maximum', 'Inspection_4_Dimension_Average', 'Inspection_4_Dimension_Minimum',
        'Inspection_5_Dimension_Maximum', 'Inspection_5_Dimension_Average', 'Inspection_5_Dimension_Minimum',
        'Inspection_10_Pull_Test'
    ]

    
    # Get all columns from the table
    cursor.execute("SHOW COLUMNS FROM em0580106p_inspection")
    available_cols = [row[0] for row in cursor.fetchall()]
    
    # Filter to only include columns that exist in the table
    existing_cols = [col for col in target_columns if col in available_cols]
    
    if not existing_cols:
        print(f"No matching columns found in em0580106p_inspection for lot {lot_number}")
        return None
    
    # Query the table
    query = f"SELECT {', '.join(existing_cols)} FROM em0580106p_inspection WHERE Lot_Number = %s"
    cursor.execute(query, (lot_number,))
    rows = cursor.fetchall()
    
    if rows:
        result = dict(zip(existing_cols, rows[0]))
        print(f"Found em0580106p_inspection data for lot {lot_number}")
        return result
    else:
        print(f"No data found in em0580106p_inspection for lot {lot_number}")
        return None

def calculate_deviation(database_avg, inspection_value):
    """Calculate deviation: (database_avg - inspection_value) / database_avg"""
    # Convert both values to numeric, handling strings and mixed types
    try:
        db_avg_numeric = pd.to_numeric(database_avg, errors='coerce')
        inspection_numeric = pd.to_numeric(inspection_value, errors='coerce')
        
        if pd.isna(db_avg_numeric) or pd.isna(inspection_numeric) or db_avg_numeric == 0:
            return None
        return (db_avg_numeric - inspection_numeric) / db_avg_numeric
    except Exception as e:
        print(f"Error calculating deviation: {e}")
        return None





# Execute
if __name__ == '__main__':
    csv_result = load_csv(FILEPATH)
    last_model_code, last_process_sn, last_date = csv_result

    all_results = []
    em0580106p_data = {}  # Store em0580106p_inspection data by lot number
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Loop through all process indices 1 to 6
    for i in range(1, 7):
        process_data = query_process_data(cursor, 1, 94)
        print(f"Process {i} - Found rows: {len(process_data)}")  # ✅ Debug
        for result in process_data:
            model_code = result.get("MODEL_CODE") or result.get(f"Process_{i}_Model_Code")  # ✅ Fix
            print(f"Model Code for Process {i}: {model_code}")  # ✅ Debug
            
            # Extract lot numbers from process data
            lot_numbers = [v for k, v in result.items() if k.endswith('_Lot_No') and v]
            if lot_numbers:
                print(f"Process {i} - Found lot numbers: {lot_numbers}")
            
            # Query em0580106p_inspection for each lot number
            for lot_no in lot_numbers:
                if lot_no not in em0580106p_data:
                    em0580106p_data[lot_no] = query_em0580106p_inspection(cursor, lot_no)
                    if em0580106p_data[lot_no]:
                        print(f"Retrieved em0580106p_inspection data for lot: {lot_no}")
                        print(f"Data: {em0580106p_data[lot_no]}")
            
            if model_code:
                inspection_data = query_database_data(cursor, 1, '60CAT0212P')
                print(f"Process {i} - Inspection results for model '{model_code}': {len(inspection_data)}")  # ✅ Debug
                all_results.extend(inspection_data)

    cursor.close()
    conn.close()

    results_df = pd.DataFrame(all_results)
    
    #%%
    pd.set_option('display.max_rows', None)  # Show all columns in DataFrame
    results_df
    #%%


    
# %%
      