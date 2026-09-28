'use strict';
// Phase 43 prototype: multi-flight stairs with landings/turns + stepped guard railings.
// Mirrors the in-app ES5 style and reuses the app's existing, already-tested corner-miter
// math (bimOffsetRing) for the landing footprint at a turn, instead of inventing new corner
// geometry. Coordinates are plan (x,z); the app is Y-up so elevation is applied on top.

function segNormal(a, b) {
  var dx = b[0] - a[0], dz = b[1] - a[1], len = Math.sqrt(dx * dx + dz * dz) || 1;
  return [-dz / len, dx / len];
}

// Verbatim port of the app's bimOffsetRing (open-polyline miter offset), so this prototype's
// landing corners match exactly what the shipped wall/roof code would produce for the same path.
function offsetRing(pts, dist, closed) {
  var n = pts.length, out = [], i;
  for (i = 0; i < n; i++) {
    if (!closed && (i === 0 || i === n - 1)) {
      var a = i === 0 ? pts[0] : pts[n - 2], b = i === 0 ? pts[1] : pts[n - 1];
      var nrm = segNormal(a, b);
      out.push([pts[i][0] + nrm[0] * dist, pts[i][1] + nrm[1] * dist]);
      continue;
    }
    var prev = pts[(i - 1 + n) % n], cur = pts[i], next = pts[(i + 1) % n];
    var n1 = segNormal(prev, cur), n2 = segNormal(cur, next);
    var mx = n1[0] + n2[0], mz = n1[1] + n2[1];
    var mlen = Math.sqrt(mx * mx + mz * mz) || 1; mx /= mlen; mz /= mlen;
    var cosH = (n1[0] * mx + n1[1] * mz);
    var scale = cosH > 0.15 ? 1 / cosH : 1; scale = Math.min(scale, 4);
    out.push([cur[0] + mx * dist * scale, cur[1] + mz * dist * scale]);
  }
  return out;
}

function cleanPath(pathIn) {
  var P = [], i;
  if (!pathIn || pathIn.length < 2) return null;
  for (i = 0; i < pathIn.length; i++) {
    var p = pathIn[i];
    if (!p || !isFinite(p[0]) || !isFinite(p[1])) return null;
    if (P.length) {
      var dx = p[0] - P[P.length - 1][0], dz = p[1] - P[P.length - 1][1];
      if (Math.sqrt(dx * dx + dz * dz) < 1e-9) continue;
    }
    P.push([p[0], p[1]]);
  }
  return P.length >= 2 ? P : null;
}

