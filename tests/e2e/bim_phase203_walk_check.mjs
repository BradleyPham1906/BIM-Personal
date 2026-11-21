/* bim_phase203_walk_check.mjs -- V203's browser check (docs/work-orders/v203/TASKS.md, C-08): WALK on a small
   course, driven by the page's own events (the DevTools protocol's keys, mouse and touches), not by hooks:
   a floor, a wall ahead, a stair of 180 mm risers, a 400 mm curb; then third person, fly, through walls, the rendered
   view while walking, Esc, and a phone's joystick. __a3dWalk only reads the walk and places the walker for a case.

   It drives any Chromium through the DevTools protocol with Node's own WebSocket, no dependencies. To run it:
     python3 -m http.server 8765 --bind 127.0.0.1                       (from the repository's root)
     chromium --headless=new --remote-debugging-port=9339 --user-data-dir=<a NEW empty folder> about:blank
     node tests/e2e/bim_phase203_walk_check.mjs <a folder for the screenshots> */
import fs from 'node:fs';
const PORT = +(process.env.CDP_PORT || 9339), APP = (process.env.APP_BASE || 'http://127.0.0.1:8765') + '/canvas_v10.html', OUT = process.argv[2] || '.';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' }); return await r.json(); } catch (e) { await sleep(250); }
  }
  throw new Error('no browser on port ' + PORT);
}
async function connect(t) {
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const wait = {}, ev = [];
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait[d.id]) { wait[d.id](d); delete wait[d.id]; } else ev.push(d); };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; wait[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, ev, ws };
}
const C = await connect(await target());
await C.send('Runtime.enable'); await C.send('Log.enable'); await C.send('Page.enable');
await C.send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 900, deviceScaleFactor: 1, mobile: false });
async function ev(expr) {
  const r = await C.send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true, userGesture: true });
  if (r.result.exceptionDetails) return { __err: (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text).slice(0, 400) };
  return r.result.result.value;
}
let pass = 0, fail = 0;
function ck(ok, msg) { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + msg); }
async function shot(name) { const r = await C.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64')); }
const KEYS = { KeyW: ['w', 87], KeyA: ['a', 65], KeyS: ['s', 83], KeyD: ['d', 68], KeyV: ['v', 86], KeyF: ['f', 70], KeyC: ['c', 67],
  Space: [' ', 32], AltLeft: ['Alt', 18], Escape: ['Escape', 27], ShiftLeft: ['Shift', 16] };
async function key(code, type) { const k = KEYS[code]; await C.send('Input.dispatchKeyEvent', { type, code, key: k[0], windowsVirtualKeyCode: k[1] }); }
async function hold(code, ms) { await key(code, 'keyDown'); await sleep(ms); await key(code, 'keyUp'); }
async function tap(code) { await key(code, 'keyDown'); await key(code, 'keyUp'); }
const state = () => ev('return window.__a3dWalk.state();');
async function place(p, yaw) { await ev(`window.__a3dWalk.place(${JSON.stringify(p)},${yaw});`); await sleep(500); }

await C.send('Page.navigate', { url: APP });
await sleep(5000);
let r = await ev('return window.__acad3dV203||null;');
ck(r && /walk/.test(r), 'the V203 marker (' + r + ')');

// the course: the floor's top at 0; a wall across at z = -6; a stair (1 m treads, 180 mm risers) at x = 10; a 400 mm curb at x = 20
r = await ev(`window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');window.__a3dSelectFor([]);
  window.__a3dColumnAt([10,-5],-0.3,50,40,0.3);
  const w=window.__a3dCurvedWall([[-5,-6],[5,-6]],null,0.3,3,'center',false);
  window.__a3dColumnAt([10,-2],0,2,1,0.18);window.__a3dColumnAt([10,-3],0,2,1,0.36);window.__a3dColumnAt([10,-5.5],0,2,4,0.54);
  window.__a3dColumnAt([20,-2],0,2,1,0.4);
  window.__a3dSelectFor([]);window.__a3dCamSet({tx:0,ty:1,tz:0,yaw:0,pitch:0.3,dist:12});return w;`);
ck(typeof r === 'string', 'the course is drawn (' + JSON.stringify(r) + ')');

// WALK from the command line, as a user types it
await ev(`window.__a3dRunCmd('walk');`);
r = await ev(`const t0=Date.now();let s;for(;;){s=window.__a3dWalk.state();if(s.on||s.err||Date.now()-t0>30000)break;await new Promise(r=>setTimeout(r,200));}return s;`);
ck(r && r.on && !r.err, 'WALK starts: Jolt loaded, the model in it (' + JSON.stringify(r && { on: r.on, st: r.st, err: r.err, tris: r.tris }) + ')');
ck(r && Math.abs(r.p[1]) < 0.05 && r.tris > 20, 'the walker stands on the floor below the view\'s focus (y ' + (r && r.p[1].toFixed(3)) + ')');
ck(r && Math.abs(r.cam.ty - (r.p[1] + r.cap.eye - Math.sin(r.cam.pitch))) < 0.05 && r.cam.dist === 1 && !r.flat, 'the camera is the walker\'s eyes, in perspective (eye ' + (r && r.cap.eye) + ')');
ck(await ev(`return getComputedStyle(document.querySelector('.a3d-walkbar')).display;`) === 'flex', 'the bar is shown: Leave, the view, Walk or Fly, Through walls');
await shot('203-walk-first');

// a wall stops them
await place([0, 0.01, 0], 0);
await hold('KeyW', 6000);
r = await state();
ck(r.p[2] > -6 + 0.15 && r.p[2] < -5, 'walking at the wall (W), they stop at it (z ' + r.p[2].toFixed(3) + ', the wall\'s face at -5.85)');
ck(Math.abs(r.p[1]) < 0.05, 'still on the floor');

// a stair of 180 mm risers is climbed
await place([10, 0.01, 0], 0);
await hold('KeyW', 4000);
r = await state();
ck(r.p[1] > 0.5 && r.p[2] < -4, 'up a stair of 180 mm risers to its landing at 0.54 m (y ' + r.p[1].toFixed(3) + ', z ' + r.p[2].toFixed(3) + ')');

// a 400 mm curb is not
await place([20, 0.01, 0], 0);
await hold('KeyW', 3000);
r = await state();
ck(r.p[1] < 0.1 && r.p[2] > -1.5, 'a 400 mm curb stops them: higher than a code step (y ' + r.p[1].toFixed(3) + ', z ' + r.p[2].toFixed(3) + ')');

// through walls while Alt is held
await place([0, 0.01, 0], 0);
await key('AltLeft', 'keyDown'); await hold('KeyW', 9000); await key('AltLeft', 'keyUp');
r = await state();
ck(r.p[2] < -6.4, 'with Alt held they pass through the wall (z ' + r.p[2].toFixed(3) + ')');

// third person: the figure, the boom
await place([0, 0.01, 0], 0);
await tap('KeyV'); await sleep(400);
r = await state();
ck(r.view === 'third' && r.extra.length === 1 && r.cam.dist > 0.3 && r.cam.dist <= 3.01, 'V: third person, the figure drawn, the camera on its boom (' + JSON.stringify({ view: r.view, extra: r.extra, dist: r.cam.dist }) + ')');
await shot('203-walk-third');
r = await ev(`return window.__a3dObjIds?window.__a3dObjIds():null;`);
ck(!Array.isArray(r) || r.indexOf('a3d-walker') < 0, 'the figure is not in the model');
await tap('KeyV'); await sleep(300);

// fly: Space rises, F back to walking
await place([0, 0.01, 0], 0);
await tap('KeyF'); await sleep(200);
await hold('Space', 1500);
r = await state();
ck(r.mode === 'fly' && r.p[1] > 1, 'F flies; Space rises (y ' + r.p[1].toFixed(3) + ')');
await tap('KeyF'); await sleep(2500);
r = await state();
ck(r.mode === 'walk' && Math.abs(r.p[1]) < 0.05, 'F again walks: gravity brings them down (y ' + r.p[1].toFixed(3) + ')');

// the mouse looks (a drag, without the pointer lock headless Chromium may refuse)
const y0 = r.yaw;
await C.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: 700, y: 450, button: 'left', clickCount: 1 });
for (let i = 1; i <= 5; i++) await C.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 700 + i * 20, y: 450, button: 'left', buttons: 1 });
await C.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: 800, y: 450, button: 'left', clickCount: 1 });
await sleep(300);
r = await state();
ck(Math.abs(r.yaw - y0) > 0.1, 'a drag on the view turns them (yaw ' + y0.toFixed(3) + ' to ' + r.yaw.toFixed(3) + ')');
ck(await ev(`return window.__a3dSelected?(window.__a3dSelected()||null):null;`) === null, 'and picks nothing: the view\'s own handlers are held back');

