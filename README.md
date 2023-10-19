# SimpleDDoS

![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)

**SimpleDDoS** is a simple Distributed Denial of Service (DDoS) script written in Python. It's designed to help users understand how DDoS attacks work and to be used responsibly for educational purposes only.

## Features

- Launch DDoS attacks against a target IP and port using multiple threads.
- Customizable number of threads and packets to send.
- Provides feedback on the total number of packets sent.

## Prerequisites

- Python 3.x
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SSL-ACTX/SimpleDDoS.git
   
2. Navigate to the project directory:
   ```bash
   cd SimpleDDoS
   
# Usage
1. Open a terminal and navigate to the SimpleDDoS directory.
   Launch the script using the following command:
   ```bash
   python dds.py <target_ip> <target_port> [-t <threads>] [-p <packets>]
   ```
   Example:

   ```bash
   python simple_ddos.py 127.0.0.1 80 -t 5 -p 1000
   ```
   Follow the on-screen instructions and let the script initiate the DDoS attack.

# Disclaimer
This script is intended for educational purposes only. Unauthorized use of this script for malicious purposes is illegal and unethical. Use responsibly and only on systems you have explicit permission to test.

# License
This project is licensed under the MIT License - see the LICENSE file for details.

**Author**
- SSL-ACTX
- Mail: seuriin@gmail.com
- Twitter: lord_xu777