// Computes the shared "walk layout" used by both the solid-stair mesh and the railing mesh:
// segment table, landing zones (centered on each interior path vertex), and the ordered list
// of flat/rising profile entries (steps interleaved with landing flats, landings pre-split at
// their vertex so the true mitered corner point is used on both sides of a turn).
function buildStairLayout(pathIn, width, baseY, numSteps, riserH, treadD, landingLen) {
  var P = cleanPath(pathIn);
  if (!P) return { error: 'Stair path needs at least 2 distinct points' };
  if (!(width > 0)) return { error: 'Width must be a positive number' };
  if (!(numSteps > 0) || !(riserH > 0) || !(treadD > 0)) return { error: 'Stair needs a positive step count, riser height, and tread depth' };
  var hw = width / 2, n = P.length, i;
  var segs = [];
  for (i = 0; i < n - 1; i++) {
    var a = P[i], b = P[i + 1];
    var dx = b[0] - a[0], dz = b[1] - a[1], len = Math.sqrt(dx * dx + dz * dz);
    if (!(len > 1e-6)) return { error: 'Stair path has a zero-length segment' };
    segs.push({ a: a, b: b, len: len });
  }
  var cum = [0];
  for (i = 0; i < segs.length; i++) cum.push(cum[i] + segs[i].len);
  var total = cum[cum.length - 1];

  var landingHalf = landingLen / 2;
  var zones = [], k;
  for (k = 1; k <= n - 2; k++) zones.push({ vertex: k, vRun: cum[k], start: cum[k] - landingHalf, end: cum[k] + landingHalf });
  for (i = 0; i < segs.length; i++) {
    var need = 0;
    if (i > 0) need += landingHalf;
    if (i < segs.length - 1) need += landingHalf;
    if (segs[i].len < need - 1e-9) return { error: 'Segment ' + (i + 1) + ' is too short for a ' + landingLen.toFixed(2) + 'm landing at both ends' };
  }

  var ringL = offsetRing(P, hw, false), ringR = offsetRing(P, -hw, false);

  function segAt(run) {
    for (var s = 0; s < segs.length; s++) if (run <= cum[s + 1] + 1e-7) return s;
    return segs.length - 1;
  }
  function plainPt(run, side) {
    var s = segAt(run), seg = segs[s];
    var t = run - cum[s];
    var ux = (seg.b[0] - seg.a[0]) / seg.len, uz = (seg.b[1] - seg.a[1]) / seg.len;
    var px = seg.a[0] + ux * t, pz = seg.a[1] + uz * t;
    var nrm = segNormal(seg.a, seg.b);
    return [px + nrm[0] * hw * side, pz + nrm[1] * hw * side];
  }
  function cpt(run, side) {
    for (var zi = 0; zi < zones.length; zi++) {
      if (Math.abs(run - zones[zi].vRun) < 1e-7) return side > 0 ? ringL[zones[zi].vertex] : ringR[zones[zi].vertex];
    }
    return plainPt(run, side);
  }

  // Flights = the runs of path between landing zones (or between a path end and the nearest
  // zone). Steps are apportioned across flights by available length (largest-remainder method,
  // the same idea the app already uses for riserH: a *target* tread depth, adjusted to fit
  // exactly) rather than walking forward in fixed treadD increments and hoping the landings
  // land on a step boundary — that would make almost any hand-drawn path fail by a few
  // centimetres. Each flight's own treads come out uniform; different flights may differ
  // slightly from each other and from the requested target, exactly as riserH already can.
  var flightBounds = [], prevEnd = 0;
  for (k = 0; k < zones.length; k++) { flightBounds.push([prevEnd, zones[k].start]); prevEnd = zones[k].end; }
  flightBounds.push([prevEnd, total]);
  var flights = flightBounds.map(function (b) { return { start: b[0], end: b[1], len: b[1] - b[0] }; });
  var totalFlightLen = flights.reduce(function (s, f) { return s + f.len; }, 0);
  var minFlight = Math.min.apply(null, flights.map(function (f) { return f.len; }));
  if (minFlight < 1e-6) return { error: 'A landing leaves no room for a flight next to it — lengthen that segment or remove the turn' };
  if (numSteps < flights.length) return { error: 'Not enough steps (' + numSteps + ') to give each of the ' + flights.length + ' flights at least one tread — raise the rise or reduce landings' };

  var raw = flights.map(function (f) { return numSteps * f.len / totalFlightLen; });
  var counts = raw.map(Math.floor);
  var used = counts.reduce(function (s, c) { return s + c; }, 0);
  var remainder = numSteps - used;
  var order = raw.map(function (r, idx) { return { idx: idx, frac: r - Math.floor(r) }; }).sort(function (a, b) { return b.frac - a.frac; });
  for (i = 0; i < remainder; i++) counts[order[i % order.length].idx]++;
  for (i = 0; i < counts.length; i++) if (counts[i] < 1) return { error: 'Flight ' + (i + 1) + ' would get zero treads — raise the rise, reduce landings, or lengthen that run' };
  for (i = 0; i < flights.length; i++) flights[i].steps = counts[i];
  for (i = 0; i < flights.length; i++) flights[i].treadLocal = flights[i].len / flights[i].steps;
  var STAIR_MIN_TREAD = 0.15;
  for (i = 0; i < flights.length; i++) {
    if (flights[i].treadLocal < STAIR_MIN_TREAD - 1e-9) return {
      error: 'Stair path is too short: flight ' + (i + 1) + ' would need a ' + flights[i].treadLocal.toFixed(3) +
        'm tread depth (below the ' + STAIR_MIN_TREAD.toFixed(2) + 'm minimum) to fit ' + flights[i].steps +
        ' of the ' + numSteps + ' treads in ' + flights[i].len.toFixed(2) + 'm — lengthen the path or add a landing to split it up'
    };
  }

  var treads = [], stepIdx = 0, fi;
  for (fi = 0; fi < flights.length; fi++) {
    var fl = flights[fi], r = fl.start;
    for (i = 0; i < fl.steps; i++) {
      var nextR = r + fl.treadLocal;
      treads.push({ t: 'step', runStart: r, runEnd: nextR, riseStart: stepIdx * riserH, riseEnd: (stepIdx + 1) * riserH });
      r = nextR; stepIdx++;
    }
  }
  var finalRun = treads.length ? treads[treads.length - 1].runEnd : 0;
  var totalRise = numSteps * riserH;

  // Interleave: flight i's treads, then the landing right after that flight (if any).
  var prof = [], stepCursor = 0;
  for (fi = 0; fi < flights.length; fi++) {
    var stepsHere = flights[fi].steps;
    for (i = 0; i < stepsHere; i++) { prof.push(treads[stepCursor]); stepCursor++; }
    if (fi < zones.length) {
      var zone = zones[fi];
      var lastRise = prof[prof.length - 1].riseEnd;
      prof.push({ t: 'landing', runStart: zone.start, runEnd: zone.vRun, riseStart: lastRise, riseEnd: lastRise });
      prof.push({ t: 'landing', runStart: zone.vRun, runEnd: zone.end, riseStart: lastRise, riseEnd: lastRise });
    }
  }

  return {
    path: P, segs: segs, cum: cum, total: total, zones: zones, flights: flights, prof: prof,
    finalRun: finalRun, totalRise: totalRise, hw: hw, cpt: cpt,
    treadAvg: totalFlightLen / numSteps
  };
}

