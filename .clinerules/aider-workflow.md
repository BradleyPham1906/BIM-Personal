---
paths:
  - "src/**"
  - "tests/**"
  - "tools/**"
  - "docs/work-orders/**"
---

# Local prototype workflow (Cline primary, Aider backup)

- Cline with the owner's free Nemotron 3.5 Super VL option is the primary first-pass implementer. Cline may read, search, edit project files, and run the required checks. Aider is a backup only when Cline is unavailable or the owner asks to switch.
- Prototype on the local `main` branch, one tool at a time. Before starting, check `git status`. If the checkout is not `main`, or has unexplained changes, stop and tell the owner rather than switching branches or overwriting work.
- Keep each task bounded by the phase research, `SPEC.md`, and `TASKS.md`. Implement complete behavior; do not add deliberate `WO-` throw stubs to `main`. Work through `[Cline]` tasks in their written order (including V175a's WO-06 before WO-05) and mark one `[x]` only after its required checks pass.
- Make a local checkpoint commit after each verified task or coherent task group so the last usable state can be restored.
- Ship a finished `[Cline]` work order with the gate, as `.clinerules/workflows/ship-task.md` says: `python3 tools/gate.py check <phase> <id>`, then `python3 tools/gate.py ship <phase> <id>`, which commits and pushes `main` when every check passes (the owner, 2026-11-13). Push nothing any other way: no `git push` by hand, no PR, no work outside a work order's scope. The gate's FAIL means fix or stop, never work around it.
- After a change under `src/`, run the required checks before rebuilding `canvas_v10.html` with `python3 tools/build_app.py`; never edit the generated HTML by hand. Until then, the existing HTML remains the last usable build. The owner uses this local file, not the hosted app, to try updates.
- Follow `CLAUDE.md` and `docs/dev/CLAUDE_INSTRUCTIONS.md` for the source, build, and test contracts. Follow Rule #1 in `CLAUDE.md` exactly: do not run tests beyond the table or browser/full-regression checks without the owner's approval.
- If a required check fails, stop adding features and make up to two focused fix attempts. If still failing, leave the last checkpoint intact, preserve the diff, and report the failing lines and unresolved issue; do not reset or discard work.
- If the owner asks to use Aider, or Cline is unavailable, Aider may take the current task on the same local `main` checkout. Do not run Cline and Aider concurrently or create a separate Aider branch for this prototype workflow.
- Keep exploration focused. Read each required task/spec/source file at most once per task; do not scan unrelated parts of the repository.
- At the end of each work order, report the task completed, files changed, checks run, local checkpoint, and anything unresolved.
