// ws-openmeteo-full.cjs: the full set of weather variables the app would ask Open-Meteo for, fetched from a
// page in Chromium (the curl route from this machine answered 429, the browser route 200 on 2026-11-24),
// and the model metadata (last run, update interval) of the models the "best match" blends.
// Usage: node ws-openmeteo-full.cjs > ws-openmeteo-full-results.json
const http = require('http');
const { chromium } = require('playwright');
const F = 'https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278' +
  '&current=temperature_2m,relative_humidity_2m,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,' +
  'cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_direction_10m,wind_gusts_10m' +
  '&minutely_15=precipitation,rain,snowfall,weather_code,visibility,wind_speed_10m,wind_gusts_10m,is_day' +
  '&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,weather_code,precipitation_probability' +
  '&forecast_days=1&forecast_minutely_15=8&timezone=auto&wind_speed_unit=ms';
const MODELS = ['dwd_icon', 'dwd_icon_eu', 'dwd_icon_d2', 'ecmwf_ifs025', 'ncep_gfs013', 'ncep_hrrr_conus', 'ukmo_global_deterministic_10km', 'ukmo_uk_deterministic_2km', 'meteofrance_arome_france_hd', 'knmi_harmonie_arome_europe'];
(async () => {
  const srv = http.createServer((q, r) => { r.writeHead(200, { 'content-type': 'text/html' }); r.end('<!doctype html><title>t</title>'); });
  await new Promise(ok => srv.listen(0, '127.0.0.1', ok));
  const opts = {};
  const px = process.env.HTTPS_PROXY || process.env.https_proxy;
  if (px) opts.proxy = { server: px, bypass: '127.0.0.1' };
  const browser = await chromium.launch(opts);
  const page = await (await browser.newContext()).newPage();
  await page.goto('http://127.0.0.1:' + srv.address().port + '/');
  const get = (u) => page.evaluate(async (u) => {
    try { const r = await fetch(u); const h = {}; r.headers.forEach((v, k) => { h[k] = v; }); return { status: r.status, headers: h, body: await r.text() }; }
    catch (e) { return { error: String(e) }; }
  }, u);
  const out = { when: new Date().toISOString(), forecast: null, meta: {} };
  const f = await get(F);
  try { f.json = JSON.parse(f.body); delete f.body; } catch (e) { }
  out.forecast = f;
  for (const m of MODELS) {
    const r = await get('https://api.open-meteo.com/data/' + m + '/static/meta.json');
    let j = null; try { j = JSON.parse(r.body); } catch (e) { }
    out.meta[m] = j ? {
      status: r.status,
      last_run_initialisation_time: j.last_run_initialisation_time && new Date(j.last_run_initialisation_time * 1000).toISOString(),
      last_run_availability_time: j.last_run_availability_time && new Date(j.last_run_availability_time * 1000).toISOString(),
      update_interval_seconds: j.update_interval_seconds, temporal_resolution_seconds: j.temporal_resolution_seconds
    } : { status: r.status, error: r.error };
  }
  console.log(JSON.stringify(out, null, 1));
  await browser.close(); srv.close();
})();
