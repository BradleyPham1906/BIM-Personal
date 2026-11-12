# V175a work orders

Spec: `SPEC.md` in this folder (part 4 has every function in full). Spec branch:
`claude/jolly-mendel-dwnanp`. Implementation target: local `main` once this phase is present there.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its required checks pass), `[skipped]`
left for Claude.

Every task: change only the file named, only inside the function named. Never touch the
`import`/`export` lines, `canvas_v10.html`, or another task's function. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed.
Write the dash as `'\u2014'`, never as the character itself.

All ten are in one file, `src/js/engine/sheets/live-text.js`. Each function is already declared there with a comment;
only its one `throw` line is replaced. The tests of Claude's part at the end of `tests/unit/live-text.test.mjs` (the
cases with no `WO-` in their name) fail until WO-01, WO-03 and WO-04 are done: that is expected.

Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [x] WO-01 [Cline] `bimLvTokens(s)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-01: not built');` with the function's body.
- **It must:** return the fields in `s` as `[{i, n, key, dp}]`, in order; `[]` when `s` is not a string. Use the regular expression given in SPEC.md part 4, created inside the function, in a `while((m=re.exec(s)))` loop. `dp` is `null` when the field has no bar, else a number.
- **Example:** `bimLvTokens('GFA {{gfa}} total')` returns `[{i:4, n:7, key:'gfa', dp:null}]`
- **May use:** nothing
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-01 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+1+0 = 1, tier B

---

## [x] WO-02 [Cline] `bimLvGroup(s)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-02: not built');` with the function's body.
- **It must:** put a comma between each three digits of the whole part of a number given as a string. If `s` does not match `/^(-?)(\d+)(\.\d+)?$/`, return `s` unchanged. Keep the minus sign in front and the decimals as they are.
- **Example:** `bimLvGroup('1234567.25')` returns `'1,234,567.25'`; `bimLvGroup('999')` returns `'999'`; `bimLvGroup('abc')` returns `'abc'`
- **May use:** nothing
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-02 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+1+0 = 1, tier B

---

## [x] WO-03 [Cline] `bimLvFormat(v, kind, dp)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-03: not built');` with the function's body.
- **It must:** follow the four rules of SPEC.md part 4 in their order: null or undefined gives the dash; a kind with no `bimLvKind` gives `String(v)`; a value that is not a finite number gives the dash; else `bimLvGroup(bimDispNum(v, d)) + K.u` with `d` = `dp` when it is a number, else `K.dp`.
- **Example:** `bimLvFormat(4389.26,'area',null)` returns `'4,389.3 m\u00b2'`; `bimLvFormat(null,'area',null)` returns `'\u2014'`
- **May use:** `bimLvKind`, `bimLvGroup` (this file), `bimDispNum` (`src/js/engine/properties/palette.js`)
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-03 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+0+0 = 0, tier B (it has a work order)

---

## [x] WO-04 [Cline] `bimLvSubst(s, look)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-04: not built');` with the function's body.
- **It must:** return `{s, keys, unknown}`. Get the tokens from `bimLvTokens(s)`; walk them left to right, adding to the result the text before each token (`s.slice`), then either what `look(key, dp)` returned (a known key) or the token exactly as typed (when `look` returned `null` or `undefined`). Add the text after the last token. A key goes into `keys` or `unknown` once. `s` not a string: `{s:'', keys:[], unknown:[]}`. Never call `replace` on the result.
- **Example:** with `look` giving `'G'` for `'gfa'` and `null` otherwise, `bimLvSubst('GFA {{gfa}} {{ nope }}', look)` returns `{s:'GFA G {{ nope }}', keys:['gfa'], unknown:['nope']}`
- **May use:** `bimLvTokens` (this file)
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-04 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+1+0 = 1, tier B

---

## [x] WO-06 [Cline] `bimLvOvReset(n, key)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-06: not built');` with the function's body.
- **It must:** remove an override. No `n.ov`: return `false`. `key` null or undefined: delete `n.ov` and `n.ovAt`, return `true`. `n.ov` has no own `key`: return `false`. Else delete `key` from `n.ov` and from `n.ovAt` (if it exists), then delete `n.ov` when it has no own keys left, the same for `n.ovAt`, and return `true`.
- **Example:** `n={ov:{s:'x'},ovAt:{s:'y'}}`; `bimLvOvReset(n,'s')` returns `true` and `n` has neither `ov` nor `ovAt`
- **May use:** nothing
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-06 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+0+0 = 0, tier B

---

