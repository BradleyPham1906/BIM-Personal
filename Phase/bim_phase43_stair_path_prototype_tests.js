'use strict';
var S = require('./bim_phase43_stair_path_prototype.js');

var fails = 0, checks = 0;
function ok(c, m) { checks++; if (!c) { fails++; console.log('  FAIL: ' + m); } }

function topo(m) {
  var und = {}, dir = {}, dup = 0, bad = 0, vol = 0, i, k;
  m.f.forEach(function (f) {
    for (i = 0; i < f.length; i++) {
      var a = f[i], b = f[(i + 1) % f.length];
      if (a === b) bad++;
      var uk = Math.min(a, b) + '-' + Math.max(a, b); und[uk] = (und[uk] || 0) + 1;
      var dk = a + '>' + b; dir[dk] = (dir[dk] || 0) + 1;
    }
    for (i = 1; i + 1 < f.length; i++) {
      var A = m.v[f[0]], B = m.v[f[i]], C = m.v[f[i + 1]];
      vol += (A[0] * (B[1] * C[2] - B[2] * C[1]) - A[1] * (B[0] * C[2] - B[2] * C[0]) + A[2] * (B[0] * C[1] - B[1] * C[0])) / 6;
    }
  });
  for (k in dir) if (dir[k] > 1) dup++;
  for (k in und) if (und[k] !== 2) bad++;
  return { dup: dup, bad: bad, vol: vol, faces: m.f.length, verts: m.v.length };
}

function checkStair(name, path, width, baseY, numSteps, riserH, treadD, landingLen) {
  console.log(name);
  var r = S.buildStairPathMesh(path, width, baseY, numSteps, riserH, treadD, landingLen);
  if (r.error) { fails++; checks++; console.log('  FAIL: unexpected error: ' + r.error); return null; }
  var t = topo(r.mesh);
  ok(t.dup === 0, name + ': no duplicated half-edge (' + t.dup + ')');
  ok(t.bad === 0, name + ': every edge shared by exactly two faces (' + t.bad + ' bad)');
  ok(t.vol > 0, name + ': positive (outward) volume, got ' + t.vol.toFixed(4));
  console.log('  faces=' + t.faces + ' verts=' + t.verts + ' vol=' + t.vol.toFixed(4) +
    ' flights=' + r.layout.flights.length + ' landings=' + r.layout.zones.length);
  return r;
}

console.log('=== straight single flight (no landings, legacy-equivalent shape) ===');
var r1 = checkStair('straight 3m rise', [[0, 0], [0, 6]], 1.2, 0, 17, 3 / 17, 6 / 17, 1.2);
if (r1) {
  ok(r1.layout.flights.length === 1, 'single flight, no landings');
  ok(r1.layout.zones.length === 0, 'zero landing zones for a 2-point path');
  var ys = r1.mesh.v.map(function (p) { return p[1]; });
  ok(Math.abs(Math.max.apply(null, ys) - 3) < 1e-6, 'top of stair reaches total rise (3m)');
  ok(Math.abs(Math.min.apply(null, ys) - 0) < 1e-6, 'bottom of stair sits at baseY (0)');
}

console.log('\n=== L-shaped stair, one 90-degree turn + landing ===');
var r2 = checkStair('L-turn', [[0, 0], [0, 4], [3, 4]], 1.0, 0, 16, 3 / 16, 0.28, 1.0);
if (r2) {
  ok(r2.layout.flights.length === 2, 'two flights either side of the turn');
  ok(r2.layout.zones.length === 1, 'one landing at the turn');
  var landingRise = r2.layout.prof.filter(function (e) { return e.t === 'landing'; })[0].riseStart;
  ok(landingRise > 0 && landingRise < r2.layout.totalRise, 'landing sits partway up the total rise (' + landingRise.toFixed(3) + ')');
  var landingEntries = r2.layout.prof.filter(function (e) { return e.t === 'landing'; });
  ok(landingEntries.length === 2, 'landing is represented as two sub-entries split at the true mitered corner');
  ok(Math.abs(landingEntries[0].riseStart - landingEntries[1].riseStart) < 1e-9, 'both landing sub-entries share the same flat rise');
}

console.log('\n=== U-shaped (two turns, three flights) ===');
var r3 = checkStair('U-shape', [[0, 0], [0, 5], [2.4, 5], [2.4, 0]], 1.2, 0, 24, 3.2 / 24, 0.28, 1.2);
if (r3) {
  ok(r3.layout.flights.length === 3, 'three flights for two turns');
  ok(r3.layout.zones.length === 2, 'two landings for two turns');
}

