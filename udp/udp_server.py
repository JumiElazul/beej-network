import sys
import socket

def main(argc: int, argv: list[str]):
    try:
        target_port = int(sys.argv[1])
    except:
        print("usage: udpserver.py port", file=sys.stderr)
        sys.exit(1)

    with socket.socket(type=socket.SOCK_DGRAM) as s:
        s.bind(('', target_port))

        while True:
            data, sender = s.recvfrom(target_port)

            print(f"Got data from {sender[0]}:{sender[1]}: \"{data.decode()}\"")
            s.sendto(f"Got your {len(data)} byte(s) of data!".encode(), sender)

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
