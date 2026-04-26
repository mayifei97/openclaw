# MrDoc (觅思文档) API 使用指南

**版本**: 1.0  
**更新时间**: 2026-03-05  
**适用版本**: MrDoc v9.3+

---

## 📌 快速开始

### 配置信息
```python
MRDOC_URL = "http://8.163.49.28:8888"
API_TOKEN = "YOUR_TOKEN"
PROJECT_ID = 1  # 文集 ID
```

---

## ✅ 正确的 API 调用方式

### 1️⃣ 创建文档

**API 路径**: `/api/create_doc/`

**请求方式**: POST (JSON)

**参数**:
```json
{
  "pid": 1,              // 文集 ID（不是 project_id！）
  "title": "文档标题",
  "doc": "<h1>HTML 内容</h1>...",  // HTML 富文本（不是 content！）
  "editor_mode": 1       // 1=HTML 富文本，2=Markdown，3=纯文本
}
```

**Python 示例**:
```python
import json
import urllib.request

url = "http://8.163.49.28:8888/api/create_doc/?token=YOUR_TOKEN"

data = {
    "pid": 1,
    "title": "文档标题",
    "doc": "<h1>HTML 内容</h1>...",
    "editor_mode": 1
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

with urllib.request.urlopen(req, timeout=30) as response:
    result = json.loads(response.read().decode('utf-8'))
    # 成功：{"status": true, "data": 文档 ID}
    # 失败：{"status": false, "data": "错误信息"}
```

**成功响应**:
```json
{
  "status": true,
  "data": 17  // 文档 ID
}
```

**文档 URL 格式**:
```
http://8.163.49.28:8888/project-{pid}/doc-{doc_id}/
示例：http://8.163.49.28:8888/project-1/doc-17/
```

---

### 2️⃣ 删除文档

**API 路径**: `/api/delete_doc/`

**请求方式**: POST (JSON)

**参数**:
```json
{
  "did": 17  // 文档 ID（注意：是 did，不是 doc_id！）
}
```

**Python 示例**:
```python
url = "http://8.163.49.28:8888/api/delete_doc/?token=YOUR_TOKEN"

data = {
    "did": 17  # 注意：参数名是 did，不是 doc_id！
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

with urllib.request.urlopen(req, timeout=30) as response:
    result = json.loads(response.read().decode('utf-8'))
    # 成功：{"status": true, "data": "ok"}
```

**注意**:
- 这是软删除，将文档状态改为 3（不是物理删除）
- 需要验证 Token 和文档创建者权限

---

### 3️⃣ 获取文档列表

**API 路径**: `/api/get_docs/`

**请求方式**: GET

**参数**:
```
?token=YOUR_TOKEN&pid=1
```

**Python 示例**:
```python
url = "http://8.163.49.28:8888/api/get_docs/?token=YOUR_TOKEN&pid=1"

req = urllib.request.Request(url, method='GET')

with urllib.request.urlopen(req, timeout=30) as response:
    result = json.loads(response.read().decode('utf-8'))
    # 成功：{"status": true, "data": [文档列表]}
```

**返回示例**:
```json
{
  "status": true,
  "data": [
    {
      "id": 17,
      "name": "文档标题",
      "parent_doc": 0,
      "top_doc": 1,
      "status": 1,
      "create_time": "2026-03-05T08:16:18.989",
      "modify_time": "2026-03-05T08:16:18.989",
      "create_user": "username",
      "editor_mode": 1
    }
  ]
}
```

---

## ❌ 常见错误（避免踩坑！）

### 错误 1: API 路径错误
```
❌ POST /api/doc/create/      → 404
❌ POST /manage/api/doc/create/ → 404
❌ POST /api/project/          → 404

✅ POST /api/create_doc/       → 成功
```

### 错误 2: 参数名错误
```python
# ❌ 错误的参数名
data = {
    "project_id": 1,    # 应该是 pid
    "content": "...",   # 应该是 doc
    "doc_id": 17        # 删除时应该是 did
}

# ✅ 正确的参数名
data = {
    "pid": 1,
    "doc": "...",
    "did": 17  # 删除时用
}
```

