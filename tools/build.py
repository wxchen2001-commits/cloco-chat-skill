#!/usr/bin/env python3
"""Repackage an upstream cloco checkout as a single chat Agent Skill.

Usage: python3 tools/build.py <path-to-cloco-checkout> <output-dir>
Writes <output-dir>/cloco/ (the skill folder). build.sh wraps this and zips it.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml  # PyYAML

HERE = Path(__file__).resolve().parent
NOTES = {
    "context-status": " *(Claude Code only — skip in chat)*",
    "lean-verify": " *(needs ~5 GB Lean install — ask first)*",
    "learn": " *(in chat: write the draft to `PROJECT/.claude/skills/`, then offer it to "
             "the user as a skill proposal so it becomes callable)*",
}
PATH_RULES = [
    (r"\.claude/skills/([a-z0-9-]+)/SKILL\.md", r"CLOCO/workflows/\1.md"),
    (r"\.claude/skills/", "CLOCO/workflows/"),
    (r"\.claude/scripts/", "CLOCO/scripts/"),
    (r"\.claude/rules/", "CLOCO/rules/"),
    (r"\.claude/agents/", "CLOCO/agents/"),
]


def rewrite(text: str) -> str:
    for pat, rep in PATH_RULES:
        text = re.sub(pat, rep, text)
    return text


def first_sentence(desc: str) -> str:
    s = re.split(r"(?<=[.!?])\s", " ".join(str(desc).split()))[0]
    return s if len(s) <= 170 else s[:167].rstrip() + "…"


def description(f: Path) -> str:
    """Upstream frontmatter is not always valid YAML (unquoted colons), so read
    single-line descriptions verbatim and use YAML only for block scalars."""
    fm = re.match(r"---\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S).group(1)
    m = re.search(r"^description:\s*(.*)$", fm, re.M)
    if not m:
        return ""
    val = m.group(1).strip()
    if val[:1] in ("|", ">"):
        return str(yaml.safe_load(fm).get("description", ""))
    return val.strip('"').strip("'")


def main(src: Path, out_root: Path) -> None:
    out = out_root / "cloco"
    if out.exists():
        shutil.rmtree(out)
    for d in ("workflows", "agents", "rules", "scripts", "templates", "reference"):
        (out / d).mkdir(parents=True)

    c = src / ".claude"
    for sk in sorted((c / "skills").iterdir()):
        if (sk / "SKILL.md").is_file():
            shutil.copy(sk / "SKILL.md", out / "workflows" / f"{sk.name}.md")
    for sub in ("agents", "rules"):
        for f in sorted((c / sub).glob("*.md")):
            shutil.copy(f, out / sub / f.name)
    for f in sorted((c / "scripts").glob("*.py")):
        shutil.copy(f, out / "scripts" / f.name)
    for f in sorted((src / "templates").glob("*.md")):
        shutil.copy(f, out / "templates" / f.name)
    shutil.copy(src / "CLAUDE.md", out / "reference" / "CLAUDE.md")
    shutil.copy(c / "WORKFLOW_QUICK_REF.md", out / "reference" / "WORKFLOW_QUICK_REF.md")
    for f in ("data_paths.py", "data_paths.R"):
        shutil.copy(src / "code" / "utils" / f, out / "templates" / f)
    shutil.copy(c / "lessons" / "LESSONS.md", out / "templates" / "LESSONS.md")
    shutil.copy(src / "data" / "registry.json", out / "templates" / "registry.json")
    shutil.copy(src / ".env.example", out / "templates" / "env.example")
    shutil.copy(src / ".gitignore", out / "templates" / "gitignore")
    shutil.copytree(src / "lean", out / "templates" / "lean")

    for sub in ("workflows", "agents", "rules", "reference", "templates"):
        for f in (out / sub).glob("*.md"):
            f.write_text(rewrite(f.read_text(encoding="utf-8")), encoding="utf-8")

    dash = out / "scripts" / "dashboard.py"
    old = 'tool = root / ".claude" / "scripts" / "git_tools.py"'
    t = dash.read_text(encoding="utf-8")
    if old not in t:
        sys.exit("dashboard.py changed upstream: review the git_tools.py patch in tools/build.py")
    dash.write_text(t.replace(old, 'tool = Path(__file__).resolve().parent / "git_tools.py"'), encoding="utf-8")

    rows = []
    for f in sorted((out / "workflows").glob("*.md")):
        rows.append(f"- `/{f.stem}` — {first_sentence(description(f))}{NOTES.get(f.stem, '')}")
    head = (HERE / "SKILL.head.md").read_text(encoding="utf-8")
    (out / "SKILL.md").write_text(head.rstrip() + "\n\n" + "\n".join(rows) + "\n", encoding="utf-8")

    rev = subprocess.run(["git", "-C", str(src), "log", "-1", "--format=%H (%ad)", "--date=short"],
                         capture_output=True, text=True).stdout.strip() or "unknown"
    (out / "reference" / "SOURCE.md").write_text(
        f"Source: https://github.com/jfimbett/cloco @ {rev}\n"
        "Author: Juan F. Imbet. README badge declares MIT; no LICENSE file in the repository at this commit.\n"
        "Repackaged for claude.ai chat use: Claude Code skills -> workflows/, .claude paths rewritten "
        "(see SKILL.md section 2). Agent, rule and script contents otherwise unchanged.\n"
        "Patched: scripts/dashboard.py finds git_tools.py next to itself instead of in the project (line ~94).\n",
        encoding="utf-8")
    print(f"built {out} — {len(rows)} commands")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
