# Quick test to check the filtered DataFrame
import pandas as pd
import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def test_filtered_dataframe():
    """Test the filtered database_data DataFrame"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Keywords to filter out
        keywords_to_filter = ['NG', 'TRIAL', 'MASTER PUMP', 'RUNNING', 'RE PI']
        
        # Build keyword filtering conditions
        ng_cause_columns = [
            'Process_1_NG_Cause', 'Process_2_NG_Cause', 'Process_3_NG_Cause',
            'Process_4_NG_Cause', 'Process_5_NG_Cause', 'Process_6_NG_Cause'
        ]
        
        keyword_conditions = []
        for keyword in keywords_to_filter:
            for column in ng_cause_columns:
                keyword_conditions.append(f"{column} NOT LIKE '%{keyword}%'")
        
        keyword_filter = " AND ".join(keyword_conditions)
        
        # Execute the query
        query = f"""
        SELECT *
        FROM database_data
        WHERE ({keyword_filter})
        AND PASS_NG = '1'
        ORDER BY DATE DESC
        LIMIT 100
        """
        
        print("Executing filtered query...")
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            df = pd.DataFrame(results)
            print(f"✅ Retrieved {len(df)} rows")
            print(f"📊 DataFrame shape: {df.shape}")
            print(f"📋 Columns: {len(df.columns)}")
            
            # Show first few column names
            print("\n📝 First 10 columns:")
            for i, col in enumerate(df.columns[:10], 1):
                print(f"  {i}. {col}")
            
            # Look for Df_Blk columns
            df_blk_cols = [col for col in df.columns if 'Df_Blk' in col]
            print(f"\n🎯 Found {len(df_blk_cols)} Df_Blk columns:")
            for col in df_blk_cols[:5]:  # Show first 5
                print(f"  - {col}")
            
            # Show PASS_NG values
            if 'PASS_NG' in df.columns:
                print(f"\n✅ PASS_NG values: {df['PASS_NG'].unique()}")
            
            # Show date range
            if 'DATE' in df.columns:
                dates = df['DATE'].dropna()
                if not dates.empty:
                    print(f"\n📅 Date range: {dates.min()} to {dates.max()}")
            
            return df
        else:
            print("❌ No results returned from query")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()

# Run the test
if __name__ == "__main__":
    df = test_filtered_dataframe()
