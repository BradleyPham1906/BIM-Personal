/* V174 research experiment (2026-11-08): a light auto layout, written in ES5 from Figma's documented
   behaviour (help.figma.com "Guide to auto layout", "Use the horizontal and vertical flows in auto layout",
   and the Plugin API typings, figma/plugin-typings 1.142.0, MIT). Data for research, not app code.

   A frame:  {dir:'row'|'column', wrap:bool, gap:number|'auto', auto:'between'|'evenly'|'around',
              crossGap:number>=0, pad:[t,r,b,l], alignMain:'start'|'center'|'end',
              alignCross:'start'|'center'|'end', alignContent:'auto'|'between' (wrap only),
              sizeW:'fixed'|'hug', sizeH:'fixed'|'hug', w, h, minW, maxW, minH, maxH,
              reverseZ:bool, children:[...]}
   A child:  {w, h, sizeW:'fixed'|'fill'|'hug', sizeH, minW, maxW, minH, maxH, hidden, absolute, x, y}
             (a child with children is a nested frame; 'hug' is valid only for one)
   Result:   {w, h, kids:[{x,y,w,h} or null when hidden], z:[child indexes, bottom to top],
              hugToFixed:['w'|'h'...], lines:n}
   The rules, each from a source (levels in layout.md):
   - hidden children leave the flow; absolute ("ignore auto layout") children leave it and keep x, y;
   - Fill on the main axis shares the free space equally from a basis of 0 (flex: 1 1 0), clamped by
     min and max with the freeze loop of css-flexbox-1 section 9.7; fixed children never shrink;
   - Fill on the cross axis stretches to the line, clamped by min and max;
   - a hug frame with a Fill child on an axis is fixed on that axis (Figma's documented rule);
   - a frame is never smaller than its padding;
   - auto gap: between, evenly, around, never below 0; one child in an auto-gap stack sits at the start;
   - numeric gap may be negative on the main axis; the gap between wrapped tracks may not;
   - wrap breaks before the first item that would not fit (its fixed size, or its min for Fill);
   - wrapped tracks are as tall as their tallest child and are placed as the cross alignment says
     ('auto'), or spread ('between', never below 0);
   - min wins over max when they conflict (CSS). */
