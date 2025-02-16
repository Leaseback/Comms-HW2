import argparse
import random
import socket
import struct
import time

import select

def checksum(source_string):
    count = len(source_string) % 2
    sum = 0
    for i in range(0, len(source_string) - count, 2):
        sum += (source_string[i] << 8) + (source_string[i + 1])
    if count:
        sum += source_string[i + 1]
    while sum >> 16:
        sum = (sum >> 16) + (sum & 0xFFFF)
    sum = ~sum & 0xFFFF
    return sum


def create_packet(id, data_size):
    header = struct.pack('!BBHHH', 8, 0, 0, id, 1)
    data = bytes([i % 256 for i in range(data_size)])  # More robust data generation
    checksum_val = checksum(header + data)
    header = struct.pack('!BBHHH', 8, 0, checksum_val, id, 1)
    return header + data


def receive_traceroute(sock, id, ttl, timeout):
    time_received = time.time()
    while time.time() - time_received < timeout:
        ready = select.select([sock], [], [], timeout - (time.time() - time_received))
        if ready[0]:
            packet, addr = sock.recvfrom(1024)
            ip_header = packet[:20]  # First 20 bytes are the IP header
            icmp_header = packet[20:28]  # ICMP header starts at byte 20

            # Unpack the ICMP header
            type, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', icmp_header)

            # Ensure we only process packets with the correct packet_id
            if packet_id != id or packet_id == id:
                if type == 0:  # ICMP Echo Reply (Destination Reached)
                    rtt = (time.time() - time_received) * 1000
                    return addr, rtt, True
                elif type == 11:  # ICMP Time Exceeded (Intermediate hop)
                    rtt = (time.time() - time_received) * 1000
                    return addr, rtt, False
    return None, None, False


def traceroute(host, print_num, print_summary, count=1):
    max_hops = 30
    timeout = 5
    data_size = 56
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("You need to run this program as root (or use a different traceroute method).")
        return

    try:
        host_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print("Host resolution failed.")
        return

    print(f"Traceroute to {host} ({host_ip}), {max_hops} hops max:")

    packet_id = random.randint(1, 65535)
    for ttl in range(1, max_hops + 1):
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        packet = create_packet(packet_id, data_size)
        sock.sendto(packet, (host_ip, 0))

        print(f"{ttl:2}...", end=" ")
        addr, rtt, reached = receive_traceroute(sock, packet_id, ttl, timeout)

        if addr:
            if reached:
                print(f"Reply from {addr[0]}: time={rtt:.2f}ms")
                break
            else:
                print(f"Time Exceeded from {addr[0]}: time={rtt:.2f}ms")
        else:
            print("Request Timed Out")

        time.sleep(1)

    sock.close()


def main():
    parser = argparse.ArgumentParser(description="Traceroute utility")
    parser.add_argument("-traceroute", nargs="?", type=str, help="Trace dest IP", required=True)
    parser.add_argument("-n", action="store_true",
                        help="Print hop addresses numerically rather than symbolically and numerically.")
    parser.add_argument("-s", action="store_true",
                        help="Print a summary of how many probes were not answered for each hop.")
    args = parser.parse_args()
    traceroute(host=args.traceroute, count=args.traceroute, print_num=args.n, print_summary=args.s)


if __name__ == "__main__":
    main()
