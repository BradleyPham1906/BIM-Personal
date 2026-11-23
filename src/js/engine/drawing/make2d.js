

  /* ================= __acad3dV189: Freeform F7, Make2D (hidden-line drawings), the pure part =================
     docs/research/research-freeform-f1-f7.md (F7) and docs/work-orders/v189/SPEC.md. Make2D on meshes: projection to a
     view, the edges a drawing keeps, a depth test against triangles, an edge cut to its visible runs. Each function is a
     work order, added below as it is built; none uses another file's names. */
function bimM2Project(p, view) {
  return [
    p[0] * view.right[0] + p[1] * view.right[1] + p[2] * view.right[2],
    p[0] * view.up[0] + p[1] * view.up[1] + p[2] * view.up[2],
    p[0] * view.dir[0] + p[1] * view.dir[1] + p[2] * view.dir[2]
  ];
}
