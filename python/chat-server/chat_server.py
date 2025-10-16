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
        try:
            peer = self.sock.getpeername()
        except OSError:
            peer = "<listener>"
        return f"User(username={self.username!r}, sock={peer})"

listener: socket.socket
active_users: set[User] = set()

def find_user_by_socket(sock: socket.socket) -> User | None:
    for user in active_users:
        if user.sock is sock:
            return user
    return None


def find_user_by_name(name: str) -> User | None:
    if not name:
        return None
    for u in active_users:
        if u.username == name:
            return u
    return None


def send_error_to(user: User, message: str):
    send_packet(user.sock, Packet(PacketType.ERROR, message))


def _broadcast_text(text: str, exclude: User | None = None):
    pkt = Packet(PacketType.CHAT, text)
    for user in active_users:
        if user is exclude:
            continue
        if user.sock is listener:
            continue

        send_packet(user.sock, pkt)


def broadcast_user_chat(sender: User, message: str):
    formatted = f"{sender.username}: {message}"
    print(f"Broadcasting: {formatted}")
    _broadcast_text(formatted, exclude=None)


def broadcast_emote(sender: User, message: str):
    formatted = f"[{sender.username} {message}]"
    print(f"Broadcasting emote: {formatted}")
    _broadcast_text(formatted, exclude=None)


def _send_private(sender: User, recipient: User, message: str):
    formatted = f"{sender.username} -> {recipient.username}: {message}"
    pkt = Packet(PacketType.CHAT, formatted)
    send_packet(recipient.sock, pkt)
    send_packet(sender.sock, pkt)


def handle_incoming_connection(listener: socket.socket):
    new_sock, addr = listener.accept()
    user = User(new_sock)
    active_users.add(user)
    print(f"New connection from {addr}. Total users: {len(active_users)}")


def format_user_list() -> str:
    names: list[str] = [u.username.strip() for u in active_users if u.username]
    unique_names: list[str] = sorted(set(names), key=str.casefold)
    header: str = f"Total users: {len(unique_names)}\n"
    return header + "\n".join(unique_names)


def handle_packet(user: User, pkt: Packet):
    match pkt.type:
        case PacketType.HELLO:
            desired_name = pkt.payload

            existing_user = find_user_by_name(desired_name)
            if existing_user is not None:
                send_error_to(user, f"Username '{desired_name}' is already taken. Please reconnect with a different name.")
                try:
                    user.sock.close()
                finally:
                    if user in active_users:
                        active_users.remove(user)
                print(f"Rejected HELLO: username '{desired_name}' taken (from {user}).")
                return

            user.username = desired_name
            print(f"{user} joined the chat.")

            ack_pkt: Packet = Packet(PacketType.HELLO, f"Welcome, {user.username}!")
            send_packet(user.sock, ack_pkt)

            join_msg: str = f"*** {user.username} has joined the chat. ***"
            _broadcast_text(join_msg, exclude=user)

        case PacketType.GOODBYE:
            print(f"{user} has left the chat.")
            active_users.remove(user)
            user.sock.close()
            leave_msg = f"*** {user.username} has left the chat. ***"
            _broadcast_text(leave_msg)

        case PacketType.CHAT:
            broadcast_user_chat(user, pkt.payload)

        case PacketType.EMOTE:
            broadcast_emote(user, pkt.payload)

        case PacketType.DM:
            payload = pkt.payload.strip()
            parts = payload.split(None, 1)

            if len(parts) < 2:
                send_error_to(user, "Usage: /dm <username> <message>")
                return

            target_name, message_body = parts[0], parts[1]
            target_user = find_user_by_name(target_name)

            if not target_user:
                send_error_to(user, f"User '{target_name}' not online.")
                return

            print(f"DM from {user.username} to {target_user.username}: {message_body}")
            _send_private(user, target_user, message_body)

        case PacketType.COMMAND:
            cmd = pkt.payload
            match cmd:
                case "users":
                    print(f"User [{user.username}] requested /users.")
                    payload: str = format_user_list()
                    send_packet(user.sock, Packet(PacketType.CHAT, payload))
                case _:
                    send_error_to(user, f"Unknown command: {cmd}")

        case PacketType.ERROR:
            print(f"Received ERROR packet from {user}: {pkt.payload}")
            pass


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
