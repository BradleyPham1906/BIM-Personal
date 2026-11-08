/* V174 research experiment: align, distribute and tidy up on boxes {x,y,w,h} (ES5). Data for research.
   Methods, by source (levels in layout.md):
   - align to the selection's bounds, to a key object (it stays), or to the parent; one box aligns to its
     parent (Figma, help article 360039956914);
   - distribute by centres: the first and last centres stay, the others step equally (Inkscape's method,
     src/actions/actions-object-align.cpp, GPL-2+, read for the method only);
   - distribute by equal gaps, two readings of "the outermost objects keep their position":
       'gaps-centre': sorted by centre, from the first's min edge to the last's max edge (Inkscape);
       'gaps-edge':   the box with the least min edge and the box with the greatest max edge stay,
                      the rest sorted by min edge between them (our reading of Figma's sentence);
   - tidy up in one dimension: sorted by min edge, the most common gap (the mode, rounded to 1) between
     all, the first stays (Figma: "the most common spacing in the selection");
   - a rotated box is aligned by its axis-aligned bounding box. */
(function (root) {
  'use strict';
  function aabb(b) {
    var t = (b.rot || 0) * Math.PI / 180, c = Math.abs(Math.cos(t)), s = Math.abs(Math.sin(t));
    var W = b.w * c + b.h * s, H = b.w * s + b.h * c, cx = b.x + b.w / 2, cy = b.y + b.h / 2;
    return { x: cx - W / 2, y: cy - H / 2, w: W, h: H };
  }
  function union(L) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, i, b;
    for (i = 0; i < L.length; i++) { b = L[i]; x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.w); y1 = Math.max(y1, b.y + b.h); }
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }
  var EDGE = { left: ['x', 'w', 0], hcenter: ['x', 'w', 0.5], right: ['x', 'w', 1], top: ['y', 'h', 0], vcenter: ['y', 'h', 0.5], bottom: ['y', 'h', 1] };
  /* boxes moved by their bounding boxes; returns new {x,y} for each (w, h, rot unchanged) */
  function align(boxes, edge, to, keyIdx, parent) {
    var E = EDGE[edge], bb = boxes.map(aabb), T;
    if (boxes.length === 1 && to === 'selection') to = 'parent';
    if (to === 'key') T = bb[keyIdx];
    else if (to === 'parent') T = parent;
    else T = union(bb);
    var target = T[E[0]] + T[E[1]] * E[2];
    return boxes.map(function (b, i) {
      if (to === 'key' && i === keyIdx) return { x: b.x, y: b.y };
      var d = target - (bb[i][E[0]] + bb[i][E[1]] * E[2]), r = { x: b.x, y: b.y };
      r[E[0]] += d;
      return r;
    });
  }
  function order(bb, key) { var ix = bb.map(function (b, i) { return i; }); ix.sort(function (a, b) { return key(bb[a]) - key(bb[b]) || a - b; }); return ix; }
  function distribute(boxes, axis, mode) {
    var P = axis === 'x' ? 'x' : 'y', S = axis === 'x' ? 'w' : 'h', bb = boxes.map(aabb), out = boxes.map(function (b) { return { x: b.x, y: b.y }; });
    if (boxes.length < 3) return { pos: out, step: null };
    var ix, i, step, pos;
    if (mode === 'centres') {
      ix = order(bb, function (b) { return b[P] + b[S] / 2; });
      var c0 = bb[ix[0]][P] + bb[ix[0]][S] / 2, c1 = bb[ix[ix.length - 1]][P] + bb[ix[ix.length - 1]][S] / 2;
      step = (c1 - c0) / (ix.length - 1);
      for (i = 0; i < ix.length; i++) out[ix[i]][P] += (c0 + i * step) - (bb[ix[i]][P] + bb[ix[i]][S] / 2);
      return { pos: out, step: step };
    }
    if (mode === 'gaps-centre') ix = order(bb, function (b) { return b[P] + b[S] / 2; });
    else {
      var lo = 0, hi = 0;
      for (i = 1; i < bb.length; i++) { if (bb[i][P] < bb[lo][P]) lo = i; if (bb[i][P] + bb[i][S] > bb[hi][P] + bb[hi][S]) hi = i; }
      ix = order(bb, function (b) { return b[P]; }).filter(function (k) { return k !== lo && k !== hi; });
      ix.unshift(lo); if (hi !== lo) ix.push(hi);
    }
    var span = 0, first = bb[ix[0]], last = bb[ix[ix.length - 1]];
    for (i = 0; i < ix.length; i++) span += bb[ix[i]][S];
    step = (last[P] + last[S] - first[P] - span) / (ix.length - 1);
    pos = first[P];
    for (i = 0; i < ix.length; i++) { out[ix[i]][P] += pos - bb[ix[i]][P]; pos += bb[ix[i]][S] + step; }
    return { pos: out, step: step };
  }
  function tidy1(boxes, axis) {
    var P = axis === 'x' ? 'x' : 'y', S = axis === 'x' ? 'w' : 'h', bb = boxes.map(aabb), ix = order(bb, function (b) { return b[P]; });
    var count = {}, best = null, i, g;
    for (i = 1; i < ix.length; i++) {
      g = Math.round(bb[ix[i]][P] - (bb[ix[i - 1]][P] + bb[ix[i - 1]][S]));
      count[g] = (count[g] || 0) + 1;
      if (best === null || count[g] > count[best] || (count[g] === count[best] && g < best)) best = g;
    }
    var out = boxes.map(function (b) { return { x: b.x, y: b.y }; }), pos = bb[ix[0]][P];
    for (i = 0; i < ix.length; i++) { out[ix[i]][P] += pos - bb[ix[i]][P]; pos += bb[ix[i]][S] + (best || 0); }
    return { pos: out, gap: best };
  }
  root.alAabb = aabb; root.alAlign = align; root.alDistribute = distribute; root.alTidy1 = tidy1; root.alUnion = union;
})(typeof module !== 'undefined' ? module.exports : this);
