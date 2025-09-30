import os
import sys
import socket
from dataclasses import dataclass
from typing import Union, Tuple, Optional

Addr = Union[tuple[str, int], tuple[str, int, int, int]]

CRLF = "\r\n"
ENCODING = "ISO-8859-1"
DEFAULT_PORT = 33090
RECV_CHUNK = 4096
HEADER_END = b"\r\n\r\n"
UNSAFE_MODE = False
ROOT_DIR = os.getcwd()

RESPONSE_404 = (
    "HTTP/1.1 404 Not Found\r\n"
    "Content-Type: text/plain\r\n"
    "Content-Length: 13\r\n"
    "Connection: close\r\n"
    "\r\n"
    "404 not found"
).encode(ENCODING)

EXT_TO_CONTENT_TYPE: dict[str, str] = {
    ".txt" : "text/plain",
    ".html": "text/html",
    ".jpeg": "image/jpeg",
    ".jpg" : "image/jpeg",
}

@dataclass
class HttpRequest:
    method: str
    path: str
    protocol: str

def _resolve_path_safe(url_path: str, root: str) -> Optional[str]:
    abs_root = os.path.abspath(root)
    requested = os.path.normpath(os.path.join(abs_root, url_path.lstrip("/")))

    if os.path.commonpath([abs_root, requested]) != abs_root:
        print("_resolve_path_safe returned an unsafe path.", file=sys.stderr)
        return None

    return requested

def _resolve_path_unsafe(url_path: str) -> str:
    path: str = os.path.abspath(os.path.normpath(os.getcwd()))
    fullpath: str = path + url_path
    return fullpath

def sanitize_path(url_path: str) -> Optional[str]:
    if UNSAFE_MODE:
        return _resolve_path_unsafe(url_path)
    else:
        return _resolve_path_safe(url_path, ROOT_DIR)

def make_response(status_line: str, headers: dict[str, str], body: bytes) -> bytes:
    head = status_line + CRLF

    for key, val in headers.items():
        head += f"{key}: {val}{CRLF}"

    head += CRLF
    return head.encode(ENCODING) + body

def read_file_bytes(filepath: str) -> Optional[bytes]:
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"Cannot read file: {filepath} ({e})", file=sys.stderr)
        return None

def receive_request(sock: socket.socket) -> Optional[str]:
    buf = bytearray()
    try:
        while True:
            chunk = sock.recv(RECV_CHUNK)
            if not chunk:
                break
            buf += chunk
            idx = buf.find(HEADER_END)
            if idx != -1:
                buf = buf[: idx + len(HEADER_END)]
                return bytes(buf).decode(ENCODING)
    except socket.timeout:
        pass
    return None

def parse_request(request_text: str) -> Optional[HttpRequest]:
    request_line = request_text.split(CRLF, 1)[0]
    method, path, protocol = request_line.split(" ", 2)
    path = sanitize_path(path)

    if path is None:
        return None

    return HttpRequest(method=method, path=path, protocol=protocol)

def handle_get(sock: socket.socket, req: HttpRequest) -> None:
    ext: str = os.path.splitext(req.path)[1]

    if ext not in EXT_TO_CONTENT_TYPE and not UNSAFE_MODE:
        print(f"Unsupported extension type: {ext}")
        sock.sendall(RESPONSE_404)
        return

    ext_type = EXT_TO_CONTENT_TYPE.get(ext)

    body = read_file_bytes(req.path)
    if body is None:
        sock.sendall(RESPONSE_404)
        return

    headers = {
        "Content-Type": f"{ext_type}",
        "Content-Length": str(len(body)),
        "Connection": "close",
    }
    resp = make_response("HTTP/1.1 200 OK", headers, body)
    sock.sendall(resp)

def dispatch_request(sock: socket.socket, request_text: str) -> None:
    req = parse_request(request_text)
    if req is None:
        sock.sendall(RESPONSE_404)
        return

    if req.method.upper() == "GET":
        handle_get(sock, req)
    else:
        sock.sendall(RESPONSE_404)

def handle_connection(inc_conn: Tuple[socket.socket, Addr]) -> None:
    sock, addr = inc_conn
    with sock:
        sock.settimeout(2.0)
        request_text = receive_request(sock)
        if request_text is None:
            print(f"Could not read full header from {addr}", file=sys.stderr)
            return

        print(f"Request received from {addr}:")
        print(request_text)
        dispatch_request(sock, request_text)

def main(argc: int, argv: list[str]) -> None:
    global ROOT_DIR, UNSAFE_MODE

    port = DEFAULT_PORT

    for arg in argv[1:]:
        if arg == "--unsafe":
            UNSAFE_MODE = True
        else:
            try:
                port = int(arg)
            except ValueError:
                print(f"Ignoring unrecognized argument: {arg}", file=sys.stderr)

    mode: str = "unsafe" if UNSAFE_MODE else "safe"
    print(f"Starting simple webserver in {mode} mode.")

    with socket.socket() as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("", port))
        server_sock.listen()
        print(f"Webserver listening on port {port}")

        try:
            while True:
                conn = server_sock.accept()
                print(f"Connection accepted from {conn[1]}")
                handle_connection(conn)
        except KeyboardInterrupt:
            print("KeyboardInterrupt hit, stopping server...")

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
