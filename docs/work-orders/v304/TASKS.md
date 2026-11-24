# V304 work orders: Live weather, the pure part

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add its function (and any table its task names, just above it) to
`src/js/engine/weather/weather-state.js`, below the file's header comment and the earlier tasks' functions, and change
nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`; no
`let`, `const`, arrow functions, classes or template strings. Use only the names listed; never a name from another file.
Implement the whole function; never a placeholder. The research's `docs/research/experiments/world-look/ws-weather-map.cjs`
shows the method (read, do not import).

The tests are in `docs/work-orders/v304/v304.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v304/v304.test.mjs
    node --check src/js/engine/weather/weather-state.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `BIM_WX_WMO`, `bimWxWmo`

- **It must:** SPEC 5 WO-01:`BIM_WX_WMO` (a table just above the function) and `bimWxWmo(code)`: WMO 4677 codes as Open-Meteo reports them, each [kind, intensity, flag]: 0, 1, 2, 3 none 0; 45, 48 none 0 fog; 51 drizzle 0.15, 53 drizzle 0.25, 55 drizzle 0.35; 56 freezing 0.2, 57 freezing 0.4; 61 rain 0.3, 63 rain 0.6, 65 rain 0.9; 66 freezing 0.4, 67 freezing 0.8; 71 snow 0.3, 73 snow 0.6, 75 snow 0.9, 77 snow 0.2; 80 rain 0.4, 81 rain 0.7, 82 rain 1; 85 snow 0.4, 86 snow 0.9; 95 rain 0.8 thunder; 96 hail 0.8 thunder; 97 rain 1 thunder; 99 hail 1 thunder. Returns {kind, intensity, fog, thunder, known: true}; for anything else (another number, a string, null) {kind: 'none', intensity: 0, fog: false, thunder: false, known: false}.
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0+0+0+0+0+0 = 0.

---

## [ ] WO-02 [Cline] `bimWxRate`

- **It must:** SPEC 5 WO-02:`bimWxRate(mmh)`: 0 unless mmh is a number above 0; else clamp(ln(mmh / 0.1) / ln(500), 0, 1).
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimWxFog`

- **It must:** SPEC 5 WO-03:`bimWxFog(vis)`: V = vis clamped to 20 .. 100000 when vis is a number (0 becomes 20: dense fog), else 50000; returns {vis: V, sigma: ln(20) / V, exp2: sqrt(ln 20) / V} (exp2: three.js FogExp2's density for the same distance).
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimWxClouds`

- **It must:** SPEC 5 WO-04:`bimWxClouds(v)`: from v.cloud_cover, v.cloud_cover_low, _mid, _high (percent, each used only when a number): low = the low layer, else the total, else 0; mid and high else 0; each /100 clamped 0..1; coverage = total/100 clamped when the total is a number, else 1 - (1 - low)(1 - mid)(1 - high); density = clamp(0.3 + 0.6 low, 0, 1); overcast = clamp((coverage - 0.6) / 0.4, 0, 1). Returns {coverage, low, mid, high, density, overcast}.
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimWxState`

- **It must:** SPEC 5 WO-05:`bimWxState(v, stepHours)`: the WeatherState of one sample v (Open-Meteo names) whose precipitation is the amount over stepHours (default 1 when not above 0): w = bimWxWmo(v.weather_code), f = bimWxFog(v.visibility), c = bimWxClouds(v); rate = v.precipitation / stepHours when a number above 0, else 0; intensity = max(w.intensity times (1 when rate > 0 or the code is unknown, else 0.6), bimWxRate(rate)); snowy when w.kind is 'snow', or v.snowfall > 0 and v.rain is not above 0. Returns {cloudCoverage, cloudLow, cloudMid, cloudHigh, cloudDensity, overcast (from c), vis, fogSigma, fogExp2 (from f), fog: w.fog, precipKind: 'none' when intensity is 0, else 'snow' when snowy, else 'rain' when w.kind is 'none', else w.kind; precipIntensity, thunder: w.thunder, windSpeed: v.wind_speed_10m or 0, windFrom: v.wind_direction_10m or 0, gust: v.wind_gusts_10m or windSpeed, snowCover: clamp(v.snow_depth / 0.05, 0, 1) or 0, codeKnown: w.known}.
- **May use:** bimWxWmo (WO-01), bimWxRate (WO-02), bimWxFog (WO-03), bimWxClouds (WO-04).
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Cline] `bimWxBlend`, `bimWxAngleBlend`

- **It must:** SPEC 5 WO-06:`bimWxBlend(x, target, dt, tau)`: target when tau is not above 0; else x + (target - x)(1 - exp(-dt / tau)). `bimWxAngleBlend(a, b, dt, tau)`: degrees, the short way: d = ((b - a) mod 360 + 540) mod 360 - 180; a + d times the same factor (1 when tau is not above 0), wrapped to [0, 360).
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-07 [Cline] `bimWxBlendState`

- **It must:** SPEC 5 WO-07:`bimWxBlendState(s, t, dt, tau)`: a new object with every field of t; when s is given, the numbers cloudCoverage, cloudLow, cloudMid, cloudHigh, cloudDensity, overcast, fogSigma, precipIntensity, windSpeed, gust and snowCover blended by bimWxBlend, windFrom by bimWxAngleBlend, then vis = ln(20) / fogSigma and fogExp2 = sqrt(ln 20) / vis; the other fields (precipKind, thunder, fog, codeKnown) are t's.
- **May use:** bimWxBlend, bimWxAngleBlend (WO-06).
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bimWxWetness`

