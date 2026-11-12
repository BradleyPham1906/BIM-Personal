# V175a spec: live text on a board (fields, numbers, overrides)

Research: `docs/research/research-presentation-live.md` (the owner's decisions: D1 to D16, all accepted as
recommended, 2026-11-11). Branch: `claude/jolly-mendel-dwnanp`. Written by Claude, 2026-11-11. Aider reads this with
TASKS.md; keep it exact and plain.

V175 is built in two parts (D16). **This is V175a.** V175b (schedules, single KPI cards and result charts as board
objects) follows in its own branch after V175a is merged.

## 1. What it does for the user

On a board in Edit, the Draw menu has two new entries.

- **Field...** puts a value of the project into a text: the project's name, the client, today's date, the board's
  name and number, the gross floor area, the site area. In the text it is written `{{key}}`, or `{{key|2}}` for two
  decimals. The text shows the value, and shows the new value when the project changes.
- **Number...** puts one number on the board with its unit, in large type: gross floor area, room area, site area,
  the floor area the zoning allows, cut volume, fill volume, or one level's gross area.

A selected live text has a **Live** group in the Properties panel: what it is bound to, what it shows, and

- **Shows**: typing other words there is an **override**. The object keeps those words and is marked with a blue
  corner tick. **Reset** goes back to the source. If the source changes after the override was made, Properties says
  so, with Reset and **Keep**.
- **Unlink**: the object keeps what it shows as plain text and no longer follows the project (one way; Ctrl+Z undoes).
- **Run again**: for cut and fill when a pad or the surface has changed since it was graded. A board never reruns an
  analysis by itself; it shows the kept value with an amber dot and the reason.
- A source that was deleted (a level) shows "Source removed: Level 2" in Edit and a dash on paper. A key that is not
  a field stays as typed and gets a red mark.

The marks show in Edit only and are never printed. Print says in a message which live objects are not up to date.

Two fixes come with it: the project's display units (m, cm, mm and decimals) are now saved with the project (D10),
and opening a project now redraws pages and boards that were drawn for the previous one (D11).

