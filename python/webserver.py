import socket
import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor

iso_std: str = "ISO-8859-1"
default_port: int = 21055

def build_response() -> bytes:
    return (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 6\r\n"
        "Connection: close\r\n"
        "\r\n"
        "Hello!"
    ).encode(iso_std)

def parse_inc_header(s: socket.socket) -> tuple[bytes, bytes]:
    buf = b""

    while True:
        chunk = s.recv(4096)
        if not chunk:
            return bytes(buf), b""
        buf += chunk
        idx = buf.find(b"\r\n\r\n")
        if idx != -1:
            idx += 4
            return bytes(buf[:idx]), bytes(buf[idx:])

def parse_content_length(header_bytes: bytes) -> int | None:
    lines: list[bytes] = header_bytes.split(b"\r\n")
    for line in lines:
        if line.lower().startswith(b"content-length:"):
            try:
                return int(line.split(b" ")[1])
            except ValueError:
                print("Error converting Content-Length into int.")
                return None

    return None

def recv_exact(s: socket.socket, length: int) -> bytes:
    out = b""

    while len(out) < length:
        chunk = s.recv(min(4096, length - len(out)))
        if not chunk:
            raise ConnectionError("Connection closed before reading full body")
        out += chunk

    return bytes(out)

def handle_connection(s: socket.socket):
    s.settimeout(0.2)
    headers, prebody = parse_inc_header(s)
    content_length = parse_content_length(headers) or 0

    remaining = max(0, content_length - len(prebody))
    body = prebody + (recv_exact(s, remaining) if remaining else b"")

    request = headers + body

    print(f"Received request from {s}:")
    print(request.decode("ISO-8859-1", errors="replace"))

    response = build_response()
    s.sendall(response)
    s.close()

def main(argc: int, argv: list[str]):
    target_port: int = default_port 

    if argc > 1:
        try:
            target_port = int(argv[1])
        except ValueError:
            print("<target_port> could not be converted to a port number; invalid format.  Using default port.")

    max_workers: int = (os.cpu_count() or 4) * 4

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', target_port))
        s.listen()
        s.settimeout(1.0)

        print(f"webserver listening on port {target_port} with {max_workers} workers...")

        running: bool = True

        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="worker") as pool:
            try:
                while running:
                    try:
                        conn: tuple[socket.socket, socket._RetAddress] = s.accept()
                    except socket.timeout:
                        continue

                    pool.submit(handle_connection, conn[0])
            except KeyboardInterrupt:
                print("Shutting down...")
            finally:
                pass


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
