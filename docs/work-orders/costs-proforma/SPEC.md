# Costs and pro forma (outline)

Notion: Later: Costs and pro forma. PIPELINE: later. Research: `docs/research/research-later-costs-proforma.md`, `docs/research/research-usages.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Next spec sprint: the formulas are pure.

## 1. The owner's decisions, 2026-11-14, as recommended

- USD and the owner's US market first; every rate, rent and yield entered by the owner, none shipped as market data;
- areas from V131's usages (GFA, net) with the standard named on the sheet;
- the feasibility summary is a calculator, labelled not a valuation.

## 2. What it does for the user

Per usage: cost per area, rent, yield and sale price; a feasibility summary (cost, value, margin) on V160's yield.

## 3. The first slice (pure functions in `src/js/engine/bim/proforma.js`, ES5, no other file's names)

- `bimPfCost(areas, rates)`: construction cost by usage and its total.
- `bimPfIncome(areas, rents, vacancy)`: gross and net income.
- `bimPfValue(noi, capRate)`: value by direct capitalisation.
- `bimPfMargin(value, cost)`: profit and margin on cost.

Tests: Hand-worked pro forma.

## 4. Not in this phase

Cash flows over time; financing; taxes.
