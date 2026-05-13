#!/usr/bin/env python3
"""Generate route maps using OSRM for real road trajectories + Gaode tiles."""

import folium
import urllib.request
import json
import time

GAODE_URL = 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'

def get_osrm_route(waypoints):
    """Get road trajectory from OSRM for a list of waypoints."""
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.loads(r.read())
            if 'routes' in data and len(data['routes']) > 0:
                # OSRM returns [lon, lat], folium needs [lat, lon]
                geom = data['routes'][0]['geometry']['coordinates']
                return [[p[1], p[0]] for p in geom], data['routes'][0]['distance']
    except Exception as e:
        print(f"  OSRM error: {e}")
    return None, 0

# Route definitions - waypoints for each route
# Route A: 启德核心区闭环
route_a_waypoints = [
    [22.3330, 114.1960],  # 协调道起点
    [22.3318, 114.2040],  # 承启道
    [22.3290, 114.2070],  # 沐安街
    [22.3260, 114.2090],  # 沐元街
    [22.3240, 114.2065],  # 启成街
    [22.3260, 114.2020],  # 返回
    [22.3300, 114.1990],  # 回协调道
    [22.3330, 114.1960],  # 回到起点
]

# Route B: 跨区综合路线
route_b_waypoints = [
    [22.3330, 114.1960],  # 协调道
    [22.3260, 114.2090],  # 承丰道
    [22.3190, 114.2180],  # 观塘道
    [22.3160, 114.2140],  # 宏光道
    [22.3140, 114.2100],  # 宏照道
    [22.3180, 114.2160],  # 启祥道
    [22.3220, 114.2130],  # 常悦道
    [22.3300, 114.1990],  # 回协调道
    [22.3330, 114.1960],  # 起点
]

# Route C: 邮轮码头特色路线
route_c_waypoints = [
    [22.3330, 114.1960],  # 协调道
    [22.3260, 114.2090],  # 承丰道
    [22.3220, 114.2150],  # 邮轮码头路
    [22.3200, 114.2200],  # 码头
    [22.3260, 114.2090],  # 返回
    [22.3250, 114.2080],  # 沐安街
    [22.3330, 114.1960],  # 起点
]

# Route D: 科学园环线
route_d_waypoints = [
    [22.4260, 114.2100],  # 科学园路
    [22.4280, 114.2140],  # 科技大道西
    [22.4300, 114.2180],  # 创新路
    [22.4280, 114.2160],  # 瑞祥街
    [22.4260, 114.2100],  # 回到起点
]

# Route E: 校园 - 科学园联动
route_e_waypoints = [
    [22.4180, 114.2070],  # 大学路 (中大)
    [22.4200, 114.2100],  # 吐露港公路
    [22.4280, 114.2140],  # 科学园路
    [22.4300, 114.2180],  # 科技大道西
    [22.4330, 114.2220],  # 马鞍山绕道
    [22.4180, 114.2070],  # 回到起点
]

# Route F: 吐露港走廊快速路线
route_f_waypoints = [
    [22.4260, 114.2100],  # 科学园路
    [22.4230, 114.2120],  # 吐露港公路南行
    [22.4310, 114.2180],  # 大老山公路
    [22.4330, 114.2220],  # 马鞍山绕道
    [22.4280, 114.2140],  # 吐露港公路北行
    [22.4260, 114.2100],  # 回到起点
]

print("=== Fetching road trajectories from OSRM ===")

routes = {}
for name, waypoints in [
    ("A", route_a_waypoints),
    ("B", route_b_waypoints),
    ("C", route_c_waypoints),
    ("D", route_d_waypoints),
    ("E", route_e_waypoints),
    ("F", route_f_waypoints),
]:
    print(f"\nRoute {name}...")
    coords, dist = get_osrm_route(waypoints)
    if coords:
        routes[name] = coords
        print(f"  ✅ {len(coords)} points, {dist:.0f}m")
    else:
        print(f"  ❌ Failed")
    time.sleep(1)  # Rate limit

if not routes:
    print("\n❌ No routes fetched, exiting")
    exit(1)

print(f"\n=== Generating maps ===")

# Colors
colors = {
    "A": "#e74c3c", "B": "#2ecc71", "C": "#3498db",
    "D": "#e67e22", "E": "#9b59b6", "F": "#1abc9c"
}

# Generate Kowloon East map
print("Kowloon East map...")
ke_map = folium.Map(location=[22.328, 114.208], zoom_start=14,
                    tiles=GAODE_URL, attr='AutoNavi', zoom_control=True)

for name in ["A", "B", "C"]:
    if name in routes:
        folium.PolyLine(routes[name], color=colors[name], weight=6, opacity=0.85).add_to(ke_map)
        # Start marker
        folium.Marker(routes[name][0], icon=folium.Icon(color="green", icon="play", prefix="fa"),
                      popup=f"Route {name}").add_to(ke_map)

ke_map.save("/root/.openclaw/workspace/tools/routes_ke_osrm.html")
print("  ✅ Saved KE HTML")

# Generate Shatin map
print("Shatin map...")
st_map = folium.Map(location=[22.428, 114.214], zoom_start=13,
                    tiles=GAODE_URL, attr='AutoNavi', zoom_control=True)

for name in ["D", "E", "F"]:
    if name in routes:
        folium.PolyLine(routes[name], color=colors[name], weight=6, opacity=0.85).add_to(st_map)
        folium.Marker(routes[name][0], icon=folium.Icon(color="green", icon="play", prefix="fa"),
                      popup=f"Route {name}").add_to(st_map)

st_map.save("/root/.openclaw/workspace/tools/routes_st_osrm.html")
print("  ✅ Saved ST HTML")

print("\n🎉 Done! Now screenshotting...")
