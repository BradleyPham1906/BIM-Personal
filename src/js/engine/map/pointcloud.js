

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

var BIM_PC_MINLEN = { 0: 20, 1: 28, 2: 26, 3: 34, 6: 30, 7: 36, 8: 38 };

function bimPcLasHeader(dv) {
  if (dv.byteLength < 227) {
    return { error: 'too short' };
  }
  var versionMajor = dv.getUint8(24);
  var versionMinor = dv.getUint8(25);
  var headerSize = dv.getUint16(94, true);
  var offsetToPoints = dv.getUint32(96, true);
  var pointFormat = dv.getUint8(104) & 0x3f;
  var recordLength = dv.getUint16(105, true);
  var count = dv.getUint32(107, true);
  var minLen = BIM_PC_MINLEN[pointFormat];
  if (minLen === undefined) {
    return { error: 'point format ' + pointFormat + ' not supported' };
  }
  if (recordLength < minLen) {
    return { error: 'record too short' };
  }
  if (offsetToPoints < headerSize || offsetToPoints + count * recordLength > dv.byteLength) {
    return { error: 'truncated' };
  }
  if (count === 0 && versionMinor >= 4) {
    count = dv.getUint32(247, true) + dv.getUint32(251, true) * 0x100000000;
  }
  var scale = [dv.getFloat64(131, true), dv.getFloat64(139, true), dv.getFloat64(147, true)];
  var offset = [dv.getFloat64(155, true), dv.getFloat64(163, true), dv.getFloat64(171, true)];
  var min = [dv.getFloat64(187, true), dv.getFloat64(203, true), dv.getFloat64(219, true)];
  var max = [dv.getFloat64(179, true), dv.getFloat64(195, true), dv.getFloat64(211, true)];
  return {
    versionMajor: versionMajor,
    versionMinor: versionMinor,
    headerSize: headerSize,
    offsetToPoints: offsetToPoints,
    pointFormat: pointFormat,
    recordLength: recordLength,
    count: count,
    scale: scale,
    offset: offset,
    min: min,
    max: max
  };
}

function bimPcStep(count, max) {
  if (typeof max === 'number' && max >= 1) {
    max = Math.floor(max);
  } else {
    max = count;
  }
  if (count <= max) {
    return 1;
  }
  return Math.ceil(count / max);
}

var BIM_PC_RGB = { 2: 20, 3: 28, 7: 30, 8: 30 };

function bimPcLasPoints(dv, h, max, origin) {
  var step = bimPcStep(h.count, max);
  var n = Math.ceil(h.count / step);
  var xyz = new Float32Array(n * 3);
  var cls = null;
  var rgb = null;
  var rgbAt = BIM_PC_RGB[h.pointFormat];
  if (rgbAt !== undefined) {
    rgb = new Uint8Array(n * 3);
  }
  if (h.pointFormat < 6) {
    cls = new Uint8Array(n);
  } else {
    cls = new Uint8Array(n);
  }
  if (origin === null || origin === undefined) {
    origin = [0, 0, 0];
  }
  var pi = 0;
  for (var i = 0; i < h.count; i += step) {
    var at = h.offsetToPoints + i * h.recordLength;
    for (var j = 0; j < 3; j++) {
      var v = dv.getInt32(at + 4 * j, true) * h.scale[j] + h.offset[j] - origin[j];
      xyz[pi * 3 + j] = v;
    }
    if (h.pointFormat < 6) {
      cls[pi] = dv.getUint8(at + 15) & 0x1f;
    } else {
      cls[pi] = dv.getUint8(at + 16);
    }
    if (rgb) {
      for (var j = 0; j < 3; j++) {
        rgb[pi * 3 + j] = dv.getUint16(at + rgbAt + 2 * j, true) >> 8;
      }
    }
    pi++;
  }
  return { n: n, xyz: xyz, cls: cls, rgb: rgb };
}
