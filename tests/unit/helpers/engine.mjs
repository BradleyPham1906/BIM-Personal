/* engine.mjs -- the BIM engine, loaded in Node for unit tests.

   import { loadEngine } from './helpers/engine.mjs';
   const E = loadEngine();          // every name an engine file exports
   E.bimParseBearing('N 45 E');

   It runs exactly the code the browser runs: the engine's files, in src/index.html's order, without
   their import and export lines (as tools/build_app.py joins them), in one function. Their imports
   are what make each file's dependencies plain; loading them one by one through Node's own module
   loader would run them in another order than the app's, so this joins them as the build does.

   The browser is stood in for by ./browser.mjs: enough for the engine's top-level code to run. Code
   that draws or touches the page is tested in the browser suites (tests/e2e/), not here. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { installBrowser } from './browser.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const SRC = path.join(ROOT, 'src');
const HEAD = /^(?:import \{[^}]*\} from '[^']+';\n)+\n/;
const TAIL = /\nexport \{([^}]*)\};\n$/;

let cached = null;

export function engineSource() {
  const html = fs.readFileSync(path.join(SRC, 'index.html'), 'utf8');
  const files = [...html.matchAll(/<!-- @include js\/engine\/(\S+) -->/g)].map((m) => m[1])
    .filter((f) => f !== '_begin.js' && f !== '_end.js');
  const names = new Set();
  let code = '';
  for (const f of files) {
    let t = fs.readFileSync(path.join(SRC, 'js', 'engine', f), 'utf8').replace(HEAD, '');
    const m = t.match(TAIL);
    if (m) {
      m[1].split(',').map((s) => s.trim()).filter(Boolean).forEach((n) => names.add(n));
      t = t.slice(0, t.length - m[0].length) + '\n';
    }
    code += t;
  }
  return { code, names: [...names].sort(), files };
}

export function loadEngine() {
  if (cached) return cached;
  installBrowser(globalThis);
  const { code, names } = engineSource();
  // Sloppy mode, as in the browser; the engine's own try/catch is left out so a failure is seen here.
  const run = new Function(code + '\nreturn {' + names.map((n) => n + ':' + n).join(',') + '};');
  cached = run.call(globalThis);
  return cached;
}