(function (root) {
  'use strict';
  var EPS = 1e-9;
  function num(v, d) { return typeof v === 'number' && isFinite(v) ? v : d; }
  function clamp(v, lo, hi) {
    if (typeof hi === 'number' && v > hi) v = hi;
    if (typeof lo === 'number' && v < lo) v = lo;
    return v;
  }
  function pads(F) {
    var p = F.pad;
    if (typeof p === 'number') return [p, p, p, p];
    if (!p) return [0, 0, 0, 0];
    return [num(p[0], 0), num(p[1], 0), num(p[2], 0), num(p[3], 0)];
  }
  /* axis helpers: main 'w' for a row */
  function ax(F) {
    var row = F.dir !== 'column';
    return { row: row, M: row ? 'w' : 'h', C: row ? 'h' : 'w',
      sM: row ? 'sizeW' : 'sizeH', sC: row ? 'sizeH' : 'sizeW',
      minM: row ? 'minW' : 'minH', maxM: row ? 'maxW' : 'maxH',
      minC: row ? 'minH' : 'minW', maxC: row ? 'maxH' : 'maxW' };
  }
  function hasKids(c) { return c && c.children && c.children.length >= 0 && Object.prototype.toString.call(c.children) === '[object Array]'; }
  /* a child's own size on an axis when it is not Fill: fixed, or its hug size if it is a frame */
  function ownSize(c, k) {
    var s = k === 'w' ? c.sizeW : c.sizeH;
    if (s === 'hug' && hasKids(c)) { var r = layout(c); return k === 'w' ? r.w : r.h; }
    return num(c[k], 0);
  }
  /* css-flexbox-1 9.7, grow case only (fixed items are inflexible; Fill has basis 0, grow 1) */
  function resolveFill(items, free0) {
    var i, it, frozenAll, rem, sumF, viol, total;
    for (i = 0; i < items.length; i++) { it = items[i]; it.target = it.basis; it.frozen = !it.fill; }
    for (;;) {
      frozenAll = true;
      for (i = 0; i < items.length; i++) if (!items[i].frozen) frozenAll = false;
      if (frozenAll) break;
      rem = free0;
      sumF = 0;
      for (i = 0; i < items.length; i++) {
        it = items[i];
        rem -= it.frozen ? it.target : it.basis;
        if (!it.frozen) sumF += 1;
      }
      if (rem > 0) for (i = 0; i < items.length; i++) { it = items[i]; if (!it.frozen) it.target = it.basis + rem / sumF; }
      else for (i = 0; i < items.length; i++) { it = items[i]; if (!it.frozen) it.target = it.basis; }
      total = 0;
      for (i = 0; i < items.length; i++) {
        it = items[i];
        if (it.frozen) continue;
        var cl = clamp(it.target, it.min, it.max);
        if (cl < 0) cl = 0;
        it.viol = cl - it.target;
        total += it.viol;
        it.target = cl;
      }
      for (i = 0; i < items.length; i++) {
        it = items[i];
        if (it.frozen) continue;
        if (Math.abs(total) < EPS) it.frozen = true;
        else if (total > 0 && it.viol > EPS) it.frozen = true;
        else if (total < 0 && it.viol < -EPS) it.frozen = true;
      }
    }
  }
  function layout(F, forceW, forceH) {
    var A = ax(F), P = pads(F), kids = F.children || [], out = { w: 0, h: 0, kids: [], z: [], hugToFixed: [], lines: 0 };
    var padM = A.row ? P[3] + P[1] : P[0] + P[2], padC = A.row ? P[0] + P[2] : P[3] + P[1];
    var padMs = A.row ? P[3] : P[0], padCs = A.row ? P[0] : P[3];
    var flow = [], i, c, anyFillM = false, anyFillC = false;
    for (i = 0; i < kids.length; i++) {
      c = kids[i];
      out.kids.push(null);
      if (c.hidden) continue;
      if (c.absolute) { out.kids[i] = { x: num(c.x, 0), y: num(c.y, 0), w: ownSize(c, 'w'), h: ownSize(c, 'h') }; continue; }
      flow.push(i);
      if (c[A.sM] === 'fill') anyFillM = true;
      if (c[A.sC] === 'fill') anyFillC = true;
    }
    /* the frame's sizing on each axis */
    var sM = F[A.sM] === 'hug' ? 'hug' : 'fixed', sC = F[A.sC] === 'hug' ? 'hug' : 'fixed';
    if (sM === 'hug' && anyFillM) { sM = 'fixed'; out.hugToFixed.push(A.M); }
    if (sC === 'hug' && anyFillC) { sC = 'fixed'; out.hugToFixed.push(A.C); }
    var fM = A.row ? forceW : forceH, fC = A.row ? forceH : forceW;
    if (typeof fM === 'number') sM = 'fixed';
    if (typeof fC === 'number') sC = 'fixed';
    var outerM = sM === 'fixed' ? clamp(typeof fM === 'number' ? fM : num(F[A.M], 0), F[A.minM], F[A.maxM]) : null;
    var outerC = sC === 'fixed' ? clamp(typeof fC === 'number' ? fC : num(F[A.C], 0), F[A.minC], F[A.maxC]) : null;
    if (outerM !== null && outerM < padM) outerM = padM;
    if (outerC !== null && outerC < padC) outerC = padC;
    var autoGap = F.gap === 'auto', gap = autoGap ? 0 : num(F.gap, 0);
    var crossGap = Math.max(0, num(F.crossGap, typeof F.gap === 'number' ? Math.max(0, F.gap) : 0));
    var wrap = !!F.wrap && sM === 'fixed';
    var innerM = outerM === null ? Infinity : outerM - padM;
    /* items with their hypothetical main size */
    var items = [];
    for (i = 0; i < flow.length; i++) {
      c = kids[flow[i]];
      var fill = c[A.sM] === 'fill';
      var it = { idx: flow[i], c: c, fill: fill, min: c[A.minM], max: c[A.maxM] };
      it.basis = fill ? 0 : clamp(ownSize(c, A.M), c[A.minM], c[A.maxM]);
      it.hyp = fill ? Math.max(0, clamp(0, c[A.minM], c[A.maxM])) : it.basis;
      it.fillC = c[A.sC] === 'fill';
      it.cross = it.fillC ? Math.max(0, clamp(0, c[A.minC], c[A.maxC])) : clamp(ownSize(c, A.C), c[A.minC], c[A.maxC]);
      items.push(it);
    }
    /* lines */
    var lines = [], cur = [], used = 0;
    for (i = 0; i < items.length; i++) {
      var add = items[i].hyp + (cur.length ? gap : 0);
      if (wrap && cur.length && used + add > innerM + EPS) { lines.push(cur); cur = []; used = 0; add = items[i].hyp; }
      cur.push(items[i]); used += add;
    }
    if (cur.length || !lines.length) lines.push(cur);
    out.lines = items.length ? lines.length : 0;
    /* main sizes per line */
    var li, L, j, maxLineM = 0;
    for (li = 0; li < lines.length; li++) {
      L = lines[li];
      var gaps = L.length > 1 ? gap * (L.length - 1) : 0;
      if (innerM !== Infinity) resolveFill(L, innerM - gaps);
      else for (j = 0; j < L.length; j++) L[j].target = L[j].fill ? L[j].hyp : L[j].basis;
      var sumM = gaps;
      for (j = 0; j < L.length; j++) sumM += L[j].target;
      L.sumM = sumM;
      if (sumM > maxLineM) maxLineM = sumM;
      var lc = 0;
      for (j = 0; j < L.length; j++) if (L[j].cross > lc) lc = L[j].cross;
      L.cross = lc;
    }
    if (outerM === null) { outerM = clamp(maxLineM + padM, F[A.minM], F[A.maxM]); if (outerM < padM) outerM = padM; innerM = outerM - padM; }
    var sumC = 0;
    for (li = 0; li < lines.length; li++) sumC += lines[li].cross;
    sumC += lines.length > 1 ? crossGap * (lines.length - 1) : 0;
    if (outerC === null) { outerC = clamp(sumC + padC, F[A.minC], F[A.maxC]); if (outerC < padC) outerC = padC; }
    var innerC = outerC - padC;
    /* a single line fills the frame's cross size (as a single-line flex container does) */
    if (lines.length === 1) lines[0].cross = innerC;
    /* tracks along the cross axis */
    var trackStart = padCs, trackGap = crossGap;
    if (lines.length > 1) {
      var freeC = innerC - sumC;
      if (F.alignContent === 'between') { trackGap = crossGap + Math.max(0, freeC / (lines.length - 1)); }
      else if (F.alignCross === 'center') trackStart += freeC / 2;
      else if (F.alignCross === 'end') trackStart += freeC;
    }
    var posC = trackStart;
    for (li = 0; li < lines.length; li++) {
      L = lines[li];
      var free = innerM - L.sumM, lead = 0, between = gap, n = L.length;
      if (autoGap) {
        var room = free;
        if (F.auto === 'evenly') { var g = Math.max(0, room / (n + 1)); lead = g; between = g; }
        else if (F.auto === 'around') { var g2 = Math.max(0, room / n); lead = g2 / 2; between = g2; }
        else { between = n > 1 ? Math.max(0, room / (n - 1)) : 0; lead = 0; }
      } else {
        if (F.alignMain === 'center') lead = free / 2;
        else if (F.alignMain === 'end') lead = free;
      }
      var posM = padMs + lead;
      for (j = 0; j < n; j++) {
        it = L[j];
        var sizeC = it.fillC ? Math.max(0, clamp(L.cross, it.c[A.minC], it.c[A.maxC])) : it.cross;
        var offC = 0;
        if (!it.fillC || sizeC < L.cross - EPS) {
          if (it.fillC) offC = 0;
          else if (F.alignCross === 'center') offC = (L.cross - sizeC) / 2;
          else if (F.alignCross === 'end') offC = L.cross - sizeC;
        }
        var r = {};
        r[A.row ? 'x' : 'y'] = posM;
        r[A.row ? 'y' : 'x'] = posC + offC;
        r[A.M] = it.target;
        r[A.C] = sizeC;
        out.kids[it.idx] = { x: r.x, y: r.y, w: r.w, h: r.h };
        posM += it.target + between;
      }
      posC += L.cross + trackGap;
    }
    out.w = A.row ? outerM : outerC;
    out.h = A.row ? outerC : outerM;
    /* canvas stacking: last on top by default; the frame's flow order otherwise */
    for (i = 0; i < kids.length; i++) out.z.push(i);
    if (F.reverseZ) out.z.reverse();
    return out;
  }
  root.lalLayout = layout;
  root.lalResolveFill = resolveFill;
})(typeof module !== 'undefined' ? module.exports : this);
