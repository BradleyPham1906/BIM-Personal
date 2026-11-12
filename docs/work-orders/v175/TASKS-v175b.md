# V175b work orders

Spec: `SPEC-v175b.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every task: add one function to `src/js/engine/sheets/live-board.js`, below the file's header comment, and change
nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed. Implement
the whole function; never a placeholder.

The tests are in `docs/work-orders/v175/v175b.test.mjs`, outside `npm test` until the end, so main stays green.
After each task run its own cases, then the file's syntax check and the unit tests (Rule #1, one file of logic):

    node --test --test-name-pattern="WO-01" docs/work-orders/v175/v175b.test.mjs
    node --check src/js/engine/sheets/live-board.js
    npm test

Nothing calls these functions until WO-11, so rebuilding `canvas_v10.html` is not needed after each task.

Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [x] WO-01 [Cline] `bimLbHist(cells, m)`

- **It must:** return `m` counts; each digit character `d` in `cells` with `d < m` adds 1 at index `d`;
  everything else is left out; `cells` not a string gives `m` zeros (SPEC part 4).
- **Example:** `bimLbHist('0.1..9', 4)` returns `[1, 1, 0, 0]`.
- **May use:** nothing.
- **Test:** the cases named `WO-01 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-02 [Cline] `bimLbPct(n, total)`

- **It must:** return `Math.round(n / total * 1000) / 10`, or `null` when either is not a finite number or `total <= 0`.
- **Example:** `bimLbPct(1, 3)` returns `33.3`.
- **May use:** nothing.
- **Test:** the cases named `WO-02 ...`. **Score:** 0.

---

## [x] WO-03 [Cline] `bimLbBars(counts, W, H, gap)`

- **It must:** follow SPEC part 4: equal widths `(W - gap * (n - 1)) / n`, `x = i * (w + gap)`, height
  `counts[i] / max * H` (0 when the largest is 0), `y = H - h`, each number rounded to two decimals; `[]` for none.
- **Example:** `bimLbBars([1, 2], 10, 4, 2)` returns `[{x:0, y:2, w:4, h:2}, {x:6, y:0, w:4, h:4}]`.
- **May use:** nothing.
- **Test:** the cases named `WO-03 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-04 [Cline] `bimLbSort(rows, key, desc)`

- **It must:** return a new, stably sorted array (the given one unchanged); empty values (`''`, `null`,
  `undefined`) last whatever `desc`; two numbers compare as numbers, else as lower-case strings; `desc` reverses
  the values; equal values keep their order. Make it stable by pairing each row with its position first.
- **Example:** values `20, 5, 12, '', 5` ascending give `5, 5, 12, 20, ''`.
- **May use:** nothing.
- **Test:** the cases named `WO-04 ...`. **Score:** 0+0+0+1+1+0 = 2.

---

## [x] WO-05 [Cline] `bimLbTotals(rows, cols)`

- **It must:** give one entry a column: for kind `'area'` or `'count'` the sum of the rows' finite numbers in
  column `k` (strings left out), `''` when there are none; `''` for every other kind.
- **Example:** SPEC part 4 gives `['', 14.5, 3]`.
- **May use:** nothing.
- **Test:** the cases named `WO-05 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-06 [Cline] `bimLbUnesc(s)`

- **It must:** read back `&lt;` `&gt;` `&quot;` `&#39;`, then `&amp;` last; not a string gives `''`.
- **Example:** `bimLbUnesc('&amp;lt;')` returns `'&lt;'`.
- **May use:** nothing.
- **Test:** the cases named `WO-06 ...`. **Score:** 0.

---

## [x] WO-07 [Cline] `bimLbKpiLabels(list)`

- **It must:** return the labels in order, from `/data-kpi="([^"]*)"/` read back with `bimLbUnesc`; a string
  without one skipped; not an array gives `[]`.
- **May use:** `bimLbUnesc` (this file).
- **Test:** the cases named `WO-07 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-08 [Cline] `bimLbKpiFind(list, label)`

- **It must:** return the index in `list` (every string counts) of the first whose read-back label equals
  `label` exactly; `-1` otherwise or when `list` is not an array.
- **May use:** `bimLbUnesc` (this file).
- **Test:** the cases named `WO-08 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-09 [Cline] `bimLbTableHtml(head, rows, foot, esc)`

- **It must:** return the exact markup of SPEC part 4: a `thead` row of `th`, a `tbody` row of `td` for each
  row with exactly as many cells as `head` (short rows filled with `<td></td>`, long ones cut), a `tfoot` only
  when `foot` is not `null`, every text through `esc`, and the "No rows" row when `rows` is empty. No spaces or
  new lines in the markup.
- **May use:** nothing (`esc` is passed in).
- **Test:** the cases named `WO-09 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-10 [Cline] `bimLbHistSvg(bars, cols, W, H)`

- **It must:** return the exact markup of SPEC part 4: the `svg` element, a `rect` for each bar with `h > 0`
  coloured `cols[i % cols.length]` (`'#888888'` when `cols` is empty), then `</svg>`.
- **May use:** nothing.
- **Test:** the cases named `WO-10 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-11 [Claude] Build the three kinds on them, and close V175b

Claude's because it crosses many files and touches what is saved (ROUTING: always D):
- review WO-01 to WO-10 against SPEC part 4; move `v175b.test.mjs` to `tests/unit/live-board.test.mjs`;
- `live-board-draw.js`: the sources (`bimBuildRoomSchedule`, `bimLevelAreas`, the boards' indicator rows through
  `bimFigSrc`, `bimResById`, `bimResStale`, `bimResGone`, `bimResultLayerUpdate`), the drawing, the marks;
- `bimBobOne` for `sched`, `kpi`, `rchart`; the Draw menu, their menus, their Properties; the numbers
  `sun.sixplus` and `solar.roofkwh` with the kinds `pct` and `kwh`;
- `npm run modules`, the build, `npm test`, `npm run check`; the browser check (Rule #1), kept in `tests/e2e/`;
- the guide, the engineering log, PIPELINE (V176 Start here), Notion; ask the owner before merging.
