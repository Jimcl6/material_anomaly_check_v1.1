import mysql.connector
from mysql.connector import Error
import socket
import time

def test_network_connection(host, port=3306, timeout=5):
    """Test basic network connectivity to the database server"""
    try:
        print(f"Attempting to connect to {host}:{port}...")
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        print("✓ Network connection successful")
        return True
    except socket.timeout:
        print(f"✗ Connection to {host}:{port} timed out after {timeout} seconds")
    except ConnectionRefusedError:
        print(f"✗ Connection to {host}:{port} was refused. Is the MySQL server running?")
    except Exception as e:
        print(f"✗ Network connection failed: {str(e)}")
    return False

def test_mysql_connection(host, user, password, database, port=3306):
    """Test MySQL database connection with credentials"""
    connection = None
    try:
        print(f"\nTesting MySQL connection to {host}...")
        start_time = time.time()
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connection_timeout=5
        )
        end_time = time.time()
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✓ Successfully connected to MySQL Server version {db_info}")
            print(f"Connection established in {end_time - start_time:.2f} seconds")
            
            # Get database name
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"✓ Connected to database: {record[0]}")
            
            # List all tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"\nFound {len(tables)} tables in the database:")
            for i, table in enumerate(tables[:10], 1):  # Show first 10 tables
                print(f"  {i}. {table[0]}")
            if len(tables) > 10:
                print(f"  ... and {len(tables) - 10} more tables")
            
            cursor.close()
            return True
            
    except Error as e:
        print(f"✗ Error while connecting to MySQL: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\nMySQL connection is closed")
    
    return False

if __name__ == "__main__":
    DB_CONFIG = {
        'host': '192.168.2.148',
        'user': 'hpi.python',
        'password': 'hpi.python',
        'database': 'fc_1_data_db',
        'port': 3306
    }
    
    # Test network connectivity first
    if test_network_connection(DB_CONFIG['host'], DB_CONFIG['port']):
        # If network is good, test MySQL connection
        test_mysql_connection(**DB_CONFIG)
    
    print("\nNote: If you're having connection issues, please check:")
    print("1. Is the MySQL server running on the specified host?")
    print("2. Are the username and password correct?")
    print("3. Does the database exist and is accessible with the provided credentials?")
    print("4. Is the server's firewall allowing connections on port 3306?")
