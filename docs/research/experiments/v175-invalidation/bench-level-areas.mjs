// V175 research: the cost of recomputing one live number from the model with the app's own function,
// bimLevelAreas (gross and net area of a level), on closed rectangular walls (data script, not a test).
// bench.mjs's 2,000 open walls hit the function's 400-edge limit and return early; this keeps under it.
//   node --max-old-space-size=2048 docs/research/experiments/v175-invalidation/bench-level-areas.mjs
import { loadEngine } from '../../../../tests/unit/helpers/engine.mjs';
const E = loadEngine();
function run(nRooms) {
  const objs = [];
  for (let i = 0; i < nRooms; i++) {
    const x = (i % 10) * 12, z = Math.floor(i / 10) * 12;
    const r = E.bimBuildWallGeometry([[x, z], [x + 8, z], [x + 8, z + 6], [x, z + 6]], 0, 3, 0.3, 'center', true, null);
    const o = { id: 'a3d-la-' + i, t: 'solid', name: 'Wall_' + i, col: '#c7bfae', pos: [0, 0, 0], mesh: r.mesh, bim: r.bim, layer: 'layer-0' };
    o.bim.levelId = 'lvl-0'; o.bim.typeCat = 'wall'; objs.push(o);
  }
  E.A3D.objs = objs;
  const t = [];
  for (let i = 0; i < 5; i++) E.bimLevelAreas('lvl-0');
  for (let i = 0; i < 31; i++) { const a = process.hrtime.bigint(); E.bimLevelAreas('lvl-0'); t.push(Number(process.hrtime.bigint() - a) / 1e6); }
  t.sort((a, b) => a - b);
  const s = E.bimLevelAreas('lvl-0');
  return { rooms: nRooms, edges: nRooms * 4, median_ms: +t[15].toFixed(4), p95_ms: +t[29].toFixed(4), gross: s.gross, net: s.net, note: s.note || '' };
}
console.log(JSON.stringify([run(10), run(50), run(100), run(101)], null, 1));
setTimeout(() => process.exit(0), 50);
