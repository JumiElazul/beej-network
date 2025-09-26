def hash_ip_addr(ip_addr: str) -> int:
    split: list[str] = ip_addr.strip().split(".")
    nums: list[int] = [int(num) for num in split]

    return (nums[0] << 24) | (nums[1] << 16) | (nums[2] << 8) | (nums[3])

def unhash_ip_addr(hashed_ip: int) -> str:
    ip_bytes: list[int] = []

    ip_bytes.append((hashed_ip >> 24) & 0xFF)
    ip_bytes.append((hashed_ip >> 16) & 0xFF)
    ip_bytes.append((hashed_ip >> 8) & 0xFF)
    ip_bytes.append((hashed_ip) & 0xFF)

    return ".".join([str(b) for b in ip_bytes])

def main():
    ip_addr: str = "198.51.100.10"

    hash: int = hash_ip_addr(ip_addr)
    original: str = unhash_ip_addr(hash)

    print(f"ip_addr: {ip_addr} -> hashed {hash} -> deconstructed: {original}")

if __name__ == "__main__":
    main()
