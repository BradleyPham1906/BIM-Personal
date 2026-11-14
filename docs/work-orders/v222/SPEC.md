# V222 spec: 4D/5D construction planning, CP0 to CP3: quantities, cost lines, allocation

Notion: Later: 4D/5D Construction Planning. Research: `docs/research/plan-4d-5d-construction-planning.md`, `docs/research/research-4d-5d-cp0-cp3.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Native slab and footing quantities and manual resource lines first, each with its provenance; the measurement rules (openings deducted, waste added) are stated settings, not a standard's rules, until a jurisdiction and edition are chosen.
- Planned cost by working day comes from explicit allocations whose shares never exceed 100%; what is not allocated stays visible.
- Generic currency; every rate entered by the owner; labelled a planning aid, not an estimate. The research's call for qualified reviewers stands before the numbers are relied on.

## 2. What it does for the user

Select slabs: a Quantities table gives each net volume, the order quantity with waste, material and labour cost lines, and a planned cost by day from the allocations you enter.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/cost-plan.js` | new, after `js/engine/bim/proforma.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v222/v222.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/bim/cost-plan.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimCpSlabNet(w, l, t, holes)`**: w l t less each hole's w l times its depth (its t when positive, capped at t; else t); never under 0.
- **WO-02 `bimCpLine(q, P)`**: order = q (1 + waste) (waste 0 unless 0 or more), material = order matRate, hours = q hoursPer, labour = hours labRate (missing rates 0); {order, material, hours, labour, total: material + labour}.
- **WO-03 `bimCpAllocate(amount, splits)`**: any share not 0 or more, or a total over 1 (by 1e-12): {error: 'invalid allocation'}; else {assigned: amount times each share, unallocated: amount - amount times the total}.
- **WO-04 `bimCpBuckets(items)`**: items [{amount, split: {bucket: share}}]: each bucket's sum of amount times share.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** quantities and the plan; **WO-06** the records.

## 7. Not in this phase

Procurement and drawing intake (v223); a jurisdiction's measurement rules; earned value.
