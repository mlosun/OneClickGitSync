# OneClickGitSync

一键批量同步多个 Git 仓库的 Python 脚本，支持自动扫描、拉取、提交和推送。

## ✨ 功能特点

- **自动扫描**：自动识别指定目录下的所有 Git 仓库
- **一键同步**：批量执行 `pull → commit → push` 流程
- **跨平台**：支持 macOS 和 Windows 系统
- **日志记录**：详细记录同步过程和错误信息，按日期自动归档
- **容错机制**：单个仓库失败不影响其他仓库的处理

## 📦 安装

### 环境要求

- Python 3.6+
- Git

### 克隆仓库

```bash
git clone https://cnb.cool/mlosun/OneClickGitSync
cd OneClickGitSync
```

或者

```bash
git clone https://github.com/mlosun/OneClickGitSync.git
cd OneClickGitSync
```

## 🚀 快速开始

### 1. 配置扫描路径

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据你的操作系统设置扫描路径：

```bash
# macOS
MACOS_PATH=/Users/yourname/dev

# Windows
WINDOWS_PATH=D:\Projects
```

脚本会自动扫描该路径下的**第一层子文件夹**，识别包含 `.git` 目录的仓库。

### 2. 运行同步

```bash
python sync.py
```

## 🔄 工作流程

1. **扫描**：遍历指定目录下的子文件夹
2. **识别**：检查是否存在 `.git` 目录判断是否为 Git 仓库
3. **同步**：对每个仓库执行以下操作
   - `git pull --rebase` - 拉取远端更新
   - `git status --porcelain` - 检测本地改动
   - 如有改动 → `git add -A` + `git commit` - 自动提交
   - `git push` - 推送到远端
4. **记录**：所有操作和错误都会记录到日志文件

## 📝 日志

- **位置**：`logs/sync_YYYYMMDD.log`
- **格式**：`[月-日 时:分:秒] 消息`
- **归档**：自动按日期创建新的日志文件

## ⏰ 自动执行

### macOS（crontab）

编辑定时任务：

```bash
crontab -e
```

添加定时任务（例如每天 8:00 和 20:00 执行）：

```cron
0 8,20 * * * /usr/bin/python3 /完整路径/sync.py >> /tmp/sync.log 2>&1
```

### Windows（任务计划程序）

1. 按 `Win + R`，输入 `taskschd.msc` 打开任务计划程序
2. 创建基本任务
3. 设置触发器（如：每天、每周）
4. 设置操作：
   - 程序：`python`
   - 参数：`C:\完整路径\sync.py`

## ❓ 常见问题

### 拉取失败

可能原因：
- 有未提交的本地改动（无法 rebase）
- 网络连接问题
- 认证失败

**解决**：手动处理冲突或检查网络/权限配置

### 推送失败

可能原因：
- 网络连接问题
- 无推送权限
- SSH 密钥未配置

**解决**：检查网络、仓库权限或 SSH 配置

### 如何跳过某个仓库？

将仓库移出扫描目录，或在文件夹名前添加 `.` 前缀

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `sync.py` | 主脚本 |
| `.env` | 路径配置文件（需从 `.env.example` 复制） |
| `.env.example` | 配置示例 |
| `logs/` | 日志目录（自动创建） |
| `.cnb.yml` | CNB 云原生构建配置 |

## 📄 许可证

[MIT License](LICENSE)

---

> 💡 提示：首次使用建议先用测试仓库验证配置，再应用到生产环境

> ⚠️ 注意：本文档由 AI 生成，可能存在错误。如发现不准确之处，欢迎提交 Issue 指正。