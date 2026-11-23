# Research: which library reads and writes DWG in the browser (D9)

Date: 2026-11-22. Status: research done to the level stated per finding; nothing built, nothing run from a download;
the owner's approval is still to be asked (part 11). Follows `research-protocol.md` and `reuse-first-integration.md`,
compactly. Prior: `research-cadcraft-gap.md` (D9: "DWG, research only first").

## 1. Abstract

Question: which open-source library lets the app read, and ideally write, AutoCAD DWG files in the browser, under
the third-party rule in `CLAUDE.md` (permissive or MPL licence, vendored and pinned under `runtime/`, loaded on
demand, behind a narrow adapter; GPL only as a separate program in a worker)? Eight candidates were read at their
source. Answer: **cc-dwg, BimCraft's own DWG library (getcadcraft/bimcraft, Apache-2.0)**, the same upstream as the
cc-ifc engine the app already vendors (V196). It is plain JavaScript with no dependencies, reads R13 to R2018
(AC1012 to AC1032) and writes R2000 to R2018 (AC1015 to AC1032), and bundles to 315 KB minified, 107 KB gzipped, ten
times smaller than the acadrust WebAssembly and twenty times smaller than LibreDWG's. It fits the rule as a normal
library, with no worker requirement. The runner-up is acadrust (MPL-2.0, Rust to WebAssembly, the library CADCraft
uses), which also fits as a normal library but costs a Rust build and 1.2 MB gzipped. LibreDWG (GPL-3.0+) fits only
as a separate worker program and is not recommended. The ODA Drawings SDK and Autodesk RealDWG are proprietary and
excluded. Reading fidelity of every candidate is still unmeasured here (part 10): the recommendation is conditional on
a bake-off on real drawings before the owner approves.

## 2. The question and the hypotheses

What a good answer must decide: the library; its licence class under the rule (normal library, or separate program
only); which DWG versions it reads and writes; its browser path (JS, or WASM and how it is built); its size; how it is
maintained; how it plugs into `src/js/engine/io/`.

