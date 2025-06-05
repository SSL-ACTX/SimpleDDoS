# SimpleDDoS: A Python-Based Educational DDoS Tool

![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)

**SimpleDDoS** is a versatile and user-friendly Python script designed for **educational purposes only**, demonstrating the principles of Distributed Denial of Service (DDoS) attacks. It provides both UDP Flood and TCP SYN Flood capabilities, with configurable parameters and real-time feedback.

**Disclaimer:** This script is provided strictly for educational purposes, security research, and authorized testing. **Unauthorized use against any network or system is illegal and unethical.** The author is not responsible for any misuse or damage caused by this script. Use responsibly and only on systems for which you have explicit, written permission to test.

## Features

*   **Multi-Method Attack:** Supports both **UDP Flood** (sending large volumes of UDP packets) and **TCP SYN Flood** (initiating many half-open TCP connections).
*   **Persistent Configuration:** Automatically saves and loads your last used attack parameters (`method`, `threads`, `count`, `ports`, `udp_packet_size`) to a JSON file (`ddos_config.json`) for quick re-use.
*   **`--auto` Mode:** Launch attacks quickly using pre-saved settings from your configuration file, ideal for continuous testing.
*   **Flexible Port Targeting:** Attack single or multiple target ports.
*   **Configurable Attack Scale:** Adjust the number of concurrent threads and the total number of packets/connections to send, or run in continuous mode.
*   **Real-time Progress Reporting:** Get live updates on total packets/connections sent, current attack rate (P/Cps), and average attack rate.
*   **Intelligent Thread Distribution:** Threads are automatically distributed among specified ports for efficient resource utilization.
*   **Robust Parameter Validation:** Includes checks for valid IP addresses, port ranges, and attack parameters to prevent errors.
*   **User-Friendly Interface:** Features a clear ASCII art header, color-coded output for better readability, and a countdown before attack initiation.

## Prerequisites

*   Python 3.x
*   Git (for cloning the repository)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SSL-ACTX/SimpleDDoS.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd SimpleDDoS
    ```

## Usage

Launch the script from your terminal within the `SimpleDDoS` directory.

### Basic Syntax

```bash
python dds.py <target_ip> [OPTIONS]
```

### Arguments

*   **`ip`**: The target IP address. (Required)

*   **`-a`, `--auto`**:
    *   Use parameters from the configuration file (`~/.config/ddos_script/ddos_config.json`).
    *   Automatically runs in **continuous** mode.
    *   Mutually exclusive with `-p`.
    *   **Example:** `python dds.py 127.0.0.1 --auto`

*   **`-p`, `--ports`**:
    *   Target ports (comma-separated, e.g., `80,443,22`).
    *   Required unless `--auto` is used.
    *   **Example:** `-p 80,443`

*   **`-m`, `--method`**:
    *   Attack method: `udp` (UDP Flood) or `tcp` (TCP SYN Flood).
    *   **Default:** Uses the `last_method` from config (`udp` if not set).
    *   **Example:** `-m tcp`

*   **`-t`, `--threads`**:
    *   Number of threads to use.
    *   Required unless `--auto` is used.
    *   **Example:** `-t 50`

*   **`-n`, `--count`**:
    *   Total number of packets (UDP) or connection attempts (TCP) across all threads.
    *   Required unless `--auto` or `--cont` is used.
    *   **Example:** `-n 100000`

*   **`--udp-packet-size`**:
    *   Size of each UDP packet in bytes. Ignored for TCP method.
    *   **Default:** Uses `udp_packet_size` from config (`2048` bytes if not set).
    *   **Example:** `--udp-packet-size 4096`

*   **`--cont`**:
    *   Run the attack continuously (ignores `-n`/`--count`).
    *   **Example:** `--cont`

### Examples

1.  **Basic UDP Flood (100k packets on port 80 with 50 threads):**
    ```bash
    python dds.py 192.168.1.100 -p 80 -m udp -t 50 -n 100000
    ```

2.  **Continuous TCP SYN Flood (on ports 80, 443 with 100 threads):**
    ```bash
    python dds.py 192.168.1.100 -p 80,443 -m tcp -t 100 --cont
    ```

3.  **UDP Flood with custom packet size:**
    ```bash
    python dds.py 192.168.1.100 -p 12345 -m udp -t 30 -n 500000 --udp-packet-size 4096
    ```

4.  **Launch using saved configuration (`--auto` mode):**
    *(First, run any command manually to save desired settings to `ddos_config.json`. Then, you can use `--auto`)*
    ```bash
    python dds.py 192.168.1.100 --auto
    ```
    This will load `last_method`, `last_threads`, `default_ports`, `udp_packet_size` from your config and run continuously.

## Configuration

The script manages its settings in a JSON file located at:
`~/.config/ddos_script/ddos_config.json`

This file stores:
*   `last_method`: The last attack method used (`udp` or `tcp`).
*   `last_threads`: The last number of threads used.
*   `last_packets`: The total packets/connections from the last *non-continuous* run.
*   `default_ports`: A list of ports used if `--auto` is specified without manually providing ports.
*   `udp_packet_size`: The default size for UDP packets.

You can manually edit this file, but it's primarily updated automatically by the script based on your last successful runs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

*   **SSL-ACTX**
*   **GitHub:** [https://github.com/SSL-ACTX](https://github.com/SSL-ACTX)