

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
function bimMepFriction(q, sec, len, fluid) {
  var rho, mu, eps, area, dh, v, re, cr, f, dp, why, state;
  if (!sec || !(q >= 0) || !isFinite(q) || !(len >= 0) || !isFinite(len) ||
      !fluid || !(fluid.rho > 0) || !(fluid.mu > 0) || !(fluid.eps >= 0)) {
    return { state: 'not evaluated', why: 'bad input' };
  }
  rho = fluid.rho;
  mu = fluid.mu;
  eps = fluid.eps;
  area = sec.area;
  dh = sec.dh;
  v = q / area;
  re = rho * v * dh / mu;
  f = null;
  dp = null;
  why = '';
  if (q === 0) {
    state = 'no flow';
    dp = 0;
  } else if (re < 2300) {
    if (sec.shape === 'round') {
      state = 'laminar';
      f = 64 / re;
    } else {
      state = 'not evaluated';
      why = 'laminar flow in a rectangular duct';
    }
  } else if (re <= 4000) {
    state = 'transitional';
    why = 'Reynolds number between 2300 and 4000';
  } else {
    cr = bimMepColebrook(re, eps / dh);
    if (!cr) {
      state = 'not evaluated';
      why = 'Colebrook did not converge';
    } else {
      state = 'turbulent';
      f = cr.f;
    }
  }
  if (f !== null) {
    dp = f * (len / dh) * rho * v * v / 2;
  }
  return { state: state, v: v, re: re, f: f, dp: dp, why: why };
}
function bimMepJoin(runs, tol) {
  if (!(tol > 0)) {
    tol = 0.01;
  }
  var nodes = [], edges = [], warnings = [];
  if (!runs) {
    return { nodes: nodes, edges: edges, warnings: warnings };
  }
  var nr = runs.length, i, run, pts, len, j, p1, p2, id1, id2, k, d, found, sys, pt;
  for (i = 0; i < nr; i++) {
    run = runs[i];
    if (!run) {
      continue;
    }
    pts = run.pts;
    if (!pts || pts.length < 2) {
      warnings.push('run ' + run.id + ' has fewer than 2 points');
      continue;
    }
    len = 0;
    for (j = 1; j < pts.length; j++) {
      p1 = pts[j - 1];
      p2 = pts[j];
      len += Math.sqrt((p2[0] - p1[0]) * (p2[0] - p1[0]) + (p2[1] - p1[1]) * (p2[1] - p1[1]) + (p2[2] - p1[2]) * (p2[2] - p1[2]));
    }
    if (len < 1e-9) {
      warnings.push('run ' + run.id + ' has no length');
      continue;
    }
    sys = run.sys;
    id1 = -1;
    id2 = -1;
    for (j = 0; j < 2; j++) {
      pt = j === 0 ? pts[0] : pts[pts.length - 1];
      found = -1;
      for (k = 0; k < nodes.length; k++) {
        d = Math.sqrt((pt[0] - nodes[k].p[0]) * (pt[0] - nodes[k].p[0]) + (pt[1] - nodes[k].p[1]) * (pt[1] - nodes[k].p[1]) + (pt[2] - nodes[k].p[2]) * (pt[2] - nodes[k].p[2]));
        if (d <= tol && nodes[k].sys === sys) {
          found = k;
          break;
        }
      }
      if (found < 0) {
        for (k = 0; k < nodes.length; k++) {
          d = Math.sqrt((pt[0] - nodes[k].p[0]) * (pt[0] - nodes[k].p[0]) + (pt[1] - nodes[k].p[1]) * (pt[1] - nodes[k].p[1]) + (pt[2] - nodes[k].p[2]) * (pt[2] - nodes[k].p[2]));
          if (d <= tol) {
            warnings.push('different systems meet at node ' + k);
            break;
          }
        }
        found = nodes.length;
        nodes.push({ id: found, p: [pt[0], pt[1], pt[2]], sys: sys });
      }
      if (j === 0) {
        id1 = found;
      } else {
        id2 = found;
      }
    }
    if (id1 === id2) {
      warnings.push('run ' + run.id + ' starts and ends at one node');
    } else {
      edges.push({ run: run.id, a: id1, b: id2, len: len });
    }
  }
  return { nodes: nodes, edges: edges, warnings: warnings };
}
