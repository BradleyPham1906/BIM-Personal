# Work orders: Claude designs, Aider types

From V175 on (the owner, 2026-11-11), a phase's build is split between Claude and Aider (Qwen 2.5 Coder
14B, local, free). Claude does the thinking and the hard code; Aider fills in the routine functions
Claude has laid out. The split saves Claude's usage without lowering quality, because tests decide
whether Aider's work is right, and Claude reviews it before anything is merged.

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
| 3. Skeleton | Claude | On the phase's branch: the hard parts written in full (engine logic, wiring across files, geometry, anything needing judgment); each routine function declared with its name, parameters and a comment saying exactly what it returns, its body only `throw new Error('WO-NN: not built');`. `npm run modules`, the build. |
| 4. Tests | Claude | A unit test for every routine function, written from the spec. Each fails until its function is filled in. |
| 5. Tasks | Claude | `vNNN/TASKS.md`: one work order per routine function, marked `[Aider]`, and anything left for Claude marked `[Claude]`. Push the branch. |
| 6. Fill in | Owner + Aider | One task at a time (below). Free. |
| 7. Review and finish | Claude | The review-aider skill: every Aider change read against its work order, fixes, the `[Claude]` and skipped tasks done, no `WO-` stub left (`grep -rn "WO-" src/` is empty), checks, build, PR, "Merge it?". |

## Doing a task with Aider (the owner)

In VS Code's terminal, on the phase's branch (`/start` in Claude, or `git switch <branch>`):

    aider
    /read docs/work-orders/v175/SPEC.md docs/work-orders/v175/TASKS.md
    do the next unticked [Aider] task

Aider adds the task's one file, fills the function in, and runs its test (`/test` runs `npm test`).
Test passes: Aider ticks the box, next task. Test fails twice: type "skip it", Aider marks it
`[skipped]`, and Claude does it later. Close Aider when you stop; nothing needs committing.

## Rules for writing work orders (Claude)

A 14B model succeeds on a small, exact task and fails on a vague one. Each work order:
- **one file, one function**, ideally under 40 lines of body;
- says **where**: the file and the function's name (it is already declared there);
- says **what**: inputs, output, and every edge case, in plain words, with an example input and its
  expected result;
- lists **the existing names it may use**, with their files; nothing else may be called;
- names **its test** and the command to run it;
- repeats the **don'ts** that matter for it (no other file, no import/export lines, ES5).

Anything that does not fit these rules is a `[Claude]` task. Score every task with `ROUTING.md`;
split one that scores 5 or more when its pieces would each score 4 or less.

## The one exception to "no placeholders"

The `WO-NN` stubs live only on the phase's branch while the work orders are open. The PR is not
merged while any stub remains or any test fails, so `main` never has a placeholder.
