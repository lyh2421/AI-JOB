# Codex 侧的技能与入口

这个目录说明「Codex 专用版本」需要哪些补充，才能和 `.claude/` 一样完整。

## 一个前提差异

Codex 只从 `~/.codex/skills` 和已安装插件加载技能，**不会**读取仓库里的 `.agents/skills/`。`AGENTS.md` 会被自动读取，但技能不会自动出现。所以克隆仓库后还需要一步安装。

## 安装技能

在仓库根目录执行：

```powershell
python scripts\install_codex_skills.py --list      # 先看看有哪些技能
python scripts\install_codex_skills.py --dry-run   # 演示，不写入
python scripts\install_codex_skills.py             # 安装到 %USERPROFILE%\.codex\skills
python scripts\install_codex_skills.py --skill asu-resume   # 只装简历技能
```

默认会装上全部技能，其中 `jobindex-search`、`jobnet-search`、`jobbank-search`、`jobdanmark-search` 是丹麦招聘网站的 CLI（需要 Bun），中国求职用不上，可以只用 `--skill asu-resume`。

安装器做三件事：

1. 把 `.agents/skills/` 下带 `SKILL.md` 的技能复制到 `%USERPROFILE%\.codex\skills\`（如设置了 `CODEX_HOME` 则用 `%CODEX_HOME%\skills`）。
2. 把技能文件里指向仓库素材的相对路径（如 `../../assets/logos/`）改写成当前仓库的绝对路径——仓库里这些相对路径已经失效，真实素材在 `assets/asu/`。
3. 目标目录含 `skills` 且不在仓库内才会写入，避免误装到别处。

安装后**新开一个 Codex 任务**，就能在输入框里用 `$asu-resume` 这样的名字调用技能。

## 本仓库提供与不提供的技能

| 技能 | 来源 | 说明 |
|---|---|---|
| `asu-resume` | 本仓库 `.agents/skills/asu-resume` | 中文技术简历，产出可编辑 HTML + 打印/PDF |
| 岗位搜索 CLI（`jobindex-search` 等） | 本仓库 `.agents/skills/` | 需要 Bun，属于可选能力 |
| `resume-generator` 等外部技能 | 第三方仓库 | **不内置**：上游未附授权文件，直接复制进本仓库存在授权风险。需要时请从原仓库自行安装到 `%USERPROFILE%\.codex\skills\` |

## 其它 Codex 侧入口

- 规范：根目录 `AGENTS.md`，真源仍是 `.claude/` 与 `.agents/`。
- 启动本地服务：根目录 `启动Codex版.cmd`（= `python scripts/start_local.py`），起主站 8000 与看板 8420。
- 斜杠命令：Codex 没有项目级斜杠命令，用自然语言说明要执行哪个流程即可，Agent 按 `.claude/commands/` 里的同名文件执行。

完整说明见 [`CODEX_README.md`](../CODEX_README.md)。
