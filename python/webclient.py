import sys
import socket

iso_standard: str = "ISO-8859-1"
target_host: str = ""
target_port: int = 80
target_file: str = "/"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_host = sys.argv[1]
    if len(sys.argv) > 2:
        target_port = int(sys.argv[2])
    if len(sys.argv) > 3:
        target_file += sys.argv[3]

    request = (
        f"GET {target_file} HTTP/1.1\r\n"
        f"Host: {target_host}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    sock: socket.socket = socket.socket()
    sock.settimeout(5.0)
    sock.connect((target_host, target_port))
    sock.sendall(request.encode(iso_standard))

    chunks: list[bytes] = []
    while True:
        d = sock.recv(4096)

        if not d:
            break

        chunks.append(d)
    sock.close()

    response_bytes: bytes = b"".join(chunks)
    response: str = response_bytes.decode(iso_standard, errors="replace")
    print(f"Response from server [host: {target_host}, port: {target_port}]")
    print(response)

