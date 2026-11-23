// V270: IGES import (engine/io/iges-io.js) with the pinned reader (runtime/occt-import/0.0.23/), on an IGES box of our
// own (tests/fixtures/iges/box-2x1x3.igs, written by docs/research/experiments/v270-iges/gen_iges_cube.mjs).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const DIR = fileURLToPath(new URL('../../runtime/occt-import/0.0.23/', import.meta.url));
const FIX = fileURLToPath(new URL('../fixtures/iges/box-2x1x3.igs', import.meta.url));
const near = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) <= eps, `${a} is not ${b}`);

test('an IGES box (2 east, 1 north, 3 up in its Z-up frame) comes in as the app\'s mesh, y up, north -z, then a closed solid', async () => {
  const reader = createRequire(import.meta.url)(DIR + 'occt-import-js.js');
  const M = await reader({ locateFile: (f) => DIR + f });
  const res = M.ReadIgesFile(fs.readFileSync(FIX), { linearUnit: 'meter' });
  const r = E.bimIgesMesh(res);
  assert.equal(r.parts, 6, 'its six faces');
  const ax = (k) => r.mesh.v.map((v) => v[k]);
  near(Math.min(...ax(0)), 0); near(Math.max(...ax(0)), 2);
  near(Math.min(...ax(1)), 0); near(Math.max(...ax(1)), 3);
  near(Math.min(...ax(2)), -1); near(Math.max(...ax(2)), 0);
  const fixed = E.bimMeshRepair(r.mesh, 1e-6);
  assert.equal(fixed.report.closed, true, 'welded, the six faces close');
  const vol = fixed.mesh.f.reduce((s, [a, b, c]) => { const A = fixed.mesh.v[a], B = fixed.mesh.v[b], C = fixed.mesh.v[c];
    return s + (A[0] * (B[1] * C[2] - B[2] * C[1]) - A[1] * (B[0] * C[2] - B[2] * C[0]) + A[2] * (B[0] * C[1] - B[1] * C[0])) / 6; }, 0);
  near(vol, 6, 1e-6);
  assert.equal(E.bimIgesMesh({ success: false }), null);
});
