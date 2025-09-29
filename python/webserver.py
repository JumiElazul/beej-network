import socket
import sys
import os

iso_std: str = "ISO-8859-1"
default_port: int = 21055

def build_response() -> bytes:
    return (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 6\r\n"
        "Connection: close\r\n"
        "\r\n"
        "Hello!\r\n"
    ).encode(iso_std)

def parse_inc_header(s: socket.socket):
    request: bytes = b""
    cont_len: int | None = None

    while True:
        req_bytes: bytes = s.recv(4096)
        request += req_bytes

        if req_bytes.endswith(b"\r\n\r\n"):
            break

    return request

def recv_bytes(s: socket.socket, amount: int, bytestream: bytes) -> bytes:
    received: int = 0
    while received < amount:
        rec: bytes = s.recv(4096)
        received += len(rec)
        bytestream += rec

    return bytestream

def handle_connection(s: socket.socket):
    request: bytes = parse_inc_header(s)

    print(f"Received request from {s}:")
    print(request.decode(iso_std))

    response: bytes = build_response()
    s.sendall(response)
    s.close()

def main(argc: int, argv: list[str]):
    target_port: int = default_port 

    if argc > 1:
        try:
            target_port = int(argv[1])
        except ValueError:
            print("<target_port> could not be converted to a port number; invalid format.  Using default port.")

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', target_port))
        s.listen()

        print(f"webserver listening on port {target_port}...")

        while True:
            inc_conn: tuple[socket.socket, socket._RetAddress] = s.accept()
            handle_connection(inc_conn[0])

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
