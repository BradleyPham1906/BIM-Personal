# V172c experiments: the sky (gendaymtx), 2026-11-01

Data, not suites. Run here on Linux x86-64, Node 22.23.4, Python 3.13, clang 18.1.3, wasi-sdk 22's sysroot.
The weather: `USA_PA_Philadelphia.Intl.AP.724080_TMYx.2009-2023` from climate.onebuilding.org (not committed).
`S` below is a scratch folder holding the unpacked wheels (`dl/lbc`, `dl/lbg`, `dl/lbr`), the native build
(`ref/gendaymtx`) and the WebAssembly one (`wasi/gendaymtx.wasm`).

| Script | What it measures |
|---|---|
| `ref_sky.py S EPW` | the reference: ladybug-radiance 0.2.12's own `SkyMatrix.from_epw().compute_sky()`, with Radiance's `gendaymtx` built natively from LBNL-ETA/Radiance `5b2a2154` (the eight files in `tools/gendaymtx/build_wasm.py`, gcc -O2) |
| `check_horiz.py S EPW` | the reference sky on a horizontal plane against the EPW's own annual sums |
| `cmp_wasm.js S WEA` | `gendaymtx.wasm` through `wasi-run.js` (stdin in, stdout out) against the native build, in Ladybug's four calls |
| `pyodide_sky.js S RUNTIME EPW` | the whole path in the committed Pyodide 0.29.5: Ladybug's `SkyMatrix` with only `_run_gendaymtx` replaced by a call to the WebAssembly module, against the reference |

## Results (one run each; the times are single runs, not averaged)

**The reference** (`ref_sky.py`): Tregenza 145 patches, direct 1700.4 and diffuse 1100.8 (sums of kWh/m2 per
patch); Reinhart 577 patches, 1700.3 and 1106.2. 0.27 s and 0.46 s.

**Against the EPW** (`check_horiz.py`): EPW annual GHI 1497.0, DHI 497.9, DNI 1700.5 kWh/m2.

| Sky | Direct on horizontal | Diffuse on horizontal | Total | Of GHI |
|---|---|---|---|---|
| Tregenza | 966.2 | 494.9 | 1461.1 | 97.6% |
| Reinhart | 977.2 | 497.1 | 1474.3 | 98.5% |

Diffuse within 0.6% of DHI; the direct short by the patch binning (the sun's energy given to patch centres), less
on the finer sky, as expected.

**WebAssembly against native** (`cmp_wasm.js`): identical bytes in all four calls.

| Call | Bytes | wasm ms | native ms | Identical |
|---|---|---|---|---|
| `-m 1 -d -O1 -A` | 1733 | 48 | 28 | yes |
| `-m 1 -s -O1 -A` | 2220 | 71 | 91 | yes |
| `-m 2 -d -O1 -A` | 5762 | 118 | 63 | yes |
| `-m 2 -s -O1 -A` | 8439 | 215 | 242 | yes |

**Ladybug in Pyodide** (`pyodide_sky.js`): Pyodide 1825 ms to load, the five wheels 195 ms; the largest difference
from the reference over 290 Tregenza values and 1154 Reinhart values: **0** kWh/m2. Ladybug's sky in Pyodide
0.71 s (Tregenza) and 0.81 s (Reinhart), with the Wea written and parsed by Ladybug itself.

**The build is reproducible**: `tools/gendaymtx/build_wasm.py` twice gives the same 114,785 bytes,
SHA-256 `240b199758b1ebc8c4e512d01f478c3b4f01105c66747a2ee12960afbbfab711`, the module these runs used. (Built under
another file name the hash differs: wasm-ld writes the name into the module's name section; the script refuses
any other name.)

Not run yet: in Chromium's worker (the same V8 as Node, but not the same host), on Safari, on a phone.