- **It must:** SPEC 5 WO-08:`bimWxWetness(wet, intensity, dt)`: while intensity > 0 it moves toward 1 with tau = 600 / max(intensity, 0.1) s; otherwise toward 0 with tau = 10800 s: wet + (goal - wet)(1 - exp(-dt / tau)).
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0.

---

## [ ] WO-09 [Cline] `bimWxUrl`

- **It must:** SPEC 5 WO-09:`bimWxUrl(lat, lon)`: null unless both are numbers, -90 <= lat <= 90 and -180 <= lon <= 180; else exactly `https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&minutely_15=precipitation,rain,snowfall,weather_code,visibility,wind_speed_10m,wind_direction_10m,wind_gusts_10m&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,snow_depth&past_minutely_15=8&forecast_minutely_15=96&forecast_days=2&timeformat=unixtime&wind_speed_unit=ms` with each coordinate as String(Math.round(x * 1e4) / 1e4).
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0.

---

## [ ] WO-10 [Cline] `bimWxSample`

- **It must:** SPEC 5 WO-10:`bimWxSample(resp, t)`: the sample at Unix second t from an Open-Meteo answer: null unless resp.minutely_15.time is a non-empty array with time[0] <= t <= its last; i the last step with time[i] <= t; for precipitation, rain, snowfall, visibility, wind_speed_10m and wind_gusts_10m the linear interpolation between steps i and i+1 (the value of step i when t is exactly on it or i is the last; null when a value needed is not a number); wind_direction_10m the same the short way round (as WO-06); weather_code that of step i; the hourly cloud_cover, cloud_cover_low, _mid, _high and snow_depth interpolated the same way on resp.hourly.time (null when absent or outside); stepHours 0.25.
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-10 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0+1+0+0+1+0 = 2.

---

## [ ] WO-11 [Cline] `bimWxDue`

- **It must:** SPEC 5 WO-11:`bimWxDue(cache, nowMs)`: false while cache.retryAt (a number, ms) is after nowMs (a 429's Retry-After); else true when there is no cache or no cache.fetchedAt; else true when nowMs - cache.fetchedAt >= 3600000.
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-11 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0.

---

## [ ] WO-12 [Cline] `bimWxSource`

- **It must:** SPEC 5 WO-12:`bimWxSource(o)`: the source to use, in order: 'open-meteo' when o.omOk; 'met-norway' when o.metAccepted and o.metOk (W8: only after the owner accepts its terms); 'cache' when o.cacheCovers; 'normals' when o.hasNormals; else 'preset' (also for no argument).
- **May use:** nothing.
- **Files:** `src/js/engine/weather/weather-state.js`, `docs/work-orders/v304/v304.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-12 ...` in `docs/work-orders/v304/v304.test.mjs`. **Score:** 0.

---

## [ ] C-13 [Claude] The wiring, consent, credits and records

- SPEC 6: the fetch while the rendered view is open, visible and live weather is on, after a one-time consent per
  project (W2); the answer kept with the project; Retry-After; one live request to confirm the parameters; the state
  blended each frame; the Open-Meteo credit (W7); MET Norway off until the owner accepts its terms (W8); the tests to
  `tests/unit/`, `npm run modules`, the build, PIPELINE, the log and Notion.
