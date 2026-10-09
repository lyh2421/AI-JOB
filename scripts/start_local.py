#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 Codex 环境里一键启动 CareerPilot-CN 本地服务。

    CareerPilot 主站    ->  http://127.0.0.1:8000
    投递进度看板        ->  http://127.0.0.1:8420/dashboard.html

仅使用标准库。每个服务在独立的控制台窗口里运行，关掉窗口或在窗口里按 Ctrl+C 即可停止。

用法：
    python scripts/start_local.py            启动两个服务并打开浏览器
    python scripts/start_local.py --check    只解析运行时路径并打印版本，不启动
    python scripts/start_local.py --no-browser
"""

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("USERPROFILE") or Path.home())

BOARD_URL = "http://127.0.0.1:8420/dashboard.html"


def find_python():
    candidates = [
        HOME / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
        Path(sys.executable),
    ]
    for path in candidates:
        if path and path.exists():
            return str(path)
    from shutil import which

    return which("python") or which("python3")


def find_node():
    candidates = [
        HOME / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe",
    ]
    for path in candidates:
        if path and path.exists():
            return str(path)
    from shutil import which

    return which("node")


def url_ready(url, timeout=2.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, OSError):
        return False


def wait_url(url, seconds=30):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if url_ready(url):
            return True
        time.sleep(0.5)
    return False


def spawn(argv):
    flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    return subprocess.Popen(argv, cwd=str(ROOT), creationflags=flags)


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="启动 CareerPilot-CN 本地服务")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="CareerPilot 主站端口，默认 8000",
    )
    parser.add_argument("--check", action="store_true", help="只检查运行时，不启动服务")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args(argv)

    python_exe = find_python()
    node_exe = find_node()
    web_url = f"http://127.0.0.1:{args.port}/"

    print(f"仓库目录 : {ROOT}")
    print(f"Python   : {python_exe or '未找到'}")
    print(f"Node     : {node_exe or '未找到（只有看板需要 Node）'}")

    if python_exe is None:
        print("[错误] 未找到 Python 3.10+。请安装 Python，或先启动一次 Codex 以展开自带运行时。")
        return 1

    if args.check:
        subprocess.run([python_exe, "-V"])
        if node_exe:
            subprocess.run([node_exe, "-v"])
        return 0

    if url_ready(web_url):
        print(f"CareerPilot 主站已在运行：{web_url}")
    else:
        print(f"正在启动 CareerPilot 主站 -> {web_url}")
        spawn([python_exe, str(ROOT / "web" / "server.py"), "--port", str(args.port)])

    if node_exe is None:
        print("[警告] 未找到 Node.js，跳过投递看板（CareerPilot 主站不受影响）。")
    elif url_ready(BOARD_URL):
        print(f"投递进度看板已在运行：{BOARD_URL}")
    else:
        print(f"正在启动投递进度看板 -> {BOARD_URL}")
        spawn([node_exe, str(ROOT / "tools" / "jobhuntbot" / "dashboard" / "server.js")])

    print()
    web_ok = wait_url(web_url, 30)
    board_ok = wait_url(BOARD_URL, 30) if node_exe else False
    print(("CareerPilot 主站 : 正常  " if web_ok else "CareerPilot 主站 : 未响应，请看对应服务窗口  ") + web_url)
    if node_exe:
        print(("投递进度看板     : 正常  " if board_ok else "投递进度看板     : 未响应，请看对应服务窗口  ") + BOARD_URL)
    print()
    print("服务各自运行在独立窗口里；关掉窗口或在窗口里按 Ctrl+C 即可停止。")

    if not args.no_browser:
        if web_ok:
            webbrowser.open(web_url)
        if board_ok:
            webbrowser.open(BOARD_URL)

    return 0 if web_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