Everything is in the existing Properties panel and Draw menu, so it works on phone, tablet and desktop as they do.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/sheets/live-text.js` | new | Pure functions: reading fields from a string, formatting, the override's rules, the print message, the menu rows; and the validators of the saved record | Aider (WO-01 to WO-10); Claude (`bimLvKind`, `bimLvKeyOk`, `bimLvBindValid`, `bimLvOvKeys`, `bimLvOvValid`) |
| `src/js/engine/sheets/live-sources.js` | new | The key table, each source's resolver, the memo per revision, what a live text shows, its marks, the list for Print | Claude (done) |
| `src/js/engine/sheets/live-edit.js` | new | The Field and Number menus, override, Reset, Keep, Unlink, Run again, the Live group of Properties | Claude (done) |
| `src/js/engine/sheets/board-objects.js` | changed | `bimBobOne` keeps `bind`, `ov`, `ovAt` on a text | Claude (done) |
| `src/js/engine/sheets/board-design.js` | changed | A text with a binding is drawn from `bimLiveShow`, with its marks in Edit | Claude (done) |
| `src/js/engine/sheets/board-design-edit.js` | changed | The Draw menu's Field... and Number... | Claude (done) |
| `src/js/engine/sheets/board-design-props.js` | changed | The Live group, its buttons and fields | Claude (done) |
| `src/js/engine/sheets/boards.js` | changed | Print's message (D4) | Claude (done) |
| `src/js/engine/properties/palette.js`, `core/objects-save.js`, `core/state.js` | changed | Units saved with the project (D10) | Claude (done) |
| `src/js/engine/ui/project-tabs.js` | changed | Opening a project moves the revision (D11) | Claude (done) |
| `src/css/site-analysis/boards-design.css` | changed | The marks | Claude (done) |
| `src/js/engine/testing/hooks-boards.js` | changed | `window.__a3dLive`, `window.__acad3dV175a` | Claude (done) |
| `tests/unit/live-text.test.mjs` | new | The tests: `WO-01 ...` to `WO-10 ...`, then Claude's | Claude (done) |

## 3. Data

A board's text object (`t:'text'`) may carry three new fields. An object without `bind` is exactly as before.

    n.bind = {k:'tok'}                                        a text whose words n.s hold fields, e.g. 'GFA {{gfa|1}}'
    n.bind = {k:'num', src:'gfa'}                             one number; n.s is '{{gfa}}' (what an older build shows, D9)
    n.bind = {k:'num', src:'level.area', id:'lvl-1', nm:'Level 1', dp:2}
                                                              id: the source's id; nm: its name when bound, to say what
                                                              was removed (D8); dp: decimals, 0 to 6, optional
    n.ov   = {s:'About 4,400 m2'}                             the override: words typed over the source's. Only key 's'
    n.ovAt = {s:'4,389 m2'}                                   the source's words when the override was made (D7)

The value itself is never saved (D8). It is computed when the board is drawn, once per revision of the model.

**A field in text:** `{{key}}` or `{{key|d}}`. `key` starts with a letter, then letters, digits, `_` or `.`, 40
characters at most. `d` is one digit, 0 to 6. Spaces are allowed inside the braces: `{{ gfa | 1 }}`.

**A token** (what `bimLvTokens` returns for each field): `{i, n, key, dp}`: `i` the index in the string where `{{`
starts, `n` the field's whole length including the braces, `key` the key without spaces, `dp` the decimals as a
number, or `null` when there is no bar.

**Kinds** (`bimLvKind(kind)`, already built): `'area'` gives `{u:' m²', dp:1}`, `'vol'` gives
`{u:' m³', dp:1}`, `'count'` gives `{u:'', dp:0}`, anything else (text) gives `null`. `u` starts with a space.

**A key row** (`bimLiveKeys()`): `[key, label, kind, group]`, for example
`['gfa', 'Gross floor area', 'area', 'Building']`.

**The dash:** `'—'` (an em dash) is what the app shows for "no value".

## 4. Functions

Only the ten work-order functions are listed in full; Claude's are described in their files' comments.

### `bimLvTokens(s)` - `sheets/live-text.js` - WO-01
- **Takes:** `s`, any value.
- **Returns:** an array of tokens `{i, n, key, dp}`, in the order they appear. `[]` when `s` is not a string or holds no field.
- **Rules:** use this regular expression, made new inside the function each call:
  `/\{\{\s*([A-Za-z][A-Za-z0-9_.]{0,39})\s*(?:\|\s*([0-6])\s*)?\}\}/g`. Loop with `re.exec(s)`. For each match `m`:
  `i` is `m.index`, `n` is `m[0].length`, `key` is `m[1]`, `dp` is `null` when `m[2]` is `undefined`, else `+m[2]`.
- **Example:** `bimLvTokens('GFA {{gfa}} total')` returns `[{i:4, n:7, key:'gfa', dp:null}]`.
  `bimLvTokens('{{site.area|2}}')` returns `[{i:0, n:15, key:'site.area', dp:2}]`.
- **Uses:** nothing.

### `bimLvGroup(s)` - `sheets/live-text.js` - WO-02
- **Takes:** `s`, a string holding a number, such as `'12345.6'`.
- **Returns:** the same number with a comma between each three digits of its whole part: `'12,345.6'`.
- **Rules:** if `s` does not match `/^(-?)(\d+)(\.\d+)?$/`, return `s` unchanged (so the dash and words pass
  through). The minus sign stays in front. The digits after the point are never grouped.
- **Example:** `'1234567'` gives `'1,234,567'`; `'-1234'` gives `'-1,234'`; `'999'` gives `'999'`; `'—'` gives `'—'`.
- **Uses:** nothing.

### `bimLvFormat(v, kind, dp)` - `sheets/live-text.js` - WO-03
- **Takes:** `v` a number or a string; `kind` one of `'area'`, `'vol'`, `'count'`, `'text'`; `dp` a number of decimals, or `null`.
- **Returns:** the string a board shows.
- **Rules, in this order:**
  1. `v` is `null` or `undefined`: return `'—'`.
  2. `var K=bimLvKind(kind);` If `K` is `null` (text, or an unknown kind): return `String(v)`.
  3. `v` is not a number, or is not finite (`typeof v!=='number'||!isFinite(v)`): return `'—'`.
  4. Otherwise return `bimLvGroup(bimDispNum(v, d)) + K.u`, where `d` is `dp` when `dp` is a number, else `K.dp`.
     (`bimDispNum` rounds to `d` decimals and trims trailing zeros.)
- **Example:** `bimLvFormat(4389.26,'area',null)` returns `'4,389.3 m²'`; `bimLvFormat(12000,'count',null)` returns
  `'12,000'`; `bimLvFormat(null,'area',null)` returns `'—'`; `bimLvFormat('Riverside','text',null)` returns `'Riverside'`.
- **Uses:** `bimLvKind`, `bimLvGroup` (this file), `bimDispNum` (`properties/palette.js`).

### `bimLvSubst(s, look)` - `sheets/live-text.js` - WO-04
- **Takes:** `s`, any value; `look`, a function `look(key, dp)` that returns a string for a key it knows, or `null`.
- **Returns:** `{s, keys, unknown}`: `s` the string with each known field replaced by what `look` returned; `keys` the
  known keys in order, each once; `unknown` the keys `look` returned `null` (or `undefined`) for, in order, each once.
- **Rules:** `s` not a string: return `{s:'', keys:[], unknown:[]}`. Get the tokens with `bimLvTokens(s)`. Build the
  result left to right from pieces of the original `s` (`s.slice`), never by calling `replace` on the result: what
  `look` returns must not be scanned again. An unknown field is copied exactly as typed, spaces included.
- **Example:** with `look` returning `'G'` for `'gfa'` and `null` otherwise,
  `bimLvSubst('GFA {{gfa}} {{ nope }}', look)` returns `{s:'GFA G {{ nope }}', keys:['gfa'], unknown:['nope']}`.
- **Uses:** `bimLvTokens` (this file).

### `bimLvOvSet(n, key, val, cur)` - `sheets/live-text.js` - WO-05
- **Takes:** `n` a board object; `key` the property (always `'s'` today); `val` the words typed; `cur` the source's words now.
- **Returns:** `true` when `n` was changed, else `false`.
- **Rules, in this order:**
  1. `n` has no `bind`: return `false`, change nothing.
  2. `val===cur` (the typed words are the source's own): if `n.ov` has `key`, return `bimLvOvReset(n,key)`; else return `false`.
  3. `n.ov` exists and `n.ov[key]===val`: return `false`, change nothing (not even `ovAt`).
  4. Otherwise make `n.ov` and `n.ovAt` when missing, set `n.ov[key]=val` and `n.ovAt[key]=cur`, return `true`.
- **Example:** `n={bind:{k:'tok'}}`; `bimLvOvSet(n,'s','About 4,400','4,389')` returns `true` and `n.ov` is
  `{s:'About 4,400'}`, `n.ovAt` is `{s:'4,389'}`.
- **Uses:** `bimLvOvReset` (this file).

### `bimLvOvReset(n, key)` - `sheets/live-text.js` - WO-06
- **Takes:** `n` a board object; `key` a property name, or `null` for every override.
- **Returns:** `true` when an override was removed, else `false`.
- **Rules:** no `n.ov`: `false`. `key` is `null` or `undefined`: `delete n.ov; delete n.ovAt;` return `true`. Else, if
  `n.ov` does not have `key` (`hasOwnProperty`): `false`. Else delete `key` from `n.ov` and from `n.ovAt` (when
  `n.ovAt` exists); then delete `n.ov` if it has no own keys left, and the same for `n.ovAt`; return `true`.
- **Example:** `n={ov:{s:'x'},ovAt:{s:'y'}}`; `bimLvOvReset(n,'s')` returns `true`, and `n` has neither `ov` nor `ovAt`.
- **Uses:** nothing.

### `bimLvOvState(n, key, cur)` - `sheets/live-text.js` - WO-07
- **Returns:** `'none'` when `n.ov` is missing or has no own `key`; `'changed'` when `n.ovAt` has own `key` and
  `n.ovAt[key]!==cur`; else `'set'`.
- **Example:** `bimLvOvState({ov:{s:'x'},ovAt:{s:'a'}},'s','b')` returns `'changed'`; with `cur` `'a'` it returns `'set'`.
- **Uses:** nothing.

### `bimLvOvKeep(n, key, cur)` - `sheets/live-text.js` - WO-08
- **Returns:** `false` when `n.ov` is missing or has no own `key`; `false` when `n.ovAt` has own `key` equal to `cur`;
  otherwise make `n.ovAt` when missing, set `n.ovAt[key]=cur`, return `true`. `n.ov` is never changed.
- **Example:** `n={ov:{s:'x'},ovAt:{s:'a'}}`; `bimLvOvKeep(n,'s','b')` returns `true` and `n.ovAt` is `{s:'b'}`.
- **Uses:** nothing.

### `bimLvPrintNote(items)` - `sheets/live-text.js` - WO-09
- **Takes:** `items`, an array of `{nm, why}` (a name and a reason, both strings; `why` may be `''`), or `null`.
- **Returns:** `''` when `items` is `null` or empty. Otherwise one sentence:
  `'Printed with N live object(s) not up to date: '` then the first three items joined by `', '`, each written
  `nm (why)`, or just `nm` when `why` is empty; then `' and K more'` when there are more than three (K = N - 3).
  "object" for N = 1, "objects" otherwise.
- **Example:** one item `{nm:'Cut volume', why:'Out of date'}` gives
  `'Printed with 1 live object not up to date: Cut volume (Out of date)'`. Five items named A to E with empty reasons
  give `'Printed with 5 live objects not up to date: A, B, C and 2 more'`.
- **Uses:** nothing.

### `bimLvMenuItems(rows)` - `sheets/live-text.js` - WO-10
- **Takes:** `rows`, an array of key rows `[key, label, kind, group]`.
- **Returns:** an array for a menu: for each row `[label, key]` (label first), and the string `'-'` between two rows
  whose `group` (index 3) differs. No `'-'` at the start or the end. `[]` for no rows.
- **Example:** rows `[['date','Date','text','Project'],['gfa','GFA','area','Building']]` give
  `[['Date','date'],'-',['GFA','gfa']]`.
- **Uses:** nothing.

## 5. Order of the work

In TASKS.md's order, top to bottom: it lists WO-06 before WO-05, because WO-05 calls WO-06's function. WO-03 needs
WO-02; WO-04 needs WO-01. Each has its own test cases, named `WO-NN ...` in `tests/unit/live-text.test.mjs`.

Until WO-01, WO-03 and WO-04 are built, the app on this branch throws when a board with a live text is drawn or a
text's words are changed in Properties: that is expected, and why this branch is not merged while a stub remains.
After WO-10, all of `npm test` passes (155 tests), and in the app: Edit a board, Draw, Field... or Number...

Then Claude (WO-11): the review, the browser check if the owner wants one, the user guide, the engineering log,
PIPELINE, the version, Notion, and the PR out of draft.

## 6. Not in this phase

- Schedules, single KPI cards, a result layer's chart as board objects, and sun hours and solar numbers: V175b.
- Overrides of anything but a live text's words (a legend's rows, a figure's cards): V175b, with those objects.
- Any rerun of an analysis by a board (D3), a Manual or frozen mode (D2), a stored value (D8).
- An escape syntax for a literal `{{key}}`: Unlink covers it (D14).
- Camera moves still move the revision (D12: recorded, not changed here).
- In Present, a date field that crosses midnight is redrawn at the next change of the model, not at midnight.
- Typing in the field's key by hand is allowed but nothing completes it: the menu is the way in.
