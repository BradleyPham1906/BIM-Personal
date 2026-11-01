# V172b, Ladybug L1: weather and comfort -- research

The owner's decisions of 2026-10-26 (`reference/research-ladybug-tools.md`, 6) set the frame: Ladybug Tools' own
Python, unchanged, run by Pyodide, the AGPL accepted, no Honeybee, Pyodide and the wheels served with the Pages site
at a fixed path, and this phase after V172. "ok start" (2026-10-31) began it. This note follows
`reference/research-protocol.md` and `reference/reuse-first-integration.md`: what was read and run on 2026-10-31,
at what level, what it shows, the design it leads to, and the questions for the owner.

## 1. What the app has (P, its code)

- **The climate data** (`src/js/engine/site-analysis/climate-data.js`, V159): CLIMATEGET asks Open-Meteo's ERA5
  archive for ten years of daily values and the last full year of hours (temperature, humidity, wind speed and
  direction at 10 m, `timezone=auto`). The hours are reduced as they arrive (a rounded temperature a hour for the
  heat map, wind roses, monthly humidity, a psychrometric density, a comfort share) and the raw series are not kept.
  So no hourly series exists in a project for Ladybug to read: a Ladybug run needs the hours again, from Open-Meteo
  or from a weather file.
- **The Climate and risk board** (`climate-board.js`): ten figures. Fig. 4 is the app's own wind rose (16 sectors,
  the registry's calm and speed bands, winter and summer roses), Fig. 8 its own psychrometric chart (hours as
  density, a box-shaped comfort zone of 20 to 27 C and 20 to 80% humidity, `app.climate`, an assumption of lv A),
  and the KPI "Outdoor comfort" is the share of hours in that box.
- **The registry** (V167): `app.climate` holds that box, the degree-day base and the wind bands; no comfort
  standard (ASHRAE 55, ISO 7730, UTCI) is recorded yet.
- **The analysis workspace** (V171b, V171c): Analyze's rows by category; Climate holds the sun, shadows, wind,
  sun hours and solar rows; a row picked shows its panel on the right, as V172's tools do.

## 2. The runtime: Pyodide

**The distribution (P, the npm registry and the packages themselves, 2026-10-31).** Pyodide's npm package is its
core runtime ("the same set of files that are installed if you use npm install pyodide": Pyodide's own
`docs/usage/downloading-and-deploying.md` at tag 0.29.5). Two lines are current:

| Version | Released | Python | Core files (bytes) | Workers |
|---|---|---|---|---|
| 314.0.7 (`latest`) | 2026-09-14 | 3.14 | `pyodide.asm.mjs` 1,250,344; `pyodide.asm.wasm` 9,598,218; `python_stdlib.zip` 2,545,637 | its loader throws "Classic web workers are not supported" and imports its core with `import()` (read in its `pyodide.js`) |
| 0.29.5 (`stable-0.29`) | 2026-09-16 | 3.13.2 | `pyodide.asm.js` 1,074,322; `pyodide.asm.wasm` 8,647,684; `python_stdlib.zip` 2,424,003 | a classic worker loads it with `importScripts` (its loader falls back to `import()` only on a TypeError) |

The package tarballs' SHA-256: 0.29.5 `6749b10e...e4aff181`, 314.0.7 `66b7949e...685ffaa0`. Both MPL-2.0.

**The choice this leads to:** 0.29.5. The app's code is ES5 (`CLAUDE_INSTRUCTIONS.md`); a classic worker driven by
ES5 code can load 0.29.5, while 314.x needs a module worker and `import`, which ES5 cannot write. 0.29.5 is still
maintained (released two days after 314.0.7). When the 0.29 line ends, moving to 314 needs the owner's exception for
an ES module worker; recorded, not needed now.

**Installing the wheels without micropip (P, `pyodide.d.ts` 0.29.5):** `unpackArchive(buffer, 'wheel',
{extractDir})` is documented, so the worker fetches each pinned wheel, checks its SHA-256 itself
(`crypto.subtle`) and unpacks it into `site-packages`; micropip, dependency resolution and PyPI are never involved.
`loadPyodide({indexURL})` takes the runtime's folder.

