import asyncio
import subprocess
import socket
import struct
import time

class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

async def convert_ip_to_uint(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]

async def convert_uint_to_ip(num):
    return socket.inet_ntoa(struct.pack('!I', num))

async def scan_ip_range(start_ip, end_ip, timeout=0.01):
    start_uint = await convert_ip_to_uint(start_ip)
    end_uint = await convert_ip_to_uint(end_ip)
    active_ips = []; inactive_ips = []
    while start_uint <= end_uint:
        current_ip = await convert_uint_to_ip(start_uint)
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket().connect((current_ip, 80))
            active_ips.append(current_ip); print(f"{colors.GREEN}Scanned IP: {current_ip}{colors.ENDC}")
        except (socket.error, socket.timeout):
            inactive_ips.append(current_ip); print(f"{colors.FAIL}Scanned IP: {current_ip}{colors.ENDC}")
        start_uint += 1
    return active_ips, inactive_ips

async def adb_connect(ip):
    try:
        await asyncio.create_subprocess_exec('adb', '-s', ip, 'tcpip', '5555', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await asyncio.create_subprocess_exec('adb', 'connect', ip, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        return ip
    except Exception as e:
        print(f"{colors.WARNING}Error connecting to {ip}: {e}{colors.ENDC}")
        return None

async def connect_ips(ips):
    tasks = []
    for ip in ips:
        tasks.append(asyncio.create_task(adb_connect(ip)))
    connected_ips = [ip for ip in await asyncio.gather(*tasks) if ip is not None]
    for ip in connected_ips:
        print(f"{colors.GREEN}ADB connected to {ip}.{colors.ENDC}")
    return connected_ips

async def write_ips_to_file(connected_ips):
    try:
        with open('connected_ips.txt', 'w') as file:
            for ip in connected_ips:
                file.write(ip + "\n")
        print(f"{colors.BLUE}List of connected IPs {' '.join(connected_ips)} written to connected_ips.txt.{colors.ENDC}")
    except IOError as e:
        print(f"{colors.WARNING}Error writing file: {e}{colors.ENDC}")

async def main():
    start_time = time.monotonic()
    active_ips, inactive_ips = await scan_ip_range("108.192.0.0", "108.192.0.255")
    print(f"{colors.BLUE}{len(active_ips)} IPs scanned in {time.monotonic() - start_time:.2f} seconds.{colors.ENDC}")

    start_time = time.monotonic()
    connected_ips = await connect_ips(active_ips)
    print(f"{colors.GREEN}{len(connected_ips)} devices connected to ADB in {time.monotonic() - start_time:.2f} seconds.{colors.ENDC}")

    start_time = time.monotonic()
    await write_ips_to_file(connected_ips)
    print(f"{colors.BLUE}List of connected IPs written to file in {time.monotonic() - start_time:.2f} seconds.{colors.ENDC}")

asyncio.run(main())
