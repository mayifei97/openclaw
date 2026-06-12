# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### 🖼️ 图片识别
- 当前模型(newapi/glm-5.1)不支持图片
- 图片识别用 **newapi/kimi-k2.6**（支持多模态），通过子agent调用
- 其他支持图片的模型：bailian/qwen3.5-plus、bailian/kimi-k2.5、codex/gpt-5.5等

### 🤖 可用模型
| Provider | 模型 | 图片 | 状态 |
|----------|------|------|------|
| astroncodingplan | astron-code-latest | ❌ | 默认模型 |
| newapi | glm-5.1 | ❌ | 当前主模型 |
| newapi | kimi-k2.6 | ✅ | 图片识别主力 |

### 🖥️ SSH

- **本地 PC（8890 端口映射）** → `localhost:8890`, 用户: `ma`, 密码: `pk85626428`
  - 网关服务器的 8890 端口通过端口映射转发到用户本地 PC
  - 主机名: `ma-VMware-Virtual-Platform`
  - 系统: Ubuntu 24.04 (内核 6.17.0-29, VMware 虚拟机)
  - 磁盘: 40G 总量，已用 18G，剩余 20G
  - 2026-05-24 验证连接成功

Add whatever helps you do your job. This is your cheat sheet.
