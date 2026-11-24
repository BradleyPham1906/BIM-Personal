// as-tree-triangles.js: counts the triangles and vertices of an EZ-Tree-style recursive branching tree,
// written here from a reading of EZ-Tree 1.1.0's src/lib/tree.js (MIT, Daniel Greenheck) as text; EZ-Tree's own
// code is not run. Its presets (JSON data) are read as data.
// Usage: node as-tree-triangles.js <presets-dir>
// Model (from tree.js): a branch is a tube of `sections` rings of `segments`+1 vertices (the seam duplicated),
// (sections+1)*(segments+1) vertices and sections*segments*2 triangles, no caps. A branch of level L < levels has
// children[L] children of level L+1; for a deciduous tree it also has a terminal child of level L+1 carrying the
// parent's section and segment counts; at the last level a deciduous branch ends in one leaf and carries `count`
// leaves; an evergreen branch carries `count` leaves at the last level only. A leaf is one quad, or two crossed
// quads when billboard is 'double' (4 vertices and 2 triangles a quad). Indices are Uint16 in tree.js, so either
// mesh above 65,535 vertices would wrap.
'use strict';
var fs = require('fs'), path = require('path');
function count(o) {
  var B = o.branch, Lv = B.levels, dec = o.type === 'deciduous', q = o.leaves.billboard === 'double' ? 2 : 1;
  var r = { branches: 0, bv: 0, bt: 0, leaves: 0 };
  function br(L, sec, seg) {
    r.branches++; r.bv += (sec + 1) * (seg + 1); r.bt += sec * seg * 2;
    if (dec) { if (L < Lv) br(L + 1, sec, seg); else r.leaves += 1; }
    if (L === Lv) r.leaves += o.leaves.count;
    else for (var i = 0; i < B.children[L]; i++) br(L + 1, B.sections[L + 1], B.segments[L + 1]);
  }
  br(0, B.sections[0], B.segments[0]);
  r.lv = r.leaves * q * 4; r.lt = r.leaves * q * 2; r.tris = r.bt + r.lt;
  r.u16 = (r.bv > 65535 || r.lv > 65535) ? 'OVERFLOW' : 'ok';
  return r;
}
function clone(o) { return JSON.parse(JSON.stringify(o)); }
var dir = process.argv[2], rows = [];
fs.readdirSync(dir).filter(function (f) { return /\.json$/.test(f); }).sort().forEach(function (f) {
  var o = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')), r = count(o);
  rows.push([f.replace('.json', ''), o.type, o.branch.levels, r.branches, r.bt, r.leaves, r.lt, r.tris, r.bv, r.lv, r.u16].join('\t'));
});
console.log('preset\ttype\tlevels\tbranches\tbranchTris\tleaves\tleafTris\ttotalTris\tbranchVerts\tleafVerts\tuint16');
console.log(rows.join('\n'));
// three detail settings for one tree: the same preset with fewer rings and sides and leaves (low), as shipped
// (mid), and with doubled rings and leaves (high)
['oak_medium.json', 'pine_medium.json'].forEach(function (f) {
  var base = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  function lod(name, ks, kg, kl, single) {
    var o = clone(base), k;
    for (k in o.branch.sections) o.branch.sections[k] = Math.max(1, Math.round(o.branch.sections[k] * ks));
    for (k in o.branch.segments) o.branch.segments[k] = Math.max(3, Math.round(o.branch.segments[k] * kg));
    o.leaves.count = Math.max(1, Math.round(o.leaves.count * kl));
    if (single) o.leaves.billboard = 'single';
    var r = count(o);
    console.log([f + ' ' + name, r.branches, r.bt, r.leaves, r.lt, r.tris, r.bv, r.lv, r.u16].join('\t'));
  }
  console.log('\nLOD\tbranches\tbranchTris\tleaves\tleafTris\ttotalTris\tbranchVerts\tleafVerts\tuint16');
  lod('low (rings x0.5, sides min 3, leaves x0.25, single quad)', 0.5, 0.5, 0.25, true);
  lod('mid (as shipped)', 1, 1, 1, false);
  lod('high (rings x2, sides x1.5, leaves x2)', 2, 1.5, 2, false);
});
