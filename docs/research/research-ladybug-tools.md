# Ladybug Tools in the app: research and the first experiment

The owner (2026-10-26) shared Ladybug, Honeybee, Butterfly and Dragonfly (ladybug.tools): "they have a lot of
analysis using weather data ... gitclone their codebase ... copy and paste their code and logic". Then, told
the code is AGPL-3.0: "i dont care about legal this app is for me, if we could copy and paste thats what i
want. i dont want to create something new again". Asked how, the owner chose **to run their Python unchanged
in the browser through Pyodide**, over a line-by-line translation or a mix of both.

This note follows `reference/research-protocol.md` and `reference/reuse-first-integration.md`. It records
what was read and run on 2026-10-26, the experiment's results, the proposed integration, and the owner's
remaining decisions. No app code has changed yet.

## 1. The upstream projects (P, read as text from their repositories, 2026-10-26)

Shallow clones kept outside the repository (the session's scratchpad), never committed.

| Project | Repository, commit | Licence | Last commit | Python lines (no tests) | What it does |
|---|---|---|---|---|---|
| ladybug (core) | github.com/ladybug-tools/ladybug `329a3b8` | AGPL-3.0 | 2026-09-22 | 29,736 | EPW, DDY, STAT and WEA weather files, data collections, sun path, psychrometric chart, wind rose, solar envelope, sky models, degree days |
| ladybug-geometry | ladybug-tools/ladybug-geometry `4191f61` | AGPL-3.0 | 2026-09-16 | 21,134 | the geometry the others use (2D and 3D, meshes, polyfaces) |
| ladybug-comfort | ladybug-tools/ladybug-comfort `00a9531` | AGPL-3.0 | 2026-10-19 | 15,102 | UTCI, PMV, adaptive comfort, PET, SolarCal, heat index, wind chill, WBGT, comfort maps |
| ladybug-radiance | ladybug-tools/ladybug-radiance `e193ef0` | AGPL-3.0 | 2026-05-18 | 3,766 | sky matrix, radiation studies; needs numpy and Radiance's `gendaymtx` (native) |
| ladybug-display | ladybug-tools/ladybug-display `9f1fdd8` | AGPL-3.0 | 2026-09-22 | 15,392 | display objects for the visualisations |
| honeybee-core | ladybug-tools/honeybee-core `a96eaa7` | AGPL-3.0 | 2026-10-21 | 19,986 | the building model: rooms, faces, apertures, shades; HBJSON |
| honeybee-energy | ladybug-tools/honeybee-energy `311d700` | AGPL-3.0 | 2026-10-21 | 60,548 | constructions, loads, schedules, programs; writes EnergyPlus IDF and OpenStudio; runs EnergyPlus as a separate program (`run.py`) |
| honeybee-radiance | ladybug-tools/honeybee-radiance `e8f57e4` | AGPL-3.0 | 2026-10-21 | 33,583 | daylight models; runs Radiance as a separate program |
| dragonfly-core | ladybug-tools/dragonfly-core `95af7bd` | AGPL-3.0 | 2026-10-21 | 29,695 | district and urban models (URBANopt, Urban Weather Generator) |
| butterfly | ladybug-tools/butterfly `c8fc0bb` | GPL-3.0 | **2020-09-10** | 10,200 | OpenFOAM cases for CFD; unmaintained for six years |

**The import closure** (counted with a script over each module's imports, inside ladybug, ladybug-comfort and
ladybug-geometry): `ladybug.epw` pulls 51 files (24,725 lines); EPW, sun path, psychrometric chart, wind rose,
solar envelope and the UTCI, PMV and adaptive comfort together pull 82 files (42,834 lines). UTCI, PMV and
adaptive alone are 4 files (1,870 lines). This is what a line-by-line translation would have cost.

**What cannot run in a browser in any form:** EnergyPlus and OpenStudio (honeybee-energy's simulation),
Radiance (honeybee-radiance, ladybug-radiance's sky matrix), OpenFOAM (butterfly), URBANopt (dragonfly). They
are native programs the Python launches. The Python that *prepares* their inputs does run (section 3).

## 2. The licence (P, the LICENSE files; the owner's decision)

Every current Ladybug Tools library is AGPL-3.0; butterfly is GPL-3.0. Shipping them inside the app makes the
app a work under the AGPL: its source is offered to whoever uses it (the repository is public already) and the
whole stays under AGPL-3.0.

**The owner's decision (2026-10-26): accepted.** "this app is for me".

**It changes an earlier decision, recorded so it is a choice, not an accident:** in V166 the owner declined
Transitous because "its terms would open the code and rule out selling the app" (PIPELINE.md, row 166). The
AGPL has that effect on the app as a whole. Pyodide itself is MPL-2.0 (P, its LICENSE at tag 0.29.5).

## 3. The experiment: their code, unchanged, in our browser (run 2026-10-26)

Kept in `wip/ladybug-poc/` (`page.html`, `run.py`): a page opened from `file://` in the Chromium the suites
use (chromium-1243, Playwright 1.63.0), which loads Pyodide 0.29.5 from jsDelivr, installs the wheels from
PyPI with micropip, writes an EPW into Pyodide's file system and runs Ladybug's own classes on it.

Weather file: Philadelphia International Airport, TMYx 2009-2023, from climate.onebuilding.org (1,601,225
bytes; downloaded by the test script, not committed).

| Step | Time from page start | Notes |
|---|---|---|
| `pyodide.js` loaded | 0.13 to 0.46 s | |
| Pyodide ready | 2.85 to 3.39 s | Python 3.13 |
| micropip | 3.2 to 3.7 s | |
| ladybug-core 0.44.62 and ladybug-comfort 0.19.12 installed (with ladybug-geometry 1.35.6, click 8.3.3) | 4.6 to 6.2 s | from PyPI, no changes |
| honeybee-energy 1.126.6 installed (with honeybee-core 1.64.79, honeybee-standards 2.0.7) | 8.7 s | |
| A 10 x 8 x 3.2 m room as a Honeybee model, written as EnergyPlus IDF (14,120 characters) and HBJSON (12,317) | 10.2 s | 1.5 s |
| A year's analysis (below) | +1.0 to 1.7 s | |

Downloaded: 6.46 MB in 19 responses for Ladybug alone; 9.96 MB in 42 with Honeybee (sizes as sent, mostly
compressed). After the first visit the browser's cache keeps them.

**The year's analysis, Ladybug's own numbers for Philadelphia:** mean dry bulb 14.20 C; UTCI (outdoor, shade,
MRT = air temperature) comfortable 40.9% of hours, heat stress 8.7%, cold stress 50.4%; the sun at noon on
21 June 73.56 deg high, azimuth 177.74 deg; the psychrometric chart's coloured mesh 614 cells; wind calm 7.4%
of hours (16 directions).

**What this shows (P, observed):** the libraries install from PyPI and run unchanged in Chromium, from a
`file://` page while online; the EPW reader, sun path, psychrometric chart, wind rose, UTCI collection and
Honeybee's model, IDF and HBJSON writers all work. Not yet tried: a phone, Safari, memory on a large model,
`ladybug-comfort`'s maps (they need numpy, which Pyodide has as a package).

## 4. Data: where the weather comes from (tested 2026-10-26)

| Source | Test | Result | Use |
|---|---|---|---|
| climate.onebuilding.org (EPW, TMYx) | GET with an Origin header; OPTIONS preflight | 200, **no Access-Control-Allow-Origin** | The browser cannot fetch it. Named, not proxied: the user downloads the ZIP and opens it in the app |
| Open-Meteo archive (ERA5), already used by V159's CLIMATEGET | the app's own code (`src/js/engine/site-analysis/climate-data.js`) | CORS open (V159) | Hourly temperature, humidity, wind already fetched; Ladybug's `EPW.from_missing_values` can take them, so most analyses need no file |
| cdn.jsdelivr.net (Pyodide) | GET with Origin | 200, `*` | Pyodide's runtime |
| pypi.org JSON, files.pythonhosted.org (wheels) | GET with Origin | 200, `*` | The wheels; or a pinned copy served with the app (section 5) |

## 5. What the app has, and where Ladybug fits (P, the app's code)

Already built: the Climate and risk board (V159: temperature with rain, wind roses, hourly heat map, sun path,
degree days, solar, a psychrometric comfort figure, from Open-Meteo), `src/js/engine/site/sun-position.js`,
and the analyses in the model (`src/js/engine/site-analysis/model-analyses.js`: sun paths on a dome,
shadows, winds by season, isovists, noise), all in V171b's analysis workspace.

Ladybug adds: EPW and design-day input; UTCI, PMV, adaptive comfort, PET, heat index, wind chill; a full
psychrometric chart with comfort polygons; degree-time and design conditions; the solar envelope; sun-hours
and radiation on the model's faces (with numpy, without Radiance: `ladybug_radiance` needs `gendaymtx`, so the
sky matrix would be read from an EPW by ladybug's own sky model); Honeybee models of the design written as
HBJSON and IDF for EnergyPlus, OpenStudio, Pollination or Grasshopper to run.

**Proposed integration (to be designed in the phase, not built yet):**
- A small engine folder, `src/js/engine/ladybug/`: loads Pyodide on first use only (the app opens as fast as
  now), installs the pinned wheels, runs one Python function per analysis in a Web Worker so the drawing never
  waits, and caches the runtime.
- Narrow adapters, ours: Open-Meteo hourly or an opened EPW -> Ladybug data collections; the app's site place
  -> `Location`; the model's rooms and walls -> Honeybee `Room`s; results -> the existing boards, diagrams and
  result layers, with Ladybug credited as the method on every one.
- Pinned versions; the wheels and Pyodide served with the Pages site so the hosted app does not depend on
  PyPI's or jsDelivr's uptime (the `file://` copy still needs a network for these analyses).
- The zero-dependency, offline contract gets one written exception: these analyses only, loaded on demand.
  Everything else in the app stays as it is and works offline.

## 6. The owner's decisions

Made on 2026-10-26:
1. The AGPL accepted; their code used as is (section 2).
2. Pyodide, running their Python unchanged, over translating it (the exception in section 5).

Made on 2026-10-26, in answer to the three questions:
3. **After V172.** Two phases, numbered as V171b was, after the phase they follow, so no later phase is
   renumbered: **V172b, weather and comfort** (EPW input, UTCI and PMV, the psychrometric chart, the wind rose,
   design days), then **V172c, sun-hours and radiation on the model**.
4. **No Honeybee export.** "dont go for this path". Honeybee, Butterfly and Dragonfly are left out; only
   ladybug, ladybug-geometry and ladybug-comfort (and numpy for V172c, if its sky needs it) are loaded.
5. **Hosted with the app, the owner asking which is the better experience.** Served from the Pages site:
   - nothing at run time depends on PyPI or jsDelivr being up, or on their versions staying where they are;
   - the versions are the ones the suites tested, byte for byte, kept by their SHA-256;
   - one origin, so no CORS, and a later service worker can keep them for offline use;
   - kept once, at a fixed path (`runtime/pyodide/0.29.5/`, `runtime/wheels/`), not inside each of the
     guide's older versions at `v/<version>/`, so the site grows about 10 MB once, not per version.
   The `file://` copy loads them from the Pages site's address, so it needs the network for these analyses only.

## 7. Still open

- A phone and Safari: not yet run (the suites' Chromium only).
- The sky matrix without Radiance: which of ladybug's sky models stands in for `gendaymtx`, and how its
  numbers compare; to be read in `ladybug/skymodel.py` and `ladybug_radiance/skymatrix.py` before (b).
- EnergyPlus itself in the browser: no official WebAssembly build found; not researched further.
