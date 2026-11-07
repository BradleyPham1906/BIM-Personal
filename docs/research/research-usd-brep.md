# NVIDIA's SMLib (USD BRep) as the kernel for Freeform: research

Phase: V181-V187, Freeform F1-F7, with the Parametric Design Foundation (#44). Researched 2026-10-31 and
2026-11-01 under `reference/research-protocol.md`. The research is done:
- read-only research of the code, issues and licences;
- experiments e01 and e02 (e02 approved by the owner on 2026-11-01);
- the independent second reader, with its corrections applied.

What remains is the owner's decisions, in section 11.

## 1. Abstract

**The question.** On 2026-10-08 NVIDIA released SMLib, a commercial NURBS B-rep kernel it bought with Solid
Modeling Solutions, as USD BRep, under Apache-2.0. IFClite runs it in a browser. Can it be the geometry kernel for
the app's Freeform group: NURBS curves and surfaces, sweeps, lofts, fillets, shells and parametric solids?

**What it has going for it:**
- **It does the work.** It has every operation the group needs, and its licence fits.
- **It runs in our one-file build.** We built it here, unchanged, with Emscripten (e02).
  - **Size:** 5.76 MB of WebAssembly (1.82 MB gzipped), or 7.79 MB as a single script with the binary embedded.
    With nothing removed by the linker, the whole kernel is 8.65 MB.
  - **It works from `file://`:** in a Blob-URL Worker it gave the correct result for a box less a cylinder, a
    16-hole plate, a wall-join union, an edge fillet and tessellation, in 5 of 5 runs.
  - **It starts fast:** it instantiates in about 180 ms.
  - **It is smaller than OCCT:** a third to a sixth of OCCT's published builds (23 to 50 MB).

**Why it is not ready to adopt now:**
- **It is three weeks old.** It has 22 open issues. Unions, differences and fillet-on-fillet are among them, all
  confirmed by a maintainer, and one is a regression in 1.0.1 on a mitre joint.
- **We would carry our own fixes.** NVIDIA takes no outside code, so any fix we needed would live in our own fork.
- **It breaks the delivery contract.** It would be the app's first binary dependency, in an ES5, zero-dependency
  app.

**The recommendation:**
1. **Build F1, NURBS curves and surfaces, in ES5.** verb-nurbs (MIT; its ES5 build) is the candidate to reuse.
2. **Make SMLib the leading candidate for the solid kernel,** ahead of OCCT on size and licence. Decide at the
   first phase that needs fillets or shells, after re-checking SMLib's open Boolean and fillet issues at that
   release.

## 2. The question and the hypotheses

The question: which kernel, if any, should the Freeform group build on, and is SMLib it?
A good answer decides whether we adopt SMLib now, later or never, and what F1 is built on.

| # | Hypothesis | Outcome | Evidence |
|---|---|---|---|
| H1 | SMLib has the operations F1-F7 need: NURBS curves and surfaces, Booleans, fillets, sweeps, lofts, shell and offset, tessellation | **Held** | SM_API's headers (4.6) |
| H2 | SMLib is robust enough today for BIM solids (wall joints, openings, fillets) | **Failed** for the general case | Issues #34, #35 and #29, all confirmed by a maintainer (4.2). The simple cases in e02 passed |
| H3 | SMLib itself can run in the one-file build opened from `file://`, in a Worker | **Held** | e01 (the mechanism) and e02 (SMLib itself, 5 of 5 runs correct) |
| H4 | A browser build of SMLib exists to reuse unchanged | **Failed** | None from NVIDIA. IFClite's is unreleased, partial, and pinned to 1.0.0 (4.5) |
| H5 | SMLib in WebAssembly is smaller than OCCT's (23 to 50 MB) | **Held** | 5.76 MB for the operations used; 8.65 MB for the whole kernel (e02) |
| H6 | SMLib's licence lets it be bundled in a public one-file app | **Held** | Apache-2.0 throughout the kernel (4.7) |
| H7 | SMLib runs on a phone within iOS's WebAssembly memory | **Open, likely** | e02's module used 25.4 MB of memory for these operations. WebKit bug 269777 puts the reliable ceiling near 300 MB. No phone was tested |

## 3. Method

**Sources, by kind:**
- **Upstream code read as text:** usd-brep at `3fd5b95` (2026-10-22, v1.0.1), IFClite at `9e3e8cf`
  (2026-10-31), and shallow clones of opencascade.js (donalffons and taucad), replicad, Manifold, truck, Fornjot,
  verb, Chili3D and CADmium. OCCT was read at `53706f78` on raw.githubusercontent.com.
- **Published artefacts:** npm tarballs, with their `.wasm` sizes measured and gzipped here.
- **Issue trackers:** usd-brep (#29, #31, #34 and #35 read in full), replicad, truck and Manifold.
- **Vendor and practitioner documents:** ocjs.org's file-size page, libcascade's BENCHMARKS.md, and Zoo's v1 post.
- **Bug trackers:** WebKit bug 269777.
- **Press:** DEVELOP3D and 3Druck on the release.

**The search log.** Two research agents ran in parallel, one on the case against SMLib and one on the
alternatives. Their logs, raw downloads and reports are kept outside the repository, as the policy asks; every
source is listed in section 12.
- **Blocked:** github.com's API and HTML to curl and gh (HTTP 403 in this session). Those pages were read through
  the fetch tool instead (marked P-wf: primary pages, read as a digest).

**Experiments:**
- **e01:** a synthetic module, testing the mechanism. Script: `reference/experiments/kernel-wasm/e01_file_origin_wasm.js`.
- **e02:** SMLib itself, built here with Emscripten 4.0.15 from usd-brep `3fd5b95` unchanged. The test driver is
  ours. Scripts: `e02_build.sh`, `e02_driver.cpp` and `e02_browser.js`, in the same folder.
- **Approval:** the sandbox refused the Emscripten install under Auto mode. It ran after the owner's approval and
  a change of the permission mode (2026-11-01).

**The independent check.** A separate research agent, the second reader, re-read the sources behind every fact
the recommendation uses: 42 facts, of which 31 were confirmed (9 with a caveat), 5 partly confirmed and 6 wrong.
- All 13 corrections it listed are applied in this version: the fix counts, file counts, commit history, the
  wording on #31, IFClite's 1.0.0 pin, which verb file is ES5, the `exit()` paths, the TBB macros, libcascade's
  benchmark setting, and two citations.
- Not checked by it: the absence of x87, SIMD, setjmp and alloca; the TCHAR count; libcascade's OCCT version;
  truck's issue numbers; WebKit 269777; the history in the press. These stay at the level given.

## 4. Findings

### 4.1 What it is (P, high)
- **The repository.** USD BRep (`github.com/NVIDIA-Omniverse/usd-brep`) holds:
  - the SMLib kernel (`source/SMLib`: 969,048 lines in 462 C/C++ files, 224 .cpp and 238 .h, counted with
    `wc -l`);
  - a C API (`source/SM_API`: 12,612 lines in 28 files);
  - an OpenUSD schema for solids (`BrepArray`), a Python API, a healer, a validator, a tessellator, and
    converters to and from OpenCASCADE.
- **Versions.** 1.0.0 on 2026-10-08 and 1.0.1 on 2026-10-21 (CHANGELOG.md lines 3 and 100).
- **Lineage.** The NURBS core is NLib, "incorporated into SMLib"
  (`.agents/skills/smlib-kernel-operations/references/lifetime-context-cache.md` 70-73). Its code cites The
  NURBS Book (Piegl and Tiller), for example `NL_SrfLstSqFit.cpp` line 7493.
- **History (S, medium).** Solid Modeling Solutions (1998), NLib bought from GeomWare (2001), NVIDIA's
  acquisition (May 2022). These come from DEVELOP3D and Wikipedia; no NVIDIA announcement was found. ClassCAD
  (AWV Informatik) is a user, per AWV's CEO quoted by DEVELOP3D.

### 4.2 Robustness (P, high)
**KNOWN_ISSUES.md at v1.0.1:**
- healing can report success after a failed repair;
- closed and periodic surfaces (spheres, tori) can be mis-repaired, the one item with no workaround;
- `shell_brep` can return a result that is not a solid;
- `stitch_brep_with_face` crashes on every input tried; the workaround is to stitch the whole Brep;
- importing malformed USD can crash; the workaround is to validate the file first;
- `brep_relationship` reports a shallow overlap as touching;
- tessellation winds triangles inside out next to fillets, and puts long thin triangles at sphere poles.

**CHANGELOG 1.0.1** lists 59 fixes: Booleans 12, sweeps and extrusions 5, fillets 6, healing and topology 12,
offsets 4, geometry 8, measurement 3, and 9 in import, export and the build.
- The Boolean fixes include writes to freed memory, results that changed from run to run, and lost operands.
- It also stopped fused multiply-add on aarch64, because it changed Boolean results there (GitHub #12).

**The issue tracker (P-wf, 2026-11-01):** 36 issues, 22 open. Among the open:
- **#34:** after a rigid translation, the union of a mitre-joint pair fails the validity check in 1.0.1, and
  passes in 1.0.0. It is a regression, confirmed by a maintainer (martinpwnv, 2026-10-26). The union still
  returns success, so the failure is silent unless the result is checked. This is exactly a wall joint.
- **#35:** a difference returns success with an empty solid. The intersection returns all of the first operand,
  and the union fails. Confirmed 2026-10-27.
- **#29:** filleting an edge made by a fillet fails, for radii 0.1 to 2.0. Confirmed 2026-10-27.
- **#37:** mirror and scale transforms.
- **#10:** shell results differ from process to process.
- **#22:** a hang creating elliptical arcs.

### 4.3 Governance (P, high)
- "USD BRep is currently not accepting external code contributions" (CONTRIBUTING.md line 6). Issues are
  welcome.
- History: four commits, one per release (initial, 0.2.0, 1.0.0, 1.0.1), with tags v1.0.0 (`c9c5979`) and v1.0.1
  (`3fd5b95`).
- There is no WebAssembly, browser or mobile target. On #31, still open, a maintainer wrote that they "don't
  currently have a plan to share" on an Android target.
- So a fix we needed would live in our own fork until NVIDIA made it.

### 4.4 Porting to WebAssembly (P, high; settled by e02)
**What helps:**
- No x87, SIMD, setjmp, alloca or OpenMP were found (not re-checked by the second reader).
- TBB calls compile only under `SM_USE_TBB`, and its allocator only under `SM_USE_TBB_SCALABLE`. Neither macro is
  defined in the build files, although premake still links tbb.
- Operations run on one thread.
- **e02 compiled all 237 kernel and API sources, unchanged, with no source errors.** The one fix needed was the
  include order: both trees have a `StdAfx.h`, and IFClite's CMake also puts the API's first.

**What hurts:**
- **`exit(-1)` calls.** There are five in `SmMessages.cpp` (lines 581, 595, 609, 682 and 703). All of them run
  when a debug-log or stdout-redirect file cannot be opened, not on geometry errors. A browser build has to keep
  those paths off.
- **A process-global context with "unlocked mutable shared state"** (`.agents/operations/concurrency.md` 12-23).
  A shared-memory WebAssembly worker counts as a thread there (59-66). So the app needs one unshared module per
  Worker, with every call serial.
- **Restarting after a crash.** IFClite's adapter treats a kernel failure as tainting the module, which has to be
  thrown away (its README, lines 28-36).

### 4.5 IFClite's browser build (P, high)
**Where it lives.** `native/smlib-adapter/` in IFClite, MPL-2.0:
- It pins usd-brep `c9c5979`, unpatched. **That commit is the v1.0.0 tag**, so IFClite's build has none of
  1.0.1's 59 fixes, and was pinned before the #34 regression.
- It compiles all of `SMLib/src` and `SM_API/src`.
- Its CMakeLists.txt (67-84) links with Emscripten 4.0.15: `-sMODULARIZE=1 -sEXPORT_ES6=1`, `-fexceptions`,
  `-sALLOW_MEMORY_GROWTH=1`, `-sSTACK_SIZE=8388608`. There are no threads and no SINGLE_FILE.
- The output is an ES module plus a `.wasm`, loaded into a module Worker served over HTTPS.

**What its C ABI exposes:** box, cylinder, Booleans (on copies), copies, transforms, volume, a manifold check,
tessellation, and two sweeps: a planar region with holes, and a disk along a B-spline.

**What it leaves out:** fillets, shells, lofts and healing are not in the ABI. A kernel failure "taints" the
module, and the process has to be thrown away.

**Its status.** It is off by default. Curved routes open only after runtime checks pass. Its installation guide is
"for explicitly qualified builds after the human licence review".

**Reuse.** Its files are MPL-2.0, file-level copyleft: copying them keeps them MPL-2.0. Its design can be reused
freely.

### 4.6 What the API covers (P, high)
**`SmApiBrep.h`:**
- Booleans: union, difference, intersection, merge, CSG trees, non-manifold.
- Sweeps: linear, rotational, pipe and draft, and taper extrudes.
- Fillets: `SmApiFilletEdges`, per edge, and variable radius.
- Shell and offset: `SmApiShellBrepFull`, `SmApiOffsetBrepFull`.
- Stitching, and tessellation.

**Other headers:**
- `SmApiFillets.h`: circular fillets and chamfers.
- `SmApiPrimitives.h` and `SmApiSurfaces.h`: lofts, as `SmApiCreateSkin*`.
- `SmApiHeal.h`: healing.
- `SmApiIntersectors.h`: sections by a plane.
- `SmApiTessellationParams.h`: tessellation by chord height, curve and surface angle, and maximum edge length.

**Import:** native `.smb` only. It reads no STEP or IGES files. NLib has an IGES writer for curves and surfaces,
which SM_API does not expose.

### 4.7 Licence (P, high)
- `LICENSE` is Apache-2.0, with its patent grant. All 463 files in SMLib and 29 in SM_API carry NVIDIA's SPDX
  Apache-2.0 header.
- THIRD_PARTY_NOTICES.md covers OpenUSD, oneTBB, Python and the proposals. Its note that USD BRep calls TBB
  directly applies only when the TBB macros are on, and they are off in e02's build.
- A binary we built would ship with the LICENSE and the notices.
- The chain of title from GeomWare to SMS to NVIDIA rests on secondary sources (S).

### 4.8 The alternatives (P unless marked; sizes measured here, gzip -9)

**OCCT** (LGPL-2.1 with the OCCT exception)
- The reference open B-rep kernel. It has everything F1-F7 needs, plus STEP and IGES.
- Upstream supports Emscripten (`dox/build/build_occt/building_occt.md` line 31, "Emscripten SDK 3.0 or newer")
  but publishes no WebAssembly package.
- Published builds:
  - replicad-opencascadejs 1.1.0: **22,980,267 bytes (7,206,977 gzipped)**, single-threaded, ES module, takes an
    embedded binary;
  - libcascade 3.1.0: 42,751,732 (12,189,560);
  - opencascade.js 2.0.0-beta: 50,305,130 (13,719,175), dormant since 2023.
- libcascade's BENCHMARKS.md gives 488 ms to start its single-threaded build. That was measured under Node v24 on
  an Apple M2 Pro, on a 38.46 MB snapshot of 2026-05-21, not in a browser.
- replicad's open bugs:
  - #282: about 200 KB leaked per union, about 180 KB per cut; open, no reply yet;
  - #241 and #248: fillets;
  - #243 and #235: Booleans.
- LGPL-2.1 section 6 asks that the user can replace the library. A separate file does that cleanly; whether a
  base64 copy inside the page does is an interpretation (U).

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
- NURBS curves and surfaces: evaluation, intersection, tessellation, and lofted, swept and revolved surfaces. No
  solids or Booleans.
- **Its ES5 build is `build/js/verbHaxe.js`, 278,479 bytes (55,974 gzipped).** The second reader parsed it with
  acorn at ecmaVersion 5.
- `verb.min.js` (295,949 bytes) is not ES5: it has a `const` at line 8688, and it wraps the code as a Rollup UMD
  module that requires `web-worker`.
- verbHaxe.js carries Haxe's worker-pool code (`verb_exe_WorkerPool`), which an adapter would leave unused.
- Last release 3.0.3 (2025-04-23).

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
| A. SMLib, our own Emscripten build | All of F1-F7; no STEP | Low now: 22 open issues, Booleans and fillets confirmed failing (simple cases pass, e02) | Apache-2.0: fits | Measured: 7.79 MB as one embedded script (2.57 MB gzipped); a Worker with restarts | Medium: 25 MB of memory here; untested on a device | The kernel unchanged (e02 proved it); we write the driver and an adapter | Active, closed to contributions; 3 weeks old |
| B. OCCT (replicad's build) | All, plus STEP and IGES | Medium: mature, with known fillet and Boolean failures and a leak | LGPL-2.1: a separate, replaceable file is the clean reading | +30.6 MB as base64; start-up measured only under Node | High: about 300 MB iOS ceiling and a leak | A published package, unchanged | Active, with many users |
| C. Manifold for Booleans, verb-nurbs for surfaces | Booleans and NURBS surfaces; no fillets, shells or solids from surfaces | High for Booleans; verb mature but quiet | Apache-2.0 and MIT | Manifold +0.72 MB as base64, ES module; verbHaxe.js is ES5 | Low | Both unchanged | Manifold active; verb quiet |
| D. truck | Most; one-edge fillet; no loft or shell | Low: Boolean panics | Apache-2.0 | Needs our own Rust build | Unknown | The crates; we write the bindings | Active, few users |
| E. Our own ES5, extended | What we write: the BSP Booleans now, F1's NURBS by the book | Booleans fragile on coplanar faces (BSP) | Ours | None | Low | None | Ours |

**The recommendation follows from the table.** No option gives every F1-F7 operation without a binary. The
options that keep the contract (C's verb, E) cover curves and surfaces, which is F1 and most of F2, but not
fillets or shells.

Between the two kernels that do, e02 moves SMLib (A) ahead of OCCT (B):
- its binary is a third to a sixth of OCCT's;
- its licence is permissive;
- it runs unchanged from `file://`.

What holds it back is robustness and governance, and both can change with time.

**So, in two steps:**
1. **F1 now, on ES5:** NURBS curves and surfaces, through verb-nurbs (verbHaxe.js) or our own code where verb
   falls short. Nothing changes in the contract.
2. **The solid kernel, at the first phase that needs fillets or shells:** SMLib, if its Boolean and fillet issues
   (#34, #35, #29) are fixed by then and our wall-joint cases pass; otherwise OCCT, or wait.

**What would change this:**
- #34, #35 and #29 fixed in a release, with the edge cases of section 7 passing in e02's harness: SMLib could come
  forward.
- A phone test failing at 25 MB, or at the sizes a full binding reaches: A and B both go.
- The owner choosing to keep solids in ES5: both go, and the solid operations wait.

## 6. The experiments

### e01: a WebAssembly kernel in the one-file build, from `file://` (run 2026-10-31)

**Setup.** `reference/experiments/kernel-wasm/e01_file_origin_wasm.js`, with its results in `e01_results.json`.
- Chromium 153.0.8010.12 (chromium-1243), driven by Playwright 1.63.0. A fresh browser for each run, 5 runs at
  each size.
- The module is synthetic, written by the script: integer arithmetic, sized to 1, 5 and 10 MB.

**What it showed:**
- `fetch()` of a sibling `.wasm` from the `file://` page fails ("TypeError: Failed to fetch"), at every size and
  in every run. So a kernel has to be embedded in the page.
- The embedded base64 compiles and runs, in the page and in a Worker made from a Blob URL.
- `crossOriginIsolated` is false and `SharedArrayBuffer` is undefined on `file://`, so no threaded Emscripten
  build can run there.
- `WebAssembly.Exception` and `WebAssembly.Tag` exist.
- A WebAssembly.Memory grew to 65,535 pages (4 GiB less 64 KiB) on this desktop.

**The numbers** (milliseconds: mean, with min to max in brackets):

| Size | Wasm bytes | Base64 bytes | Decode | Compile (page) | Compile (Worker) | Page load to ready |
|---|---|---|---|---|---|---|
| 1 MB | 1,048,917 | 1,398,556 | 10.9 (7.7-13.6) | 16.6 (13.4-18.3) | 5.3 (3.2-7.6) | 118 (97-128) |
| 5 MB | 5,246,864 | 6,995,820 | 26.7 (26.0-27.4) | 17.8 (14.2-27.1) | 11.6 (9.9-17.0) | 208 (179-309) |
| 10 MB | 10,493,693 | 13,991,592 | 58.0 (51.1-79.5) | 25.8 (23.2-27.9) | 22.0 (18.2-24.9) | 402 (316-586) |

Chromium compiles each function lazily at its first call, so "compile" here is mostly validation. e02 measures
real first calls.

### e02: SMLib itself, built to WebAssembly (run 2026-11-01)

**Build.**
- Script: `e02_build.sh`, run outside the repository.
- Toolchain: Emscripten 4.0.15 (emsdk at `d7b4130`).
- Sources: usd-brep `3fd5b95`, unchanged: 224 kernel and 13 API sources, plus our `e02_driver.cpp`.
- Flags: as IFClite's (C++17, `SM_NO_DEBUG_CODE`, `SM_NO_GFX_OUTPUT_CODE`, `NDEBUG`, `-fexceptions`), plus
  `-O3`.
- Link options: growing memory, an 8 MiB stack, MODULARIZE.
- Time: the link takes about 50 s. The compile, on 4 cores, was not timed end to end, because it was resumed
  after the include-order fix.

**Sizes:**

| Output | Bytes | gzip -9 |
|---|---|---|
| `smlib.wasm`, the operations our driver uses (the linker drops the rest) | 5,756,945 | 1,819,880 |
| `smlib.mjs`, its ES-module glue | 111,031 | |
| `smlib_single.js`, one classic script with the binary embedded: the form the one-file app would carry | 7,787,278 | 2,568,924 |
| `smlib_full.wasm`, the whole kernel kept (`--no-gc-sections`): the bound a full binding approaches | 8,645,681 | 2,698,553 |

**The run.**
- Harness: `e02_browser.js`, with its results in `e02_results.json`.
- Setup: Chromium 153.0.8010.12, Playwright 1.63.0, 5 runs with a fresh browser each.
- Loading: the single-file build was embedded in a page opened from `file://` and started in a Blob-URL Worker.
- Measurement: each operation was called twice. The first call carries Chromium's lazy compile.
- Cross-check: the ES-module build gave the same five values under Node.

| Operation (our driver) | Expected | Result, 5 of 5 runs | First call, ms | Second call, ms |
|---|---|---|---|---|
| A 10 x 10 x 3 box less a cylinder of radius 2 | 300 - 12 pi = 262.301 | 262.30088816552296 | 164 (147-191) | 44.5 (36-58) |
| A 12 x 12 x 1.5 plate less 16 cylinders of radius 0.75 (upstream's own fixture) | 173.588 | 173.58849916868843 | 520 (459-618) | 407 (345-479) |
| Two walls (4 x 0.2 x 3 and 0.2 x 4 x 3) joined at a corner | 4.68 | 4.68 | 32.9 (26-43) | 19.6 (17-23) |
| A circular fillet of radius 1 on one edge of a 10 cm box | 1000 - (1 - pi/4) x 10 = 997.854 | 997.8539816503691 | 57.9 (50-66) | 29.1 (23-35) |
| Tessellation of the 16-hole plate (including its 16 cuts) | succeeds | succeeded | 407 (376-450) | 310 (266-400) |

Every result was also checked as a manifold solid before its volume was taken.

**The rest of the run:**
- **Instantiation:** 178 ms in the Worker (152-224).
- **Memory:** 25,427,968 bytes after all the operations, the same in every run.
- **Page:** 7,788,525 bytes. From navigation to every result back took 2,505 ms (2,343-2,638). That covers
  parsing the page, starting the Worker, decoding the embedded binary, instantiating, and both calls of all five
  operations.
- **Threads:** `SharedArrayBuffer` was undefined, so none were used and none were needed.

**What e02 shows:**
- SMLib needs no changes to run in the app's delivery form.
- It is a third to a sixth of OCCT's size.
- Its simple operations take tens to hundreds of milliseconds.

**What e02 does not show:**
- Robustness on the hard cases: the edge cases of section 7 and the issues' own inputs were not run.
- Behaviour on a phone.
- A full binding's API surface and its size, beyond the bound.

## 7. Edges

- **Coincident faces** (a wall meeting a wall, a slab on a wall) are where B-rep Booleans fail: SMLib's #34, OCCT
  in replicad #243. e02's corner join passed. #34's mitre joint after a translation is the case to add next.
- **Fillets** fail where the radius approaches a neighbouring face, and on fillet-made edges (#29).
- **Closed surfaces** (spheres, tori, cylinders from other tools) break SMLib's healer, the one known issue with
  no workaround.
- **Silent failures.** #34's union and #35's difference both return success, so an adapter has to check every
  result: a manifold solid, and a volume within bounds, as e02's driver does.
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
- **The size today:** `canvas_v10.html` is 3,729,520 bytes. Against that:
  - SMLib's single-file build (7,787,278) would make it about 3.1 times as large;
  - replicad's OCCT as base64 (about 30.6 MB) about 9.2 times;
  - Manifold (about 0.72 MB) about 1.2 times.

## 9. Risks and threats to validity

- **e02 ran only simple, well-posed cases, and our own driver.** It shows the build works. It does not show the
  kernel is robust.
- **One desktop Chromium.** No phone, Safari or Firefox was tested.
- **The issue counts and states move weekly.** They were read on 2026-11-01.
- **The first-call timings include Chromium's lazy compile.** Another engine compiles differently.
- **The LGPL reading of an embedded OCCT is ours, not a lawyer's.**
- **SMLib's history before NVIDIA rests on secondary sources.**

## 10. What is still open (U)

- SMLib on a phone: memory and speed. This needs a device, or the owner's.
- The issues' own inputs (#34, #35, #29) in e02's harness. They need the files attached to the issues.
- Whether a trimmed OCCT ("7.1 MB, compressed 2.4 MB" per ocjs.org) keeps fillets, shells and lofts.
- truck's WebAssembly size: not published.
- NVIDIA's own announcement, and AWV's statement.

## 11. The owner's decisions

1. **e02.** Approved 2026-11-01 and run (section 6).
2. **The contract, for a kernel.** When a phase needs fillets or shells, may the app carry a WebAssembly kernel?
   - Embedded in the one file: SMLib measured at 7.79 MB, 2.57 MB gzipped.
   - Or beside it on Pages, loaded on first use of a solid tool.
   - Or must solids stay in ES5?
3. **F1 through verb-nurbs?** Reuse verb-nurbs (MIT; `build/js/verbHaxe.js`, ES5, 56 KB gzipped) for NURBS curves
   and surfaces, bundled like openskp. Or write F1 ourselves from The NURBS Book?
4. **Booleans through Manifold?** Manifold (Apache-2.0, 541 KB) would make Booleans robust on meshes. This is
   separate from the NURBS kernel. Now, later or not at all?

Answers: 1, approved. 2 to 4, none yet.

## 12. References

Levels: P read at the source, P-wf the source read through the fetch tool, S secondary. All read 2026-10-31 to
2026-11-01.

| Source | What was read | Level |
|---|---|---|
| usd-brep, `github.com/NVIDIA-Omniverse/usd-brep` @ `3fd5b95` | README, CHANGELOG (1.0.0, 1.0.1), KNOWN_ISSUES, CONTRIBUTING (line 6), LICENSE, THIRD_PARTY_NOTICES, BUILDING, `.agents/operations/concurrency.md`, SM_API headers, `SmMessages.cpp` 581-703, source counts; built unchanged in e02 | P |
| usd-brep issues and commits | The issue list; #29, #31, #34 and #35 in full; the commit history | P-wf |
| IFClite, `github.com/LTplus-AG/ifc-lite` @ `9e3e8cf` | `native/smlib-adapter/` (README 28-36 and 48-50, CMakeLists.txt 5-84, `include/ifclite_smlib.h`, browser/), `packages/wasm/README.md` 408-415 and CHANGELOG, `licenses/retained/README.md`, `docs/guide/retained-installation.md` line 3, `rust/geometry/src/lib.rs` 140 | P |
| Louis Truempler's post (LinkedIn), via the owner, 2026-10-31 | The claim that IFClite runs the kernel in a browser | S (checked against IFClite's code) |
| Emscripten 4.0.15, `github.com/emscripten-core/emsdk` @ `d7b4130` | The toolchain e02 used | P |
| OCCT, `github.com/Open-Cascade-SAS/OCCT` @ `53706f78` | LICENSE_LGPL_21, OCCT_LGPL_EXCEPTION, `dox/build/build_occt/building_occt.md` 20-32, `dox/samples/samples.md` 34 | P |
| replicad and replicad-opencascadejs (npm 1.2.0, 1.1.0) | Tarballs: the `.wasm` files measured, the glue; issues #282, #272, #241, #248, #243, #235 | P, P-wf |
| libcascade (npm 3.1.0), `github.com/taucad/opencascade.js` @ `341fa789` | README, BENCHMARKS.md 44, 135-195, the single `.wasm` measured | P |
| opencascade.js (npm 2.0.0-beta), and `ocjs.org/docs/getting-started/file-size` | The tarball measured; the file-size page | P, P-wf |
| Manifold, `github.com/elalish/manifold` @ `2f33e782`, npm manifold-3d 3.5.4 | README 18-23, d.ts, the `.wasm` measured, issue #745 | P |
| truck, `github.com/ricosjp/truck` @ `1ca3214e` | Crates, CHANGELOG; issues #135, #114, #57, #68, #53, #123, #128 | P, P-wf |
| verb, `github.com/pboyer/verb`, npm verb-nurbs 3.0.3 | `build/js/verbHaxe.js` (ES5, measured), `verb.min.js` (not ES5), API | P |
| Fornjot, CADmium, Chili3D | READMEs (archived; inactive; `cpp/CMakeLists.txt` 86-90) | P, P-wf |
| WebKit bug 269777 | "Only ~300 MB of RAM is reliably available to WebAssembly pages" | P-wf |
| Zoo, `zoo.dev/blog/zoo-design-studio-v1` | Their own geometry engine | P-wf |
| DEVELOP3D, "Nvidia launches USD BRep geometry kernel for solid modelling" | History, ClassCAD | S |
| 3Druck, on SMLib under Apache-2.0 | The release | S |
| This app: `src/js/engine/bim/csg-booleans.js`, `reference/research-rhino-guide-gap.md`, `reference/plan-parametric-design.md`, `src/js/vendor/openskp.js`, `THIRD_PARTY_NOTICES.md`, `CLAUDE_INSTRUCTIONS.md` lines 50-51 | As cited | P |
