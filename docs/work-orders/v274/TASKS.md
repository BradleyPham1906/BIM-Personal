# V274 work orders: XR-1, the headset view

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/render/headset.js`, below the file's header comment, and
change nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed; never a name
from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v274/v274.test.mjs`, outside `npm test` while the orders are open, so main stays
green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v274/v274.test.mjs
    node --check src/js/engine/render/headset.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimHsUrlBytes(url)`

- **It must:** SPEC 4 WO-01: the `p` parameter of the link (found anywhere among the parameters), read as URL-safe
  base64: replace `-` by `+` and `_` by `/`, add `=` until the length is a multiple of 4, decode with `atob` inside a
  `try`, and return the bytes as a `Uint8Array`; `null` when there is no `p`, it is empty, or `atob` throws.
- **Example:** `bimHsUrlBytes('https://x.example/cfg?a=1&p=WAE&b=2')` returns `Uint8Array [0x58, 0x01]`.
- **User path:** internal only (WO-10 reads the pasted QR link with it).
- **May use:** `atob` (the browser's).
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v274/v274.test.mjs`.
- **Distinguishing case:** forgetting the padding, or `+` and `/`, fails the Cardboard v1 link (it holds `-` and `_`
  and its length is not a multiple of 4).
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimHsProfileDecode(bytes)`

- **It must:** SPEC 4 WO-02 in full: start from the Cardboard v2 default
  `{vendor: '', model: '', sl: 0.039, il: 0.064, fov: [60, 60, 60, 60], valign: 'bottom', tl: 0.035, k: [0.34, 0.55], button: 'magnet'}`
  (a fresh object and fresh arrays each call); read the protobuf fields one by one: a key is a varint, field number
  `key >> 3` (use `Math.floor(key / 8)`), wire type `key & 7`. Varints are 7 bits a byte, low first, the top bit set
  when more follow. Floats are `DataView.getFloat32(offset, true)` rounded with `Math.round(x * 1e6) / 1e6`. Fields:
  1 vendor and 2 model (length-delimited, one character per byte), 3 sl, 4 il, 6 tl (float), 5 fov and 7 k (floats,
  packed in one length-delimited field or one float per field; collect all, then use fov only if exactly 4 arrived,
  k if at least 1), 11 valign (`['bottom', 'center', 'top']`), 12 button (`['none', 'magnet', 'touch', 'indirect']`;
  an index outside keeps the default). Wire type 1 skips 8 bytes; an unknown length-delimited field is skipped; an
  unknown varint or float field is read and dropped. Null, empty bytes, a field running past the end, or wire type 3,
  4, 6 or 7 return `{error: 'the viewer settings could not be read'}`.
- **Example:** the Cardboard v1 bytes in the test return `{vendor: 'Google, Inc.', model: 'Cardboard v1', sl: 0.042,
  il: 0.06, fov: [40, 40, 40, 40], valign: 'bottom', tl: 0.035, k: [0.441, 0.156], button: 'magnet'}`.
- **User path:** internal only.
- **May use:** `DataView`, `Uint8Array`, `String.fromCharCode`, `Math`.
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v274/v274.test.mjs`.
- **Distinguishing case:** reading only packed repeats fails the unpacked `k` case; sharing one default object between
  calls fails when a later call changes it; not checking the end fails the cut-short float.
- **Score:** 0+1+0+0+2+0 = 3 (a file format; the test pins every field).

---

## [ ] WO-03 [Cline] `bimHsDistort(k, t)`

- **It must:** SPEC 4 WO-03: `t * (1 + k[0] t^2 + k[1] t^4 + ...)` for every coefficient; `t` when `k` is empty.
- **Example:** `bimHsDistort([0.34, 0.55], 0.5)` returns `0.5596875`.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-03 ...`.
- **Distinguishing case:** stopping at two coefficients fails the three-coefficient case.
- **Score:** 0.

---

## [ ] WO-04 [Cline] `bimHsLayout(P, S)`

- **It must:** SPEC 4 WO-04: `mpp = 0.0254 / S.ppi`; `dx = P.il / 2 / mpp`; `bezel = S.bezel` when it is a number
  (0 included), else 0.004; `y` is `(P.tl - bezel) / mpp` for `valign` 'bottom', `S.h / 2` for 'center',
  `S.h - (P.tl - bezel) / mpp` for 'top'; return `{mpp: mpp, lensL: [S.w / 2 - dx, y], lensR: [S.w / 2 + dx, y]}`.
- **Example:** Cardboard v2 on `{w: 2532, h: 1170, ppi: 460}` gives `lensL` about `[686.47, 561.42]`.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...`.
- **Distinguishing case:** `S.bezel || 0.004` fails the bezel-0 case.
- **Score:** 0.

---

