# The daily routine: Claude Code, the cloud, Aider

The owner works with three tools on this repository (2026-11-08; Aider and Ollama replaced Bionic as
the local tools 2026-11-11). No tool remembers another's session:
the repository is the memory. Git carries the work between them, and `docs/dev/PIPELINE.md` says
where the project stands.

## The whole routine

    open the tool  ->  /start  ->  work  ->  /finish

`/start` and `/finish` are this repository's own commands (`.claude/skills/start/`, `.claude/skills/finish/`).
They work in Claude Code on the PC and in a cloud session. The owner only has to remember those two
words; Claude does the steps and says what it found.

## Who does what

| Tool | Where | For |
|---|---|---|
| Claude Code, local | `C:\World-BIM-platform\BIM-Personal`, run `claude` in PowerShell | The main workbench: phases, features, bugs, build and tests, PRs. Sends bulk work to Qwen. |
| Claude Code, cloud | The Claude app or claude.ai/code | Work away from the PC, research, watching PRs and fixing CI, a second task in parallel. |
| Aider | VS Code's terminal on the PC, run `aider` in the repo | Quick edits, questions about the code, private or offline work. Free. |
| Qwen 2.5 Coder 14B | Ollama, `http://localhost:11434/v1`, model `qwen2.5-coder:14b` | Aider's model, and the subcontractor local Claude sends bulk work to (`tools/local_llm.py`). Only reachable from the PC. |

Local and cloud Claude share one usage limit (`/usage` shows it). Aider and Qwen do not use it.
Aider and Claude share the one Qwen model: keep Aider on `qwen2.5-coder:14b` while Claude delegates,
or Ollama swaps models (about 9 GB each) and every call waits for a reload.

## The four rules

1. **One branch, one tool.** Two tools never work on the same branch at the same time.
2. **Push before switching** between the PC and the cloud: they see each other only through GitHub.
3. **Pull before starting** on the PC, so no work is done on an old copy.
4. **The repo is the memory.** What the next session needs goes in `PIPELINE.md`, the code, or the PR.

## Switching

- **Leaving the PC mid-task:** `/finish` (it pushes the branch). In the cloud: "continue on branch X".
- **An Aider edit:** just make it and close Aider; the next Claude session reviews it (see "Aider" below). Then in either Claude:
  "review the diff on branch X against main" before the PR is merged.
- **Two tasks at once:** the second one in the cloud, on its own branch.

## Aider

The repo carries Aider's settings, so `aider` in the repo root needs no flags:

- `.aider.conf.yml`: the model (`ollama_chat/qwen2.5-coder:14b`, with `OLLAMA_API_BASE` set), the
  `diff` edit format (small search/replace edits, never whole files), no auto-commits, and
  `AIDER_CONVENTIONS.md` read on every session.
- `AIDER_CONVENTIONS.md`: the repo's rules in short (edit `src/`, never `canvas_v10.html` or the
  generated import/export lines, ES5, no dependencies, no emojis, branch `aider/<task>`).
- `.aiderignore`: what Aider never maps or edits (the build output, `runtime/`, `vendor/`, the
  SketchUp reader, fixtures, the engineering log).

A session: `aider`, `/add` the one or two files the task touches (or ask Aider which ones), and ask
for the change. Then close Aider. Nothing else: no branch, no build, no commit.

The review is automatic. When a Claude session opens, a hook (`.claude/settings.json` runs
`tools/pending_aider.py`) finds uncommitted changes and unmerged `aider/*` branches, with what was
asked of Aider (`.aider.chat.history.md`), and Claude runs the review-aider skill before anything
else: it moves the work to an `aider/<task>` branch, reviews and fixes it, rebuilds, runs the checks,
opens a PR, and asks the owner one question: "Merge it?". A forgotten review is impossible: the
notice repeats every session until the work is merged. A 14B model works best on one file and one
clear change at a time.

## Building a phase with work orders

From V175 on, Claude writes the spec, the hard code, the tests and a list of small tasks; Aider
fills in the tasks for free; Claude reviews and finishes. In VS Code, on the phase's branch:

    aider
    /read docs/work-orders/v175/SPEC.md docs/work-orders/v175/TASKS.md
    do the next unticked [Aider] task

Repeat "do the next task" until none is left; say "skip it" when one fails twice. Steps and rules:
`docs/work-orders/README.md`.

## This PC's setup (2026-11-08)

Git 2.56, Node 26, Python 3.13 (with a `python3.exe` copy beside `python.exe`), TypeScript 5.9.3
installed globally (the module check needs it), PowerShell execution policy `RemoteSigned` for the user.
The clone has `core.autocrlf false` and `core.eol lf`: a CRLF checkout fails every unit test.
