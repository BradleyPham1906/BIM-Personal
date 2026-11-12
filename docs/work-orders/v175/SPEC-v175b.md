# V175b spec: schedules, single KPI cards and result charts on a board

Research: `docs/research/research-presentation-live.md` (the owner's D1 to D16, all as recommended, 2026-11-11;
D16 splits V175 in two, and this is the second part). V175a (fields, numbers, overrides) is merged
(BradleyPham1906/BIM-Personal#87, #89). Written by Claude, 2026-11-12. Implementation target: local `main`.
Cline reads this with `TASKS-v175b.md`; keep it exact and plain.

## 1. What it does for the user

On a board in Edit, the Draw menu gains three entries after Field and Number:

- **Schedule...**: a table drawn from the model. Two to start: **Rooms** (number, name, level, area, occupants)
  and **Areas by level** (level, gross area, room area, efficiency). Its rows are the model's now; a total row
  sums the areas. In Properties: its title, which column it is sorted by, ascending or descending.
- **Indicator...**: one card taken out of a site board's indicator row (Climate and risk, Zoning and yield,
  Access, People), for example the lot area or the hottest month, placed alone where it is wanted.
- **Result chart...**: one result layer's chart: its legend, what it measured, and for Sun hours a histogram of
  how much of the ground gets how many hours.

Two numbers join the Number menu: the **share of the ground with 6 hours of sun or more** (from the newest Sun
hours layer) and the **roofs' solar yield in a year** (kWh, from the last Solar run).

