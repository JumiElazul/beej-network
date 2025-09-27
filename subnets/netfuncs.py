import sys
import json

def ipv4_to_value(ipv4_addr):
    """
    Convert a dots-and-numbers IP address to a single 32-bit numeric
    value of integer type. Returns an integer type.

    Example:

    ipv4_addr: "255.255.0.0"
    return:    4294901760  (Which is 0xffff0000 hex)

    ipv4_addr: "1.2.3.4"
    return:    16909060  (Which is 0x01020304 hex)
    """

    split: list[str] = ipv4_addr.split(".")
    nums: list[int] = [int(num) for num in split]
    val: int = (nums[0] << 24) | (nums[1] << 16) | (nums[2] << 8) | nums[3]
    return val

def value_to_ipv4(addr):
    """
    Convert a single 32-bit numeric value of integer type to a
    dots-and-numbers IP address. Returns a string type.

    Example:

    There is only one input value, but it is shown here in 3 bases.

    addr:   0xffff0000 0b11111111111111110000000000000000 4294901760
    return: "255.255.0.0"

    addr:   0x01020304 0b00000001000000100000001100000100 16909060
    return: "1.2.3.4"
    """

    byte_str: list[str] = []
    byte_str.append(str((addr >> 24) & 0xff))
    byte_str.append(str((addr >> 16) & 0xff))
    byte_str.append(str((addr >> 8) & 0xff))
    byte_str.append(str((addr) & 0xff))
    return ".".join(byte_str)

def get_subnet_mask_value(slash):
    """
    Given a subnet mask in slash notation, return the value of the mask
    as a single number of integer type. The input can contain an IP
    address optionally, but that part should be discarded.

    Returns an integer type.

    Example:

    There is only one return value, but it is shown here in 3 bases.

    slash:  "/16"
    return: 0xffff0000 0b11111111111111110000000000000000 4294901760

    slash:  "10.20.30.40/23"
    return: 0xfffffe00 0b11111111111111111111111000000000 4294966784
    """

    prefix_len: int = int(slash.split("/")[-1])
    mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF

    return mask

def ips_same_subnet(ip1, ip2, slash):
    """
    Given two dots-and-numbers IP addresses and a subnet mask in slash
    notation, return true if the two IP addresses are on the same
    subnet.

    Returns a boolean.

    FOR FULL CREDIT: this must use your get_subnet_mask_value() and
    ipv4_to_value() functions. Don't do it with pure string
    manipulation.

    This needs to work with any subnet from /1 to /31

    Example:

    ip1:    "10.23.121.17"
    ip2:    "10.23.121.225"
    slash:  "/23"
    return: True
    
    ip1:    "10.23.230.22"
    ip2:    "10.24.121.225"
    slash:  "/16"
    return: False
    """

    subnet_mask: int = get_subnet_mask_value(slash)
    ip1_subnet = ipv4_to_value(ip1) & subnet_mask
    ip2_subnet = ipv4_to_value(ip2) & subnet_mask

    return ip1_subnet == ip2_subnet

def get_network(ip_value, netmask):
    """
    Return the network portion of an address value as integer type.

    Example:

    ip_value: 0x01020304
    netmask:  0xffffff00
    return:   0x01020300
    """

    return ip_value & netmask

def find_router_for_ip(routers: dict[str, dict[str, str]], ip):
    """
    Search a dictionary of routers (keyed by router IP) to find which
    router belongs to the same subnet as the given IP.

    Return None if no routers is on the same subnet as the given IP.

    FOR FULL CREDIT: you must do this by calling your ips_same_subnet()
    function.

    Example:

    [Note there will be more data in the routers dictionary than is
    shown here--it can be ignored for this function.]

    routers: {
        "1.2.3.1": {
            "netmask": "/24"
        },
        "1.2.4.1": {
            "netmask": "/24"
        }
    }
    ip: "1.2.3.5"
    return: "1.2.3.1"


    routers: {
        "1.2.3.1": {
            "netmask": "/24"
        },
        "1.2.4.1": {
            "netmask": "/24"
        }
    }
    ip: "1.2.5.6"
    return: None
    """

    best_router: str | None = None
    best_prefix: int = -1

    for router_ip, info in routers.items():
        slash = info.get("netmask")
        if not slash:
            continue

        try:
            prefix = int(slash.split("/")[-1])
        except (ValueError, IndexError):
            continue

        if ips_same_subnet(router_ip, ip, slash):
            if prefix > best_prefix:
                best_prefix = prefix
                best_router = router_ip

    return best_router

def test_ipv4_to_value(ip: str, expected: int) -> bool:
    """
    Simple test wrapper for ipv4_to_value().
    Prints result and returns True/False depending on success.
    """
    result = ipv4_to_value(ip)
    if result == expected:
        print(f"PASS: {ip} -> {result} (expected {expected})")
        return True
    else:
        print(f"FAIL: {ip} -> {result} (expected {expected})")
        return False

