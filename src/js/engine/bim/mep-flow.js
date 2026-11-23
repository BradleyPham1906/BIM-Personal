

  /* ================= __acad3dV201: MEP runs, the pure part =================
     docs/research/research-notion-v193-mep.md and research-mep-runs.md (the owner's decisions as recommended,
     2026-11-14) and docs/work-orders/v201/SPEC.md. Round and rectangular sections; straight friction by
     Darcy-Weisbach with Colebrook (turbulent) or 64/Re (laminar, round only), the transition refused; runs joined end
     to end in 3D; a single-source tree; flows from the terminals' demand; friction-only paths and the critical one.
     Never a system pressure, a sizing or a compliance finding. SI units. Each function is a work order in
     docs/work-orders/v201/TASKS.md, added below as it is built; none uses another file's names. */
function bimMepSection(p) {
  if (!p) {
    return null;
  }
  if (p.shape === 'round') {
    if (typeof p.d !== 'number' || !isFinite(p.d) || p.d <= 0) {
      return null;
    }
    return { shape: 'round', area: Math.PI * p.d * p.d / 4, perimeter: Math.PI * p.d, dh: p.d };
  }
  if (p.shape === 'rect') {
    if (typeof p.w !== 'number' || !isFinite(p.w) || p.w <= 0 ||
        typeof p.h !== 'number' || !isFinite(p.h) || p.h <= 0) {
      return null;
    }
    return { shape: 'rect', area: p.w * p.h, perimeter: 2 * (p.w + p.h), dh: 2 * p.w * p.h / (p.w + p.h) };
  }
  return null;
}
function bimMepColebrook(re, rr) {
  if (!(re > 4000) || !(rr >= 0) || !(rr < 1)) {
    return null;
  }
  var log10 = function (x) {
    return Math.log(x) / Math.LN10;
  };
  var g = function (x) {
    return x + 2 * log10(rr / 3.7 + 2.51 * x / re);
  };
  if (!(g(1) < 0) || !(0 < g(100))) {
    return null;
  }
  var lo = 1, hi = 100, mid, i;
  for (i = 0; i < 100; i++) {
    mid = (lo + hi) / 2;
    if (g(mid) > 0) {
      hi = mid;
    } else {
      lo = mid;
    }
  }
  var x = (lo + hi) / 2;
  return { f: 1 / (x * x), residual: g(x) };
}