function weldMesh(rawFaces) {
  var vm = {}, verts = [], faces = [], i, j;
  function vid(p) {
    var k = p[0].toFixed(5) + ',' + p[1].toFixed(5) + ',' + p[2].toFixed(5);
    if (vm[k] === undefined) { vm[k] = verts.length; verts.push(p); }
    return vm[k];
  }
  for (i = 0; i < rawFaces.length; i++) {
    var f = [];
    for (j = 0; j < rawFaces[i].length; j++) f.push(vid(rawFaces[i][j]));
    faces.push(f);
  }
  return { v: verts, f: faces };
}

// Pushes a face after collapsing any consecutive (including wraparound) coincident vertices.
// A tight inner turn (a landing zone as wide as the corridor's own half-width pinches to a
// point exactly at the corner) legitimately degenerates some quads to triangles or to nothing
// on that side; dropping the repeated vertex keeps every remaining face non-degenerate instead
// of emitting a zero-area face with a self-loop edge.
function pushPoly(raw, pts) {
  var out = [], i;
  function same(a, b) { return Math.abs(a[0] - b[0]) < 1e-9 && Math.abs(a[1] - b[1]) < 1e-9 && Math.abs(a[2] - b[2]) < 1e-9; }
  for (i = 0; i < pts.length; i++) { if (!out.length || !same(out[out.length - 1], pts[i])) out.push(pts[i]); }
  while (out.length > 1 && same(out[0], out[out.length - 1])) out.pop();
  if (out.length >= 3) raw.push(out);
}

