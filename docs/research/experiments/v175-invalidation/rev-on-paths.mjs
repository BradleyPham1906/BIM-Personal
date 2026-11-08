// V175 research: does the model's revision (A3D_REV) move on each change path? (data script, not a test)
// A3D_REV is read through bimPageSig, whose key starts with it (sheets/pages-display.js:94-96). Each path is
// called in Node through tests/unit/helpers/engine.mjs; a path the stand-in cannot run is reported as such.
//   node --max-old-space-size=1024 docs/research/experiments/v175-invalidation/rev-on-paths.mjs [index]
// One probe per run (an index 0..6): in the Node stand-in some paths run out of memory, and a run per path
// keeps one from hiding the others.
import { loadEngine } from '../../../../tests/unit/helpers/engine.mjs';
const E = loadEngine();
const rev = () => +E.bimPageSig({ id: 's' }).split('|')[0];
const out = [];
const ONLY = process.argv[2] ? +process.argv[2] : -1; let K = -1;
function probe(name, fn) {
  K++; if (ONLY >= 0 && K !== ONLY) return;
  const a = rev(); let err = null;
  try { fn(); } catch (e) { err = String(e && e.message).slice(0, 160); }
  out.push({ path: name, before: a, after: rev(), moved: rev() !== a, error: err });
}
probe('saveSoon()', () => E.saveSoon());
probe('pushUndo() alone', () => E.pushUndo());
probe('doUndo()', () => E.doUndo());
probe('bimSetUnits("mm")', () => E.bimSetUnits('mm', null));
const rec = JSON.parse(JSON.stringify(E.bimProjectRecord())); rec.titleBlock = { project: 'Other project', client: '', drawnBy: '', checkedBy: '' };
probe('bimLoadProjectRecord(record) [project load, tab-lock refresh]', () => E.bimLoadProjectRecord(rec));
probe('bimRestoreState(snapshot) alone', () => E.bimRestoreState(E.bimSnapshotState()));
probe('paint()', () => E.paint());
console.log(JSON.stringify(out, null, 1));
setTimeout(() => process.exit(0), 400);
