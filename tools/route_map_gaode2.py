#!/usr/bin/env python3
"""Generate route maps using folium with Gaode tiles."""

import folium
from folium import plugins
import os

# Gaode tile server
GAODE_URL = 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'

# Simple route definitions
routes = {
    "Route A - 启德核心区闭环 (~4.5km)": {
        "color": "#e74c3c",
        "coords": [
            [22.3330, 114.1960], [22.3325, 114.2000], [22.3318, 114.2040],
            [22.3290, 114.2070], [22.3260, 114.2090], [22.3250, 114.2080],
            [22.3240, 114.2065], [22.3235, 114.2045], [22.3260, 114.2020],
            [22.3300, 114.1990], [22.3330, 114.1960]
        ],
    },
    "Route B - 跨区综合路线 (~7km)": {
        "color": "#2ecc71",
        "coords": [
            [22.3330, 114.1960], [22.3325, 114.2000], [22.3318, 114.2040],
            [22.3260, 114.2090], [22.3240, 114.2120], [22.3220, 114.2150],
            [22.3190, 114.2180], [22.3180, 114.2160], [22.3160, 114.2140],
            [22.3140, 114.2120], [22.3120, 114.2100], [22.3140, 114.2080],
            [22.3160, 114.2060], [22.3180, 114.2040], [22.3200, 114.2020],
            [22.3220, 114.2000], [22.3240, 114.1980], [22.3260, 114.1960],
            [22.3280, 114.1940], [22.3300, 114.1920], [22.3320, 114.1900],
            [22.3330, 114.1960]
        ],
    },
    "Route C - 启德邮轮码头特色路线 (~5.5km)": {
        "color": "#3498db",
        "coords": [
            [22.3330, 114.1960], [22.3325, 114.2000], [22.3318, 114.2040],
            [22.3290, 114.2070], [22.3260, 114.2090], [22.3240, 114.2120],
            [22.3220, 114.2150], [22.3210, 114.2180], [22.3200, 114.2200],
            [22.3220, 114.2180], [22.3240, 114.2160], [22.3260, 114.2140],
            [22.3280, 114.2120], [22.3300, 114.2100], [22.3320, 114.2080],
            [22.3330, 114.1960]
        ],
    },
}

shatin_routes = {
    "Route D - 科学园环线 (~3.5km)": {
        "color": "#e67e22",
        "coords": [
            [22.4260, 114.2100], [22.4270, 114.2120], [22.4280, 114.2140],
            [22.4290, 114.2160], [22.4295, 114.2180], [22.4290, 114.2160],
            [22.4280, 114.2140], [22.4270, 114.2120], [22.4260, 114.2100]
        ],
    },
    "Route E - 校园-科学园联动路线 (~6km)": {
        "color": "#9b59b6",
        "coords": [
            [22.4180, 114.2070], [22.4190, 114.2080], [22.4200, 114.2100],
            [22.4220, 114.2110], [22.4240, 114.2120], [22.4260, 114.2130],
            [22.4280, 114.2140], [22.4290, 114.2160], [22.4300, 114.2180],
            [22.4310, 114.2200], [22.4320, 114.2220], [22.4330, 114.2240],
            [22.4320, 114.2220], [22.4300, 114.2200], [22.4280, 114.2180],
            [22.4260, 114.2160], [22.4240, 114.2140], [22.4220, 114.2120],
            [22.4200, 114.2100], [22.4180, 114.2070]
        ],
    },
    "Route F - 吐露港走廊快速路线 (~8km)": {
        "color": "#1abc9c",
        "coords": [
            [22.4260, 114.2100], [22.4270, 114.2120], [22.4280, 114.2140],
            [22.4290, 114.2160], [22.4300, 114.2180], [22.4310, 114.2200],
            [22.4320, 114.2220], [22.4310, 114.2200], [22.4290, 114.2180],
            [22.4270, 114.2160], [22.4250, 114.2140], [22.4260, 114.2100]
        ],
    },
}

# Generate Kowloon East map
print("=== Generating Kowloon East map ===")
ke_map = folium.Map(
    location=[22.328, 114.208],
    zoom_start=14,
    tiles=GAODE_URL,
    attr='AutoNavi',
    zoom_control=True
)

for name, info in routes.items():
    folium.PolyLine(
        info["coords"],
        color=info["color"],
        weight=5,
        opacity=0.85,
        popup=name
    ).add_to(ke_map)
    
    # Start marker
    folium.Marker(
        info["coords"][0],
        popup=f"起点: {name}",
        icon=folium.Icon(color="green", icon="play", prefix="fa")
    ).add_to(ke_map)
    
    # End marker
    folium.Marker(
        info["coords"][-1],
        popup=f"终点: {name}",
        icon=folium.Icon(color="red", icon="stop", prefix="fa")
    ).add_to(ke_map)

ke_map.save("/root/.openclaw/workspace/tools/routes_kowloon_east_folium.html")
print("  Saved Kowloon East HTML")

# Generate Shatin map
print("\n=== Generating Shatin map ===")
st_map = folium.Map(
    location=[22.428, 114.214],
    zoom_start=13,
    tiles=GAODE_URL,
    attr='AutoNavi',
    zoom_control=True
)

for name, info in shatin_routes.items():
    folium.PolyLine(
        info["coords"],
        color=info["color"],
        weight=5,
        opacity=0.85,
        popup=name
    ).add_to(st_map)
    
    folium.Marker(
        info["coords"][0],
        popup=f"起点: {name}",
        icon=folium.Icon(color="green", icon="play", prefix="fa")
    ).add_to(st_map)
    
    folium.Marker(
        info["coords"][-1],
        popup=f"终点: {name}",
        icon=folium.Icon(color="red", icon="stop", prefix="fa")
    ).add_to(st_map)

st_map.save("/root/.openclaw/workspace/tools/routes_shatin_folium.html")
print("  Saved Shatin HTML")

print("\n HTML maps generated. Now trying to screenshot with Playwright...")
