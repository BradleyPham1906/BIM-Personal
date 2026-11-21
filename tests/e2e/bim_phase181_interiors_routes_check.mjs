/* V181 browser check: mark a door as an exit, run routes in Analyze, set the project limit, and verify the plan overlay. */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const APP = process.env.BIM_APP_URL || 'http://127.0.0.1:8765/canvas_v10.html';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errors = [];
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', (e) => errors.push(e.message));
let pass = 0, fail = 0;
const ck = (ok, name) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name); };
const wait = () => page.waitForTimeout(250);

try {
  await page.goto(APP);
  await page.waitForTimeout(3500);
  const ready = await page.evaluate(() => {
    if (window.__a3dEnter) window.__a3dEnter();
    if (window.closePalette) window.closePalette();
    window.__a3dTestSetObjs([
      { id: 'eg-room', t: 'room', name: 'Test room', area: 16, pts: [[0, 0], [4, 0], [4, 4], [0, 4]], y: 0, pos: [0, 0, 0], layer: 'layer-0' },
      { id: 'eg-wall', t: 'solid', name: 'North wall', pos: [0, 0, 0], bim: { type: 'wall', centerline: [[0, 0], [4, 0]], thickness: 0.15, baseY: 0, height: 3 } },
      { id: 'eg-door', t: 'opening', name: 'North door', pos: [0, 0, 0], bim: { type: 'door', center: [2, 0], width: 1, hostWallId: 'eg-wall', exit: false } }
    ]);
    window.__a3dFlat(true);
    window.__a3dFit();
    window.__a3dSelectFor(['eg-door']);
    window.__a3dRefreshProps();
    const right = document.getElementById('a3d-right');
    if (right && !right.classList.contains('open')) document.querySelector('[data-a3d="rdrawer"]').click();
    return !!window.__a3dAnalyzeCards && !!document.querySelector('#a3d-canvas');
  });
  ck(ready, 'the app loads with the Analyze and canvas hooks');

  const exitField = page.locator('#a3d-propsbody input[data-propf="egressExit"]');
  ck(await exitField.count() === 1, 'Properties exposes the marked-exit checkbox on a door');
  await exitField.evaluate((e) => { e.checked = true; e.dispatchEvent(new Event('change', { bubbles: true })); });
  await wait();
  ck(await page.evaluate(() => window.__a3dState().objs.find((o) => o.id === 'eg-door').bim.exit === true), 'checking the field saves the door as an exit');

  await page.evaluate(() => { window.__a3dSelectFor([]); window.__a3dAnzView(); window.__a3dAwPick('card', 'egress'); });
  await wait();
  const panel = page.locator('#a3d-propsbody [data-awpanel="card:egress"]');
  const run = panel.locator('[data-anzact="egress:run"]');
  ck(await run.count() === 1 && await run.isEnabled(), 'Analyze shows the Circulation and exits card with Run routes');
  const hide = panel.locator('[data-anzact="egress:hide"]');
  ck(await hide.count() === 1 && !(await hide.isEnabled()), 'Hide routes is disabled before a route is drawn');
  await run.evaluate((e) => e.click());
  await wait();
  const status0 = await panel.locator('.a3d-awp-about').innerText();
  const limitField = panel.locator('[data-egress-param="limit"]');
  ck(await hide.isEnabled(), 'Hide routes is enabled while the overlay is shown');
  ck(await limitField.inputValue() === '' && await limitField.getAttribute('placeholder') === 'Not chosen', 'the project travel limit is initially unset');
  ck(/not an egress-compliance finding/.test(await panel.innerText()), 'the estimate disclaimer is visible');

  await limitField.evaluate((e) => { e.value = '10'; e.dispatchEvent(new Event('change', { bubbles: true })); });
  await wait();
  await run.evaluate((e) => e.click());
  await wait();
  const status1 = await panel.locator('.a3d-awp-about').innerText();
  ck(/1 rooms: 0 within, 0 over, 0 blocked, 1 not evaluated/.test(status0), 'routes run without inventing a travel limit');
  ck(/1 rooms: 1 within, 0 over/.test(status1), 'the owner-selected registry limit is used on rerun');

  const overlay = await page.evaluate(() => {
    window.__a3dTestPaint();
    const c = document.getElementById('a3d-canvas'), x = c.getContext('2d');
    const d = x.getImageData(0, 0, c.width, c.height).data;
    let route = 0, exit = 0;
    for (let i = 0; i < d.length; i += 4) {
      if (d[i] === 36 && d[i + 1] === 180 && d[i + 2] === 126) route++;
      if (d[i] === 255 && d[i + 1] === 191 && d[i + 2] === 71) exit++;
    }
    return { route, exit };
  });
  ck(overlay.route > 0 && overlay.exit > 0, 'the route and marked exit are drawn on the plan (' + JSON.stringify(overlay) + ')');
  await hide.evaluate((e) => e.click());
  await wait();
  ck(!(await panel.locator('[data-anzact="egress:hide"]').isEnabled()), 'hiding the routes disables Hide routes again');
  ck(errors.length === 0, 'no console errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
} finally {
  await browser.close();
}

console.log(pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
