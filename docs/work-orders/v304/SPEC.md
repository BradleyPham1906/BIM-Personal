# V304 spec: Live weather, the pure part

Research: `docs/research/research-world-look.md` (parts 4.2, 11) and `docs/research/research-world-look/weather-sky.md`
(4.1 to 4.3, 4.6, 7), its experiment `docs/research/experiments/world-look/ws-weather-map.cjs`, and the independent check
in `docs/research/research-world-look/independent-check.md` (38 of 40 confirmed; MET Norway corrected). The owner's
decisions: all as the research recommends, answered 2026-11-24 ("nah u do what best"), with W8 carried out as "MET Norway
off until the owner reads and accepts its terms" (its terms require acceptance by a person, which Claude cannot give).
Implementation target: local `main`. Written by Claude, 2026-11-24.

## 1. The decisions this spec follows

- **W1** Open-Meteo's free API, treated as non-commercial while the app has no subscriptions or advertising; credited.
- **W3** Live weather when the view's time is now; the forecast for the coming hours; the archive (already used by the
  climate board) for a past date; the chosen preset otherwise.
- **W6, W8** The fallback order: Open-Meteo, then MET Norway only once the owner has accepted its terms, then the cached
  answer, then climate normals, then the chosen preset.
- One request per site per hour (models update every 1 to 6 hours for those named), in Unix time (daylight saving and
  fractional zones), metres per second, coordinates to 4 decimals; 15-minute steps 2 hours back and 24 hours ahead.
- Fog from visibility by WMO-No. 8's meteorological optical range: sigma = ln 20 / V (5 % contrast); a visibility of 0
  is dense fog, null is missing.
- Blending toward a new state is frame-rate independent: x += (target - x)(1 - exp(-dt / tau)).

## 2. What it does for the user

Nothing visible yet: V304 gives the rendered view a WeatherState from live data, and V305 draws it (the sky, fog, wet
surfaces). Claude's C-13 adds the fetch, the consent (W2), the credits (W7) and storage with the project.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/weather/weather-state.js` | new, after `js/engine/site/sun-position.js` in `src/index.html` (header done) | 13 pure functions in 12 work orders (part 5) | Cline, WO-01 to WO-12 |
| `docs/work-orders/v304/v304.test.mjs` | new | their tests (12 cases) | Claude (done) |
| the app's own files | changed | the fetch, consent, credits, storage, the Analyze/rendered view's control | Claude, C-13 |

## 4. Units

Visibility m, sigma 1/m, precipitation mm (per step) and mm/h, wind m/s and degrees from north (the direction it blows
from), snow depth m, time s (Unix seconds in the answer), ms in `bimWxDue`.

## 5. Functions, `src/js/engine/weather/weather-state.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function
may use an earlier one of this file, as its task says. "A number" means `typeof x === 'number'` and finite.

- **WO-01** `BIM_WX_WMO` (a table just above the function) and `bimWxWmo(code)`: WMO 4677 codes as Open-Meteo reports
  them, each [kind, intensity, flag]: 0, 1, 2, 3 none 0; 45, 48 none 0 fog; 51 drizzle 0.15, 53 drizzle 0.25, 55 drizzle
  0.35; 56 freezing 0.2, 57 freezing 0.4; 61 rain 0.3, 63 rain 0.6, 65 rain 0.9; 66 freezing 0.4, 67 freezing 0.8; 71 snow
  0.3, 73 snow 0.6, 75 snow 0.9, 77 snow 0.2; 80 rain 0.4, 81 rain 0.7, 82 rain 1; 85 snow 0.4, 86 snow 0.9; 95 rain 0.8
  thunder; 96 hail 0.8 thunder; 97 rain 1 thunder; 99 hail 1 thunder. Returns {kind, intensity, fog, thunder, known:
  true}; for anything else (another number, a string, null) {kind: 'none', intensity: 0, fog: false, thunder: false,
  known: false}.
