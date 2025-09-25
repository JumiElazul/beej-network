import socket
import sys

def main(argc: int, argv: list[str]):
    try:
        server = sys.argv[1]
        port = int(sys.argv[2])
        message = sys.argv[3]
    except:
        print("usage: udpclient.py server port message", file=sys.stderr)
        sys.exit(1)

    with socket.socket(type=socket.SOCK_DGRAM) as s:
        print("Sending message...")
        s.sendto(message.encode(), (server, port))

        data, sender = s.recvfrom(4096)
        print(f"Got reply: \"{data.decode()}\"")

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
