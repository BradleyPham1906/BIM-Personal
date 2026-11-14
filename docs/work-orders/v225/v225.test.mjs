/* V225's work-order tests (docs/work-orders/v225/SPEC.md, WO-01 to WO-04): the pure functions of src/js/engine/ui/openbridge-theme.js.
   Outside tests/unit/ while the work orders are open. Run them with:
     node --test docs/work-orders/v225/v225.test.mjs
     node --test --test-name-pattern="WO-01" docs/work-orders/v225/v225.test.mjs
   A function not built yet fails its own cases and no others. The file is read as text. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const NAMES = ["bimObLum", "bimObContrast", "bimObPasses", "bimObTheme"];
function load() {
  let src = fs.readFileSync(path.join(ROOT, 'src/js/engine/ui/openbridge-theme.js'), 'utf8');
  if (process.env.V225_REF) src += fs.readFileSync(process.env.V225_REF, 'utf8');
  src = src.replace(/^import \{[^}]*\} from '[^']+';\n/gm, '').replace(/\nexport \{[^}]*\};\n?$/, '\n');
  return new Function(src + '\nreturn {' + NAMES.map((n) => n + ':typeof ' + n + "==='function'?" + n + ':undefined').join(',') + '};')();
}
const X = load();
const fn = (n) => { assert.equal(typeof X[n], 'function', n + ' is not built yet in src/js/engine/ui/openbridge-theme.js'); return X[n]; };
const near = (a, b, e, m) => assert.ok(Math.abs(a - b) <= (e === undefined ? 1e-9 : e), (m || '') + ' ' + a + ' is not ' + b);

test('WO-01 relative luminance (WCAG 2): black 0, white 1', () => {
  near(fn('bimObLum')('#000000'), 0); near(fn('bimObLum')('#ffffff'), 1, 1e-12);
  near(fn('bimObLum')('808080'), 0.21586050011389926, 1e-12);
  assert.equal(fn('bimObLum')('#fff'), null);
});
test('WO-02 contrast ratio: black on white 21', () => {
  near(fn('bimObContrast')('#000000', '#ffffff'), 21, 1e-9);
  near(fn('bimObContrast')('#ffffff', '#000000'), 21, 1e-9);
  near(fn('bimObContrast')('#777777', '#ffffff'), 4.478, 1e-3);
  assert.equal(fn('bimObContrast')('x', '#ffffff'), null);
});
test('WO-03 WCAG levels: AA 4.5, large text 3, AAA 7', () => {
  assert.equal(fn('bimObPasses')(4.5, 'AA'), true); assert.equal(fn('bimObPasses')(4.478, 'AA'), false);
  assert.equal(fn('bimObPasses')(3.1, 'large'), true); assert.equal(fn('bimObPasses')(6.9, 'AAA'), false);
});
test('WO-04 a theme for a mode (day, dusk, night), day where a token has no value for it', () => {
  const T = { bg: { day: '#ffffff', night: '#000000' }, ink: { day: '#111111', dusk: '#222222', night: '#eeeeee' } };
  assert.deepEqual(fn('bimObTheme')(T, 'night'), { bg: '#000000', ink: '#eeeeee' });
  assert.deepEqual(fn('bimObTheme')(T, 'dusk'), { bg: '#ffffff', ink: '#222222' });
});
