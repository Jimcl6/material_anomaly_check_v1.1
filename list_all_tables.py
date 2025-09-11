import mysql.connector
from mysql.connector import Error

def list_all_tables():
    """List all tables in the database"""
    try:
        conn = mysql.connector.connect(
            host='192.168.2.148',
            user='hpi.python',
            password='hpi.python',
            database='fc_1_data_db',
            connection_timeout=5
        )
        
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables in the database:")
        print("=" * 80)
        
        # Group tables by prefix
        table_groups = {}
        for table in tables:
            # Extract prefix (everything before first underscore or the whole name)
            prefix = table.split('_')[0] if '_' in table else table
            if prefix not in table_groups:
                table_groups[prefix] = []
            table_groups[prefix].append(table)
        
        # Print tables by prefix
        for prefix, table_list in sorted(table_groups.items()):
            print(f"\n{prefix}* ({len(table_list)} tables):")
            for table in sorted(table_list):
                print(f"  - {table}")
        
        # Check for required tables
        required_tables = [
            'process1_data', 'process2_data', 'process3_data',
            'process4_data', 'process5_data', 'process6_data',
            'database_data', 'fm05000102_inspection', 'em0580106p_inspection',
            'em0580107p_inspection', 'csb6400802_inspection', 'rdb5200200_inspection',
            'dfb6600600_inspection'
        ]
        
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print("\n⚠️  Missing required tables:")
            for table in missing_tables:
                print(f"  - {table}")
        else:
            print("\n✓ All required tables are present")
        
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    list_all_tables()
    input("\nPress Enter to exit...")
