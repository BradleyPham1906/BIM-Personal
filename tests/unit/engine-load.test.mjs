// The engine loads in Node, and what its files declare they export is there.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine, engineSource } from './helpers/engine.mjs';

test('the engine runs its top-level code without throwing', () => {
  const E = loadEngine();
  assert.ok(Object.keys(E).length > 2000);
});

test('every setter another file uses is a function', () => {
  const E = loadEngine();
  const setters = engineSource().names.filter((n) => /^set[A-Z]/.test(n));
  assert.ok(setters.length >= 20);
  assert.deepEqual(setters.filter((n) => typeof E[n] !== 'function'), []);
});

test('a setter returns the value it wrote, as the assignment it replaced did', () => {
  const E = loadEngine();
  assert.equal(E.setBIM_PAT_SVG_SEQ(41), 41);
});
