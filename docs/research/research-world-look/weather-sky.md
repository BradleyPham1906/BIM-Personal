# World look: live weather data and sky and weather rendering

**Status:** research by one of three parallel research agents, 2026-11-24. Not implementation approval. The
independent second reader the protocol asks for has not yet re-checked this note (see "What is still open").
Sibling topics (rendering efficiency, instancing and LOD; trees, people and audio) are in their own notes.

## 1. Abstract

The question: how can the World BIM's rendered view show the real weather at the site, live (the sky, clouds,
rain, snow, fog, wind and wet surfaces changing with measured or forecast data), cheaply enough for a phone, and
still work offline? The answer, on the evidence below: take one keyless forecast request per site per hour from
Open-Meteo (CORS open, CC BY 4.0, free for non-commercial use only, 10 000 calls a day per IP), with MET Norway's
Locationforecast as the keyless, CORS-open fallback; keep the last answer with the project so the view opens
offline; turn each time step into a small WeatherState vector (cloud cover by layer, overcast, a fog extinction
from visibility by Koschmieder's law as WMO defines it, precipitation kind and intensity from the WMO 4677 code
and the rate, wind, thunder, snow depth, and a wetness that soaks and dries over time) and blend toward it with
a frame-rate independent exponential rule, as games blend weather types. For the sky, three.js r186's own
`Sky.js` (MIT, the same release the app vendors, but not in the app's bundle) gives an analytic Preetham-form
sky with a built-in 2D cloud layer whose coverage and density are uniforms: the cheapest credible live sky,
measured here at about four to five times the app's gradient dome per pixel (software rendering). Hillaire's
2020 LUT atmosphere is the next step (about 1 ms on an iPhone 6s by its author's figures); volumetric clouds
are a desktop-only option. The rendered view is a progressive accumulation renderer, so weather that moves
(rain, snow, drifting clouds, lightning) has to be drawn as an overlay over the averaged picture, not inside it.

## 2. The question and the hypotheses

What a good answer must decide: the data source and its fallback; the request cadence; the parameter vector and
its mapping; the blending rule; the sky technique; the techniques for clouds, rain, snow, fog, wet surfaces and
wind; how this fits the app's rendered view; and what the owner must decide.

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | Open-Meteo's forecast answers a browser keylessly with CORS, every time | **Partly failed.** CORS holds (`access-control-allow-origin: *`; a preflight asking for `user-agent` answered 200). But from this cloud machine the forecast endpoint answered 429 "Daily API request limit exceeded" to curl and to Chromium (once 200 in Chromium, then 429 a minute later); headers `X-RateLimit-Limit: 10000.0`, `X-RateLimit-Window: 86400`, `Retry-After: 16609`. Limits are per IP, so users behind a shared address can hit them. | ws-endpoints-results.txt, ws-browser-cors-results.json, ws-openmeteo-full-results.json; Open-Meteo terms |
| H2 | At least two other keyless sources answer a browser with CORS | **Held.** MET Norway Locationforecast (global) and Nowcast (Nordic), NWS api.weather.gov (US), Bright Sky (Germany) and RainViewer (radar tiles) all answered 200 from a page in Chromium. **aviationweather.gov's METAR API failed**: no `access-control-allow-origin` header; Chromium's fetch threw "Failed to fetch". It is named, not proxied. | ws-browser-cors-results.json |
| H3 | Asking more often than every 15 minutes gains nothing | **Held, and stronger:** the models behind Open-Meteo update every 1 to 6 hours and arrive 1.5 to 7.5 hours after their start time (measured from their metadata); true 15-minute data exists only for Central Europe and North America, interpolated from hourly elsewhere. One request returns a day of 15-minute steps. | ws-openmeteo-full-results.json; Open-Meteo docs |
| H4 | The vendored three.js 0.186.1 bundle already has a physical sky | **Failed.** `runtime/three/0.186.1/bim-three.min.js` exports three's core and four glTF addons only (tools/three/build_three.mjs); no `Sky`. The r186 addon `examples/jsm/objects/Sky.js` (MIT, identical on the r186 tag and npm 0.186.1, SHA-256 34121b60...) exists and has a cloud layer; it is WebGL only (`SkyMesh` is its WebGPU/TSL twin). | grep of the bundle; Sky.js read as text |
| H5 | A LUT-based atmosphere costs per frame no more than a few times the app's gradient dome | **Held (software rendering, ranking only).** Sampling a 200 x 100 sky-view texture full screen cost about the same as the gradient dome; building the 96 x 50 texture with Hillaire's mobile step counts cost 0.8 to 1.9 ms in SwiftShader, while a per-pixel ray-march cost 60 to 80 times the dome. Hillaire reports about 1 ms in total on an iPhone 6s. | ws-sky-cost-results.json; Hillaire 2020 Table 2 |
| H6 | Volumetric clouds run at 60 fps on a current phone | **Failed on the evidence read.** takram's three.js volumetric clouds: iPhone 13, 36 to 53 fps on the Low preset with temporal upscaling; its author advises a skybox if Low is too slow. Frostbite: 0.91 ms for 720p clouds on Xbox One; Horizon Zero Dawn targeted 2 ms on PS4. | takram clouds README; Hillaire 2016; Schneider 2015 |
| H7 | Visibility maps to fog density by Koschmieder's law | **Held for the arithmetic** (WMO-No. 8 eq. 9.6: MOR P = ln(1/0.05)/sigma, about 3/sigma). **Threat to the input:** model visibility is a weak field (Open-Meteo issue #1540 "visibility data", open since 2025-10-20, content not read; practitioners' forums say model visibility is often reported as unlimited). | WMO-No. 8; ws-weather-map-results.json |
| H8 | The weather can blend toward a new state at the same speed whatever the frame rate | **Held.** `x += (target - x)(1 - exp(-dt/tau))` reached 0.950213 after 60 s with tau 20 s at 30, 60 and 120 fps and in one 60 s step, equal to 1 - e^-3. | ws-weather-map-results.json |
| H9 | Weather fits the rendered view without changing its design | **Failed in part.** The view averages 16 to 256 jittered passes and restarts when its signature changes (`bimRvSig`, rendered-view.js:154 and 175); anything that moves every frame would restart it. Static weather (sky, frozen clouds, fog, wetness, snow) fits inside the average; moving weather needs an overlay drawn after it. | rendered-view.js:162-207; rendered-core.js:246-259 |

## 3. Method

Sources by kind: services answering requests from here (Open-Meteo, MET Norway, NWS, AviationWeather, RainViewer,
Bright Sky); their terms and documentation pages, read as text; papers (Hillaire 2020, Hillaire 2016 Frostbite
course notes, Zotti et al. 2007 on Preetham, WMO-No. 8); open implementations read as text, licence first
(three.js r186 `Sky.js` and `SkyMesh.js`, Epic's UnrealEngineSkyAtmosphere licence, Bruneton's 2017 code
licence, takram three-geospatial atmosphere and clouds READMEs, webgpu-sky-atmosphere README); practitioners'
accounts (Lagarde's water drop posts; Schneider's Horizon Zero Dawn talk page; GTAMods wiki; FiveM native
documentation); the app's own code. Downloads are in the scratchpad (`ws-src/`), read as text, never run.

Experiments (scripts and raw results in `docs/research/experiments/world-look/`):

- `ws-endpoints.sh` -> `ws-endpoints-results.txt`: each source by curl, a GET with an Origin header and an OPTIONS
  preflight, status, CORS, cache and rate-limit headers, time to first byte.
- `ws-browser-cors.cjs` -> `ws-browser-cors-results.json`: each source fetched from a page at http://127.0.0.1 in
  Chromium 158 (Playwright, headless), as the app would fetch it.
- `ws-openmeteo-full.cjs` -> `ws-openmeteo-full-results.json`: the full variable set and ten models' metadata
  (`/data/<model>/static/meta.json`: last run, availability time, update interval).
- `ws-sky-cost.cjs` -> `ws-sky-cost-results.json`: full-screen WebGL2 passes timed in headless Chromium, which here
  renders through SwiftShader (ANGLE on Vulkan, SwiftShader driver): software rendering on this machine, for
  ranking techniques only, three runs at 390 x 844 and 1280 x 720. Every shader written here from the method.
- `ws-weather-map.cjs` -> `ws-weather-map-results.json`: the proposed mapping and blending on eleven cases
  including edges.

The independent check (a second reader re-reading every source behind a fact the code will use) has not been
done; it is listed under section 10.

### Search log

| Where | Query or address | What came back | Kept or set aside, and why |
|---|---|---|---|
| curl, Chromium | api.open-meteo.com/v1/forecast (current, minutely_15, hourly) | 429 to curl; 200 once then 429 in Chromium; full CORS headers | Kept: CORS P; the limit is real here |
| curl, Chromium | api.open-meteo.com/data/<model>/static/meta.json | 200 every time, no rate-limit headers, while the forecast was 429 | Kept: update intervals P; whether it is a documented, supported endpoint is U |
| curl | open-meteo.com/en/terms, /en/licence, /en/docs, /en/pricing | Terms, limits, licence, variables, WMO table, 15-minute regions, timeformat note | Kept, P |
| curl, Chromium | api.weather.gov points and KDCA latest observation | 200, ACAO *, preflight allows `User-Agent`; 403 to an empty User-Agent | Kept: US only |
| curl | weather.gov/documentation/services-web-api | Open data, rate limit not public, User-Agent asked for | Kept, P |
| curl, Chromium | aviationweather.gov/api/data/metar | 200 to curl without ACAO; browser fetch refused | Named as not CORS-open; set aside |
| curl, Chromium | api.met.no locationforecast 2.0 compact; nowcast 2.0 | 200, ACAO *, Expires and Last-Modified headers | Kept: the fallback |
| curl | api.met.no/doc/TermsOfService, /doc/License | Identification, 20 requests/s per application in total, caching rules, CC BY 4.0 and NLOD 2.0 | Kept, P |
| curl, Chromium | api.rainviewer.com/public/weather-maps.json; a tile | 200, ACAO *, tile max-age 172800 | Kept for later; personal and educational use only |
| curl | rainviewer.com/api.html, /api/weather-maps-api.html | Past 2 h at 10 min, zoom 7 maximum, attribution mandatory | Kept, P |
| curl, Chromium | api.brightsky.dev/current_weather | 200, ACAO * | Kept as a German option; DWD licence not read (U) |
| raw.githubusercontent.com | three.js r186 Sky.js, SkyMesh.js, Water.js, webgl_shaders_sky.html, LICENSE | Read; unpkg three@0.186.1 Sky.js identical | Kept, P |
| grep | runtime/three/0.186.1/bim-three.min.js | Fog, FogExp2, InstancedMesh, Points, Data3DTexture present; no Sky | Kept, P |
| sebh.github.io | egsr2020.pdf | Table 2 (LUT sizes, steps, ms on GTX 1080 and iPhone 6s), section 7 | Kept, P |
| raw.githubusercontent.com | sebh/UnrealEngineSkyAtmosphere LICENSE; ebruneton/precomputed_atmospheric_scattering LICENSE | MIT (Epic Games 2020); BSD 3-clause (Bruneton 2017) | Kept, P |
| raw.githubusercontent.com | takram three-geospatial atmosphere and clouds READMEs, LICENSE; JolifantoBambla webgpu-sky-atmosphere README, LICENSE | MIT both; device fps table for clouds; atmosphere is GLSL, WebGPU documented separately | Kept, P for what the READMEs say, S for the fps (author's own measurements) |
| media.contentapi.ea.com | s2016-pbs-frostbite-sky-clouds-new.pdf | Tables 3 and 4 (Xbox One), weather texture section 5.3.1 | Kept, P |
| guerrilla-games.com | HZD cloudscapes page | Abstract: 2 ms GPU target; PDF and PPT links | Kept for the budget; slides not read (52 MB), S |
| advances.realtimerendering.com | s2015, s2017, s2019 | 406 to curl without an Accept header; s2019 index read with one; RDR2 talk listed | Talk itself not read (U) |
| gtamods.com | wiki Timecyc.dat (Weather redirects to it) | Per-hour keyframes interpolated per weather; parameter list; GTA V weather list | Kept, S (reverse-engineered community knowledge) |
| raw.githubusercontent.com | citizenfx/natives MISC and GRAPHICS | Weather transition by percentage; over-time transition in seconds; rain level; wind m/s clamped 0 to 12 | Kept, S |
| wiki.rage.mp | Weather | 403 | Set aside, refused |
| seblagarde.wordpress.com | water drop 3a and 3b | Wet albedo theory, DoWetProcess code | Kept, P for the post's method, S for its sources |
| en.wikipedia.org | Visibility | Koschmieder with 2 % (3.912/b) | Kept as the second source; WMO uses 5 % |
| WebSearch, then weather.gov copy | WMO-No. 8 (2008) Part I chapter 9 | Eqs 9.5 and 9.6 read in the PDF | Kept, P |
| old.wmo.int | CIMO Guide 2018 preliminary chapter 9 | 000 (no answer) | Set aside |
| WebSearch, GitHub search API | open-meteo visibility issues | Issue #1540 "visibility data" (open), #2163 fractional UTC offsets (open) | Titles P; #1540's text refused (github.com 403 to this session) |
| WebSearch, tuwien.ac.at | Zotti, Wilkie, Purgathofer 2007 | PDF read: Preetham fitted for turbidity 2 to 6 only; negative zenith luminance near the edges; poor near sunrise and sunset | Kept, P |

## 4. Findings by topic

### 4.1 Live data sources (P unless said; high confidence for what was measured)

**Open-Meteo.** Keyless; CORS open, preflight allows `user-agent` and exposes the rate-limit headers to scripts.
Terms (read 2026-11-24): the free API is for non-commercial use only, "less than 10'000 API calls per day, 5'000 per
hour and 600 per minute" (the pricing page adds 300 000 a month); "Rate limits are applied by IP addresses and
application"; non-commercial includes "private or non-profit websites or apps that do not have subscriptions or
advertising"; data under CC BY 4.0 with a link "next to any location Open-Meteo data are displayed", e.g.
"Weather data by Open-Meteo.com". The server software is AGPLv3, so self-hosting is possible as a separate
program. Variables confirmed in the docs: `cloud_cover`, `cloud_cover_low` (up to 3 km, "low level clouds and fog"),
`cloud_cover_mid` (3 to 8 km), `cloud_cover_high` (from 8 km), `visibility` (m, "influenced by low clouds, humidity
and aerosols"), `weather_code` (WMO), `precipitation`, `rain`, `showers`, `snowfall`, `snow_depth`, `is_day`,
`wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m`, radiation (`direct_normal_irradiance`,
`diffuse_radiation`), `freezing_level_height`. "Current conditions are based on 15-minutely weather model data."
15-minute data comes from NOAA RRFS (North America) and DWD ICON-D2 and Météo-France AROME (Central Europe);
"If 15-minutely data is requested for other regions data is interpolated from 1-hourly". The WMO table in the docs
lists 0, 1, 2, 3, 45, 48, 51 to 57, 61 to 67, 71 to 77, 80 to 82, 85, 86, 95, 96, 99, with the note that 96 and 99
come only from models with explicit hail (ICON, UKMO); 97 also appears in their table. A timing trap: with the
default ISO times, "Daylight saving time (DST) changes within the requested range are ignored"; the docs advise
`timeformat=unixtime`. Open issue #2163 (title read) reports hourly data in fractional-offset zones stamped 30 or
45 minutes off. Measured model metadata (2026-11-24, ws-openmeteo-full-results.json):

| Model | Update interval | Time step | Last run start -> available |
|---|---|---|---|
| dwd_icon (global) | 6 h | 1 h | 12:00 -> 15:46 |
| dwd_icon_eu, dwd_icon_d2 | 3 h | 1 h | 15:00 -> 17:55, 16:36 |
| ecmwf_ifs025 | 6 h | 3 h | 06:00 -> 13:30 |
| ncep_gfs013 | 6 h | 1 h | 12:00 -> 17:23 |
| ncep_hrrr_conus | 1 h | 1 h | 17:00 -> 18:28 |
| ukmo_global_deterministic_10km | 6 h | 1 h | 06:00 -> 12:55 |
| ukmo_uk_deterministic_2km | 1 h | 1 h | 14:00 -> 18:17 |
| meteofrance_arome_france_hd | 3 h | 1 h | 15:00 -> 18:53 |
| knmi_harmonie_arome_europe | 1 h | 1 h | 16:00 -> 18:35 |

(The docs' summary table says ICON updates "every 3 hours"; the global ICON's metadata says 6 h and the EU and D2
nests 3 h. Both recorded; the metadata is the measurement.)

**MET Norway, Locationforecast 2.0.** Keyless, global, CORS open (`Access-Control-Allow-Origin: *`, preflight 204),
answers with `Expires` and `Last-Modified`. Terms (revised 2026-11-05): identify yourself by User-Agent, or, where
a browser cannot, "the website must instead identify itself using an Origin (Javascript) or Referer" header, which
browsers send; total traffic under 20 requests a second per application, "total, not per client", including
traffic "coming directly from the browsers"; never repeat a request before `Expires`; use `If-Modified-Since`;
truncate coordinates to 4 decimals (5 or more answers 403 on new products); spread requests, not on the hour;
"Applications on mobile devices must not retrieve new data as long as the application is not in use"; the
user's IP is logged in Oslo. Licence: CC BY 4.0 and NLOD 2.0, credit "Data from MET Norway". The compact
product has cloud area fraction, precipitation amount, wind and a symbol code; it has no visibility (to confirm
in the complete product: U).

**US National Weather Service, api.weather.gov.** Keyless, CORS open, US only. Docs: open data "free to use for
any purpose"; rate limit "not public", retry after about 5 seconds; a User-Agent with contact is asked for (an
empty one got 403 here; the browser's own was accepted, 200 from Chromium). Observations are station METARs
(`max-age=300`).

**AviationWeather.gov Data API.** Keyless, worldwide METARs (airports only), JSON. **No CORS**: no
`Access-Control-Allow-Origin` on the GET; the browser refused it. Named here, not proxied.

**RainViewer.** Keyless, CORS open on the index and the tiles. "Free public weather radar API for personal,
educational, and small-scale community use"; attribution mandatory ("Weather data by RainViewer" with a link);
past 2 hours at 10-minute steps; maximum zoom 7 (about 1.2 km a pixel at the equator, our arithmetic); radar
coverage only where radars exist. Useful later for "is it raining at the site right now" in covered places; not
needed for the first phase.

**Bright Sky (DWD open data, Germany).** Keyless, CORS open, 200. Its DWD licence terms were not read (U).

Latency from here, first byte: Open-Meteo 0.14 to 0.28 s, NWS 0.18 to 0.23 s, MET Norway 0.40 to 0.57 s,
RainViewer 0.45 s, Bright Sky 0.42 s (one run each; through this environment's proxy).

### 4.2 How games represent and blend weather (S, medium confidence)

- **GTA trilogy (III, Vice City, San Andreas)**, from the GTAMods wiki's reading of `timecyc.dat`: one parameter
  set per weather type per keyframe (each game hour in III and Vice City; 8 keyframes a day in San Andreas), and
  "each value of one entry gets interpolated with the previous and the next setting of the current ingame
  weather". The set holds ambient colours, direct light colour, sky top and bottom colours (the bottom is the fog
  colour), sun core and corona colours and sizes, shadow intensity, far clip, fog start, cloud colours and alpha,
  water colour. The next weather is read from a fixed hourly list.
- **GTA V**, from the FiveM natives documentation (community reverse engineering): `_SET_WEATHER_TYPE_TRANSITION
  (type1, type2, percentWeather2)` "mixes two weather types"; `SET_WEATHER_TYPE_OVERTIME_PERSIST(type, time)` moves
  to a type over a time "in seconds"; `_SET_RAIN_LEVEL` drives rain, rain sound and puddle growth separately from
  the type; `SET_WIND_SPEED` is in m/s, clamped 0 to 12. Named weather types include EXTRASUNNY, CLEAR, CLOUDS,
  SMOG, FOGGY, OVERCAST, RAIN, THUNDER, CLEARING, SNOW (GTAMods' list). Rockstar's own timecycle files were not
  read (they are game data), so the per-type parameter lists stay S.
- **RDR2** lists HIGHPRESSURE to WHITEOUT (21 types, GTAMods). Bauer's 2019 SIGGRAPH talk on RDR2's clouds and
  fog is listed on the Advances course page but was not read (U).
- **Frostbite (Hillaire 2016), P:** sky, fog and clouds "could only be linearly blended" before their rework;
  clouds are driven by a weather texture whose red channel is 2D cloud density and green the cloud type, both
  "statically assigned to a level and also dynamically updated if necessary".

The pattern all three share: a small set of named states, each a parameter vector, a per-time-of-day variant,
and a scalar blend between two states over seconds to minutes, with precipitation, wetness and wind as separate
scalars. For this app the time-of-day part comes from physics (the sun position the app already computes,
`sun-position.js`, and a physical sky), so the state needs no hourly keyframes; only night keeps an artistic
row (`BIM_RV_NIGHT`).

### 4.3 The proposed WeatherState and its mapping (our design; the inputs P, the coefficients U until tuned)

| Field | From (Open-Meteo, MET Norway in brackets) | Rule |
|---|---|---|
| cloudCoverage 0..1 | `cloud_cover` (`cloud_area_fraction`) | /100; if absent, 1 - (1-low)(1-mid)(1-high) (random overlap) |
| cloudLow, cloudMid, cloudHigh | `cloud_cover_low/mid/high` | /100; low drives the cloud layer's density, high a thin cirrus look |
| cloudDensity 0..1 | cloudLow | 0.3 + 0.6 low (thick low deck reads darker than cirrus) |
| overcast 0..1 | cloudCoverage | (cover - 0.6)/0.4, clamped: blends the physical sky toward an overcast gradient (the app's `overcast` row) and dims the sun |
| sunScale, skyScale | `direct_normal_irradiance`, `diffuse_radiation` | ratio to a clear-sky value at the same sun elevation (clear-sky model to choose: U) |
| fogSigma (1/m) | `visibility` | ln(20)/V, from WMO's MOR (5 % transmission); V clamped 20 m..100 km; null -> 50 km; FogExp2 density sqrt(ln 20)/V |
| precipKind | `weather_code` (`symbol_code`), `snowfall`, `rain` | WMO groups: 51-55 drizzle, 56/57/66/67 freezing, 61-65/80-82 rain, 71-77/85/86 snow, 96/99 hail, 95/97 thunder with rain |
| precipIntensity 0..1 | `weather_code`, `precipitation` (mm/h) | max(code's level, log10(rate/0.1)/log10(500)) |
| thunder | codes 95-99 | flag: lightning flashes |
| windSpeed, windFrom, gust | `wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m` (`wind_speed`, `wind_from_direction`) | m/s; rain slant, cloud drift, foliage |
| snowCover 0..1 | `snow_depth` | depth / 0.05 m, clamped (threshold U) |
| wetness 0..1 | precipIntensity over time | integrator: soaks with tau 600 s / intensity, dries with tau 3 h (to tune; Lagarde: depends on porosity and exposure) |
| day | the app's own sun position | not `is_day`: the app's sun is the authority for the picture |

The experiment (ws-weather-map-results.json) ran eleven cases. It caught one edge in the first version: a
visibility of 0 (dense fog) was treated as missing and mapped to 50 km; corrected to "0 is a value, only null is
missing", clamped to 20 m. An unknown code (5) maps to no precipitation with `codeKnown: false`; drizzle with
0 mm reads 0.09 intensity, not zero.

**Blending.** Each numeric field moves toward its target with `x += (target - x)(1 - exp(-dt/tau))`, which is
frame-rate independent (H8). Proposed tau: clouds 60 s, overcast and light 30 s, fog 30 s, precipitation 8 s,
wind 5 s; wetness and snow as integrators over hours. The categorical precipKind switches when intensity has
faded below 0.05 (rain fades out before snow fades in), as GTA V keeps rain level separate from the type. Between
fetches the 15-minute series is interpolated linearly at the clock time; the code takes the nearest step.

### 4.4 Sky rendering (P for what the sources say; costs S, measured here only in software)

- **Preetham (1999), three.js `Sky.js` (r186, MIT).** An analytic sky: per-pixel optical depth from zenith angle,
  Rayleigh and Mie (Henyey-Greenstein) phases, a sun disc; uniforms `turbidity`, `rayleigh`, `mieCoefficient`,
  `mieDirectionalG`, `sunPosition`. In r186 it also draws **a cloud layer**: a plane projection of the view ray,
  4-octave gradient noise with per-octave drift, a large-scale coverage noise, Beer-powder self-shadow, a
  Henyey-Greenstein silver lining, opacity by Beer's law, composited through the atmosphere; uniforms
  `cloudCoverage`, `cloudDensity`, `cloudScale`, `cloudSpeed`, `cloudElevation`, `time`, `showSunDisc`. It is
  WebGL only ("When using WebGPURenderer, use SkyMesh"). It is not in the app's bundle; adding it means one more
  export line in `tools/three/build_three.mjs` and new manifest entries. Limits (Zotti, Wilkie and Purgathofer 2007,
  P): Preetham was fitted for turbidity 2 to 6 only, gives negative zenith luminance near the edges of its inputs,
  is problematic with the sun more than 85 degrees from the zenith, and does not match measured clear skies as
  well as the CIE clear-sky models. So: keep turbidity 2 to 6, and keep the app's own dusk and night rows below
  about 5 degrees of sun elevation.
- **Hillaire (2020), P.** Four small LUTs re-rendered every frame, so weather and time of day can change freely:
  transmittance 256 x 64 (40 steps), sky-view 200 x 100 (30 steps; 96 x 50 with 8 steps on mobile), aerial
  perspective 32 x 32 x 32 (32 x 32 x 16 on mobile), multiple scattering 32 x 32 (20 steps). GTX 1080: 0.14 ms
  on screen, 0.31 ms in total at 1280 x 720. iPhone 6s: 0.53, 0.27, 0.11 and 0.12 ms for the four LUTs; "for Epic
  Games' Fortnite, the total sky rendering cost was roughly 1ms on iPhone 6s". Reference code MIT (Epic Games
  2020). A WebGPU port exists (webgpu-sky-atmosphere, MIT, 2024).
- **Bruneton (2008, 2017), P.** Precomputed 4D scattering; code BSD 3-clause. Hillaire measured a full LUT update
  with Bruneton's code at 250 ms on a GTX 1080, which suits a fixed Earth atmosphere but not per-frame weather.
  takram's three.js port (MIT) is GLSL, Earth-limited, and ships precomputed textures.
- **Measured here (software, ranking only):** per frame at 1280 x 720, median of three runs: gradient dome
  9.4 ms, Preetham-form sky with 4-octave cloud layer 45.9 ms (about 4.9 times), per-pixel ray-march 748.8 ms
  (about 80 times), 200 x 100 LUT build 17.8 ms plus sample 7.0 ms, 96 x 50 mobile LUT build 1.3 ms plus sample
  6.4 ms. At 390 x 844 the ratios were similar (analytic with clouds about 4 times the dome).

**Fit for the app:** the app's sky dome is drawn once per accumulated picture and filtered into an environment
map by PMREM (`rendered-core.js:146-160`), so the sky's per-frame cost matters less here than in a game; what
matters is that a changed weather state re-runs `setSky` (a new dome and a PMREM pass) and restarts the
accumulation. `Sky.js` is the shortest path and costs little; Hillaire's LUTs are the quality path for twilight
and aerial perspective. Neither needs WebGPU.

### 4.5 Clouds, rain, snow, fog, wet surfaces, wind

| Effect | Cheapest credible technique | Cost class | Phone | What the app needs |
|---|---|---|---|---|
| Clouds | 2D noise layer in the sky shader (Sky.js r186) driven by coverage and density | Low (a few noise octaves per sky pixel) | Yes | Sky.js in the bundle; coverage, density, drift from WeatherState |
| Clouds, volumetric | Ray-marched cloud shell with weather texture (Schneider 2015; Hillaire 2016; takram, MIT) | High: 0.9 ms 720p Xbox One; 2 ms PS4 budget; iPhone 13 36-53 fps Low | No | Desktop-only option, later |
| Overcast | Blend sky toward a flat grey gradient; dim and soften the sun; raise sky light | Free | Yes | The app's `overcast` row already exists; blend by `overcast` |
| Rain, snow | Instanced streaks (rain) or sprites (snow) in a box that follows the camera, count by intensity, slanted by wind | Medium, fill-bound | Yes, with a capped count | An overlay pass after the accumulated picture; depth from the first pass so streaks hide behind walls (U, design) |
| Fog | Exponential fog on every material: three's `FogExp2` (exp-squared, available) or true exp(-sigma d) by a shader chunk | Low | Yes | Turn `fog` on for the model materials in weather mode (today `fog: false` on all model materials, rendered-core.js:116-121 and 156) |
| Height fog | exp(-sigma d) with sigma falling with height | Low | Yes | A shader chunk (three has no height fog) |
| Wet surfaces | Lagarde: `Diffuse *= lerp(1, lerp(1, 0.2, porosity), wet)`; gloss toward 1 | Low | Yes | Per-material porosity (the surface kinds, `surface-kinds.js`, U), roughness lower, colour darker |
| Snow cover | Whiten faces whose normal points up, by snowCover | Low | Yes | A shader chunk |
| Wind | Cloud drift and rain slant from the wind; foliage sway is the assets agent's | Free | Yes | WeatherState fields |
| Lightning | Brief sky and ambient flash at random intervals when thunder | Free | Yes | Overlay; never in the accumulated picture |

Rain streak cost measured here in software: 2 000 streaks 27 ms at 390 x 844 and 46 ms at 1280 x 720; 10 000
about 145 and 220 ms (fill and blending dominate; ranking only). Fewer, larger streaks near the camera are the
lever.

### 4.6 Efficiency

- **Cadence.** Models update every 1 to 6 hours (measured), so one request per site per hour, at a random minute
  (MET Norway's rule against peaks on the hour), returning the next 24 hours of 15-minute steps and the last
  2 hours (`past_minutely_15`), is enough; between requests the app interpolates. 24 requests a day per user is
  0.24 % of Open-Meteo's daily limit. MET Norway: honour `Expires` and `If-Modified-Since`.
- **On change only.** The live weather is fetched only while the rendered view is open, the tab is visible
  (`document.visibilityState`) and "live" is on; the WeatherState is quantised (for example cover in tenths,
  visibility in a log step) into the view's signature so the picture restarts and the PMREM is redone only when
  the look changes, not each frame.
- **Caching and offline.** The last answer is kept with the project (as `climate-data.js` keeps `A3D.site.climate`,
  so the board opens offline), with its fetch time and source; offline, the view uses the stored series while it
  covers the moment, then the site's climate normals the app already derives, then the chosen sky preset.
- **Failure.** On 429 read `Retry-After` and stop asking until then; try MET Norway; then the cache; say which in
  the view's state text and a toast, as the build contract asks.

## 5. The alternatives compared

Criteria, stated first: (a) keyless and CORS-open from a browser; (b) licence compatible with a public Apache-2.0
app, attribution acceptable; (c) global coverage; (d) the variables the WeatherState needs (cloud layers,
visibility, code, precipitation, wind, snow depth); (e) limits that suit one request an hour per user; (f) latency.

| Source | (a) | (b) | (c) | (d) | (e) | (f) |
|---|---|---|---|---|---|---|
| Open-Meteo forecast | Yes | CC BY 4.0; free API non-commercial only | Global, best-match models | All, incl. cloud layers and visibility | 10 000/day, 5 000/h, 600/min per IP; 429 seen here | 0.14-0.28 s |
| MET Norway Locationforecast | Yes | CC BY 4.0 / NLOD 2.0, any use | Global | Cloud fraction (layers in complete), precip, wind, symbol; visibility U | 20 req/s total for the whole app; IP logged | 0.40-0.57 s |
| NWS api.weather.gov | Yes | Open data, any use | US only | Observations and grid forecasts | Not public | 0.18-0.23 s |
| AviationWeather METAR | **No CORS** | US government | Airports worldwide | Cloud layers, visibility, present weather | Rate-limited | 0.21 s |
| RainViewer | Yes | Personal and educational only | Radar areas | Precipitation radar only | Not posted | 0.45 s |
| Bright Sky | Yes | DWD terms (U) | Germany | DWD observations | Not posted | 0.42 s |

Recommendation from the table: Open-Meteo primary (only source meeting (c) and (d) together), MET Norway as the
fallback (any-use licence, global), NWS optional for US sites. What would change it: the owner deciding the app
is commercial (Open-Meteo's free API is then excluded; MET Norway's 20 requests a second in total becomes the
ceiling for all users together, or a paid Open-Meteo plan or a self-hosted Open-Meteo server).

Sky techniques, criteria: phone frame cost, quality at twilight and in overcast, licence, effort, WebGL2 and WebGPU.

| Technique | Phone cost | Quality | Licence | Effort | WebGL2 / WebGPU |
|---|---|---|---|---|---|
| App's gradient dome + presets | Lowest | No sun glow, no clouds | Ours | None | Both |
| three.js Sky.js r186 (Preetham + cloud layer) | Low (about 4-5 times the dome, software) | Good by day; weak at twilight (Zotti 2007) | MIT | Small: one bundle export | WebGL (SkyMesh needs WebGPURenderer, not bundled) |
| Hillaire 2020 LUTs | About 1 ms on iPhone 6s (author) | Good at twilight, aerial perspective, any weather | MIT reference | Medium: our port | Both (WebGPU port exists) |
| Bruneton precomputed | Low at runtime | Good; fixed atmosphere | BSD 3 | Medium; 250 ms recompute | WebGL (takram GLSL) |
| Volumetric clouds | High; not 60 fps on iPhone 13 | Best | MIT (takram) | Large | WebGL; desktop only |

Recommendation: Sky.js first, Hillaire LUTs second, volumetric clouds only as a desktop option.

## 6. The experiments

As listed in section 3; the numbers are in sections 2, 4.1, 4.4 and 4.5. Environment: Node 22.23.5, Chromium
158.0.8127.36 headless via Playwright, renderer "ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero)),
SwiftShader driver)", this cloud machine, its proxy. Three runs per size for the shader costs (the first run of
each size is warm-up-affected and higher). Not measured: any GPU, any phone, Safari, Firefox, WebGPU.

## 7. Edges

- Visibility 0 is a value (dense fog), not missing; null is missing (caught by the experiment).
- Unknown or new WMO codes: no precipitation, flagged; 96 and 99 only from ICON or UKMO; 97 also listed.
- 15-minute data is interpolation outside Central Europe and North America: say so on the result.
- Time zones: ISO times ignore DST changes inside a request, and fractional-offset zones are reported wrong
  (issue #2163): ask for `timeformat=unixtime` and convert with the app's own zone code.
- The study date and time are not "now": `bimSunSettings` defaults to 21 June 12:00. Live weather belongs only to
  a "now" mode; for another moment, the forecast (16 days ahead, 92 days back) or the archive the app already
  calls gives that moment's weather.
- Polar day and night: the app's sun decides day; `is_day` is ignored.
- A site with no latitude and longitude has no live weather.
- MET Norway: coordinates truncated to 4 decimals; a 203 status means a deprecated product.
- Preetham outside turbidity 2 to 6 and with the sun lower than about 5 degrees: fall back to the app's dusk and
  night rows.
- A changed weather state restarts the accumulated picture and the PMREM pass; quantise it.

## 8. What the app already has

- `src/js/engine/site-analysis/climate-data.js:21-64`: Open-Meteo archive and air-quality URLs, `bimClimGet` with
  errors by host (`bimCtxErr(bimMapHost(url), e)`), results kept with the project. The forecast host is new.
- `src/js/engine/render/rendered-core.js:22-30` sky rows (clear, overcast, dusk, white, night); `:84-89`
  `bimRvSkyFor`; `:129-160` the gradient dome, PMREM environment, `scene.fog` on the ground only; `:116-121` model
  materials with `fog: false`; `:246-259` per-picture lights, sky scale and fog distances.
- `src/js/engine/render/rendered-view.js:154-207`: the signature, the accumulation and its refinement loop; `:47-60`
  the per-browser sky setting.
- `src/js/engine/site/sun-position.js:140-155`: the sun from the site's saved or studied date and time.
- `runtime/three/0.186.1/bim-three.min.js`: Fog, FogExp2 (exp-squared, read from the bundle), InstancedMesh,
  InstancedBufferGeometry, Points, Data3DTexture; no Sky. `tools/three/build_three.mjs` decides the exports.
- `src/js/engine/render/water-sim.js` and `docs/research/research-notion-later-water-presentation.md` (V220): the
  same accumulation conflict is noted there for animated water; one overlay design can serve both.

## 9. Risks and threats to validity

- Rate limits per IP: users behind shared addresses (offices, mobile carriers' NAT) may see 429 as this machine
  did. Medium likelihood; handled by back-off and the fallback.
- Licence scope: Open-Meteo's free tier is non-commercial; the repository is public and Apache-2.0, but whether
  the deployed app is "non-commercial" is the owner's call.
- Privacy: every source sees the user's IP and the site's coordinates; MET Norway says so in its terms. The app
  should ask before the first live request.
- Model weather is not observed weather: visibility in particular (issue #1540); fog may be missed. Medium.
- All shader timings are software rendering; no phone or GPU was measured. The GPU and phone figures are the
  authors' own (Hillaire; takram), not checked here.
- Game sources are community reverse engineering (S); they inform the design, not code.
- The meta.json endpoint answered without rate-limit headers, but whether it is supported for clients is U.
- One run per endpoint for latency; one day; one location (London; Washington for NWS; Oslo for Nowcast).

## 10. What is still open (U), and why

- The independent second reader's check of every fact above (protocol step 9): not done in this pass.
- Open-Meteo issue #1540's text: github.com refused this session (403); title only.
- MET Norway complete product's variables (visibility, cloud layers): not fetched.
- Bright Sky's DWD licence; RainViewer's full terms page: not read.
- Bauer 2019 (RDR2) and Schneider's slides themselves: not read (size, 406).
- The clear-sky model for `sunScale` (for example a Kasten-type relation): not chosen or read.
- Wetness time constants, snow-depth threshold, rain counts per device: to tune by eye and on devices.
- Phone, tablet and GPU frame times for Sky.js and a Hillaire port: need a device.
- The CIE overcast sky formula for the overcast blend: seen only as a listing in Zotti 2007; to read in CIE S 011.

## 11. The owner's decisions

1. **Commercial or not.** Open-Meteo's free API allows non-commercial use only. Is the deployed World BIM
   non-commercial (no subscriptions, no advertising)? If not: a paid plan, a self-hosted Open-Meteo, or MET Norway
   alone (any use, but 20 requests a second for all users together).
2. **Consent.** Ask the user once before sending the site's coordinates to a weather service (their IP is logged)?
3. **"Live" only at now.** Live weather only when the view's time is the present; for a studied date, the
   forecast or archive weather of that moment, or the chosen preset?
4. **The sky.** Add three.js `Sky.js` (MIT, r186) to the vendored bundle now (a bundle and manifest change),
   and research Hillaire's LUTs as the second step?
5. **Moving weather.** Accept an overlay over the averaged picture for rain, snow and lightning (they are not in
   saved pictures unless asked), or freeze them into the picture?
6. **Fallback order.** Open-Meteo, then MET Norway, then the cache, then climate normals, then the preset?
7. **Credits.** "Weather data by Open-Meteo.com" and "Data from MET Norway", with links, shown in the rendered view
   whenever live weather is on.

## 12. Recommendations

1. A `weather/` module (ES5, behind the adapter rule): fetch Open-Meteo hourly per site at a random minute while
   the rendered view is open and visible, `timeformat=unixtime`, `minutely_15` for 24 h and 2 h back, `hourly`
   cloud layers; keep the answer with the project; MET Norway as fallback; back off on 429 by `Retry-After`.
2. A pure `bimWeatherState(sample)` and `bimWeatherBlend(state, target, dt)` with unit tests on the edges in
   section 7 (they are logic, testable in `tests/unit/`).
3. Sky.js in the bundle; its uniforms driven by the state; overcast and night through the app's existing rows.
4. Fog on model materials in weather mode, sigma = ln(20)/visibility; a height-fog chunk later.
5. Wetness and snow by material uniforms (Lagarde's rule); porosity by surface kind.
6. Rain, snow and lightning as an overlay after the accumulated picture, capped counts per device class.
7. Hillaire LUT atmosphere as the quality step; volumetric clouds desktop-only, later.

## 13. References

| Source | URL | What was read | Date | Level |
|---|---|---|---|---|
| Open-Meteo terms | https://open-meteo.com/en/terms | Free-API limits, non-commercial definition, per-IP limits, pricing table | 2026-11-24 | P |
| Open-Meteo licence | https://open-meteo.com/en/licence | CC BY 4.0, attribution link, AGPLv3 server | 2026-11-24 | P |
| Open-Meteo forecast docs | https://open-meteo.com/en/docs | Variables, WMO table, 15-minute regions, timeformat, model table | 2026-11-24 | P |
| Open-Meteo API and metadata | https://api.open-meteo.com/v1/forecast ; /data/<model>/static/meta.json | Responses and headers from here | 2026-11-24 | P |
| Open-Meteo issues #1540, #2163 | https://github.com/open-meteo/open-meteo/issues | Titles and states via GitHub search API | 2026-11-24 | P (titles), U (content) |
| MET Norway terms | https://api.met.no/doc/TermsOfService | Identification, traffic, caching, privacy | 2026-11-24 | P |
| MET Norway licence | https://api.met.no/doc/License | CC BY 4.0, NLOD 2.0, credit | 2026-11-24 | P |
| MET Norway Locationforecast, Nowcast | https://api.met.no/weatherapi/locationforecast/2.0/compact | Responses and headers | 2026-11-24 | P |
| NWS API docs | https://www.weather.gov/documentation/services-web-api | Open data, rate limit, User-Agent | 2026-11-24 | P |
| NWS API | https://api.weather.gov/ | Responses and headers | 2026-11-24 | P |
| AviationWeather Data API | https://aviationweather.gov/data/api/ | Usage, cache files; METAR response headers | 2026-11-24 | P |
| RainViewer API | https://www.rainviewer.com/api.html ; /api/weather-maps-api.html | Terms of use, FAQ, frames, zoom, attribution | 2026-11-24 | P |
| Bright Sky | https://api.brightsky.dev/current_weather | Response and headers only | 2026-11-24 | P (response) |
| three.js Sky.js r186 | https://raw.githubusercontent.com/mrdoob/three.js/r186/examples/jsm/objects/Sky.js | Whole file; npm 0.186.1 copy identical | 2026-11-24 | P |
| three.js SkyMesh.js r186 | .../examples/jsm/objects/SkyMesh.js | Uniforms, cloud code | 2026-11-24 | P |
| three.js licence | .../r186/LICENSE ; runtime/three/0.186.1/LICENSE | MIT | 2026-11-24 | P |
| Vendored bundle | runtime/three/0.186.1/bim-three.min.js ; tools/three/build_three.mjs | Exports, fog formula | 2026-11-24 | P |
| Hillaire 2020 | https://sebh.github.io/publications/egsr2020.pdf | Sections 5, 7; Table 2 | 2026-11-24 | P |
| Epic UnrealEngineSkyAtmosphere | https://github.com/sebh/UnrealEngineSkyAtmosphere (LICENSE) | MIT | 2026-11-24 | P |
| Bruneton precomputed scattering | https://github.com/ebruneton/precomputed_atmospheric_scattering (LICENSE) | BSD 3-clause | 2026-11-24 | P |
| takram three-geospatial | https://github.com/takram-design-engineering/three-geospatial (atmosphere, clouds READMEs, LICENSE) | Method, limits, device fps table, MIT | 2026-11-24 | P (README), S (fps) |
| webgpu-sky-atmosphere | https://github.com/JolifantoBambla/webgpu-sky-atmosphere | README, MIT | 2026-11-24 | P |
| Hillaire 2016, Frostbite sky and clouds | https://media.contentapi.ea.com/content/dam/eacom/frostbite/files/s2016-pbs-frostbite-sky-clouds-new.pdf | Sections 3.5, 5.3.1, 5.10; Tables 3, 4 | 2026-11-24 | P |
| Schneider 2015, HZD clouds | https://www.guerrilla-games.com/read/the-real-time-volumetric-cloudscapes-of-horizon-zero-dawn | Abstract (2 ms target) | 2026-11-24 | S |
| Zotti, Wilkie, Purgathofer 2007 | https://www.cg.tuwien.ac.at/research/publications/2007/zotti-2007-wscg/zotti-2007-wscg-paper.pdf | Sections 2, 3, 7 | 2026-11-24 | P |
| WMO-No. 8 (2008), Part I ch. 9 | https://www.weather.gov/media/epz/mesonet/CWOP-WMO8.pdf | Eqs 9.5, 9.6 (MOR at 5 %) | 2026-11-24 | P |
| Wikipedia, Visibility | https://en.wikipedia.org/wiki/Visibility | Koschmieder with a 2 % threshold (3.912/b) | 2026-11-24 | S |
| GTAMods wiki, Time cycle | https://gtamods.com/wiki/Timecyc.dat | Format, interpolation, parameters, weather lists | 2026-11-24 | S |
| FiveM natives | https://github.com/citizenfx/natives (MISC/SetWeatherTypeTransition.md, SetWeatherTypeOvertimePersist.md, SetRainLevel.md, SetWindSpeed.md) | Whole files | 2026-11-24 | S |
| Advances in Real-Time Rendering 2019 | https://advances.realtimerendering.com/s2019/index.htm | Listing of the RDR2 talk only | 2026-11-24 | U (talk) |
| Lagarde, water drop 3a and 3b | https://seblagarde.wordpress.com/2013/03/19/water-drop-3a-physically-based-wet-surfaces/ ; .../2013/04/14/water-drop-3b-physically-based-wet-surfaces/ | Wet albedo theory; DoWetProcess | 2026-11-24 | P (method), S (measurements cited) |
| The app's code | files and lines in section 8 | As listed | 2026-11-24 | P |
