# V225 work orders: The OpenBridge UI foundation

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/ui/openbridge-theme.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v225/v225.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v225/v225.test.mjs
    node --check src/js/engine/ui/openbridge-theme.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimObLum(hex)`

- **It must:** SPEC 5 WO-01: '#rrggbb' or 'rrggbb' (any case; else null): each channel c/255 linearised (c/12.92 at or under 0.04045, else ((c + 0.055)/1.055)^2.4); 0.2126 R + 0.7152 G + 0.0722 B.
- **May use:** nothing.
- **Files:** `src/js/engine/ui/openbridge-theme.js`, `docs/work-orders/v225/v225.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v225/v225.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimObContrast(a, b)`

- **It must:** SPEC 5 WO-02: (the lighter + 0.05) / (the darker + 0.05); null when either colour is invalid.
- **May use:** bimObLum (WO-01).
- **Files:** `src/js/engine/ui/openbridge-theme.js`, `docs/work-orders/v225/v225.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v225/v225.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimObPasses(ratio, level)`

- **It must:** SPEC 5 WO-03: ratio >= 7 for 'AAA', 3 for 'large', else 4.5 (1e-9 tolerance); false for a non-number.
- **May use:** nothing.
- **Files:** `src/js/engine/ui/openbridge-theme.js`, `docs/work-orders/v225/v225.test.mjs`
- **Budget:** 5
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v225/v225.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimObTheme(tokens, mode)`

- **It must:** SPEC 5 WO-04: for each token {day, dusk, night}: its value for the mode, else its day value.
- **May use:** nothing.
- **Files:** `src/js/engine/ui/openbridge-theme.js`, `docs/work-orders/v225/v225.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v225/v225.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] The theme in the app

Claude's: the tokens from the reviewed kit as data, the Settings switch, every pair checked by WO-02 and WO-03 at build time; the icons after the licence review. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 225, Notion.
