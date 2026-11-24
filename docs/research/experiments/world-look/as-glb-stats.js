// as-glb-stats.js: reads a .glb's header and JSON chunk as data (glTF 2.0, section 4.4: a 12-byte header, then a
// JSON chunk and an optional BIN chunk) and reports what a living-world asset needs to know: bytes, triangles,
// skins and joints, the most joints a vertex is bound to (JOINTS_1 present means 8), animations with their
// durations and channel counts, morph targets, textures, extensions. Nothing in the file is executed.
// Usage: node as-glb-stats.js file.glb [...]
'use strict';
var fs = require('fs');
var COMP = { 5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4 };
function stats(file) {
  var b = fs.readFileSync(file), magic = b.readUInt32LE(0), ver = b.readUInt32LE(4);
  if (magic !== 0x46546c67) return { file: file, error: 'not a glb' };
  var jl = b.readUInt32LE(12), J = JSON.parse(b.slice(20, 20 + jl).toString('utf8'));
  var binLen = 20 + jl < b.length ? b.readUInt32LE(20 + jl) : 0;
  var tris = 0, verts = 0, morph = 0, j1 = false, i, k;
  (J.meshes || []).forEach(function (m) {
    m.primitives.forEach(function (p) {
      var pa = J.accessors[p.attributes.POSITION];
      verts += pa.count;
      var mode = p.mode === undefined ? 4 : p.mode;
      var n = p.indices !== undefined ? J.accessors[p.indices].count : pa.count;
      if (mode === 4) tris += n / 3; else if (mode === 5 || mode === 6) tris += n - 2;
      if (p.targets) morph = Math.max(morph, p.targets.length);
      if (p.attributes.JOINTS_1 !== undefined) j1 = true;
    });
  });
  var anims = (J.animations || []).map(function (a) {
    var t = 0; a.samplers.forEach(function (s) { var ac = J.accessors[s.input]; if (ac.max && ac.max[0] > t) t = ac.max[0]; });
    return (a.name || '?') + ' ' + t.toFixed(2) + 's/' + a.channels.length + 'ch';
  });
  var animBytes = 0, seen = {};
  (J.animations || []).forEach(function (a) { a.samplers.forEach(function (s) { [s.input, s.output].forEach(function (ai) {
    if (seen[ai]) return; seen[ai] = 1; var ac = J.accessors[ai], nc = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 }[ac.type] || 1; animBytes += ac.count * nc * COMP[ac.componentType]; }); }); });
  var imgBytes = 0; (J.images || []).forEach(function (im) { if (im.bufferView !== undefined) imgBytes += J.bufferViews[im.bufferView].byteLength; });
  return { file: file.split('/').pop(), bytes: b.length, version: ver, generator: (J.asset || {}).generator, meshes: (J.meshes || []).length, verts: verts, tris: tris,
    skins: (J.skins || []).length, joints: (J.skins || []).map(function (s) { return s.joints.length; }), weightsPerVertex: j1 ? 8 : 4,
    morphTargets: morph, materials: (J.materials || []).length, images: (J.images || []).length, imageBytes: imgBytes, animationBytes: animBytes, binBytes: binLen,
    extensionsUsed: J.extensionsUsed || [], animations: anims };
}
process.argv.slice(2).forEach(function (f) { console.log(JSON.stringify(stats(f), null, 1)); });
