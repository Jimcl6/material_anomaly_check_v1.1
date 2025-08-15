
#%%
import socket

try:
    # Get the hostname of the current machine
    hostname = socket.gethostname()

    # Get the IP address associated with the hostname
    ip_address = socket.gethostbyname(hostname)

    print(f"Your Computer Name is: {hostname}")
    print(f"Your Local IP Address is: {ip_address}")

except socket.gaierror:
    print("Could not resolve hostname to an IP address.")
except Exception as e:
    print(f"An error occurred: {e}")

#%%   