| H | Claim (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | A DWG reader under MIT/BSD/ISC/Apache-2.0/MPL-2.0 exists with a browser path covering R2000 to R2018 | **Held** | Five: cc-dwg, acadrust, acad-ts, @isopodlabs/dwg, and acadrust's npm WASM builds (P, licence files read) |
| H2 | acadrust builds for `wasm32-unknown-unknown` | **Held (S for the build; not built here)** | Its CI checks the lib for wasm32 with default, no-default and all features (P, `ci.yml`); `dwg-to-dxf@0.1.2` ships a WASM whose `Cargo.lock` pins acadrust 0.6.8 by the same checksum as the crate read here (P) |
| H3 | LibreDWG cannot ship as a normal library under the rule | **Held** | GPL-3.0-or-later (P, upstream README); `@mlightcad/libredwg-web` is GPL-3.0 (P, package.json) |
| H4 | A permissive DWG library costs under 2 MB gzipped on demand | **Held** | cc-dwg 107 KB gz, acad-ts 262 KB gz, acadrust WASM 1.19 MB gz (measured, part 6) |
| H5 | A permissive library writes DWG at R2000 or later | **Held as documented, not tested** | cc-dwg `write.js` (AC1015 to AC1032), acadrust README (AC1009 to AC1032), acad-ts README (all); no write was run here |
| H6 | DWG in this app needs a worker for licence reasons | **Failed** for the recommended library (Apache-2.0); a worker is still wanted for responsiveness on big files (cc-dwg ships its own, `read-async.js`) |

## 3. Method

Search log (2026-11-22, all from this environment):

| # | Where | Query / request | Result | Kept / set aside |
|---|---|---|---|---|
| 1 | repo | `grep dwg` in `docs/research`, `src/js/engine/io` | D9 in `research-cadcraft-gap.md`; `import-entry.js:49` refuses `.dwg` with a toast | Kept: context |
| 2 | raw.githubusercontent | storytold/cadcraft README | "DWG files (R13 through 2018) open and save through the open-source acadrust library"; DWG write R2000 | Kept |
| 3 | crates.io API | `/api/v1/crates/acadrust` | MPL-2.0, 0.6.8 (2026-10-27), 37 versions since 2026-02-07, repo hakanaktt/acadrust | Kept |
| 4 | static.crates.io | acadrust-0.6.8.crate, unpacked to scratch, read as text | Cargo.toml, README, LICENSE, THIRD_PARTY_NOTICES, `src/io/dwg/*` | Kept |
| 5 | raw.githubusercontent | hakanaktt/acadrust `.github/workflows/ci.yml` | `wasm` job: `cargo check --lib --target wasm32-unknown-unknown` x3 | Kept |
| 6 | api.github.com, `gh api` | repo metadata for acadrust, libredwg-web | **Refused** (403: GitHub access limited to this session's repositories). Stars, issues not read | Recorded |
| 7 | npm registry | `npm view` for @mlightcad/libredwg-web, libredwg-web, dwg, acadrust, dwg2dxf, dxf-viewer, dxf-parser, @mlightcad/cad-simple-viewer, @mlightcad/libredwg-converter | Part 5 table; `libredwg-web`, `dwg`, `acadrust` are 404 on npm | Kept |
| 8 | npm registry | `npm search dwg` | Found acad-ts, @isopodlabs/dwg, dwgdxf, dwg-to-dxf, @njbestway/acad-rust-converter, dwg2dxf-converter, @cadview/dwg, @flyfish-dev/cad-viewer | Kept the permissive ones for download |
| 9 | npm tarballs | 6 packages downloaded to scratch, each in its own folder, read as text, never run | Sizes, SHA-256, LICENSE, README, Cargo.toml of the WASM glue | Kept |
| 10 | raw.githubusercontent | LibreDWG/libredwg README, NEWS | GPL-3+, reads and writes all versions; 0.15 NEWS lists six security fixes incl. CVE-2026-63474 | Kept |
| 11 | www.gnu.org | /software/libredwg/ | **Refused** (connection reset) | Recorded; GitHub mirror used |
| 12 | raw.githubusercontent | DomCR/ACadSharp LICENSE, README | MIT; DWG R/W AC1014 to AC1032; C# only | Kept as ancestry |
| 13 | www.opendesign.com | /products/drawings | Pricing and membership pages: proprietary SDK | Kept (exclusion) |
| 14 | repo | `vendor/cc-ifc/PROVENANCE.md` | Names BimCraft's own clean-room DWG engine, cc-dwg | Led to 15 |
| 15 | github.com (git, blob-less clone) | getcadcraft/bimcraft @ e36a94d | `app/dwg/` (26 files) and `tests/lib/dwg/` (39 files, with the writer); LICENSE, NOTICE, PROVENANCE, THIRD_PARTY | Kept |
| 16 | local | esbuild 0.28.2 (the version `tools/ifc` pins) bundling cc-dwg into an IIFE | Size only; the bundle was not run | Kept, part 6 |

Experiments: sizes and hashes only (part 6). No downloaded code was executed (the protocol's rule); no Rust build was
run (the reuse-first rule asks the owner first). Scripts were shell commands kept in the session scratchpad; the
commands are in part 6 so they can be repeated. Independent second reader: **not done** in this session (one agent);
part 10 lists it as open.

## 4. Findings

F1. **cc-dwg (BimCraft) is Apache-2.0, clean-room, dependency-free JavaScript.** P: `LICENSE` (Apache 2.0, sha256
`0d542e0c...94594`), `NOTICE` (trademark clause: the names CadCraft/BimCraft may not be used, as for cc-ifc), every file
`SPDX-License-Identifier: Apache-2.0`; `PROVENANCE.md`: "written clean-room from the Open Design Alliance's published
Open Design Specification for .dwg files, version 5.4.1"; LibreDWG, libdxfrw and the ODA File Converter used only as
black-box test oracles, never read or shipped. No bare imports in any of its 39 files; `Buffer` only behind a
`typeof Buffer` guard. Confidence high.

F2. **cc-dwg versions.** P: `header-vars.js:25` `VERSION_NUM = {AC1012, AC1014, AC1015, AC1018, AC1021, AC1024, AC1027,
AC1032}` (read R13 to R2018); `container-read.js:44` refuses other AC10xx and pre-R13 with a message;
`tests/lib/dwg/write.js` header: `writeDwg(model, {version})` for AC1015, AC1018, AC1021, AC1024, AC1027, AC1032;
`index.js` exports `readDwg`, `writeDwg`, `VERSIONS`. `readDwg` never throws on a damaged object by default (notes it in
`report.notes`), `strict` throws, `recover` walks unlisted objects. Its test harness (`tests/tools/dwg-test/README.md`)
compares against ODA-converted truth for 13 drawings x 7 versions (85 files). Confidence: high for what the code
declares; fidelity untested here.

F3. **cc-dwg layout.** P: BimCraft ships the read side in `app/dwg/` (26 files, byte-identical to the same files in
`tests/lib/dwg/`, checked with `cmp`); the full library with the writer is `tests/lib/dwg/` (39 files, 689,631 bytes,
tree `b5a357e1e5c71ec2f8c147ebcefb49db54ede68e`). Its `read-async.js` runs `readDwg` in a module worker built from its
own files by `import.meta.resolve`, which does not survive bundling into one classic script; the adapter supplies its
own worker instead (part 8). History: 7 commits touching these folders, 2026-10-13 to 2026-11-17 (weekly snapshots).

F4. **acadrust is MPL-2.0 Rust, R/W AC1009 to AC1032 (as documented).** P: crate 0.6.8 Cargo.toml `license = "MPL-2.0"`,
LICENSE (MPL 2.0 text), README "File Version Support" table (R/W for DXF and DWG, AC1009 to AC1032). Its DWG code is
ported from ACadSharp (MIT; THIRD_PARTY_NOTICES). 229,982 lines of Rust in `src/`; crate 2,787,321 bytes, sha256
`eb201e11...99929`. Wasm-aware code: `memmap2` and `rayon` excluded on wasm32; `DwgReader::from_stream` takes any
`Read + Seek` (so `Cursor<&[u8]>`), `DwgWriter::write_to_vec`. Has bounded decompression (`with_max_decompressed_bytes`)
and mesh budgets. Used by CADCraft and Open CAD Studio (README). 37 releases in nine months. Confidence high.

F5. **acadrust has no official npm/WASM build.** P: npm `acadrust` is 404. Third-party builds: `dwg-to-dxf@0.1.2`
(MPL-2.0, gitee.com/seaweedman, created 2026-11-03): DWG to DXF text only, acadrust 0.6.8 `default-features = false`,
`opt-level = "s"`, `wasm-opt = false`; `@njbestway/acad-rust-converter@0.1.0` (MIT AND MPL-2.0, acadrust 0.6.6, with a
JSON entry); `dwgdxf@2.0.1` (labelled MIT, acadrust 0.4.0, README wrongly calls acadrust MIT; stale). None writes DWG
from JS. Confidence high.

F6. **LibreDWG is GPL-3.0-or-later; its web build is GPL-3.0.** P: upstream README lines 5-6 and 241-243 ("reads all
DWG versions", "the writer can write all DWG versions"); `@mlightcad/libredwg-web@0.9.2` package.json `GPL-3.0`, no
LICENSE file in the tarball; its README says DWG write and DXF read share LibreDWG's `USE_WRITE` gate. Upstream NEWS for
0.15 (2026-11-28, beta) lists six security fixes in the parsers (heap overflow, double free, use-after-free). Under the
rule it can only be "its own unchanged file under `runtime/`, run only inside a worker, reached only by messages", and
the app must work without it. Confidence high.

F7. **acad-ts is MIT TypeScript (port of ACadSharp), R/W AC1009 to AC1032 (as documented).** P: LICENSE (MIT, Jochen
Kuehner and Albert Domenech); README version table; `dist/index-min.js` (esbuild ESM, platform neutral) 1,245,408
bytes, 261,849 gzipped, no `require`. 20 releases since 2026-04-13. Confidence high for the claims; fidelity untested.

F8. **Others.** `@isopodlabs/dwg@1.2.1` (MIT): read only, R13 to R2018, 450 KB dist, one release (2026-10-01).
`dwg2dxf-converter@1.0.4` labelled MIT but "powered by LibreDWG WebAssembly": the label cannot be right for GPL code;
excluded. `dwg2dxf@2.0.3` (ISC label, an Emscripten build of LibreDWG by its description): same problem; excluded.
`@cadview/dwg`, `@classic-homes/viewer-dwg`: GPL (LibreDWG). `@flyfish-dev/cad-viewer`: AGPL-3.0. ACadSharp itself (MIT,
C#): no browser path short of a .NET WebAssembly runtime; it is the ancestor of acadrust and acad-ts. ODA Drawings SDK
and Autodesk RealDWG: proprietary, paid membership or licence (P for ODA: its pricing and membership pages; RealDWG
from general knowledge, U); excluded by the rule.

F9. **What the app's DXF importer can take.** P: `src/js/engine/io/import-dxf.js` handles LINE, LWPOLYLINE, POLYLINE,
CIRCLE, ARC, POINT, 3DFACE only (no INSERT, TEXT, MTEXT, HATCH, DIMENSION). Any "DWG to DXF text, then the existing
importer" route inherits that limit, so a direct model adapter is better.

## 5. The alternatives compared

Criteria, fixed before the table: licence class under the rule; DWG versions read and written; browser path and
build cost; download size on demand (gzipped); maintenance; and fit with the rule.

| | cc-dwg (BimCraft e36a94d) | acadrust 0.6.8 (own WASM build) | acad-ts 3.9.0 | LibreDWG via @mlightcad/libredwg-web 0.9.2 | @isopodlabs/dwg 1.2.1 | ODA / RealDWG |
|---|---|---|---|---|---|---|
| Licence | Apache-2.0 (same as this repo) | MPL-2.0 (file-level copyleft) | MIT | GPL-3.0(+) | MIT | Proprietary |
| Read | AC1012-AC1032 (R13-R2018) | AC1009-AC1032 (R11/12-R2018) | AC1009-AC1032 | all (R13-R2018 solid; preR13 partial) | AC1012-AC1032 | all |
| Write | AC1015-AC1032 (R2000-R2018) | AC1009-AC1032 | AC1009-AC1032 | all versions per upstream | none | all |
| Browser path | Plain JS, one IIFE by esbuild (as cc-ifc) | Rust + wasm-bindgen; we build it (cargo present here, wasm32 target not installed) | Plain JS (ESM bundle; re-bundle as IIFE) | Emscripten WASM + glue, prebuilt | Plain JS | None open |
| Size (measured) | 315 KB min, **107 KB gz** (full); 178 KB / 58 KB read-only | 3.37 MB, 1.19 MB gz (dwg-to-dxf's read-only build; with write and JSON about 6.8 MB raw per @njbestway) | 1.25 MB, 262 KB gz | 7.84 MB wasm, 2.05 MB gz, + 110 KB glue | 450 KB unbundled | n/a |
| Maintenance | Company (The Data Design Group), weekly snapshots, ODA-truth corpus tests | 37 releases, CI on 3 OS + wasm32, two downstream CAD apps | 20 releases, one maintainer, tracks ACadSharp commits | GNU project, frequent; repeated parser CVEs | one release | n/a |
| Already in the app's supply chain | Yes: cc-ifc from the same repo (V196) | No | No | No | No | No |
| Fit with the rule | **Normal library** | **Normal library** (MPL file kept as its own file, source offered) | **Normal library** | **Separate worker program only**; app must work without it | Normal, but read only | **Excluded** |

Recommendation: **cc-dwg**. It is the only candidate that is at once permissive under our own licence, plain JS (no
toolchain, no WASM, works the way cc-ifc already works in this repo), the smallest by a factor of ten, and
read-and-write across R2000 to R2018. acadrust is the runner-up and wins on breadth (R12 to R2018, AEC objects, ACIS)
and on the evidence of two shipping CAD apps.

What would change it: (a) the bake-off (part 10) shows cc-dwg dropping entities that acadrust or acad-ts keep on real
drawings; (b) R12 or R13c3 drawings turn out to matter to the owner (cc-dwg refuses pre-R13); (c) BimCraft stops
publishing `tests/lib/dwg` or changes its licence. Under (a) or (b) the choice is acadrust; acad-ts is the fallback if
a Rust build is unwanted.

## 6. The experiments (measurements only)

Environment: this container, 2026-11-22, Node with npm 10, esbuild 0.28.2 (the version `tools/ifc/package-lock.json`
pins), one run each (sizes are deterministic).

| Artifact | Bytes | Gzip | SHA-256 |
|---|---|---|---|
| acadrust-0.6.8.crate | 2,787,321 | (is gzip) | eb201e11e1c75584e4deefc2b30afb83e2f34d16338733439d38664cb9599929 |
| dwg-to-dxf 0.1.2 `dist/wasm/dwg_to_dxf_bg.wasm` (acadrust 0.6.8) | 3,366,462 | 1,186,238 | ef07747eb0306db27c4e5d3b58f0eb56811187d5b3fe011dafc4e81b1c1e3acd |
| @njbestway/acad-rust-converter 0.1.0 `acad-rust_bg.wasm` (0.6.6) | 6,756,778 | not measured | |
| dwgdxf 2.0.1 `dwgdxf_bg.wasm` (acadrust 0.4.0) | 821,610 | not measured | |
| @mlightcad/libredwg-web 0.9.2 `wasm/libredwg-web.wasm` | 7,840,315 | 2,052,713 | e4b873d9921bcc779d4389ca28fccc08c9fd8ada9b1d54baa104d42b19a6f609 |
| @mlightcad/libredwg-web 0.9.2 tarball | 2,352,311 | | cb9a4e1ae54dcec0c4d02e6dc2ae5cfe6c63d6507ffc7a6a4c52eb9d26f17568 |
| acad-ts 3.9.0 `dist/index-min.js` | 1,245,408 | 261,849 | a4356a398d3b8a90cbfc84aa6a513266507dd6896e567ba7652a6e8a3de74c54 |
| cc-dwg `tests/lib/dwg/*.js` source (39 files) | 689,631 | 206,440 | git tree b5a357e1e5c71ec2f8c147ebcefb49db54ede68e |
| cc-dwg full, `esbuild index.js --bundle --minify --format=iife --target=es2020` | 314,778 | 107,409 (gzip -9) | (scratch only) |
| cc-dwg read only (`readDwg` from `read.js`), same flags | 178,384 | 58,318 | (scratch only) |

Commands: `npm view <pkg> license version dist.unpackedSize dist.tarball repository.url`; `curl` the tarball or crate
into its own new folder; `tar xzf`; `ls -l`, `sha256sum`, `gzip -c | wc -c`; for cc-dwg
`git clone --filter=blob:none --no-checkout https://github.com/getcadcraft/bimcraft.git`, `git checkout HEAD --
tests/lib/dwg app/dwg LICENSE NOTICE PROVENANCE.md THIRD_PARTY.md`, then the esbuild line above. What these show: size
only. They do not show that any library reads a file correctly.

## 7. Edges

- Pre-R13 (AC1009 R11/R12, AC1.x, MC0.0) and R13c3 (AC1013): cc-dwg and @isopodlabs refuse; acadrust, acad-ts and
  LibreDWG claim R12. The adapter must toast the version it refused, not fail silently.
- R2007 (AC1021) uses a different container (Reed-Solomon, LZ77 variant): a separate code path in every library
  (`r2007.js`, `decompressor_ac21.rs`), the most likely place for a reading gap; the bake-off must include it.
- AutoCAD 2018 to 2026 still save AC1032; there is no newer DWG version to support as of this date (U: no newer
  signature appears in any of the libraries read).
- Proxy objects, ACIS solids (3DSOLID, REGION, BODY), dynamic blocks, AEC objects: cc-dwg reads ACIS data and dynamic
  blocks (`solid-read.js`, `dynblock-read.js`); acadrust reads AEC (ACAD Arch). Whether the app can show them is a
  separate question.
- Damaged files and decompression bombs: cc-dwg never throws by default and notes failures; acadrust caps decompressed
  bytes. A 10-byte "AC1027fake" stub is in BimCraft's corpus as a must-not-crash case.
- Code pages before R2007 (about 40): all claim support; Japanese, Korean, Chinese, Cyrillic and Vietnamese fixtures
  exist in BimCraft's `fixtures/dwg/codepage/` (DXF form).
- `file://`: a plain-JS library inside `canvas_v10.html`'s runtime folder still needs fetching, like three.js; an IIFE
  loaded by a `<script>` tag works from `file://` where a WASM `fetch` does not, a point in cc-dwg's favour.

## 8. What the app already has

- `src/js/engine/io/import-entry.js:49`: `.dwg` (with STEP/IGES) answers "is not supported ... Export as DXF". The hook
  for a DWG branch.
- `src/js/engine/io/import-dxf.js:175` `bimImportDXF(text, filename)`, with `bimDxfApplyLayer` (164) and `dxfAciToHex`
  (18): layer and colour mapping to reuse; entity coverage as in F9.
- `src/js/engine/io/dxf-export.js`: the DXF writer whose element-to-entity choices a DWG save would mirror.
- `src/js/engine/io/ifc-full.js` with `runtime/cc-ifc/cfbd948/bim-ifc.min.js`, `vendor/cc-ifc/` and
  `tools/ifc/build_ifc.mjs`: the exact precedent (same upstream, esbuild to one classic script with one global, loaded
  on demand, MANIFEST-pinned).
- `src/js/engine/io/ifcos-worker.js`: a classic worker built from a Blob that checks each runtime file's SHA-256 before
  use; the pattern for a DWG worker.

## 9. Risks and threats to validity

- **Fidelity unmeasured** for every candidate (no downloaded code was run). Every version table above is the
  library's own claim (P for the claim, U for the behaviour).
- cc-dwg's writer lives under BimCraft's `tests/lib/`, not in its shipped `app/`: BimCraft may be using it only in
  tests, so its write path may be less exercised than its read path.
- Single upstream: cc-dwg and cc-ifc both depend on one company's public repository, published as weekly snapshots;
  a licence change would affect only later revisions (the pinned one stays Apache-2.0).
- acadrust's WASM was measured from a third party's build, not ours; our build with the writer would be larger.
- Search coverage: npm and crates.io only; GitHub search and repository metadata were refused (search log 6). A
  permissive reader published only on GitHub could be missed.
- Licence labels on npm were found wrong twice (F8, F5's dwgdxf); every licence here was read in the LICENSE file or
  manifest itself, not the registry label alone.

## 10. What is still open (U)

1. A bake-off: read the same drawings (BimCraft's public `fixtures/dwg` and Autodesk's public samples, all versions
   AC1015 to AC1032, plus an R2007 and a damaged file) with cc-dwg, acadrust and acad-ts, and compare entity counts and
   geometry with an ezdxf dump. Needs the owner's approval to run upstream code (reuse-first policy), in an isolated
   folder.
2. Round trip: write R2000 and R2018 with cc-dwg from a small app model and reopen it in acadrust and LibreDWG's
   `dwgread` (oracles as programs only).
3. The independent second reader (protocol step 9) has not re-checked F1 to F8.
4. acadrust's repository metadata (open issues, stars) and LibreDWG's gnu.org page: hosts refused here.
5. Autodesk RealDWG's licence terms: general knowledge only (U); changes nothing, it is excluded either way.

## 11. The owner's decisions

- **Q1.** Approve cc-dwg (BimCraft, Apache-2.0) as the DWG library, pinned at a BimCraft commit, vendored like cc-ifc?
  Or acadrust (MPL-2.0, Rust/WASM build, 1.2 MB gz) for R12 coverage and a wider user base?
- **Q2.** Read only first (58 KB gz), or read and write (107 KB gz) in one step?
- **Q3.** Approve running the bake-off (open item 1) on public drawings before the phase starts?

Answers: not yet given.

## Integration sketch (if Q1 is cc-dwg)

- `vendor/cc-dwg/`: BimCraft `tests/lib/dwg/` at the pinned commit, unchanged, with LICENSE, NOTICE, PROVENANCE.md,
  and a README naming the commit (as `vendor/cc-ifc/README.md`). Never edited by hand.
- `tools/dwg/build_dwg.mjs`: esbuild (the pinned 0.28.2 in `tools/ifc`, or its own lock) bundles `index.js` into one
  classic IIFE with one global (`CCDWG`), as `tools/ifc/build_ifc.mjs` does.
- `runtime/cc-dwg/<rev>/cc-dwg.min.js` (about 315 KB) plus LICENSE and NOTICE, each pinned by bytes and SHA-256 in
  `runtime/MANIFEST.json`, checked by `tools/check_runtime.py`.
- `src/js/engine/io/dwg-io.js` (new, ES5, the only file that calls the library): `bimDwgLoad()` loads the script on
  first use; `bimImportDWG(arrayBuffer, name)` runs `CCDWG.readDwg` in a classic Blob worker (the `ifcos-worker.js`
  pattern: SHA-256 checked, `importScripts` of the bundle, bytes in, a plain entity list out, transferred), then maps
  LINE, ARC, CIRCLE, LWPOLYLINE, POLYLINE, ELLIPSE, SPLINE, TEXT, MTEXT, INSERT (blocks expanded), 3DFACE and layers
  to the app's records, reusing `bimDxfApplyLayer` and `dxfAciToHex`; `bimExportDWG(version)` builds the cc-dwg model
  from the same choices as `dxf-export.js` and calls `writeDwg`, behind a Save-as menu entry. Failures warned and
  toasted, with `report.notes` summarised.
- `import-entry.js:49`: route `.dwg` to `bimImportDWG`; STEP/IGES keep their message.
- A worker for responsiveness only, not for licence: the library is Apache-2.0 and may be joined, but keeping it out
  of `canvas_v10.html` and loading it on demand is what the rule asks.
- Tests: `tests/unit/dwg-io.test.mjs` for the mapping with a stubbed model; a public fixture DWG under
  `tests/fixtures/` (BimCraft's `fixtures/dwg/df1-ocs-blocks.dwg` and its truth JSON, Apache-2.0, credited) for the
  phase's browser check.
- If acadrust is chosen instead: `vendor/acadrust-glue/` (a 40-line wasm-bindgen crate in the style of dwg-to-dxf's
  `lib.rs`, plus write), built once with `cargo build --target wasm32-unknown-unknown` and `wasm-bindgen`;
  `runtime/acadrust/0.6.8/acadrust_bg.wasm` and its glue JS pinned; the same `dwg-io.js` adapter, with the WASM
  fetched inside the worker; MPL-2.0 notice and source pointer shipped beside it.

## 12. References

| Source | URL | What was read | Date | Level |
|---|---|---|---|---|
| BimCraft (cc-dwg) | github.com/getcadcraft/bimcraft @ e36a94db95aa472c19ea1580864ea7622056d00e (2026-11-17) | LICENSE, NOTICE, PROVENANCE.md "DWG"; `tests/lib/dwg/index.js`, `write.js` 1-30, `read.js` 1-40, `read-async.js` 1-25, `objects-write.js` 1-15, `container-read.js` 40-47, `header-vars.js` 25, `model.js` 20; `tests/tools/dwg-test/README.md`; file list; `git log` | 2026-11-22 | P |
| acadrust 0.6.8 | static.crates.io/crates/acadrust/acadrust-0.6.8.crate; crates.io API | Cargo.toml, LICENSE, README (versions, wasm), THIRD_PARTY_NOTICES, CHANGELOG 0.6.8, `src/io/dwg/dwg_reader.rs` (public fns, 955-975), `dwg_writer.rs` (public fns) | 2026-11-22 | P |
| acadrust CI | raw.githubusercontent.com/hakanaktt/acadrust/main/.github/workflows/ci.yml | `wasm` job | 2026-11-22 | P |
| CADCraft README | raw.githubusercontent.com/storytold/cadcraft/main/README.md | lines 30, 92-93, 117 | 2026-11-22 | P |
| dwg-to-dxf 0.1.2 | registry.npmjs.org/dwg-to-dxf/-/dwg-to-dxf-0.1.2.tgz | LICENSE, LICENSES/NOTICE.md, README, wasm/Cargo.toml, wasm/Cargo.lock, wasm/src/lib.rs | 2026-11-22 | P |
| @njbestway/acad-rust-converter 0.1.0 | registry.npmjs.org | NOTICE, README | 2026-11-22 | P |
| dwgdxf 2.0.1 | registry.npmjs.org | LICENSE, README | 2026-11-22 | P |
| @mlightcad/libredwg-web 0.9.2 | registry.npmjs.org | package.json, README, wasm file sizes | 2026-11-22 | P |
| LibreDWG | raw.githubusercontent.com/LibreDWG/libredwg/master/README, NEWS | licence, read/write scope, 0.15 security fixes | 2026-11-22 | P (gnu.org refused) |
| acad-ts 3.9.0 | registry.npmjs.org/@node-projects/acad-ts | LICENSE, README (versions), package.json (bundle script), dist/index-min.js | 2026-11-22 | P |
| @isopodlabs/dwg 1.2.1 | registry.npmjs.org | LICENSE.txt, README | 2026-11-22 | P |
| dwg2dxf-converter, dwg2dxf, @cadview/dwg, @flyfish-dev/cad-viewer, others | npm search / npm view | registry metadata only | 2026-11-22 | S (labels; two found wrong) |
| ACadSharp | raw.githubusercontent.com/DomCR/ACadSharp/master/LICENSE, README | MIT, version table | 2026-11-22 | P |
| ODA Drawings SDK | www.opendesign.com/products/drawings | pricing and membership navigation | 2026-11-22 | P (for "proprietary") |
| Autodesk RealDWG | none read | general knowledge | | U |
| This repo | `CLAUDE.md` "Third-party libraries"; `research-protocol.md`; `reuse-first-integration.md`; `research-cadcraft-gap.md` 45, 68, 84; `vendor/cc-ifc/*`; `runtime/MANIFEST.json`; `src/js/engine/io/import-entry.js` 40-53, `import-dxf.js`, `ifcos-worker.js` 1-100 | | 2026-11-22 | P |
