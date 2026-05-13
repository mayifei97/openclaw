#!/usr/bin/env python3
"""Screenshot folium HTML maps to PNG images using Playwright."""

from playwright.sync_api import sync_playwright
import os
import time

maps = [
    ("routes_kowloon_east_folium.html", "routes_kowloon_east.png", "九龙东 Demo 路线"),
    ("routes_shatin_folium.html", "routes_shatin.png", "沙田 Demo 路线"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    for html_file, png_file, title in maps:
        html_path = f"file:///root/.openclaw/workspace/tools/{html_file}"
        page = browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1200})
        
        try:
            page.goto(html_path, wait_until="domcontentloaded", timeout=30000)
            # Wait for map tiles to load
            time.sleep(5)
            page.screenshot(path=f"/root/.openclaw/workspace/tools/{png_file}", full_page=True)
            print(f"✅ {title} → {png_file}")
        except Exception as e:
            print(f"❌ Failed to screenshot {title}: {e}")
        finally:
            page.close()
    
    browser.close()

print("\n Done!")
