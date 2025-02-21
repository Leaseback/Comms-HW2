# Ping and Traceroute

This program provides a Python implementation of the `ping` and `traceroute` commands, using sockets to communicate with remote hosts.

## Features
- **Ping**: Sends ICMP Echo Request packets to a remote host and waits for an Echo Reply, measuring the round-trip time (RTT). This mimics the "ping" command built into most Operating Systems.
- **Traceroute**: Traces the route packets take to a destination by sending ICMP Echo Request packets with incrementing TTL values.

## Requirements
This script uses the following Python libraries, all of which are part of the standard Python library:
- `argparse`: For parsing command-line arguments.
- `random`: For generating random numbers, used for packet IDs.
- `socket`: For working with network connections.
- `struct`: For working with binary data, specifically ICMP packets.
- `time`: For measuring round-trip times.
- `select`: For waiting on sockets.

No additional packages need to be installed.

## Setup
Before running the script, ensure you have Python 3.x installed on your machine.

If you're on Linux or macOS, you may need to run the script as a superuser (`root`) to have permission to use raw sockets.

### Running the Script
1. Clone this repository to your local machine or copy the script into a file (e.g., `my_traceroute.py`).
2. Open a terminal and navigate to the directory where the script is located.

## Usage

### Ping
The `ping` command sends ICMP Echo Requests to a host and reports the round-trip time (RTT) for each packet.

#### Syntax
python my_ping.py -ping <host> -c <count> -i <interval> -s <size> -t <timeout>


- `-ping <host>`: The destination host (IP address or domain name) to ping. This is a required argument.
- `-c <count>`: The number of packets to send. Default is `4`.
- `-i <interval>`: The time (in seconds) between sending each packet. Default is `1`.
- `-s <size>`: The size (in bytes) of the data section of each ICMP packet. Default is `56`.
- `-t <timeout>`: The timeout (in seconds) for receiving a reply. Default is `1`.

#### Example
To ping `google.com` with 5 packets, a 2-second interval between each packet, and a timeout of 2 seconds:

python my_ping.py -ping google.com -c 5 -i 2 -t 2


### Traceroute
The `traceroute` command sends ICMP Echo Requests with increasing TTL values to trace the path taken by packets to a destination.

#### Syntax
python my_traceroute.py -traceroute <host> -n -s

- `-traceroute <host>`: The destination host (IP address or domain name) for the traceroute. This is a required argument.
- `-n`: If provided, prints hop addresses numerically rather than symbolically.
- `-s`: If provided, prints a summary of hops that didn’t answer probes.

#### Example
To trace the route to `google.com`:
python my_traceroute.py -traceroute google.com


To trace the route and print only numerical IP addresses with a summary of unresponsive hops:

python my_traceroute.py -traceroute google.com -n -s


## How It Works

### Ping
- The script creates ICMP Echo Request packets and sends them to the target host.
- It waits for an ICMP Echo Reply and calculates the round-trip time.
- If the reply is received, it prints the time; otherwise, it reports a timeout.

### Traceroute
- The script sends ICMP Echo Request packets with increasing TTL values, starting from 1.
- It listens for ICMP Time Exceeded (TTL expired) or Echo Reply (destination reached) messages.
- It prints the address and round-trip time for each hop along the route.
- The process continues until the destination is reached or the maximum TTL (30 hops) is reached.

## Limitations
- This script requires raw socket permissions, making it require special permission to work on Windows machines and sudo permissions to work on Linux machines.
- The traceroute function supports up to 30 hops, as is common with standard traceroute tools.
- Error handling is basic and may need improvements.