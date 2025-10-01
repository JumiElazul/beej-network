import socket
import os
import time

DEST_URL: str = "time.nist.gov"
DEST_PORT: int = 37
BYTES_WANTED: int = 4

def system_seconds_since_1900():
    seconds_delta = 2208988800

    seconds_since_unix_epoch = int(time.time())
    seconds_since_1900_epoch = seconds_since_unix_epoch + seconds_delta

    return seconds_since_1900_epoch

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((DEST_URL, DEST_PORT))
        s.settimeout(2.0)

        rec: bytes = b""
        while len(rec) < BYTES_WANTED:
            b: bytes = s.recv(BYTES_WANTED - len(rec))
            rec += b

        print(f"System time: {system_seconds_since_1900()} since epoch.")
        print(f"NIST time  : {int.from_bytes(rec, "big")} since epoch.")

    print("Closing connection...")

if __name__ == "__main__":
    main()
