

  /* ================= __acad3dV190: LOD-C point clouds, the pure part =================
     docs/research/research-notion-v188-point-clouds.md (the owner's decisions as recommended, 2026-11-14) and
     docs/work-orders/v190/SPEC.md. Local LAS (1.2 to 1.4, formats 0 to 3 and 6 to 8) and PLY (ASCII and binary
     little-endian) read from their bytes, sampled to a point budget and rebased on a whole-metre origin in double
     precision before float32; ASPRS class names, a height ramp, ground points thinned by cell. LAZ, COPC and EPT come
     later, behind the library rule. Each function is a work order in docs/work-orders/v190/TASKS.md, added below as
     it is built; none uses another file's names. */
