---
name: ship-task
description: Complete one open Cline work order end to end, including tests, gate checks, progress updates, commit, and push. Use when the owner invokes /ship-task or asks Cline to take the next work order.
---

# Ship one work order

This skill owns the full task lifecycle. Do not report a task complete when only its code or tests are complete.
It is complete only after `tools/gate.py ship` succeeds and the gate's commit is pushed to `main`.

## Select the task

- `/ship-task` with no arguments: take the first open `[Cline]` task from `docs/work-orders/QUEUE.md`.
- `/ship-task v178 WO-01`: take the named task.
- Work on one task at a time. Ship it before starting another. Continue to another task only when the owner
  explicitly asks for a batch.

## Complete and ship

1. Check `git status` and confirm the branch is `main`. If there are changes you cannot explain, stop and tell the
   owner. Do not overwrite or discard existing work.
2. Run `git pull --ff-only origin main` when local `main` has no unpushed commits. If it fails, continue only if the
   gate can safely merge `origin/main` at ship time.
3. Read the selected task block in `docs/work-orders/<phase>/TASKS*.md`, its referenced SPEC section, and its named
   tests. Inspect the current target file and locate the named function before editing. If it already exists, replace
   its body in place; never append a second definition or duplicate surrounding code. If it does not exist, add it once
   at the instructed location. After editing, inspect the diff and confirm the named function has exactly one
   definition in `src/js`.
4. Implement only the task's named functions and files. Follow the task's constraints, use ES5, and do not weaken or
   remove tests. Keep the patch limited to the requested function; do not copy or regenerate the whole file.
5. Run the task's exact test command and `node --check` on every changed JavaScript file. Review the diff for duplicate
   declarations, malformed braces, and unrelated changes. Fix failures, then run:

       python3 tools/gate.py check <phase> <id>

6. **If `check` passes, immediately run `ship`; do not stop, ask for approval, or report success before this step:**

       python3 tools/gate.py ship <phase> <id>

   This rebuilds `canvas_v10.html`, rechecks the task, ticks its `[Cline]` checkbox, appends to
   `docs/work-orders/<phase>/GATE-LOG.md`, commits, merges `origin/main`, and pushes `main`. Never commit or push
   manually. Do not use `--dry-run` unless the owner explicitly requests a dry run.
7. Confirm the gate reported a commit and successful push, and that the task is ticked and logged. If the gate fails,
   a merge conflicts, or the push fails, do not say the task shipped; report the exact failure and stop.
8. Report the task ID, checks, commit hash, and push result. Then stop unless the owner requested more tasks.

## Failure handling

- Allow at most two focused fix attempts for a failure. Then preserve the work and report the failing lines.
- Skip `[Claude]` tasks and protected paths.
- If existing code passes its task checks but the gate cannot record it without a code change, stop and report that;
  do not invent a code edit.
- Multiple task IDs may be passed to `gate.py ship`, but prefer one task per ship so each completion is recorded
  immediately.

## Gate options

- `--no-llm`: skip the local model's second opinion.
- `--strict-llm`: make a local-model CONCERN fail the gate.
- `--dry-run`: ticks and logs without committing or pushing; only use when the owner requests it.
