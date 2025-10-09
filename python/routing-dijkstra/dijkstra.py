import sys
import json
import math  # If you want to use math.inf for infinity
from typing import Optional

def get_subnet_mask_from_slash(slash: str) -> int:
    n = int(slash.split("/")[-1])
    return ((1 << n) - 1) << (32 - n)

def ipv4_to_value(ip: str) -> int:
    split: list[str] = ip.split(".")
    octets: list[int] = [int(n) for n in split]

    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]

def is_same_subnet(ip1: str, ip2: str, slash: str) -> bool:
    subnet_mask: int = get_subnet_mask_from_slash(slash)

    ip1_val: int = ipv4_to_value(ip1)
    ip2_val: int = ipv4_to_value(ip2)

    return (ip1_val & subnet_mask) == (ip2_val & subnet_mask)

def value_to_ipv4(value: int) -> str:
    value &= 0xFFFFFFFF
    return ".".join(str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0))

def find_start_router(routers: dict[str, dict], src_ip: str) -> Optional[str]:
    for router_ip, data in routers.items():
        subnet_mask: str = data.get("netmask", "/24")
        if is_same_subnet(router_ip, src_ip, subnet_mask):
            return router_ip
    return None 

def init_dijkstra(routers: dict[str, dict], src_ip: str):
    nodes: set[str] = set(routers.keys())
    distances: dict[str, float] = {node: math.inf for node in nodes}
    parents: dict[str, Optional[str]] = {node: None for node in nodes}
    to_visit: set[str] = set(nodes)

    start: Optional[str] = find_start_router(routers, src_ip)
    if start is None:
        raise ValueError(f"No router found on the same subnet as {src_ip}")

    distances[start] = 0.0
    return to_visit, distances, parents, start

def dijkstras_shortest_path(routers: dict[str, dict], src_ip, dest_ip):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """

    to_visit, distances, parents, start = init_dijkstra(routers, src_ip)

    while to_visit:
        current_node: str = min(to_visit, key=lambda n: distances[n])
        to_visit.remove(current_node)

        edges = routers.get(current_node, {}).get("connections", {})

        for neighbor, link in edges.items():
            if neighbor not in distances:
                continue
            if neighbor not in to_visit:
                continue

            weight = link.get("ad", 1)
            alt = distances[current_node] + weight

            if alt < distances[neighbor]:
                distances[neighbor] = alt
                parents[neighbor] = current_node

    
    path: list[str] = []
    dest_router = find_start_router(routers, dest_ip)

    path: list[str] = []
    curr: Optional[str] = dest_router

    while curr is not None and curr != start:
        path.append(curr)
        curr = parents[curr]

    if curr != start:
        path = []

    if len(path) > 0:
        path.append(start)
        path.reverse()

    print(f"{src_ip} -> {dest_ip}   {path}")

#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        # print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def main(argv):
    router_file_name: str = "example1.json"
    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
