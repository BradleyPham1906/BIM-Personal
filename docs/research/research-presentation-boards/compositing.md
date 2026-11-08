# V174 research: compositing, opacity, groups and masks on boards

Part of the V174 "Presentation P1: boards" research (research agent 3 of the phase). This note
covers blend modes, opacity, groups and isolation, and masks: from the specifications, measured in
the browser, and mapped to the V176 exports (PDF, SVG, PNG). Written 2026-11-08 by a research
agent; every source read and every experiment run on that date.

Levels: P = the primary source read itself (the specification's text, an implementation's code, the
compatibility data's own file); S = a dependable secondary source, gap said; U = a search summary or
our own inference not checked (never used for code).

## 1. Abstract

Question: can a board drawn on a canvas 2D context give every element opacity, one of the W3C's 16
blend modes and a mask, with groups that composite as one, and can the same model be written to PDF
and SVG later without changing how it looks? Answer: yes, with three cautions. The canvas keywords
are exactly the 16 `<blend-mode>` values of Compositing and Blending Level 1, and Chromium 153's
results match our own implementation of the W3C formulas within 1 unit of 8 bits (2 for exclusion)
on opaque colours; PDF 32000-1 has the same 16 modes under other names, and SVG/CSS the same
keywords. The cautions: (1) Figma has 18 modes plus pass-through, not 16 (it adds linear burn and
linear dodge, which neither canvas nor PDF has); (2) a group with opacity or a blend mode must be
drawn into its own offscreen canvas, or overlapping children show through each other (measured: 64
units of difference in the overlap); (3) canvas has no luminance mask: it needs a filter
(`ctx.filter`, missing from Safari without a flag) or a pixel loop. Recommendation: keep the
element model as PDF and SVG define it (mode, opacity, group isolated or pass-through, mask alpha or
luminance), draw groups through element-sized offscreen canvases, alpha masks with
`destination-in`, luminance masks baked once to an alpha canvas and cached.

## 2. The question and the hypotheses

Question: what must the V174 board renderer do so that opacity, the 16 blend modes, groups and
masks look right on canvas on every supported browser, and so that V176 can write the same thing to
PDF and SVG?

| # | Hypothesis | Outcome |
|---|---|---|
| H1 | Canvas `globalCompositeOperation` accepts exactly the 16 W3C blend modes (plus the 12 Porter-Duff operators) and Chromium computes them as the W3C formulas say, in gamma-encoded sRGB | Held. 28 keywords accepted; opaque error at most 1.0 (exclusion 1.99) over 12,800 opaque pairs per mode; matches formulas applied to the encoded values, so blending is in sRGB, not linear (exp. a) |
| H2 | Translucent colours match the formulas as closely as opaque ones | Failed in part. Premultiplied error at most 2.8 units in 13 modes, but up to 21 for color-dodge, 11 for color-burn and 8 for saturation near their singular points (source alpha 254, channel near 1); unpremultiplied read-back error up to 21 at alpha 16 from 8-bit storage (exp. a) |
| H3 | An unknown mode string is ignored and the previous mode kept | Held, with a surprise: `"normal"` is accepted but reads back as `"source-over"` in Chromium (the spec says it should read back as given); case, spaces, `plus-lighter`, `linear-burn` ignored (exp. e) |
| H4 | Per-child `globalAlpha` is not group opacity; an offscreen canvas drawn with `globalAlpha` is | Held. Overlap 127,163,63 naive vs 126,227,126 isolated (W3C 128,227,128); max difference 64 (exp. b) |
| H5 | A group drawn through an offscreen canvas with default settings looks identical to drawing the children directly (group invariance) | Held: 0 of 7,200 pixels differ, when drawn at an integer offset; at x + 0.5 it is resampled (180 pixels differ, by up to 128) (exp. b) |
| H6 | The "same 16 modes as Figma" | Failed. Figma's layer blend modes are 18 plus PASS_THROUGH: it adds LINEAR_BURN and LINEAR_DODGE (P, Figma plugin typings) |
| H7 | PDF's soft mask defaults to luminosity | Failed. The soft-mask dictionary's `S` (Alpha or Luminosity) is required, with no default (PDF 32000-1 Table 144). It is SVG/CSS `mask-type` whose initial value is luminance |
| H8 | `clip()` is a hard 1-bit edge | Failed in Chromium: clip edges are anti-aliased like fills (448 partial pixels for a fill, 454 for the clip, alpha differing by at most 1); both leave the same seam where two clipped halves meet (alpha 192, not 255) (exp. c) |
| H9 | A luminance mask on a 2000 x 1400 board costs much more than an alpha mask | Held if recomputed each frame (37 ms by pixels, 34 ms by SVG filter, against 15 ms); not if baked once and cached (16 ms) (exp. c) |
| H10 | 200 elements with non-normal modes stay inside a 60 fps budget (16.7 ms) | Borderline. 9 ms normal, 16 ms random modes, 17 to 23 ms non-separable only; with 20 isolated groups and blended children 19 to 21 ms (exp. d, SwiftShader, headless) |
| H11 | SVG `mix-blend-mode`, `isolation` and `mask` (the V176 SVG path) render as the canvas does | Held in Chromium: opaque pixels identical in all 16 modes; translucent within 5 units; isolation and luminance masks as specified (exp. f) |

## 3. Method

### 3.1 Search log

| Date | Where | What | Outcome |
|---|---|---|---|
| 11-08 | raw.githubusercontent.com w3c/fxtf-drafts (main, master) compositing-1/Overview.bs, css-masking-1/Overview.bs | Bikeshed sources | 404 on both branches (the drafts moved; drafts.fxtf.org/compositing-2 redirects to the CSSWG repository) |
| 11-08 | www.w3.org/TR/compositing-1/ | Compositing and Blending Level 1, CRD 2024-03-21 | read in full as text, P (www.w3.org answered today; it was refused on 2026-10-17) |
| 11-08 | www.w3.org/TR/css-masking-1/, /TR/filter-effects-1/, /TR/SVG2/render.html | Masking (7.10.1, 9.2), feColorMatrix luminanceToAlpha, SVG 2 group rendering and group opacity (3.6) | read, P |
| 11-08 | raw.githubusercontent.com whatwg/html main `source` (8.1 MB) | grep: CanvasCompositing, globalAlpha and globalCompositeOperation setters, drawing model, clip steps, settings | read, P |
| 11-08 | raw.githubusercontent.com mdn/browser-compat-data main (8.1.8) | api/CanvasRenderingContext2D.json; css/properties/mix-blend-mode, isolation, mask-type | read, P for support data |
| 11-08 | raw.githubusercontent.com mdn/content | globalcompositeoperation/index.md | read, S (MDN's prose) |
| 11-08 | opensource.adobe.com PDF32000_2008.pdf | ISO 32000-1:2008 as published free by Adobe; 11.3.5, 11.3.6, 11.4.5, 11.4.6, 11.5.3, 11.6.5, 11.6.6, Table 58, 136, 137, 144, 147 | read through pdftotext, P (two formula glyphs lost, see 4.4) |
| 11-08 | raw.githubusercontent.com figma/plugin-typings master (1.142.0) | plugin-api.d.ts: BlendMode, MaskType, isMask, layer blendMode | read, P |
| 11-08 | raw.githubusercontent.com google/skia main | src/opts/SkRasterPipeline_opts.h (blend stages); LICENSE (BSD) | read, P |
| 11-08 | raw.githubusercontent.com mozilla/pdf.js master | src/core/evaluator.js `normalizeBlendMode`; src/display/canvas.js soft masks and knockout; filter_factory.js; LICENSE (Apache 2.0) | read, P |
| 11-08 | bugzilla.mozilla.org REST, short_desc "globalCompositeOperation", "canvas blend mode", "soft-light", "mix-blend-mode" | bug lists, then comments of 1993150, 1422642, 1345045, 1009317, 1474349 | read, P (as reports) |
| 11-08 | bugs.webkit.org REST, quicksearch "canvas globalCompositeOperation", "canvas filter" | lists, then comments of 209802, 240288, 265095, 221542 | read, P (as reports) |
| 11-08 | issues.chromium.org search | page is a script app; 84 KB shell, no results as text | not reached |
| 11-08 | api.github.com (commit history of BCD) | 403 | refused |

Counter-evidence searched for deliberately: browsers that differ from the formulas (Mozilla 954372
dodge equals burn, worksforme; 1009317 dodge artifacts with shadows), clip with blend modes
(Mozilla 1422642, 1474349, 1151821), unbounded operators (Mozilla 1993150, fixed 2025-11), Safari
operators ignored for text and video (WebKit 265095, 221542), Safari's slow `destination-in`
(WebKit 209802), timing side channels (Mozilla 1345045), and the PDF 2008 text against the W3C
text (section 4.4). Chromium's tracker was not searchable as text (gap).

### 3.2 Experiments

Scripts in `docs/research/experiments/v174-blend/` (data, never a suite), each with its output
beside it (`results-*.txt`):

- `w3c-blend.js`: our own ES5 implementation of the W3C formulas (sections 5.1, 6, 10.1, 10.2).
- `exp-a-modes.js`: 16 modes, 25,600 colour pairs each, two context kinds, against `w3c-blend.js`.
- `exp-b-groups.js`: group opacity, pass-through against isolated, group blend, invariance.
- `exp-c-masks.js`: clip, alpha mask by `destination-in`, luminance mask by pixels and by SVG filter;
  N = 30 timed runs after 3 warm-up; clip anti-aliasing, seams and unbounded operators.
- `exp-d-cost.js`: 200 elements, modes and groups, N = 30 frames after 3 warm-up.
- `exp-e-keywords.js`: 45 strings into `globalCompositeOperation`, out-of-range `globalAlpha`.
- `exp-f-svg-parity.js`: SVG with `mix-blend-mode`, `mask`, `isolation`, drawn into a canvas, against
  canvas 2D.

Environment: Playwright 1.63.0 (Node v22.23.4), its Chromium 153.0.8010.12 headless shell
(`/opt/pw-browsers/chromium_headless_shell-1243`), Linux x86_64, 4 vCPU Intel Xeon 2.10 GHz; the
WebGL renderer reports ANGLE on SwiftShader (software GPU). Firefox, Safari, iOS and Android are not
available here: for them the note relies on BCD, the bug trackers and the specifications.

### 3.3 Independent check

Not yet done. A second reader should re-check the facts marked for it in section 12.

## 4. Findings

### 4.1 The blend formulas (W3C Compositing and Blending Level 1) (P, high)

Edition: W3C Candidate Recommendation Draft, 21 March 2024 (previous CR 13 January 2015); editor
Chris Harrelson (Google), former editors Rik Cabanier (Adobe) and Nikos Andronikos (Canon).

- `<blend-mode>` = normal | darken | multiply | color-burn | lighten | screen | color-dodge |
  overlay | soft-light | hard-light | difference | exclusion | hue | saturation | color |
  luminosity (3.4.1): 16 keywords.
- Canvas (section 4): `globalCompositeOperation` takes `<blend-mode> | <composite-mode>`, with
  `<composite-mode>` = clear | copy | source-over | destination-over | source-in | destination-in |
  source-out | destination-out | source-atop | destination-atop | xor | lighter (12 operators;
  `destination` was removed in 2014). Initial source-over.
- General formula (6): blend in place, `Cs' = (1 - ab) x Cs + ab x B(Cb, Cs)`, then composite
  `co = as x Fa x Cs' + ab x Fb x Cb`, with Fa, Fb from the Porter-Duff operator (source-over: Fa = 1,
  Fb = 1 - as). Written out for source-over (10): `ao = as + ab(1 - as)`;
  `ao x Co = as(1 - ab)Cs + as x ab x B(Cb, Cs) + (1 - as) ab x Cb`.
- Blending must not use premultiplied values; the mixing result is clamped (10).
- Separable B (10.1): normal Cs; multiply Cb x Cs; screen Cb + Cs - Cb x Cs; overlay =
  HardLight(Cs, Cb); darken min; lighten max; color-dodge: 0 if Cb = 0, else 1 if Cs = 1, else
  min(1, Cb / (1 - Cs)); color-burn: 1 if Cb = 1, else 0 if Cs = 0, else 1 - min(1, (1 - Cb) / Cs);
  hard-light: Multiply(Cb, 2Cs) if Cs <= 0.5 else Screen(Cb, 2Cs - 1); soft-light: Cb - (1 - 2Cs) Cb
  (1 - Cb) if Cs <= 0.5 else Cb + (2Cs - 1)(D(Cb) - Cb), D(Cb) = ((16Cb - 12)Cb + 4)Cb if Cb <= 0.25
  else sqrt(Cb); difference |Cb - Cs|; exclusion Cb + Cs - 2 Cb Cs.
- Non-separable (10.2): Lum(C) = 0.3 R + 0.59 G + 0.11 B; ClipColor pulls a colour back into
  [0, 1] along its luminance; SetLum adds l - Lum(C) then clips; Sat = max - min; SetSat rescales
  mid and max, min = 0. hue = SetLum(SetSat(Cs, Sat(Cb)), Lum(Cb)); saturation =
  SetLum(SetSat(Cb, Sat(Cs)), Lum(Cb)); color = SetLum(Cs, Lum(Cb)); luminosity = SetLum(Cb,
  Lum(Cs)).
- Groups (8): a group composites its elements onto an initial backdrop, then the result onto the
  group backdrop. Non-isolated: the initial backdrop is the group backdrop; isolated: transparent
  black. Default groups are invariant (A + (B + C) = (A + B) + C); isolation, a non-normal mode or a
  non-source-over operator can break that. In SVG, opacity, filters, 3D transforms, blending and
  masking make a group isolated (3.3); in HTML every stacking context is isolated (3.2).
- An isolated group whose bottom element uses a backdrop-dependent operator (destination-in,
  source-in, ...) composites to nothing (9.2).
- Order (3.1): filter first, then clipping, masking, blending and compositing.
- Security: blending must take the same time whatever the pixel values (timing attacks; Mozilla
  1345045 is the case that made this a rule).
- Knockout groups were removed from this specification in 2013; they exist only in PDF.

### 4.2 Canvas 2D (WHATWG HTML) (P, high)

- `globalAlpha` setter: if the value is infinite, NaN or outside 0.0 to 1.0, return (ignored);
  initial 1.0. Measured: 1.5, -0.1, NaN, Infinity ignored; `null` becomes 0 by WebIDL conversion
  (a trap: the app must never assign an unchecked value).
- `globalCompositeOperation` setter: if the value is not identical to one of the `<blend-mode>` or
  `<composite-mode>` values, return; else set. So case-sensitive, no trimming; unknown values keep
  the previous operator. Both are saved and restored with `save()`/`restore()` (measured).
- Drawing model, in order: render the shape onto an infinite transparent bitmap (A); convert to the
  context's colour space; multiply alpha by global alpha; apply the filter if not "none" (B); draw
  the shadow from B (C) and composite C within the clipping region; composite B within the clipping
  region with the current operator. So opacity is applied before the filter, the shadow is
  composited with the same blend mode as the shape, and every operator is applied over the whole
  clipping region, not only the shape: `source-in`, `destination-in`, `copy` clear what lies outside
  the shape (measured: inside the clip but outside the shape the board became transparent).
- `clip()` intersects the clipping region with the path (nonzero or evenodd); there is no union or
  subtraction (the spec keeps that as a v6 idea). Restored only by `restore()`.
- Context settings: `colorSpace` "srgb" (default) or "display-p3", `willReadFrequently`.
- There is no layer API in the specification today: grouping is the app's offscreen canvas.

### 4.3 Browser support (P from BCD 8.1.8, high for canvas, medium per mode)

| Feature | Chrome | Edge | Firefox | Safari / iOS |
|---|---|---|---|---|
| `globalAlpha`, `globalCompositeOperation` | 1 | 12 | 1.5 | 2 |
| `ctx.filter` (needed for a filter-based luminance mask) | 52 | 79 (mirror) | 49 | 18 behind the "Canvas Filters" preference only |
| `clip(path)` | 36 | 14 | 31 | 7 |
| CSS `mix-blend-mode`, 12 separable | 41 | 79 | 32 | 8 |
| CSS `mix-blend-mode` hue, saturation, color, luminosity | 41 | 79 | 32 | 10 |
| `mix-blend-mode` on SVG elements | 41 | 79 | 32 | no |
| `plus-lighter` (CSS only) | 100 | 100 | 99 | 9.1 |
| `isolation` | 41 | 79 | 36 | 8 |
| `mask-type` luminance/alpha | 24 | 79 | 35 | 7 |

BCD has no sub-entries for each canvas operator: it records `globalCompositeOperation` as a whole.
That the 16 blend keywords work in canvas on every engine is therefore S: MDN's page lists them all
without exceptions, and the bug trackers show engine-specific bugs rather than missing modes (a
second reader should look for a WPT run of `2d.composite.*` per browser). The Safari gap for
`ctx.filter` is the one with consequences (section 4.6); pdf.js's own code says older Safari accepts
`url(#id)` filters silently and draws unfiltered, and detects it.

### 4.4 PDF 32000-1:2008 (P from the Adobe-published text; two glyphs S)

- Blend mode names (Table 136, 137): Normal, Compatible (= Normal, deprecated), Multiply, Screen,
  Overlay, Darken, Lighten, ColorDodge, ColorBurn, HardLight, SoftLight, Difference, Exclusion; Hue,
  Saturation, Color, Luminosity. Set by the ExtGState `BM` key (name, or array of names: the first
  one the reader knows is used); `CA` stroking alpha and `ca` non-stroking alpha; `SMask` the soft
  mask; `AIS` alpha-is-shape; `TK` text knockout (Table 58).
- The formulas are the W3C's, with two differences in the 2008 text: ColorDodge gives 1 when cs = 1
  even with cb = 0 (W3C gives 0), and ColorBurn gives 0 when cs = 0 even with cb = 1 (W3C gives 1).
  So a black backdrop under white in color-dodge, and white under black in color-burn, differ by the
  whole range between a 2008 reader and a W3C one. Chromium follows the W3C (measured) and so does
  Skia's code. The SoftLight `D(x)` for x > 0.25 shows only "x" in the extracted text: the radical is
  a glyph lost by pdftotext; the W3C text, Skia's code (`sqrt_(m)`) and our match to Chromium say
  sqrt (S for the PDF reading; ISO 32000-2 was not read).
- Non-separable modes in PDF use Lum = 0.30 R + 0.59 G + 0.11 B, as the W3C; for CMYK the K
  component takes special rules (not needed: boards are RGB).
- Interpretation of alpha (11.3.6): the same weighted formula as W3C section 10.
- Isolated groups (11.4.5): initial backdrop transparent. Knockout groups (11.4.6): each element
  composites with the group's initial backdrop, so the topmost object wins, colour and opacity.
  Group attributes (Table 147): `/S /Transparency`, `/CS` colour space, `/I` isolated (default
  false), `/K` knockout (default false).
- Soft masks (11.6.5, Table 144): `/S` is required, `Alpha` or `Luminosity`, no default; `/G` the
  group; `/BC` the backdrop colour for Luminosity (default black); `/TR` transfer function
  (default Identity). Outside the group's box the mask is the transfer of 0 (Alpha) or of BC's
  luminosity. For DeviceRGB the luminosity is Y = 0.30 R + 0.59 G + 0.11 B, on device values, no
  gamma (11.5.3). A soft mask replaces the previous one; it does not intersect as a clip does.
- Difference and Exclusion are the only separable modes that are not "white-preserving" (11.7.4.2, note 2).

### 4.5 SVG and CSS (P, high)

- Same keywords as canvas in `mix-blend-mode`; `isolation: auto | isolate`; `opacity` on a `g` is
  group opacity, rendered "into an RGBA offscreen image" and then blended as a whole (SVG 2 3.6.1).
- `clip-path`: a 1-bit silhouette "with the possible exception of anti-aliasing along the edge"
  (CSS Masking 6). `mask`: always an isolated group; `mask-type: luminance | alpha`, initial
  luminance (9.2). Luminance: optionally to linearRGB if `color-interpolation` says so, then the
  luminance-to-alpha coefficients of feColorMatrix, times alpha (7.10.1). Filter Effects 1 gives
  0.2126, 0.7152, 0.0722 (SVG 1.1 gave 0.2125, 0.7154, 0.0721). Measured in Chromium: grey 128 under
  a default mask gives alpha 128, so it computes on sRGB values, not linear.
- Note the two luminance weightings: PDF and the non-separable blend modes use 0.30/0.59/0.11; CSS
  and SVG masks use 0.2126/0.7152/0.0722. A luminance mask exported from the board will be a little
  different in PDF than in SVG unless the PDF mask is pre-baked (section 5).

### 4.6 Masks on canvas (P for the API, measured for cost)

| Kind | How on canvas | Edge | Cost on 2000 x 1400, median (p90), default context |
|---|---|---|---|
| Vector clip | `save; path; clip(); draw; restore` | anti-aliased in Chromium, same as a fill | 3.9 ms (4.2), drawImage alone 2.0 |
| Alpha mask | element into an offscreen canvas, `destination-in` with the mask canvas, draw the offscreen | soft, any shape | 15.4 ms (16.2) |
| Alpha mask from a gradient | `destination-in` then `fillRect` with the gradient | soft | 23.8 ms (25.4) |
| Luminance mask, pixels each frame | getImageData, alpha = lum x a, putImageData, then as alpha | soft | 37.3 ms (59.8) |
| Luminance mask, cached | the same, baked once | soft | 15.9 ms (17.3) |
| Luminance mask, SVG filter each frame | `ctx.filter = 'url(#l2a)'` with feColorMatrix luminanceToAlpha | soft | 33.7 ms (43.8); identical alpha to the pixel loop |

Prior art: pdf.js draws PDF soft masks exactly so: the mask group into a canvas, a luminosity
filter, `destination-in`, with a pixel-loop fallback for browsers that ignore the filter (Apache
2.0, read as text). Figma's masks are ALPHA, VECTOR or LUMINANCE, and a mask masks all its later
siblings up to the end of its group (plugin typings), the same scoping a board needs.

### 4.7 What can go wrong (counter-evidence) (P as reports; confidence medium)

- Precision: Chromium's raster pipeline works on premultiplied values with fast reciprocals
  (`rcp_fast` in Skia's dodge, burn and clip_color), which explains exp. a's larger translucent
  errors near the singular points of dodge, burn and SetSat. Exclusion of two near-black values
  gives 0 where the formula gives 1.99 (8-bit rounding).
- Colour space: blending is done on gamma-encoded sRGB values in canvas, SVG and PDF device RGB
  alike; none of them blends in linear light. Consistent, but not physically correct; a
  `display-p3` canvas would blend in P3 values (not tested).
- Firefox: 1422642 (unconfirmed, 2017) and 1474349 (new, 2018) report blend or `lighter` results
  wrong under a clip; 1151821 (fixed 2015) the same regression; 1993150 (fixed 2025-11) unbounded
  operators unsupported in its accelerated canvas until then; 1009317 colour-dodge artifacts with
  shadows; 954372 dodge equals burn (worksforme).
- Safari: 265095 operators ignored for `fillText`/`strokeText` (new, 2023); 221542 `source-in` not
  applied to video (new); 240288 `copy` gives wrong results (new, 2022); 209802 `destination-in`,
  `source-in`, `source-out`, `source-atop` ten times slower than `destination-out` (new, 2020, macOS).
  The last argues for testing the mask path on a Mac before release.
- Chromium: its tracker could not be searched as text from here (gap); the measured behaviour is the
  evidence for Chromium.

## 5. The alternatives compared

Criteria, set before the comparison: right result for group opacity and blends (the spec's
model); cost per frame on a 2000 x 1400 board with 200 elements; works on Safari; maps one to one
to PDF and SVG for V176.

### 5.1 Groups

| Option | Correct | Cost (exp. d) | Safari | PDF / SVG |
|---|---|---|---|---|
| A. Per-child globalAlpha, children drawn on the board | no for opacity < 1 (overlaps show) | 9 ms | yes | not what PDF/SVG draw |
| B. Isolated offscreen sized to the group's box | yes | 9 to 12 ms (normal), 19 to 21 ms (blended children, group multiply) | yes | Form XObject `/I true`; `g` with opacity or `isolation:isolate` |
| C. Offscreen the size of the board per group | yes | 90 to 100 ms | yes | same as B |
| D. Pass-through (no offscreen) when the group has opacity 1 and mode normal | yes for that case (invariance, 0 pixels differ) | 9 ms | yes | Form XObject `/I false`; plain `g` |

Recommendation: D when the group is default, B otherwise; never C. Offscreen canvases are kept per
group (or pooled by size) and drawn at integer device offsets. Reusing one scratch canvas for 200
elements cost 76 ms against 28 ms with one canvas each (each reuse after a draw forces a copy).

### 5.2 Masks

| Option | Correct | Cost | Safari | PDF / SVG |
|---|---|---|---|---|
| clip() | vector masks only | 4 ms | yes | `W n` clip path; `clip-path` |
| destination-in alpha mask | alpha masks | 15 ms | yes (slow path reported, WebKit 209802) | SMask `/S /Alpha`; `mask-type:alpha` |
| Luminance by `ctx.filter` each frame | yes | 34 ms | no (flag only) | SMask `/S /Luminosity`; `mask` default |
| Luminance baked by pixels once, then alpha | yes | 16 ms per frame, 37 ms when the mask changes | yes | as alpha (pre-baked), or as luminosity |

Recommendation: vector masks by `clip()`; alpha masks by `destination-in`; luminance masks baked to
an alpha canvas with the pixel loop (works everywhere, same numbers as the filter) and re-baked only
when the mask element changes. What would change it: Safari shipping `ctx.filter` (then the filter
is simpler), or a mask that animates every frame (then the 37 ms matters).

## 6. The experiments (raw numbers)

(a) Blend modes, 25,600 pairs per mode (12,800 opaque; 12,800 with alpha in 255/254/192/128/64/16),
same numbers for the default and the `willReadFrequently` context. Max error in 8-bit units:

| Mode | Opaque max | Opaque mean | Translucent premultiplied max |
|---|---|---|---|
| normal, darken, lighten, difference | 0.00 | 0.000 | 1.87, 1.87, 1.71, 2.71 |
| multiply | 1.00 | 0.530 | 1.74 |
| screen | 0.50 | 0.356 | 1.74 |
| overlay, hard-light | 0.99 | 0.51 | 1.75, 2.19 |
| color-dodge | 0.50 | 0.258 | 21.23 |
| color-burn | 0.51 | 0.223 | 10.60 |
| soft-light | 0.50 | 0.356 | 1.46 |
| exclusion | 1.99 | 1.061 | 2.83 |
| hue, saturation, color, luminosity | 0.50 | 0.28 to 0.33 | 2.55, 8.11, 1.50, 1.48 |

Unpremultiplied read-back error for translucent pairs reached 4.5 to 21 (8-bit premultiplied
storage at alpha 16). Edge pairs: dodge black under white gives 0 (W3C), burn white under black
255 (W3C), hard-light at source 128 takes the screen branch (128/255 > 0.5), hue of red on grey
gives grey.

(b) Groups over white and a blue band: naive overlap 127,163,63 (W3C chain 128,164,64), isolated
126,227,126 (W3C 128,227,128); over blue 64,132,63 vs 0,164,126; 6,000 of 7,200 pixels differ, by up
to 64. Multiply children over blue: pass-through red-only area 0,0,0; isolated 255,0,0 (2,400
pixels differ by 255). Isolated group drawn with multiply at 0.5 over blue: 0,114,127 (W3C
0,114,128). Invariance: 0 pixels differ. Offset x + 0.5: 180 pixels differ, by up to 128.

(c) and (d): the tables in 4.6 and 5.1; full output in `results-c-masks.txt`, `results-d-cost.txt`.
Frame times for (d), default context, median (p90) ms: normal 9.0 (9.1); random non-normal modes
15.9 (21.3); non-separable only 22.6 (24.3) on the second run, 16.9 (21.7) on the first; 20
box-sized groups 12.0 (13.8); blended groups 18.6 (19.6); board-sized groups 97.6 (111.3); 200
isolated elements with a shared scratch 75.9 (91.5), with their own canvases 27.5 (31.5).

(e) Keywords: all 28 grammar values accepted; `normal` read back as `source-over`; ignored:
plus-lighter, plus-darker, darker, linear-burn, linear-dodge, pass-through, Multiply, MULTIPLY,
leading or trailing space, colorDodge, ColorDodge, color_dodge, over, foo, empty, destination. A
draw after an ignored value uses the previous mode (difference: 55,155,205). No setter threw.

(f) SVG against canvas, 400 pairs per mode: opaque pixels identical in all 16; translucent within
5 (dodge), 4 (burn), 3 (hue), 2 (others). Default mask: grey 128 gives 128, alpha-type mask at 0.25
gives 64, red gives 54. A `g` without isolation lets a multiply child darken the backdrop (0,0,0);
`isolation:isolate` keeps it red (255,0,0).

## 7. Edges

- `normal` reads back as `source-over` in Chromium: compare with the stored value, never with the
  context's read-back. Store the element's mode as the W3C keyword; translate `normal` to
  `source-over` (as pdf.js does for PDF's Normal and Compatible).
- Figma's LINEAR_BURN and LINEAR_DODGE have no canvas or PDF operator (`lighter` is Porter-Duff plus,
  applied to alpha too, not linear dodge); a Figma import would have to approximate or drop them.
  PASS_THROUGH is a group setting, not a blend mode.
- Dodge with cb = 0 and cs = 1, burn with cb = 1 and cs = 0: W3C and PDF 2008 disagree (4.4).
- Group opacity 1 and mode normal: no offscreen needed (invariance); any other opacity, a mode, a
  mask or a filter on the group: offscreen. A blended child inside a pass-through group blends with
  the board beneath (W3C's paper aeroplane example).
- `source-in`, `destination-in`, `copy` and `destination-atop` clear outside the shape within the
  clip: use them only inside an offscreen mask canvas, never on the board.
- An isolated group whose first element is `destination-in` composites to nothing.
- Shadows composite with the shape's blend mode (drawing model); a shadow under a multiply element
  is multiplied too, while Figma lets an effect have its own blend mode.
- `globalAlpha = null` sets 0; out-of-range values are ignored silently.
- An offscreen drawn at a fractional device offset is resampled (blurred edges).
- Clip seams: two clips meeting on a pixel boundary leave alpha 192, not 255 (conflation).
- Luminance coefficients differ between PDF (0.30/0.59/0.11) and SVG/CSS (0.2126/0.7152/0.0722).

## 8. What the app already has

Not read for this side of the research (another agent reads the app's code; the coordinator asked
this agent for the specifications and the measurements). `grep -rn 'globalCompositeOperation' src/`
is where a reader should start.

## 9. Risks and threats to validity

- One engine measured: Chromium 153 in a headless shell on SwiftShader. A real GPU would change the
  timings (likely faster) and could change rounding (Skia's GPU path is not the raster pipeline).
- The two context kinds gave identical results in exp. a, so the "default" context may also have
  rasterised on the CPU here; the GPU path is untested.
- Timings include one `getImageData` per frame to flush the work; real frames do not read back.
- Phone and tablet costs not measured (a 2000 x 1400 offscreen per group is memory as well as time:
  11.2 MB each).
- The PDF side was read, not rendered: no PDF reader was run here.

## 10. What is still open (U)

- Per-browser support of each canvas blend keyword: BCD lacks it; check WPT `2d.composite` results.
- Safari's and Firefox's numeric agreement with the formulas, and Safari's `destination-in` cost.
- Chromium's own bug tracker (not readable as text from here).
- ISO 32000-2 (PDF 2.0): whether it corrects ColorDodge and ColorBurn to the W3C reading; the
  SoftLight radical in the 2008 text (glyph lost in extraction).
- The fxtf-drafts Bikeshed sources (404); the TR text was used instead.

## 11. The owner's decisions

1. Blend modes: the W3C's 16 (canvas, PDF and SVG all have them), or also Figma's linear burn and
   dodge, which would need per-pixel work on canvas and could not be written to PDF as a mode?
2. Groups: offer "pass-through" and "isolated" as Figma does (pass-through the default), or always
   isolate a group that has any setting?
3. Luminance masks: allow them (baked, re-baked when the mask changes), or alpha and vector only in
   V174?
4. Export of luminance masks: write PDF `/Luminosity` (PDF's weights) or pre-bake to `/Alpha` so PDF
   and SVG match the board exactly?

## 12. References

- W3C, Compositing and Blending Level 1, Candidate Recommendation Draft 2024-03-21,
  https://www.w3.org/TR/compositing-1/ (P, read in full 2026-11-08). Second reader: sections 4, 6,
  8, 9.1, 10.1, 10.2.
- WHATWG, HTML Living Standard, source file, https://raw.githubusercontent.com/whatwg/html/main/source
  (P, 2026-11-08): CanvasCompositing, the globalAlpha and globalCompositeOperation setters, Drawing
  model, clip steps, CanvasRenderingContext2DSettings. Second reader: the two setters, the drawing model.
- W3C, CSS Masking Module Level 1, CRD 2021-08-05, https://www.w3.org/TR/css-masking-1/ (P,
  2026-11-08): 6 (clip paths), 7.10 (mask processing), 9.2 (mask-type).
- W3C, Filter Effects Module Level 1, https://www.w3.org/TR/filter-effects-1/ (P, 2026-11-08):
  feColorMatrix luminanceToAlpha matrix.
- W3C, SVG 2, Rendering model, https://www.w3.org/TR/SVG2/render.html (P, 2026-11-08): 3.6, 3.6.1.
- ISO 32000-1:2008 (PDF 1.7), Adobe's free copy,
  https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf (P, 2026-11-08):
  Table 58, 11.3.5 with Tables 136-137, 11.3.6, 11.4.5, 11.4.6, 11.5.3, 11.6.5 with Table 144, 11.6.6
  with Table 147. Second reader: ColorDodge, ColorBurn, SoftLight D(x), Table 144's S.
- MDN browser-compat-data 8.1.8, api/CanvasRenderingContext2D.json, css/properties/mix-blend-mode.json,
  isolation.json, mask-type.json, https://github.com/mdn/browser-compat-data (P, 2026-11-08).
- MDN content, CanvasRenderingContext2D.globalCompositeOperation,
  https://github.com/mdn/content (S, 2026-11-08).
- Figma, plugin-typings 1.142.0, plugin-api.d.ts (BlendMode, MaskType, BlendMixin.isMask,
  layer blendMode), https://github.com/figma/plugin-typings (P, 2026-11-08).
- Google, Skia main, src/opts/SkRasterPipeline_opts.h (blend stages), BSD licence,
  https://github.com/google/skia (P, read as text 2026-11-08).
- Mozilla, pdf.js master, src/core/evaluator.js (normalizeBlendMode), src/display/canvas.js (soft
  masks, knockout), src/display/filter_factory.js, Apache 2.0, https://github.com/mozilla/pdf.js (P,
  read as text 2026-11-08).
- Mozilla Bugzilla 1993150, 1422642, 1474349, 1151821, 1345045, 1009317, 954372,
  https://bugzilla.mozilla.org (P as reports, 2026-11-08).
- WebKit Bugzilla 209802, 240288, 265095, 221542, https://bugs.webkit.org (P as reports, 2026-11-08).
- Refused or not reached on 2026-11-08: raw.githubusercontent.com w3c/fxtf-drafts compositing-1 and
  css-masking-1 (404), api.github.com (403), issues.chromium.org (script page, no text).
