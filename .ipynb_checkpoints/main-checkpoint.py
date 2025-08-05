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


def main():
    csv_result = load_csv(FILEPATH)
    if not csv_result:
        return
    last_model_code, last_process_sn, last_date = csv_result

    all_results = []
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Loop through all process indices 1 to 6
    for i in range(1, 7):
        process_data = query_process_data(cursor, i, last_process_sn)
        print(f"Process {i} - Found rows: {len(process_data)}")  # ✅ Debug
        for result in process_data:
            model_code = result.get("MODEL_CODE") or result.get(f"Process_{i}_Model_Code")  # ✅ Fix
            print(f"Model Code for Process {i}: {model_code}")  # ✅ Debug
            if model_code:
                inspection_data = query_database_data(cursor, i, model_code)
                print(f"Process {i} - Inspection results for model '{model_code}': {len(inspection_data)}")  # ✅ Debug
                all_results.extend(inspection_data)

    cursor.close()
    conn.close()

    results_df = pd.DataFrame(all_results)
    print(results_df)

    if all_results:
        df = pd.DataFrame(all_results)

        # Select only columns matching the inspection data pattern
        pattern = r'^Process_\d+_.+_Inspection_\d+_(Maximum|Average|Minimum)_Data$'
        inspection_cols = [col for col in df.columns if re.match(pattern, col)]
        if inspection_cols:
            print("\nInspection Data Columns (showing head):")
            print(df[inspection_cols].head())
            # Convert inspection columns to numeric if possible
            for col in inspection_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            # Calculate and print the total average for each inspection data column
            numeric_inspection_cols = df[inspection_cols].select_dtypes(include='number')
            if not numeric_inspection_cols.empty:
                averages = numeric_inspection_cols.mean()
                print("\nTotal Average for Each Inspection Data Column:")
                print(averages)
                # Save the inspection data columns to an Excel file
                output_path = 'inspection_data_output.xlsx'
                df[inspection_cols].to_excel(output_path, index=False)
                print(f"\nInspection data saved to {output_path}")
                # Save the averages to a separate DataFrame and Excel file
                averages_df = averages.reset_index()
                averages_df.columns = ['Column', 'Average']
                averages_output_path = 'inspection_data_averages.xlsx'
                averages_df.to_excel(averages_output_path, index=False)
                print(f"Averages saved to {averages_output_path}")
            else:
                print("No numeric inspection data columns found for averaging.")
        else:
            print("No inspection data columns found matching the pattern.")
    else:
        print("No results to compile into DataFrame.")


#%% Execute
if __name__ == '__main__':
    main()
# %%
      