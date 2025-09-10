import mysql.connector
from mysql.connector import Error

def get_table_structure(conn, table_name):
    """Get the structure of a table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        return [col[0] for col in columns]
    except Error as e:
        print(f"Error getting structure for {table_name}: {e}")
        return None

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
        
        # Check the correct table name
        cursor = conn.cursor()
        
        # Check if df06600600_inspection exists
        cursor.execute("SHOW TABLES LIKE 'df06600600_inspection'")
        if cursor.fetchone():
            print("\n=== df06600600_inspection table found ===")
            # Get row count
            cursor.execute("SELECT COUNT(*) FROM df06600600_inspection")
            count = cursor.fetchone()[0]
            print(f"Row count: {count:,}")
            
            # Get column info
            columns = get_table_structure(conn, 'df06600600_inspection')
            if columns:
                print(f"\nColumns ({len(columns)}):")
                for col in columns[:10]:  # Show first 10 columns
                    print(f"  - {col}")
                if len(columns) > 10:
                    print(f"  - ... and {len(columns) - 10} more columns")
            
            # Show sample data
            cursor.execute("SELECT * FROM df06600600_inspection LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print("\nSample data (first 3 rows):")
                for i, row in enumerate(rows, 1):
                    print(f"Row {i}: {row[:5]}{'...' if len(row) > 5 else ''}")
        else:
            print("\n✗ df06600600_inspection table not found")
        
        # Check for rdb5200200_inspection vs rd05200200_inspection
        print("\n=== Checking RD inspection tables ===")
        cursor.execute("SHOW TABLES LIKE 'rd%inspection'")
        rd_tables = [t[0] for t in cursor.fetchall()]
        
        if rd_tables:
            print(f"Found RD inspection tables: {', '.join(rd_tables)}")
            for table in rd_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"- {table}: {count:,} rows")
        else:
            print("No RD inspection tables found")
        
        # List all inspection tables for reference
        print("\n=== All inspection tables ===")
        cursor.execute("SHOW TABLES WHERE Tables_in_fc_1_data_db LIKE '%inspection%'")
        inspection_tables = [t[0] for t in cursor.fetchall()]
        
        for table in inspection_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"- {table}: {count:,} rows")
        
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
