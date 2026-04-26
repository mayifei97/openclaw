#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MrDoc API 工具 - 用于上传/删除文档到觅思文档

使用方法:
    上传：python3 mrdoc_upload.py upload "文档标题" "HTML 文件路径"
    删除：python3 mrdoc_upload.py delete <文档 ID>

示例:
    python3 mrdoc_upload.py upload "基金日报 -2026 年 3 月 5 日" "./report.html"
    python3 mrdoc_upload.py delete 17

配置信息:
    - MrDoc URL: http://8.163.49.28:8888
    - API Token: 见下方配置
    - 文集 ID: 1 (基金投资)
"""

import sys
import json
import urllib.request
import urllib.error

# ========== 配置区 ==========
MRDOC_URL = "http://8.163.49.28:8888"
API_TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"
PROJECT_ID = 1  # 基金投资文集
EDITOR_MODE = 1  # 1=HTML 富文本，2=Markdown，3=纯文本
# ===========================

def upload_to_mrdoc(title, html_content, project_id=PROJECT_ID):
    """
    上传文档到 MrDoc
    
    Args:
        title: 文档标题
        html_content: HTML 格式的文档内容
        project_id: 文集 ID
    
    Returns:
        dict: 包含 status 和 data(文档 ID) 的字典
    """
    url = f"{MRDOC_URL}/api/create_doc/?token={API_TOKEN}"
    
    data = {
        "pid": project_id,
        "title": title,
        "doc": html_content,
        "editor_mode": EDITOR_MODE
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        return {"status": False, "error": f"HTTP Error {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"status": False, "error": f"URL Error: {e.reason}"}
    except Exception as e:
        return {"status": False, "error": f"Error: {str(e)}"}

def delete_doc(doc_id):
    """
    删除 MrDoc 文档（软删除，状态改为 3）
    
    Args:
        doc_id: 文档 ID
    
    Returns:
        dict: 包含 status 和 data 的字典
    """
    url = f"{MRDOC_URL}/api/delete_doc/?token={API_TOKEN}"
    
    data = {
        "did": doc_id  # 注意：参数名是 did，不是 doc_id
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        return {"status": False, "error": f"HTTP Error {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"status": False, "error": f"URL Error: {e.reason}"}
    except Exception as e:
        return {"status": False, "error": f"Error: {str(e)}"}

def list_docs(project_id=PROJECT_ID):
    """
    获取文集文档列表
    
    Args:
        project_id: 文集 ID
    
    Returns:
        dict: 包含 status 和 data(文档列表) 的字典
    """
    url = f"{MRDOC_URL}/api/get_docs/?token={API_TOKEN}&pid={project_id}"
    
    req = urllib.request.Request(url, method='GET')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        return {"status": False, "error": f"HTTP Error {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"status": False, "error": f"URL Error: {e.reason}"}
    except Exception as e:
        return {"status": False, "error": f"Error: {str(e)}"}

def main():
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  上传：python3 mrdoc_upload.py upload \"文档标题\" \"HTML 文件路径\"")
        print("  删除：python3 mrdoc_upload.py delete <文档 ID>")
        print("  列表：python3 mrdoc_upload.py list")
        print("\n示例：")
        print("  python3 mrdoc_upload.py upload \"基金日报 -2026 年 3 月 5 日\" \"./report.html\"")
        print("  python3 mrdoc_upload.py delete 17")
        print("  python3 mrdoc_upload.py list")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "upload":
        if len(sys.argv) < 4:
            print("错误：上传需要文档标题和文件路径")
            print("用法：python3 mrdoc_upload.py upload \"文档标题\" \"HTML 文件路径\"")
            sys.exit(1)
        
        title = sys.argv[2]
        file_path = sys.argv[3]
        
        # 读取 HTML 文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"错误：文件不存在 - {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"错误：读取文件失败 - {str(e)}")
            sys.exit(1)
        
        # 上传到 MrDoc
        print(f"正在上传文档：{title}")
        result = upload_to_mrdoc(title, html_content)
        
        if result.get('status'):
            doc_id = result.get('data')
            doc_url = f"{MRDOC_URL}/project-{PROJECT_ID}/doc-{doc_id}/"
            print(f"✅ 上传成功！")
            print(f"📄 文档 ID: {doc_id}")
            print(f"🔗 文档链接：{doc_url}")
        else:
            print(f"❌ 上传失败！")
            print(f"错误信息：{result.get('data', result.get('error', '未知错误'))}")
            sys.exit(1)
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("错误：删除需要文档 ID")
            print("用法：python3 mrdoc_upload.py delete <文档 ID>")
            sys.exit(1)
        
        doc_id = int(sys.argv[2])
        print(f"正在删除文档 {doc_id}...")
        result = delete_doc(doc_id)
        
        if result.get('status'):
            print(f"✅ 已删除文档 {doc_id}")
        else:
            print(f"❌ 删除失败！")
            print(f"错误信息：{result.get('data', result.get('error', '未知错误'))}")
            sys.exit(1)
    
    elif command == "list":
        print(f"正在获取文集 {PROJECT_ID} 的文档列表...")
        result = list_docs()
        
        if result.get('status'):
            docs = result.get('data', [])
            print(f"\n📚 文集 {PROJECT_ID} 共有 {len(docs)} 个文档：\n")
            for doc in docs:
                status_icon = "✅" if doc.get('status') == 1 else "❌"
                print(f"{status_icon} ID:{doc['id']:3d} | {doc['name']} | {doc['create_time'][:10]}")
        else:
            print(f"❌ 获取列表失败！")
            print(f"错误信息：{result.get('data', result.get('error', '未知错误'))}")
            sys.exit(1)
    
    else:
        print(f"错误：未知命令 '{command}'")
        print("可用命令：upload, delete, list")
        sys.exit(1)

if __name__ == "__main__":
    main()
