from flask import Flask, render_template, request, jsonify
import os
import subprocess
import requests

app = Flask(__name__)

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
import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

EDGE_TEMPLATE = []
FALLBACK_EDGE_KM = {}
for i in range(len(NODES)):
    for j in range(i + 1, len(NODES)):
        EDGE_TEMPLATE.append((i, j))
        lat1, lon1 = map(float, NODES[i]["coord"].split(","))
        lat2, lon2 = map(float, NODES[j]["coord"].split(","))
        dist = haversine_km(lat1, lon1, lat2, lon2)
        FALLBACK_EDGE_KM[(i, j)] = max(dist * 1.3, 1.0) # approximate road distance

graph_built = False

def to_lon_lat(lat_lng):
    lat, lng = [x.strip() for x in lat_lng.split(",")]
    return f"{lng},{lat}"

def fetch_route(api_key, coords_list):
    lon_lats = [to_lon_lat(c) for c in coords_list]
    coords_str = ";".join(lon_lats)
    url = f"https://us1.locationiq.com/v1/directions/driving/{coords_str}"
    params = {"key": api_key, "overview": "full", "steps": "false", "alternatives": "false", "geometries": "geojson"}
    response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if data.get("routes"): return data["routes"][0]
    if data.get("results"): return data["results"][0]
    raise ValueError("No route found in API response.")

import time

def build_graph_file(api_key):
    edges = []
    for u, v in EDGE_TEMPLATE:
        origin = NODES[u]["coord"]
        destination = NODES[v]["coord"]
        try:
            if api_key:
                route = fetch_route(api_key, [origin, destination])
                distance_km = float(route.get("distance", 0.0)) / 1000.0
                if distance_km <= 0: distance_km = FALLBACK_EDGE_KM[(u, v)]
                time.sleep(0.5) # Prevent rate limiting
            else:
                distance_km = FALLBACK_EDGE_KM[(u, v)]
        except Exception:
            distance_km = FALLBACK_EDGE_KM[(u, v)]
            if api_key: time.sleep(0.5)
        edges.append((u, v, distance_km))
    
    with open(GRAPH_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"{len(NODES)} {len(edges)}\n")
        for u, v, d in edges:
            f.write(f"{u} {v} {d:.4f}\n")

def parse_cpp_output(output):
    # Output looks like:
    # Locations: ...
    # Source: ... Destination: ...
    # Congestion used: ... Graph data: ...
    # [Dijkstra] Cost: ... Nodes explored: ... Path: ...
    # [A*] Cost: ... Nodes explored: ... Path: ...
    
    results = {}
    algo = None
    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("[Dijkstra]"):
            algo = "Dijkstra"
            results[algo] = {}
        elif line.startswith("[A*]"):
            algo = "A*"
            results[algo] = {}
        elif line.startswith("Cost:") and algo:
            results[algo]["cost"] = line.replace("Cost:", "").strip()
        elif line.startswith("Nodes explored:") and algo:
            results[algo]["nodes"] = line.replace("Nodes explored:", "").strip()
        elif line.startswith("Path:") and algo:
            results[algo]["path"] = line.replace("Path:", "").strip()
    return results

@app.route("/")
def index():
    return render_template("index.html", nodes=NODES)

@app.route("/api/route", methods=["POST"])
def get_route():
    data = request.json
    src = int(data.get("src", 0))
    dest = int(data.get("dest", 1))
    api_key = os.getenv("LOCATIONIQ_API_KEY", "").strip()
    
    origin = NODES[src]["coord"]
    destination = NODES[dest]["coord"]

    global graph_built
    
    # 1. Build graph file ONCE per server run to avoid slow requests
    if not graph_built:
        build_graph_file(api_key)
        graph_built = True
    
    # We will get distance, time and geometry from the real API later based on the path
    duration, distance = 0.0, 0.0
    congestion = 2.0
    
    # Estimate congestion directly from origin to destination as a proxy
    if api_key:
        try:
            route = fetch_route(api_key, [origin, destination])
            traffic = route.get("traffic")
            if traffic is not None:
                try:
                    congestion = float(traffic)
                except (TypeError, ValueError):
                    pass
            else:
                dist = float(route.get("distance", 0.0))
                dur = float(route.get("duration", 0.0))
                speed = (dist / dur) if dur > 0 else 0.0
                if speed <= 4: congestion = 5.0
                elif speed <= 7: congestion = 4.0
                elif speed <= 10: congestion = 3.0
                elif speed <= 14: congestion = 2.0
                else: congestion = 1.0
        except Exception as e:
            pass
    
    # Call C++ executable
    cmd = ["app.exe", str(src), str(dest), f"{congestion:.2f}", GRAPH_FILE_PATH]
    try:
        cpp_output = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
        comparisons = parse_cpp_output(cpp_output)
    except Exception as e:
        return jsonify({"error": str(e), "cpp_output": getattr(e, 'output', '')}), 500

    path_str = comparisons.get("Dijkstra", {}).get("path", "")
    if not path_str or path_str == "-":
        path_str = comparisons.get("A*", {}).get("path", "")

    route_geometry = None

    if path_str and path_str != "-":
        names_to_id = {n["name"]: k for k, n in NODES.items()}
        nodes_in_path = []
        path_coords = []
        for name in path_str.split("->"):
            name = name.strip()
            if name in names_to_id:
                nid = names_to_id[name]
                nodes_in_path.append(nid)
                path_coords.append(NODES[nid]["coord"])
        
        # Now fetch the exact path geometry along all points
        if api_key and len(path_coords) >= 2:
            try:
                full_route = fetch_route(api_key, path_coords)
                distance = float(full_route.get("distance", 0.0))
                duration = float(full_route.get("duration", 0.0))
                route_geometry = full_route.get("geometry")
            except Exception as e:
                pass

        if distance == 0.0:
            total_dist_km = 0.0
            for i in range(len(nodes_in_path) - 1):
                u, v = nodes_in_path[i], nodes_in_path[i+1]
                edge = (u, v) if (u, v) in FALLBACK_EDGE_KM else (v, u)
                total_dist_km += FALLBACK_EDGE_KM.get(edge, 5.0)
            
            distance = total_dist_km * 1000.0  # Convert to meters
            duration = (total_dist_km / 30.0) * 3600.0  # Assume 30 km/h speed, convert to seconds

    return jsonify({
        "duration": duration,
        "distance": distance,
        "comparisons": comparisons,
        "cpp_output": cpp_output,
        "nodes": NODES,
        "route_geometry": route_geometry
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
