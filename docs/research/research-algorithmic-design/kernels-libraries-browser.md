# Algorithmic design: geometry kernels, node-editor libraries and browser limits

Side note for `docs/research/research-algorithmic-design.md`. Question and hypotheses: `00-question.md` (H4, H7 and
the library side of the node editor). Researched 2026-11-14 and 2026-11-15. Upstream code was read as text only:
npm tarballs were downloaded with curl, listed and read; nothing was installed, built or run.

**Status: in progress.** Parts marked "(pending)" are not yet read at the source. This file is extended as the
research goes.

Levels: P = read at the source; S = dependable secondary; U = seen only in a summary. Confidence high / medium / low.

## 1. Summary of findings (so far)

| # | Finding | Level | Confidence |
|---|---|---|---|
| 1 | Manifold's npm package `manifold-3d` is 3.5.5 (published 2026-11-13), Apache-2.0; `manifold.wasm` is 542,744 bytes (204,769 gzip -9), its glue `manifold.js` 82,371 bytes (19,098 gzip -9). The package's unpacked 2.79 MB is mostly an optional CAD worker bundle (1.73 MB) that an adapter would not ship | P (registry metadata, tarball listed and measured here) | High |
| 2 | OCCT through replicad-opencascadejs 1.2.1 (2026-11-06, LGPL-2.1-only): `replicad_single.wasm` 22,942,327 bytes, `replicad_multi.wasm` 22,475,349 bytes. About 42 times Manifold's binary | P (tarball listed here) | High |
| 3 | `opencascade.js` on npm: `latest` is still 1.1.1 of 2020-09-27; the 2.0.0 beta tag was last touched 2023-03-23. Dormant, as `research-usd-brep.md` 4.8 found | P (registry metadata) | High |
| 4 | The repo has already measured the delivery mechanism: a sibling `.wasm` cannot be fetched from `file://` in Chromium, an embedded base64 binary compiles and runs in a Blob-URL worker, `SharedArrayBuffer` is undefined there (`research-usd-brep.md` section 6, e01 and e02). This is not repeated here | P (the repo's own experiments) | High for Chromium |
| 5 | The repo has already measured that `file://` has no service worker and no OPFS in Chromium, and that storage on `file://` differs in each engine (`research-local-storage.md` 4.4) | P (the repo's own experiments) | High for Chromium |
| 6 | Node-editor libraries with a classic-script build and no framework: litegraph.js 0.7.18 (MIT, `build/litegraph.core.min.js` 176,325 bytes, last npm release 2024-01-08), Drawflow 0.0.60 (MIT, `dist/drawflow.min.js` 46,190 bytes, 2024-09-03), Rete 2.0.6 core (MIT, `rete.min.js` 18,496 bytes, but its rendering needs separate plugins). React Flow / xyflow and Flume need React; Baklava needs Vue | P (registry metadata and tarballs listed here) | High for sizes and dependencies; touch support pending |

## 2. Findings by topic

### 2.1 Package facts read from the npm registry and the tarballs (P, 2026-11-14)

All tarballs fetched from `registry.npmjs.org` with curl; sha1 matches the registry's `dist.shasum` in each case.

| Package, version, date | Licence (package.json) | Tarball bytes | sha256 of the tarball (first 16) | Files that matter, bytes |
|---|---|---|---|---|
| manifold-3d 3.5.5, 2026-11-13 | Apache-2.0 (LICENSE file read: Apache License 2.0) | 722,143 | 79854f081b95a552 | `manifold.wasm` 542,744 (gzip 204,769; sha256 b172438703ef72de...); `manifold.js` 82,371 (gzip 19,098); `manifold.d.ts` 61,470; `dist/worker.bundled.js` 1,734,944 (the manifoldCAD worker, optional) |
| replicad-opencascadejs 1.2.1, 2026-11-06 | LGPL-2.1-only | 15,093,004 | 07b6fb17a26a0be2 | `replicad_single.wasm` 22,942,327; `replicad_single.js` 60,483; `replicad_multi.wasm` 22,475,349 |
| replicad 1.2.1, 2026-11-06 | MIT | 1,374,735 | 8c4ce4dc6d7e4575 | `replicad.js` 708,324; `replicad.umd.cjs` 776,245; depends on flatbush, opentype.js |
| opencascade.js 1.1.1, 2020-09-27 (latest); beta 2.0.0-beta.b5ff984 | LGPL-2.1-only | not downloaded (66.7 MB unpacked) | | see `research-usd-brep.md` 4.8: 50,305,130 bytes for the beta's wasm |
| @jscad/modeling 2.13.0, 2026-02-22 | MIT | 340,124 | cc86485bb3e48dba | `dist/jscad-modeling.min.js` 250,793; no dependencies |
| three-bvh-csg 0.0.18, 2026-02-17 | MIT | 221,467 | 9cfc598742c8a072 | `build/index.umd.cjs` 169,425; peers: three, three-mesh-bvh |
| three-mesh-bvh 0.9.18, 2026-11-03 | MIT | 434,105 | b041bf9ab59b90ca | peer: three |
| clipper2-ts 2.0.1-19, 2026-11-07 | BSL-1.0 | 378,007 | e437fd35f7ac6533 | pure TypeScript port; no dependencies |
| clipper2-wasm 0.4.0, 2026-05-18 | BSL-1.0 | 429,138 | 22b3afe094024bd1 | `dist/umd/clipper2z.wasm` 213,643; `clipper2z.js` 54,145 |
| clipper-lib 6.4.2, 2019-11-08 (Clipper 1) | BSL | 49,682 | 634d7d7627939bbe | `clipper.js` 203,786, one classic script |
| polygon-clipping 0.15.7, 2023-12-18 | MIT | 91,226 | 23bdea671a650111 | `dist/polygon-clipping.umd.min.js` 29,106 |
| straight-skeleton 3.0.0, 2026-03-24 | MIT (package) | 681,235 | 66ab400f389445f9 | `dist/index.js` 1,034,461 (pending: what it embeds) |
| earcut 3.2.4, 2026-09-28 | ISC | 34,818 | 2f63624cc056e4f2 | `dist/earcut.min.js` 9,749 |
| verb-nurbs 3.0.3, 2025-04-23 | MIT | not re-downloaded | | see `research-usd-brep.md` 4.8: `build/js/verbHaxe.js` 278,479 bytes, ES5 |
| litegraph.js 0.7.18, 2024-01-08 | MIT | 660,475 | a951ff79919b4e5f | `build/litegraph.core.min.js` 176,325; `litegraph.min.js` 491,365 (with all node packs); `css/litegraph.css` 12,820; no dependencies |
| @comfyorg/litegraph 0.17.2, 2025-08-06 | MIT | 869,481 | 21c459056519b033 | `dist/litegraph.umd.js` 402,538; `litegraph.es.js` 619,240; no dependencies |
| rete 2.0.6, 2025-06-30 | MIT | 47,958 | 3fb8b51360eae433 | `rete.min.js` 18,496; depends on @babel/runtime |
| drawflow 0.0.60, 2024-09-03 | MIT | 15,497 | e587758f8c4e8e02 | `dist/drawflow.min.js` 46,190; `drawflow.min.css` 1,910; no dependencies |
| baklavajs 2.8.1, 2025-11-02 | MIT | 294,216 | 88d7ef9e156fdc42 | `dist/bundle.js` 175,784; renderer is `@baklavajs/renderer-vue` |
| @xyflow/react 12.12.1, 2026-11-02 | MIT | 251,321 | ffd8b20eff216ceb | `dist/umd/index.js` 188,872; peers: react, react-dom |
| flume 1.2.0, 2025-11-05 | MIT | 367,654 | 1c5565a79d99551b | peers: react, react-dom |

### 2.2 What the repo already established (cited, not repeated)

- `docs/research/research-usd-brep.md` (2026-10-31 to 11-01): OCCT builds 23 to 50 MB; Manifold 541 KB, mesh only;
  SMLib (Apache-2.0) built here at 5.76 MB and run from `file://` in a Blob-URL worker; verb-nurbs' ES5 build;
  the app's BSP CSG at `src/js/engine/bim/csg-booleans.js` with `CSG_EPS = 1e-5`, fragile on coplanar faces.
- `docs/research/experiments/kernel-wasm/`: e01 (synthetic wasm of 1, 5, 10 MB embedded as base64, compiled in the
  page and in a Blob-URL worker from `file://`; sibling fetch fails; no SharedArrayBuffer) and e02 (SMLib).
- `docs/research/solidcraft-integration-map.md` (2026-11-13): SolidCraft's Rust port of SMLib; incomplete
  discovery, nothing built.
- `docs/research/research-local-storage.md` 4.4 and 4.7: `file://` storage per engine, no service worker and no
  OPFS on `file://` in Chromium, install rules.

### 2.3 to 2.8 (pending)

Manifold's loader and guarantees; OCCT in the browser; pure-JS alternatives and Clipper2's licence; node editors
(touch, engines); browser platform facts from MDN and the specifications; instancing.

## 3. The pasted advice, line by line (pending)

## 4. What bears on H4 and H7 (pending)

## 5. Counter-evidence (pending)

## 6. Still open (U) (pending)

## 7. Search log

| When | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 2026-11-14 | the repository | `research-usd-brep.md`, `solidcraft-integration-map.md`, `research-local-storage.md` 4.4-4.7, `experiments/kernel-wasm/` | Prior kernel and `file://` findings | Kept, cited |
| 2026-11-14 | registry.npmjs.org | Metadata for 27 package names | 26 answered 200; `csg.js` 404 (Evan Wallace's csg.js is not published under that name) | Kept; csg.js to be read on GitHub |
| 2026-11-14 | registry.npmjs.org | 19 tarballs by curl | All fetched; sha1 equal to the registry's | Kept |

## 8. References (so far)

| Source | Address | What was read | Date | Level |
|---|---|---|---|---|
| npm registry metadata | `https://registry.npmjs.org/<name>` for the packages in 2.1 | `dist-tags`, the latest version's `license`, `dist`, dependencies, `time` | 2026-11-14 | P |
| npm tarballs | `https://registry.npmjs.org/<name>/-/<file>.tgz` | File listings (`tar -tzvf`), sizes, LICENSE of manifold-3d | 2026-11-14 | P |
| This repository | paths in 2.2 | As cited | 2026-11-14 | P |
