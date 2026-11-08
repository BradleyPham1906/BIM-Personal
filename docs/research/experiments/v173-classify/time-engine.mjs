// V173: natural breaks as the engine has it (map/classify.js, plain arrays), timed in Node.
import { loadEngine } from '../../../../tests/unit/helpers/engine.mjs';
const E = loadEngine();
let s = 1; const r = () => { s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; };
for (const n of [1e3, 1e4, 3e4, 1e5, 3e5]) for (const k of [5, 9]) {
  const x = Array.from({ length: n }, () => Math.exp(1.5 * (r() + r() + r() - 1.5)));
  const t = [];
  for (let i = 0; i < 3; i++) { const a = performance.now(); E.bimClsBreaks(x, 'natural', { k }); t.push(performance.now() - a); }
  console.log(`n=${n} k=${k} ms ${t.map((v) => v.toFixed(1)).join(' ')}`);
}
console.log(process.version);
