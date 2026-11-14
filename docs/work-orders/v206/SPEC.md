# V206 spec: That Open: the Review view and IFC import (with Hub H3's identity)

Notion: That Open (Review view, IFC import); Later: Hub H3: full IFC. Research: `docs/research/research-thatopen.md`, `docs/research/research-notion-hub-h3-ifc.md`, `docs/research/research-ifc-engine.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The owner's answers (2026-11-13): a Review view loaded on demand (B); on the app's own three.js without That Open's WebGPU paths; That Open (web-ifc) also for IFC import, retiring cc-ifc (V196) once it matches it on the same 13 files; after V176-V177.
- Hub H3 is folded in: every imported element keeps its IFC GlobalId so the history and the hub compare IFC elements by identity; IFC4 written by V177, IFC2x3, IFC4 and IFC4.3 read.
- Fragments' geometry becomes the app's meshes per element in metres, +Y up, with V196's layers, storeys and property sets; the walls-and-slabs reader (import-ifc.js) stays as the fallback.

## 2. What it does for the user

Open an IFC in Review to look, clip and measure without importing; Import brings it into the editable model through That Open, each element keeping its GlobalId.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/io/ifc-review.js` | new, after `js/engine/io/ifc-full.js` in `src/index.html` (header done) | 7 pure functions (part 5) | Cline, WO-01 to WO-07 |
| `docs/work-orders/v206/v206.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-08, WO-09 |

## 5. Functions, `src/js/engine/io/ifc-review.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimTorMesh(pos, idx, scale)`**: null unless pos has a multiple of 3 values; vertices [x s, z s, (0 - y) s] (s = scale when positive, else 1; written 0 - y so 0 stays 0); faces of each 3 indices.
- **WO-02 `bimTorGuidValid(g)`**: with BIM_TOR_B64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$' just above it: a string of 22 characters, the first one of 0 to 3, the rest in the alphabet.
- **WO-03 `bimTorGuidFromHex(hex)`**: 32 hex digits (dashes removed, any case; else null) as 128 bits; the first character from the top 2 bits, then 21 characters of 6 bits each, by BIM_TOR_B64.
- **WO-04 `bimTorGuidToHex(g)`**: the inverse of WO-03, lower-case hex; null for an invalid GUID.
- **WO-05 `bimTorCompare(a, b)`**: two {class: count} maps: every class in either, sorted; {same: [classes with equal counts], diff: [{cls, a, b}] with absent as 0}.
- **WO-06 `bimTorArea(pts)`**: the area of a planar polygon in 3D: half the length of its Newell normal; 0 for none.
- **WO-07 `bimTorClip(p, plane)`**: true when (p - plane.p) . plane.n > 1e-9 (the clipped-away side); a point on the plane is kept.

## 6. Order of the work

WO-01 to WO-07 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-08** the review view; **WO-09** ifc import through that open.

## 7. Not in this phase

Editing inside review; bcf issues; ifc validation by an upload.
