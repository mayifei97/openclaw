# MrDoc API 技能

**版本**: 1.0  
**创建时间**: 2026-03-05  
**作者**: 根据用户反馈创建

---

## 触发条件

当用户提到以下关键词时，应参考本技能：
- "上传到觅思文档"
- "MrDoc"
- "觅思文档 API"
- "上传文档"

---

## 使用指南

**重要**: 所有 MrDoc API 调用必须参考 `skills/mrdoc-api-guide.md` 文档！

该文档包含：
1. ✅ 正确的 API 调用方式
2. ❌ 常见错误和避坑指南
3. 🛠️ 可复用的 Python 脚本
4. 📋 参数名速查表

---

## 快速调用

### 方法 1: 使用脚本（推荐）
```bash
# 上传文档
python3 /home/admin/.openclaw/workspace/scripts/mrdoc_upload.py upload "文档标题" "文件.html"

# 删除文档
python3 /home/admin/.openclaw/workspace/scripts/mrdoc_upload.py delete <文档 ID>

# 列出文档
python3 /home/admin/.openclaw/workspace/scripts/mrdoc_upload.py list
```

### 方法 2: 直接调用 API
参考 `skills/mrdoc-api-guide.md` 中的 Python 示例代码

---

## 关键参数名（必须记住！）

| 操作 | 参数名 | 常见错误 |
|------|--------|---------|
| 创建文档 | `pid`, `doc` | ❌ project_id, content |
| 删除文档 | `did` | ❌ doc_id |
| 获取列表 | `pid` (URL 参数) | ❌ project_id |

**记忆口诀**: 
- 创建用 `pid` 和 `doc`
- 删除用 `did`
- 列表用 `pid`

---

## 配置信息

```python
MRDOC_URL = "http://8.163.49.28:8888"
API_TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"
PROJECT_ID = 1  # 基金投资文集
EDITOR_MODE = 1  # HTML 富文本
```

---

## 文档格式要求

**必须使用 HTML 富文本格式** (`editor_mode=1`)：
- ✅ 包含完整的 HTML 标签：`<h1>`, `<table>`, `<strong>` 等
- ✅ 可以包含 CSS 样式
- ❌ 不要使用 Markdown 格式

示例：
```html
<h1>标题</h1>
<table>
  <tr><th>列 1</th><th>列 2</th></tr>
  <tr><td>值 1</td><td>值 2</td></tr>
</table>
```

---

## 错误处理

如果 API 调用失败，按以下步骤排查：

1. **检查 API 路径**: 必须是 `/api/create_doc/` 或 `/api/delete_doc/`
2. **检查参数名**: `pid`, `doc`, `did`（不是 project_id, content, doc_id）
3. **检查 Content-Type**: 必须是 `application/json`
4. **检查 Token**: 确认 Token 有效且放在 URL 参数中
5. **查看详细文档**: `skills/mrdoc-api-guide.md` 的故障排查章节

---

## 经验来源

本技能基于 2026-03-05 的实际使用经验创建：
- 初次使用时尝试了多个错误的 API 路径
- 花费大量时间排查参数名错误
- 最终找到正确的调用方式

**目的**: 避免其他会话重复犯错，节省时间

---

## 相关文档

- 详细 API 指南：`skills/mrdoc-api-guide.md`
- 上传脚本：`scripts/mrdoc_upload.py`
- 记忆文件：`memory/2026-03-05.md`
- 长期记忆：`MEMORY.md`
