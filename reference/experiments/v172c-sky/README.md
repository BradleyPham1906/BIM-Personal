# V172c experiments: the sky (gendaymtx), 2026-11-01

Data, not suites. Run here on Linux x86-64, Node 22.23.4, Python 3.13, clang 18.1.3, wasi-sdk 22's sysroot.
The weather: `USA_PA_Philadelphia.Intl.AP.724080_TMYx.2009-2023` from climate.onebuilding.org (not committed).
`S` below is a scratch folder holding the unpacked wheels (`dl/lbc`, `dl/lbg`, `dl/lbr`), the native build
(`ref/gendaymtx`) and the WebAssembly one (`wasi/gendaymtx.wasm`).

**Which Radiance.** The module in `runtime/` is built from the release **rad6R0P1a** (`7abde14f`, 2025-08-23). The
first build (from `master` at `5b2a2154`) was replaced the same day: the second reader (`../v172c-check.md`, 1c)
found that from 2025-12-19 (`2559a9be`, in rad6R0P2) `gendaymtx -A` writes a `NAVERAGED=` header line, while
ladybug-radiance 0.2.12 skips a fixed 9 lines (`skymatrix.py` 584, `data_lines[9:-1]`); with the longer header
Ladybug keeps the ground, drops the zenith and puts every sky value one patch off. The first experiments did not see
it: they compared Ladybug's parse with itself, and horizontal totals hardly move when every patch shifts by one.
`alignment.py` is the test that would have.

| Script | What it measures |
|---|---|
| `ref_sky.py S EPW` | the reference: ladybug-radiance 0.2.12's own `SkyMatrix.from_epw().compute_sky()`, with Radiance's `gendaymtx` built natively (gcc -O2) from the same release and the same eight files as `tools/gendaymtx/build_wasm.py` |
| `check_horiz.py S EPW` | the reference sky on a horizontal plane against the EPW's own annual sums |
| `alignment.py S WEA EXE...` | Ladybug's `_parse_mtx_data` against an independent parse that finds the header's end by its blank line and skips the ground: is every patch on its own dome patch? |
| `cmp_wasm.js S WEA` | `gendaymtx.wasm` through `wasi-run.js` (stdin in, stdout out) against the native build, in Ladybug's four calls |
| `pyodide_sky.js S RUNTIME EPW` | the whole path in the committed Pyodide 0.29.5: Ladybug's `SkyMatrix` with only `_run_gendaymtx` replaced by a call to the WebAssembly module, against the reference |
| `np_load.js RUNTIME` | numpy by Pyodide's `loadPackage` from the committed runtime (under Node the lock's SHA-256 is not checked; in a browser it is, as Subresource Integrity) |

## Results, the release build (one run each; times are single runs)

**Alignment** (`alignment.py`), the test the first build would have failed:

| Build | Header | -m 1 -d | -m 1 -s | -m 2 -d | -m 2 -s |
|---|---|---|---|---|---|
| rad6R0P1a (the one in `runtime/`) | 8 lines | 0 of 145 misplaced | 0 of 145 | 0 of 577 | 0 of 577 |
| master `5b2a2154` (the first build) | 9 lines | 93 of 145 misplaced | 142 of 145 | 291 of 577 | 569 of 577 |

**The reference** (`ref_sky.py`): Tregenza 145 patches, direct 1700.4 and diffuse 1101.9 (sums of kWh/m2 per
patch); Reinhart 577 patches, 1700.3 and 1106.4. 0.29 s and 0.50 s.

**Against the EPW** (`check_horiz.py`): EPW annual GHI 1497.0, DHI 497.9, DNI 1700.5 kWh/m2.

| Sky | Direct on horizontal | Diffuse on horizontal | Total | Of GHI |
|---|---|---|---|---|
| Tregenza | 966.2 | 495.2 | 1461.3 | 97.6% |
| Reinhart | 977.2 | 497.1 | 1474.3 | 98.5% |

Diffuse within 0.6% of DHI; the direct short by the patch binning (the sun's energy given to patch centres), less
on the finer sky. (With the misaligned first build the Tregenza diffuse was 494.9: the totals barely notice.)

**WebAssembly against native** (`cmp_wasm.js`): identical bytes in all four calls.

| Call | Bytes | wasm ms | native ms | Identical |
|---|---|---|---|---|
| `-m 1 -d -O1 -A` | 1718 | 43 | 25 | yes |
| `-m 1 -s -O1 -A` | 2205 | 62 | 64 | yes |
| `-m 2 -d -O1 -A` | 5747 | 103 | 63 | yes |
| `-m 2 -s -O1 -A` | 8424 | 207 | 239 | yes |

**Ladybug in Pyodide** (`pyodide_sky.js`): Pyodide 1710 ms to load, the wheels 81 ms; the largest difference from
the reference over 290 Tregenza values and 1154 Reinhart values: **0** kWh/m2; Ladybug's sky 0.61 s and 0.85 s.

**numpy** (`np_load.js`): loaded from the committed runtime in 777 ms, 2.2.5.

**The build is reproducible**: `tools/gendaymtx/build_wasm.py` twice gives the same 114,742 bytes,
SHA-256 `45726aea4f019ca39dd2c6ba1cdfe42554f523010b7ac6ed6b25504d70ef05e5`, the module in `runtime/`. (Built under
another file name the hash differs: wasm-ld writes the name into the module's name section; the script refuses
any other name.)

In Chromium's worker: see `../v172c-rays/README.md`. Not run: Safari, a phone.
