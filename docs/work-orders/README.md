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
| 4. Build | Cline | On local `main`, implement one task at a time from the research, spec and tests. Complete behavior; do not add deliberate throw stubs. |
| 5. Check and try | Cline + owner | Follow Rule #1 in `CLAUDE.md`; rebuild `canvas_v10.html` only after the required checks pass, and use that local file. The previous HTML stays usable until then. Make a local recovery checkpoint after a verified task or coherent group. Do not push. |
| 6. Review and improve | Claude | When available, compare the implementation against the research, spec and task criteria; fix gaps and improve the prototype. Browser checks and full regression still require owner approval. |
| 7. Backup | Aider | Take over only when Cline is unavailable or the owner asks. Follow the same local-main, no-push and check rules. |

## Doing a task with Cline

In VS Code, on local `main`, ask Cline to read the phase research, `SPEC.md` and `TASKS.md`, then
complete the first open `[Cline]` task. Cline may edit project files directly and run the checks
required by Rule #1. It marks a task `[x]` only after those checks pass. If a check fails, it makes
up to two focused fix attempts; if still failing, it stops, preserves the diff and reports the failure
for later review.

## Rules for writing work orders (Claude)

A model is more reliable on a small, exact task than on a vague one. Each work order:
- **one file, one function**, ideally under 40 lines of body;
- says **where**: the file and the function's name (it is already declared there);
- says **what**: inputs, output, and every edge case, in plain words, with an example input and its
  expected result;
- lists **the existing names it may use**, with their files; nothing else may be called;
- names **its test** and the command to run it;
- repeats the **don'ts** that matter for it (no other file, no import/export lines, ES5).

Anything that does not fit these rules is a `[Claude]` task. Score every task with `ROUTING.md`;
split one that scores 5 or more when its pieces would each score 4 or less.

## Keep the local prototype usable

Do not create `throw new Error('WO-NN: not built')` placeholders on `main`. Work orders are complete
implementation tasks, not invitations to land a temporarily broken skeleton. If a new feature is
unfinished, keep its controls unavailable or complete the bounded task before building a usable
prototype. Never push the prototype or publish it to Pages without the owner's explicit approval.
