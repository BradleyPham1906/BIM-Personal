// ws-browser-cors.cjs: the weather sources fetched from a real page in Chromium (Playwright, headless),
// from an http://127.0.0.1 origin, as the app would fetch them. A CORS refusal shows as a TypeError
// ("Failed to fetch"); a status shows when the response is readable. 2026-11-24. Data, never a suite.
// Usage: node ws-browser-cors.cjs > ws-browser-cors-results.json
const http = require('http');
const { chromium } = require('playwright');
const URLS = {
  openmeteo_forecast: 'https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current=cloud_cover,weather_code,visibility&forecast_days=1',
  openmeteo_meta: 'https://api.open-meteo.com/data/dwd_icon/static/meta.json',
  nws_observation: 'https://api.weather.gov/stations/KDCA/observations/latest',
  aviationweather_metar: 'https://aviationweather.gov/api/data/metar?ids=EGLL&format=json',
  metno_locationforecast: 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5074&lon=-0.1278',
  rainviewer_index: 'https://api.rainviewer.com/public/weather-maps.json',
  brightsky_current: 'https://api.brightsky.dev/current_weather?lat=52.52&lon=13.40'
};
(async () => {
  const srv = http.createServer((q, r) => { r.writeHead(200, { 'content-type': 'text/html' }); r.end('<!doctype html><title>t</title>'); });
  await new Promise(ok => srv.listen(0, '127.0.0.1', ok));
  const port = srv.address().port;
  const opts = {};
  const px = process.env.HTTPS_PROXY || process.env.https_proxy;
  if (px) opts.proxy = { server: px, bypass: '127.0.0.1' };
  const browser = await chromium.launch(opts);
  const ctx = await browser.newContext({ ignoreHTTPSErrors: false });
  const page = await ctx.newPage();
  await page.goto('http://127.0.0.1:' + port + '/');
  const out = { when: new Date().toISOString(), browser: browser.version(), origin: 'http://127.0.0.1:' + port, results: {} };
  for (const k of Object.keys(URLS)) {
    out.results[k] = await page.evaluate(async (u) => {
      const t0 = performance.now();
      try {
        const r = await fetch(u);
        const tx = await r.text();
        return { status: r.status, ms: Math.round(performance.now() - t0), bytes: tx.length, head: tx.slice(0, 120) };
      } catch (e) {
        return { error: String(e), ms: Math.round(performance.now() - t0) };
      }
    }, URLS[k]);
  }
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
  srv.close();
})();