**Hosting (P, Pyodide's docs; tested):** "Any service that hosts static files and that correctly sets the WASM MIME
type and CORS headers will work. For instance, you can use GitHub Pages." The live Pages site answers a GET with
`Access-Control-Allow-Origin: *`, `cache-control: max-age=600`, and gzip (the 3.7 MB one-file build arrives as 1.15
MB); a preflight OPTIONS is refused (405), which a plain GET does not need. Whether Pages compresses `.wasm` is not
yet known (U until the runtime is deployed): 6.2 MB over the wire if it does, about 9.8 MB if not.

**Browsers (P, Pyodide's `docs/usage/index.md` at 0.29.5):** tested against Chrome 112, Firefox 112 and Safari 16.4
(all March to April 2023). Only Chromium runs here, so Safari, iOS and Firefox are not tried (U, said in the app).

**The experiment (P, run 2026-10-31 in Chromium 1243 with Playwright 1.63.0):** `scratchpad/poc2/` (not committed):
a page from `file://` makes a classic worker from a Blob; the worker `importScripts` 0.29.5's `pyodide.js`, calls
`loadPyodide`, fetches the four wheels, checks their hashes, unpacks them, and runs Ladybug's EPW reader, UTCI, PMV,
psychrometric chart with its PMV polygons and two strategies, wind rose and design days on Philadelphia's TMYx EPW.
Three ways, the same results each time:

| Way | Pyodide ready | Wheels checked and in | Analyses | Total | Wasm heap |
|---|---|---|---|---|---|
| `file://` page, runtime on another origin with CORS (the one-file build reading the Pages site) | 3.7 s | 3.9 s | 5.4 s | 9.3 s | 36.3 MB |
| page and runtime on one origin (the multi-file Pages app) | 3.4 s | 3.6 s | 5.1 s | 8.7 s | 36.3 MB |
| `file://` page, the Pages address routed by Playwright to local files (a suite) | 4.9 s | 5.0 s | 5.0 s | 10.1 s | 36.3 MB |

Only five core files were asked for (`pyodide.js`, `pyodide-lock.json`, `python_stdlib.zip`, `pyodide.asm.wasm`,
`pyodide.asm.js`): Ladybug's modules need nothing Pyodide unvendors. A Blob worker from a `file://` page is a
secure context with `crypto.subtle`. Playwright's `context.route` serves a worker's `importScripts` and `fetch`, so a
suite can serve the runtime from local files at the Pages address.

## 3. The wheels (P, PyPI's JSON and the files, SHA-256 checked 2026-10-31)

| Wheel | Bytes | SHA-256 | Licence | Requires |
|---|---|---|---|---|
| `ladybug_geometry-1.35.7-py3-none-any.whl` (2026-10-28) | 205,631 | `fd73bddb...5c89139` | AGPL-3.0 | none |
| `ladybug_core-0.44.63-py3-none-any.whl` (2026-10-28) | 275,212 | `21d67827...7905e9556` | AGPL-3.0 | ladybug-geometry 1.35.7, click 8.3.3 |
| `ladybug_comfort-0.19.13-py3-none-any.whl` (2026-10-28) | 177,721 | `227e246d...abb62e8` | AGPL-3.0 | ladybug-core 0.44.63 (numpy only for its maps) |
| `click-8.3.3-py3-none-any.whl` (2026-04-22) | 110,502 | `a2bf429b...14305613` | BSD-3-Clause | none on Linux |

Newer than the experiment of 2026-10-26 (0.44.62, 0.19.12, 1.35.6). The full hashes are in the runtime's lock file
when built. Runtime and wheels together: 13,055,699 bytes.

## 4. Ladybug's code for this phase (P, read in the wheels above: the code that runs)

- **EPW** (`ladybug/epw.py`): `EPW.from_file_string(text)` is "intended for workflows where ladybug does not have
  access to a file system (eg. within a web browser)". `EPW.from_missing_values(is_leap_year)` makes an empty year
  whose collections are filled by `.values =`, its docstring listing what a usable file needs (dry bulb, dew point,
  humidity, station pressure, direct normal and diffuse radiation, wind direction and speed, total sky cover, opaque
  sky cover or horizontal infrared). The first record of the year is Ladybug's 00:00 (the EPW's hour 1, 00:01 to
  01:00) for the fields over an hour (station pressure and the three radiations); for the fields at an instant
  (temperature, dew point, humidity, wind, sky cover, the sky's infrared: their data types' `point_in_time`) it
  moves the file's last row to the front, "if the first value is at 1 AM, move last item to start position", so
  their 00:00 is the value at 00:00. (Corrected 2026-11-01: the suite's hour-by-hour check found the first reading
  incomplete; see section 14.)
- **UTCI** (`ladybug_comfort/utci.py`, `collection/utci.py`, `parameter/utci.py`): "a Python version of the original
  UTCI_approx application written in Fortran, Version a 0.002, October 2009". Wind is clamped to 0.5 to 17 m/s at 10
  m; air temperature and the radiant difference are not checked. The collection takes air temperature, humidity,
  mean radiant temperature (air temperature when none) and wind (0.5 m/s when none). `original_utci_category` is the
  official ten-band scale; the default eleven-point scale adds a "slight heat stress" band of Ladybug's own (26 to
  28 C), so the app uses the official one. Cold bands are `utci < threshold`, heat bands `utci > threshold`: 26.0
  and 9.0 exactly are "no thermal stress".
