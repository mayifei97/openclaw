#!/usr/bin/env python3
"""Screenshot folium HTML maps to PNG images using Playwright."""

from playwright.sync_api import sync_playwright
import os

maps = [
    ("route_kowloon_east.html", "routes_kowloon_east.png", "九龙东 Demo 路线"),
    ("route_shatin.html", "routes_shatin.png", "沙田 Demo 路线"),
    ("route_all_combined.html", "routes_all_combined.png", "全部路线总览"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    for html_file, png_file, title in maps:
        html_path = f"file:///root/.openclaw/workspace/tools/{html_file}"
        page = browser.new_page()
        page.goto(html_path, wait_until="networkidle", timeout=30000)
        # Set viewport to full page
        page.set_viewport_size({"width": 1600, "height": 1200})
        page.wait_for_timeout(2000)  # Wait for tiles to load
        page.screenshot(path=f"/root/.openclaw/workspace/tools/{png_file}", full_page=True)
        print(f"✅ {title} → {png_file}")
        page.close()
    browser.close()

print("\n🎉 All screenshots saved!")
