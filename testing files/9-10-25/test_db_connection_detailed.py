import mysql.connector
from mysql.connector import Error, errorcode
import socket
import ssl
import sys

def test_database_connection():
    """Test database connection with detailed error handling"""
    config = {
        'host': '192.168.2.148',
        'user': 'hpi.python',
        'password': 'hpi.python',
        'database': 'fc_1_data_db',
        'connection_timeout': 10
    }
    
    print("Database Connection Test")
    print("=======================")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    
    try:
        # Test basic TCP connection first
        print("\n[1/4] Testing TCP connection...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((config['host'], 3306))
        sock.close()
        print("✓ TCP connection successful")
        
        # Test MySQL connection without database
        print("\n[2/4] Testing MySQL server connectivity...")
        test_config = config.copy()
        test_config['database'] = None
        
        try:
            conn = mysql.connector.connect(**test_config)
            server_version = conn.get_server_info()
            conn.close()
            print(f"✓ MySQL server is running (Version: {server_version})")
        except Error as e:
            print(f"✗ MySQL server error: {e}")
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("  - Username or password is incorrect")
            return
        
        # Test connection with database
        print("\n[3/4] Testing database access...")
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            
            # Get database information
            cursor.execute("SELECT DATABASE(), USER(), VERSION()")
            db_info = cursor.fetchone()
            print(f"✓ Connected to database: {db_info[0]}")
            print(f"  - User: {db_info[1]}")
            print(f"  - MySQL Version: {db_info[2]}")
            
            # List tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n[4/4] Found {len(tables)} tables in the database")
            
            # Group tables by prefix
            table_groups = {}
            for (table_name,) in tables:
                prefix = table_name.split('_')[0] if '_' in table_name else 'other'
                if prefix not in table_groups:
                    table_groups[prefix] = []
                table_groups[prefix].append(table_name)
            
            # Print table groups
            print("\nTable groups (first 5 of each):")
            for prefix, table_list in table_groups.items():
                print(f"\n{prefix}* ({len(table_list)} tables):")
                for table in table_list[:5]:
                    print(f"  - {table}")
                if len(table_list) > 5:
                    print(f"  ... and {len(table_list) - 5} more")
            
            # Check for required tables
            required_tables = [
                'process1_data', 'process2_data', 'process3_data',
                'process4_data', 'process5_data', 'process6_data',
                'database_data', 'fm05000102_inspection', 'em0580106p_inspection',
                'em0580107p_inspection', 'csb6400802_inspection', 'rdb5200200_inspection',
                'dfb6600600_inspection'
            ]
            
            missing_tables = [t for t in required_tables 
                            if not any(t in table for table in [t[0] for t in tables])]
            
            if missing_tables:
                print("\n⚠️  Missing required tables:")
                for table in missing_tables:
                    print(f"  - {table}")
            else:
                print("\n✓ All required tables are present")
            
            cursor.close()
            conn.close()
            
        except Error as e:
            print(f"✗ Database error: {e}")
            if e.errno == errorcode.ER_BAD_DB_ERROR:
                print("  - The specified database does not exist")
            elif e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("  - Access denied for user")
                print("  - Please verify the username and password")
            
    except socket.timeout:
        print("✗ Connection timed out. The server is not responding.")
    except ConnectionRefusedError:
        print("✗ Connection was refused. The MySQL server might not be running.")
    except socket.gaierror:
        print("✗ Could not resolve hostname. Please check the server address.")
    except ssl.SSLError as e:
        print(f"✗ SSL error: {e}")
        print("  - Try adding 'ssl_disabled=True' to the connection parameters")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nConnection test complete.")

if __name__ == "__main__":
    test_database_connection()
    
    # Keep the window open if run directly
    if sys.platform == 'win32':
        input("\nPress Enter to exit...")
