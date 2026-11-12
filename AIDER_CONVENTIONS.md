# Rules for Aider, the backup implementer

Read by Aider on every session (`.aider.conf.yml`). Cline with the owner's free Nemotron 3.5
Super VL option is the primary first-pass implementer; use Aider only when Cline is unavailable
or the owner asks to switch. Follow the local prototype workflow in `.clinerules/aider-workflow.md`.

- Edit only `src/`, `tests/`, `tools/` and `docs/`. Never edit `canvas_v10.html`: it is built by
  `python3 tools/build_app.py`.
- Never edit the `import { ... } from ...;` lines at the top or the `export { ... };` line at the
  bottom of `src/js/engine/**` files. `npm run modules` writes them.
- JavaScript is ES5: `var`, `function`, no arrow functions, no classes, no `let`/`const`, no template
  strings. No dependencies. No emojis. No placeholders or TODO stubs.
- Make small, targeted edits. Never rewrite a whole file. Keep files under about 400 lines.
- Use only functions and files that exist in the code you were shown. If something is unknown, say so.
- Work on local `main` only after checking that the checkout is clean and no other tool is using it.
  Do not switch branches or overwrite unexplained changes.
- Work-order tasks are marked `[Cline]`; Aider may take one only after the owner asks or Cline is
  unavailable. Complete the task rather than leaving a `WO-` stub.
- Rebuild `canvas_v10.html` after source changes and run only the checks required by Rule #1 in
  `CLAUDE.md`. Do not run browser checks or full regression without owner approval.
- Keep Aider edits on local `main`; never push or open a PR unless the owner explicitly asks.
- Aider does not auto-commit. If the owner asks Aider to take over, leave a clear diff for review;
  the owner or Cline can make the local checkpoint commit after the required checks pass.
- If the task does not fit the code as described, stop and say what is different.

## Should Aider do this?

When asked to "score" a task, read `docs/work-orders/ROUTING.md`, answer its six questions with a
reason each, give the total and the tier, and say plainly if the task is for Claude.

## Work orders (`docs/work-orders/vNNN/TASKS.md`)

When the owner asks Aider to take over a work order and says "do the next task":
1. Take the first task marked `[ ]` and `[Cline]`. Do only that one.
2. `/add` the one file it names. Implement the complete behavior in the named function, using only
   the names the task lists. For legacy tasks with an existing `WO-` stub, replace that stub.
3. Run only the checks required by Rule #1 in `CLAUDE.md`. Mark `[ ]` as `[x]` only after the task's
   required checks pass and nothing that was passing breaks.
4. If checks fail, make up to two focused fix attempts. If they still fail, or the owner says "skip
   it", preserve the diff, mark `[ ]` as `[skipped]`, and report what Claude needs to review. Never
   put a throw stub back into the implementation.
