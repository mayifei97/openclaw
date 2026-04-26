#!/usr/bin/env python3
import requests
import json

# MrDoc API 配置
BASE_URL = "http://8.163.49.28:8888"
TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"

# 要删除的文档
DOC_ID = 23
PID = 1  # 基金投资文集

# 尝试删除文档的 API 路径
urls_to_try = [
    f"{BASE_URL}/api/delete_doc/",
    f"{BASE_URL}/manage/api/delete_doc/",
    f"{BASE_URL}/api/doc/delete/",
]

data = {
    "doc_id": DOC_ID,
    "pid": PID
}

headers = {
    "Content-Type": "application/json"
}

print(f"尝试删除文档：doc-{DOC_ID} (文集：project-{PID})")
print("=" * 50)

for url in urls_to_try:
    print(f"\n尝试 URL: {url}")
    try:
        # 尝试带 token 参数的请求
        response = requests.post(
            url, 
            params={"token": TOKEN},
            json=data, 
            headers=headers,
            timeout=30
        )
        print(f"状态码：{response.status_code}")
        print(f"响应内容：{response.text[:500]}")
        
        result = response.json()
        if result.get("status") == True:
            print("\n✅ 文档删除成功！")
            print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
            break
        elif "success" in str(result).lower() or "deleted" in str(result).lower():
            print("\n✅ 文档删除成功！")
            print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
            break
        else:
            print(f"❌ 失败：{result}")
            
    except Exception as e:
        print(f"请求异常：{e}")
        continue
else:
    print("\n❌ 所有 URL 尝试失败")
    print("建议：登录觅思文档后台手动删除文档")
