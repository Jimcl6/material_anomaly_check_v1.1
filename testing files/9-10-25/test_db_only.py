print("Testing database connection...")
try:
    import mysql.connector
    print("✓ mysql.connector is installed")
    
    try:
        conn = mysql.connector.connect(
            host='192.168.2.148',
            user='hpi.python',
            password='hpi.python',
            database='fc_1_data_db',
            connection_timeout=5
        )
        print("✓ Successfully connected to database")
        
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE(), USER(), VERSION()")
        db_info = cursor.fetchone()
        print(f"  - Database: {db_info[0]}")
        print(f"  - User: {db_info[1]}")
        print(f"  - MySQL Version: {db_info[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        
except ImportError:
    print("✗ mysql.connector is not installed")

input("\nPress Enter to exit...")