Each is drawn from the model each time the board is (D2). A result kept from an analysis is never run again by a
board (D3): when the model has changed since, it is drawn with the amber mark and Properties has **Run again**.
A source that was removed (the layer deleted, the board's indicator gone) says what it was bound to and is a dash
on paper (D8). The title of each is its own, typed in Properties, and is not an override (it has no source).
**Unlink** (D6) is not offered for these three: a table or chart has no plain-text form; delete it instead.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/sheets/live-board.js` | new (empty now) | Pure functions: the histogram, percentages, bars, sorting and totals, reading an indicator's label, a table's and a chart's markup | Cline, WO-01 to WO-10 |
| `src/js/engine/sheets/live-board-draw.js` | new | The three kinds' sources and drawing; the record's checks for them | Claude, WO-11 |
| `src/js/engine/sheets/board-objects.js` | changed | `bimBobKinds` and `bimBobOne` know `sched`, `kpi`, `rchart` | Claude, WO-11 |
| `src/js/engine/sheets/board-design.js` | changed | `bimBdsNode` draws them | Claude, WO-11 |
| `src/js/engine/sheets/live-edit.js`, `board-design-edit.js`, `board-design-props.js` | changed | The Draw menu's three entries, their menus, their Properties | Claude, WO-11 |
| `src/js/engine/sheets/live-sources.js`, `live-text.js` | changed | The two new number keys and their kinds (`pct`, `kwh`) | Claude, WO-11 |
| `docs/work-orders/v175/v175b.test.mjs` | new | The work orders' tests; moved to `tests/unit/live-board.test.mjs` at WO-11 | Claude (done) |

## 3. Data

Three new kinds of board object, saved in the board's record. None saves a value, only what it shows (D8).

    {id:'e7', t:'sched', x,y,w,h, src:'rooms'|'levels', ttl:'Rooms', sk:'area', sd:true}
        sk: the column key it is sorted by (absent: the model's order); sd: descending
    {id:'e8', t:'kpi',   x,y,w,h, f:'zn.kpis', lab:'Lot area'}
        f: the indicator row's figure key (one of clim.kpis, zn.kpis, acc.kpis, ppl.kpis); lab: the card's label
    {id:'e9', t:'rchart',x,y,w,h, res:'res-abc-12', nm:'Sun hours, 2026-06-21', ttl:''}
        res: the result layer's id; nm: its name when placed, to say what was removed

**A schedule's rows** are objects keyed by column: `{number:'1.01', name:'Office', level:'Level 0', area:24.5,
occupants:3}`. **Its columns** are `[{k:'area', t:'Area', kind:'area'}, ...]`, kind one of `text`, `area`,
`count`, `pct`. **A cell** is shown by `bimLvFormat(v, kind, null)` (V175a), so an area is `24.5 m²`.

**Sun hours' cells** (a result layer's `data.cells`): one character a grid cell, `'0'` to `'7'` the cell's place
on the app's 8-colour ramp (`BIM_SIM_RAMP`), `'.'` a cell under a roof.

**An indicator row** is a list of HTML strings, one a card, each with `data-kpi="<label, escaped>"` (made by
`bimClbKpi`, `site-analysis/climate-board.js:312`).

**A bar**: `{x, y, w, h}` in the chart's own units, `y` measured down from the top.

## 4. Functions (the work orders)

Every one goes in `src/js/engine/sheets/live-board.js`, below its header comment, as a plain `function` (ES5).
None may change its arguments.

### `bimLbHist(cells, m)` - WO-01
- **Takes:** `cells` a string (or anything); `m` the number of bins, 1 to 10.
- **Returns:** an array of `m` counts. Each character `'0'` to `'9'` whose digit `d` is less than `m` adds 1 to
  index `d`. Every other character (`'.'`, letters, digits `>= m`) is left out. Not a string: `m` zeros.
- **Example:** `bimLbHist('0.1..9', 4)` returns `[1, 1, 0, 0]`.

### `bimLbPct(n, total)` - WO-02
- **Returns:** `n / total` as a percentage, rounded to one decimal (`Math.round(n / total * 1000) / 10`).
  `null` when either is not a finite number (`typeof` not `'number'`, or not `isFinite`) or `total <= 0`.
- **Example:** `bimLbPct(1, 3)` returns `33.3`; `bimLbPct(0, 0)` returns `null`.

### `bimLbBars(counts, W, H, gap)` - WO-03
- **Returns:** one bar `{x, y, w, h}` a count. All bars have the width `w = (W - gap * (n - 1)) / n`
  (`n` the number of counts); bar `i` is at `x = i * (w + gap)`; its height is `counts[i] / max * H`, or `0` when
  the largest count is 0; `y = H - h`. Every number rounded to two decimals (`Math.round(v * 100) / 100`).
  No counts: `[]`.
- **Example:** `bimLbBars([1, 2], 10, 4, 2)` returns `[{x:0, y:2, w:4, h:2}, {x:6, y:0, w:4, h:4}]`.

### `bimLbSort(rows, key, desc)` - WO-04
- **Returns:** a **new** array of the same row objects (the given one is not changed), sorted by `row[key]`.
- **Rules:** an empty value (`''`, `null`, `undefined`) always goes last, whatever `desc`. Two numbers
  (`typeof 'number'`) compare as numbers; anything else compares as `String(v).toLowerCase()`. `desc` true
  reverses the order of the values. Rows with equal values keep their order (the sort is stable: compare their
  first positions when the values are equal; `Array.prototype.sort` alone is not stable everywhere).
- **Example:** rows with `a` = `20, 5, 12, '', 5` sorted by `'a'` ascending come out `5, 5, 12, 20, ''`, the
  two 5s in the order they came in.

### `bimLbTotals(rows, cols)` - WO-05
- **Returns:** an array as long as `cols`: for a column whose `kind` is `'area'` or `'count'`, the sum of the
  rows' values for its `k` that are finite numbers (strings are left out); `''` when none is, and `''` for any
  other kind.
- **Example:** columns `text`, `area`, `count` over rows `{a:10.5, c:2}`, `{a:4, c:''}`, `{a:'3', c:1}` give
  `['', 14.5, 3]`.

### `bimLbUnesc(s)` - WO-06
- **Returns:** `s` with `&lt;` `&gt;` `&quot;` `&#39;` read back as `<` `>` `"` `'`, and `&amp;` as `&`
  **last**, so `'&amp;lt;'` gives `'&lt;'`. Not a string: `''`.

### `bimLbKpiLabels(list)` - WO-07
- **Returns:** the labels of the cards, in order: for each string, the first `data-kpi="..."` it holds (regular
  expression `/data-kpi="([^"]*)"/`), read back with `bimLbUnesc`. A string with none is skipped. Not an
  array: `[]`.
- **May use:** `bimLbUnesc`.

### `bimLbKpiFind(list, label)` - WO-08
- **Returns:** the index in `list` of the first string whose `data-kpi` label, read back with `bimLbUnesc`,
  equals `label` exactly; `-1` when none does or `list` is not an array. The index counts every string,
  including those without a label.
- **May use:** `bimLbUnesc`.

### `bimLbTableHtml(head, rows, foot, esc)` - WO-09
- **Takes:** `head` an array of `n` strings; `rows` an array of arrays of strings; `foot` an array of strings or
  `null`; `esc` a function that escapes one string for HTML.
- **Returns:** exactly `'<table class="a3d-clb-dtab"><thead><tr>' + a <th> each + '</tr></thead><tbody>' + a
  <tr> each row with a <td> each + '</tbody>' + (foot ? '<tfoot><tr>' + a <td> each + '</tr></tfoot>' : '') +
  '</table>'`. Every cell's text goes through `esc`. Every row has exactly `n` cells: a short one is filled with
  empty cells (`<td></td>`), a long one is cut. No rows: one row `'<tr><td colspan="n" class="none">No
  rows</td></tr>'` with `n` written as the number. No spaces or new lines anywhere in the markup.

### `bimLbHistSvg(bars, cols, W, H)` - WO-10
- **Returns:** `'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H" width="W" height="H"
  preserveAspectRatio="none">'` (the numbers written in) then, for each bar `i` whose `h` is more than 0,
  `'<rect x="x" y="y" width="w" height="h" fill="C"/>'` where `C` is `cols[i % cols.length]`, or `'#888888'`
  when `cols` is empty; then `'</svg>'`. A bar of height 0 is left out but still uses its colour's turn.

## 5. Order of the work

WO-01 to WO-10, top to bottom (WO-07 and WO-08 need WO-06). Each is tested on its own:

    node --test --test-name-pattern="WO-01" docs/work-orders/v175/v175b.test.mjs

The app does not call these functions until WO-11, so the local build stays usable after each one; nothing on
screen changes until then. Then Claude (WO-11) builds the three kinds on them, the menus and Properties, the two
numbers, moves the tests into `tests/unit/`, runs the browser check (Rule #1: a phase's new interface), and
closes the phase.

## 6. Not in this phase

- Schedules of anything but rooms and areas by level (walls, doors, a custom schedule): later, from V114's
  schedules, when the owner asks.
- Editing a schedule's cells on the board, or per-cell overrides (D5's path keys): not asked for.
- A chart for a result layer other than Sun hours' histogram: the others show their legend and their text.
- Running an analysis from a board (D3).
