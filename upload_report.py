import requests
import json

url = "http://8.163.49.28:8888/api/create_doc/"
params = {"token": "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"}

with open("/root/.openclaw/workspace/daily_report_20260522.html", "r", encoding="utf-8") as f:
    doc_content = f.read()

data = {
    "pid": 1,
    "title": "基金日报 2026-05-22",
    "doc": doc_content,
    "editor_mode": 1
}

print(f"Payload size: {len(doc_content)} bytes")

try:
    resp = requests.post(url, params=params, json=data, timeout=60)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:2000]}")
    if resp.status_code == 200:
        result = resp.json()
        if result.get("status") or result.get("code") == 0 or "doc_id" in str(result):
            doc_id = result.get("doc_id", "N/A")
            print(f"\n✅ 上传成功！文档ID: {doc_id}")
        else:
            print(f"\n⚠️ 响应: {result}")
except Exception as e:
    print(f"Error: {e}")
