import os
import socket
import time

def sys_time_since_epoch():
    seconds_delta = 2208988800 

    seconds_since_unix_epoch = int(time.time())
    seconds_since_1900_epoch = seconds_since_unix_epoch + seconds_delta

    return seconds_since_1900_epoch

if __name__ == "__main__":
    with socket.socket() as sock:
        sock.settimeout(5.0)
        sock.connect(("time.nist.gov", 37))

        buf = bytearray()
        while len(buf) < 4:
            chunk = sock.recv(4 - len(buf))
            if not chunk:
                raise ConnectionError("peer closed before sending the full TIME payload.")
            buf += chunk

        t = int.from_bytes(buf, "big")

        if t == 0:
            print("NIST time returned 0 (incorrect), try again in 4 seconds.")
        else:
            print(f"NIST time since epoch   :  {t} seconds.")
            print(f"System time since epoch :  {sys_time_since_epoch()} seconds.")

