# The daily routine: Claude Code, Cline, Aider backup

The owner works with Claude Code, Cline, and Aider on this repository (2026-11-11: Cline with
Nemotron 3.5 Super VL is the primary prototype tool; Aider is the backup). No tool remembers another's session:
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
| Cline | VS Code on the PC, using the owner's free Nemotron 3.5 Super VL option | The primary first-pass implementer for researched prototypes and work orders on local `main`; rebuilds the offline HTML and runs the required checks. |
| Claude Code, local | `C:\World-BIM-platform\BIM-Personal`, run `claude` in PowerShell | Research, phase specs, difficult design or debugging, and review/refinement of Cline's prototype against the research and task criteria. Sends bounded bulk work to Qwen. |
| Claude Code, cloud | The Claude app or claude.ai/code | Work away from the PC, research, watching PRs and fixing CI, a second task in parallel. |
| Aider (backup) | VS Code's terminal on the PC, run `aider` in the repo | Fallback when Cline is unavailable or the owner asks to switch. Uses the same `main` rules; ships only through `tools/gate.py`. |
| Qwen 2.5 Coder 14B | Ollama, `http://localhost:11434/v1`, model `qwen2.5-coder:14b` | Aider's model and the subcontractor local Claude sends bulk work to (`tools/local_llm.py`). Only reachable from the PC. |

Local and cloud Claude share one usage limit (`/usage` shows it). Cline's free model option, Aider
and Qwen do not use that Claude limit. Aider and Claude share the one Qwen model: keep Aider on
`qwen2.5-coder:14b` while Claude delegates, or Ollama swaps models (about 9 GB each) and every call
waits for a reload.

## The four rules

1. **One branch, one tool.** Two tools never work on the same branch at the same time.
2. **Only the gate pushes main.** Cline works on `main` and ships a finished `[Cline]` work order with
   `python3 tools/gate.py ship <phase> <id>` (the owner, 2026-11-13), which pushes only when every check
   passes. Nothing else is pushed to `main` by hand; Aider's work goes through the same gate. Claude's
   own work still goes on `claude/` branches with a draft PR.
3. **Pull before starting** on the PC only when local `main` has no unpushed prototype commits. Never
   reset, rebase or discard local prototype work to match GitHub.
4. **The repo is the memory.** What the next session needs goes in `PIPELINE.md`, the code, or the PR.

## Switching

- **Leaving a Claude feature branch:** `/finish` (it pushes the branch). In the cloud: "continue on branch X".
- **A Cline work order:** when the gate passes, `tools/gate.py ship` pushes it; unfinished work stays as
  checkpoint commits on local `main`; do not run `/finish` on it. Claude audits
  what shipped in batches (`/audit`).
- **An Aider fallback:** use it only when Cline is unavailable or the owner asks, then leave a diff for
  review. Do not run Aider and Cline concurrently.
- **Two tasks at once:** the second one in the cloud, on its own branch.

## Aider backup

The repo carries Aider's settings, so `aider` in the repo root needs no flags. Aider is not the normal
phase implementer:

- `.aider.conf.yml`: the model (`ollama_chat/qwen2.5-coder:14b`, with `OLLAMA_API_BASE` set), the
  `diff` edit format (small search/replace edits, never whole files), no auto-commits, and
  `AIDER_CONVENTIONS.md` read on every session.
- `AIDER_CONVENTIONS.md`: the repo's rules in short (edit `src/`, never `canvas_v10.html` or the
  generated import/export lines, ES5, no dependencies, no emojis, backup-only use on local `main`).
- `.aiderignore`: what Aider never maps or edits (the build output, `runtime/`, `vendor/`, the
  SketchUp reader, fixtures, the engineering log).

A session: first ensure Cline is not using the checkout. Work on local `main` only, and use Aider only
when the owner requests the fallback or Cline is unavailable. Follow the same source, build, and test
rules as Cline. Aider does not auto-commit or push.

The `pending_aider.py` hook and review-aider skill remain for legacy or explicitly requested Aider
work. They do not move Cline's local-main prototype to another branch or publish it.

## Building a phase with work orders

From V175 on, Claude researches and writes the spec, tests and ordered work list. Cline makes the
first implementation pass from those materials on local `main`, completing each task without
deliberate throw stubs. It runs the required checks before rebuilding `canvas_v10.html`; until then,
the existing file remains the last usable build. When `tools/gate.py check` passes, `ship` pushes it
to `main` (`.clinerules/workflows/ship-task.md`); Claude audits shipped work in batches (`/audit`)
instead of reviewing each task before it can land.
If Cline is unavailable, Aider may take over one task at a time under the same rules.

Work orders are marked `[Cline]`; anything that requires Claude's research or judgment is marked
`[Claude]`. Complete the first open `[Cline]` task in order and mark it done only after its required
checks pass. See `docs/work-orders/README.md`.

After a usable task or coherent group passes its required checks, make a local checkpoint commit so
the last known-good prototype is recoverable. Only `tools/gate.py ship` pushes it.

## This PC's setup (2026-11-08)

Git 2.56, Node 26, Python 3.13 (with a `python3.exe` copy beside `python.exe`), TypeScript 5.9.3
installed globally (the module check needs it), PowerShell execution policy `RemoteSigned` for the user.
The clone has `core.autocrlf false` and `core.eol lf`: a CRLF checkout fails every unit test.