## [x] WO-05 [Cline] `bimLvOvSet(n, key, val, cur)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-05: not built');` with the function's body.
- **It must:** follow the four rules of SPEC.md part 4 in their order: no `n.bind` gives `false`; `val===cur` resets an existing override with `bimLvOvReset(n,key)` or returns `false`; the same override again returns `false` and changes nothing; else set `n.ov[key]=val` and `n.ovAt[key]=cur` (making the two objects when missing) and return `true`.
- **Example:** `n={bind:{k:'tok'}}`; `bimLvOvSet(n,'s','About 4,400','4,389')` returns `true`; `n.ov` is `{s:'About 4,400'}` and `n.ovAt` is `{s:'4,389'}`
- **May use:** `bimLvOvReset` (this file)
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-05 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+0+0 = 0, tier B

---

## [x] WO-07 [Cline] `bimLvOvState(n, key, cur)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-07: not built');` with the function's body.
- **It must:** return `'none'` when `n.ov` is missing or has no own `key`; `'changed'` when `n.ovAt` exists, has own `key`, and `n.ovAt[key]!==cur`; otherwise `'set'`.
- **Example:** `bimLvOvState({ov:{s:'x'},ovAt:{s:'a'}},'s','b')` returns `'changed'`
- **May use:** nothing
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-07 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+0+0 = 0, tier B

---

## [x] WO-08 [Cline] `bimLvOvKeep(n, key, cur)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-08: not built');` with the function's body.
- **It must:** return `false` when `n.ov` is missing or has no own `key`; return `false` when `n.ovAt` exists and its own `key` already equals `cur`; otherwise make `n.ovAt` when missing, set `n.ovAt[key]=cur`, and return `true`. Never change `n.ov`.
- **Example:** `n={ov:{s:'x'},ovAt:{s:'a'}}`; `bimLvOvKeep(n,'s','b')` returns `true` and `n.ovAt` is `{s:'b'}`
- **May use:** nothing
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-08 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+0+0 = 0, tier B

---

## [x] WO-09 [Cline] `bimLvPrintNote(items)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-09: not built');` with the function's body.
- **It must:** return `''` for `null` or an empty array. Else `'Printed with N live object not up to date: '` ("objects" when N is not 1), then the first three items joined with `', '`, each `nm (why)` or only `nm` when `why` is empty, then `' and K more'` when N is over 3 (K = N - 3).
- **Example:** five items named A to E, each `why:''`, give `'Printed with 5 live objects not up to date: A, B, C and 2 more'`
- **May use:** nothing
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-09 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+0+0 = 0, tier B

---

## [x] WO-10 [Cline] `bimLvMenuItems(rows)` in `src/js/engine/sheets/live-text.js`

- **Replace** the line `throw new Error('WO-10: not built');` with the function's body.
- **It must:** return an array with `[row[1], row[0]]` for each row (the label first, then the key), and the string `'-'` between two rows whose `row[3]` (the group) differs. No `'-'` first or last. `[]` for no rows.
- **Example:** `bimLvMenuItems([['date','Date','text','Project'],['gfa','GFA','area','Building']])` returns `[['Date','date'],'-',['GFA','gfa']]`
- **May use:** nothing
- **Test:** `npm test` -> `tests/unit/live-text.test.mjs`, the cases named `WO-10 ...`
- **Done when:** those cases pass and no test that passed before fails.
- **Score:** 0+0+0+0+0+0 = 0, tier B

---

## [x] WO-11 [Claude] Review, finish and hand over V175a

Claude's because it crosses files and closes the phase (tier D: review and finish):
- each of WO-01 to WO-10 read against its order, fixed where needed; any `[skipped]` task done;
  `grep -rn "WO-" src/` empty;
- `npm run modules`, the build, `npm test` (155 pass);
- ask the owner whether to run a browser check of the Draw menu's Field and Number, the Live group and a print;
- the user guide (`docs/src/`), the engineering log entry, `BIM_APP_VERSION`, PIPELINE (hash, size, tests, V175b
  marked Start here), CLAUDE.md's module map (three new files in `sheets/`), Notion;
- review the local prototype against the spec and ask the owner before any push or publication.

## Done by Claude already (2026-11-11), for reference

`live-sources.js` and `live-edit.js` in full; the record (`bimBobOne`), the drawing, the Draw menu, the Properties
panel's Live group, Print's message, the marks' CSS, the test hooks; D10 (units saved with the project) and D11
(opening a project moves the revision); the tests. Checked: with a private reference version of the ten functions,
all 155 unit tests passed; with the stubs back in, only the `WO-` cases and the seven cases that stand on them fail.
