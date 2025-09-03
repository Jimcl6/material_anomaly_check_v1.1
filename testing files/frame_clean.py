import os
import pandas as pd
import mysql.connector
import datetime

x = datetime.datetime.now()

NETWORK_DIR = fr"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
# FILENAME = f"PICompiled{x.year}-{x.strftime("%m")}-{x.strftime('%d')}.csv"
FILENAME = f"PICompiled2025-07-11.csv"
FILEPATH = os.path.join(NETWORK_DIR, FILENAME)
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def read_csv_with_pandas(file_path):
    try:
        piCompiled = pd.read_csv(file_path).tail(1)
        piCompiled["MODEL CODE"] = piCompiled["MODEL CODE"].astype(str).str.replace('"', '', regex=False)
        print("CSV successfully loaded into a DataFrame!")
        return piCompiled[['DATE', 'MODEL CODE', 'PROCESS S/N']]
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

def get_frame_lot_from_process_data(process_sn_list, csv_date):
    """Get Frame lot numbers from process1_data table"""
    connection = create_db_connection()
    if not connection:
        return None
    
    frame_lot_mapping = {}
    try:
        cursor = connection.cursor(dictionary=True)
        for process_sn in process_sn_list:
            query = """
            SELECT Process_1_S_N, Process_1_Frame, Process_1_Frame_Lot_No, Process_1_DATE
            FROM process1_data
            WHERE Process_1_S_N = %s
            AND Process_1_DATE = %s
            AND Process_1_Frame IS NOT NULL
            AND Process_1_Frame != ''
            LIMIT 1
            """
            cursor.execute(query, (process_sn, csv_date))
            row = cursor.fetchone()
            if row:
                frame_lot_mapping[process_sn] = row['Process_1_Frame_Lot_No']
        cursor.close()
        connection.close()
        return frame_lot_mapping
    except Exception as e:
        print(f"Error getting Frame lot numbers: {e}")
        if connection:
            connection.close()
        return None

def get_frame_inspection_data(frame_lot_mapping):
    """Get inspection data from fm05000102_inspection table"""
    if not frame_lot_mapping:
        return pd.DataFrame()
    
    connection = create_db_connection()
    if not connection:
        return pd.DataFrame()
    
    try:
        cursor = connection.cursor(dictionary=True)
        lot_numbers = list(frame_lot_mapping.values())
        placeholders = ','.join(['%s'] * len(lot_numbers))
        
        query = f"""
        SELECT * FROM fm05000102_inspection
        WHERE Lot_Number IN ({placeholders})
        ORDER BY Date DESC
        """
        
        cursor.execute(query, lot_numbers)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error getting Frame inspection data: {e}")
        if connection:
            connection.close()
        return pd.DataFrame()

def get_database_data_for_model(model_code, limit=100):
    """
    Query database_data table with ALL columns from SQL database
    
    Args:
        model_code: The model code to filter by
        limit: Number of records to retrieve (default 100)
    
    Returns:
        DataFrame with complete database data including all columns
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
            'REPAIRED',
            'INSPECTION ONLY',
            'CHANGE PUMP'
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
        
        # Query for ALL columns from database_data table with filtering
        query = f"""
        SELECT *
        FROM database_data
        WHERE Model_Code = %s
        AND PASS_NG = '1'
        AND ({keyword_filter})
        ORDER BY DATE DESC
        LIMIT {limit}
        """
        
        print(f"Executing query for {limit} records (PASS_NG = '1', excluding problematic keywords)")
        print(f"Filtering out keywords: {problematic_keywords}")
        cursor.execute(query, (model_code,))
        results = cursor.fetchall()
        
        if results:
            df = pd.DataFrame(results)
            print(f"Retrieved {len(df)} records from database_data for model {model_code}")
            print(f"Database DataFrame shape: {df.shape}")
            print(f"Database DataFrame has ALL {len(df.columns)} columns from SQL table")
            
            # Show date range if available
            if 'DATE' in df.columns:
                dates = df['DATE'].dropna()
                if not dates.empty:
                    print(f"Historical data date range: {dates.min()} to {dates.max()}")
            
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

def create_frame_excel_output(inspection_df, database_df, output_filename='frame_data_output.xlsx'):
    """Create Excel output with Frame inspection and database data"""
    try:
        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            if not inspection_df.empty:
                inspection_df.to_excel(writer, sheet_name='Frame_Inspection_Data', index=False)
                print(f"  Created 'Frame_Inspection_Data' sheet with {len(inspection_df)} rows")
            
            if database_df is not None and not database_df.empty:
                database_df.to_excel(writer, sheet_name='Database_Data', index=False)
                print(f"  Created 'Database_Data' sheet with {len(database_df)} rows")
        
        print(f"Excel file '{output_filename}' created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False

# Main execution function
def process_frame_material_data():
    """Main function to process Frame material data"""
    print("=== STARTING FRAME MATERIAL DATA PROCESSING ===")
    
    # 1. Read CSV data
    print("\n1. Reading CSV data...")
    csv_data = read_csv_with_pandas(FILEPATH)
    if csv_data is None or csv_data.empty:
        print("Failed to read CSV data")
        return
    
    process_sn_list = csv_data['PROCESS S/N'].tolist()
    model_code = csv_data['MODEL CODE'].iloc[0]
    csv_date = csv_data['DATE'].iloc[0]
    
    print(f"Process S/N list: {process_sn_list}")
    print(f"Model Code: {model_code}")
    print(f"CSV Date: {csv_date}")
    
    # 2. Get Frame lot numbers from process data
    print("\n2. Getting Frame lot numbers from process1_data...")
    frame_lot_mapping = get_frame_lot_from_process_data(process_sn_list, csv_date)
    if not frame_lot_mapping:
        print("No Frame lot numbers found")
        return
    
    print(f"Frame lot mapping: {frame_lot_mapping}")
    
    # 3. Get Frame inspection data
    print("\n3. Getting Frame inspection data...")
    inspection_df = get_frame_inspection_data(frame_lot_mapping)
    print(f"Inspection data shape: {inspection_df.shape}")
    
    # 4. Get database data with ALL columns
    print("\n4. Getting database data with ALL columns...")
    database_df = get_database_data_for_model(model_code, 100)
    if database_df is not None:
        print(f"Database data shape: {database_df.shape}")
    
    # 5. Create Excel output
    print("\n5. Creating Excel output...")
    create_frame_excel_output(inspection_df, database_df, 'frame_data_output.xlsx')
    
    print("\n=== FRAME PROCESSING COMPLETED ===")
    print(f"Inspection data: {inspection_df.shape}")
    print(f"Database data: {database_df.shape if database_df is not None else 'None'}")

if __name__ == "__main__":
    process_frame_material_data()
