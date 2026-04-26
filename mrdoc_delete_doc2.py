#!/usr/bin/env python3
import requests
import json

# MrDoc API 配置
BASE_URL = "http://8.163.49.28:8888"
TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"

# 要删除的文档
DOC_ID = 23

# 尝试不同的请求方式
print(f"尝试删除文档：doc-{DOC_ID}")
print("=" * 50)

# 方式 1: GET 请求带参数
url1 = f"{BASE_URL}/api/delete_doc/"
params1 = {"token": TOKEN, "doc_id": DOC_ID}

print(f"\n方式 1 - GET 请求：{url1}")
try:
    response = requests.get(url1, params=params1, timeout=30)
    print(f"状态码：{response.status_code}")
    result = response.json()
    print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    if result.get("status") == True:
        print("✅ 删除成功！")
    else:
        print(f"❌ 失败：{result.get('data', '未知错误')}")
except Exception as e:
    print(f"请求异常：{e}")

# 方式 2: POST 请求，doc_id 作为 URL 参数
url2 = f"{BASE_URL}/api/delete_doc/{DOC_ID}/"
params2 = {"token": TOKEN}

print(f"\n方式 2 - POST 请求：{url2}")
try:
    response = requests.post(url2, params=params2, timeout=30)
    print(f"状态码：{response.status_code}")
    result = response.json()
    print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    if result.get("status") == True:
        print("✅ 删除成功！")
    else:
        print(f"❌ 失败：{result.get('data', '未知错误')}")
except Exception as e:
    print(f"请求异常：{e}")

# 方式 3: 使用表单数据而不是 JSON
url3 = f"{BASE_URL}/api/delete_doc/"
params3 = {"token": TOKEN}
data3 = {"doc_id": DOC_ID}

print(f"\n方式 3 - POST 表单数据：{url3}")
try:
    response = requests.post(url3, params=params3, data=data3, timeout=30)
    print(f"状态码：{response.status_code}")
    result = response.json()
    print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    if result.get("status") == True:
        print("✅ 删除成功！")
    else:
        print(f"❌ 失败：{result.get('data', '未知错误')}")
except Exception as e:
    print(f"请求异常：{e}")
