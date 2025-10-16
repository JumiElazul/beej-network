import sys
import socket
import select
from packet import *

class User:
    def __init__(self, sock: socket.socket, username: str | None = None):
        self.sock = sock
        self.username = username
        self.byte_buffer = bytearray()

    def __repr__(self):
        return f"User(username={self.username!r}, sock={self.sock.getpeername()})"

listener: socket.socket
active_users: set[User] = set()

def find_user_by_socket(sock: socket.socket):
    for user in active_users:
        if user.sock is sock:
            return user

    return None


def handle_incoming_connection(listener: socket.socket):
    new_sock, addr = listener.accept()
    user = User(new_sock)
    active_users.add(user)
    print(f"New connection from {addr}. Total users: {len(active_users)}")


def _broadcast(pkt: Packet, exclude: User | None = None):
    for user in active_users:
        if user is not exclude and user.sock is not listener:
            send_packet(user.sock, pkt)


def handle_packet(user: User, pkt: Packet):
    match pkt.type:
        case PacketType.HELLO:
            user.username = pkt.payload
            print(f"{user} joined the chat.")

            ack_pkt: Packet = Packet(PacketType.HELLO, f"Welcome, {user.username}!")
            send_packet(user.sock, ack_pkt)

            join_pkt: Packet = Packet(PacketType.CHAT, f"*** {user.username} has joined the chat. ***")
            _broadcast(join_pkt, exclude=user)

        case PacketType.GOODBYE:
            print(f"{user} has left the chat.")
            active_users.remove(user)
            user.sock.close()
            leave_pkt = Packet(PacketType.CHAT, f"*** {user.username} has left the chat. ***")
            _broadcast(leave_pkt)

        case PacketType.CHAT:
            linked_payload: str = f"{user.username}: {pkt.payload}"
            print(f"'{user.username}' typed: '{pkt.payload}' -> Broadcasting '{linked_payload}'.")
            pkt.payload = linked_payload
            _broadcast(pkt, exclude=None)

        case PacketType.EMOTE:
            linked_payload: str = f"[{user.username} {pkt.payload}]"
            print(f"User [{user.username} typed: {pkt.payload} -> Broadcasting '{linked_payload}'.")
            pkt.payload = linked_payload
            _broadcast(pkt, exclude=None)


def main(argv: list[str]):
    try:
        port: int = int(argv[1])
    except:
        print("usage: python3 chat_server.py <port>")
        sys.exit(1)

    global listener

    try:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('', port))
        listener.listen()
        active_users.add(User(listener))
        print(f"Chat server listening on port {port}...")
    except socket.error:
        print("Error creating socket.")
        sys.exit(1)

    while True:
        ready_to_read, _, _ = select.select([u.sock for u in active_users], [], [])
        for sock in ready_to_read:
            if sock is listener:
                handle_incoming_connection(listener)
                continue

            user: User | None = find_user_by_socket(sock)

            if not user:
                continue

            pkt = receive_packet(user.sock, user.byte_buffer)

            if pkt is None:
                continue

            handle_packet(user, pkt)

if __name__ == "__main__":
    main(sys.argv)
