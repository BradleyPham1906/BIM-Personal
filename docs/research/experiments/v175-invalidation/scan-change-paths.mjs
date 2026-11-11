// V175 research, invalidation: where model changes pass through (data script, not a test).
// Reads every engine file under src/js/engine as text and, for each named function, records whether its
// body calls pushUndo(), saveSoon(), and whether it writes a project field of A3D (an approximate regex:
// assignment, push, splice, pop, shift, unshift, sort, reverse on A3D.<field>). Prints counts and the
// functions that write a project field or call pushUndo() without calling saveSoon() in the same body.
// The body of a named function includes its nested callbacks; a call in a caller is not seen, so a
// "bypass" listed here is a pointer to read, not a proven fault.
//   node docs/research/experiments/v175-invalidation/scan-change-paths.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..');
const ENG = path.join(ROOT, 'src', 'js', 'engine');
const FIELDS = 'objs|levels|grids|layers|counts|views|types|sheets|titleBlock|buildings|site|classifications|resultLayers|pres|dataFeatures|history|roomScheme|activeLevel|activeLayer|activeWallType|levelFilter|activeBuilding';
const WRITE = new RegExp('A3D\\.(' + FIELDS + ')\\b(\\[[^\\]]*\\])?\\s*(=(?!=)|\\.(push|splice|pop|shift|unshift|sort|reverse)\\()');

function walk(d, out) {
  for (const f of fs.readdirSync(d)) {
    const p = path.join(d, f);
    if (fs.statSync(p).isDirectory()) walk(p, out); else if (f.endsWith('.js')) out.push(p);
  }
  return out;
}
function bodies(src) {
  const re = /function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{/g, out = [];
  let m;
  while ((m = re.exec(src))) {
    let i = re.lastIndex, depth = 1, q = null;
    for (; i < src.length && depth; i++) {
      const c = src[i];
      if (q) { if (c === '\\') i++; else if (c === q) q = null; continue; }
      if (c === '"' || c === "'") q = c;
      else if (c === '/' && src[i + 1] === '*') { const e = src.indexOf('*/', i + 2); i = e < 0 ? src.length : e + 1; }
      else if (c === '{') depth++; else if (c === '}') depth--;
    }
    out.push({ name: m[1], body: src.slice(m.index, i), line: src.slice(0, m.index).split('\n').length });
  }
  return out;
}
const files = walk(ENG, []);
// Second pass: a function "reaches saveSoon" when its body calls saveSoon() or calls, by name, a function that
// reaches it (a fixed point over names; one name declared twice counts if either copy reaches it).
const ALL = [];
for (const f of files) for (const b of bodies(fs.readFileSync(f, 'utf8'))) ALL.push(b);
const reaches = new Set(['saveSoon']);
for (let changed = true; changed;) {
  changed = false;
  for (const b of ALL) {
    if (reaches.has(b.name)) continue;
    const calls = b.body.slice(b.body.indexOf('{')).match(/\b[A-Za-z_$][\w$]*(?=\()/g) || [];
    if (calls.some((c) => c !== b.name && reaches.has(c))) { reaches.add(b.name); changed = true; }
  }
}
let nFn = 0, nUndo = 0, nSave = 0, nWrite = 0, nUndoNoSave = 0, nWriteNoSave = 0;
const undoNoSave = [], writeNoSave = [];
for (const f of files) {
  const rel = path.relative(ROOT, f).replace(/\\/g, '/');
  for (const b of bodies(fs.readFileSync(f, 'utf8'))) {
    if (b.name === 'pushUndo' || b.name === 'saveSoon' || b.name === 'bimRestoreState') continue;
    nFn++;
    const u = /\bpushUndo\(\)/.test(b.body), s = /\bsaveSoon\(\)/.test(b.body), w = WRITE.test(b.body);
    if (u) nUndo++; if (s) nSave++; if (w) nWrite++;
    const r = reaches.has(b.name);
    if (u && !s) { nUndoNoSave++; undoNoSave.push(rel + ':' + b.line + ' ' + b.name + (r ? '  [reaches saveSoon through a callee]' : '  [NOT reached through a callee]')); }
    if (w && !s && !u) { nWriteNoSave++; writeNoSave.push(rel + ':' + b.line + ' ' + b.name + (r ? '  [reaches saveSoon through a callee]' : '  [NOT reached through a callee]')); }
  }
}
console.log(JSON.stringify({ files: files.length, functions: nFn, callPushUndo: nUndo, callSaveSoon: nSave, writeProjectField: nWrite,
  pushUndoWithoutSaveSoon: nUndoNoSave, writeWithoutUndoOrSave: nWriteNoSave }, null, 1));
console.log('\n-- pushUndo() without saveSoon() in the same body --');
undoNoSave.forEach((s) => console.log(s));
console.log('\n-- a project field written, neither pushUndo() nor saveSoon() in the same body --');
writeNoSave.forEach((s) => console.log(s));
