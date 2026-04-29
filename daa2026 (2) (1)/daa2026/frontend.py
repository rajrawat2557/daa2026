import os
import subprocess

import requests

LOCATIONIQ_DIRECTIONS_URL = "https://us1.locationiq.com/v1/directions/driving/{origin};{destination}"
DEFAULT_TIMEOUT = 15
GRAPH_FILE_PATH = "runtime_graph.txt"

NODES = {
    0: {"name": "ISBT", "coord": "30.2881,77.9980"},
    1: {"name": "Clock Tower", "coord": "30.3254,78.0413"},
    2: {"name": "Rajpur Road", "coord": "30.3440,78.0546"},
    3: {"name": "Ballupur", "coord": "30.3166,78.0339"},
    4: {"name": "Prem Nagar", "coord": "30.2695,77.9950"},
    5: {"name": "Clement Town", "coord": "30.2802,77.9734"},
}
EDGE_TEMPLATE = [(0, 1), (1, 2), (1, 3), (3, 4), (4, 5), (2, 3)]
FALLBACK_EDGE_KM = {
    (0, 1): 3.0,
    (1, 2): 4.0,
    (1, 3): 2.0,
    (3, 4): 5.0,
    (4, 5): 3.0,
    (2, 3): 3.0,
}


def to_lon_lat(lat_lng):
    lat, lng = [x.strip() for x in lat_lng.split(",")]
    return f"{lng},{lat}"


def fetch_route(api_key, origin, destination):
    url = LOCATIONIQ_DIRECTIONS_URL.format(
        origin=to_lon_lat(origin),
        destination=to_lon_lat(destination),
    )
    params = {
        "key": api_key,
        "overview": "false",
        "steps": "false",
        "alternatives": "false",
        "geometries": "geojson",
    }
    response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if data.get("routes"):
        return data["routes"][0]
    if data.get("results"):
        return data["results"][0]
    raise ValueError("No route found in API response.")


def route_metrics(route):
    duration = float(route.get("duration", 0.0))
    distance = float(route.get("distance", 0.0))

    traffic = route.get("traffic")
    if traffic is not None:
        try:
            congestion = float(traffic)
        except (TypeError, ValueError):
            congestion = 2.0
    else:
        speed = (distance / duration) if duration > 0 else 0.0
        if speed <= 4:
            congestion = 5.0
        elif speed <= 7:
            congestion = 4.0
        elif speed <= 10:
            congestion = 3.0
        elif speed <= 14:
            congestion = 2.0
        else:
            congestion = 1.0

    return duration, distance, congestion


def get_user_input():
    print("Graph node mapping (real coordinates used for API):")
    for node_id, node in NODES.items():
        print(f"{node_id} -> {node['name']} ({node['coord']})")
    print()

    src = int(input("Enter source node number: ").strip())
    dest = int(input("Enter destination node number: ").strip())
    if src not in NODES or dest not in NODES:
        raise ValueError("Source/Destination must be between 0 and 5.")

    origin = NODES[src]["coord"]
    destination = NODES[dest]["coord"]
    print(f"Using source coordinates: {origin}")
    print(f"Using destination coordinates: {destination}")
    return src, dest, origin, destination


def build_graph_file(api_key):
    edges = []
    print("\nBuilding graph edges from LocationIQ...")

    for u, v in EDGE_TEMPLATE:
        origin = NODES[u]["coord"]
        destination = NODES[v]["coord"]
        try:
            route = fetch_route(api_key, origin, destination)
            _, distance, _ = route_metrics(route)
            distance_km = distance / 1000.0
            if distance_km <= 0:
                distance_km = FALLBACK_EDGE_KM[(u, v)]
            print(f"{NODES[u]['name']} -> {NODES[v]['name']}: {distance_km:.2f} km")
        except Exception:
            distance_km = FALLBACK_EDGE_KM[(u, v)]
            print(f"{NODES[u]['name']} -> {NODES[v]['name']}: fallback {distance_km:.2f} km")

        edges.append((u, v, distance_km))

    with open(GRAPH_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"{len(NODES)} {len(edges)}\n")
        for u, v, d in edges:
            f.write(f"{u} {v} {d:.4f}\n")


def run_cpp(src, dest, congestion):
    cmd = [
        "app.exe",
        str(src),
        str(dest),
        f"{congestion:.2f}",
        GRAPH_FILE_PATH,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def main():
    api_key = os.getenv("LOCATIONIQ_API_KEY", "").strip()
    if not api_key:
        print("WARNING: LOCATIONIQ_API_KEY not set. Using offline fallback data.")

    src, dest, origin, destination = get_user_input()
    build_graph_file(api_key)

    try:
        route = fetch_route(api_key, origin, destination)
        duration, distance, congestion = route_metrics(route)
    except Exception as e:
        print(f"LocationIQ API failed: {e}")
        print("Using fallback congestion = 2.0")
        duration, distance, congestion = 0.0, 0.0, 2.0

    print("\nLocationIQ API Data:")
    print(f"Duration: {duration}")
    print(f"Distance: {distance}")
    print(f"Congestion (computed): {congestion}")

    print("\nC++ Pathfinding Output:")
    print(run_cpp(src, dest, congestion))


if __name__ == "__main__":
    main()
