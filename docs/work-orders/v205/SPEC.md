# V205 spec: LOD-G, Gaussian splats as a backdrop

Notion: V192 LOD-G: Gaussian splats. Research: `docs/research/research-notion-v192-splats.md`, `docs/research/research-bridge-splatting.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- A visual-only, isolated layer: never converted to BIM geometry, never measured from, left out of exports unless ticked.
- antimatter15's .splat format first (32 bytes a splat); its viewer's drawing technique (MIT) written into the rendered view ourselves, or vendored under the library rule after its licence and dependencies are read.
- Placed by the owner with two point pairs (scale, a turn about the vertical, a move), shown with its placement error; full 3D alignment later.
- A size limit measured on the owner's phone before it is set; 1,000,000 splats until then.

## 2. What it does for the user

Import a .splat capture; place it with two clicked pairs; it shows as a photoreal backdrop in the rendered view on its own layer, to trace against.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/render/splats.js` | new, after `js/engine/render/rendered-map.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v205/v205.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/render/splats.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimSplatParse(buf)`**: an ArrayBuffer of 32-byte splats, little-endian: position float32 x3 at 0, scale float32 x3 at 12, colour uint8 x4 at 24, rotation uint8 x4 at 28 read as (b - 128) / 128. {n, pos, scale (Float32Array n*3), rgba (Uint8Array n*4), rot (Float32Array n*4)}; a length not a multiple of 32 gives {error: 'not a .splat file (its length is not a multiple of 32)'}.
- **WO-02 `bimSplatBounds(pos)`**: {min, max, centre} of the [x, y, z] triples; null for none.
- **WO-03 `bimSplatFit2(a0, a1, b0, b1)`**: in plan (x, z): s = |b1 - b0| / |a1 - a0|, rot = the difference of their headings (atan2(dz, dx)), t = b0 - s R a0 in plan and b0[1] - s a0[1] in height. {s, rot, t}; null when either pair's plan length is under 1e-9.
- **WO-04 `bimSplatApply(T, p)`**: [s (cos x - sin z) + t0, s y + t1, s (sin x + cos z) + t2].
- **WO-05 `bimSplatOrder(pos, eye)`**: the indices sorted by squared distance from the eye, farthest first, ties by index; [] for none.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** splats in the rendered view; **WO-07** the records.

## 7. Not in this phase

Training splats; editing splats; splats in sheets and prints.
