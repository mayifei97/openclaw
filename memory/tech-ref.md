# 技术参考文档（从MEMORY.md迁移）

---

## 🧹 子 Agent 会话清理方法

子agent完成后，会话记录残留在多处，需全部清理才能从Dashboard消失：

1. **会话索引文件**：`/root/.openclaw/agents/main/sessions/sessions.json`（Dashboard读这个文件）
   - 用Python读取JSON，删除对应session key的条目
2. **会话记录文件**：`/root/.openclaw/agents/main/sessions/{session_id}.*`（.jsonl、.trajectory.jsonl、.trajectory-path.json）
   - 直接rm删除
3. **任务运行数据库**：`/root/.openclaw/tasks/runs.sqlite`（task_runs + task_delivery_state表）
   - 用SQL按child_session_key或task_id删除
4. **网关内存缓存**：重启网关后生效（但重启会断连当前会话）

```python
import json, sqlite3, os, glob

targets = ['子agent的session_id片段']  # 如 ['d65e14f2', 'f4bae9d3']
sessions_dir = '/root/.openclaw/agents/main/sessions'

# 1. Clean sessions.json
with open(f'{sessions_dir}/sessions.json', 'r') as f:
    data = json.load(f)
keys_to_remove = [k for k in data if any(t in k for t in targets)]
for k in keys_to_remove: del data[k]
with open(f'{sessions_dir}/sessions.json', 'w') as f:
    json.dump(data, f, indent=2)

# 2. Clean session files
for f in os.listdir(sessions_dir):
    if any(t in f for t in targets):
        os.remove(os.path.join(sessions_dir, f))

# 3. Clean runs database
conn = sqlite3.connect('/root/.openclaw/tasks/runs.sqlite')
c = conn.cursor()
c.execute("SELECT task_id FROM task_runs WHERE child_session_key LIKE '%" + "%' OR child_session_key LIKE '%".join(targets) + "%'")
task_ids = [r[0] for r in c.fetchall()]
if task_ids:
    c.execute(f"DELETE FROM task_delivery_state WHERE task_id IN ({','.join(['?']*len(task_ids))})", task_ids)
    c.execute(f"DELETE FROM task_runs WHERE task_id IN ({','.join(['?']*len(task_ids))})", task_ids)
conn.commit(); conn.close()
```

⚠️ 不要自己执行 `openclaw gateway restart`，会断连当前会话！让用户来操作。

---

## 📊 Dashboard 技术细节

### CPU趋势图"秒统计"功能
- **秒模式**：显示最近60个数据点（约60秒），时间戳显示到秒
- **分钟模式**：将秒级数据聚合为分钟级（每60秒求平均），显示最近60分钟
- **数据来源**：`/api/sysmon-data` 端点读取 `sysmon_data.json`
- **更新频率**：前端每1秒调用一次API更新图表

### 云监控问题
- 阿里云cloudmonitor会定期杀死所有node进程
- 原sysmon.js(Node.js版)每6秒被杀→数据5-6秒间隔
- 已改写为Python版(`sysmon_py.py`)，Python进程不受影响
- 服务文件：`/etc/systemd/system/openclaw-sysmon.service`
- 数据文件：`/root/.openclaw/workspace/tools/sysmon_data.json`

### 端口服务
- 8887：OpenClaw Dashboard（今日请求数/Token消耗统计已按用户要求移除,2026-04-28）
- 8888：MrDoc觅思文档（Docker容器v9.3）
- 8889：文件管理器
