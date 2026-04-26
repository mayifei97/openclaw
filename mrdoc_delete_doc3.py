#!/usr/bin/env python3
import requests
import json

# MrDoc API 配置
BASE_URL = "http://8.163.49.28:8888"
TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"

# 要删除的文档
DOC_ID = 23
PID = 1

# 尝试更多可能的 API 路径
urls_to_try = [
    # v9.3 可能的路径
    {"url": f"{BASE_URL}/api/doc/delete/", "method": "POST", "json": {"doc_id": DOC_ID}},
    {"url": f"{BASE_URL}/api/document/delete/", "method": "POST", "json": {"doc_id": DOC_ID}},
    {"url": f"{BASE_URL}/manage/doc/delete/", "method": "POST", "json": {"doc_id": DOC_ID}},
    # 带 pid 参数
    {"url": f"{BASE_URL}/api/delete_doc/", "method": "POST", "json": {"doc_id": DOC_ID, "pid": PID}},
    # GET 请求带 doc_id
    {"url": f"{BASE_URL}/api/delete_doc/?token={TOKEN}&doc_id={DOC_ID}", "method": "GET", "json": None},
]

headers = {"Content-Type": "application/json"}

print(f"尝试删除文档：doc-{DOC_ID} (文集：project-{PID})")
print("=" * 60)

for i, config in enumerate(urls_to_try, 1):
    url = config["url"]
    method = config["method"]
    data = config["json"]
    
    print(f"\n[{i}/{len(urls_to_try)}] {method} {url}")
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        else:
            if data:
                response = requests.post(url, params={"token": TOKEN}, json=data, headers=headers, timeout=30)
            else:
                response = requests.post(url, params={"token": TOKEN}, timeout=30)
        
        print(f"状态码：{response.status_code}")
        
        # 尝试解析 JSON
        try:
            result = response.json()
            print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("status") == True or result.get("success") == True:
                print("\n✅ 删除成功！")
                break
            elif "success" in str(result).lower() or "deleted" in str(result).lower() or "删除成功" in str(result).lower():
                print("\n✅ 删除成功！")
                break
            else:
                print(f"❌ 失败")
        except:
            print(f"响应内容：{response.text[:300]}")
            print("❌ 无法解析 JSON")
            
    except Exception as e:
        print(f"请求异常：{e}")
        continue
else:
    print("\n" + "=" * 60)
    print("❌ 所有 API 路径尝试失败")
    print("\n建议操作：")
    print("1. 登录觅思文档后台：http://8.163.49.28:8888")
    print("2. 进入'基金投资'文集 (project-1)")
    print("3. 找到文档'雯雯基金调仓计划 - 2026 年 3 月深度分析报告'(doc-23)")
    print("4. 手动删除该文档")
