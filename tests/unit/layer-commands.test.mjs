// V256: AutoCAD's layer commands (engine/layers/layer-commands.js), their plans.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();

test('LAYISO keeps the chosen layers and the layers above them, and turns the rest off', () => {
  const L = [{ id: 'a' }, { id: 'b', parent: 'a' }, { id: 'c' }, { id: 'd', visible: false }];
  const p = E.bimLayIsoPlan(L, ['b']);
  assert.deepEqual(p.keep.sort(), ['a', 'b']);
  assert.deepEqual(p.off, ['c'], 'a layer already off is not counted');
});

test('a snapshot keeps every setting LAYERP and LAYUNISO put back', () => {
  const L = [{ id: 'a', visible: false, frozen: true, color: '#112233', lineweight: 0.5 }, { id: 'b' }];
  const s = E.bimLayerSnap(L, 'b');
  assert.equal(s.cur, 'b');
  assert.equal(s.ls[0].visible, false);
  assert.equal(s.ls[0].lineweight, 0.5);
  assert.equal(s.ls[1].visible, undefined, 'an unset flag stays unset, so it is restored as unset');
  L[0].visible = true;
  assert.equal(s.ls[0].visible, false, 'the snapshot is a copy');
});