- **UTCI in the sun** (`collection/solarcal.py`, `OutdoorSolarCal`): "the SolarCal model of ASHRAE-55", from the
  location, direct normal and diffuse horizontal irradiance, horizontal infrared and the surface temperature (dry
  bulb when unknown); by default an open area (body fully exposed, the whole sky in view) and ground reflectance
  0.25. Horizontal infrared comes from the EPW, or from `ladybug.skymodel.calc_horizontal_infrared(sky cover in
  tenths, dry bulb, dew point)` (EnergyPlus's method, after Walton 1983 and Clark and Allen 1978).
- **PMV** (`pmv.py`, `collection/pmv.py`, `parameter/pmv.py`): Fanger's model, with SET above the still-air
  threshold. `PMVParameter`: PPD at most 10% ("most buildings in the ASHRAE-55 and EN-15251 standards"), no humidity
  limits, still air 0.1 m/s.
- **The psychrometric chart** (`ladybug/psychchart.py`): from temperature and humidity collections and the mean
  station pressure; its lines (saturation, temperature, humidity, humidity ratio, enthalpy, wet bulb) and its
  coloured mesh of hours are 2D geometry in chart units (x = temperature, y = humidity ratio x 1500), drawn here by
  the app.
- **The PMV polygon and passive strategies** (`ladybug_comfort/chart/polygonpmv.py`): defaults 1.1 met, 0.7 clo, 0.1
  m/s, MRT equal to air temperature; one polygon per set of conditions, or merged; evaporative cooling, fans, mass
  and night ventilation, internal heat and passive solar polygons, each evaluated hour by hour. How they are put
  together is in Ladybug's Grasshopper component `LB PMV Polygon.py` (read as text at ladybug-grasshopper's master,
  AGPL-3.0) and its parameters in `LB Passive Strategy Parameters.py`: mass and night ventilation up to 12 C above
  the comfort polygon's warmest, as long as the outdoor air 8 hours earlier was 3 C below it; fans at 1.0 m/s
  ("values above 1 m/s tend to blow papers off desks"); a balance temperature of 12.8 C for internal heat ("fairly
  low"); 50 W/m2 of solar flux to raise the space 1 C for passive solar; the total is the hours inside any
  polygon. Passive solar needs the irradiance on the solar windows (global horizontal "assumes that all windows
  are skylights"); `Wea.directional_irradiance` gives it for a south-facing window.
- **The wind rose** (`ladybug/windrose.py`): 16 sectors centred on the compass points (north 348.75 to 11.25,
  lower edge in, upper out); calm is a speed of exactly 0 (EPW files report calm as 0); the prevailing direction is
  the fullest sector.
- **Design days** (`epw.py`, `ddy.py`, `designday.py`): from an EPW's DESIGN CONDITIONS line (ASHRAE's values), else
  `approximate_design_day`, a percentile of the one year, which Ladybug says "tend to be less accurate ... usually
  derived from multiple years", citing ASHRAE HOF 2013 chapter 14. A `.ddy` file is read by `DDY.from_ddy_file`.

**Found (P, run on Philadelphia's TMYx 2009-2023):** the EPW's DESIGN CONDITIONS line cites the "2025 ASHRAE
Handbook -- Fundamentals - Chapter 14" and puts `Heating` in field 3; Ladybug 0.44.63 reads `Heating` from field 4
for every edition but 2009, so it reads nothing, and its "best available" design days fall back to the one-year
approximation without a word: heating 99.6% -7.2 C and cooling 0.4% 33.9 C, where ASHRAE's are -9.6 C and 34.1 C.
The `.ddy` in the same ZIP is read correctly by Ladybug's own `DDY` (heating 99.6% -9.6 C; cooling 0.4% 34.1 C dry
bulb with a coincident wet bulb of 23.8 C). So the app opens the station's ZIP (EPW and DDY) and takes the design
days from the DDY, with Ladybug's code unchanged.

## 5. The standards (each value's level)

| Topic | Edition | What is used | Read | Level |
|---|---|---|---|---|
| UTCI | Bröde et al., UTCI_a002 (October 2009), COST Action 730; utci.org | the polynomial's validity: air -50 to +50 C, MRT 30 C below to 70 C above air, wind at 10 m 0.5 to 17 m/s, vapour pressure under 50 hPa; the reference condition (walking 4 km/h, MRT = air, 0.5 m/s at 10 m, 50% humidity) | `ReadMe_UTCI_a002.txt` and `UTCI_a002.f90` (the official program, read as text, the `.exe` never run); the poster "Calculating UTCI Equivalent Temperatures" (2009) | P |
| UTCI's scale | the same; Blazejczyk et al. 2013 | ten bands at -40, -27, -13, 0, 9, 26, 32, 38 and 46 C | the poster's scale graphic and Ladybug's `UTCIParameter`; the 2013 paper's repository answers scripts with a browser check | P (S for the paper) |
| PMV, PPD | ISO 7730:2005 | Fanger's model; 12 of the standard's test cases | the MIT validation tables of Tartarini (`validation-data-comfort-models` v1.1.0), which pythermalcomfort, CBE's tool and R's comf test against | S (the standard is sold) |
| PMV comfort | ASHRAE 55-2023 | PMV within +/-0.5 (PPD at most 10%), still air 0.1 m/s | pythermalcomfort 4.8.0 ("the only option available is 55-2023"); Ladybug's `PMVParameter`; ashrae.org refuses scripts (403) | S |
| SolarCal | ASHRAE 55 (its appendix) | MRT in the sun | Ladybug's `OutdoorSolarCal` | S |
| Design conditions | ASHRAE Handbook -- Fundamentals 2025, chapter 14 | heating 99.6% and 99%; cooling 0.4%, 1% and 2% with the coincident wet bulb | the EPW's header and the DDY, which carry the station's values; Ladybug's docstrings | P for the values, S for their definitions (the Handbook is sold) |
| EPW | EnergyPlus 24.1, Auxiliary Programs, the EPW data dictionary | hour 1 is 00:01 to 01:00; temperature, humidity, pressure and wind "at the time indicated"; radiation over the preceding hour; missing codes 99.9, 999, 999999, 9999; calm is direction 0 and speed 0 | Big Ladder's copy of NREL's documentation | P |

**Checked against the published values (P, run natively on the same wheels):** Ladybug's `fanger_pmv` matches all 12
ISO 7730:2005 cases and one more (PMV within 0.1, PPD within 1); its UTCI matches all 8 in-range reference values
within 0.1 C. Outside UTCI's validity it still returns a number (51 C air: 61.7; 0 m/s wind is taken as 0.5) where
pythermalcomfort returns none: the app says when an hour lies outside the range.

## 6. Practice

- **CBE Clima** (Betti, Tartarini, Nguyen and Schiavon, Building Simulation 2023; its documentation and MIT code,
  P): a web tool for architects reading EPW files. Outdoor comfort is UTCI in four conditions: sun and wind, shade
  and wind, sun and still air, shade and still air ("the windless situation sets the value at 0.5 m/s, the minimum
  value allowed by the UTCI model"; shade puts MRT at the dry bulb). UTCI and its stress categories as year-long heat
  maps; the psychrometric chart with the hours' frequency; wind roses and wind heat maps. "The designer can
  influence two factors out of the four ... exposure to the sun and ... to the wind."
- **Ladybug Tools' primer** (docs.ladybug.tools, P): UTCI Comfort with Outdoor Solar MRT for the sun; PMV Polygon with
  passive strategies and the hours inside each; Psychrometric Chart; Wind Rose; Import DDY.

## 7. Data (tested)

| Source | Test | Result | Use |
|---|---|---|---|
| climate.onebuilding.org (EPW, DDY, STAT in a ZIP) | 2026-10-26, Origin and preflight | 200, no `Access-Control-Allow-Origin` | Named, not proxied: the user downloads the station's ZIP and opens it in the app |
| Open-Meteo archive (ERA5) | 2026-10-31 | `timezone=Etc/GMT+5` returns the whole series in standard time (UTC-5), as an EPW is; `America/New_York` puts the request's offset (UTC-4) on every hour (V171d). The third request answered "Daily API request limit exceeded" | The year's hours when no file is open, asked for in the site's standard time |
| GitHub Pages | 2026-10-31 | `Access-Control-Allow-Origin: *`, gzip | Serves the runtime to the app and to the one-file copy |
| npm registry, PyPI | 2026-10-31 | the files and their SHA-256 | Where the pinned bytes come from |

## 8. Edges, for the tests

- **Leap years:** Open-Meteo's 2024 has 8,784 hours; `AnalysisPeriod(is_leap_year=True)` takes them; an EPW is
  usually 8,760.
- **Hours:** for the fields over an hour (pressure, radiation) Ladybug's index 0 is the EPW's hour 1 (00:01 to 01:00);
  for the fields at an instant its index 0 is the value at 00:00 (section 4). Open-Meteo's radiation is the mean of
  the preceding hour, its temperature the value at the hour. So an Open-Meteo year gives each instant's variable its
  own hour, and pressure and radiation the hour after. An hour's alignment does not change a year's shares; it does
  move each hour on the heat map and the sun against the temperature in UTCI's sun case.
- **Time zones:** `Etc/GMT` names are whole hours with the sign reversed (`Etc/GMT+5` is UTC-5). A half-hour zone
  (India, Newfoundland, central Australia) has none: the hours are asked for in UTC and moved by the whole hours of
  the offset, and the remaining half hour is said. Not yet tried against the service (its daily limit), U.
- **Missing values:** the EPW's codes; Open-Meteo's nulls. Ladybug fills neither: hours missing are reported and
  left out.
- **UTCI:** outside its validity it is extrapolated by Ladybug; wind under 0.5 m/s is taken as 0.5. The bands' edges
  as in section 4.
- **Calm:** Ladybug counts a speed of exactly 0; Open-Meteo's model winds are rarely 0, so its calm share is near 0
  where a station's is not. The app's own rose uses the registry's threshold (V159). Said on the rose.
- **Design days:** the 2025 header layout (section 4); one year from Open-Meteo gives an approximation, said with
  Ladybug's own caveat.

## 9. The design proposed

- **The runtime, served with the site:** `runtime/pyodide/0.29.5/` (the five core files) and `runtime/wheels/` (the
  four wheels, named by version, never overwritten), pinned by a lock file of URLs, sizes and SHA-256. The
  multi-file app loads them from its own origin; the one-file `canvas_v10.html` from the Pages address, so it
  needs the network for these analyses only, as decided.
- **One worker, ES5:** `src/js/engine/ladybug/`: the worker made from a Blob on first use (the app opens as fast as
  now), `importScripts` and `loadPyodide`, each wheel's hash checked before it is unpacked, then one Python
  function per analysis; a failure is warned and toasted with its cause (no network, a hash that does not match, a
  browser without WebAssembly). The zero-dependency contract gets its written exception: these analyses, on demand.
- **Narrow adapters, ours** (a small Python module run in the worker, and the ES5 around it): an EPW, or the
  station's ZIP with its DDY, opened from a file; or Open-Meteo's year asked for in the site's standard time with
  the variables the analyses need (temperature, dew point, humidity, surface pressure, wind speed and direction,
  direct normal and diffuse radiation, cloud cover). The site's place becomes Ladybug's `Location`. Results come
  back as numbers and 2D geometry, drawn in the board's style; Ladybug and its version are named on every figure.
- **The analyses:** UTCI over the year in Clima's four conditions, with the official scale; the psychrometric chart
  with ASHRAE 55's PMV comfort and Ladybug's five passive strategies, each with its share of hours; the wind rose;
  the design days (heating 99.6%, cooling 0.4%, with their 24-hour profiles).
- **Kept with the project:** the results and what they came from (the file's station and name, or the Open-Meteo
  year and the date asked), not the hours (a year of eight variables would add about half a megabyte); a run again
  after a reload opens the file or asks Open-Meteo again.
- **The registry:** three records with their editions: UTCI's scale (Bröde et al. 2009), ASHRAE 55-2023's PMV
  limits and the strategy parameters, ASHRAE Fundamentals 2025 chapter 14's percentiles.
- **The tests:** the suite serves the runtime from local files at the Pages address (section 2). Its reference,
  apart from the app, in Python: the EPW and DDY read as text, UTCI by the official polynomial transcribed from
  UTCI_a002.f90, PMV by Fanger's method checked against ISO 7730's cases, the wind sectors and calm counted, the
  design days read from the DDY; and the same wheels run natively, so the browser's numbers must equal CPython's.

## 10. The owner's decisions

Asked together on 2026-10-31, and answered the same day:

1. **How the runtime reaches the site.** Asked: committed to the repository, or a lock file with the files'
   SHA-256 and the files fetched from npm and PyPI when the site is built and the suites run. The owner: "which one
   is more reliable and smooth?" Committing is: nothing outside GitHub is needed to deploy or to test, and what
   Pages serves is byte for byte what the suites ran; for the person using the app the two are the same. So the
   runtime is committed, the deliberate vendoring `reuse-first-integration.md` asks the owner for: exactly the nine
   files under `runtime/`, each pinned by its SHA-256 in a manifest, their licences in `THIRD_PARTY_NOTICES.md`.
2. **Where the results show.** The owner: "these boards should be interactive and each analysis can be add in. not
   a static board. like a generate table or chart in excel ya know? ... in our current 3 boards they are really good
   but those components in the board are not editable and can be rearrange drag or whatever." So the boards become
   editable: each analysis a component added from a list, dragged into place, resized, its options set as a chart's
   are in Excel, removed; kept with the project and undone. Researched in section 13 before it is designed.
3. **UTCI:** Clima's four conditions (sun or shade, wind or still air).
4. **The psychrometric chart:** two clothing levels merged (0.5 and 1.0 clo at 1.1 met) with Ladybug's five
   passive strategies and its default parameters.

## 13. Editable boards (the owner's answer 2, researched 2026-10-31)

**Practice (P, each product's own documentation):**
- **ArcGIS Dashboards** ("Dashboard layouts", doc.arcgis.com): a dashboard is elements filling the screen, laid out
  as rows and columns in a layout tree; an element is moved by its drag handle onto an indicator ("Dock as a
  column"), resized by dragging its border (the share of the row is shown), stacked onto another as tabs, or grouped;
  "Distribute width evenly"; a separate mobile view.
- **Grafana** ("Create dashboards", grafana.com): an Edit mode; "Add new element" adds a panel; two layouts, Custom
  (a panel dragged by its title and resized by its lower-right corner) and Auto grid ("panels resize and fit
  automatically", with a minimum column width, up to 10 columns and a row height); each panel's Settings, Edit
  visualization, Copy, Duplicate, Delete; panels grouped into rows or tabs; Save.
- **Power BI** ("Use gridlines and snap-to-grid", learn.microsoft.com): a free canvas, visuals snapped to a grid,
  smart guides, Align and Distribute; each visual's axes and gridlines set in its Format pane.
- **Excel** ("Create a chart from start to finish", support.microsoft.com): data selected, Insert, Recommended Charts
  with a preview, or All Charts; then chart elements (title, legend, axes, gridlines) shown or hidden, quick layouts
  and styles.

**The app (P, its code):** the three boards (`climate-board.js`, `zoning-envelope.js`, `access-board.js`) build their
figures with one card function, `bimClbCard`, on a 12-column grid (`boards.css`: spans of 4, 5, 6, 7 and 12; every
card half width on a medium screen, full on a phone; kept whole when printed). Since V162 a board is a page of the
set (`sheets/boards.js`): `A3D.pres` keeps one board of each kind and the set's order, for the Presentation panel,
Present and Print set. Nothing about a board's figures is kept: they are written fresh each time.

**The design proposed:** a board keeps its figures as a list in its record (`A3D.pres`): each figure's kind, its
width (a third, a half, two thirds or full) and its options; a board without a list shows today's figures in
today's order, so every project opens as it does now. An **Edit** button on the board's bar: each figure gets a
handle to drag it (mouse, pen or finger), its width, its options, Duplicate and Remove; **Add a figure** opens a
catalogue of every analysis that has data, grouped by category, each with a preview, as Excel's Recommended Charts;
Reset gives the default back; each change is one undo step and is kept with the project; the keyboard moves a
focused figure. A figure's options are those that make sense for it, as a chart's are in Excel: what it shows, how
(chart or table), the period, a condition (UTCI's four), its title. On a phone the board is one column and a figure
moves by its handle or by Up and Down. Present and Print set show the board as arranged.

**The questions it left, answered 2026-10-31:**
- **The layout.** The owner: "it should act based on the config i already have (snap, grid, ortho). do not invent new
  stuff". The app's Snaps panel (`ui/shortcuts.js`, `A3D_SNAP`) holds Point snap, Grid snap, Ortho and the grid
  size, toggled by F8, F9 and the status pill, and applied today to drawing, the gizmo and push-pull. So a figure on
  a board in Edit moves and is sized freely, as a viewport on a sheet is (`sheets/viewports.js`: dragged by its
  body, sized by its corner), and those same settings govern it: Grid snap snaps its edges to the board's own grid
  (its 12 columns across, `boards.css`, and the same step down), Ortho keeps a drag straight across or straight
  down, Point snap catches its edges on other figures' edges within the same 12 px (`pxThreshold`). No new setting.
  On a phone the board flows into one column in reading order, as boards do today.
- **The catalogue:** any analysis on any board, and boards of one's own; the three boards are the first.
- **When:** within V172b; Ladybug's figures are the first made this way, and the three boards become editable.

## 11. Sources (read 2026-10-31 unless said)

| Source | URL | What was read | Level |
|---|---|---|---|
| Pyodide 0.29.5 and 314.0.7 | registry.npmjs.org/pyodide | the tarballs: loaders, `pyodide.d.ts`, `pyodide-lock.json`, sizes, hashes | P |
| Pyodide docs at tag 0.29.5 | raw.githubusercontent.com/pyodide/pyodide/0.29.5/docs/ | `usage/webworker.md`, `usage/downloading-and-deploying.md`, `usage/index.md`, `project/changelog.md` | P |
| The four wheels | pypi.org, files.pythonhosted.org | the JSON and the files; the modules of section 4 read as text | P |
| Ladybug's Grasshopper components | raw.githubusercontent.com/ladybug-tools/ladybug-grasshopper/master/ | `LB PMV Polygon.py`, `LB Outdoor Solar MRT.py`, `LB UTCI Comfort.py`, `LB Wind Rose.py`, `LB Psychrometric Chart.py`, `LB Passive Strategy Parameters.py`; LICENSE (AGPL-3.0) | P |
| Ladybug Tools primer | docs.ladybug.tools/ladybug-primer | PMV Polygon, UTCI Comfort, Outdoor Solar MRT, Psychrometric Chart, Wind Rose, Import DDY | P |
| UTCI | www.utci.org | `UTCI Program Code.zip` (ReadMe, Fortran), `utci_poster.pdf` | P |
| Blazejczyk et al. 2013, Geographia Polonica 86(1) | rcin.org.pl/igipz/publication/46784 | refused: a "verifying browser" page | none |
| Validation tables | raw.githubusercontent.com/FedericoTartarini/validation-data-comfort-models/v1.1.0/ | `ts_pmv_ppd.json`, `ts_utci.json`, README, LICENSE (MIT) | S for ISO 7730's values |
| pythermalcomfort 4.8.0 | pypi.org | the wheel read as text: `models/pmv_ppd_ashrae.py`, `models/utci.py`, `tests/` (MIT) | S |
| ASHRAE Standard 55 | ashrae.org | refused (403) | none |
| CBE Clima | center-for-the-built-environment.gitbook.io/clima; github CenterForTheBuiltEnvironment/clima | the documentation's outdoor comfort, UTCI, psychrometric and wind pages; README, LICENSE (MIT) | P |
| EPW data dictionary | bigladdersoftware.com/epx/docs/24-1/auxiliary-programs/energyplus-weather-file-epw-data-dictionary.html | the field definitions | P |
| Philadelphia Intl AP TMYx 2009-2023 | climate.onebuilding.org (2026-10-26) | the EPW and DDY, for the experiment; never committed | P |
| Open-Meteo archive | archive-api.open-meteo.com | three requests (time zones; the daily limit) | P |
| GitHub Pages | bradleypham1906.github.io/BIM-Personal/ | response headers | P |
| ArcGIS Dashboards | doc.arcgis.com/en/dashboards/latest/get-started/dashboard-layout.htm | the whole page (layouts, move, resize, stack, group) | P |
| Grafana | grafana.com/docs/grafana/latest/dashboards/build-dashboards/create-dashboard/ | create, layouts (custom, auto grid), move, resize, panel actions, groupings | P |
| Power BI | learn.microsoft.com/en-us/power-bi/create-reports/desktop-gridlines-snap-to-grid | gridlines, snap to grid, smart guides, align | P |
| Excel | support.microsoft.com/en-us/office/create-a-chart-from-start-to-finish-0baf399e-dd61-4e18-8a73-b3fd5d5680c2 | creating a chart, recommended charts, chart elements | P |

## 12. Still open

- Safari, iOS and Firefox: not run (Chromium only here).
- Whether Pages compresses `.wasm`: known once the runtime is deployed.
- Half-hour time zones against Open-Meteo: to try when its daily limit allows.
- Ladybug's reading of the 2025 header: worked around by the DDY; an issue upstream is the owner's to open or not.
- Sun-hours and radiation on the model: V172c.

## 14. As built (2026-10-31 to 2026-11-01)

**The engine** (patches `Phase/patch_v172b_a.py` to `_e.py`; the files in `src/js/engine/ladybug/`, `src/py/bim_ladybug.py`
embedded by `tools/embed_py.py`): the runtime committed under `runtime/` and pinned by `runtime/MANIFEST.json`
(`tools/check_runtime.py`, run by the Pages workflow and by `tools/build_site.py`); one classic worker made from a Blob,
loading Pyodide 0.29.5 and checking each wheel's SHA-256 before unpacking it; the adapter; the two sources (a file, or
Open-Meteo's year); the four analyses, kept with the weather they read, the versions that made them and the standards
they used.

**The registry:** four topics in Climate -- `utci` (UTCI_a002's scale and range, P), `ashrae.55` (PPD 10%, still air
0.1 m/s, S), `app.comfort` (Ladybug's defaults: 0.5 and 1.0 clo at 1.1 met, the strategy parameters, SolarCal's
exposure, A), `ashrae.dd` (the design conditions' percentiles, S). `bimLbParams` passes them to the adapter; the adapter
checks the strategy parameters against the ranges Ladybug's own component enforces, a value outside going back to the
default, said. A result keeps `bimStdStamp` of what it used; a change marks only the results that used it.

**Analyze:** Climate's rows (`ladybug/panel.js`): Weather for Ladybug (open a file, get a year of hours, Run all four),
then UTCI, the psychrometric chart, the wind rose and the design days, each with its numbers, the standards it used,
Run, Show on the board and Add to a board (any board in the set, or a new one).

**The boards made editable** (section 13; `sheets/board-figures.js`, `sheets/board-edit.js`,
`css/site-analysis/boards-arranged.css`): every card of the three boards and Ladybug's is named (`'@clim.temp'` among
its classes); a board is read for its cards by drawing it once (`A3D_FIGCAP`), so each figure is drawn by its own
board's code wherever it is placed. A list of figures is kept in the board's record (`figs`, and `off` for its own
figures taken off); a board without one is drawn exactly as before (the suite compares the kept build's HTML). The list
is laid out at the board's full width, 1408 px, its 12 columns and rows of the same step, and zoomed to a narrower main
view (`zoom`), so the arrangement is the same on any screen and on paper; in bands of figures whose rows overlap, which
print without being split; on a phone its figures flow in reading order. Edit measures a board without a list where
its grid puts the figures (within 0.1 px) and keeps nothing until the first change. The drawing's own Snap, Grid and
Ortho govern a drag, in that order, as they govern a point being drawn.

**Found while building:**
- Open-Meteo's instants were an hour late: the adapter gave every variable the hour after, as an EPW's hour 1 is read
  for the fields over an hour; Ladybug moves a file's last row to the front for the fields at an instant (section 4,
  corrected). The suite's hour-by-hour check against the official UTCI polynomial found it (patch e).
- The catalogue's previews sat outside a board's element, so the board's chart rules (`.a3d-clb .hit`, its ticks and
  grids) did not apply and the charts' hit areas painted black: Edit's dialogs now carry the board's own class and
  are excluded from `bimClbEl`.
- A file:// page is read by its name's extension: the kept build (`.bak_phase172b_pre`) is opened from a copy named
  `.html` for the suite's comparison.

**Sources added 2026-11-01:** utci.org's `UTCI Program Code.zip` again (SHA-256
`83ea34dc2428093c8b0f4e299bfb0a24752ff49ec1e11741927a75dafae283f1`): its polynomial's 210 terms read out of
`UTCI_a002.f90` by a script into `tests/ladybug_reference.py` (coefficients and powers only), P; Tartarini's validation
tables v1.1.0 (`ts_pmv_ppd.json` SHA-256 `182f8f8c6c6f9798424e6a95a1373b37bce70367e56aa24fb46215aff84a1025`, `ts_utci.json`
`671094bb22fb69b4be71f060719c6ac1a40d25ff2f40dd09db4015ca73dac03d`, MIT): ISO 7730's 12 cases and UTCI's 8 in-range values,
S. The suite's weather is made up (`tests/ladybug_fixture.py`): no station's file is committed.
