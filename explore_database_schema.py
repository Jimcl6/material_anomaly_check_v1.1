import mysql.connector
from mysql.connector import Error

def main():
    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host='192.168.2.148',
            user='hpi.python',
            password='hpi.python',
            database='fc_1_data_db',
            connection_timeout=5
        )
        
        print("✓ Successfully connected to the database")
        
        cursor = conn.cursor()
        
        # Get database version
        cursor.execute("SELECT VERSION()")
        db_version = cursor.fetchone()[0]
        print(f"\nDatabase Version: {db_version}")
        
        # List all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"\nFound {len(tables)} tables in the database:")
        print("=" * 80)
        
        # Print all tables
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
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
        
        # Show structure of required tables that exist
        print("\n=== Table Structures ===")
        for table in required_tables:
            if table in tables:
                print(f"\nTable: {table}")
                print("-" * (len(table) + 8))
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"Columns ({len(columns)}):")
                for col in columns[:5]:  # Show first 5 columns
                    print(f"  - {col[0]} ({col[1]})")
                if len(columns) > 5:
                    print(f"  - ... and {len(columns) - 5} more columns")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Row count: {count:,}")
        
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nDatabase connection closed")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