function buildStairPathMesh(pathIn, width, baseY, numSteps, riserH, treadD, landingLen) {
  var L = buildStairLayout(pathIn, width, baseY, numSteps, riserH, treadD, landingLen);
  if (L.error) return L;
  var prof = L.prof, cpt = L.cpt, raw = [], i, sd;
  function y3(xz, rise) { return [xz[0], baseY + rise, xz[1]]; }

  for (sd = -1; sd <= 1; sd += 2) {
    for (i = 0; i < prof.length; i++) {
      var e = prof[i];
      var blXZ = cpt(e.runStart, sd), brXZ = cpt(e.runEnd, sd);
      var bl = y3(blXZ, 0), br = y3(brXZ, 0);
      var tr = y3(brXZ, e.riseEnd), tl = y3(blXZ, e.riseEnd);
      var flat = Math.abs(e.riseEnd - e.riseStart) < 1e-9;
      if (i === 0 || flat) {
        if (sd < 0) { pushPoly(raw, [bl, br, tr]); pushPoly(raw, [bl, tr, tl]); }
        else { pushPoly(raw, [bl, tr, br]); pushPoly(raw, [bl, tl, tr]); }
      } else {
        var ml = y3(blXZ, e.riseStart);
        if (sd < 0) { pushPoly(raw, [bl, br, tr]); pushPoly(raw, [bl, tr, ml]); pushPoly(raw, [ml, tr, tl]); }
        else { pushPoly(raw, [bl, tr, br]); pushPoly(raw, [bl, ml, tr]); pushPoly(raw, [ml, tl, tr]); }
      }
    }
  }
  for (i = 0; i < prof.length; i++) {
    var e2 = prof[i];
    pushPoly(raw, [y3(cpt(e2.runEnd, -1), 0), y3(cpt(e2.runStart, -1), 0), y3(cpt(e2.runStart, 1), 0), y3(cpt(e2.runEnd, 1), 0)]);
    pushPoly(raw, [y3(cpt(e2.runStart, -1), e2.riseEnd), y3(cpt(e2.runEnd, -1), e2.riseEnd), y3(cpt(e2.runEnd, 1), e2.riseEnd), y3(cpt(e2.runStart, 1), e2.riseEnd)]);
    if (Math.abs(e2.riseEnd - e2.riseStart) > 1e-9) {
      pushPoly(raw, [y3(cpt(e2.runStart, -1), e2.riseStart), y3(cpt(e2.runStart, -1), e2.riseEnd), y3(cpt(e2.runStart, 1), e2.riseEnd), y3(cpt(e2.runStart, 1), e2.riseStart)]);
    }
  }
  pushPoly(raw, [y3(cpt(L.finalRun, 1), 0), y3(cpt(L.finalRun, 1), L.totalRise), y3(cpt(L.finalRun, -1), L.totalRise), y3(cpt(L.finalRun, -1), 0)]);

  // Global orientation flip: the per-face windings above are internally consistent (every
  // undirected edge is already shared by exactly two faces with no duplicated direction), but
  // come out net inward. Reversing every face flips overall handedness to outward without
  // touching that already-correct topology.
  raw = raw.map(function (f) { return f.slice().reverse(); });
  var m = weldMesh(raw);
  return { mesh: m, layout: L };
}

// Stepped guard railing: a top rail following the tread/landing nosing line (jumping at each
// riser, flat across treads/landings, matching the stair's own stepped profile rather than a
// continuously sloped rail), plus a vertical post under each waypoint. Built from small boxes
// so it's real, dimensioned geometry (not a decal) without needing a second offset-ring pass.
function boxBetween3D(p1, p2, thick) {
  var ax = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]];
  var len = Math.sqrt(ax[0] * ax[0] + ax[1] * ax[1] + ax[2] * ax[2]);
  if (!(len > 1e-9)) return null;
  ax = [ax[0] / len, ax[1] / len, ax[2] / len];
  var refUp = Math.abs(ax[1]) > 0.9 ? [1, 0, 0] : [0, 1, 0];
  function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function norm(a) { var l = Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }
  var side = norm(cross(ax, refUp));
  var up2 = norm(cross(side, ax));
  var h = thick / 2;
  function corner(p, s, u) { return [p[0] + side[0] * s * h + up2[0] * u * h, p[1] + side[1] * s * h + up2[1] * u * h, p[2] + side[2] * s * h + up2[2] * u * h]; }
  var v = [
    corner(p1, -1, -1), corner(p1, 1, -1), corner(p1, 1, 1), corner(p1, -1, 1),
    corner(p2, -1, -1), corner(p2, 1, -1), corner(p2, 1, 1), corner(p2, -1, 1)
  ];
  var f = [
    [0, 1, 2, 3], [7, 6, 5, 4],
    [4, 5, 1, 0], [5, 6, 2, 1], [6, 7, 3, 2], [7, 4, 0, 3]
  ];
  return { v: v, f: f };
}