// the rendered view while walking: one pass a frame, more when still
r = await ev(`const s=await window.__a3dRendered(true);return s;`);
await place([0, 0.01, -2], 0);
await hold('KeyS', 800);
r = await ev(`const t0=Date.now();let s;for(;;){s=window.__a3dRendered();if(s.done>=6||s.err||Date.now()-t0>15000)break;await new Promise(r=>setTimeout(r,200));}return s;`);
ck(r && r.on && !r.err && r.done >= 6, 'the rendered view walks too, refining when still (' + JSON.stringify(r && { done: r.done, err: r.err }) + ')');
await shot('203-walk-rendered');
await ev('await window.__a3dRendered(false);');

// Esc leaves, the camera back where it was. With the pointer locked, the first Esc is the browser's (it lets the
// pointer go; headless Chromium does not, so the page is asked to), the next one leaves
if (await ev('return !!document.pointerLockElement;')) { await ev('document.exitPointerLock();'); await sleep(200); }
await tap('Escape'); await sleep(400);
r = await state();
ck(!r.on && Math.abs(r.cam.dist - 12) < 1e-6 && Math.abs(r.cam.tz) < 1e-6, 'Esc leaves; the camera is back where it was (' + JSON.stringify({ on: r.on, dist: r.cam.dist }) + ')');
ck(r.extra.length === 0, 'no figure left behind');

