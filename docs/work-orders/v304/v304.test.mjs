/* V304's work-order tests (docs/work-orders/v304/SPEC.md): the pure functions of src/js/engine/weather/weather-state.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v304/v304.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v304/v304.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text.
   Expected numbers come from closed forms, WMO-No. 8 (visibility) and the research's experiment
   (docs/research/experiments/world-look/ws-weather-map-results.json), not from the implementation. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ['bimWxWmo', 'bimWxRate', 'bimWxFog', 'bimWxClouds', 'bimWxState', 'bimWxBlend', 'bimWxAngleBlend',
  'bimWxBlendState', 'bimWxWetness', 'bimWxUrl', 'bimWxSample', 'bimWxDue', 'bimWxSource'];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/weather/weather-state.js'), 'utf8');
  if (process.env.V304_REF) src += fs.readFileSync(process.env.V304_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/weather/weather-state.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-12 : e), (m || '') + ' ' + a + ' is not ' + b);
const L20 = Math.log(20);

test('WO-01 WMO 4677 codes: kind, intensity, fog and thunder flags; unknown codes flagged', () => {
  const w = fn('bimWxWmo');
  assert.deepEqual(w(0), { kind: 'none', intensity: 0, fog: false, thunder: false, known: true });
  assert.deepEqual(w(45), { kind: 'none', intensity: 0, fog: true, thunder: false, known: true });
  assert.deepEqual(w(55), { kind: 'drizzle', intensity: 0.35, fog: false, thunder: false, known: true });
  assert.deepEqual(w(67), { kind: 'freezing', intensity: 0.8, fog: false, thunder: false, known: true });
  assert.deepEqual(w(75), { kind: 'snow', intensity: 0.9, fog: false, thunder: false, known: true });
  assert.deepEqual(w(82), { kind: 'rain', intensity: 1, fog: false, thunder: false, known: true });
  assert.deepEqual(w(96), { kind: 'hail', intensity: 0.8, fog: false, thunder: true, known: true });
  assert.deepEqual(w(95), { kind: 'rain', intensity: 0.8, fog: false, thunder: true, known: true });
  [5, 50, 100, -1, null, '61', NaN, undefined].forEach((c) => assert.deepEqual(w(c), { kind: 'none', intensity: 0, fog: false, thunder: false, known: false }, String(c)));
});

test('WO-02 precipitation rate to intensity on a log scale: 0.1 mm/h is zero, 50 mm/h is one', () => {
  const r = fn('bimWxRate');
  near(r(0.1), 0); near(r(50), 1); near(r(1), 1 / Math.log10(500), 1e-12); near(r(500), 1, 0, 'clamped above');
  assert.equal(r(0.05), 0, 'clamped below'); assert.equal(r(0), 0); assert.equal(r(-3), 0); assert.equal(r(null), 0); assert.equal(r('5'), 0);
});

test('WO-03 fog from visibility (WMO MOR, 5 % contrast): sigma = ln 20 / V; 0 is dense fog, null is missing', () => {
  const f = fn('bimWxFog');
  const a = f(40000); near(a.vis, 40000); near(a.sigma, 7.489e-5, 5e-9, 'the experiment\'s clear day'); near(a.exp2, Math.sqrt(L20) / 40000);
  near(f(150).sigma, 0.01997, 5e-6, 'dense fog');
  near(f(0).vis, 20, 0, 'a visibility of 0 is a value: dense fog, clamped to 20 m');
  near(f(null).vis, 50000, 0, 'missing: 50 km'); near(f(undefined).vis, 50000); near(f(NaN).vis, 50000);
  near(f(1e7).vis, 100000, 0, 'clamped to 100 km');
});

test('WO-04 clouds: total and layers, random overlap when the total is absent, density and overcast', () => {
  const c = fn('bimWxClouds');
  const a = c({ cloud_cover: 90, cloud_cover_low: 70, cloud_cover_mid: 60 });
  near(a.coverage, 0.9); near(a.low, 0.7); near(a.mid, 0.6); near(a.high, 0); near(a.density, 0.72, 1e-12); near(a.overcast, 0.75, 1e-12);
  const b = c({ cloud_cover_low: 50, cloud_cover_mid: 50, cloud_cover_high: 50 });
  near(b.coverage, 0.875, 1e-12, 'random overlap 1 - 0.5^3');
  const d = c({ cloud_cover: 40 }); near(d.low, 0.4, 1e-12, 'low falls back to the total'); near(d.overcast, 0);
  const e = c({}); near(e.coverage, 0); near(e.density, 0.3, 1e-12);
  near(c({ cloud_cover: 140 }).coverage, 1, 0, 'clamped');
});

test('WO-05 the WeatherState: the research\'s cases (heavy showers, snow, thunder with hail, drizzle with no amount)', () => {
  const s = fn('bimWxState');
  const r = s({ weather_code: 82, cloud_cover: 90, cloud_cover_low: 70, cloud_cover_mid: 60, visibility: 3000, precipitation: 12, rain: 0, showers: 12, wind_speed_10m: 9, wind_gusts_10m: 18, wind_direction_10m: 225 }, 1);
  assert.equal(r.precipKind, 'rain'); near(r.precipIntensity, 1); near(r.fogSigma, L20 / 3000, 1e-15); near(r.windSpeed, 9); near(r.gust, 18); near(r.windFrom, 225); assert.equal(r.thunder, false);
  const sn = s({ weather_code: 73, cloud_cover: 100, visibility: 1200, precipitation: 1.4, snowfall: 1.0, rain: 0, snow_depth: 0.02 }, 1);
  assert.equal(sn.precipKind, 'snow'); near(sn.precipIntensity, 0.6, 1e-12, 'the code\'s level wins over 1.4 mm/h'); near(sn.snowCover, 0.4, 1e-12);
  const th = s({ weather_code: 99, cloud_cover: 100, precipitation: 20, visibility: 2000, wind_speed_10m: 12 }, 1);
  assert.equal(th.precipKind, 'hail'); assert.equal(th.thunder, true); near(th.gust, 12, 0, 'gust defaults to the wind speed');
  const dz = s({ weather_code: 51, cloud_cover: 100, visibility: 5000, precipitation: 0 }, 1);
  assert.equal(dz.precipKind, 'drizzle'); near(dz.precipIntensity, 0.09, 1e-12, 'a known code with no amount: 0.6 of its level');
  const q = s({ weather_code: 61, precipitation: 0.5, rain: 0.5 }, 0.25);
  near(q.precipIntensity, Math.log10(20) / Math.log10(500), 1e-12, '0.5 mm in 15 minutes is 2 mm/h');
  const u = s({ weather_code: 5, cloud_cover: 50, visibility: 8000 }, 1);
  assert.equal(u.codeKnown, false); assert.equal(u.precipKind, 'none');
  const rn = s({ weather_code: 3, precipitation: 3 }, 1); assert.equal(rn.precipKind, 'rain', 'an amount with a dry code is rain');
  const sf = s({ weather_code: 3, precipitation: 1, snowfall: 0.7 }, 1); assert.equal(sf.precipKind, 'snow', 'snowfall without rain is snow');
  const fg = s({ weather_code: 45, visibility: 0 }, 1); assert.equal(fg.fog, true); near(fg.vis, 20);
});

test('WO-06 blending is frame-rate independent (e: 0.950213 at 30, 60 and 120 fps), and angles take the short way', () => {
  const b = fn('bimWxBlend');
  [30, 60, 120].forEach((fps) => { let x = 0; for (let i = 0; i < 60 * fps; i++) x = b(x, 1, 1 / fps, 20); near(x, 0.950213, 1e-6, fps + ' fps'); });
  near(b(0, 1, 60, 20), 1 - Math.exp(-3), 1e-15, 'one 60 s step'); near(b(3, 7, 1, 0), 7, 0, 'tau 0 jumps');
  const a = fn('bimWxAngleBlend');
  near(a(350, 10, 1, 0), 10, 1e-12); near(a(350, 10, Math.log(2), 1), 0, 1e-12, 'halfway from 350 to 10 is 0, not 180');
  near(a(10, 350, Math.log(2), 1), 0, 1e-12); near(a(90, 270, 0, 5), 90, 1e-12);
});

test('WO-07 blending a whole state: numbers ease, the wind turns the short way, fog eases in sigma, kinds switch', () => {
  const bs = fn('bimWxBlendState'), s = fn('bimWxState');
  const A = s({ weather_code: 0, cloud_cover: 0, visibility: 40000, wind_speed_10m: 2, wind_direction_10m: 350 }, 1);
  const B = s({ weather_code: 63, cloud_cover: 100, visibility: 2000, precipitation: 4, wind_speed_10m: 8, wind_direction_10m: 30 }, 1);
  const h = bs(A, B, Math.log(2), 1);
  near(h.cloudCoverage, 0.5, 1e-12); near(h.windSpeed, 5, 1e-12); near(h.windFrom, 10, 1e-12, 'from 350 to 30 by way of north');
  near(h.fogSigma, (A.fogSigma + B.fogSigma) / 2, 1e-15); near(h.vis, L20 / h.fogSigma, 1e-9); near(h.fogExp2, Math.sqrt(L20) / h.vis, 1e-15);
  assert.equal(h.precipKind, 'rain', 'the kind switches to the target'); near(h.precipIntensity, B.precipIntensity / 2, 1e-12);
  assert.deepEqual(bs(null, B, 1, 1), B, 'no previous state: the target');
  assert.equal(A.cloudCoverage, 0, 'the inputs are not changed');
});

test('WO-08 wetness soaks in about ten minutes of rain and dries over hours', () => {
  const w = fn('bimWxWetness');
  near(w(0, 0.6, 900), 1 - Math.exp(-0.9), 1e-12, '15 minutes at intensity 0.6: tau 1000 s');
  near(w(1, 0, 10800), Math.exp(-1), 1e-12, 'three hours dry: tau 3 h'); near(w(0.5, 0.01, 60), 0.5 + 0.5 * (1 - Math.exp(-0.01)), 1e-12, 'a trace of rain soaks at most as slowly as intensity 0.1');
  near(w(0, 0, 100), 0);
});

test('WO-09 the request: Unix time, metres per second, 15-minute steps 2 h back and 24 h ahead, coordinates to 4 decimals', () => {
  const u = fn('bimWxUrl')(51.507351, -0.127758);
  assert.equal(u, 'https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278' +
    '&minutely_15=precipitation,rain,snowfall,weather_code,visibility,wind_speed_10m,wind_direction_10m,wind_gusts_10m' +
    '&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,snow_depth' +
    '&past_minutely_15=8&forecast_minutely_15=96&forecast_days=2&timeformat=unixtime&wind_speed_unit=ms');
  assert.ok(fn('bimWxUrl')(-33.86882, 151.20929).indexOf('latitude=-33.8688&longitude=151.2093&') > 0, 'south and east');
  assert.equal(fn('bimWxUrl')(91, 0), null); assert.equal(fn('bimWxUrl')(0, 181), null); assert.equal(fn('bimWxUrl')('51', 0), null);
});

test('WO-10 a sample at a moment: linear between 15-minute steps, the code held, the wind the short way, hourly clouds', () => {
  const R = { minutely_15: { time: [0, 900, 1800], precipitation: [0, 1, 2], rain: [0, 1, null], snowfall: [0, 0, 0], weather_code: [3, 61, 63],
    visibility: [10000, 8000, 6000], wind_speed_10m: [2, 4, 6], wind_direction_10m: [350, 30, 60], wind_gusts_10m: [3, 5, 7] },
    hourly: { time: [0, 3600], cloud_cover: [40, 80], cloud_cover_low: [20, 60], cloud_cover_mid: [0, 0], cloud_cover_high: [10, 10], snow_depth: [0, 0] } };
  const s = fn('bimWxSample'), a = s(R, 450);
  near(a.precipitation, 0.5, 1e-12); near(a.visibility, 9000, 1e-9); near(a.wind_speed_10m, 3, 1e-12); near(a.wind_direction_10m, 10, 1e-12, 'by way of north');
  assert.equal(a.weather_code, 3, 'the step at or before'); near(a.cloud_cover, 45, 1e-12, 'hourly, interpolated'); near(a.stepHours, 0.25);
  assert.equal(s(R, 1350).rain, null, 'a null neighbour gives null, not a guess'); assert.equal(s(R, 1800).weather_code, 63, 'the last step exactly');
  near(s(R, 900).precipitation, 1, 0, 'on a step');
  assert.equal(s(R, -1), null); assert.equal(s(R, 1801), null); assert.equal(s({}, 0), null); assert.equal(s(null, 0), null);
});

test('WO-11 when to fetch: no answer yet, or an hour old, but never before Retry-After', () => {
  const d = fn('bimWxDue'), H = 3600000;
  assert.equal(d(null, 5), true); assert.equal(d({ fetchedAt: 0 }, H - 1), false); assert.equal(d({ fetchedAt: 0 }, H), true);
  assert.equal(d({ fetchedAt: 0, retryAt: 2 * H }, 1.5 * H), false, 'a 429 waits for Retry-After'); assert.equal(d({ fetchedAt: 0, retryAt: 2 * H }, 2 * H), true);
  assert.equal(d({ retryAt: 10 }, 5), false, 'refused before the first answer'); assert.equal(d({ retryAt: 10 }, 11), true);
});

test('WO-12 the source, in the owner\'s order: Open-Meteo, MET Norway (only once its terms are accepted), cache, normals, preset', () => {
  const s = fn('bimWxSource');
  assert.equal(s({ omOk: true, metAccepted: true, metOk: true }), 'open-meteo');
  assert.equal(s({ omOk: false, metAccepted: true, metOk: true, cacheCovers: true }), 'met-norway');
  assert.equal(s({ omOk: false, metAccepted: false, metOk: true, cacheCovers: true }), 'cache', 'MET Norway is off until the owner accepts its terms (W8)');
  assert.equal(s({ omOk: false, metAccepted: true, metOk: false, cacheCovers: false, hasNormals: true }), 'normals');
  assert.equal(s({}), 'preset'); assert.equal(s(), 'preset');
});