function buildStairGuardMesh(layout, baseY, side, railHeight, railThick, postThick) {
  var prof = layout.prof, cpt = layout.cpt, i;
  var kf = [];
  // Dedup by the ACTUAL resulting 3D point, not the raw (run,rise) pair: at a pinched landing
  // corner (landingLen equal to the corridor width) two different run values can land on the same
  // mitered corner point once passed through cpt -- the same pinch already handled for the main
  // stair mesh via pushPoly. Deduping on (run,rise) alone would place two coincident posts.
  function pushKf(run, rise) {
    var xz = cpt(run, side), pt = [xz[0], rise, xz[1]];
    var last = kf[kf.length - 1];
    if (last && Math.abs(last.pt[0] - pt[0]) < 1e-9 && Math.abs(last.pt[1] - pt[1]) < 1e-9 && Math.abs(last.pt[2] - pt[2]) < 1e-9) return;
    kf.push({ run: run, rise: rise, pt: pt });
  }
  pushKf(prof[0].runStart, prof[0].riseStart);
  for (i = 0; i < prof.length; i++) {
    pushKf(prof[i].runStart, prof[i].riseEnd);
    pushKf(prof[i].runEnd, prof[i].riseEnd);
  }
  function kf3(k, extra) {
    return [k.pt[0], baseY + k.pt[1] + (extra || 0), k.pt[2]];
  }
  // Rails only span flat (same-rise) keyframe pairs; a same-run vertical jump at a riser sits
  // entirely inside the taller adjoining post (identical vertical axis and local frame, fully
  // overlapping range), so a rail box there would only duplicate that post's own cap face.
  var flatPairs = [];
  for (i = 0; i < kf.length - 1; i++) {
    if (Math.abs(kf[i + 1].rise - kf[i].rise) > 1e-9) continue;
    flatPairs.push({ a: i, b: i + 1 });
  }
  // Adjacent flat pairs continuing in the exact same direction (a straight run of several
  // treads, or two landing sub-segments that stay collinear at a wide-miter turn) are merged
  // into one box before building. Chaining separate boxes end to end instead leaves an internal
  // cap at every junction whose vertex numbering, once welded, exactly collides in direction
  // with the next box's own side face -- a genuine duplicated half-edge, not a harmless seam.
  function segDir3(ia, ib) {
    var A = kf3(kf[ia], railHeight), B = kf3(kf[ib], railHeight);
    var dx = B[0] - A[0], dy = B[1] - A[1], dz = B[2] - A[2], len = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
    return [dx / len, dy / len, dz / len];
  }
  var mergedPairs = [];
  for (i = 0; i < flatPairs.length; i++) {
    var curP = flatPairs[i];
    if (mergedPairs.length) {
      var lastP = mergedPairs[mergedPairs.length - 1];
      if (lastP.b === curP.a) {
        var d1 = segDir3(lastP.a, lastP.b), d2 = segDir3(curP.a, curP.b);
        var cx = d1[1] * d2[2] - d1[2] * d2[1], cy = d1[2] * d2[0] - d1[0] * d2[2], cz = d1[0] * d2[1] - d1[1] * d2[0];
        if (Math.sqrt(cx * cx + cy * cy + cz * cz) < 1e-6) { lastP.b = curP.b; continue; }
      }
    }
    mergedPairs.push({ a: curP.a, b: curP.b });
  }
  var raw = [], boxCount = 0, postCount = 0;
  for (i = 0; i < mergedPairs.length; i++) {
    var a = kf3(kf[mergedPairs[i].a], railHeight), b = kf3(kf[mergedPairs[i].b], railHeight);
    var box = boxBetween3D(a, b, railThick);
    if (box) { for (var j = 0; j < box.f.length; j++) raw.push(box.f[j].map(function (idx) { return box.v[idx]; })); boxCount++; }
  }
  for (i = 0; i < kf.length; i++) {
    var top = kf3(kf[i], railHeight), bot = kf3(kf[i], 0);
    var post = boxBetween3D(bot, top, postThick);
    if (post) { for (var j2 = 0; j2 < post.f.length; j2++) raw.push(post.f[j2].map(function (idx) { return post.v[idx]; })); postCount++; }
  }
  return { mesh: weldMesh(raw), rails: boxCount, posts: postCount };
}

module.exports = {
  segNormal: segNormal, offsetRing: offsetRing, cleanPath: cleanPath,
  buildStairLayout: buildStairLayout, buildStairPathMesh: buildStairPathMesh,
  boxBetween3D: boxBetween3D, buildStairGuardMesh: buildStairGuardMesh, weldMesh: weldMesh
};
