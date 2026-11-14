# V212 work orders: Survey control, traverses and closure

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/survey/traverse-control.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v212/v212.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v212/v212.test.mjs
    node --check src/js/engine/survey/traverse-control.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimSvDms(s)`

- **It must:** SPEC 5 WO-01: a number as it is (null when not finite); a string 'D-M-S' or 'D M S' (minutes and seconds optional, seconds decimal, a leading minus) as D + M/60 + S/3600 with the sign; null for anything else or minutes or seconds of 60 or more.
- **May use:** nothing.
- **Files:** `src/js/engine/survey/traverse-control.js`, `docs/work-orders/v212/v212.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v212/v212.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimSvLatDep(legs)`

- **It must:** SPEC 5 WO-02: legs [[azimuth degrees from north clockwise, distance]]: {lat: d cos az, dep: d sin az (each per leg), sumN, sumE, perimeter}.
- **May use:** nothing.
- **Files:** `src/js/engine/survey/traverse-control.js`, `docs/work-orders/v212/v212.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v212/v212.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimSvClosure(legs, kind, start, end)`

- **It must:** SPEC 5 WO-03: 'open': {status: 'not assessable', why: 'an open traverse has no independent closure'}; 'link' without start or end: 'not assessable', 'a link traverse needs its known end'; else {status: 'computed', east, north (the sums, or start + sums - end for a link), misclosure, perimeter, ratio: perimeter / misclosure (Infinity at 0)}.
- **May use:** bimSvLatDep (WO-02).
- **Files:** `src/js/engine/survey/traverse-control.js`, `docs/work-orders/v212/v212.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v212/v212.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimSvCompass(legs, start)`

- **It must:** SPEC 5 WO-04: the start [E, N], then each point after a leg moved by its departure and latitude less sumE d / perimeter and sumN d / perimeter.
- **May use:** bimSvLatDep (WO-02).
- **Files:** `src/js/engine/survey/traverse-control.js`, `docs/work-orders/v212/v212.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v212/v212.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimSvAngular(angles)`

- **It must:** SPEC 5 WO-05: the sum of the interior angles less (n - 2) 180; null for fewer than 3.
- **May use:** nothing.
- **Files:** `src/js/engine/survey/traverse-control.js`, `docs/work-orders/v212/v212.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v212/v212.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Wiring into the app

Claude's: the interface on phone, tablet and desktop, saving with the project and undo; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 212, Notion.
