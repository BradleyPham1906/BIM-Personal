# Ship a work order (Cline)

Run this as `/ship-task.md <phase> <id>`, for example `/ship-task.md v175c WO-01`. With no arguments, take
the first open `[Cline]` task listed in `docs/work-orders/QUEUE.md`.

The gate (`tools/gate.py`) is the reviewer. When it passes, the work goes to `main` on GitHub with no
wait for Claude. Claude audits shipped work later, in batches. You do not judge your own work: the gate does.

## Steps

1. `git status`. Be on `main`. If there are changes you cannot explain, stop and tell the owner.
2. `git pull --ff-only origin main` when local `main` has no unpushed commits. If it fails, carry on:
   the gate merges `origin/main` itself at the end.
3. Read the task block in `docs/work-orders/<phase>/TASKS*.md`, the part of `SPEC.md` it points to, and
   the test cases named after the task. Read each file once.
4. Implement the task: only the file(s) it names, only the function(s) it names. ES5 (`var`, `function`).
   Use only the names listed under **May use**. Never edit a test you did not write for this task,
   `SPEC.md`, the `import`/`export` lines, or `canvas_v10.html`.
5. Run the task's own tests (the command in the TASKS file). Fix until they pass.
6. Run the gate without shipping:

       python3 tools/gate.py check <phase> <id>

   Each `FAIL` line says what is wrong. Fix it. Never get past a FAIL by weakening a test, moving code
   to another file, or deleting a check: the gate catches those, and they are against the rules.
7. When `check` says PASSED:

       python3 tools/gate.py ship <phase> <id>

   It rebuilds `canvas_v10.html`, runs every check again, ticks the task, writes
   `docs/work-orders/<phase>/GATE-LOG.md`, commits, merges `origin/main` and pushes `main`.
8. Report in four lines: the task, the files changed, the gate's result (and the local model's
   verdict), the commit. Then go to the next open `[Cline]` task in the queue, unless the owner said one task.

## When it fails

- Two fix attempts per failure, at most. Then stop: leave the work in place (do not reset or discard),
  and report the `FAIL` lines. Claude takes it from there.
- `ship` says the merge with `origin/main` conflicts or fails: it has undone the merge and pushed nothing.
  Report it and stop; that is Claude's.
- A task marked `[Claude]`, or one the gate calls protected: skip it, take the next `[Cline]` task.
- Several small tasks of the same file may ship together: `python3 tools/gate.py ship v175c WO-03 WO-04`.

## Options

- `--no-llm`: skip the local model's second opinion (Ollama down, or to save time).
- `--strict-llm`: a CONCERN from the local model fails the gate instead of only flagging it.
- `--dry-run`: tick and log, but no commit and no push.
