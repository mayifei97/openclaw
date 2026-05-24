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

### 🖥️ SSH

- **本地 PC（8890 端口映射）** → `localhost:8890`, 用户: `ma`, 密码: `pk85626428`
  - 网关服务器的 8890 端口通过端口映射转发到用户本地 PC
  - 主机名: `ma-VMware-Virtual-Platform`
  - 系统: Ubuntu 24.04 (内核 6.17.0-29, VMware 虚拟机)
  - 磁盘: 40G 总量，已用 18G，剩余 20G
  - 2026-05-24 验证连接成功

Add whatever helps you do your job. This is your cheat sheet.
