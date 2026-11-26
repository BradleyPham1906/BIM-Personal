

  /* ================= __acad3dV227: Track D, the drone bridge project: flight planning, the pure part =================
     docs/research/research-bridge-splatting.md and docs/work-orders/v227/SPEC.md. Photogrammetry flight planning: GSD, the
     height for a GSD, a photo's footprint, spacing for overlap, flight lines. Each function is a work order, added below as
     it is built; none uses another file's names. */

function bimDpGsd(sw, f, iw, h) {
  if (sw <= 0 || f <= 0 || iw <= 0 || h <= 0) return null;
  return sw * h * 100 / (f * iw);
}

function bimDpHeight(gsd, sw, f, iw) {
  if (gsd <= 0 || sw <= 0 || f <= 0 || iw <= 0) return null;
  return gsd * f * iw / (sw * 100);
}

function bimDpFootprint(sw, sh, f, h) {
  if (f <= 0) return null;
  return {w: sw * h / f, h: sh * h / f};
}

function bimDpSpacing(len, overlap) {
  if (overlap < 0 || overlap >= 1) return null;
  return len * (1 - overlap);
}

function bimDpLines(width, spacing) {
  if (spacing <= 0) return null;
  return Math.ceil(width / spacing - 1e-9) + 1;
}
