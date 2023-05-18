import subprocess
import socket
import os
import struct
import time

# Define colors for outputs
class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Define a function to convert a string IP address to an unsigned int
def convert_ip_to_uint(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]

# Define a function to convert an unsigned int IP address to a string
def convert_uint_to_ip(num):
    return socket.inet_ntoa(struct.pack('!I', num))

# Define a function to scan a range of IP addresses
def scan_ip_range(start_ip, end_ip, timeout=0.01):
    start_uint = convert_ip_to_uint(start_ip)
    end_uint = convert_ip_to_uint(end_ip)

    active_ips = []
    inactive_ips = []

    while start_uint <= end_uint:
        current_ip = convert_uint_to_ip(start_uint)
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket().connect((current_ip, 80))
            active_ips.append(current_ip)
        except (socket.error, socket.timeout):
            inactive_ips.append(current_ip)
        start_uint += 1
    return active_ips, inactive_ips

# Define the range of IP addresses to scan
ip_range_start = "192.168.1.1"
ip_range_end = "192.168.1.255"

# Scan the IP address range
start_time = time.time()
active_ips, inactive_ips = scan_ip_range(ip_range_start, ip_range_end)
elapsed_time = time.time() - start_time

# Print the summary of IP scanning
print(f"{colors.HEADER}IP Address Summary{colors.ENDC}")
print(f"{colors.BLUE}Active IPs: {', '.join(active_ips)}{colors.ENDC}")
print(f"{colors.FAIL}Inactive IPs: {', '.join(inactive_ips)}{colors.ENDC}")
print(f"{colors.GREEN}Scanned {len(active_ips) + len(inactive_ips)} IPs in {elapsed_time:.2f} seconds.{colors.ENDC}")
print("\n")

# Set up the Android Device Bridge on each active device
connected_ips = []
unconnected_ips = []
for ip in active_ips:
    try:
        subprocess.check_output(['adb', '-s', ip, 'tcpip', '5555'], stderr=subprocess.STDOUT, universal_newlines=True)
        subprocess.check_output(['adb', 'connect', ip], stderr=subprocess.STDOUT, universal_newlines=True)
        connected_ips.append(ip)
    except subprocess.CalledProcessError as e:
        unconnected_ips.append(ip)
        print(f"{colors.WARNING}Error: {e.output}{colors.ENDC}")

# Print the summary of ADB connection
print(f"{colors.HEADER}ADB Connection Summary{colors.ENDC}")
print(f"{colors.GREEN}ADB Connected IPs: {', '.join(connected_ips)}{colors.ENDC}")
print(f"{colors.WARNING}ADB Unconnected IPs: {', '.join(unconnected_ips)}{colors.ENDC}")
print("\n")

# Write the list of connected IPs to a file
try:
    with open('connected_ips.txt', 'w') as file:
        for ip in connected_ips:
            file.write(ip + "\n")
    # Print the confirmation of writing to file
    print(f"{colors.BLUE}Successfully written the list of connected IPs to connected_ips.txt.{colors.ENDC}")
except IOError as e:
    print(f"{colors.WARNING}Error: {e}{colors.ENDC}")
