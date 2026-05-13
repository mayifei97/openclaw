#!/usr/bin/env python3
"""Generate real maps for HK autonomous driving demo routes using known coordinates."""

import folium
from folium import PolyLine, Marker, Icon

# ── Known coordinates for key roads ──

# KAI TAK (启德) area
KEI_TAK = {
    "協調道": [(22.3330, 114.1960), (22.3325, 114.2000), (22.3318, 114.2040)],
    "承啟道": [(22.3318, 114.2040), (22.3290, 114.2070), (22.3260, 114.2090)],
    "沐安街": [(22.3260, 114.2090), (22.3250, 114.2080), (22.3240, 114.2065)],
    "沐元街": [(22.3240, 114.2065), (22.3235, 114.2045)],
    "啟成街": [(22.3235, 114.2045), (22.3260, 114.2020), (22.3300, 114.1990)],
    "承豐道": [(22.3260, 114.2090), (22.3240, 114.2120), (22.3220, 114.2150)],
    "觀塘道": [(22.3190, 114.2180), (22.3160, 114.2200), (22.3130, 114.2230)],
    "宏光道": [(22.3180, 114.2160), (22.3170, 114.2140), (22.3160, 114.2120)],
    "宏照道": [(22.3160, 114.2120), (22.3140, 114.2100), (22.3120, 114.2080)],
    "啟祥道": [(22.3180, 114.2160), (22.3200, 114.2130), (22.3220, 114.2100)],
    "常悅道": [(22.3200, 114.2130), (22.3220, 114.2110), (22.3240, 114.2090)],
    "郵輪碼頭路": [(22.3220, 114.2150), (22.3210, 114.2180), (22.3200, 114.2200)],
}

# SHATIN (沙田/科学园) area
SHATIN = {
    "科學園路": [(22.4260, 114.2100), (22.4270, 114.2120), (22.4280, 114.2140)],
    "科技大道西": [(22.4270, 114.2120), (22.4280, 114.2150), (22.4290, 114.2180)],
    "創新路": [(22.4280, 114.2140), (22.4295, 114.2160), (22.4310, 114.2180)],
    "瑞祥街": [(22.4290, 114.2180), (22.4280, 114.2160), (22.4270, 114.2140)],
    "大學路": [(22.4180, 114.2070), (22.4190, 114.2085), (22.4200, 114.2100)],
    "吐露港公路": [(22.4200, 114.2100), (22.4230, 114.2120), (22.4260, 114.2100)],
    "馬鞍山繞道": [(22.4310, 114.2180), (22.4330, 114.2220), (22.4340, 114.2250)],
    "大老山公路": [(22.4310, 114.2180), (22.4320, 114.2200), (22.4330, 114.2220)],
}

# ── Route definitions ──

routes = {
    "Route A - 启德核心区闭环 (~4.5km)": {
        "color": "#e74c3c", "map": "ke", "center": [22.328, 114.203], "zoom": 14,
        "roads": ["協調道", "承啟道", "沐安街", "沐元街", "啟成街"],
        "desc": "启德核心区闭环",
    },
    "Route B - 跨区综合路线 (~7km)": {
        "color": "#2ecc71", "map": "ke", "center": [22.320, 114.215], "zoom": 13,
        "roads": ["協調道", "承豐道", "觀塘道", "宏光道", "宏照道", "啟祥道", "常悅道"],
        "desc": "跨区综合路线",
    },
    "Route C - 启德邮轮码头特色路线 (~5.5km)": {
        "color": "#3498db", "map": "ke", "center": [22.324, 114.210], "zoom": 13,
        "roads": ["協調道", "承啟道", "承豐道", "郵輪碼頭路", "沐安街"],
        "desc": "启德邮轮码头特色路线",
    },
    "Route D - 科学园环线 (~3.5km)": {
        "color": "#e67e22", "map": "st", "center": [22.428, 114.214], "zoom": 14,
        "roads": ["科學園路", "科技大道西", "創新路", "瑞祥街"],
        "desc": "科学园环线",
    },
    "Route E - 校园-科学园联动路线 (~6km)": {
        "color": "#9b59b6", "map": "st", "center": [22.425, 114.214], "zoom": 12,
        "roads": ["大學路", "吐露港公路", "科學園路", "科技大道西", "馬鞍山繞道"],
        "desc": "校园-科学园联动路线",
    },
    "Route F - 吐露港走廊快速路线 (~8km)": {
        "color": "#1abc9c", "map": "st", "center": [22.428, 114.218], "zoom": 12,
        "roads": ["科學園路", "吐露港公路", "大老山公路", "馬鞍山繞道"],
        "desc": "吐露港走廊快速路线",
    },
}


def build_route_coords(road_names, coord_dict):
    """Build continuous coordinate list from road segments."""
    points = []
    for road in road_names:
        if road in coord_dict:
            points.extend(coord_dict[road])
    return points


# ── Generate individual Kowloon East map ──
ke_map = folium.Map(location=[22.325, 114.208], zoom_start=13, tiles="OpenStreetMap")

for name, info in routes.items():
    if info["map"] != "ke":
        continue
    coords = build_route_coords(info["roads"], KEI_TAK)
    if len(coords) >= 2:
        PolyLine(coords, color=info["color"], weight=5, opacity=0.85,
                 popup=f"{info['desc']}").add_to(ke_map)
        Marker(coords[0], icon=Icon(color="green", icon="play", prefix="fa"),
               popup=f"起点: {info['desc']}").add_to(ke_map)
        Marker(coords[-1], icon=Icon(color="red", icon="stop", prefix="fa"),
               popup=f"终点: {info['desc']}").add_to(ke_map)

ke_map.save("/root/.openclaw/workspace/tools/route_kowloon_east.html")
print("✅ Kowloon East map saved")

# ── Generate individual Shatin map ──
st_map = folium.Map(location=[22.428, 114.214], zoom_start=13, tiles="OpenStreetMap")

for name, info in routes.items():
    if info["map"] != "st":
        continue
    coord_dict = SHATIN
    coords = build_route_coords(info["roads"], coord_dict)
    if len(coords) >= 2:
        PolyLine(coords, color=info["color"], weight=5, opacity=0.85,
                 popup=f"{info['desc']}").add_to(st_map)
        Marker(coords[0], icon=Icon(color="green", icon="play", prefix="fa"),
               popup=f"起点: {info['desc']}").add_to(st_map)
        Marker(coords[-1], icon=Icon(color="red", icon="stop", prefix="fa"),
               popup=f"终点: {info['desc']}").add_to(st_map)

st_map.save("/root/.openclaw/workspace/tools/route_shatin.html")
print("✅ Shatin map saved")

# ── Generate combined overview ──
combined = folium.Map(location=[22.38, 114.21], zoom_start=11, tiles="OpenStreetMap")

for name, info in routes.items():
    coord_dict = KEI_TAK if info["map"] == "ke" else SHATIN
    coords = build_route_coords(info["roads"], coord_dict)
    if len(coords) >= 2:
        PolyLine(coords, color=info["color"], weight=4, opacity=0.8,
                 popup=f"{name}\n{info['desc']}").add_to(combined)

combined.save("/root/.openclaw/workspace/tools/route_all_combined.html")
print("✅ Combined overview saved")

print("\n🎉 All maps generated!")
