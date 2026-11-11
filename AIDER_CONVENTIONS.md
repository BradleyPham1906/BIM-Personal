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
- Work on a branch named `aider/<task>`, never on `main`.
- After an edit, the owner runs `python3 tools/build_app.py` and `npm test`, and commits
  `canvas_v10.html` with the change.
- If the task does not fit the code as described, stop and say what is different.
