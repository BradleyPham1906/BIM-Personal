# V226 spec: Track C, the PennDOT LRFD input writer

Notion: Parked: Tracks C and D. Research: `docs/research/penndot/PENNDOT_INPUT_SPEC.md`, `docs/research/penndot/PENNDOT_OFFICIAL_DOCS.md`, `docs/research/research-openbridge.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- One writer serves PSLRFD and STLRFD: a shared core of 23 commands and a thin module per program; a command code is never read without its program (DPL is Drape Point Location in PSLRFD and Design Plate Location in STLRFD).
- Commands are emitted in the manual's order: STLRFD's by its section numbers now; PSLRFD's when its section 5.2 is extracted.
- Field-by-field records wait for the field definitions the spec lists as missing; nothing is written from guesswork.

## 2. What it does for the user

From a girder model, Export, PennDOT: an input file for PSLRFD or STLRFD with its commands named and in the manual's order.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/penndot-input.js` | new, after `js/engine/structure/frame-solve.js` in `src/index.html` (header done) | 3 pure functions (part 5) | Cline, WO-01 to WO-03 |
| `docs/work-orders/v226/v226.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-04, WO-05 |

## 5. Functions, `src/js/engine/structure/penndot-input.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimPdName(program, code)`**: with BIM_PD_PS (the 44 PSLRFD codes and names of the spec's inventory) and BIM_PD_ST (the 57 STLRFD codes in section order, 5.3 CFG to 5.59 ORF) just above it: for 'PS' the name or null; for 'ST' 'Design Plate Location' for DPL, else the code when it is an STLRFD command, else null; any other program null.
- **WO-02 `bimPdShared()`**: the STLRFD codes that PSLRFD also has, sorted (23).
- **WO-03 `bimPdStOrder(codes)`**: {ok: false, why: 'not an STLRFD command: C'} for the first unknown code; else the codes that come before an earlier one's section, as {ok: false, why: "out of the manual's order: A, B"}; else {ok: true}.

## 6. Order of the work

WO-01 to WO-03 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-04** field definitions and the writer; **WO-05** the records.

## 7. Not in this phase

Running penndot's programs; aashto checks of our own; field records before their definitions.
