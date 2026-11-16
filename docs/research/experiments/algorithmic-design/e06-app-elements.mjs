// e06: what the app's own wall geometry costs a generator (H1's second half: the geometry is the cost).
// Loads the engine in Node as the unit tests do (tests/unit/helpers/engine.mjs). Data, never a suite.
// Only the pure function bimBuildWallGeometry is measured. The interactive makers (buildWallSolid,
// buildWindowOpening) repaint and refresh the page and exhaust memory in the Node stand-in, and the
// opening cutter (bimBuildWallOpening) is private to its file: both need the browser, so their cost is open.
// Run: node docs/research/experiments/algorithmic-design/e06-app-elements.mjs
import { loadEngine } from '../../../../tests/unit/helpers/engine.mjs';
const E = loadEngine();
const now = () => Number(process.hrtime.bigint()) / 1e6;
console.log('node ' + process.version + '; bimBuildWallGeometry, straight 9.6 m walls 3.5 m high, 0.2 m thick');
console.log('');
console.log('| walls | total (ms), median of 9 | per wall (ms) | JSON of the meshes (KB) |');
console.log('|---|---|---|---|');
for(const n of [10, 100, 1000, 10000]){
  const runs = []; let bytes = 0;
  for(let i = 0; i < 9; i++){ const t0 = now(); bytes = 0;
    for(let s = 0; s < n; s++){ const r = E.bimBuildWallGeometry([[0, s], [9.6, s]], 0, 3.5, 0.2, 'center', false);
      if(r.error) throw new Error(r.error); if(i === 8) bytes += JSON.stringify(r.mesh).length; }
    runs.push(now() - t0); }
  runs.sort((x, y) => x - y);
  console.log(`| ${n} | ${runs[4].toFixed(2)} | ${(runs[4] / n).toFixed(4)} | ${(bytes / 1024).toFixed(0)} |`);
}
