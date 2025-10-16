import threading
import sys
import os
import socket
from packet import *

from chatui import init_windows, read_command, print_message, end_windows

server_socket: socket.socket
running: bool = True

def listen_server(server: socket.socket):
    buf = bytearray()

    while True:
        try:
            pkt: Packet | None = receive_packet(server, buf)
        except ConnectionResetError:
            print("Server closed connection.")
            break
        except Exception as e:
            print(f"Error receiving packet: {e}")
            break

        if pkt is None:
            continue

        print_message(pkt.payload)

        if pkt.type is PacketType.ABORT:
            os._exit(1)


def start_client(username: str, server_addr: str, port: int) -> socket.socket:
    global server_socket

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.connect((server_addr, port))
    except socket.error:
        print(f"Error connecting to {server_addr}:{port}.")
        sys.exit(1)

    init_windows()

    server_thread = threading.Thread(target=listen_server, args=[server_socket], daemon=True)
    server_thread.start()

    pkt: Packet = Packet(PacketType.HELLO, username)
    send_packet(server_socket, pkt)

    return server_socket


def end_client(server: socket.socket):
    goodbye_pkt: Packet = Packet(PacketType.GOODBYE, "")
    send_packet(server, goodbye_pkt)
    end_windows()
    server.close()


def handle_help():
    print_message("== help menu ==")
    print_message("/help                 : help menu.  you're here.")
    print_message("/users                : lists all users currently connected.")
    print_message("/me                   : emote command.  ex. /em does a dance -> [user does a dance]")
    print_message("/dm <username> <text> : direct messages <text> to <name>")
    print_message("/q                    : quit the application")


def handle_users():
    pkt: Packet = Packet(PacketType.COMMAND, "users")
    send_packet(server_socket, pkt)


def handle_emote(emote_text: str):
    if not emote_text:
        return

    emote_pkt = Packet(PacketType.EMOTE, emote_text)
    send_packet(server_socket, emote_pkt)


def handle_whisper(command: str):
    parts = command.split(None, 1)

    if len(parts) < 2:
        print_message("usage: /dm <username> <message>")
        return

    target, message = parts[0].strip(), parts[1].strip()

    if not target or not message:
        print_message("Usage: /dm <username> <message>")
        return

    pm_payload = f"{target} {message}"
    pm_pkt = Packet(PacketType.DM, pm_payload)
    send_packet(server_socket, pm_pkt)


def handle_quit():
    global running
    running = False


def handle_non_chat_commands(command: str):
    split: list[str] = command.split(" ")
    command = split[0]
    rest = " ".join(split[1:])

    match command:
        case "/help" | "/h":
            handle_help()
        case "/users":
            handle_users()
        case "/me":
            handle_emote(rest)
        case "/dm":
            handle_whisper(rest)
        case "/q":
            handle_quit()
        case _:
            print_message(f"command {command} not recognized.")


def handle_command(command: str):
    if not command.startswith("/"):
        chat_pkt: Packet = Packet(PacketType.CHAT, command)
        send_packet(server_socket, chat_pkt)
    else:
        handle_non_chat_commands(command)


def main(argv: list[str]):
    try:
        username: str = argv[1]
        server_addr: str = argv[2]
        port: int = int(argv[3])
    except:
        print("usage: python3 chat_client.py <username> <server_addr> <port>")
        sys.exit(1)

    server_socket: socket.socket = start_client(username, server_addr, port)

    while running:
        try:
            command: str = read_command(f"{username}> ")
        except:
            break

        handle_command(command)

    end_client(server_socket)

if __name__ == "__main__":
    main(sys.argv)
