// as-glb-rootmotion.js: for each animation in a .glb (read as data), the translation channels' travel: how far each
// animated node's translation moves in x, y and z over the clip. A clip whose hips travel little in the walking
// direction is "in place": the app must move the character itself, and the clip's playback rate must be matched to
// the walker's speed (stride length / cycle time) or the feet slide. Usage: node as-glb-rootmotion.js file.glb
'use strict';
var fs = require('fs');
var f = process.argv[2], b = fs.readFileSync(f), jl = b.readUInt32LE(12), J = JSON.parse(b.slice(20, 20 + jl).toString('utf8'));
var bin = b.slice(20 + jl + 8);
function acc(i) {
  var a = J.accessors[i], v = J.bufferViews[a.bufferView], n = { SCALAR: 1, VEC3: 3, VEC4: 4 }[a.type], st = v.byteStride || n * 4, o = (v.byteOffset || 0) + (a.byteOffset || 0), out = [];
  if (a.componentType !== 5126) return null;
  for (var k = 0; k < a.count; k++) { var e = []; for (var c = 0; c < n; c++) e.push(bin.readFloatLE(o + k * st + c * 4)); out.push(e); }
  return out;
}
(J.animations || []).forEach(function (A) {
  var best = null;
  A.channels.forEach(function (ch) {
    if (ch.target.path !== 'translation') return;
    var s = A.samplers[ch.sampler], o = acc(s.output), t = acc(s.input); if (!o) return;
    var mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
    o.forEach(function (p) { for (var c = 0; c < 3; c++) { if (p[c] < mn[c]) mn[c] = p[c]; if (p[c] > mx[c]) mx[c] = p[c]; } });
    var r = [mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]], tot = r[0] + r[1] + r[2];
    if (!best || tot > best.tot) best = { node: J.nodes[ch.target.node].name, range: r.map(function (x) { return +x.toFixed(3); }), tot: tot, dur: t[t.length - 1][0] };
  });
  console.log(A.name + '\t' + (best ? best.node + '\ttravel x,y,z ' + best.range.join(',') + '\tclip ' + best.dur.toFixed(3) + 's' : 'no translation channel'));
});
