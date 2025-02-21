import argparse
import random
import socket
import struct
import time

import select


def checksum(source_string):
    """
        Generates a checksum for a given string (used for packet validation).

        Args:
            source_string (bytes): The data for which the checksum is to be generated.

        Returns:
            int: The checksum value for the given data.
        """
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
    """
            Given packet_id and a desired packet size created a ICMP Echo packet

            Args:
                id (int): The packet ID / Number
                data_size: The amount of bytes to pack into the packet

            Returns:
                Packet: A ICMP Echo Packet of ID id of size data_size
            """
    header = struct.pack('!BBHHH', 8, 0, 0, id, 1)
    data = bytes([i % 256 for i in range(data_size)])  # More robust data generation
    checksum_val = checksum(header + data)
    header = struct.pack('!BBHHH', 8, 0, checksum_val, id, 1)
    return header + data


def receive_ping(sock, id, timeout):
    """
                Listens for pings on socket sock

                Args:
                    sock (Socket): The socket to listen on
                    id (int): The packet ID
                    timeout (int): Time in seconds to wait before timeing out

                Returns:
                    Packet: The received packet or None if timed out
                """
    time_received = time.time()
    while time.time() - time_received < timeout:
        ready = select.select([sock], [], [], timeout - (time.time() - time_received))
        if ready[0]:
            packet, addr = sock.recvfrom(1024)
            icmp_header = packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', icmp_header)
            if type == 0 and packet_id == id:  # Check ICMP type for reply (0)
                rtt = (time.time() - time_received) * 1000
                return addr, rtt
    return None


def ping(host, count=4, interval=1, timeout=1, data_size=56):
    """
                Pings a given host address and prints the response (if any)

                Args:
                    host (Str): The ip address or hostname to ping
                    count (int) (default 4): Amount of packets to send
                    interval (int) (default 1): Time to wait between sending each packet
                    timeout (int) (default 1): Time to wait for packet before timing out
                    data_size (int) (default 56): Size of packets to send when pinging

                Returns:
                    None
                """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("You need to run this program as root (or use a different ping method).")
        return

    try:
        host_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print("Host resolution failed.")
        return

    print(f"PING {host} ({host_ip}): {count} packets of {data_size} bytes")

    packet_id = random.randint(1, 65535)

    for i in range(count):
        packet = create_packet(packet_id, data_size)
        sock.sendto(packet, (host_ip, 0))  # Port 0 for ICMP
        print(f"Sent packet {i + 1}")

        result = receive_ping(sock, packet_id, timeout)

        if result is None:
            print(f"Request timeout for packet {i + 1}")
        else:
            addr, rtt = result
            print(f"Reply from {addr[0]}: bytes={len(packet) - 28} time={rtt:.2f}ms")

        time.sleep(interval)

    print(f"Ping to {host} completed.")
    sock.close()


def main():
    """
                Takes in user command and arguments, parsing them and calls the ping() function accordingly
    """
    parser = argparse.ArgumentParser(description="Ping utility")
    parser.add_argument("-ping", nargs="?", type=str, help="Ping dest IP", required=True)
    parser.add_argument("-c", default=4, nargs="?", type=int, help="Number of packets to send")
    parser.add_argument("-i", default=1, nargs="?", type=int, help="Time between packets")
    parser.add_argument("-s", default=56, nargs="?", type=int, help="Data size")  # Use the -s argument
    parser.add_argument("-t", default=1, nargs="?", type=int, help="Timeout")
    args = parser.parse_args()
    ping(host=args.ping, count=args.c, interval=args.i, timeout=args.t, data_size=args.s)


if __name__ == "__main__":
    main()
