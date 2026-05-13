#!/usr/bin/env python3
"""Generate real maps with Gaode (AutoNavi) map tiles as base layer - fixed coordinate alignment."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.patches as mpatches
import numpy as np
import os
import urllib.request
from PIL import Image
import io
import math

# Load Chinese font
ZH_FONT = FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')

# Gaode tile server
TILE_URL = 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'

def lonlat_to_tile(lon, lat, zoom):
    """Convert lat/lon to tile coordinates."""
    n = 2 ** zoom
    x = int((lon + 180) / 360 * n)
    y = int((1 - np.log(np.tan(np.radians(lat)) + 1/np.cos(np.radians(lat))) / np.pi) / 2 * n)
    return x, y

def download_tile(z, x, y):
    """Download a single tile from Gaode."""
    url = TILE_URL.format(x=x, y=y, z=z)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return Image.open(io.BytesIO(r.read()))
    except Exception as e:
        print(f"  Failed tile z={z}, x={x}, y={y}: {e}")
        return None

def get_map_image(center_lat, center_lon, zoom, width_tiles=8, height_tiles=6):
    """Download map tiles around center point and stitch together."""
    cx, cy = lonlat_to_tile(center_lon, center_lat, zoom)
    
    start_x = cx - width_tiles // 2
    start_y = cy - height_tiles // 2
    
    print(f"  Center: ({center_lon}, {center_lat}) -> tile ({cx}, {cy})")
    print(f"  Range: x[{start_x}:{start_x+width_tiles}], y[{start_y}:{start_y+height_tiles}]")
    
    tiles = []
    for row in range(height_tiles):
        tile_row = []
        for col in range(width_tiles):
            tx = start_x + col
            ty = start_y + row
            tile = download_tile(zoom, tx, ty)
            if tile:
                # Convert palette images to RGB
                if tile.mode == 'P':
                    tile = tile.convert('RGB')
                tile_row.append(tile)
            else:
                blank = Image.new('RGB', (256, 256), '#e8e8e8')
                tile_row.append(blank)
        tiles.append(tile_row)
    
    if not tiles or not tiles[0]:
        return None, start_x, start_y
    
    tile_w, tile_h = tiles[0][0].size
    full_w = len(tiles[0]) * tile_w
    full_h = len(tiles) * tile_h
    
    map_img = Image.new('RGB', (full_w, full_h))
    for row_idx, tile_row in enumerate(tiles):
        for col_idx, tile in enumerate(tile_row):
            if tile:
                map_img.paste(tile, (col_idx * tile_w, row_idx * tile_h))
    
    return map_img, start_x, start_y

def lonlat_to_pixel(lon, lat, zoom, start_x, start_y, map_width_px, map_height_px):
    """Convert lat/lon to pixel coordinates on the map image."""
    n = 2 ** zoom
    
    # Calculate normalized tile position
    x_norm = (lon + 180) / 360 * n
    y_norm = (1 - np.log(np.tan(np.radians(lat)) + 1/np.cos(np.radians(lat))) / np.pi) / 2 * n
    
    # Convert to pixel coordinates (tile origin is top-left)
    px = (x_norm - start_x) * 256
    py = (y_norm - start_y) * 256
    
    return px, py

# Route definitions
routes = {
    "Route A - 启德核心区闭环 (~4.5km)": {
        "color": "#e74c3c",
        "coords": [(22.3330, 114.1960), (22.3325, 114.2000), (22.3318, 114.2040),
                   (22.3290, 114.2070), (22.3260, 114.2090), (22.3250, 114.2080),
                   (22.3240, 114.2065), (22.3235, 114.2045), (22.3260, 114.2020),
                   (22.3300, 114.1990), (22.3330, 114.1960)],
        "roads": ["协调道", "承启道", "沐安街", "沐元街", "启成街"],
    },
    "Route B - 跨区综合路线 (~7km)": {
        "color": "#2ecc71",
        "coords": [(22.3330, 114.1960), (22.3325, 114.2000), (22.3318, 114.2040),
                   (22.3260, 114.2090), (22.3240, 114.2120), (22.3220, 114.2150),
                   (22.3190, 114.2180), (22.3180, 114.2160), (22.3170, 114.2140),
                   (22.3160, 114.2120), (22.3140, 114.2100), (22.3120, 114.2080),
                   (22.3180, 114.2160), (22.3200, 114.2130), (22.3220, 114.2100),
                   (22.3240, 114.2090), (22.3330, 114.1960)],
        "roads": ["协调道", "承丰道", "观塘道", "宏光道", "宏照道", "启祥道", "常悦道"],
    },
    "Route C - 启德邮轮码头特色路线 (~5.5km)": {
        "color": "#3498db",
        "coords": [(22.3330, 114.1960), (22.3325, 114.2000), (22.3318, 114.2040),
                   (22.3260, 114.2090), (22.3240, 114.2120), (22.3220, 114.2150),
                   (22.3210, 114.2180), (22.3200, 114.2200), (22.3260, 114.2090),
                   (22.3250, 114.2080), (22.3240, 114.2065), (22.3330, 114.1960)],
        "roads": ["协调道", "承启道", "承丰道", "邮轮码头路", "沐安街"],
    },
}

shatin_routes = {
    "Route D - 科学园环线 (~3.5km)": {
        "color": "#e67e22",
        "coords": [(22.4260, 114.2100), (22.4270, 114.2120), (22.4280, 114.2140),
                   (22.4290, 114.2180), (22.4280, 114.2160), (22.4270, 114.2140),
                   (22.4260, 114.2100)],
        "roads": ["科学园路", "科技大道西", "创新路", "瑞祥街"],
    },
    "Route E - 校园-科学园联动路线 (~6km)": {
        "color": "#9b59b6",
        "coords": [(22.4180, 114.2070), (22.4190, 114.2085), (22.4200, 114.2100),
                   (22.4230, 114.2120), (22.4260, 114.2100), (22.4280, 114.2140),
                   (22.4290, 114.2180), (22.4310, 114.2180), (22.4330, 114.2220),
                   (22.4340, 114.2250), (22.4180, 114.2070)],
        "roads": ["大学路", "吐露港公路", "科学园路", "科技大道西", "马鞍山绕道"],
    },
    "Route F - 吐露港走廊快速路线 (~8km)": {
        "color": "#1abc9c",
        "coords": [(22.4260, 114.2100), (22.4270, 114.2120), (22.4280, 114.2140),
                   (22.4230, 114.2120), (22.4310, 114.2180), (22.4320, 114.2200),
                   (22.4330, 114.2220), (22.4310, 114.2180), (22.4280, 114.2140)],
        "roads": ["科学园路", "吐露港公路(南行)", "大老山公路", "马鞍山绕道"],
    },
}

LANDMARKS_KE = {
    "启德发展区": (22.328, 114.203),
    "邮轮码头": (22.320, 114.220),
    "九龙湾": (22.318, 114.215),
    "启德跑道公园": (22.323, 114.212),
}

LANDMARKS_ST = {
    "香港科学园": (22.428, 114.214),
    "香港中文大学": (22.419, 114.208),
    "马鞍山": (22.433, 114.223),
}

def draw_on_map(map_img, start_x, start_y, zoom, routes, landmarks, title, filename, figsize=(18, 14)):
    """Draw routes on top of map image with correct coordinate alignment."""
    if map_img is None:
        print(f"  No map for {filename}")
        return
    
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Show map image (origin='upper' for correct orientation)
    ax.imshow(map_img, origin='upper', extent=[0, map_img.width, map_img.height, 0])
    
    def to_px(lon, lat):
        px, py = lonlat_to_pixel(lon, lat, zoom, start_x, start_y, map_img.width, map_img.height)
        return px, py
    
    # Draw routes
    for name, info in routes.items():
        coords = info["coords"]
        pixels = [to_px(lon, lat) for lat, lon in coords]
        px = [p[0] for p in pixels]
        py = [p[1] for p in pixels]
        
        ax.plot(px, py, color=info["color"], linewidth=5, alpha=0.85,
                marker='o', markersize=8, markerfacecolor='white',
                markeredgecolor=info["color"], markeredgewidth=2,
                label=name)
        
        # Road labels
        roads = info["roads"]
        for i, road in enumerate(roads):
            if i < len(coords):
                lat, lon = coords[i]
                ppx, ppy = to_px(lon, lat)
                ax.text(ppx, ppy - 12, road, fontsize=9, color=info["color"],
                        fontweight='bold', ha='center', va='bottom',
                        fontproperties=ZH_FONT,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                 edgecolor=info["color"], alpha=0.85))
        
        # Start/end markers
        start = coords[0]
        end = coords[-1]
        spx, spy = to_px(start[1], start[0])
        epx, epy = to_px(end[1], end[0])
        
        ax.text(spx, spy - 18, '▶ 起点', fontsize=11, color='green',
                fontweight='bold', ha='center', va='bottom', fontproperties=ZH_FONT,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#d5f5e3', edgecolor='green', alpha=0.9))
        ax.text(epx, epy + 18, ' 终点', fontsize=11, color='red',
                fontweight='bold', ha='center', va='top', fontproperties=ZH_FONT,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', edgecolor='red', alpha=0.9))
    
    # Landmarks
    for name, (lat, lon) in landmarks.items():
        lpx, lpy = to_px(lon, lat)
        ax.text(lpx, lpy, ' ' + name, fontsize=10, color='#333',
                ha='center', va='center', fontproperties=ZH_FONT,
                bbox=dict(boxstyle='circle,pad=0.4', facecolor='#fff3cd',
                         edgecolor='#f0ad4e', alpha=0.9))
    
    # Legend
    legend_elements = [mpatches.Patch(color=info["color"], label=name)
                       for name, info in routes.items()]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11,
              framealpha=0.95, fancybox=True, prop=ZH_FONT)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=15, fontproperties=ZH_FONT)
    ax.set_xlim(0, map_img.width)
    ax.set_ylim(map_img.height, 0)  # Flip y-axis to match image coordinates
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {filename}")

# Generate Kowloon East map
print("=== Generating Kowloon East map ===")
ke_img, ke_sx, ke_sy = get_map_image(22.328, 114.208, 14, 8, 6)
if ke_img:
    draw_on_map(ke_img, ke_sx, ke_sy, 14, routes, LANDMARKS_KE,
                "九龙东 (Kowloon East) - 自动驾驶 Demo 路线",
                "/root/.openclaw/workspace/tools/routes_kowloon_east.png")

# Generate Shatin map
print("\n=== Generating Shatin map ===")
st_img, st_sx, st_sy = get_map_image(22.428, 114.214, 13, 8, 6)
if st_img:
    draw_on_map(st_img, st_sx, st_sy, 13, shatin_routes, LANDMARKS_ST,
                "沙田 (Shatin) - 自动驾驶 Demo 路线",
                "/root/.openclaw/workspace/tools/routes_shatin.png")

# Generate combined overview
print("\n=== Generating combined overview ===")
all_routes = {**routes, **shatin_routes}
all_landmarks = {**LANDMARKS_KE, **LANDMARKS_ST}
# Use wider zoom for overview
overview_img, ov_sx, ov_sy = get_map_image(22.38, 114.21, 11, 10, 8)
if overview_img:
    draw_on_map(overview_img, ov_sx, ov_sy, 11, all_routes, all_landmarks,
                "全部自动驾驶 Demo 路线总览 (九龙东 + 沙田)",
                "/root/.openclaw/workspace/tools/routes_all_combined.png", figsize=(22, 16))

print("\n Done!")
