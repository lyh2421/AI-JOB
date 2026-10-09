#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把仓库里的 Agent Skills 安装到 Codex 的个人技能目录。

Codex 只从 `~/.codex/skills` 加载技能，不会读取仓库里的 `.agents/skills`，
所以克隆仓库后技能不会自动出现在 Codex 里。本脚本按仓库的薄指针原则，
把技能复制到个人技能目录，并在安装时把技能文件里指向仓库素材的相对路径
（例如 `../../assets/logos/`）改写成安装机上的绝对路径。

用法：
    python scripts/install_codex_skills.py --list          列出可安装技能
    python scripts/install_codex_skills.py --dry-run       只演示，不写入
    python scripts/install_codex_skills.py                 安装全部技能
    python scripts/install_codex_skills.py --skill asu-resume
    python scripts/install_codex_skills.py --target D:\\my-skills

安装后需要新开一个 Codex 任务，技能才会出现在技能列表里。
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO / ".agents" / "skills"
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt"}
SHARED_ASSETS = "assets/asu"


def default_target():
    codex_home = os.environ.get("CODEX_HOME")
    base = Path(codex_home) if codex_home else Path.home() / ".codex"
    return base / "skills"


def discover_skills():
    if not SOURCE_ROOT.is_dir():
        return []
    return sorted(p for p in SOURCE_ROOT.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def rewrite_patterns():
    assets = (REPO / SHARED_ASSETS).as_posix()
    resume_refs = (REPO / ".agents" / "skills" / "resume" / "references").as_posix()
    return [
        (re.compile(r"(?:\.\./)+assets/"), assets + "/"),
        (re.compile(r"(?:\.\./)+resume/references/"), resume_refs + "/"),
        (re.compile(r"(?:\.\./)+asu/references/"), (REPO / ".agents" / "skills" / "asu" / "references").as_posix() + "/"),
    ]


def rewrite_text_files(skill_dir):
    patterns = rewrite_patterns()
    changed = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for pattern, replacement in patterns:
            text = pattern.sub(replacement, text)
        if path.name == "openai.yaml":
            text = fix_icon_paths(text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(path.relative_to(skill_dir).as_posix())
    return changed


def fix_icon_paths(text):
    fallback = (REPO / "assets" / "asu" / "icons" / "user.svg").as_posix()
    lines = []
    for line in text.splitlines():
        match = re.match(r"^(\s*icon_(?:small|large):\s*)\"(.*)\"\s*$", line)
        if match:
            candidate = Path(match.group(2))
            if not candidate.is_file():
                line = f'{match.group(1)}"{fallback}"'
        lines.append(line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def check_target(target, skills, force):
    resolved = target.resolve()
    if resolved == REPO or REPO in resolved.parents:
        raise SystemExit(f"[错误] 目标目录不能在仓库内：{resolved}")
    if resolved.name != "skills":
        raise SystemExit(f"[错误] 目标目录必须以 skills 结尾：{resolved}")
    existing = [s.name for s in skills if (resolved / s.name).exists()]
    if existing and not force:
        print("[提示] 以下技能已存在，会被覆盖（旧的多余文件不会删除）：" + "、".join(existing))
    return resolved


def install(skill, target, dry_run):
    destination = target / skill.name
    print(f"  {skill.name}  ->  {destination}")
    if dry_run:
        return
    shutil.copytree(skill, destination, dirs_exist_ok=True)
    changed = rewrite_text_files(destination)
    if changed:
        print(f"      已改写素材路径：{'、'.join(changed)}")


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="安装本仓库的 Agent Skills 到 Codex")
    parser.add_argument("--skill", action="append", help="只安装指定技能，可重复")
    parser.add_argument("--target", help="技能目录，默认 %%USERPROFILE%%\\.codex\\skills 或 %%CODEX_HOME%%\\skills")
    parser.add_argument("--list", action="store_true", help="只列出可安装技能")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要执行的操作")
    parser.add_argument("--force", action="store_true", help="已存在的技能直接覆盖，不再提示")
    args = parser.parse_args(argv)

    skills = discover_skills()
    if args.skill:
        wanted = set(args.skill)
        skills = [s for s in skills if s.name in wanted]
        missing = wanted - {s.name for s in skills}
        if missing:
            raise SystemExit(f"[错误] 未找到技能：{'、'.join(sorted(missing))}")

    if not skills:
        raise SystemExit(f"[错误] {SOURCE_ROOT} 下没有找到任何带 SKILL.md 的技能。")

    print(f"仓库   : {REPO}")
    print("可安装 : " + "、".join(s.name for s in skills))

    if args.list:
        return 0

    target = check_target(Path(args.target) if args.target else default_target(), skills, args.force)
    print(f"目标   : {target}")
    if args.dry_run:
        print("模式   : 演示（不写入）")
    for skill in skills:
        install(skill, target, args.dry_run)

    if not args.dry_run:
        print()
        print("完成。请在 Codex 里新开一个任务，然后输入 $asu-resume 之类的技能名调用。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
