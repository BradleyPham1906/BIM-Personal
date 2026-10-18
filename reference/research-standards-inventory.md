# V167's migration list: the app's constants, classified (2026-10-18)

Read from the build (`canvas_v10.html` at V166b) while V166b's checks ran: every `BIM_` constant
(267), with the comment beside it. Line numbers are the V166b build's and will move; search by
name. "Cited" is what the code's comment or its phase's note names; "level" is that phase's note's,
not re-read here. Nothing below has been changed in the code.

## The classes

| Class | What | In V167 |
|---|---|---|
| **S** | A standard's value: a code, a method, a guideline, with an edition | A registry record, dated, cited, by place |
| **H** | A standard's value with no citation in the code | A record marked U until its source is read |
| **C** | A definition or a measured constant that no jurisdiction changes | Stays in code, its source cited in a comment |
| **A** | The app's assumption where data is missing | A registry record published by the app ("assumption"), overridable with a reason |
| **M** | A method's own parameter (a grid, a budget, a radius) | Stays with its method version |
| **E** | A data source's address | Stays in the data catalogue (V134), not a standard |
| **D** | Display: colours, labels, icons, keys, panel sizes | Stays in code |
| **N** | A numerical tolerance | Stays in code |

## S: standards, to become records

| Constant | Line | Value | Standard (as cited) | Phase |
|---|---|---|---|---|
| `BIM_OCC_LOADS` | 12891 | occupant load factors by use, gross or net | IBC Table 1004.5 (2018 and 2021) | V105 |
| `BIM_COMBOS` | 42638 | load combinations and factors | ASCE 7 section 2.3.1 | V125 |
| `BIM_DG_ROADS` (u, r) | 20272 | typical daily traffic by road class, urban and rural | FHWA's functional classification | V164 |
| `BIM_DG_CRTN_MAX` | 20282 | 300 m | CRTN (1988): the method's range | V164 |
| `BIM_MV_XTAB` | 20473 | 4 x 3 table of stress levels | Furth, Mekuria and Nixon (2016), unsignalized crossing without a refuge | V166 |
| `BIM_MV_PTAL_WALK` | 20480 | 8 min to a bus, 12 to rail | TfL's PTAL | V166 |
| `BIM_MV_PTAL_K` | 20480 | 2 min (bus), 0.75 (rail) | TfL's PTAL: reliability allowance | V166 |
| `BIM_MV_PTAL` | 20481 | bands 1a to 6b by index | TfL's PTAL | V166 |
| `BIM_MV_GUIDE` | 20477 | 400 m to green space, 800 m to shops and a primary school | "the design guides" (V166's note) | V166 |
| `BIM_ACC_SPEED` | 24530 | 80 m a minute (4.8 km/h) | TfL's PTAL walking speed | V161 |
| `BIM_ACC_LEED` | 23271 | 90, 140, 300, 400 intersections a square mile | LEED ND's connectivity thresholds | V161 |
| `BIM_CLIM_WHO24`, `BIM_CLIM_WHO_YEAR` | 22261 | 15 and 5 micrograms a cubic metre (PM2.5) | WHO's air quality guidelines (2021) | V159 |
| `BIM_LAND_ZONES` | 21037 | FEMA zone groups and their order | FEMA's National Flood Hazard Layer zones | V165 |
| `BIM_LAND_SLOPE` | 21029 | five slope classes, 0 to 25% and over | V165's note (planning practice) | V165 |
| `BIM_KOPPEN` | 22267 | the Koppen-Geiger zones' names | Koppen-Geiger classification | V159 |
| the 2012 stress criteria | in `bimMvStress` | thresholds inside the method | Mekuria, Furth and Nixon (2012), MTI 11-19 | V166: a **method version**, not a record |
| the section library | V126 | AISC W and C shapes | AISC's shapes database | V126: to locate in code; a record per edition |

## H: a standard with no citation

| Constant | Line | Value | Reading | Status |
|---|---|---|---|---|
| `BIM_SLOPE_BANDS` | 8251 | 0, 2, 5, 8.33, 15, 25, 50% | 8.33% is 1:12, logged so in V144; it reads as the US accessibility ramp limit, and 2% as the cross-slope limit | U: source not read (ada.gov and access-board.gov refused here) |

## A: the app's assumptions, to become overridable records

| Constant | Line | Value | Used for |
|---|---|---|---|
| `BIM_DG_ROADS` (v, p, l) | 20272 | speed, heavy vehicles %, lanes by class | noise, where OpenStreetMap does not say |
| `BIM_CTX_LEVEL_H`, `BIM_CTX_DEFAULT_H` | 29088 | 3 m a storey; 6 m a building | context heights where OpenStreetMap has none |
| `BIM_CTX_TREE_H`, `BIM_CTX_TOWER_H`, `BIM_CTX_LINE_H`, `BIM_CTX_DECK*`, `BIM_CTX_PIER` | 29316 | 8 m trees, 25 m towers, 20 m lines, bridge decks | context objects |
| `BIM_ROAD_W` | 29311 | road widths by class | context roads |
| `BIM_ROOF_ANGLE`, `BIM_ROOF_KNEE`, `BIM_ROOF_HALFHIP`, `BIM_ROOF_MINWALL` | 29883 | 30 degrees and the shapes' proportions | LOD2 roofs from OpenStreetMap |
| `BIM_USAGE_DEFAULTS` | 41765 | five usages' ratios and storey heights | already editable per project (V131) |
| `BIM_CLIM_BASE` | 22259 | 18 degrees C | degree days |
| `BIM_CLIM_CALM`, `BIM_CLIM_WIND_BINS` | 22259 | 0.5 m/s; the rose's speed bins | the wind rose |
| `BIM_CLIM_COMFORT` | 22261 | 20 to 27 degrees C, 20 to 80% humidity | the comfort chart |
| `BIM_SURVEY_TOL` | 9597 | survey check tolerances | V138's survey check |

## M, E, D, N: stay in code

- **M (method parameters):** `BIM_LAND_*` grid, flat, stream, pond and catchment thresholds; `BIM_MV_R`,
  `BIM_MV_DOOR`, `BIM_MV_CAR`, `BIM_MV_NODES`, `BIM_MV_TOL`, `BIM_MV_CARS`; `BIM_ACC_BANDS`,
  `BIM_ACC_MAXT`, `BIM_ACC_FRONT`, `BIM_ACC_STEPS`, `BIM_ACC_IXR`, `BIM_ACC_IXMERGE`, `BIM_ACC_CUT`;
  `BIM_CLIM_YEARS`, `BIM_CLIM_EQ_*`; `BIM_SITERUN_RADIUS`; `BIM_DG_STEP`; `BIM_DG_LAMBDA` (0.686 m,
  the wavelength at 500 Hz for ISO 9613-2's barrier term: a physical derivation, kept with the method).
- **C (definitions):** `BIM_G` (9.80665), `BIM_FT2_M2`, `BIM_WGS84_A`, `BIM_WGS84_E2`, `BIM_UTM_K0`,
  `BIM_D2R`, `BIM_SOLAR_CONST` (1361 W/m2, a measured value: its source to be cited in a comment).
- **E (data sources):** `BIM_GEOCODE_URL`, `BIM_OVERPASS_URL`, `BIM_OVERPASS_MIRRORS`, `BIM_TERRARIUM_URL`,
  `BIM_LAND_FEMA`, `BIM_CLIM_ARCHIVE`, `BIM_CLIM_AQ`, `BIM_CLIM_EQ`, `BIM_CEN_TIGER`, `BIM_CEN_API`,
  `BIM_MAP_STYLES`, `BIM_DATA_PRESETS`, `BIM_DATA_PORTALS`.
- **D and N:** the rest: colours, ramps, labels, icons, panel sizes, keys, cache sizes, tolerances.

## The values said in words

The same numbers are written into what the analyses say. Counted in the V166b build (matches of
the phrase anywhere, comments included):

| Phrase | Matches |
|---|---|
| "8 minutes" | 5 |
| "12 minutes", "12 to rail", "station within 12" | 7 |
| "4.8 km/h", "80 m a minute" | 4 |
| "300 m" | 6 |
| "400 m" | 14 |
| "800 m" | 2 |
| "2 minutes (bus)", "0.75 (rail)" | 1 |
| "LEED ND" | 11 |
| "1004.5" | 3 |
| "ASCE 7" | 4 |

Each sentence that states a record's value is built from the record in V167, so an override or a
new edition changes the words with the number. The suite's "no literal left" check reads the
strings as well as the code.

## Order of the move

1. The reader, the record format and the profile tree, with S's TfL, CRTN, FHWA and WHO records
   (V164 to V166's analyses), their suites unchanged.
2. The occupant loads (IBC) and the combinations (ASCE 7), V105's and V125's suites unchanged.
3. The A records, each overridable, with "the app's assumption" as its publisher.
4. H's slope bands, once their source is read; until then a record marked U.
