#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台 Git 多仓库批量同步工具
支持：
  1. 双击手动同步（macOS/Windows 均可）
  2. 被系统定时任务调用，实现后台自动同步
作者：Your Name
更新：2025-12-08
"""

import subprocess
import sys
import pathlib
import datetime
import platform

# -------------------- 基础配置 --------------------
# 以下路径全部基于「脚本所在目录」计算，搬家也方便
根目录 = pathlib.Path(__file__).resolve().parent  # 本脚本文件夹
日志目录 = 根目录 / "logs"  # 日志目录
仓库清单文件 = 根目录 / "repos.txt"  # 仓库路径清单
日志文件 = 日志目录 / f"sync_{datetime.date.today():%Y%m%d}.log"  # 日志按天归档


# -------------------- 工具函数 --------------------
def 记录日志(msg: str, is_success: bool = None):
    """
    同时打印到终端 + 追加到日志文件，方便后续排错
    时间格式：月-日 时:分:秒
    is_success: True=成功信息(✅), False=失败信息(❌), None=普通信息
    """
    ts = datetime.datetime.now().strftime("%m-%d %H:%M:%S")

    # 根据状态添加图标
    if is_success is True:
        prefix = "✅"
    elif is_success is False:
        prefix = "❌"
    else:
        prefix = "ℹ️"

    line = f"[{ts}] {prefix} {msg}"
    print(line)
    # 追加写，UTF-8 兼容中文路径/提交信息
    日志文件.open("a", encoding="utf-8").write(line + "\n")


def 执行git命令(*args, repo: pathlib.Path):
    """
    在指定仓库目录内执行 git 命令
    返回 subprocess.CompletedProcess 对象
    """
    return subprocess.run(
        ["git"] + list(args), cwd=repo, text=True, capture_output=True, encoding="utf-8"
    )


def 同步仓库(repo: pathlib.Path):
    """
    对单个仓库执行：
      1. git pull --rebase
      2. 如有改动则自动 add + commit
      3. git push
    任何一步失败都会记录错误并跳过
    """
    if not (repo / ".git").is_dir():
        记录日志(f"跳过 {repo} （未发现 .git 目录）", is_success=False)
        return

    记录日志(f"开始处理  {repo}")

    # 1. 拉取远端更新
    res = 执行git命令("pull", "--rebase", repo=repo)
    if res.returncode:
        记录日志(f"  拉取失败: {res.stderr.strip()}", is_success=False)
        return

    # 2. 检查是否有未提交改动
    res = 执行git命令("status", "--porcelain", repo=repo)
    if res.stdout.strip():
        # 有改动 -> 自动提交
        执行git命令("add", "-A", repo=repo)
        执行git命令(
            "commit",
            "-m",
            f"auto-sync {datetime.datetime.now():%Y-%m-%d_%H%M}",
            repo=repo,
        )

    # 3. 推送到远端
    res = 执行git命令("push", repo=repo)
    if res.returncode:
        记录日志(f"  推送失败: {res.stderr.strip()}", is_success=False)
        return

    记录日志("  完成", is_success=True)


def 主函数():
    """
    入口函数：
      - 创建日志目录
      - 检查 repos.txt 是否存在
      - 逐行读取仓库路径
      - 调用 sync_repo 批量同步
    """
    # 创建日志目录（如果不存在）
    日志目录.mkdir(exist_ok=True)

    if not 仓库清单文件.exists():
        sys.exit("repos.txt 没找到！请参照 README 创建此文件并写入仓库路径。")

    # 允许空行和 # 注释行
    repos = [
        p
        for p in 仓库清单文件.read_text(encoding="utf-8").splitlines()
        if p.strip() and not p.strip().startswith("#")
    ]
    if not repos:
        sys.exit("repos.txt 是空的！请至少填写一个本地仓库路径。")

    记录日志("===== 批量同步开始 =====")
    for path_str in repos:
        repo = pathlib.Path(path_str).expanduser().resolve()
        if not repo.exists():
            记录日志(f"路径不存在：{repo}", is_success=False)
            continue
        同步仓库(repo)
    记录日志("===== 全部完成 =====", is_success=True)


# -------------------- 主程序 --------------------
if __name__ == "__main__":
    主函数()
    # Windows 双击运行时防止窗口秒退
    if platform.system() == "Windows":
        input("\n按回车键退出 ...")
