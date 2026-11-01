# NVIDIA's SMLib (USD BRep) as the kernel for Freeform: research

Phase: V181-V187, Freeform F1-F7, with the Parametric Design Foundation (#44). Researched 2026-10-31 and
2026-11-01, under `reference/research-protocol.md`. Status: **research in progress**. The read-only research
and experiment e01 are done. The build experiment (e02) waits on the owner's approval
(`reference/reuse-first-integration.md`), and so does the separate second reader.

## 1. Abstract

**The question.** On 2026-10-08 NVIDIA released SMLib, a commercial NURBS B-rep kernel it bought with Solid
Modeling Solutions, as USD BRep, under Apache-2.0. IFClite runs it in a browser. Can it be the geometry kernel for
the app's Freeform group: NURBS curves and surfaces, sweeps, lofts, fillets, shells and parametric solids?

**The answer.** It covers the operations, and its licence fits. It is not ready for us now, for three reasons:
- **Robustness.** It is a 1.0 release three weeks old, with 22 open issues. Unions, differences and
  fillet-on-fillet, the operations a BIM app leans on, are among them, and one is a regression in 1.0.1. Its own
  list of known issues has crashes with no workaround.
- **No build to reuse.** NVIDIA publishes no WebAssembly build. The one browser build there is, IFClite's, is
  unreleased, exposes about ten operations and waits on IFClite's own licence review.
- **The delivery contract.** Any C++ kernel arrives as a WebAssembly binary. From `file://` that binary has to be
  embedded in the page as base64 (measured, e01), and it would be the first binary dependency in an ES5,
  zero-dependency app.

**The recommendation.**
- Build F1, NURBS curves and surfaces, in the app's own ES5, with verb-nurbs (MIT, ES5) as the candidate to
  reuse.
- Leave the choice of solid kernel to the phases that need fillets and shells. By then SMLib can be measured
  (e02) and re-read at a later release, and set against OCCT, the only open kernel that does all of it in a
  browser today.

## 2. The question and the hypotheses

The question: which kernel, if any, should the Freeform group build on, and is SMLib it?
A good answer decides whether we adopt SMLib now, later or never, and what F1 is built on.

| # | Hypothesis | Outcome | Evidence |
|---|---|---|---|
| H1 | SMLib has the operations F1-F7 need: NURBS curves and surfaces, Booleans, fillets, sweeps, lofts, shell and offset, tessellation | **Held** | SM_API's headers (4.6) |
| H2 | SMLib is robust enough today for BIM solids (unions of wall joints, openings, fillets) | **Failed** | KNOWN_ISSUES.md; issues #34, #35, #29 (4.2) |
| H3 | A WebAssembly kernel can run in the one-file build opened from `file://`, in a Worker | **Held as a mechanism**, with SMLib's own size not measured | e01 (6) |
| H4 | A browser build of SMLib exists to reuse unchanged | **Failed** | None from NVIDIA. IFClite's is unreleased and partial (4.5) |
| H5 | SMLib compiled to WebAssembly is smaller than OCCT's (23 to 50 MB) | **Open** | Not built: e02 waits on approval |
| H6 | SMLib's licence lets it be bundled in a public one-file app | **Held** | Apache-2.0 throughout the kernel (4.7) |
| H7 | SMLib runs on a phone within iOS's WebAssembly memory | **Open** | WebKit bug 269777 puts the reliable ceiling near 300 MB; not tested here |

## 3. Method

**Sources, by kind:**
- **Upstream code read as text:** usd-brep at `3fd5b95` (2026-10-22, v1.0.1), IFClite at `9e3e8cf`
  (2026-10-31), and shallow clones of OCCT, opencascade.js (donalffons and taucad), replicad, Manifold, truck,
  Fornjot, verb, Chili3D and CADmium.
- **Published artefacts:** npm tarballs, with their `.wasm` sizes measured and gzipped here.
- **Project pages:** the issue trackers of usd-brep, replicad, truck and Manifold.
- **Vendor and practitioner documents:** ocjs.org's file-size page, libcascade's BENCHMARKS.md, and Zoo's v1 post.
- **Bug trackers:** WebKit bug 269777.
- **Press:** DEVELOP3D and 3Druck on the release.

**The search log.** Two research agents ran in parallel, one on the case against SMLib and one on the
alternatives. Their logs, raw downloads and reports are kept outside the repository, as the policy asks. Every
search in them is summarised in section 12, by source.
- **Blocked:** github.com's API and HTML to curl and gh (HTTP 403 in this session). Those pages were read
  through the fetch tool instead (marked P-wf: primary pages, read as a digest).

**Experiments.**
- **e01** (`reference/experiments/kernel-wasm/e01_file_origin_wasm.js`): run, 5 runs at each size.
- **e02**, the Emscripten build of SMLib: not run. It waits on the owner, and the environment's sandbox
  refused to install Emscripten without that approval (section 11).

**The independent check.**
- I re-read every fact the recommendation rests on against its source:
  - CONTRIBUTING.md line 6;
  - `SmMessages.cpp` 581-609, which calls `exit(-1)`;
  - no STEP reader in SMLib or SM_API;
  - IFClite's CMakeLists.txt lines 68-84;
  - IFClite's `docs/guide/retained-installation.md` line 3, "after the human licence review";
  - the six `.wasm` sizes, re-measured with gzip -9.
- All were confirmed.
- **Still to do:** the separate second reader the protocol asks for, run with e02.

## 4. Findings

### 4.1 What it is (P, high)
- **The repository.** USD BRep (`github.com/NVIDIA-Omniverse/usd-brep`) holds:
  - the SMLib kernel (`source/SMLib`, 969,048 lines in 463 files);
  - a C API (`source/SM_API`, 12,612 lines in 28 files);
  - an OpenUSD schema for solids (`BrepArray`), a Python API, a healer, a validator, a tessellator, and
    converters to and from OpenCASCADE.
- **Versions.** 1.0.0 on 2026-10-08 and 1.0.1 on 2026-10-21 (CHANGELOG.md).
- **Lineage.** The NURBS core is NLib, "incorporated into SMLib"
  (`.agents/skills/smlib-kernel-operations/references/lifetime-context-cache.md` 70-73). Its code cites The
  NURBS Book (Piegl and Tiller), chapters 9 and 10.4.
- **History (S, medium).** Solid Modeling Solutions (1998), NLib bought from GeomWare (2001), NVIDIA's
  acquisition (May 2022). These come from DEVELOP3D and Wikipedia; no NVIDIA announcement was found. ClassCAD
  (AWV Informatik) is a user, per AWV's CEO quoted by DEVELOP3D.

### 4.2 Robustness (P, high)
**KNOWN_ISSUES.md at v1.0.1:**
- healing can report success after a failed repair;
- closed and periodic surfaces (spheres, tori) can be mis-repaired, with no workaround;
- `shell_brep` can return a result that is not a solid;
- `stitch_brep_with_face` crashes on every input tried;
- `brep_relationship` reports a shallow overlap as touching;
- tessellation winds triangles inside out next to fillets, and puts long thin triangles at sphere poles.

**CHANGELOG 1.0.1** fixed about 50 bugs, in four groups:
- Booleans: 11, including writes to freed memory, results that changed from run to run, and lost operands;
- sweeps: 5;
- fillets: 7;
- healing: 11.

It also stopped fused multiply-add on aarch64, which had changed Boolean results there. That is a sign the
results depend on floating-point details.

**The issue tracker (P-wf, 2026-11-01):** 36 issues, 22 open. Among the open:
- **#34:** a mitre-joint union fails validity after only a translation. It is a regression in 1.0.1, confirmed by
  a maintainer. This is exactly a wall joint.
- **#35:** a difference returns an empty solid.
- **#29:** filleting an edge made by a fillet fails.
- **#37:** mirror and scale transforms.
- **#10:** shell results differ from run to run.
- **#22:** hangs.

### 4.3 Governance (P, high)
- "USD BRep is currently not accepting external code contributions" (CONTRIBUTING.md line 6). Issues are
  accepted.
- History is one squashed commit, with two tags. There is no WebAssembly, browser or mobile target, and the
  maintainers declined an Android port in #31.
- So a fix we needed would live in our own fork until NVIDIA made it.

### 4.4 Porting to WebAssembly (P, high, except where marked)
**What helps:**
- No x87, SIMD, setjmp, alloca or OpenMP.
- TBB appears only under `#ifdef SM_USE_TBB`, which the shipped build leaves off.
- Operations run on one thread.

**What hurts:**
- `exit(-1)` on some errors (`SmMessages.cpp` 581-703), which would end the whole module.
- A process-global context with "unlocked mutable shared state". `.agents/operations/concurrency.md` says the
  unit of concurrency is the process, and a shared-memory WebAssembly worker counts as a thread. So it needs one
  unshared module per Worker, every call serial, and a restart after any crash.
- TCHAR strings in about 1,300 lines (S: compiles under Emscripten as char, not tested).

### 4.5 IFClite's browser build (P, high)
**Where it lives.** `native/smlib-adapter/` in IFClite, MPL-2.0:
- It pins usd-brep `c9c5979`, unpatched.
- It compiles all of `SMLib/src` and `SM_API/src`.
- Its CMakeLists.txt (68-84) links with Emscripten 4.0.15: `-sMODULARIZE=1 -sEXPORT_ES6=1`, `-fexceptions`,
  `-sALLOW_MEMORY_GROWTH=1`, `-sSTACK_SIZE=8388608`. There are no threads and no SINGLE_FILE.
- The output is an ES module plus a `.wasm`, loaded into a module Worker served over HTTPS.

**What its C ABI exposes:**
- box, cylinder, Booleans (on copies), copies, volume, a manifold check, tessellation;
- two sweeps: a planar region with holes, and a disk along a B-spline.

**What it refuses or leaves out:** fillets, shells, lofts and healing. A kernel failure "taints" the module, and
the process has to be thrown away.

**Its status.** It is off by default. Curved routes open only after runtime checks pass. Its installation guide is
"for explicitly qualified builds after the human licence review". No size is published.

**Reuse.** Its files are MPL-2.0, file-level copyleft: copying them keeps them MPL-2.0. Its design can be reused
freely.

### 4.6 What the API covers (P, high)
**SM_API's headers cover:**
- primitives;
- linear, rotational, pipe and draft sweeps, and taper extrudes;
- lofts (skins);
- full and non-manifold Booleans;
- fillets, chamfers and variable-radius fillets;
- shell and offset;
- stitching and healing;
- NURBS curves and surfaces;
- intersections, including sections by a plane;
- mass properties;
- tessellation by chord height, angle and edge length.

**Import:** native `.smb` only. It reads no STEP or IGES files, and USD and OCCT need their own large libraries.

### 4.7 Licence (P, high)
- `LICENSE` is Apache-2.0, with its patent grant. Every kernel file carries an NVIDIA SPDX Apache-2.0 header.
- Other terms in THIRD_PARTY_NOTICES.md cover only things outside the kernel: OpenUSD, TBB, Python and the
  proposals.
- A binary we built would ship with the LICENSE and the notices.
- The chain of title from GeomWare to SMS to NVIDIA rests on secondary sources (S).

### 4.8 The alternatives (P unless marked; sizes measured here, gzip -9)

**OCCT** (LGPL-2.1 with the OCCT exception)
- The reference open B-rep kernel. It has everything F1-F7 needs, plus STEP and IGES.
- Upstream supports Emscripten (`dox/build/build_occt/building_occt.md` 20-32) but publishes no WebAssembly
  package.
- Published builds:
  - replicad-opencascadejs 1.1.0: **22,980,267 bytes (7,206,977 gzipped)**, single-threaded, ES module, takes an
    embedded binary;
  - libcascade 3.1.0, OCCT 8.0.1: 42,751,732 (12,189,560);
  - opencascade.js 2.0.0-beta: 50,305,130 (13,719,175), dormant since 2023.
- libcascade measures 488 ms to start its single-threaded build on a desktop (BENCHMARKS.md 135-195).
- replicad's open bugs: #282, about 200 KB leaked per Boolean union; #241 and #248, fillets; #243 and #235,
  Booleans.
- LGPL-2.1 section 6 asks that the user can replace the library. A separate file does that cleanly. Whether a
  base64 copy inside the page does is an interpretation, U.

**Manifold** (Apache-2.0)
- Guaranteed-manifold Booleans on **triangle meshes**: no B-rep, NURBS, fillets or lofts.
- 541,470 bytes (203,834 gzipped), serial, ES module (not ES5).
- Users it names: OpenSCAD, Blender, BRL-CAD, Babylon.js and IFC.js.

**truck** (Apache-2.0, Rust)
- NURBS B-rep, Booleans, sweeps, a single-edge fillet, and STEP.
- No published WebAssembly.
- Open: Boolean panics (#135, #114, #57); #53, "Support for Chamfer/Fillet".
- Its one production user, CADmium, is inactive.

**verb-nurbs** (MIT)
- NURBS curves and surfaces: evaluation, intersection, tessellation, and lofted, swept and revolved surfaces.
- No solids or Booleans.
- **Plain ES5 JavaScript**, 295,949 bytes (56,834 gzipped). Last release 3.0.3 (2025-04).

**Set aside:**
- Fornjot: archived 2026-06-19, "shut down".
- Zoo: its own GPU engine, not open.
- IFClite's own kernel: exact Booleans on meshes, with no NURBS authoring.

## 5. The alternatives compared

The criteria, set before the comparison:
- **Coverage:** F1-F7's operations.
- **Robustness:** today, on the operations BIM uses.
- **Licence:** fit with a public one-file app.
- **Contract:** what it costs the delivery contract (ES5, no dependencies, `file://`).
- **Phones:** the risk on phones.
- **Reuse:** what we would reuse, as against write.
- **Maintenance:** of the upstream.

| | Coverage | Robustness | Licence | Contract | Phones | Reuse | Maintenance |
|---|---|---|---|---|---|---|---|
| A. SMLib, our own Emscripten build | All of F1-F7; no STEP | Low now: 22 open issues, Booleans and fillets regressing | Apache-2.0: fits | A WebAssembly binary, size unknown (e02); a Worker with restarts | Unknown | The kernel unchanged; we write the build and an adapter (IFClite's design as reference) | Active but closed to contributions; 3 weeks old |
| B. OCCT (replicad's build) | All, plus STEP and IGES | Medium: mature, with known fillet and Boolean failures and a leak | LGPL-2.1: a separate, replaceable file is the clean reading | +30.6 MB as base64; about 0.5 s to start | High: about 300 MB iOS ceiling and a leak | A published package, unchanged | Active, with many users |
| C. Manifold for Booleans, verb-nurbs for surfaces | Booleans and NURBS surfaces; no fillets, shells or solids from surfaces | High for Booleans; verb mature but quiet | Apache-2.0 and MIT | Manifold +0.72 MB as base64, ES module; verb is ES5 | Low | Both unchanged | Manifold active; verb quiet |
| D. truck | Most; one-edge fillet; no loft or shell | Low: Boolean panics | Apache-2.0 | Needs our own Rust build | Unknown | The crates; we write the bindings | Active, few users |
| E. Our own ES5, extended | What we write: the BSP Booleans now, F1's NURBS by the book | Booleans fragile on coplanar faces (BSP) | Ours | None | Low | None | Ours |

**The recommendation follows from the table.** No option gives every F1-F7 operation without a binary. The
options that keep the contract (C's verb, E) cover curves and surfaces, which is F1 and most of F2, but not
fillets or shells.

**So, in two steps:**
1. **F1 now, on ES5:** NURBS curves and surfaces, through verb-nurbs (reuse first) or our own code where verb
   falls short. Nothing changes in the contract.
2. **The solid kernel, at the first phase that needs fillets or shells:** SMLib (A) or OCCT (B), decided on e02's
   numbers and SMLib's state at that release. Until then SMLib is the watched candidate. It has the better
   licence and coverage; OCCT has the maturity.

**What would change this:**
- e02 giving a small SMLib, with #34 and #35 fixed in a release: A comes forward.
- The owner allowing a separate `.wasm` beside the one file: B's licence question goes.
- A phone test failing at OCCT's size: B goes.

## 6. The experiments

### e01: a WebAssembly kernel in the one-file build, from `file://` (run 2026-10-31)

**Setup.** `reference/experiments/kernel-wasm/e01_file_origin_wasm.js`, with its results in `e01_results.json`.
- Chromium 153.0.8010.12 (chromium-1243), driven by Playwright 1.63.0. A fresh browser for each run, 5 runs at
  each size.
- The module is synthetic, written by the script: integer arithmetic, sized to 1, 5 and 10 MB. No upstream code
  ran.

**What it showed:**
- `fetch()` of a sibling `.wasm` from the `file://` page fails ("TypeError: Failed to fetch"), at every size and
  in every run. So a kernel has to be embedded in the page.
- The embedded base64 decodes and compiles. The module runs in the page and in a Worker made from a Blob URL.
  Both returned the expected result.
- `crossOriginIsolated` is false and `SharedArrayBuffer` is undefined on `file://`, in the page and in the
  Worker. So no threaded Emscripten build can run there.
- `WebAssembly.Exception` and `WebAssembly.Tag` exist, so native WebAssembly exceptions are available.
- A WebAssembly.Memory grew to 65,535 pages (4 GiB less 64 KiB) on this desktop.

**The numbers** (milliseconds: mean, with min to max in brackets, from the second run of the script):

| Size | Wasm bytes | Base64 bytes | Decode | Compile (page) | Compile (Worker) | Page load to ready |
|---|---|---|---|---|---|---|
| 1 MB | 1,048,917 | 1,398,556 | 10.9 (7.7-13.6) | 16.6 (13.4-18.3) | 5.3 (3.2-7.6) | 118 (97-128) |
| 5 MB | 5,246,864 | 6,995,820 | 26.7 (26.0-27.4) | 17.8 (14.2-27.1) | 11.6 (9.9-17.0) | 208 (179-309) |
| 10 MB | 10,493,693 | 13,991,592 | 58.0 (51.1-79.5) | 25.8 (23.2-27.9) | 22.0 (18.2-24.9) | 402 (316-586) |

**What the numbers mean:**
- Base64 adds a third to the size.
- Chromium compiles each function lazily at its first call, so "compile" here is mostly validation. A real
  kernel's first operation pays the rest; ocjs.org says compiling OCCT "might take longer than downloading".
- The synthetic module gzips to 0.7% of its size, where real code gzips to about 30% (replicad's 31%,
  Manifold's 38%). So its download sizes do not carry over; its raw sizes do.

### e02: SMLib built for the browser (not run; waits on the owner)

**The plan:**
1. **Isolation.** All of it outside the repository, in the session's scratch directory. Nothing committed but the
   script and its numbers.
2. **Toolchain.** Install emsdk 4.0.15 from `github.com/emscripten-core/emsdk`, which downloads its LLVM and Node
   binaries.
3. **Sources.** usd-brep at `3fd5b95` and at IFClite's `c9c5979`, unchanged.
4. **Build.** Compile `source/SMLib/src` and `source/SM_API/src` with `emcc -O3`, no threads, in two variants:
   JavaScript exceptions, and `-fwasm-exceptions`. Also a `SINGLE_FILE` build.
5. **Measure** with the e01 harness:
   - the `.wasm` bytes, raw and gzipped;
   - first-call time for box, cylinder, union, difference, a fillet on a box edge and tessellation, from `file://`
     in a Blob-URL Worker;
   - peak memory;
   - the #34 and #35 cases.

## 7. Edges

- **Coincident faces** (a wall meeting a wall, a slab on a wall) are where B-rep Booleans fail: SMLib's #34, OCCT
  in replicad #243. A test set has to be built from them.
- **Fillets** fail where the radius approaches a neighbouring face, and on fillet-made edges (#29).
- **Closed surfaces** (spheres, tori, cylinders from other tools) break SMLib's healer: KNOWN_ISSUES has no
  workaround.
- **aarch64 against x86-64.** SMLib's results changed with fused multiply-add. WebAssembly does not fuse by
  default, a fact read but not tested.
- **iOS.** A tab's WebAssembly memory can fall to about 300 MB after a reload (WebKit 269777).

## 8. What the app already has

- **Booleans:** `src/js/engine/bim/csg-booleans.js` lines 189-191 (`csgUnion`, `csgSubtract`, `csgIntersect`).
  These are BSP-tree Booleans on polygon meshes, in ES5, with a plane tolerance `CSG_EPS = 1e-5` (line 2). Meshes
  go in through `meshPolys` (102) and come back through `polysToMesh` (161). Results are new meshes; nothing
  keeps a B-rep or the inputs.
- **The gap:** `reference/research-rhino-guide-gap.md` lines 29-38, 50 and 61-64 list what is missing: NURBS
  curves and surfaces, polysurfaces, Pipe, Cap and fillets on solids. PAD and POCKET exist.
- **The plan:** `reference/plan-parametric-design.md`, which says its approval gate needs the owner before any new
  dependency or build step.
- **The precedent for bundled third-party code:** `src/js/vendor/openskp.js` (216,247 bytes; credited in
  THIRD_PARTY_NOTICES.md section openskp). It is JavaScript, not a binary.
- **The size today:** `canvas_v10.html` is 3,729,520 bytes. OCCT's smallest build as base64 would be about
  8 times that; Manifold about a fifth.

## 9. Risks and threats to validity

- **e01 is synthetic and ran on one desktop Chromium.** No phone, Safari or Firefox was tested. The timings stand
  for the mechanism, not for SMLib.
- **The issue counts move weekly.** They were read on 2026-11-01 through the fetch tool's digest.
- **SMLib's size and speed in WebAssembly are unknown** until e02.
- **The LGPL reading of an embedded OCCT is ours, not a lawyer's.**
- **SMLib's history before NVIDIA rests on secondary sources.**

## 10. What is still open (U)

- SMLib's WebAssembly size, start-up time and memory: e02.
- How it behaves on a phone: needs a device or the owner's.
- Whether replicad's OCCT, or a trimmed OCCT ("7.1 MB, compressed 2.4 MB" per ocjs.org), keeps fillets, shells
  and lofts.
- truck's WebAssembly size: not published.
- NVIDIA's own announcement and AWV's statement: not found.
- The bodies of issues #22 to #39 beyond their titles. Only #31 and #34 were read in full.

## 11. The owner's decisions

1. **e02.** Install emsdk 4.0.15 in the scratch directory, compile usd-brep unchanged, and measure, as section 6
   lists. The sandbox refused the install without this approval (2026-10-31).
2. **The contract, for a kernel.** When a phase needs fillets or shells, may the app carry a WebAssembly binary?
   Either embedded in the one file (for `file://`), or beside it as a separate file on Pages, with the one file
   loading it lazily on first use of a solid tool. Or must solids stay in ES5?
3. **F1 through verb-nurbs?** Reuse verb-nurbs (MIT, ES5, 56 KB gzipped) for NURBS curves and surfaces, bundled
   like openskp, or write F1 ourselves from The NURBS Book?
4. **Booleans through Manifold?** Manifold (Apache-2.0, 541 KB) would make Booleans robust on meshes. This is
   separate from the NURBS kernel. Now, later or not at all?

Answers: none yet.

## 12. References

Levels: P read at the source, P-wf the source read through the fetch tool, S secondary. All read 2026-10-31 to
2026-11-01.

| Source | What was read | Level |
|---|---|---|
| usd-brep, `github.com/NVIDIA-Omniverse/usd-brep` @ `3fd5b95` | README, CHANGELOG (1.0.0, 1.0.1), KNOWN_ISSUES, CONTRIBUTING (line 6), LICENSE, THIRD_PARTY_NOTICES, BUILDING, `.agents/operations/concurrency.md`, SM_API headers, `SmMessages.cpp` 581-703, source counts | P |
| usd-brep issues, `github.com/NVIDIA-Omniverse/usd-brep/issues` | The list; #31 and #34 in full | P-wf |
| IFClite, `github.com/LTplus-AG/ifc-lite` @ `9e3e8cf` | `native/smlib-adapter/` (README, CMakeLists.txt 68-84, browser/), `packages/wasm/README.md` 408-415 and CHANGELOG, `licenses/retained/README.md`, `docs/guide/retained-installation.md` line 3, `rust/geometry/src/lib.rs` 140 | P |
| Louis Truempler's post (LinkedIn), via the owner, 2026-10-31 | The claim that IFClite runs the kernel in a browser | S (checked against IFClite's code) |
| OCCT, `github.com/Open-Cascade-SAS/OCCT` @ `53706f78` | LICENSE_LGPL_21, OCCT_LGPL_EXCEPTION, `dox/build/build_occt/building_occt.md` 20-32, `dox/samples/samples.md` 34 | P |
| replicad and replicad-opencascadejs (npm 1.2.0, 1.1.0) | Tarballs: the `.wasm` files measured, the glue; issues #282, #272, #241, #248, #243, #235 | P, P-wf |
| libcascade (npm 3.1.0), `github.com/taucad/opencascade.js` @ `341fa789` | README, BENCHMARKS.md 135-195, the single `.wasm` measured | P |
| opencascade.js (npm 2.0.0-beta), and `ocjs.org/docs/getting-started/file-size` | The tarball measured; the file-size page | P, P-wf |
| Manifold, `github.com/elalish/manifold` @ `2f33e782`, npm manifold-3d 3.5.4 | README, d.ts, the `.wasm` measured, issue #745 | P |
| truck, `github.com/ricosjp/truck` @ `1ca3214e` | Crates, CHANGELOG; issues #135, #114, #57, #68, #53, #123, #128 | P, P-wf |
| verb, `github.com/pboyer/verb`, npm verb-nurbs 3.0.3 | `build/js/verbHaxe.js` (ES5, measured), API | P |
| Fornjot, CADmium, Chili3D | READMEs (archived; inactive; `cpp/CMakeLists.txt` 86-90) | P, P-wf |
| WebKit bug 269777 | "Only ~300 MB of RAM is reliably available to WebAssembly pages" | P-wf |
| Zoo, `zoo.dev/blog/zoo-design-studio-v1` | Their own geometry engine | P-wf |
| DEVELOP3D, "Nvidia launches USD BRep geometry kernel for solid modelling" | History, ClassCAD | S |
| 3Druck, on SMLib under Apache-2.0 | The release | S |
| This app: `src/js/engine/bim/csg-booleans.js`, `reference/research-rhino-guide-gap.md`, `reference/plan-parametric-design.md`, `src/js/vendor/openskp.js`, `THIRD_PARTY_NOTICES.md`, `CLAUDE_INSTRUCTIONS.md` lines 50-51 | As cited | P |
