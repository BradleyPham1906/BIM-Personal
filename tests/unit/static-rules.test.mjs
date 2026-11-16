import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const CHECKER = path.join(ROOT, 'tools', 'check_static_rules.py');
const PYTHON = 'python3';

function runChecker(files) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'bim-static-rules-'));
  try {
    for (const [name, content] of Object.entries(files)) {
      const file = path.join(tmp, name);
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, content);
    }
    return spawnSync(PYTHON, [CHECKER, '--root', tmp], { encoding: 'utf8' });
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

test('allows one test-hook assignment and ignores comments and strings', () => {
  const result = runChecker({
    'hooks/a.js': [
      '/* window.__a3dFake = function() {}; */',
      'var note = "window.__a3dFake = function() {};";',
      'window.__a3dReal = function() {};',
      'if (window.__a3dReal === value) {}'
    ].join('\n')
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /1 test-hook assignments?, no duplicates/);
});

test('rejects duplicate test-hook definitions across files', () => {
  const result = runChecker({
    'hooks/a.js': 'window.__a3dReal = function() {};\n',
    'hooks/b.js': 'window.__a3dReal = function() {};\n'
  });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /duplicate test hook window\.__a3dReal/);
  assert.match(result.stderr, /hooks[\\/]a\.js:1/);
  assert.match(result.stderr, /hooks[\\/]b\.js:1/);
});

test('reports an invalid source root instead of passing silently', () => {
  const result = spawnSync(PYTHON, [CHECKER, '--root', path.join(os.tmpdir(), 'missing-bim-js-root')], {
    encoding: 'utf8'
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /source root does not exist/);
});
