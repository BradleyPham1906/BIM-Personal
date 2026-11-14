# V225 spec: The OpenBridge UI foundation

Notion: OpenBridge UI foundation, licensed assets and phased adoption. Research: `docs/research/research-openbridge.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- OpenBridge's design tokens adopted in phases as data (day, dusk and night palettes), each colour pair checked for WCAG contrast before use; its icons only after the per-revision licence review the research asks for.
- No change to model storage, simulation or delivery; the staged kit on the branch feat/openbridge-ui-intake is the source once reviewed.
- Day is the fallback for a token with no value in a mode.

## 2. What it does for the user

Settings, Theme: OpenBridge's day, dusk and night palettes for the app's panels, every text colour meeting WCAG AA against its background.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/ui/openbridge-theme.js` | new, after `js/engine/ui/build-ui.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v225/v225.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/ui/openbridge-theme.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimObLum(hex)`**: '#rrggbb' or 'rrggbb' (any case; else null): each channel c/255 linearised (c/12.92 at or under 0.04045, else ((c + 0.055)/1.055)^2.4); 0.2126 R + 0.7152 G + 0.0722 B.
- **WO-02 `bimObContrast(a, b)`**: (the lighter + 0.05) / (the darker + 0.05); null when either colour is invalid.
- **WO-03 `bimObPasses(ratio, level)`**: ratio >= 7 for 'AAA', 3 for 'large', else 4.5 (1e-9 tolerance); false for a non-number.
- **WO-04 `bimObTheme(tokens, mode)`**: for each token {day, dusk, night}: its value for the mode, else its day value.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** the theme in the app; **WO-06** the records.

## 7. Not in this phase

Icons before the licence review; a redesign of the panels; openbridge's web components.
