import sys

IP_FP_PREFIX: str = "tcp_data/tcp_addrs_"
DAT_FP_PREFIX: str = "tcp_data/tcp_data_"

def read_file_binary(filepath: str) -> bytes:
    with open(filepath, "rb") as fp:
        return fp.read()

def ip_into_bytestring(ip: str) -> bytes:
    split: list[str] = ip.split(".")
    byte_list: list[bytes] = [int(s).to_bytes(1, "big") for s in split]
    return b"".join(byte_list)

def parse_ips(data: bytes) -> tuple[str, str]:
    ip1, ip2 = data.decode().split()
    return ip1, ip2

def build_pseudoheader(ips: tuple[str, str], tcp_len: int) -> bytearray:
    """
    The pseudoheader format is as follows, each line is 8 bytes, with a pipe (|)
    for the 4 byte seperator:

    0x0 Source Addr | Dest Addr
    0x9 Zero   PTCL | TCP Length

    Zero is always 0x0, PTCL is 0x06 for TCP.  TCP length is the big-endian
    representation of the length of the total bytes in the .dat file.
    """

    pseudoheader: bytearray = bytearray()

    src, dst = ip_into_bytestring(ips[0]), ip_into_bytestring(ips[1])

    pseudoheader += src + dst
    pseudoheader += (0x00).to_bytes(1, "big")
    pseudoheader += (0x06).to_bytes(1, "big")
    pseudoheader += tcp_len.to_bytes(2, byteorder="big")

    return pseudoheader

def calc_checksum(data: bytearray) -> int:
    checksum: int = 0

    for i in range(0, len(data), 2):
        word = int.from_bytes(data[i:i + 2], "big")
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

    checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return (~checksum) & 0xFFFF

def compare(ip_path: str, data_path: str):
    ip_file: bytes = read_file_binary(ip_path)
    data_file: bytes = read_file_binary(data_path)

    ips: tuple[str, str] = parse_ips(ip_file)

    pseudoheader: bytearray = build_pseudoheader(ips, len(data_file))
    tcp_checksum: int = int.from_bytes(data_file[16:18], "big")
    tcp_zero_checksum: bytes = data_file[:16] + b"\x00\x00" + data_file[18:]

    if len(tcp_zero_checksum) % 2 == 1:
        tcp_zero_checksum += b'\x00'

    data: bytearray = pseudoheader + tcp_zero_checksum
    checksum: int = calc_checksum(data)

    res: str = "PASS" if tcp_checksum == checksum else "FAIL"
    print(f"[ Checksum {checksum:>6} : Expected: {tcp_checksum:>6} ] -> [{res}]")

def main(argc: int, argv: list[str]):
    for i in range(0, 10):
        ip_path: str = IP_FP_PREFIX + str(i) + ".txt"
        data_path: str = DAT_FP_PREFIX + str(i) + ".dat"
        compare(ip_path, data_path)

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
