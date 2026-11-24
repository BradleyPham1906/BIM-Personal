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
- **A batch of phases is still one phase at a time:** implement a phase, ship it, then start the next. Never leave
  two phases' changes in the working tree together: the gate sees every changed file and refuses them all.

## Complete and ship

0. Run `python3 tools/handoff.py status` (Windows: `python`). If work is parked from another machine, run
   `python3 tools/handoff.py resume` first and ship that work before starting anything new.
1. Check `git status` and confirm the branch is `main`. If there are changes you cannot explain, stop and tell the
   owner. Do not overwrite or discard existing work.
2. Run `git pull --ff-only origin main` when local `main` has no unpushed commits. If it fails, continue only if the
   gate can safely merge `origin/main` at ship time.
3. Read the selected task block in `docs/work-orders/<phase>/TASKS*.md`, its referenced SPEC section, and its named
   tests. Before editing, run `git rev-parse --show-toplevel` and verify the target exists under that root; use the
   resulting absolute path for scripted writes. Locate the named function in the current file. If it already exists,
   replace only its body in place; never append a second definition, use stale line numbers, or regenerate the whole
   file.
4. Implement only the task's named functions and files. Follow the task's constraints, use ES5, and do not weaken or
   remove tests. After each write, inspect `git diff --check` and the target's full diff, confirm the named function
   has exactly one definition, and run `node --check` on the target. If any edit command fails (including a missing
   path or failed write), stop immediately: verify the current directory and repository root, inspect the actual diff,
   and repair from the current file contents only. Never claim the functions are correct while cleanup errors or
   unexplained lines remain; preserve the diff and report the failure if it cannot be repaired safely.
5. Run the task's exact test command and `node --check` on every changed JavaScript file. Review the diff for numbered
   editor-gutter text (`^\s*[0-9]+\s+\|`), duplicate declarations, malformed braces, and unrelated changes. Fix
   failures, then run:

       python3 tools/gate.py check <phase> <id>

6. **If `check` passes, immediately run `ship`; do not stop, ask for approval, or report success before this step:**

       python3 tools/gate.py ship <phase> <id>

   This rebuilds `canvas_v10.html`, rechecks the task, ticks its `[Cline]` checkbox, appends to
   `docs/work-orders/<phase>/GATE-LOG.md`, commits, merges `origin/main`, and pushes `main`. Never commit or push
   manually. Do not use `--dry-run` unless the owner explicitly requests a dry run.
7. Confirm the gate reported a commit and successful push, and that the task is ticked and logged. If the gate fails,
   a merge conflicts, or the push fails, do not say the task shipped; report the exact failure and stop.
8. Report the task ID, checks, commit hash, and push result. Then stop unless the owner requested more tasks.

This workflow ends with the normal response; do not invoke a tool named `finish` or the separate Claude `/finish`
routine for a Cline work order.

## Leaving a machine (the owner, 2026-11-24)

The owner moves between a MacBook, the Beelink at home and the office PC. Unshipped work stays on the machine
it was done on, where the next machine cannot see it. When the owner says they are stopping or switching
machines and a task is not shipped, run `python3 tools/handoff.py park` (Windows: `python`): it puts the work
on the `wip/park` branch on GitHub and leaves this machine clean. Never push it any other way.

## Stop rules (the owner, 2026-11-24)

These override anything else in this skill. When one applies, stop, keep the work, and report the gate's exact
`FAIL` lines to the owner. Do not try another way round.

- **Never edit a protected path**, whatever the reason: `tools/` (the gate included), `.cline/`, `.clinerules/`,
  `.claude/`, `.github/`, `src/index.html`, `src/js/engine/core/`, `src/js/engine/history/` (except a file
  `PROTECTED_EXEMPT` in `tools/gate.py` lists), `rendered-core.js`, `runtime/`, `vendor/`, `docs/dev/`, `CLAUDE.md`,
  `package.json`, `tests/unit/helpers/`, `tests/fixtures/`, a `SPEC*.md`. If you already did, undo it with
  `git checkout -- <path>`.
- **`spec error (Claude's, not yours)`**: the task itself is wrong. Stop. Do not move the code to another file.
- **`origin/main has a newer gate or skill`**: run the command the gate prints, then run the gate again. This is
  the one failure you fix yourself.
- **`outside the task's scope`** because another phase's work is in the tree: run the three commands the gate
  prints (stash the other files, ship, `git stash pop`). If the stray file belongs to no open task, stop.
- **Never** move a function to a different file, rename it, change a task's `**Files:**` line, commit by hand, or
  push by hand to get a task through.

## Failure handling

- Allow at most two focused fix attempts for a failure. Then preserve the work and report the failing lines.
- Skip `[Claude]` tasks.
- If existing code passes its task checks but the gate cannot record it without a code change, stop and report that;
  do not invent a code edit.
- Multiple task IDs may be passed to `gate.py ship`, but prefer one task per ship so each completion is recorded
  immediately.

## Gate options

- `--no-llm`: skip the local model's second opinion.
- `--strict-llm`: make a local-model CONCERN fail the gate.
- `--dry-run`: ticks and logs without committing or pushing; only use when the owner requests it.
