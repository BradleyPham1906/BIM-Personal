# Rules for Aider in this repository

Read by Aider on every session (`.aider.conf.yml`). The full rules are in `CLAUDE.md`.

- Edit only `src/`, `tests/`, `tools/` and `docs/`. Never edit `canvas_v10.html`: it is built by
  `python3 tools/build_app.py`.
- Never edit the `import { ... } from ...;` lines at the top or the `export { ... };` line at the
  bottom of `src/js/engine/**` files. `npm run modules` writes them.
- JavaScript is ES5: `var`, `function`, no arrow functions, no classes, no `let`/`const`, no template
  strings. No dependencies. No emojis. No placeholders or TODO stubs.
- Make small, targeted edits. Never rewrite a whole file. Keep files under about 400 lines.
- Use only functions and files that exist in the code you were shown. If something is unknown, say so.
- Leave edits uncommitted. Claude reviews them at its next session, rebuilds `canvas_v10.html`,
  runs the checks, commits on an `aider/<task>` branch and opens the pull request.
- If the task does not fit the code as described, stop and say what is different.

## Should Aider do this?

When asked to "score" a task, read `docs/work-orders/ROUTING.md`, answer its six questions with a
reason each, give the total and the tier, and say plainly if the task is for Claude.

## Work orders (`docs/work-orders/vNNN/TASKS.md`)

When asked to "do the next task":
1. Take the first task marked `[ ]` and `[Aider]`. Do only that one.
2. `/add` the one file it names. Replace only the `throw new Error('WO-NN: not built');` line in the
   function it names. Use only the names the task lists.
3. Run the tests (`/test`). If the task's cases pass and nothing else broke, change its `[ ]` to `[x]`
   in TASKS.md.
4. If they fail, fix once more. If they still fail, or if told "skip it", put back the `throw` line,
   change `[ ]` to `[skipped]`, and stop. Claude will do it.
