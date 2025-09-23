import os
import sys 
import socket
from html import escape
from urllib.parse import quote

iso_standard: str = "ISO-8859-1"
default_port: int = 21500
max_port: int = 65535

RESPONSE_404: bytes = (
    b"HTTP/1.1 404 Not Found\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: 13\r\n"
    b"Connection: close\r\n"
    b"\r\n"
    b"404 Not found\r\n"
)

RESPONSE_405: bytes = (
    b"HTTP/1.1 405 Method Not Allowed\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: 22\r\n"
    b"Connection: close\r\n"
    b"\r\n"
    b"405 Method Not Allowed\r\n"
)

valid_methods: list[str] = ["GET"]
ext_to_content_type: dict[str, str] = {
        ".txt": "text/plain",
        ".htm": "text/html",
        ".html": "text/html",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
     }

def set_target_port() -> int:
    target_port: int = default_port
    if len(sys.argv) > 1:
        try:
            target_port = int(sys.argv[1])

            if target_port < 1025 or target_port > max_port:
                raise
            
            return target_port
        except:
            print(f"Invalid port specified, using default {default_port}")

    return default_port

def build_directory_listing_html() -> bytes:
    entries = []
    print("No file was specified '/', building directory entries.")
    try:
        for name in sorted(os.listdir()):
            full = os.path.join(".", name)
            if os.path.isfile(full):
                ext = os.path.splitext(name)[1]
                if ext in ext_to_content_type:
                    safe_text = escape(name)
                    safe_href = "/" + quote(name)
                    entries.append(f'<li><a href="{safe_href}">{safe_text}</a></li>')
    except Exception as e:
        msg = escape(f"Error reading directory: {e}")
        html = f"<!doctype html><meta charset={iso_standard}><h1>Directory</h1><p>{msg}</p>"
        body = html.encode(iso_standard)
        header = (
            f"HTTP/1.1 500 Internal Server Error\r\n"
            f"Content-Type: text/html; charset={iso_standard}\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: close\r\n\r\n"
        ).encode(iso_standard)
        return header + body

    print(f"Showing directory files: {entries}")

    html = (
        "<!doctype html>"
        f"<meta charset={iso_standard}>"
        "<title>Directory listing</title>"
        "<h1>Directory listing</h1>"
        "<ul>"
        + ("\n".join(entries) if entries else "<li><em>(no servable files)</em></li>")
        + "</ul>"
    )

    body = html.encode(iso_standard)
    header = (
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: text/html; charset={iso_standard}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode(iso_standard)
    return header + body

def sanitize_uri(uri: str) -> str:
    # For now, only handle files from the directory the webserver is running in.
    stripped_uri: str = os.path.split(uri)[-1]

    if stripped_uri == "":
        stripped_uri = "/"

    print(f"uri {uri} -> {stripped_uri} [sanitized]")

    return stripped_uri

def read_file_bytes(filepath: str) -> bytes | None:
    try:
        with open(filepath, "rb") as fp:
            data = fp.read()
            return data
    except:
        return None

def build_response_for_req(request: str) -> bytes:
    request_line: str = request.split("\r\n")[0]
    method, uri, http_version = request_line.split(" ") # HTTP version unused currently

    if method not in valid_methods:
        return RESPONSE_405

    safe_uri: str = sanitize_uri(uri)

    if safe_uri == "/":
        return build_directory_listing_html()

    ext = os.path.splitext(safe_uri)[1]

    if ext not in ext_to_content_type:
        return RESPONSE_404

    content_type: str = ext_to_content_type[ext]

    file_bytes: bytes | None = read_file_bytes(safe_uri)
    if file_bytes is None:
        return RESPONSE_404

    content_length: int = len(file_bytes)

    response_header = (
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {content_length}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode(iso_standard)

    return response_header + file_bytes

def handle_new_connection(s: socket.socket):
    print(f"Handling socket {s}:")
    request_bytes: bytes = b""

    while True:
        r = s.recv(4096)

        if not r:
            break

        request_bytes += r

        if r.endswith(b"\r\n"):
            break

    request: str = request_bytes.decode(iso_standard, errors="replace")
    print(f"request: {request}")
    response: bytes = build_response_for_req(request)
    s.sendall(response)

if __name__ == "__main__":
    target_port = set_target_port()

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", target_port))
        s.listen()
        print(f"Webserver listening on port {target_port}...")

        try:
            while True:
                with s.accept()[0] as new_socket:
                    handle_new_connection(new_socket)
        except KeyboardInterrupt:
            print("KeyboardInterupt stopping server.")
