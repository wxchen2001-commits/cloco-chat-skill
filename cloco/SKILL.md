---
name: cloco
description: Run the cloco economics-paper pipeline (jfimbett/cloco) in chat — idea, data, identification, analysis, drafting, referee review, replication audit, submission. Use when the user says "cloco" or names one of its commands, e.g. /find-data, /identify, /econometrics-check, /draft-paper, /audit-replication, /submit.
---

# cloco in chat

This skill packages the cloco research pipeline (https://github.com/jfimbett/cloco by Juan F. Imbet; its README declares the MIT licence, though the repository ships no LICENSE file — see `reference/SOURCE.md`) so it runs inside the Claude chat instead of a Claude Code project. The original commands live in `workflows/`, the specialist agents in `agents/`, the shared rules in `rules/`, helper scripts in `scripts/`, templates in `templates/`, and the original project instructions in `reference/CLAUDE.md`.

## 1. Set up the two locations

**CLOCO** — this skill's own folder, the directory that contains this SKILL.md. If its path is not obvious, find it once:
`find / -maxdepth 6 -type d -path '*cloco/workflows' 2>/dev/null | head -1` (CLOCO is its parent). Everything in CLOCO is read-only.

**PROJECT** — the paper's working folder, where `paper/`, `code/`, `data/`, `quality_reports/` and the project's own `.claude/` state live.
- If the user's project is on their computer and a folder is connected, PROJECT is that folder and you work in it with the device shell (`device_bash`, mounted under `$HOME/mnt/<folder>`). Bring files into the workspace only for steps the device shell cannot do.
- Otherwise PROJECT is a folder in the workspace (e.g. `./<slug>/`), delivered to the user at the end.
- New project: create `paper/ code/ data/raw data/processed quality_reports/ .claude/` in PROJECT, and copy `CLOCO/templates/` into `PROJECT/templates/` and `CLOCO/rules/domain-profile.md` into `PROJECT/.claude/rules/domain-profile.md`. Copy `CLOCO/templates/LESSONS.md` to `PROJECT/.claude/lessons/LESSONS.md`, `templates/registry.json` to `PROJECT/data/registry.json`, `templates/env.example` to `PROJECT/.env.example`, `templates/gitignore` to `PROJECT/.gitignore`, `templates/data_paths.py` and `data_paths.R` to `PROJECT/code/utils/`. Copy `templates/lean/` to `PROJECT/lean/` only if the paper has formal theory.

## 2. How to read the workflow files

The files were written for Claude Code. Translate as you go:

| In the workflow text | Do this in chat |
|---|---|
| `/command args` | Read `CLOCO/workflows/<command>.md` in full, set `$ARGUMENTS` to whatever the user typed after the command, and follow the steps. Ignore the frontmatter fields `allowed-tools`, `disable-model-invocation`, `argument-hint`. |
| `CLOCO/scripts/<x>.py ...` | Run as `CLAUDE_PROJECT_DIR="<PROJECT>" python3 "<CLOCO>/scripts/<x>.py" ...`. All scripts honour `CLAUDE_PROJECT_DIR`. Use `python3`; never write into CLOCO. |
| `CLOCO/rules/<x>.md` | If `PROJECT/.claude/rules/<x>.md` exists, it overrides the packaged one; otherwise read the packaged one. Project-specific edits (domain profile, etc.) go to the PROJECT copy. |
| `.claude/state`, `.claude/plans`, `.claude/specs`, `.claude/lessons`, `.claude/agent-memory`, `.claude/sessions`, `.claude/SESSION_REPORT.md` | These are project state: they live under `PROJECT/.claude/`. Create them when first needed. |
| `templates/<x>.md` | `PROJECT/templates/<x>.md` if present, else `CLOCO/templates/<x>.md`. |
| "Dispatch / launch / delegate to the `<name>` agent (Task tool)" | Spawn a subagent with the Agent tool (general-purpose). Its prompt is: the full body of `CLOCO/agents/<name>.md` (below its frontmatter), then the task from the workflow, then the absolute paths of every file it must read (PROJECT files and the CLOCO rules/agents it references), and whether PROJECT is reached through the device shell. The user invoking a cloco command that names an agent is the request to run that agent. Relay what matters from its report; never pass its report off as your own work. |
| Agent "mode: standalone / pipeline" | Same as the original. The research-orchestrator's routing is done by you, following `CLOCO/agents/research-orchestrator.md` and `CLOCO/rules/orchestrator-protocol.md`. |
| `.claude/settings`, status line, terminal titles, `/context-status`, `make watch` | Claude Code only. Skip, and say so briefly if the user asked for them. |

## 3. Hooks: do these by hand

In Claude Code these ran automatically. In chat you are the hook:

1. **Research journal** — after every agent report, append one entry to `PROJECT/quality_reports/research_journal.md` in the format of `CLOCO/rules/research-journal.md` (agent, score if any, one-line verdict, report path).
2. **Secrets guard** — before any `git commit`, `git push` or `git add` of a sensitive path in PROJECT, run `CLAUDE_PROJECT_DIR="<PROJECT>" python3 "<CLOCO>/scripts/git_tools.py" audit`. Any critical/high finding (credentials, `.env`, `.pgpass`, keys, data files, oversized blobs) stops the commit until the user decides.
3. **Quality gate** — before a commit, if `PROJECT/quality_reports/` has a quality report, its latest score must be ≥ 80 (see `CLOCO/rules/quality-gates.md`); otherwise tell the user and commit only if they say so.
4. **Path guard** — when writing analysis code under `code/`, `replication/` or `explorations/`, no hard-coded machine paths (home dirs, Dropbox, drive letters); route data paths through `code/utils/data_paths.py` and `data/registry.json`.
5. **Verify reminder** — after editing `.tex`, `.qmd` or `.R`/`.py` analysis files, compile or run them before calling the task done.
6. **Session log** — at the end of a substantial session, write a log to `PROJECT/quality_reports/session_logs/` using `templates/session-log.md`.
7. **Lessons** — when the user corrects you, record it in `PROJECT/.claude/lessons/LESSONS.md` per `CLOCO/rules/lessons-protocol.md`, and read that file at the start of every cloco session.

## 4. Starting a session

1. Locate CLOCO and PROJECT (section 1).
2. Read `CLOCO/reference/CLAUDE.md` (pipeline overview), `PROJECT/.claude/lessons/LESSONS.md` and the project's domain profile, if they exist.
3. If PROJECT already has state, run `CLAUDE_PROJECT_DIR="<PROJECT>" python3 "<CLOCO>/scripts/dashboard.py"` and report phase, last action and next command in two or three lines — this replaces the session-welcome banner.
4. Then run the command the user asked for. If they named none, suggest the next command from the dashboard, or `/interview-me` for a new project.

## 5. Data outside WRDS, Lean, integrity

- **Data.** cloco assumes WRDS and Dropbox. For CSMAR, Wind, Choice, Bloomberg or exchange data, download through the user's browser (read the `chrome-browser` skill first; the user signs in and solves CAPTCHAs; list each file with size before downloading) or have the user export from the terminal. Register every file with `scripts/data_registry.py add`. WRDS (`/wrds`) works only if the user supplies credentials in `PROJECT/.env`; never type passwords yourself.
- **Lean / theory proofs** (`/lean-verify`, Lean steps in `/theory-model`, `/submit`): the first setup downloads about 5 GB. Ask before running `lean_tools.py setup`; for a purely empirical paper, skip them and say so.
- **Integrity.** Same as cloco's own rules: no fabricated data or citations, every number in the paper comes from code output, deviations from a pre-analysis plan are recorded. These outrank speed.

## 6. Command index

Each command is a file in `workflows/`. Read the file before running it; the line below is only for choosing.

- `/audit-replication` — Validate replication package by dispatching the replication-verifier agent in submission mode (checks 1-10).
- `/commit` — Stage, commit, create PR, and merge to main.
- `/compile-latex` — Compile a Beamer LaTeX slide deck with XeLaTeX (3 passes + bibtex).
- `/context-status` — Show current context status and session health. *(Claude Code only — skip in chat)*
- `/create-talk` — Generate academic presentations (Beamer .tex or Quarto RevealJS .qmd) by dispatching the storyteller agent (creator) and discussant agent (critic).
- `/data-analysis` — End-to-end data analysis dispatching Coder (main Claude) for implementation and Debugger agent for code review.
- `/data-deposit` — Prepare AEA Data Editor compliant replication package by dispatching Coder (main Claude) for package assembly and replication-verifier agent for validation.
- `/data-profile` — Automated profiling of a dataset that is already on disk — variable types, missingness, distributions, panel structure (unit × time, balance, duplicates), treatment va…
- `/data-registry` — Show, verify, and maintain the project's data registry (data/registry.json) — the committed map of where every dataset lives (Dropbox, project data/ folder, external d…
- `/deploy` — Render Quarto slides and sync to docs/ for GitHub Pages deployment.
- `/discovery` — Run the entire Discovery phase in one command from an existing research spec — literature review (librarian + editor) and data discovery (explorer + surveyor) in paral…
- `/draft-paper` — Draft academic economics papers by dispatching the economics-paper-writer agent.
- `/econometrics-check` — Causal inference design audit.
- `/find-data` — Data discovery and assessment dispatching the explorer agent (finder) and data-quality-surveyor agent (critic).
- `/git-steward` — Repository hygiene and GitHub workflow — audit that no credentials, data files, or oversized blobs are committed or in history; propose branches and worktrees for para…
- `/humanizer` — Strip AI writing patterns from text.
- `/identify` — Design identification strategy by dispatching the causal-strategist agent (proposer) and identification-critic agent (critic).
- `/interview-me` — Interactive interview to formalize a research idea into a structured specification with hypotheses and empirical strategy
- `/journal` — Regenerate the research journal timeline from quality reports and git history.
- `/lean-verify` — Machine-check the paper's formal results in Lean 4 + Mathlib. *(needs ~5 GB Lean install — ask first)*
- `/learn` — Extract reusable knowledge from the current session into a persistent skill. *(in chat: write the draft to `PROJECT/.claude/skills/`, then offer it to the user as a skill proposal so it becomes callable)*
- `/lit-review` — Structured literature search dispatching the academic-librarian agent for collection and academic-editor agent for coverage critique.
- `/new-project` — Full research pipeline from idea to paper.
- `/paper-excellence` — Multi-agent paper review dispatching econometrics-critic, debugger, academic-proofreader, and replication-verifier in parallel.
- `/pipeline-status` — Show the current research pipeline status for the active project, or display the pipeline guide for a specific project type.
- `/pre-analysis-plan` — Draft pre-analysis plans by dispatching the causal-strategist agent in PAP mode.
- `/proofread` — Manuscript proofreading dispatching the academic-proofreader agent.
- `/research-ideation` — Generate structured research questions, testable hypotheses, and empirical strategies from a topic or dataset
- `/respond-to-referee` — Structure point-by-point referee responses using the revision-protocol routing.
- `/review-code` — Code review dispatching the Debugger agent in standalone mode (categories 4-12 only).
- `/review-paper` — Full manuscript review dispatching 2 blind blind-peer-referee agents and the academic-editor agent for editorial decision.
- `/revive` — Rescue an old or abandoned working paper.
- `/scout` — Fast go/no-go triage of a research idea BEFORE committing to the full pipeline.
- `/setup-project` — Project setup assistant.
- `/structural-estimation` — Design and implement structural estimation strategies by dispatching the structural-estimation-expert agent.
- `/submit` — Final submission verification gate.
- `/target-journal` — Journal targeting dispatching the academic-editor agent in journal-selection mode.
- `/theory-model` — Develop formal theoretical models in economics or finance by dispatching the econ-finance-theorist agent.
- `/validate-bib` — Validate bibliography entries against citations in all lecture files.
- `/visual-audit` — Visual layout audit of Beamer (.tex) or Quarto (.qmd) slide decks.
- `/wrds` — Explore and pull data from WRDS (CRSP, Compustat, IBES, TRACE, Dealscan, BoardEx, Audit Analytics, ...) directly from the session when the author has credentials — lis…
