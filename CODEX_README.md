# Codex 本地运行说明（CareerPilot-CN）

本文件说明如何在本机 Codex（Codex CLI / Codex 桌面版）里运行本项目。项目全貌见 [`README.md`](README.md)。

## 一键启动

双击仓库根目录的 `启动Codex版.cmd`，或在仓库根目录执行：

```powershell
python scripts\start_local.py
```

启动器会自动完成：

1. 依次尝试 Codex 自带运行时（`%USERPROFILE%\.cache\codex-runtimes\...`）和系统 `python` / `node`。
2. 在独立控制台窗口里分别启动 CareerPilot 主站和 JobHuntBot 看板。
3. 等待健康检查通过后打印结果，并自动打开浏览器。

可用参数：

| 参数 | 作用 |
|---|---|
| `--check` | 只解析并打印运行时版本，不启动服务 |
| `--no-browser` | 启动服务但不自动打开浏览器 |
| `--port 8010` | 更换主站端口（默认 `8000`）|

停止服务：关掉对应服务的控制台窗口，或在窗口里按 `Ctrl+C`。

## 安装技能（克隆后做一次）

Codex 只从 `~/.codex/skills` 加载技能，不会读取仓库里的 `.agents/skills/`，所以技能需要安装一次：

```powershell
python scripts\install_codex_skills.py --list              # 查看可安装技能
python scripts\install_codex_skills.py --skill asu-resume  # 只装中文简历技能
python scripts\install_codex_skills.py                     # 或安装全部
```

安装器会把技能复制到 `%USERPROFILE%\.codex\skills`（设置过 `CODEX_HOME` 时用 `%CODEX_HOME%\skills`），并把技能文件里已失效的 `../../assets/...` 相对路径改写成当前仓库的绝对路径。安装后**新开一个 Codex 任务**，输入 `$asu-resume` 即可调用。细节见 [`.codex/README.md`](.codex/README.md)。

## 访问入口

| 入口 | 本地地址（Codex） | 在线访问（网站版） |
|---|---|---|
| **CareerPilot 主站**（岗位搜索/评分/简历库/AI 助手） | [http://127.0.0.1:8000](http://127.0.0.1:8000) | *（留空，由使用者自行填写自己的阿里云服务器地址）* |
| **投递进度看板**（JobHuntBot 本地看板） | [http://127.0.0.1:8420/dashboard.html](http://127.0.0.1:8420/dashboard.html) | *（留空，由使用者自行填写自己的阿里云服务器地址）* |

「在线访问（网站版）」一列按需求留空：部署到自己的服务器后再填入自家地址。本地运行时用左列的 `127.0.0.1` 地址即可。

## 依赖情况

- **CareerPilot 主站**：只依赖 Python 标准库（`http.server` + `sqlite3`），装好 Python 3.10+ 就能直接启动，无需 `pip install`。
- **JobHuntBot 看板**：零依赖 Node 静态服务，无需 `npm install`。
- **可选增强**：`pip install -r requirements.txt` 后可启用 PDF / DOCX 简历解析（`pdfplumber`、`python-docx`）和 PDF 导出（`reportlab`）；未安装时对应功能会提示降级，不影响启动。
- **岗位搜索 CLI**：`.agents/skills/*/cli` 下的 TypeScript 工具需要 Bun，属于可选能力。

## 在 Codex 里用 Agent 工作流

Codex 会自动读取仓库根目录的 `AGENTS.md`。常用流程：

```text
/doctor  ->  /setup  ->  /scrape  ->  /rank  ->  /apply
```

投递后用 `/outcome` 记录结果，`/board` 查看行动队列，`/html-report` 查看求职漏斗。斜杠命令的真源在 `.claude/commands/`，在 Codex 里用自然语言说明要执行哪个流程，Agent 会按同名规范文件执行。

## 已在本机 Codex 环境验证

- 主站 `http://127.0.0.1:8000` 返回 200（页面为中文界面）。
- 看板 `http://127.0.0.1:8420/dashboard.html` 返回 200。
- 两个服务用 Codex 自带运行时（Python 3.12 / Node 24）启动成功，未安装任何第三方 Python 包。
