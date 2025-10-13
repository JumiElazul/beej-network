import threading
import time
import socket
import sys

from chatui import init_windows, read_command, print_message, end_windows

def usage():
    print("usage: python3 chat-client <nickname> <server_name> <port>", file=sys.stderr)
    sys.exit(1)

def parse_args(argv: list[str]):
    try:
        nickname: str = argv[1]
        server: str = argv[2]
        port: int = int(argv[3])
        return nickname, server, port
    except:
        print(f"Could not parse arguments passed to client: {argv}", file=sys.stderr)
        sys.exit(1)

def runner():
    count = 0

    while True:
        time.sleep(2)
        print_message(f"*** Runner count: {count}")
        count += 1

def create_socket_and_connect(server: str, port: int):
    try:
        s: socket.socket = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((server, port))
        return s
    except:
        print(f"Could not connect to ({server}:{port}).", file=sys.stderr)
        sys.exit(1)

def main(argv: list[str]):
    nickname, server, port = parse_args(argv)
    s: socket.socket = create_socket_and_connect(server, port)

    init_windows()

    t1 = threading.Thread(target=runner, daemon=True)
    t1.start()

    while True:
        try:
            command = read_command("Enter a thing> ")
        except:
            break

        print_message(f">>> {command}")

    end_windows()

if __name__ == "__main__":
    main(sys.argv)