console.log('\n=== apportionment: uneven flight lengths still tile exactly ===');
var r4 = checkStair('uneven flights', [[0, 0], [0, 3], [10, 3]], 1.0, 0, 20, 3.4 / 20, 0.3, 1.0);
if (r4) {
  var f = r4.layout.flights;
  ok(f[0].steps + f[1].steps === 20, 'all steps accounted for across flights (' + f[0].steps + '+' + f[1].steps + ')');
  ok(f[1].steps > f[0].steps, 'the longer flight (10m) gets more steps than the shorter (3m minus landing)');
}

console.log('\n=== fail-safe rejections ===');
var bad1 = S.buildStairLayout([[0, 0], [0, 0.3], [3, 0.3]], 1.0, 0, 16, 0.18, 0.28, 1.0);
ok(!!bad1.error, 'a segment too short for its landing is refused, not silently squeezed (' + (bad1.error || 'no error') + ')');

var bad2 = S.buildStairLayout([[0, 0], [0, 1]], 1.0, 0, 16, 0.18, 0.28, 1.0);
ok(!!bad2.error, 'not enough path length is refused rather than producing overlapping treads (' + (bad2.error || 'no error') + ')');

var bad3 = S.buildStairLayout([[0, 0], [0, 2], [1, 2], [1, 4], [2, 4]], 1.0, 0, 3, 1, 1, 1.0);
ok(!!bad3.error, 'too few steps for the number of flights is refused (' + (bad3.error || 'no error') + ')');

var bad4 = S.buildStairLayout([[0, 0], [0, 0]], 1.0, 0, 16, 0.18, 0.28, 1.0);
ok(!!bad4.error, 'a degenerate (duplicate-point) path is refused');

console.log('\n=== guard railing ===');
// boxBetween3D is the shared primitive (posts and rail segments alike); verify it in isolation
// for both a horizontal and a vertical link before trusting the assembled guard.
(function () {
  var hbox = S.boxBetween3D([0, 1, 0], [2, 1, 0], 0.1);
  var ht = topo(hbox);
  ok(ht.dup === 0 && ht.bad === 0, 'boxBetween3D (horizontal): watertight manifold');
  ok(Math.abs(ht.vol - 2 * 0.1 * 0.1) < 1e-9, 'boxBetween3D (horizontal): volume = length x thick^2 (' + ht.vol.toFixed(6) + ')');
  var vbox = S.boxBetween3D([0, 0, 0], [0, 0.9, 0], 0.05);
  var vt = topo(vbox);
  ok(vt.dup === 0 && vt.bad === 0, 'boxBetween3D (vertical post): watertight manifold');
  ok(Math.abs(vt.vol - 0.9 * 0.05 * 0.05) < 1e-9, 'boxBetween3D (vertical post): volume = height x thick^2 (' + vt.vol.toFixed(6) + ')');
  ok(S.boxBetween3D([1, 1, 1], [1, 1, 1], 0.1) === null, 'boxBetween3D refuses a zero-length link rather than emitting garbage');
})();

var r5 = checkStair('railing host: L-turn', [[0, 0], [0, 4], [3, 4]], 1.0, 0, 16, 3 / 16, 0.28, 1.0);
if (r5) {
  // The assembled guard is a union of many individually-watertight boxes (posts + stepped rail
  // segments) that touch at their joints — the real app CSG-unions these into one true solid
  // via its already-proven csgUnion kernel (not reproduced here); this prototype checks the
  // per-box primitive and the overall assembly shape instead of a naive weld of touching boxes.
  var g = S.buildStairGuardMesh(r5.layout, 0, 1, 0.9, 0.05, 0.05);
  ok(g.posts > r5.layout.prof.length, 'at least one post per profile waypoint, more where risers add a jump (' + g.posts + ')');
  // Rails only span flat (same-rise) keyframe pairs -- a vertical riser jump is already fully
  // covered by the taller adjoining post's own extent, so building a rail there would only
  // duplicate that post's cap face. Every post still gets a flat rail on at least one side
  // (fewer rails than posts-1, since consecutive posts across a riser jump are deliberately
  // not directly connected).
  ok(g.rails > 0 && g.rails < g.posts, 'flat rail segments connect same-rise posts only, verticals left to the posts (' + g.rails + ' rails, ' + g.posts + ' posts)');
  var railYs = g.mesh.v.map(function (p) { return p[1]; });
  // The keyframe path sits at nominal railHeight above each tread; boxBetween3D extends the
  // physical rail centered on that centerline, so its outer surface is another half-thickness higher.
  ok(Math.abs(Math.max.apply(null, railYs) - (r5.layout.totalRise + 0.9 + 0.025)) < 1e-6,
    'top of railing sits railHeight + half its own thickness above the top tread (' + Math.max.apply(null, railYs).toFixed(4) + ')');
  ok(Math.abs(Math.min.apply(null, railYs) - 0) < 1e-6, 'posts reach down to the tread/landing surface (min y = 0)');
}

console.log('\n' + (checks - fails) + '/' + checks + ' assertions passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
