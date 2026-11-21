

  /* ================= __acad3dV190: LOD-C point clouds, the pure part =================
     docs/research/research-notion-v188-point-clouds.md (the owner's decisions as recommended, 2026-11-14) and
     docs/work-orders/v190/SPEC.md. Local LAS (1.2 to 1.4, formats 0 to 3 and 6 to 8) and PLY (ASCII and binary
     little-endian) read from their bytes, sampled to a point budget and rebased on a whole-metre origin in double
     precision before float32; ASPRS class names, a height ramp, ground points thinned by cell. LAZ, COPC and EPT come
     later, behind the library rule. Each function is a work order in docs/work-orders/v190/TASKS.md, added below as
     it is built; none uses another file's names. */

/**
 * bimPcSniff(b) - detect point cloud format from first bytes
 * (a Uint8Array): 'las' for LASF (bytes 76 65 83 70),
 *   'laz' when also byte 104 has bit 6 or 7 set (& 0xC0),
 *   'ply' for ply followed by \n or \r, else '' (also for under 4 bytes).
 */
function bimPcSniff(b) {
  if (b === null || b === undefined || b.length < 4) {
    return '';
  }
  if (b[0] === 76 && b[1] === 65 && b[2] === 83 && b[3] === 70) {
    if (b.length > 104 && (b[104] & 0xC0) !== 0) {
      return 'laz';
    }
    return 'las';
  }
  if (b[0] === 112 && b[1] === 108 && b[2] === 121 && (b[3] === 10 || b[3] === 13)) {
    return 'ply';
  }
  return '';
}
