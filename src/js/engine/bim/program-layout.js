

  /* ================= __acad3dV236: The layout view, the pure part =================
     docs/research/research-program-to-plan.md, its layout-methods.md, anthropocity-features.md and algorithms.md, and
     docs/work-orders/v236/SPEC.md. Rooms on a bay grid in two bands, small rooms clustered, the wall graph, corridors
     routed from user paths (direct legs, a spine, spurs), the stair, and the scorecard every study carries. Each
     function is a work order, added below as it is built; none uses another file's names. */
/* WO-01: bimPlBayWidth(areas, depth, bmin, bmax, step) - 24 lines */
function bimPlBayWidth(areas, depth, bmin, bmax, step) {
  if (depth <= 0 || areas.reduce(function (s, a) { return s + a; }, 0) <= 0) return null;
  var best = null, b = bmin, k, total, err;
  while (b <= bmax) {
    k = [];
    for (var i = 0; i < areas.length; i++) k[i] = Math.max(1, Math.round(areas[i] / (b * depth)));
    total = areas.reduce(function (s, a) { return s + a; }, 0);
    err = 0;
    for (var i = 0; i < k.length; i++) err += Math.abs(k[i] * b * depth - areas[i]);
    err = err / total;
    if (best === null || err < best.error - 1e-12) best = { bay: b, bays: k, error: err };
    b = Number((b + step).toFixed(6));
  }
  return best;
}
