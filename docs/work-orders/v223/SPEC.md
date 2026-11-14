# V223 spec: 4D/5D construction planning, CP4 and CP5: procurement and drawing intake

Notion: Later: 4D/5D Construction Planning. Research: `docs/research/research-4d-5d-cp4-cp5.md`, `docs/research/plan-4d-5d-construction-planning.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Order deadlines count working days back from the need date, skipping weekends and the owner's holidays (the research's fixture: 5 days before 2026-01-16 with the 12th off is 2026-01-08).
- Drawing intake (reading quantities from drawings) is measured by precision and recall on a reviewed sample before it is trusted; no AI service is called by this phase.
- Dates are calendar dates in UTC, no time zones.

## 2. What it does for the user

Each cost line gets an order-by date from its need date and lead time; the drawing intake shows its measured precision and recall.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/procurement.js` | new, after `js/engine/bim/cost-plan.js` in `src/index.html` (header done) | 3 pure functions (part 5) | Cline, WO-01 to WO-03 |
| `docs/work-orders/v223/v223.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-04, WO-05 |

## 5. Functions, `src/js/engine/bim/procurement.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimCpDate(s)`**: 'YYYY-MM-DD' as Date.UTC(year, month - 1, day); null for anything else. Write bimCpIso(t), the inverse ('YYYY-MM-DD' from UTC), with it.
- **WO-02 `bimCpWorkdayBefore(need, n, holidays)`**: null for a bad date or n under 0; n times: one day back, then further back while the day is Saturday, Sunday or in holidays ('YYYY-MM-DD' strings); the result as 'YYYY-MM-DD'.
- **WO-03 `bimCpScores(tp, fp, fn)`**: {precision: tp / (tp + fp), recall: tp / (tp + fn)}, each null when its denominator is 0.

## 6. Order of the work

WO-01 to WO-03 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-04** procurement dates and intake review; **WO-05** the records.

## 7. Not in this phase

Calling ai services; supplier portals; time zones.
