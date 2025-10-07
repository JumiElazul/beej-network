import heapq
import sys
import json
import math  # If you want to use math.inf for infinity

def ipv4_to_value(ipv4_addr: str) -> int:
    split: list[str] = ipv4_addr.split(".")
    nums: list[int] = [int(x) for x in split]
    return (nums[0] << 24) | (nums[1] << 16) | (nums[2] << 8) | nums[3]

def value_to_ipv4(addr: int) -> str:
    nums: list[str] = []
    nums.append(str((addr >> 24) & 0xFF))
    nums.append(str((addr >> 16) & 0xFF))
    nums.append(str((addr >> 8)  & 0xFF))
    nums.append(str((addr >> 0)  & 0xFF))
    return ".".join(nums)

def get_subnet_mask_value(slash: str) -> int:
    ntwk_bits: int = int(slash.split("/")[1])
    host_bits: int = 32 - ntwk_bits

    return ((1 << ntwk_bits) - 1) << host_bits

def ips_same_subnet(ip1: str, ip2: str, slash: str) -> bool:
    ip1_val: int = ipv4_to_value(ip1)
    ip2_val: int = ipv4_to_value(ip2)
    subnet_mask: int = get_subnet_mask_value(slash)

    netwk1: int = ip1_val & subnet_mask
    netwk2: int = ip2_val & subnet_mask
    return netwk1 == netwk2

def get_network(ip_value: int, netmask: int) -> int:
    return ip_value & netmask

def find_router_for_ip(routers, ip):
    for router_ip, data in routers.items():
        slash = data.get("netmask", "/24")
        if ips_same_subnet(ip, router_ip, slash):
            return router_ip

    return None

def build_graph(routers: dict[str, dict]) -> dict[str, dict[str, int]]:
    graph: dict[str, dict[str, int]] = {}
    for router, info in routers.items():
        graph.setdefault(router, {})
        connections = info.get("connections", {})
        for vertex, edge in connections.items():
            ad = int(edge.get("ad", 1))
            graph[router][vertex] = ad

    return graph

def reconstruct_path(prev: dict[str, str | None], start: str, goal: str) -> list[str]:
    path: list[str] = []
    cur = goal

    if cur not in prev and cur != start:
        return []

    while cur is not None:
        path.append(cur)
        if cur == start:
            break
        cur = prev.get(cur)

    path.reverse()
    return path

def routers_shortest_path(graph: dict[str, dict[str, int]], start: str, goal: str) -> list[str]:
    if start == goal:
        return [start]

    dist: dict[str, int] = {start: 0}
    prev: dict[str, str | None] = {start: None}
    pq: list[tuple[int, str]] = [(0, start)]
    visited: set[str] = set()

    while pq:
        dis, curr = heapq.heappop(pq)
        if curr in visited:
            continue

        visited.add(curr)

        if curr == goal:
            return reconstruct_path(prev, start, goal)

        for vertex, weight in graph.get(curr, {}).items():
            if vertex in visited:
                continue

            new_dist = dis + weight
            if new_dist < dist.get(vertex, math.inf):
                dist[vertex] = new_dist
                prev[vertex] = curr
                heapq.heappush(pq, (new_dist, vertex))

    return []

def dijkstras_shortest_path(routers, src_ip, dest_ip):
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

    src_router = find_router_for_ip(routers, src_ip)
    dest_router = find_router_for_ip(routers, dest_ip)

    if src_router is None or dest_router is None:
        return None

    if src_router == dest_router:
        return []

    graph = build_graph(routers)
    path_including_endpoints = routers_shortest_path(graph, src_router, dest_router)

    if not path_including_endpoints:
        return []

    return path_including_endpoints

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
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def main():
    json_data = read_routers("example1.json")

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)
    return 0

if __name__ == "__main__":
    sys.exit(main())
    