### 错误 3: Content-Type 错误
```python
# ❌ 错误：使用 form-data
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# ✅ 正确：使用 JSON
headers = {'Content-Type': 'application/json'}
```

### 错误 4: Token 传递位置错误
```python
# ❌ 错误：放在 Header
headers = {'Authorization': 'Bearer TOKEN'}

# ✅ 正确：放在 URL 参数
url = "http://8.163.49.28:8888/api/create_doc/?token=YOUR_TOKEN"
```

### 错误 5: 编辑器模式错误
```python
# ❌ 错误：使用 Markdown 格式但 editor_mode=1
data = {
    "doc": "# Markdown 标题",  # Markdown 内容
    "editor_mode": 1           # 1=HTML，会导致渲染错误
}

# ✅ 正确：HTML 内容 + editor_mode=1
data = {
    "doc": "<h1>HTML 标题</h1>",
    "editor_mode": 1
}
```

---

## 📋 参数名速查表

| API | 参数名 | 说明 | 示例 |
|-----|--------|------|------|
| 创建文档 | `pid` | 文集 ID | `1` |
| 创建文档 | `doc` | 文档内容（HTML） | `"<h1>内容</h1>"` |
| 创建文档 | `editor_mode` | 编辑器模式 | `1` (HTML) |
| 创建文档 | `title` | 文档标题 | `"日报"` |
| 删除文档 | `did` | 文档 ID | `17` |
| 获取列表 | `pid` | 文集 ID（URL 参数） | `1` |

**记忆口诀**: 
- 创建用 `pid` 和 `doc`
- 删除用 `did`
- 列表用 `pid`（URL 参数）

---

## 🛠️ 可复用脚本

使用现成的 Python 脚本，避免手动调用 API：

```bash
# 上传文档
python3 scripts/mrdoc_upload.py upload "文档标题" "文件.html"

# 删除文档
python3 scripts/mrdoc_upload.py delete 17

# 列出文档
python3 scripts/mrdoc_upload.py list
```

脚本位置：`/home/admin/.openclaw/workspace/scripts/mrdoc_upload.py`

---

## 📊 编辑器模式说明

| 模式 | 值 | 内容格式 | 适用场景 |
|------|-----|----------|---------|
| HTML 富文本 | 1 | HTML 标签 | 正式报告、带样式的文档 |
| Markdown | 2 | Markdown 语法 | 简单文档、笔记 |
| 纯文本 | 3 | 纯文本 | 代码片段、日志 |

**推荐**: 正式报告使用 `editor_mode=1`（HTML 富文本）

---

## 🔍 故障排查

### 问题 1: 返回 404
**原因**: API 路径错误  
**解决**: 确认路径是 `/api/create_doc/`（不是 `/api/doc/create/`）

### 问题 2: 返回"系统异常"
**可能原因**:
1. 参数名错误（如 `project_id` 而不是 `pid`）
2. Content-Type 不是 JSON
3. Token 无效

**解决**: 检查参数名、Content-Type、Token

### 问题 3: 文档创建成功但内容为空
**原因**: 参数名错误（如 `content` 而不是 `doc`）  
**解决**: 确认参数名是 `doc`

### 问题 4: 删除失败
**可能原因**:
1. 参数名错误（如 `doc_id` 而不是 `did`）
2. Token 不是文档创建者

**解决**: 确认参数名是 `did`，使用正确的 Token

---

## 📚 历史经验

**2026-03-05 问题记录**:
- 初次使用时尝试了多个错误的 API 路径，均返回 404
- 正确的 API 路径是 `/api/create_doc/`
- 删除 API 的参数名是 `did`，不是直观的 `doc_id`
- 必须使用 JSON 格式，form-data 会失败
- 文档 URL 格式在 v9.3 中改为 `/project-{pid}/doc-{doc_id}/`

**教训**: 
1. 仔细查看 MrDoc 源码中的 API 定义
2. 参数名要严格按照源码（`pid`, `doc`, `did`）
3. 所有经验已记录到本文件和脚本中，避免重复犯错

---

## 📖 参考资料

- MrDoc 官方文档：https://www.mrdoc.pro/
- MrDoc GitHub: https://github.com/zmister2016/MrDoc
- API 源码位置：`/app/MrDoc/app_api/views.py`