// a phone: the joystick under the left thumb moves them
await C.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 3, mobile: true });
await C.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 2 });
await sleep(800);
await ev(`window.__a3dCamSet({tx:0,ty:1,tz:0,yaw:0,pitch:0.3,dist:12});await window.__a3dWalk.enter();`);
await sleep(600);
await place([0, 0.01, 0], 0);
const J = await ev(`const j=document.querySelector('.a3d-walkjoy'),b=j.getBoundingClientRect();return {d:getComputedStyle(j).display,x:b.left+b.width/2,y:b.top+b.height/2,R:b.width/2};`);
ck(J && J.d === 'block', 'on a phone the joystick is shown (' + JSON.stringify(J) + ')');
await C.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: J.x, y: J.y - J.R * 0.3, id: 1 }] });
await C.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: J.x, y: J.y - J.R * 0.9, id: 1 }] });
await sleep(1500);
r = await state();
await C.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
ck(r.p[2] < -0.8 && r.joy && r.joy.f > 0.5, 'pushing the joystick up walks them forward (z ' + r.p[2].toFixed(3) + ', ' + JSON.stringify(r.joy) + ')');
await shot('203-walk-phone');
r = await ev(`const b=document.querySelector('.a3d-walkbar').getBoundingClientRect();return {l:b.left,r:b.right,w:innerWidth};`);
ck(r && r.l >= 0 && r.r <= r.w, 'the bar fits the phone\'s width (' + JSON.stringify(r) + ')');
await ev(`document.querySelector('[data-walkact="leave"]').click();`);
await sleep(300);
ck(!(await state()).on, 'Leave ends the walk');

const errs = C.ev.filter((e) => (e.method === 'Runtime.exceptionThrown') || (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'error') ||
  (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'warning' && /\[BIM\] (Walk|Rendered)/.test(JSON.stringify(e.params.args))));
ck(errs.length === 0, 'no console errors, no Walk or rendered-view warnings (' + errs.length + ')' + (errs.length ? ': ' + JSON.stringify(errs[0]).slice(0, 400) : ''));
console.log(`\n${pass} passed, ${fail} failed`);
C.ws.close();
process.exit(fail ? 1 : 0);
