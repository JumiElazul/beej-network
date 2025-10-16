import socket
import os

MIN_PORT: int = 1025
MAX_PORT: int = (1 << 16)

def main():
    open_ports: list[int] = []

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        for port in range(MIN_PORT, MAX_PORT):
            result: int = s.connect_ex(('localhost', port))
            if result == 0:
                open_ports.append(port)

    print("-------------------------------")
    print("--------  Open ports:  --------")
    print("-------------------------------")
    print(open_ports)

if __name__ == "__main__":
    main()
