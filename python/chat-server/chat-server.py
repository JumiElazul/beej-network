import sys
import socket
import select

def usage():
    print("usage: chat-server <port>")

def add_socket(active_sockets: set[socket.socket], s: socket.socket):
    active_sockets.add(s)
    print(f"Added socket {s.getpeername()} to active sockets set (currently {len(active_sockets)} active sockets).")

def remove_socket(active_sockets: set[socket.socket], s: socket.socket):
    active_sockets.remove(s)
    print(f"Removed socket {s.getpeername()} from active sockets set (currently {len(active_sockets)} active sockets).")

def main(argc: int, argv: list[str]):
    try:
        port: int = int(argv[1])
    except:
        usage()
        sys.exit(1)

    listener: socket.socket = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', port))
    listener.listen()

    active_sockets: set[socket.socket] = set()
    active_sockets.add(listener)

    print(f"chat-server listening on port {port}...")

    try:
        while True:
            ready_sockets, _, _ = select.select(active_sockets, [], [])

            for ready in ready_sockets:
                if ready is listener:
                    new_socket: socket.socket = listener.accept()[0]
                    add_socket(active_sockets, new_socket);
                else:
                    received: bytes = ready.recv(256)
                    print(received.decode())

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, stopping server...")

    listener.close()

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
