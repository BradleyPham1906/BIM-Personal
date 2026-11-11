# VNNN spec: <feature name>

Research: `docs/research/<note>.md` (the owner's decisions: <list or link>). Branch: `<branch>`.
Written by Claude, <date>. Aider reads this with TASKS.md; keep it exact and plain.

## 1. What it does for the user

<A few sentences: what the owner will see and be able to do, on phone, tablet and desktop.>

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/<folder>/<file>.js` | new | <...> | Claude (hard parts) + Aider (WO-01..) |

## 3. Data

<Every object shape the feature uses: fields, types, units, defaults, an example.>

## 4. Functions

For each function, Claude's or Aider's:

### `functionName(arg1, arg2)` - `src/js/engine/<folder>/<file>.js` - WO-NN or Claude
- **Takes:** <each argument, type, meaning>
- **Returns:** <type, meaning>
- **Rules and edge cases:** <each one, with what happens>
- **Example:** `functionName(...)` returns `...`
- **Uses:** <existing names, with their files>

## 5. Order of the work

<Which tasks depend on which; what the owner can test in the app after each group.>

## 6. Not in this phase

<What is deliberately left out, so neither tool adds it.>
