> 本文档由 AI 生成，未经仔细审核，仅供参考。

# GitMultiSync

🚀 跨平台 Git 多仓库批量同步工具

一个轻量级的 Python 脚本，支持在 macOS 和 Windows 系统上同时实现：

- 🔄 **批量同步**：一键同步多个 Git 仓库
- ⏰ **自动调度**：支持系统定时任务自动执行
- 🖱️ **图形友好**：双击即可运行，无需命令行操作
- 📝 **详细日志**：完整的同步过程记录和错误追踪

## ✨ 主要特性

- **跨平台兼容**：原生支持 macOS 和 Windows
- **零配置运行**：解压即用，无额外依赖
- **智能提交**：自动检测变更并提交
- **错误容错**：单个仓库失败不影响其他仓库
- **日志归档**：按日期自动归档日志文件
- **路径友好**：支持相对路径、绝对路径和用户目录简写

## 📁 项目结构

```
GitMultiSync/
├── sync.py              # 核心同步脚本
├── repos.txt            # 仓库路径配置文件
├── repos.txt.example    # 仓库路径配置文件模板
├── README.md            # 项目说明文档
├── .gitignore           # Git 忽略文件配置
└── logs/                # 日志文件目录（自动创建）
    └── sync_YYYYMMDD.log
```

## 🚀 快速开始

### 1. 获取项目

```bash
git clone https://github.com/你的用户名/GitMultiSync.git
cd GitMultiSync
```

### 2. 配置仓库路径

复制配置模板并编辑：

```bash
cp repos.txt.example repos.txt
```

编辑 `repos.txt` 文件，每行填写一个本地仓库的绝对路径：

```txt
# macOS 示例
/Users/yourname/dev/projectA
/Users/yourname/dev/projectB

# Windows 示例
D:\Projects\projectC
D:\Projects\projectD

# 支持注释（以 # 开头）和空行
```

### 3. 手动同步测试

1. 通过 python 运行 `sync.py` 文件
2. 脚本将显示实时同步进度
3. 完成后在 `logs/` 目录生成日志文件。

### 4. 创建桌面图标

#### macOS（使用快捷指令）
TODO

#### Windows（使用快捷方式）
1. 使用桌面右键新建`快捷方式`
2. 在请键入对象的位置输入`python /完整路径/GitMultiSync/sync.py`
3. 下一步完成后即在桌面生成快捷方式

### 5. 设置自动同步

#### macOS（使用 cron）

```bash
crontab -e
```

添加以下内容（示例：每天 8:00 和 20:00 自动同步）：

```cron
# 每天 8:00 和 20:00 执行同步
0 8,20 * * * /usr/bin/python3 /完整路径/GitMultiSync/sync.py
```

#### Windows（使用任务计划程序）

1. `Win + R` → 输入 `taskschd.msc`
2. 创建基本任务
3. 设置触发器（如：每天）
4. 设置操作：
   - 程序或脚本：`python`
   - 参数：`C:\完整路径\GitMultiSync\sync.py`

## 🔧 工作原理

脚本对每个配置的仓库执行以下操作：

1. **拉取更新**：`git pull --rebase`
2. **检测变更**：`git status --porcelain`
3. **自动提交**：如有未提交变更，执行 `git add -A` 和 `git commit`
4. **推送更新**：`git push`

任何步骤失败都会记录错误并继续处理下一个仓库。

## 📊 日志系统

- 日志文件位置：`logs/sync_YYYYMMDD.log`
- 日志格式：`[月-日 时:分:秒] 消息内容`
- 自动创建日志目录
- 按日期归档，便于追踪历史记录

## ⚙️ 自定义配置

### 修改同步策略

编辑 `sync.py` 中的 `sync_repo()` 函数：

```python
# 默认使用 rebase 策略
git_cmd("pull", "--rebase", repo=repo)

# 可改为 merge 策略
# git_cmd("pull", "--no-rebase", repo=repo)
```

### 自定义提交信息模板

```python
git_cmd(
    "commit", "-m",
    f"auto-sync {datetime.datetime.now():%Y-%m-%d_%H%M}",
    repo=repo
)
```

### 多远程仓库支持

在目标仓库中添加额外的远程地址：

```bash
# 添加第二个远程仓库
git remote set-url --add origin https://github.com/user/repo.git

# 查看当前远程配置
git remote -v
```

## 🐛 常见问题

### Q: 双击运行后窗口闪退？

**A:** 请在命令行中执行脚本查看详细错误：

```bash
python sync.py
```

常见原因：
- 未安装 Git 或未添加到系统 PATH
- SSH 密钥未配置
- 仓库路径不存在或权限不足

### Q: 日志文件中文乱码？

**A:** 确保系统终端使用 UTF-8 编码：

- **macOS**：默认支持 UTF-8
- **Windows**：Windows 10 1903+ 版本默认 UTF-8，老版本需在注册表中设置

### Q: 如何跳过某些仓库的同步？

**A:** 在 `repos.txt` 中使用 `#` 注释该行，或临时删除该行：

```txt
# 暂时跳过这个仓库
# /Users/yourname/dev/projectA

/Users/yourname/dev/projectB
```

### Q: 如何处理合并冲突？

**A:** 脚本遇到合并冲突会跳过该仓库，请手动处理：

```bash
cd /path/to/conflicted/repo
git status
# 手动解决冲突后
git add .
git rebase --continue
```

## 📝 开发说明

### 环境要求

- Python 3.6+
- Git 2.0+
- 操作系统：macOS 10.12+ 或 Windows 10+

### 核心函数

- `git_cmd()`: 执行 Git 命令的封装函数
- `log()`: 统一日志输出函数
- `sync_repo()`: 单仓库同步逻辑
- `main()`: 主程序入口

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -m 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- [Git 官方文档](https://git-scm.com/doc)
- [Python 官方文档](https://docs.python.org/3/)
- [macOS cron 教程](https://www.maketecheasier.com/use-cron-macos/)
- [Windows 任务计划程序教程](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)

---

> 💡 **提示**：首次使用建议先用测试仓库验证配置正确性，再应用到生产环境。