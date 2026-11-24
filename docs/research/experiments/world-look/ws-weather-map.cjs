// ws-weather-map.cjs: the proposed mapping from live weather variables to a WeatherState vector, and its blending
// rule, checked on edge cases. Our own arithmetic; no network. 2026-11-24. Data, never a suite.
// Usage: node ws-weather-map.cjs > ws-weather-map-results.json
'use strict';
const LN20 = Math.log(20); // WMO-No. 8 (2008) I.9 eq. 9.6: MOR P = ln(1/0.05)/sigma, about 3/sigma
// WMO 4677 code (as Open-Meteo reports it) -> precipitation kind and intensity 0..1, fog flag, thunder flag
function wmo(code) {
  const T = {
    0: ['none', 0], 1: ['none', 0], 2: ['none', 0], 3: ['none', 0], 45: ['none', 0, 'fog'], 48: ['none', 0, 'fog'],
    51: ['drizzle', 0.15], 53: ['drizzle', 0.25], 55: ['drizzle', 0.35], 56: ['freezing', 0.2], 57: ['freezing', 0.4],
    61: ['rain', 0.3], 63: ['rain', 0.6], 65: ['rain', 0.9], 66: ['freezing', 0.4], 67: ['freezing', 0.8],
    71: ['snow', 0.3], 73: ['snow', 0.6], 75: ['snow', 0.9], 77: ['snow', 0.2],
    80: ['rain', 0.4], 81: ['rain', 0.7], 82: ['rain', 1.0], 85: ['snow', 0.4], 86: ['snow', 0.9],
    95: ['rain', 0.8, 'thunder'], 96: ['hail', 0.8, 'thunder'], 97: ['rain', 1.0, 'thunder'], 99: ['hail', 1.0, 'thunder']
  };
  const r = T.hasOwnProperty(code) ? T[code] : null;
  return r ? { kind: r[0], intensity: r[1], fog: r[2] === 'fog', thunder: r[2] === 'thunder', known: true } : { kind: 'none', intensity: 0, fog: false, thunder: false, known: false };
}
function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
// mm/h -> 0..1 on a log scale: 0.1 mm/h barely visible, 50 mm/h a cloudburst
function rateToIntensity(mmh) { return mmh > 0 ? clamp(Math.log10(mmh / 0.1) / Math.log10(500), 0, 1) : 0; }
function toState(v) {
  const w = wmo(v.weather_code);
  // first run mapped visibility 0 (dense fog) to the 50 km default: 0 is a value, only null or absent is missing
  const vis = (typeof v.visibility === 'number' && isFinite(v.visibility)) ? clamp(v.visibility, 20, 100000) : 50000;
  const sigma = LN20 / vis;                         // Beer-Lambert extinction, 1/m
  const exp2 = Math.sqrt(LN20) / vis;               // three.js FogExp2 density with the same 95 % at the visibility
  const low = (v.cloud_cover_low ?? v.cloud_cover ?? 0) / 100, mid = (v.cloud_cover_mid ?? 0) / 100, high = (v.cloud_cover_high ?? 0) / 100;
  const randomOverlap = 1 - (1 - low) * (1 - mid) * (1 - high);
  const total = (v.cloud_cover ?? randomOverlap * 100) / 100;
  const precipRate = (v.precipitation ?? 0) * (v._stepHours ? 1 / v._stepHours : 1);
  const intensity = Math.max(w.intensity * (precipRate > 0 || !w.known ? 1 : 0.6), rateToIntensity(precipRate));
  const snowy = w.kind === 'snow' || (v.snowfall > 0 && !(v.rain > 0));
  return {
    cloudCoverage: +total.toFixed(3), cloudLow: low, cloudMid: mid, cloudHigh: high, randomOverlap: +randomOverlap.toFixed(3),
    cloudDensity: +clamp(0.3 + 0.6 * low, 0, 1).toFixed(3),           // thick low deck reads darker than cirrus
    overcast: +clamp((total - 0.6) / 0.4, 0, 1).toFixed(3),            // sky colour toward grey as cover nears 100 %
    fogSigma: +sigma.toExponential(3), fogExp2Density: +exp2.toExponential(3), visibility_m: vis,
    precipKind: intensity > 0 ? (snowy ? 'snow' : w.kind === 'none' ? 'rain' : w.kind) : 'none', precipIntensity: +intensity.toFixed(3),
    windSpeed: v.wind_speed_10m ?? 0, windFrom: v.wind_direction_10m ?? 0, gust: v.wind_gusts_10m ?? v.wind_speed_10m ?? 0,
    thunder: w.thunder, day: v.is_day === 1, codeKnown: w.known
  };
}
// wetness: rises while it rains, dries over hours (an integrator, not a straight map)
function stepWetness(wet, precipIntensity, dtS) {
  const wetTau = 600, dryTau = 3 * 3600;              // ten minutes to soak, about three hours to dry (to be tuned)
  const target = precipIntensity > 0 ? 1 : 0, tau = precipIntensity > 0 ? wetTau / Math.max(precipIntensity, 0.1) : dryTau;
  return wet + (target - wet) * (1 - Math.exp(-dtS / tau));
}
// frame-rate independent blend toward a target: x += (target - x) * (1 - exp(-dt/tau))
function blend(x, target, dt, tau) { return x + (target - x) * (1 - Math.exp(-dt / tau)); }
const out = { when: new Date().toISOString(), cases: {}, blending: {}, wetness: {} };
const CASES = {
  clear_day: { weather_code: 0, cloud_cover: 5, cloud_cover_low: 0, cloud_cover_mid: 0, cloud_cover_high: 5, visibility: 40000, is_day: 1, wind_speed_10m: 2, wind_direction_10m: 270 },
  london_overcast_from_metar: { weather_code: 3, cloud_cover: 100, cloud_cover_low: 100, visibility: 10000, is_day: 0, wind_speed_10m: 5.1, wind_direction_10m: 100 },
  dense_fog: { weather_code: 45, cloud_cover: 100, cloud_cover_low: 100, visibility: 150, is_day: 1, wind_speed_10m: 0.5 },
  heavy_rain_showers: { weather_code: 82, cloud_cover: 90, cloud_cover_low: 70, cloud_cover_mid: 60, visibility: 3000, precipitation: 12, rain: 0, showers: 12, is_day: 1, wind_speed_10m: 9, wind_gusts_10m: 18 },
  snow: { weather_code: 73, cloud_cover: 100, cloud_cover_low: 90, visibility: 1200, precipitation: 1.4, snowfall: 1.0, rain: 0, is_day: 1, wind_speed_10m: 4 },
  thunder_hail: { weather_code: 99, cloud_cover: 100, cloud_cover_low: 80, visibility: 2000, precipitation: 20, is_day: 1, wind_speed_10m: 12, wind_gusts_10m: 25 },
  edge_unknown_code: { weather_code: 5, cloud_cover: 50, visibility: 8000 },
  edge_visibility_null: { weather_code: 2, cloud_cover: 40, visibility: null },
  edge_visibility_zero: { weather_code: 45, cloud_cover: 100, visibility: 0 },
  edge_layers_no_total: { weather_code: 2, cloud_cover_low: 50, cloud_cover_mid: 50, cloud_cover_high: 50, visibility: 20000 },
  edge_drizzle_no_amount: { weather_code: 51, cloud_cover: 100, visibility: 5000, precipitation: 0 }
};
for (const k in CASES) out.cases[k] = toState(CASES[k]);
// frame-rate independence: blend 0 -> 1 with tau 20 s for 60 s at 30, 60 and 120 frames per second, and in one 60 s step
for (const fps of [30, 60, 120]) { let x = 0; const dt = 1 / fps; for (let i = 0; i < 60 * fps; i++) x = blend(x, 1, dt, 20); out.blending['fps_' + fps] = +x.toFixed(6); }
out.blending.one_step_60s = +blend(0, 1, 60, 20).toFixed(6);
out.blending.analytic_1_minus_exp_minus3 = +(1 - Math.exp(-3)).toFixed(6);
// wetness: one hour of moderate rain, then four hours dry, sampled every 15 minutes
let wet = 0; const trace = [];
for (let m = 0; m <= 300; m += 15) { trace.push([m, +wet.toFixed(3)]); wet = stepWetness(wet, m < 60 ? 0.6 : 0, 900); }
out.wetness.rain_1h_then_dry = trace;
console.log(JSON.stringify(out, null, 1));
