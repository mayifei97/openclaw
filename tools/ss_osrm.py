#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

maps = [
    ("routes_ke_osrm.html", "routes_ke_final.png"),
    ("routes_st_osrm.html", "routes_st_final.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    for html_file, png_file in maps:
        page = browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1200})
        try:
            page.goto(f"file:///root/.openclaw/workspace/tools/{html_file}",
                      wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.screenshot(path=f"/root/.openclaw/workspace/tools/{png_file}", full_page=True)
            print(f"✅ {png_file}")
        except Exception as e:
            print(f"❌ {html_file}: {e}")
        page.close()
    browser.close()
print("Done!")
