#!/usr/bin/env python3
import requests
import json

# MrDoc API 配置
BASE_URL = "http://8.163.49.28:8888"
TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"

# 尝试创建文集（项目）
# MrDoc v9.3 API 路径尝试
urls_to_try = [
    f"{BASE_URL}/api/project/create/",
    f"{BASE_URL}/manage/api/create_project/",
    f"{BASE_URL}/api/create_project/",
]

data = {
    "name": "雯雯基金分析",
    "description": "雯雯个人基金投资组合分析与调仓报告",
    "access_level": 1  # 私有或公开，根据实际情况调整
}

headers = {
    "Content-Type": "application/json"
}

print("尝试创建文集：雯雯基金分析")
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
        if result.get("status") == True or result.get("data"):
            print("\n✅ 文集创建成功！")
            print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 提取文集 ID
            project_data = result.get("data", {})
            if isinstance(project_data, dict):
                project_id = project_data.get("id", project_data.get("project_id", project_data.get("pid")))
                print(f"\n📚 新文集 ID: {project_id}")
                print(f"访问 URL: {BASE_URL}/project-{project_id}/")
                break
        else:
            print(f"❌ 失败：{result}")
            
    except Exception as e:
        print(f"请求异常：{e}")
        continue
else:
    print("\n❌ 所有 URL 尝试失败，可能需要手动创建文集")
    print("建议：登录觅思文档后台手动创建文集，然后告诉我文集 ID")
