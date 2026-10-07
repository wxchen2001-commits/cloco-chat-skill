# cloco-chat-skill

**Run the full [cloco](https://github.com/jfimbett/cloco) economics-paper pipeline inside the Claude chat (claude.ai and the Claude desktop app) — no terminal needed.**

From a research idea to a submission-ready empirical paper: literature, data, identification, analysis, drafting, blind referee review and an AEA-style replication audit. Forty-one commands and twenty-one specialist agents, packaged as a single skill you upload once.

[中文说明见下方](#中文说明)

---

## Why this exists

[cloco](https://github.com/jfimbett/cloco) by Juan F. Imbet is a multi-agent, quality-gated research pipeline for economics papers. It is built as a **Claude Code project template**: its commands, agents and hooks only work when you open the cloned folder in the Claude Code terminal.

This repository repackages it as **one Agent Skill** for the chat interface:

- all 41 commands become workflow files the chat Claude follows;
- the 21 agents (econometrics critic, identification critic, blind peer referees, replication verifier, …) run as sub-agents;
- the helper scripts (project dashboard, data registry, git secrets audit) run against your project folder;
- the Claude Code hooks (research journal, secrets guard, quality gate, path guard) become explicit steps the skill tells Claude to perform.

If you live in the terminal, use upstream cloco directly. If you work in the chat, use this.

## Install (claude.ai / Claude desktop)

1. Turn on code execution: **Settings → Capabilities**.
2. Download **[`dist/cloco.zip`](dist/cloco.zip)** — do not unzip it.
   (GitHub's green "Download ZIP" button will *not* work: the uploaded folder must be named exactly `cloco`.)
3. Go to **Customize → Skills** (claude.ai/customize/skills) → **+** → **Create skill** → **Upload a skill**, and choose `cloco.zip`.

See Anthropic's guide: [Use Skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Use

Just name the command in a chat message:

```
cloco /scout Does extreme heat in China raise natural-gas futures volatility?
cloco /interview-me            ← turn an idea into a research spec
cloco /find-data               ← data discovery + quality critique
cloco /identify                ← identification strategy + critic
cloco /econometrics-check paper/main.tex
cloco /review-paper            ← two blind referees + editor decision
cloco /audit-replication       ← 10-check pre-submission audit
```

Claude reads the matching workflow, sets up or reopens your project folder (`paper/`, `code/`, `data/`, `quality_reports/`), and runs the agents that workflow calls for. If your project lives on your own computer, connect the folder in the desktop app and Claude works on it there.

## Commands

| Stage | Commands |
|---|---|
| Idea | `/scout` `/research-ideation` `/interview-me` `/revive` `/new-project` |
| Discovery | `/lit-review` `/find-data` `/discovery` `/data-profile` `/data-registry` `/wrds` |
| Strategy | `/identify` `/pre-analysis-plan` `/theory-model` `/structural-estimation` `/lean-verify` |
| Analysis | `/data-analysis` `/review-code` `/econometrics-check` |
| Writing | `/draft-paper` `/humanizer` `/proofread` `/validate-bib` `/target-journal` |
| Review | `/review-paper` `/paper-excellence` `/respond-to-referee` |
| Submission | `/audit-replication` `/data-deposit` `/submit` |
| Talks | `/create-talk` `/compile-latex` `/visual-audit` `/deploy` |
| Project | `/setup-project` `/pipeline-status` `/journal` `/learn` `/commit` `/git-steward` `/context-status` |

Full one-line descriptions are in [`cloco/SKILL.md`](cloco/SKILL.md#6-command-index).

## What changed from upstream

| Upstream (Claude Code) | This skill (chat) |
|---|---|
| `.claude/skills/<cmd>/SKILL.md` | `cloco/workflows/<cmd>.md` |
| `.claude/agents`, `.claude/rules`, `.claude/scripts` | bundled in the skill; paths rewritten to `CLOCO/...` |
| Project state in `.claude/` (lessons, plans, state) | still in your project's `.claude/` folder |
| Hooks run automatically | the skill instructs Claude to do them by hand (journal, secrets audit before commits, quality gate ≥ 80, path guard, compile-before-done, session log, lessons) |
| Agents launched with the Task tool | launched as chat sub-agents with the agent file as their brief |
| Assumes WRDS + Dropbox | also covers browser downloads and terminal exports (CSMAR, Wind, Choice, Bloomberg, exchanges) |
| `dashboard.py` looks for `git_tools.py` in the project | looks next to itself |

Agent, rule and script contents are otherwise unchanged. The upstream commit this is built from is recorded in [`cloco/reference/SOURCE.md`](cloco/reference/SOURCE.md).

## Limitations

- Hooks are **instructions, not enforcement**: in chat nothing physically blocks a commit; Claude follows the rules in the skill.
- Terminal-only features (status line, `/context-status`, `make watch`) are skipped.
- `/lean-verify` and the Lean steps of `/theory-model` need a ~5 GB Lean + Mathlib install; Claude asks before running it.
- Multi-agent commands use more of your usage allowance than a single chat reply.
- Like any research assistant, it drafts; you are the author. Check every result, citation and declaration before you submit, and follow your journal's AI-use policy.

## Rebuild from upstream

```bash
./build.sh            # clones jfimbett/cloco, repackages it into cloco/, writes dist/cloco.zip
```

## Credits and licence

- **cloco** — Juan F. Imbet, https://github.com/jfimbett/cloco. All the research-pipeline design, agents, rules and scripts are his work. Its README declares the MIT licence; at the time of packaging the repository did not include a LICENSE file.
- **Chat repackaging** — Wenxuan (Arthur) Chen ([@wxchen2001-commits](https://github.com/wxchen2001-commits)).

Released under the MIT licence; see [LICENSE](LICENSE) and [NOTICE](NOTICE). If this is useful, please star **both** this repository and [upstream cloco](https://github.com/jfimbett/cloco).

---

## 中文说明

**在 Claude 聊天框（网页版和桌面端）里直接运行完整的 [cloco](https://github.com/jfimbett/cloco) 经济学论文流水线，不需要命令行。**

cloco 是 Juan F. Imbet 开发的多智能体论文流水线，覆盖选题、文献、找数据、识别策略、实证分析、写作、盲审和复现审计。原版是 Claude Code 项目模板，只能在终端里用。这个仓库把它打包成**一个 skill**，上传一次就能在聊天框里调用全部 41 个命令和 21 个专家 agent。

### 安装

1. 打开代码执行：**Settings → Capabilities**。
2. 下载 **[`dist/cloco.zip`](dist/cloco.zip)**，不要解压。注意不能用 GitHub 绿色按钮的 "Download ZIP"，因为上传的文件夹名必须正好是 `cloco`。
3. 进入 **Customize → Skills**，点 **+ → Create skill → Upload a skill**，选择 `cloco.zip`。

### 使用

在聊天里直接说命令即可，例如：

```
cloco /scout 中国极端高温是否推高天然气期货波动
cloco /econometrics-check paper/main.tex
cloco /audit-replication
```

### 和原版的区别

- 原版自动运行的 hook（研究日志、提交前查密钥、质量分门槛等）改为由 skill 规定 Claude 手动执行。
- agent 以聊天子 agent 的方式运行。
- 增加了国内常用数据源的说明：CSMAR、Wind、Choice 等可以通过浏览器下载或终端导出，不依赖 WRDS。

### 致谢

流水线的设计、agent、规则和脚本全部来自 Juan F. Imbet 的 [cloco](https://github.com/jfimbett/cloco)。觉得有用的话，请同时给本仓库和原版 cloco 点个 Star。
