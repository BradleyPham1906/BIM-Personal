// V172g, io/file-save.js and io/project-file.js: what the marker says, the envelope version 2, and the gzip form
// (docs/research/research-local-storage.md, part 14).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();

test('the marker: not in a file, changed since its file, in its file', () => {
  assert.equal(E.bimFileState(null, 0).kind, 'none');
  assert.equal(E.bimFileState({ id: 'd' }, 0).kind, 'none', 'an empty project never worked on is not marked');
  const fresh = E.bimFileState({ id: 'd' }, 3);
  assert.equal(fresh.kind, 'unsaved', 'a project holding objects but never saved to a file is marked');
  assert.equal(fresh.text, 'Not saved to a file');
  assert.equal(E.bimFileState({ id: 'd', unsaved: 1 }, 0).kind, 'unsaved', 'an edit marks even an empty project');
  const changed = E.bimFileState({ id: 'd', fileName: 'House.acad3d.json', unsaved: 1 }, 5);
  assert.equal(changed.kind, 'changed');
  assert.equal(changed.text, 'Changes not saved to House.acad3d.json');
  const at = new Date(2026, 10, 7, 14, 5).getTime();
  assert.equal(E.bimFileState({ fileName: 'House.acad3d.json', fileVia: 'saved', fileAt: at }, 5).text, 'Saved to House.acad3d.json at 14:05');
  assert.equal(E.bimFileState({ fileName: 'H.acad3d.json.gz', fileVia: 'opened', fileAt: at }, 5).text, 'Opened from H.acad3d.json.gz at 14:05');
  assert.equal(E.bimFileState({ fileName: 'H.acad3d.json', fileVia: 'downloaded', fileAt: at }, 5).text, 'Downloaded as H.acad3d.json at 14:05');
});

test('envelope version 2 carries the project record itself, with the view and the id counter', () => {
  const env = JSON.parse(E.bimBuildProjectEnvelope());
  assert.equal(env.app, 'acad3d-project');
  assert.equal(env.formatVersion, 2);
  assert.equal(typeof env.appVersion, 'string');
  assert.ok(env.data.cam && typeof env.data.cam.dist === 'number', 'the view is in the file');
  assert.equal(typeof env.data.seq, 'number', 'the id counter is in the file');
  assert.equal('docId' in env.data, false, 'the browser\'s own id for the project is not');
  assert.deepEqual(Object.keys(env.data).sort(), Object.keys(E.bimProjectRecord()).sort(), 'one list of what a project is');
});

test('reading a file: version 1 and 2 without a word, a newer one with a warning, a foreign one refused', () => {
  const v1 = E.bimParseProjectEnvelope(JSON.stringify({ app: 'acad3d-project', formatVersion: 1, data: { objs: [] } }));
  assert.equal(v1.warn, null);
  const v2 = E.bimParseProjectEnvelope(E.bimBuildProjectEnvelope());
  assert.equal(v2.warn, null);
  assert.ok(v2.data.cam);
  const v3 = E.bimParseProjectEnvelope(JSON.stringify({ app: 'acad3d-project', formatVersion: 3, data: { objs: [] } }));
  assert.match(v3.warn, /newer version/);
  assert.equal(E.bimParseProjectEnvelope('{"app":"other","data":{}}').error, 'not a recognized project file');
  assert.equal(E.bimParseProjectEnvelope('\u001f\u008b not text').error, 'not valid JSON');
});

test('the compressed form starts 1F 8B and reads back exactly; a cut file is refused whole', async () => {
  if (typeof CompressionStream !== 'function') return;   // Node 18+ has it; older Node skips
  const text = E.bimBuildProjectEnvelope();
  const z = new Uint8Array(await new Response(new Blob([new TextEncoder().encode(text)]).stream()
    .pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
  assert.deepEqual([z[0], z[1]], [0x1f, 0x8b]);
  const back = await new Response(new Blob([z]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
  assert.equal(back, text);
  await assert.rejects(new Response(new Blob([z.slice(0, z.length - 10)]).stream()
    .pipeThrough(new DecompressionStream('gzip'))).text());
});
