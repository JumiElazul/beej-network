import socket
import sys
import os

iso_std: str = "ISO-8859-1"

def usage(argc: int):
    if argc < 2:
        print("usage: python3 webclient.py <target_url> <target_port = 80> <file_path = />")
        print("<target_url> required.")
        print("<target_port> defaults to 80 if unspecified.")
        print("<file_path> defaults to '/' if unspecified.")
        exit(1)

def build_request(host: str, path: str, payload: str) -> bytes:
    return (
        f"GET /{path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Content-Length: {len(payload)}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{payload}"
    ).encode(iso_std)

def main(argc: int, argv: list[str]):
    usage(argc)

    target_url: str = ""
    target_port: int = 80
    target_path: str = "/"
    payload: str = ""

    if argc > 1:
        target_url = argv[1]
    if argc > 2:
        try:
            target_port = int(argv[2])
        except ValueError:
            print("<target_port> invalid; using default port 80.")
    if argc > 3:
        target_path = argv[3]
    if argc > 4:
        payload = argv[4]

    with socket.socket() as s:
        s.settimeout(4.0)
        print(f"Connecting to {target_url} on port {target_port}...")
        s.connect((target_url, target_port))

        request: bytes = build_request(target_url, target_path, payload)
        s.sendall(request)

        received: bytes = b""
        while True:
            rec_bytes: bytes = s.recv(4096)
            if len(rec_bytes) == 0:
                break
            received += rec_bytes

        print(f"Received response from {target_url}:")
        print(received.decode(iso_std, errors="replace"))

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
