#%%
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine

pd.set_option('display.max_columns', None)  # Show all columns in DataFrame output

file_path = r'\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled\PICompiled2025-07-11.csv'

def read_csv_with_pandas(file_path):

    try:
        piCompiled = pd.read_csv(file_path)
        print("CSV successfully loaded into a DataFrame!")
        # print(piCompiled.head())  # Show first few rows
        return piCompiled[['MODEL CODE', 'PROCESS S/N']]
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None
    
# Working MySQL connection code, but commented out for now
def one_read_from_mysql():
    conn = mysql.connector.connect(
        host='192.168.2.148',
        user='hpi.python',
        password='hpi.python',
        database='fc_1_data_db'
    )
    cursor = conn.cursor()

    # Execute query
    cursor.execute('SELECT * FROM database_data')
    
    # Fetch data
    results = cursor.fetchall()

    # Get column names
    column_names = [desc[0] for desc in cursor.description]

    # Create DataFrame
    df = pd.DataFrame(results, columns=column_names)
    exclude_cols = ['DATETIME', 'TIME', ]

    df_cleaned = df.drop(columns=exclude_cols, errors='ignore')

    conn.close()

    print("Data successfully loaded into a DataFrame!")
    print(df.head())
    # return df

latest_run = read_csv_with_pandas(file_path).tail(1)

df_database_data = one_read_from_mysql()


# %%
