import sys
import socket
import select

listener: socket.socket

class User():
    def __init__(self, nickname: str, socket: socket.socket):
        self.nickname = nickname
        self.socket = socket

    def __str__(self):
        return self.nickname

def parse_args(argv: list[str]):
    try:
        port: int = int(argv[3])
        return port
    except:
        print(f"Could not parse arguments passed to client: {argv}", file=sys.stderr)
        sys.exit(1)

def create_listener_socket(port: int):
    listener: socket.socket = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', port))
    listener.listen()

    print(f"chat-server listening on port {port}...")
    return listener

def run_server_loop(active_users: set[User]):
    while True:
        sockets: list[socket.socket] = [user.socket for user in active_users]
        ready_to_read, _, _ = select.select(sockets, [], [])

        for s in ready_to_read:
            pass

def main(argv: list[str]):
    port: int = parse_args(argv)
    active_users: set[User] = set()

    listener = create_listener_socket(port)
    active_users.add(User("", listener))

    run_server_loop(active_users)

if __name__ == "__main__":
    main(sys.argv)
