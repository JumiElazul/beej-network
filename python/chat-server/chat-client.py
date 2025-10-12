import threading
import time
import socket
import sys

from chatui import init_windows, read_command, print_message, end_windows

def window_output(s: socket.socket):
    while True:
        b: bytes = s.recv(256)

        if len(b) > 0:
            print_message(b.decode())

def usage():
    print("usage: chat-client <nickname> <server_address> <port>")

def main(argc: int, argv: list[str]):
    try:
        nickname: str = argv[1]
        server: str = argv[2]
        port: int = int(argv[3])
    except (IndexError, ValueError):
        usage()
        sys.exit(1)

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.connect((server, port))
        except ConnectionRefusedError:
            print(f"Connection to {server} on port {port} could not be established.")
            sys.exit(1)

        print(f"Connected to {server} on port {port}...")

        init_windows()

        window_thread = threading.Thread(target=window_output, args={s}, daemon=True)
        window_thread.start()

        while True:
            try:
                command = read_command(f"{nickname}> ")
            except KeyboardInterrupt:
                print("KeyboardInterrupt")
                break
            except:
                break

            s.sendall(command.encode())

        end_windows()

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
