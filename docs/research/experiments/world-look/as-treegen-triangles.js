// as-treegen-triangles.js: the triangle and vertex counts of three.js 0.186.1's examples/jsm/generators/TreeGenerator.js
// (MIT), worked out from its growBranch() and createGeometry() read as text; three's code is not run. With its
// defaults (lengthVariance 0, branchLengthFalloff 0) the counts do not depend on the seed: a tube of length L has
// clamp(round(L / sectionLength), 3, 24) sections, so sections + 1 rings, of max(3, radialSegments - level) vertices
// (no duplicated seam, no caps), and (rings - 1) * radial * 2 triangles; a tube recurses while level < levels - 1
// and L >= minLength, into children[level] children of length L * lengthRatio. It makes branches only (no leaves).
// Usage: node as-treegen-triangles.js
'use strict';
var D = { levels: 4, children: [3, 12, 8], lengthRatio: 0.62, trunkLength: 9, minLength: 0.6, radialSegments: 6, sectionLength: 1.3 };
function count(p) {
  var r = { tubes: 0, v: 0, t: 0 };
  (function grow(L, level) {
    var sec = Math.max(3, Math.min(24, Math.round(L / p.sectionLength))), rad = Math.max(3, p.radialSegments - level);
    r.tubes++; r.v += (sec + 1) * rad; r.t += sec * rad * 2;
    if (level >= p.levels - 1 || L < p.minLength) return;
    var n = p.children[Math.min(level, p.children.length - 1)];
    for (var i = 0; i < n; i++) grow(L * p.lengthRatio, level + 1);
  })(p.trunkLength, 0);
  return r;
}
function with_(o) { var p = JSON.parse(JSON.stringify(D)), k; for (k in o) p[k] = o[k]; return p; }
[['levels 3 (trunk, branch, twig)', { levels: 3 }], ['levels 4 (defaults)', {}], ['levels 5, children [3,12,8,4]', { levels: 5, children: [3, 12, 8, 4] }],
 ['defaults, radialSegments 4', { radialSegments: 4 }], ['defaults, trunkLength 20 (a 20 m tree)', { trunkLength: 20 }]].forEach(function (c) {
  var r = count(with_(c[1]));
  console.log(c[0] + '\ttubes ' + r.tubes + '\tverts ' + r.v + '\ttris ' + r.t + '\tindex ' + (r.v > 65535 ? 'Uint32' : 'Uint16'));
});
