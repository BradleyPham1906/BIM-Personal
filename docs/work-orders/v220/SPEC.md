# V220 spec: Water and presentation rendering

Notion: Later: Water and presentation rendering. Research: `docs/research/research-notion-later-water-presentation.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Ponds first, as a visual layer (V143's ponds); flooding only as a display of results validated elsewhere, with a visible disclaimer.
- Evan Wallace's techniques (MIT) written ourselves: a heightfield wave, drops, Fresnel by Schlick, caustics by area ratio; a still image first, animation as an option.
- Falls back to flat water where the GPU cannot; caustics and refraction separate, optional milestones.

## 2. What it does for the user

Ponds in the rendered view with a moving surface, reflections by Fresnel and caustics on their beds.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/render/water-sim.js` | new, after `js/engine/render/splats.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v220/v220.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/render/water-sim.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimWtrStep(h, v, n, damp)`**: on an n x n grid: each interior cell's velocity becomes (v + (the mean of its four neighbours' heights - h) 2) damp (damp 0.995 unless in 0..1], 1 allowed), boundary velocities unchanged; then every height plus its new velocity. {h, v} new arrays.
- **WO-02 `bimWtrDrop(h, n, x, y, r, s)`**: a copy with, at each cell within distance r of (x, y) (d = distance / r < 1), s (0.5 + cos(pi d) / 2) added.
- **WO-03 `bimWtrSchlick(n1, n2, cosT)`**: f0 + (1 - f0)(1 - cosT)^5 with f0 = ((n1 - n2)/(n1 + n2))^2.
- **WO-04 `bimWtrCaustic(oldA, newA)`**: oldA / newA, Infinity when newA is not positive.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** water in the rendered view; **WO-06** the records.

## 7. Not in this phase

Hydraulic flood modelling; animated exports; ocean waves.
