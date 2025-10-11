# Example usage:
#
# python select_server.py 3490

import sys
import socket
import select

MAX_RECEIVE: int = 4096
open_sockets: set[socket.socket] = set()

def connect_socket(socket: socket.socket):
    global open_sockets
    print(f"{socket.getpeername()}: connected")
    open_sockets.add(socket)

def disconnect_socket(socket: socket.socket):
    global open_sockets
    print(f"{socket.getpeername()}: disconnected")
    open_sockets.remove(socket)

def run_server(port: int):
    global open_sockets

    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', port))
    listener.listen()
    print(f"Select server listening on port {port}...")

    open_sockets.add(listener)

    try:
        while True:
            ready_to_read, _, _ = select.select(open_sockets, [], [])

            for ready in ready_to_read:
                if ready is listener:
                    print("new connection")
                    new_socket: socket.socket = listener.accept()[0]
                    connect_socket(new_socket);
                else:
                    received: bytes = ready.recv(MAX_RECEIVE)

                    if len(received) > 0:
                        length: int = len(received)
                        print(f"received {length} bytes from {ready.getpeername()} -> {received.decode()}")
                    else:
                        disconnect_socket(ready)
    except KeyboardInterrupt:
        print("KeyboardInterrupt, stopping server...")

    listener.close()


#--------------------------------#
# Do not modify below this line! #
#--------------------------------#

def usage():
    print("usage: select_server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
