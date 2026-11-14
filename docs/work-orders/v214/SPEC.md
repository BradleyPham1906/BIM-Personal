# V214 spec: Costs and pro forma

Notion: Later: Costs and pro forma. Research: `docs/research/research-later-costs-proforma.md`, `docs/research/research-usages.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- USD and the owner's US market first; every rate, rent, vacancy and cap rate entered by the owner, none shipped as market data.
- Areas from V131's usages and V160's yield, the measurement standard named on the sheet.
- An unlevered, stabilised operating model (no financing, no tax), labelled a calculator, not a valuation.

## 2. What it does for the user

A Pro forma panel: income lines per usage (quantity, rate, periods, vacancy), operating costs and cost items; it shows NOI, yield on cost, value at a cap rate, profit and margin, updated as the model's areas change.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/proforma.js` | new, after `js/engine/bim/parametric.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v214/v214.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/bim/proforma.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimPfmLine(l)`**: gross = qty rate periods (periods 1 unless positive; missing qty or rate 0); vacancy used when 0 <= v < 1, else 0; {name (or ''), gross, effective: gross (1 - v)}.
- **WO-02 `bimPfmTotals(lines, opex)`**: {gross, effective (sums of the lines), opex (0 unless positive), noi: effective - opex}.
- **WO-03 `bimPfmCost(items)`**: the sum of the items' finite numeric amounts.
- **WO-04 `bimPfmMetrics(noi, cost, cap)`**: {yieldOnCost: noi / cost (null unless cost > 0), value: noi / cap (null unless cap > 0), profit: value - cost, marginOnCost: profit / cost} with nulls carried.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** wiring into the app; **WO-06** the records.

## 7. Not in this phase

Cash flows over time; financing and tax; market data.
