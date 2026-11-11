# VNNN work orders

Spec: `SPEC.md` in this folder. Branch: `<branch>`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its test passes), `[skipped]` left for Claude.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.

---

## [ ] WO-01 [Aider] `functionName` in `src/js/engine/<folder>/<file>.js`

- **Replace** the line `throw new Error('WO-01: not built');` with the function's body.
- **It must:** <exact behaviour, edge cases>
- **Example:** `functionName(...)` returns `...`
- **May use:** `nameA` (`<file>`), `nameB` (`<file>`)
- **Test:** `npm test` -> `tests/unit/<area>.test.mjs`, the cases named `WO-01 ...`
- **Done when:** those cases pass and nothing else fails.

---

## [ ] WO-02 [Claude] <what>

<Why it is Claude's: crosses files, needs judgment, ...>
