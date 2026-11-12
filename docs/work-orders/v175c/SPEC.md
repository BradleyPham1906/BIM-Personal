# V175c spec: one paper space (Pages and Boards as one Layout)

Research: `docs/research/research-one-paper-space.md` (the owner's D1 to D8, all as recommended, 2026-11-12).
The quick fixes (D3) are merged (BradleyPham1906/BIM-Personal#93). Written by Claude, 2026-11-12. Implementation
target: local `main`. Cline reads this with `TASKS.md`; keep it exact and plain.

## 0. The three steps

V175c is built in three steps, each one usable on its own (research part 5, alternative c):

| Step | What the owner sees | Work orders |
|---|---|---|
| **1. One list** (this spec, in full) | Every page of the set, a drawing sheet or a board, is a **Layout**: numbered in one series (A101, A102 ...), with a tab beside Model; one **+ Layout** in place of + Page and + Board | WO-01 to WO-06, below |
| 2. One editor | A viewport (plan, elevation, section or schedule at a scale) is an object on a layout; Draw, Properties, layers and align work on a drawing sheet; the sheet bar's actions on the one bar; old sheets open as layouts | Written when step 1 is merged |
| 3. One print | One vector print (SVG) of a layout's viewports and its objects | Written when step 2 is merged |

Steps 2 and 3 are outlined in part 6, so step 1 is built to fit them.

## 1. What step 1 does for the user

- **The tabs beside Model** list every layout of the set, in the set's order: drawing sheets and boards alike, each
  as "A101 - Site plan". A click opens it: a sheet in its layout view, a board as it opens today.
- **Numbers in one series** (D6): a new layout gets the next number after the highest (A101, A102 ...), whether it
  is a sheet or a board. A board that has no number yet (every board made before V175c) gets one the first time the
  project is opened, after the sheets, in the set's order. The number is editable: double-click a tab (as a sheet's
  tab renames today), or in a board's Properties. Two layouts with the same number are allowed but said: the
  Presentation panel names them.
- **One + Layout** (D5): in the Presentation panel, and the + at the end of the tabs. It opens a menu: **Drawing
  sheet** (a sheet as + Page makes it today), **Board** (a blank board), and the three site analysis boards
  (**Climate and risk**, **Zoning and yield**, **Access and people**), as + Board offers them today.
- **The name** (D7): the panel's heading and its buttons say Layout; the Presentation panel stays the place that
  lists the set.
- Everything else is as today: a sheet still has its own editor and a board its own, until step 2.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/sheets/layouts.js` | new (empty now) | The pure functions: the next number, a number made good, a label, the tabs' list, numbers used twice | Cline, WO-01 to WO-05 |
| `src/js/engine/sheets/layout-tabs.js` | changed | The tabs from the whole set; + opens + Layout's menu; double-click renumbers a board too | Claude, WO-06 |
| `src/js/engine/sheets/boards.js`, `board-figures.js` | changed | A board's `num`, kept (`bimBrdKeep`), given at load when missing | Claude, WO-06 |
| `src/js/engine/sheets/sheets.js` | changed | `bimNextSheetNumber` counts boards' numbers too (one series) | Claude, WO-06 |
| `src/js/engine/sheets/presentation-panel.js` | changed | + Layout; numbers on the list; duplicates said | Claude, WO-06 |
| `docs/work-orders/v175c/v175c.test.mjs` | new | The work orders' tests; moved to `tests/unit/layouts.test.mjs` at WO-06 | Claude (done) |

## 3. Data

A board's record gains one field. A sheet's record is unchanged (it has `number` already).

    board.num = 'A102'      the layout's number: letters, digits, space, dot, dash, underscore; 12 at most

**A layout entry** (what the tabs and the panel read; built from `bimPresSeq()`, the set in its order):

    {t:'sheet'|'board', id:'sheet-...'|'board-...', num:'A101', name:'Site plan'}

For a sheet, `num` is `sheet.number` and `name` is `sheet.name`. For a board, `num` is `board.num` and `name` is
`bimBoardLabel(board)` (the custom board's own name, or the site board's: "Climate and risk").

**A tab** (what `bimLyTabs` returns for each entry): `{id, t, label, on}`: `label` from `bimLyLabel(num, name)`,
`on` true for the layout on screen.

## 4. Functions (the work orders)

Every one goes in `src/js/engine/sheets/layouts.js`, below its header comment, as a plain `function` (ES5). None
uses another file's name. None may change its arguments.

### `bimLyNextNumber(numbers, prefix)` - WO-01
- **Takes:** `numbers` an array of the layouts' numbers (strings; other values are left out); `prefix` a short
  string of letters, such as `'A'`.
- **Returns:** `prefix` followed by one more than the highest number among the strings that are exactly the prefix
  (any case) followed by digits only, after trimming spaces; when there is none, or the highest is below 101,
  `prefix + '101'`. In words: the series starts at 101.
- **Rules:** build the regular expression inside the function: `new RegExp('^' + prefix + '(\\d+)$', 'i')`
  (the prefix is letters only), and test each trimmed string with it. `'A150b'` and `'A1.5'` do not match.
  `numbers` not an array: `prefix + '101'`.
- **Example:** `bimLyNextNumber(['A101', 'A103', 'A102'], 'A')` returns `'A104'`; `bimLyNextNumber(['A5'], 'A')`
  returns `'A101'`; `bimLyNextNumber(['A101', 'P101', 'P102'], 'P')` returns `'P103'`.

### `bimLyNumberValid(s)` - WO-02
- **Returns:** `s` with every run of spaces made one space and the ends trimmed; then `''` if that is empty or holds
  any character other than letters, digits, space, `.`, `-` and `_` (regular expression `/^[A-Za-z0-9 ._-]+$/`);
  else its first 12 characters. Not a string: `''`.
- **Example:** `bimLyNumberValid('  A-101  ')` returns `'A-101'`; `bimLyNumberValid('A<101>')` returns `''`.

### `bimLyLabel(number, name)` - WO-03
- **Returns:** both trimmed (`null` or `undefined` read as `''`): `number + ' - ' + name` when both are there;
  else the one that is there; else `'Layout'`.
- **Example:** `bimLyLabel('A101', 'Site plan')` returns `'A101 - Site plan'`; `bimLyLabel('', '')` returns `'Layout'`.

### `bimLyTabs(entries, activeId)` - WO-04
- **Takes:** `entries` an array of layout entries (part 3); `activeId` the id of the layout on screen, or `null`.
- **Returns:** a **new** array, one tab a entry in the same order: `{id: e.id, t: e.t, label: bimLyLabel(e.num,
  e.name), on: e.id === activeId}`. Not an array: `[]`. The entries are not changed.
- **May use:** `bimLyLabel` (this file).

### `bimLyDupNumbers(entries)` - WO-05
- **Returns:** the numbers used by more than one entry, compared trimmed and without case, each listed once, in the
  order in which each one's second use appears, written as it was first written (trimmed). An empty number (`''`,
  `null`, missing) is never a duplicate. Not an array: `[]`.
- **Example:** entries numbered `'A102', 'A101', 'a102 ', 'A101', 'A103'` give `['A102', 'A101']`.

## 5. Order of the work

WO-01 to WO-05, top to bottom; WO-04 needs WO-03. Each is tested on its own:

    node --test --test-name-pattern="WO-01" docs/work-orders/v175c/v175c.test.mjs

Nothing calls these functions until WO-06, so the local build is usable after each one and nothing on screen
changes. Then Claude (WO-06) builds step 1 on them: the tabs, the numbers, + Layout, the panel; moves the tests into
`tests/unit/`; runs the browser check (Rule #1: a phase's new interface); and writes step 2's spec.

## 6. Steps 2 and 3, outlined (not built now)

- **Step 2, one editor.** The board's map frame (`t:'map'`) becomes the one viewport object: its source a plan, an
  elevation, a section or a schedule; its scale and pan; Work in this viewport (model space through it) as a sheet
  has it. A sheet opens as a layout whose objects are a title block and one viewport object for each of its
  viewports, at their places and scales; its number and tab are kept. The sheet bar's actions (Sheet Setup, Title
  Block, Export, Print, Present) join the board's bar. A layout marked **drawing sheet** (D4) keeps the live values,
  figures and charts out of its Draw menu.
- **Step 3, one print.** A layout prints as one SVG of its objects and viewports at its page size, in place of the
  sheet's canvas print and the board's HTML print.

## 7. Not in step 1

- Any change to how a sheet or a board is edited or printed (steps 2 and 3).
- A prefix other than A for new layouts: the number is editable; a choice of prefix waits for the owner's use.
- Hiding a layout from Present (as LayOut allows): later, if asked.