def test_value_to_ipv4(value: int, expected: str) -> bool:
    """
    Simple test wrapper for value_to_ipv4().
    Prints result and returns True/False depending on success.
    """
    result = value_to_ipv4(value)
    if result == expected:
        print(f"PASS: {value} -> {result} (expected {expected})")
        return True
    else:
        print(f"FAIL: {value} -> {result} (expected {expected})")
        return False

def test_get_subnet_mask_value(slash: str, expected: int) -> bool:
    """
    Simple test wrapper for get_subnet_mask_value().
    Prints result and returns True/False depending on success.
    """
    result = get_subnet_mask_value(slash)
    if result == expected:
        print(f"PASS: {slash} -> {hex(result)} (expected {hex(expected)})")
        return True
    else:
        print(f"FAIL: {slash} -> {hex(result)} (expected {hex(expected)})")
        return False


def test_ips_same_subnet(ip1: str, ip2: str, slash: str, expected: bool) -> bool:
    """
    Simple test wrapper for ips_same_subnet().
    Prints result and returns True/False depending on success.
    """
    result = ips_same_subnet(ip1, ip2, slash)
    if result == expected:
        print(f"PASS: {ip1} , {ip2} , {slash} -> {result} (expected {expected})")
        return True
    else:
        print(f"FAIL: {ip1} , {ip2} , {slash} -> {result} (expected {expected})")
        return False

# def my_tests():
#     print("=====================================")
#     print("This is the result of my custom tests")
#     print("=====================================")
#
#     test_ipv4_to_value("255.255.0.0", 4294901760)
#     test_ipv4_to_value("1.2.3.4", 16909060)
#     test_ipv4_to_value("0.0.0.0", 0)
#     test_ipv4_to_value("255.255.255.255", 0xffffffff)
#
#     test_value_to_ipv4(4294901760, "255.255.0.0")
#     test_value_to_ipv4(16909060, "1.2.3.4")
#     test_value_to_ipv4(0, "0.0.0.0")
#     test_value_to_ipv4(0xffffffff, "255.255.255.255")
#
#     test_ips_same_subnet("10.23.121.17", "10.23.121.225", "/23", True)
#     test_ips_same_subnet("10.23.230.22", "10.24.121.225", "/16", False)
#     test_ips_same_subnet("192.168.1.0",  "192.168.1.255", "/24", True)
#     test_ips_same_subnet("192.168.1.42", "192.168.2.42",  "/24", False)
#     test_ips_same_subnet("192.168.1.127", "192.168.1.128", "/25", False)
#     test_ips_same_subnet("192.168.1.64",  "192.168.1.127", "/25", True)
#     test_ips_same_subnet("10.0.0.0", "10.0.0.1", "/31", True)
#     test_ips_same_subnet("10.0.0.2", "10.0.0.3", "/31", True)
#     test_ips_same_subnet("10.0.0.1", "10.0.0.2", "/31", False)
#     test_ips_same_subnet("10.0.0.1", "20.0.0.1",  "/1",  True)
#     test_ips_same_subnet("10.0.0.1", "200.0.0.1", "/1",  False)

## -------------------------------------------
## Do not modify below this line
##
## But do read it so you know what it's doing!
## -------------------------------------------

def usage():
    print("usage: netfuncs.py infile.json", file=sys.stderr)

def read_routers(file_name):
    with open(file_name) as fp:
        json_data = fp.read()
        
    return json.loads(json_data)

def print_routers(routers):
    print("Routers:")

    routers_list = sorted(routers.keys())

    for router_ip in routers_list:

        slash_mask = routers[router_ip]["netmask"]
        netmask_value = get_subnet_mask_value(slash_mask)
        netmask = value_to_ipv4(netmask_value)

        # Get the network number
        router_ip_value = ipv4_to_value(router_ip)
        network_value = get_network(router_ip_value, netmask_value)
        network_ip = value_to_ipv4(network_value)

        print(f" {router_ip:>15s}: netmask {netmask}: " \
            f"network {network_ip}")

def print_same_subnets(src_dest_pairs):
    print("IP Pairs:")

    src_dest_pairs_list = sorted(src_dest_pairs)

    for src_ip, dest_ip in src_dest_pairs_list:
        print(f" {src_ip:>15s} {dest_ip:>15s}: ", end="")

        if ips_same_subnet(src_ip, dest_ip, "/24"):
            print("same subnet")
        else:
            print("different subnets")

def print_ip_routers(routers, src_dest_pairs):
    print("Routers and corresponding IPs:")

    all_ips = sorted(set([i for pair in src_dest_pairs for i in pair]))

    router_host_map = {}

    for ip in all_ips:
        router = str(find_router_for_ip(routers, ip))
        
        if router not in router_host_map:
            router_host_map[router] = []

        router_host_map[router].append(ip)

    for router_ip in sorted(router_host_map.keys()):
        print(f" {router_ip:>15s}: {router_host_map[router_ip]}")


def main(argv):
    if "my_tests" in globals() and callable(my_tests):
        my_tests()
        return 0

    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    src_dest_pairs = json_data["src-dest"]

    print_routers(routers)
    print()
    print_same_subnets(src_dest_pairs)
    print()
    print_ip_routers(routers, src_dest_pairs)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
