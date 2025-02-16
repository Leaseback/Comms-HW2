import argparse


def traceroute(host, print_num, print_summary, count=1):
    print("STUB")


def main():
    parser = argparse.ArgumentParser(description="Traceroute utility")
    parser.add_argument("-traceroute", nargs="?", type=str, help="Trace dest IP", required=True)
    parser.add_argument("-n", action="store_true",
                        help="Print hop addresses numerically rather than symbolically and numerically.")
    parser.add_argument("-s", action="store_true",
                        help="Print a summary of how many probes were not answered for each hop.")
    args = parser.parse_args()
    traceroute(host=args.ping, count=args.traceroute, print_num=args.n, print_summary=args.s)


if __name__ == "__main__":
    main()
