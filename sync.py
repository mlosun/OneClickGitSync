#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键同步多个 Git 仓库
自动扫描指定目录下的 Git 仓库并执行同步
"""

import subprocess
import sys
import pathlib
import datetime
import platform
from pathlib import Path

# ==================== 配置 ====================
根目录 = pathlib.Path(__file__).resolve().parent
日志目录 = 根目录 / "logs"
日志文件 = 日志目录 / f"sync_{datetime.date.today():%Y%m%d}.log"
ENV文件 = 根目录 / ".env"


# ==================== 系统识别 ====================
def 获取系统类型():
    """获取当前操作系统类型"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"


def 读取env文件():
    """从 .env 文件读取扫描路径"""
    if not ENV文件.exists():
        记录日志(f"❌ .env 文件不存在：{ENV文件}")
        return None

    系统类型 = 获取系统类型()
    扫描路径 = None

    try:
        with open(ENV文件, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip().upper()
                    value = value.strip()

                    # 根据系统类型选择对应的路径
                    if 系统类型 == "macos" and key == "MACOS_PATH":
                        扫描路径 = value
                        break
                    elif 系统类型 == "windows" and key == "WINDOWS_PATH":
                        扫描路径 = value
                        break

        if 扫描路径:
            记录日志(f"✅ 已加载 {系统类型} 系统路径配置：{扫描路径}")
        else:
            记录日志(f"❌ .env 文件中未找到 {系统类型.upper()}_PATH 配置")

    except Exception as e:
        记录日志(f"❌ 读取 .env 文件失败：{str(e)}")

    return 扫描路径


def 扫描并同步仓库(扫描路径):
    """扫描指定路径下的子文件夹，发现一个 Git 仓库就立即同步"""
    基础路径 = Path(扫描路径).expanduser().resolve()
    计数 = 0

    if not 基础路径.exists():
        记录日志(f"❌ 扫描路径不存在：{基础路径}")
        return

    try:
        # 遍历第一层子文件夹
        for 子目录 in 基础路径.iterdir():
            if 子目录.is_dir() and not 子目录.name.startswith("."):
                # 检查是否是 Git 仓库
                git目录 = 子目录 / ".git"
                if git目录.is_dir():
                    计数 += 1
                    同步仓库(子目录)

    except PermissionError:
        记录日志(f"❌ 路径访问被拒绝：{基础路径}")
    except Exception as e:
        记录日志(f"❌ 扫描失败：{str(e)}")

    if 计数 == 0:
        记录日志("❌ 未发现 Git 仓库")
    else:
        记录日志(f"✅ 完成，共处理 {计数} 个仓库")


def 记录日志(msg: str, end: str = "\n"):
    """打印到终端 + 追加到日志文件"""
    ts = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}]{msg}"
    print(line, end=end)
    日志文件.open("a", encoding="utf-8").write(line + "\n")


def 执行git命令(*args, repo: pathlib.Path):
    """在指定仓库目录内执行 git 命令"""
    return subprocess.run(
        ["git"] + list(args), cwd=repo, text=True, capture_output=True, encoding="utf-8"
    )


def 同步仓库(repo: pathlib.Path):
    """对单个仓库执行同步：pull → 检查变更 → 自动提交 → push"""
    # 1. 拉取远端更新
    res = 执行git命令("pull", "--rebase", repo=repo)
    if res.returncode:
        错误行 = [line.strip() for line in res.stderr.strip().split('\n') if line.strip()]
        if 错误行:
            记录日志(f"- {repo.name} ❌ 拉取失败")
            记录日志(f"  ├─ {错误行[0]}")
            for line in 错误行[1:]:
                记录日志(f"  └─ {line}")
        else:
            记录日志(f"- {repo.name} ❌ 拉取失败")
        return

    # 2. 检查是否有未提交改动
    res = 执行git命令("status", "--porcelain", repo=repo)
    if res.stdout.strip():
        # 有改动 -> 自动提交
        执行git命令("add", "-A", repo=repo)
        res = 执行git命令(
            "commit",
            "-m",
            f"auto-sync {datetime.datetime.now():%Y-%m-%d_%H%M}",
            repo=repo,
        )
        if res.returncode:
            错误行 = [line.strip() for line in res.stderr.strip().split('\n') if line.strip()]
            if 错误行:
                记录日志(f"- {repo.name} ❌ 提交失败")
                记录日志(f"  ├─ {错误行[0]}")
                for line in 错误行[1:]:
                    记录日志(f"  └─ {line}")
            else:
                记录日志(f"- {repo.name} ❌ 提交失败")
            return
        # 3. 推送到远端
        res = 执行git命令("push", repo=repo)
        if res.returncode:
            错误行 = [line.strip() for line in res.stderr.strip().split('\n') if line.strip()]
            if 错误行:
                记录日志(f"- {repo.name} ❌ 推送失败")
                记录日志(f"  ├─ {错误行[0]}")
                for line in 错误行[1:]:
                    记录日志(f"  └─ {line}")
            else:
                记录日志(f"- {repo.name} ❌ 推送失败")
            return
        记录日志(f"- {repo.name} ✅ 已提交并推送")
    else:
        # 3. 推送到远端
        res = 执行git命令("push", repo=repo)
        if res.returncode:
            错误行 = [line.strip() for line in res.stderr.strip().split('\n') if line.strip()]
            if 错误行:
                记录日志(f"- {repo.name} ❌ 推送失败")
                记录日志(f"  ├─ {错误行[0]}")
                for line in 错误行[1:]:
                    记录日志(f"  └─ {line}")
            else:
                记录日志(f"- {repo.name} ❌ 推送失败")
            return
        记录日志(f"- {repo.name} ✅ 已同步（无改动）")


def 主函数():
    """主入口：读取配置 → 扫描 → 同步"""
    # 创建日志目录
    日志目录.mkdir(exist_ok=True)

    扫描路径 = 读取env文件()
    if not 扫描路径:
        sys.exit("未找到有效的扫描路径配置，请检查 .env 文件。")

    # 扫描并同步仓库
    扫描并同步仓库(扫描路径)


if __name__ == "__main__":
    主函数()

    # Windows 双击运行时防止窗口秒退
    if platform.system() == "Windows":
        input("\n按回车键退出 ...")
