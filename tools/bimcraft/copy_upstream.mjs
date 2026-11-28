// tools/bimcraft/copy_upstream.mjs -- the owner, 2026-11-28: "copy their code ... reuse the codes, dont write new stuff".
// Copies BimCraft's BIM-authoring core (github.com/getcadcraft/bimcraft, Apache-2.0) into vendor/bimcraft/app/,
// every file unchanged, with that repository's LICENSE, NOTICE, PROVENANCE.md, TRADEMARKS.md and THIRD_PARTY.md:
// the files the ROOTS below import, followed through every import (static and dynamic), and nothing else.
//   git clone https://github.com/getcadcraft/bimcraft <dir> && git -C <dir> checkout <REV>
//   node tools/bimcraft/copy_upstream.mjs <dir>           copies, and writes vendor/bimcraft/FILES.txt with each SHA-256
//   node tools/bimcraft/copy_upstream.mjs <dir> --check   fails when vendor/bimcraft differs from the clone
import fs from 'node:fs'; import path from 'node:path'; import crypto from 'node:crypto'; import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { REV, ROOTS } from './roots.mjs';
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '..', '..');
const src = process.argv[2], check = process.argv.includes('--check');
if (!src) { console.error('usage: node tools/bimcraft/copy_upstream.mjs <bimcraft clone> [--check]'); process.exit(2); }
const head = execFileSync('git', ['-C', src, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
if (!head.startsWith(REV)) { console.error('the clone is at ' + head + ', expected ' + REV); process.exit(2); }
const app = path.join(src, 'app'), seen = new Set(), ext = new Set();
function follow(rel) {
  rel = path.posix.normalize(rel);
  if (seen.has(rel)) return;
  const f = path.join(app, rel);
  if (!fs.existsSync(f)) throw new Error('missing upstream file ' + rel);
  seen.add(rel);
  const t = fs.readFileSync(f, 'utf8');
  const re = /(?:^|\n)\s*(?:import\s[^'"]*?from\s*|import\s*|export\s[^'"]*?from\s*)['"]([^'"]+)['"]|import\(\s*['"]([^'"]+)['"]\s*\)/g;
  let m;
  while ((m = re.exec(t))) {
    const s = m[1] || m[2];
    if (s.startsWith('.')) follow(path.posix.join(path.posix.dirname(rel), s)); else ext.add(s);
  }
}
ROOTS.forEach(follow);
const files = [...seen].sort(), top = ['LICENSE', 'NOTICE', 'PROVENANCE.md', 'TRADEMARKS.md', 'THIRD_PARTY.md'];
const out = path.join(root, 'vendor', 'bimcraft'), sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const list = top.map((f) => [f, path.join(src, f)]).concat(files.map((f) => ['app/' + f, path.join(app, f)]));
const manifest = '# BimCraft @ ' + head + ' (github.com/getcadcraft/bimcraft), copied unchanged by tools/bimcraft/copy_upstream.mjs\n' +
  '# libraries the copied files import (not copied: tools/bimcraft/build_bimcraft.mjs leaves them out): ' + ([...ext].sort().join(', ') || 'none') + '\n' +
  list.map(([rel, abs]) => sha(fs.readFileSync(abs)) + '  ' + rel).join('\n') + '\n';
if (check) {
  let bad = 0;
  for (const [rel, abs] of list) {
    const p = path.join(out, rel);
    if (!fs.existsSync(p) || !fs.readFileSync(p).equals(fs.readFileSync(abs))) { console.error('differs: vendor/bimcraft/' + rel); bad++; }
  }
  if (!fs.existsSync(path.join(out, 'FILES.txt')) || fs.readFileSync(path.join(out, 'FILES.txt'), 'utf8') !== manifest) { console.error('differs: vendor/bimcraft/FILES.txt'); bad++; }
  if (bad) process.exit(1);
  console.log('vendor/bimcraft is BimCraft @ ' + REV + ': ' + files.length + ' files, unchanged');
  process.exit(0);
}
fs.rmSync(path.join(out, 'app'), { recursive: true, force: true });
for (const [rel, abs] of list) { const p = path.join(out, rel); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.copyFileSync(abs, p); }
fs.writeFileSync(path.join(out, 'FILES.txt'), manifest);
console.log('copied ' + files.length + ' files of BimCraft @ ' + head.slice(0, 8) + ' to vendor/bimcraft/app; they import: ' + ([...ext].sort().join(', ') || 'nothing else'));
