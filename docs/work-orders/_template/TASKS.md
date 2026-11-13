# VNNN work orders

Spec: `SPEC.md` in this folder. Implementation target: local `main`. One task at a time, top to bottom.
`[ ]` open, `[x]` done (its required checks pass), `[skipped]` left for Claude.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.
Do not add a deliberate `WO-` throw stub; implement complete behavior.

---

## [ ] WO-01 [Cline] `functionName` in `src/js/engine/<folder>/<file>.js`

- **Implement:** the complete function behavior specified in `SPEC.md`; do not leave a placeholder or partial stub.
- **It must:** <exact behaviour, edge cases>
- **Example:** `functionName(...)` returns `...`
- **May use:** `nameA` (`<file>`), `nameB` (`<file>`)
- **Files:** `src/js/engine/<folder>/<file>.js`, `tests/unit/<area>.test.mjs` (what `tools/gate.py` lets change)
- **Budget:** 60 (added src lines the gate allows; default 120)
- **Test:** `npm test` -> `tests/unit/<area>.test.mjs`, the cases named `WO-01 ...`
- **Done when:** `python3 tools/gate.py check <phase> WO-01` passes; then `ship` it.

---

## [ ] WO-02 [Claude] <what>

<Why it is Claude's: crosses files, needs judgment, ...>
