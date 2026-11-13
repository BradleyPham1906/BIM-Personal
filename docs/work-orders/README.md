# Work orders: Claude specifies, Cline builds the first pass

From V175 on (the owner, 2026-11-11), Claude researches and writes the phase spec, tests and ordered
tasks; Cline, using the owner's free Nemotron 3.5 Super VL option, builds the first usable prototype.
Claude later reviews and improves it against the research and task criteria. Aider is a backup only
when Cline is unavailable or the owner asks to switch.

## The folder

    docs/work-orders/
      _template/SPEC.md     copy for each phase
      _template/TASKS.md    copy for each phase
      v175/SPEC.md          the phase's spec and roadmap
      v175/TASKS.md         its work orders, ticked as they are done

The phase's tests live in `tests/unit/<area>.test.mjs`, where `npm test` finds them.

## How a phase runs

| Step | Who | What |
|---|---|---|
| 1. Research | Claude | As before (`docs/research/research-protocol.md`), the owner's decisions asked at the end. |
| 2. Spec | Claude | `vNNN/SPEC.md`: what the feature does, every file and function, inputs and outputs, edge cases, the order of the work. |
| 3. Tests and tasks | Claude | Write focused tests and `vNNN/TASKS.md`. Mark first-pass implementation tasks `[Cline]`; reserve `[Claude]` for decisions or work that should not be delegated. |
| 4. Build | Cline | On `main`, implement one task at a time from the research, spec and tests. Complete behavior; do not add deliberate throw stubs. |
| 5. Gate and ship | Cline | `python3 tools/gate.py check <phase> <id>`, fix every FAIL, then `ship`: it rebuilds `canvas_v10.html`, ticks the task, logs it in `GATE-LOG.md`, commits and pushes `main` (`.clinerules/workflows/ship-task.md`). No wait for Claude. |
| 6. Audit | Claude | In batches, not per task (`/audit`): read what shipped against the research and spec; fix, or reopen the task. Meanwhile Claude keeps `QUEUE.md` two phases ahead. Browser checks and full regression still require owner approval. |
| 7. Backup | Aider | Take over only when Cline is unavailable or the owner asks. Follow the same local-main, no-push and check rules. |

## Doing a task with Cline

In VS Code, on `main`, type `/ship-task.md` (the first open task in `QUEUE.md`) or
`/ship-task.md v175c WO-01`. Cline implements the task, runs the gate and ships it. If the gate still
fails after two focused fix attempts, it stops, preserves the diff and reports the FAIL lines.

## The gate (`tools/gate.py`)

The review Claude used to do by hand, as checks a script runs in seconds. It fails when:
- the task is not an open `[Cline]` task, or names no `src/` file or no test;
- a changed file is outside the task's files (its `**Files:**` line, else the paths in its block, else
  the TASKS file's opening paragraph; paths after "do not" / "not" are left out), or in a protected
  path (`core/`, `history/`, `rendered-core.js`, `tools/`, `.github/`, `runtime/`, `vendor/`,
  `src/index.html`, the rules and docs/dev);
- a test line is removed or changed (tests may only grow), a SPEC changes, or a TASKS file changes
  beyond its checkboxes;
- added code is not ES5, has an emoji, a `WO-` stub or `debugger`, touches import/export lines, or
  calls a `bim*` name declared nowhere in `src/`;
- more src lines are added than the task's `**Budget:**` (default 120);
- `node --check`, the task's own tests (at least one must run), `npm test` or `npm run check` fail.
Then the local model (Qwen, `tools/local_llm.py`) reads the task and the diff and answers PASS or
CONCERN. A CONCERN is logged and flagged for the audit; `--strict-llm` makes it a failure.

`ship` merges `origin/main` (never rebases); a conflict outside `canvas_v10.html`, or a failure after
the merge, undoes the merge and pushes nothing. CI runs on every push as before.

## The queue

`QUEUE.md` lists the phases whose `[Cline]` tasks are ready. Claude's job is to keep it two or more
phases ahead: research, the owner's decisions asked together, then SPEC, tests and TASKS for several
phases in one sprint, instead of one phase at a time behind Cline.

## Rules for writing work orders (Claude)

A model is more reliable on a small, exact task than on a vague one. Each work order:
- **one file, one function**, ideally under 40 lines of body;
- says **where**: the file and the function's name (it is already declared there);
- says **what**: inputs, output, and every edge case, in plain words, with an example input and its
  expected result;
- lists **the existing names it may use**, with their files; nothing else may be called;
- names **its test** and the command to run it;
- names **its files** (`- **Files:**`) and, when it should be small, a **budget** (`- **Budget:** N`):
  the gate allows nothing else;
- repeats the **don'ts** that matter for it (no other file, no import/export lines, ES5).

Anything that does not fit these rules is a `[Claude]` task. Score every task with `ROUTING.md`;
split one that scores 5 or more when its pieces would each score 4 or less.

## Keep the local prototype usable

Do not create `throw new Error('WO-NN: not built')` placeholders on `main`. Work orders are complete
implementation tasks, not invitations to land a temporarily broken skeleton. If a new feature is
unfinished, keep its controls unavailable or complete the bounded task before building a usable
prototype. Push only through `tools/gate.py ship`; never by hand.