## [ ] WO-05 [Cline] `bimHsEyeTan(P, S, L, eye)`

- **It must:** SPEC 4 WO-05: with `c` the eye's lens (`L.lensL` or `L.lensR`) and its half of the screen (left eye
  x from 0 to `S.w / 2`, right eye from `S.w / 2` to `S.w`), the distances in metres from `c` to the half's left,
  right, bottom (y 0) and top (y `S.h`) edges, times `L.mpp`; each side is
  `Math.min(lensLimit, bimHsDistort(P.k, distance / P.sl))`, the lens limits being `Math.tan(degrees * Math.PI / 180)`
  of `P.fov[0]` on the outer side (left for 'left', right for 'right'), `P.fov[1]` on the inner side, `P.fov[2]`
  bottom, `P.fov[3]` top. Return `{left, right, bottom, top}`.
- **Example:** SPEC 4 WO-05's left-eye numbers.
- **User path:** internal only.
- **May use:** `bimHsDistort` (this file).
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-05 ...`.
- **Distinguishing case:** using `fov[0]` for the left side of both eyes fails the uneven-fov case.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Cline] `bimHsHeadQuat(alpha, beta, gamma, screenDeg)`

- **It must:** SPEC 4 WO-06 exactly: null when `alpha`, `beta` or `gamma` is null or undefined; otherwise, in radians,
  x = beta, y = alpha, z = -gamma; `q` from the 'YXZ' formula in the SPEC; then `q` times `[-Math.SQRT1_2, 0, 0, Math.SQRT1_2]`;
  then times `[0, 0, Math.sin(o), Math.cos(o)]` with `o = -(screenDeg || 0) * Math.PI / 180 / 2`. Write the
  quaternion product once as an inner function and use it twice.
- **Example:** `bimHsHeadQuat(0, 90, 0, 0)` returns `[0, 0, 0, 1]` within 1e-12.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-06 ...`.
- **Distinguishing case:** multiplying in the other order, or 'XYZ' instead of 'YXZ', fails the alpha-30 and
  landscape cases.
- **Score:** 0+0+0+0+2+0 = 2 (rotations; every term is given).

---

## [ ] WO-07 [Cline] `bimHsYaw(q)`

- **It must:** SPEC 4 WO-07: `fx = -2 (x z + w y)`, `fz = -(1 - 2 (x x + y y))` from `q = [x, y, z, w]`; return 0 when
  both are under 1e-9 in size, else `Math.atan2(-fx, -fz)`.
- **Example:** the heading of `bimHsHeadQuat(30, 90, 0, 0)` is `Math.PI / 6`.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-07 ...`.
- **Distinguishing case:** `atan2(fx, fz)` gives the opposite heading and fails the -100 degree case.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bimHsRecentre(q, yaw)`

- **It must:** SPEC 4 WO-08: with `s = Math.sin(-yaw / 2)`, `c = Math.cos(-yaw / 2)` and `q = [x, y, z, w]`, return
  `[c x + s z, c y + s w, c z - s x, c w - s y]` (the turn `[0, s, 0, c]` times `q`).
- **Example:** `bimHsRecentre([0, Math.sin(0.25), 0, Math.cos(0.25)], 0.5)` returns `[0, 0, 0, 1]`.
- **User path:** internal only (WO-10 calls it when the headset starts and on a re-centre tap).
- **May use:** nothing.
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-08 ...`.
- **Distinguishing case:** multiplying on the right (`q` times the turn) changes the pitch and fails the pitch case.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-09 [Cline] `bimHsSupport(env)`

- **It must:** SPEC 4 WO-09: `{ok: !!(env.secure && env.webgl2), notes}`, the notes for each false item in the order
  and words of the SPEC.
- **User path:** Headset mode's message when it starts (WO-10).
- **May use:** nothing.
- **Files:** `src/js/engine/render/headset.js`, `docs/work-orders/v274/v274.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-09 ...`.
- **Score:** 0.

---

## [ ] WO-10 [Claude] The Headset mode in the rendered view

Claude's: it crosses files (the rendered view, walk mode, the settings), draws with three.js (two targets, an off-axis
frustum per eye from WO-05, the correction pass on WO-04's lenses, as `docs/research/experiments/devices-xr/phone-test.html`
measured), asks the motion permission inside the tap, holds the wake lock, saves the viewer settings, and offers the
camera behind. Score 2+2+2+1+2+1 = 10.

---

## [ ] WO-11 [Claude] Tests into tests/unit, modules, the browser check

Move these cases to `tests/unit/headset.test.mjs`, `npm run modules`, the build, and the one browser check of the new
mode (CLAUDE.md Rule #1).

---

## [ ] WO-12 [Claude] The records

QUEUE, PIPELINE, the research note's decisions, Notion.
