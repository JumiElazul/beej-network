import sys

# Read in the tcp_addrs_0.txt file.
# Split the line in two, the source and destination addresses.
# Write a function that converts the dots-and-numbers IP addresses into bytestrings.
# Read in the tcp_data_0.dat file.
# Write a function that generates the IP pseudo header bytes from the IP addresses from tcp_addrs_0.txt and the TCP length from the tcp_data_0.dat file.
# Build a new version of the TCP data that has the checksum set to zero.
# Concatenate the pseudo header and the TCP data with zero checksum.
# Compute the checksum of that concatenation
# Extract the checksum from the original data in tcp_data_0.dat.
# Compare the two checksums. If they’re identical, it works!
# Modify your code to run it on all 10 of the data files. The first 5 files should have matching checksums! The second five files should not! That is, the second five files are simulating being corrupted in transit.

def usage():
    print("usage: tcp-packet <file_number>")
    print("valid numbers are found in the inputs/ folder.")

def get_ips_from_file(filepath: str) -> list[str]:
    with open(filepath, "rb") as fp:
        try:
            line: str = fp.read().decode()
            return line.strip().split()
        except:
            print("Something went wrong in get_ips_from_file")
            exit(1)

def byteify_ip(ip: str) -> bytes:
    b: bytes = b""

    str_split: list[str] = ip.split(".")
    nums: list[int] = [int(num) for num in str_split]

    for num in nums:
        b += num.to_bytes(1, "big")

    return b

def get_checksum_from_header(header: bytes) -> int:
    byte_slice: bytes = header[16:18]
    return int.from_bytes(byte_slice)

def checksum(pseudoheader: bytes, tcp_zero_cksum: bytes):
    data = pseudoheader + tcp_zero_cksum
    offset = 0

    total = 0

    while offset < len(data):
        word = int.from_bytes(data[offset:offset + 2], "big")
        offset += 2

        total += word
        total = (total & 0xFFFF) + (total >> 16)

    return ~(total) & 0xFFFF

def test_packet_no(file_no: int):
    pseudoheader: bytes = b""

    prefix_addr: str = f"inputs/tcp_addrs_{file_no}.txt"
    prefix_data: str = f"inputs/tcp_data_{file_no}.dat"

    ips = get_ips_from_file(prefix_addr)

    src_ip_bytes = byteify_ip(ips[0])
    dst_ip_bytes = byteify_ip(ips[1])

    pseudoheader += src_ip_bytes
    pseudoheader += dst_ip_bytes

    pseudoheader += (0).to_bytes(1, "big")
    pseudoheader += (6).to_bytes(1, "big")

    with open(prefix_data, "rb") as fp:
        tcp_data: bytes = fp.read()
        tcp_len: int = len(tcp_data)

        cksum_expected: int = get_checksum_from_header(tcp_data)

        tcp_zero_cksum = tcp_data[:16] + b"\x00\x00" + tcp_data[18:]

        if len(tcp_zero_cksum) % 2 == 1:
            tcp_zero_cksum += b'\x00'

        pseudoheader += tcp_len.to_bytes(2, "big")

        cksum_calc: int = checksum(pseudoheader, tcp_zero_cksum)

        ok = (cksum_calc == cksum_expected)

        status = "PASS" if ok else "FAIL"
        print(f"{file_no}: calc=0x{cksum_calc:04x}  expect=0x{cksum_expected:04x}  -> {status}")

def main():
    for file_no in range(0, 10):
        test_packet_no(file_no)

if __name__ == "__main__":
    main()
