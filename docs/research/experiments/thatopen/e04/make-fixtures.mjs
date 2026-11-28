// e04: two small data sets of our own, for the Review view's point clouds and splats (V206, the owner's decision 11,
// 2026-11-28), made by this script so the repository holds no third-party scans:
//   tests/fixtures/thatopen/potree/{metadata.json, hierarchy.bin, octree.bin}  a Potree 2.0 cloud, one leaf node:
//     a 10 m x 6 m floor (40 x 25 points) and a wall 3 m high at its back (40 x 15), 1600 points, 0.25 m apart, coloured (DEFAULT encoding:
//     each point int32 x, y, z then uint16 r, g, b; PotreeConverter 2.0's layout, as potree-core 2.0.17 reads it)
//   tests/fixtures/thatopen/splat.ply  an INRIA 3DGS binary ply: 64 gaussians on a 4 x 4 x 4 grid, 1 m apart,
//     14 float properties each (x y z scale_0..2 rot_0..3 opacity f_dc_0..2), the ones That Open's parser needs
//     (components-front SplatLoader/gsplat/ply.ts 36-42)
// node docs/research/experiments/thatopen/e04/make-fixtures.mjs
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../../..');
const out = path.join(root, 'tests/fixtures/thatopen');
fs.mkdirSync(path.join(out, 'potree'), { recursive: true });

// the cloud: z up in the scan's frame (Potree's), metres
const pts = [];
for (let i = 0; i < 40; i++) for (let j = 0; j < 25; j++) pts.push([i * 0.25, j * 0.25, 0, 180, 170, 150]);   // the floor, 1000
for (let i = 0; i < 40; i++) for (let k = 1; k <= 15; k++) pts.push([i * 0.25, 6, k * 0.2, 200, 90, 60]);       // the wall, 600
const scale = 0.001, offset = [0, 0, 0];
const min = [0, 0, 0], max = [10, 6, 3];
const stride = 12 + 6, oct = Buffer.alloc(pts.length * stride);
pts.forEach((p, n) => {
  const b = n * stride;
  for (let a = 0; a < 3; a++) oct.writeInt32LE(Math.round((p[a] - offset[a]) / scale), b + 4 * a);
  for (let a = 0; a < 3; a++) oct.writeUInt16LE(p[3 + a] * 257, b + 12 + 2 * a);
});
// one node, 22 bytes: type (1 leaf), child mask, number of points, byte offset (uint64), byte size (uint64)
const hier = Buffer.alloc(22);
hier.writeUInt8(1, 0); hier.writeUInt8(0, 1); hier.writeUInt32LE(pts.length, 2);
hier.writeBigUInt64LE(0n, 6); hier.writeBigUInt64LE(BigInt(oct.length), 14);
const meta = {
  version: '2.0', name: 'bim-personal-e04', description: 'synthetic: a floor and a wall (docs/research/experiments/thatopen/e04)',
  points: pts.length, projection: '', hierarchy: { firstChunkSize: 22, stepSize: 4, depth: 0 },
  offset, scale: [scale, scale, scale], spacing: 0.5,
  boundingBox: { min, max }, encoding: 'DEFAULT',
  attributes: [
    { name: 'position', description: '', size: 12, numElements: 3, elementSize: 4, type: 'int32', min, max },
    { name: 'rgb', description: '', size: 6, numElements: 3, elementSize: 2, type: 'uint16', min: [0, 0, 0], max: [65535, 65535, 65535] }]
};
fs.writeFileSync(path.join(out, 'potree/metadata.json'), JSON.stringify(meta, null, 1) + '\n');
fs.writeFileSync(path.join(out, 'potree/hierarchy.bin'), hier);
fs.writeFileSync(path.join(out, 'potree/octree.bin'), oct);

// the splat
const props = ['x', 'y', 'z', 'scale_0', 'scale_1', 'scale_2', 'rot_0', 'rot_1', 'rot_2', 'rot_3', 'opacity', 'f_dc_0', 'f_dc_1', 'f_dc_2'];
const n = 64, head = 'ply\nformat binary_little_endian 1.0\nelement vertex ' + n + '\n' + props.map((p) => 'property float ' + p).join('\n') + '\nend_header\n';
const body = Buffer.alloc(n * props.length * 4);
let k = 0;
for (let x = 0; x < 4; x++) for (let y = 0; y < 4; y++) for (let z = 0; z < 4; z++) {
  const v = [x, y, z, Math.log(0.15), Math.log(0.15), Math.log(0.15), 1, 0, 0, 0, 3, (x - 1.5) / 2, (y - 1.5) / 2, (z - 1.5) / 2];
  v.forEach((f, a) => body.writeFloatLE(f, (k * props.length + a) * 4)); k++;
}
fs.writeFileSync(path.join(out, 'splat.ply'), Buffer.concat([Buffer.from(head, 'ascii'), body]));
console.log('cloud: ' + pts.length + ' points, octree.bin ' + oct.length + ' bytes; splat.ply ' + (head.length + body.length) + ' bytes');