- **WO-02** `bimWxRate(mmh)`: 0 unless mmh is a number above 0; else clamp(ln(mmh / 0.1) / ln(500), 0, 1).
- **WO-03** `bimWxFog(vis)`: V = vis clamped to 20 .. 100000 when vis is a number (0 becomes 20: dense fog), else 50000;
  returns {vis: V, sigma: ln(20) / V, exp2: sqrt(ln 20) / V} (exp2: three.js FogExp2's density for the same distance).
- **WO-04** `bimWxClouds(v)`: from v.cloud_cover, v.cloud_cover_low, _mid, _high (percent, each used only when a number):
  low = the low layer, else the total, else 0; mid and high else 0; each /100 clamped 0..1; coverage = total/100 clamped
  when the total is a number, else 1 - (1 - low)(1 - mid)(1 - high); density = clamp(0.3 + 0.6 low, 0, 1); overcast =
  clamp((coverage - 0.6) / 0.4, 0, 1). Returns {coverage, low, mid, high, density, overcast}.
- **WO-05** `bimWxState(v, stepHours)`: the WeatherState of one sample v (Open-Meteo names) whose precipitation is the
  amount over stepHours (default 1 when not above 0): w = bimWxWmo(v.weather_code), f = bimWxFog(v.visibility),
  c = bimWxClouds(v); rate = v.precipitation / stepHours when a number above 0, else 0; intensity = max(w.intensity times
  (1 when rate > 0 or the code is unknown, else 0.6), bimWxRate(rate)); snowy when w.kind is 'snow', or v.snowfall > 0
  and v.rain is not above 0. Returns {cloudCoverage, cloudLow, cloudMid, cloudHigh, cloudDensity, overcast (from c), vis,
  fogSigma, fogExp2 (from f), fog: w.fog, precipKind: 'none' when intensity is 0, else 'snow' when snowy, else 'rain'
  when w.kind is 'none', else w.kind; precipIntensity, thunder: w.thunder, windSpeed: v.wind_speed_10m or 0, windFrom:
  v.wind_direction_10m or 0, gust: v.wind_gusts_10m or windSpeed, snowCover: clamp(v.snow_depth / 0.05, 0, 1) or 0,
  codeKnown: w.known}.
- **WO-06** `bimWxBlend(x, target, dt, tau)`: target when tau is not above 0; else x + (target - x)(1 - exp(-dt / tau)).
  `bimWxAngleBlend(a, b, dt, tau)`: degrees, the short way: d = ((b - a) mod 360 + 540) mod 360 - 180; a + d times the
  same factor (1 when tau is not above 0), wrapped to [0, 360).
- **WO-07** `bimWxBlendState(s, t, dt, tau)`: a new object with every field of t; when s is given, the numbers
  cloudCoverage, cloudLow, cloudMid, cloudHigh, cloudDensity, overcast, fogSigma, precipIntensity, windSpeed, gust and
  snowCover blended by bimWxBlend, windFrom by bimWxAngleBlend, then vis = ln(20) / fogSigma and fogExp2 = sqrt(ln 20) /
  vis; the other fields (precipKind, thunder, fog, codeKnown) are t's.
- **WO-08** `bimWxWetness(wet, intensity, dt)`: while intensity > 0 it moves toward 1 with tau = 600 / max(intensity,
  0.1) s; otherwise toward 0 with tau = 10800 s: wet + (goal - wet)(1 - exp(-dt / tau)).
- **WO-09** `bimWxUrl(lat, lon)`: null unless both are numbers, -90 <= lat <= 90 and -180 <= lon <= 180; else exactly
  `https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&minutely_15=precipitation,rain,snowfall,weather_code,visibility,wind_speed_10m,wind_direction_10m,wind_gusts_10m&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,snow_depth&past_minutely_15=8&forecast_minutely_15=96&forecast_days=2&timeformat=unixtime&wind_speed_unit=ms`
  with each coordinate as String(Math.round(x * 1e4) / 1e4).
- **WO-10** `bimWxSample(resp, t)`: the sample at Unix second t from an Open-Meteo answer: null unless resp.minutely_15.time
  is a non-empty array with time[0] <= t <= its last; i the last step with time[i] <= t; for precipitation, rain,
  snowfall, visibility, wind_speed_10m and wind_gusts_10m the linear interpolation between steps i and i+1 (the value of
  step i when t is exactly on it or i is the last; null when a value needed is not a number); wind_direction_10m the
  same the short way round (as WO-06); weather_code that of step i; the hourly cloud_cover, cloud_cover_low, _mid, _high
  and snow_depth interpolated the same way on resp.hourly.time (null when absent or outside); stepHours 0.25.
- **WO-11** `bimWxDue(cache, nowMs)`: false while cache.retryAt (a number, ms) is after nowMs (a 429's Retry-After);
  else true when there is no cache or no cache.fetchedAt; else true when nowMs - cache.fetchedAt >= 3600000.
- **WO-12** `bimWxSource(o)`: the source to use, in order: 'open-meteo' when o.omOk; 'met-norway' when o.metAccepted and
  o.metOk (W8: only after the owner accepts its terms); 'cache' when o.cacheCovers; 'normals' when o.hasNormals; else
  'preset' (also for no argument).

## 6. Order of the work

WO-01 to WO-12 in order. Then Claude: **C-13** the wiring: a fetch only while the rendered view is open, visible and
"Live weather" is on, after a one-time consent per project (W2); the answer kept with the project; a 429's Retry-After
stored as cache.retryAt; one live request to confirm the parameters answer (the research's machine was rate-limited);
the state blended each frame (tau 20 s for clouds and fog, 5 s for rain); the credit "Weather data by Open-Meteo.com"
with its link while live weather is on (W7); MET Norway left off until the owner accepts its terms (W8); then the tests
to `tests/unit/`, `npm run modules`, the build and the records. V305 draws the state (the sky, fog, wet surfaces).

## 7. Not in this phase

Drawing anything (V305, V306); MET Norway's request and mapping (after W8); climate normals as a fallback source (the
climate board has the archive; a normals summary is C-13's or later); radar tiles.
