/* bim_phase174_boards_phone_check.mjs -- V174's phone pass (390 x 844, touch), run 2026-11-08: 8 of 8.
   Run as bim_phase174_boards_edge_check.mjs is (a local server on 8765, Edge with --remote-debugging-port=9333 and a
   NEW empty profile), then: node tests/e2e/bim_phase174_boards_phone_check.mjs <a folder for the screenshots>.
   It checks: the board drawn for a phone, a row stack shown as a column in reading order (D11), no sideways page
   scroll, the Edit bar's Draw on screen, the page gallery and the Draw menu fitting the phone, and the console. */
import fs from 'node:fs';
const PORT = 9333, APP = 'http://127.0.0.1:8765/canvas_v10.html', OUT = process.argv[2] || '.';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let t; for (let i = 0; i < 40; i++) { try { t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json(); break; } catch (e) { await sleep(250); } }
const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const wait = {}, evs = [];
await new Promise((r) => ws.onopen = r);
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait[d.id]) { wait[d.id](d); delete wait[d.id]; } else evs.push(d); };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; wait[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (e) => { const r = await send('Runtime.evaluate', { expression: `(async()=>{${e}})()`, awaitPromise: true, returnByValue: true }); return r.result.exceptionDetails ? { __err: (r.result.exceptionDetails.exception || {}).description } : r.result.result.value; };
await send('Runtime.enable'); await send('Log.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
await send('Page.navigate', { url: APP }); await sleep(5000);
let pass = 0, fail = 0; const ck = (ok, m) => { ok ? pass++ : fail++; console.log((ok ? 'PASS ' : 'FAIL ') + m); };
const shot = async (n) => { const r = await send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${OUT}/${n}.png`, Buffer.from(r.result.data, 'base64')); };
const W8 = 'await new Promise(r=>setTimeout(r,250));';
let r = await ev(`window.__a3dEnter&&window.__a3dEnter();var D=window.__a3dBoardDesign;window.__a3dBrdNew('Phone');${W8}
  var dl=document.querySelector('.a3d-clb-dlg [data-brddlg="cancel"]');if(dl)dl.click();${W8}
  var ly=window.__a3dLayerNew({name:'Row'});
  var a=D.add('rect',{layer:ly,x:10,y:20,w:30,h:20,fill:'#2a78d6'}),b=D.add('rect',{layer:ly,x:50,y:20,w:30,h:20,fill:'#eb6834'}),c=D.add('text',{layer:ly,x:90,y:20,w:40,h:10,s:'Hello'});
  D.stack(ly,{dir:'row',gap:5});${W8}
  var q=s=>document.querySelector('.a3d-clb-dsn [data-bde="'+s+'"]').getBoundingClientRect();
  var A=q(a),B=q(b),C=q(c),se=document.scrollingElement;
  var bar=document.querySelector('.a3d-clb-ebar [data-brd="draw"]'),br=bar?bar.getBoundingClientRect():null;
  return {narrow:!!document.querySelector('.a3d-clb.w-s'),ax:Math.round(A.left),bx:Math.round(B.left),cx:Math.round(C.left),ay:Math.round(A.top),by:Math.round(B.top),cy:Math.round(C.top),
    sw:se.scrollWidth,iw:innerWidth,page:(D.objs()&&window.__a3dBrdRecord(window.__a3dBrdState().cid).page)||null,draw:br?{l:Math.round(br.left),r:Math.round(br.right),vis:br.width>0}:null};`);
ck(r && r.narrow, 'the board is drawn for a phone');
ck(r && Math.abs(r.ax - r.bx) <= 1 && Math.abs(r.bx - r.cx) <= 1 && r.ay < r.by && r.by < r.cy, 'a row stack is shown as a column in reading order (' + JSON.stringify(r) + ')');
ck(r && r.page && r.page.key === 'iso-A4' && r.page.o === 'l', 'the first drawing gave the board the smallest page that holds it (' + JSON.stringify(r && r.page) + ')');
ck(r && r.sw <= r.iw, 'no sideways page scroll (' + (r && r.sw) + ' <= ' + (r && r.iw) + ')');
ck(r && r.draw && r.draw.vis && r.draw.l >= 0 && r.draw.r <= r.iw, 'Draw is on screen');
await shot('v174-phone-board');
r = await ev(`var b=document.querySelector('.a3d-clb-ebar [data-brd="page"]');if(b)b.click();${W8}
  var d=document.querySelector('.a3d-clb-dlgin'),cards=document.querySelectorAll('.a3d-clb-dlg .a3d-pggc'),out=0;
  [].forEach.call(cards,function(c){var q=c.getBoundingClientRect();if(q.right>innerWidth+1||q.left<-1)out++;});
  var dr=d?d.getBoundingClientRect():null;return {cards:cards.length,out:out,dlg:dr?{l:Math.round(dr.left),r:Math.round(dr.right)}:null,iw:innerWidth};`);
ck(r && r.cards === 16 && r.out === 0 && r.dlg && r.dlg.l >= 0 && r.dlg.r <= r.iw, 'the page gallery fits the phone (' + JSON.stringify(r) + ')');
await shot('v174-phone-gallery');
r = await ev(`var c=document.querySelector('.a3d-clb-dlg [data-brddlg="cancel"]');if(c)c.click();${W8}
  var m=document.querySelector('.a3d-clb-ebar [data-brd="draw"]');m.click();${W8}
  var items=document.querySelectorAll('#a3d-ltmenu [data-ltm], #a3d-ltmenu button'),o=0;[].forEach.call(items,function(i){var q=i.getBoundingClientRect();if(q.right>innerWidth+1)o++;});
  return {items:items.length,out:o};`);
ck(r && r.items >= 12 && r.out === 0, 'the Draw menu fits the phone (' + JSON.stringify(r) + ')');
const errs = evs.filter((e) => e.method === 'Runtime.exceptionThrown' || (e.method === 'Log.entryAdded' && e.params.entry.level === 'error' && !/favicon/.test(e.params.entry.url || '')) || (e.method === 'Runtime.consoleAPICalled' && (e.params.type === 'error' || (e.params.type === 'warning' && JSON.stringify(e.params.args).indexOf('[BIM]') >= 0))));
errs.forEach((e) => console.log('CONSOLE', JSON.stringify(e.params).slice(0, 300)));
ck(errs.length === 0, 'no console errors and no [BIM] warnings (' + errs.length + ')');
console.log(`\n${pass} of ${pass + fail} passed`); ws.close(); process.exit(0);
