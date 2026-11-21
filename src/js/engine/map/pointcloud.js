

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

function bimPcOrigin(h) {
  return [
    Math.floor((h.min[0] + h.max[0]) / 2),
    Math.floor((h.min[1] + h.max[1]) / 2),
    Math.floor(h.min[2])
  ];
}

function bimPcPlyHeader(text) {
  if (typeof text !== 'string') {
    return { error: 'not text' };
  }
  var lines = text.split('\n');
  if (lines[0].indexOf('ply') !== 0) {
    return { error: 'not a PLY header' };
  }
  var endIdx = -1;
  for (var i = 0; i < lines.length; i++) {
    if (lines[i].indexOf('end_header') === 0) {
      endIdx = i;
      break;
    }
  }
  if (endIdx === -1) {
    return { error: 'not a PLY header' };
  }
  var headerEnd = text.indexOf('end_header') + 11;
  while (headerEnd < text.length && (text.charAt(headerEnd) === '\r' || text.charAt(headerEnd) === '\n')) {
    headerEnd++;
  }
  var format = null, count = 0, props = [], inVertex = false, hasListProp = false, hasVertex = false;
  for (var i = 1; i < endIdx; i++) {
    var p = lines[i].replace(/\r$/, '').split(/\s+/);
    var k = [];
    for (var j = 0; j < p.length; j++) if (p[j] !== '') k.push(p[j]);
    if (k.length === 0) continue;
    if (k[0] === 'comment' || k[0] === 'obj_info') continue;
    if (k[0] === 'format') { format = k[1]; }
    else if (k[0] === 'element') {
      if (k[1] === 'vertex') { inVertex = true; hasVertex = true; count = parseInt(k[2], 10); }
      else inVertex = false;
    } else if (k[0] === 'property' && inVertex) {
      if (k[1] === 'list') { hasListProp = true; }
      else props.push({ name: k[2], type: k[1] });
    }
  }
  if (hasListProp) return { error: 'a list property on vertices' };
  if (format === null) return { error: 'format missing not supported' };
  if (format !== 'ascii' && format !== 'binary_little_endian') return { error: 'format ' + format + ' not supported' };
  if (!hasVertex) return { error: 'no vertex element' };
  return { format: format, count: count, props: props, headerBytes: headerEnd };
}

var BIM_PC_PLYSIZE = {
  char: 1, int8: 1,
  uchar: 1, uint8: 1,
  short: 2, int16: 2,
  ushort: 2, uint16: 2,
  int: 4, int32: 4,
  uint: 4, uint32: 4,
  float: 4, float32: 4,
  double: 8, float64: 8
};

function bimPcPlyRead(dv, at, type) {
  var m = {
    char: 'getInt8', int8: 'getInt8',
    uchar: 'getUint8', uint8: 'getUint8',
    short: 'getInt16', int16: 'getInt16',
    ushort: 'getUint16', uint16: 'getUint16',
    int: 'getInt32', int32: 'getInt32',
    uint: 'getUint32', uint32: 'getUint32',
    float: 'getFloat32', float32: 'getFloat32',
    double: 'getFloat64', float64: 'getFloat64'
  }[type];
  return dv[m](at, true);
}

function bimPcPlyPoints(bytes, h, max, origin) {
  var xi = -1, yi = -1, zi = -1, ri = -1, gi = -1, bi = -1;
  for (var i = 0; i < h.props.length; i++) {
    var nm = h.props[i].name;
    if (nm === 'x') xi = i;
    else if (nm === 'y') yi = i;
    else if (nm === 'z') zi = i;
    else if (nm === 'red') ri = i;
    else if (nm === 'green') gi = i;
    else if (nm === 'blue') bi = i;
  }
  if (xi < 0 || yi < 0 || zi < 0) return { error: 'no x, y, z' };
  var hasRgb = ri >= 0 && gi >= 0 && bi >= 0;
  var step = bimPcStep(h.count, max);
  var n = Math.ceil(h.count / step);
  var xyz = new Float32Array(n * 3);
  var rgb = hasRgb ? new Uint8Array(n * 3) : null;
  if (origin === null || origin === undefined) origin = [0, 0, 0];
  var M = {
    char: 'getInt8', int8: 'getInt8',
    uchar: 'getUint8', uint8: 'getUint8',
    short: 'getInt16', int16: 'getInt16',
    ushort: 'getUint16', uint16: 'getUint16',
    int: 'getInt32', int32: 'getInt32',
    uint: 'getUint32', uint32: 'getUint32',
    float: 'getFloat32', float32: 'getFloat32',
    double: 'getFloat64', float64: 'getFloat64'
  };
  var offAt = function (pos) {
    var o = 0;
    for (var k = 0; k < pos; k++) o += BIM_PC_PLYSIZE[h.props[k].type];
    return o;
  };
  if (h.format === 'ascii') {
    var text = new TextDecoder().decode(bytes).split('\n');
    var dl = [], started = false;
    for (var i = 0; i < text.length; i++) {
      if (started) dl.push(text[i]);
      else if (text[i].indexOf('end_header') === 0) started = true;
    }
    var pi = 0;
    for (var si = 0; si < h.count; si += step) {
      if (si >= dl.length) return { error: 'truncated' };
      var vk = dl[si].replace(/\r$/, '').split(/\s+/);
      var kk = [];
      for (var j = 0; j < vk.length; j++) if (vk[j] !== '') kk.push(vk[j]);
      xyz[pi * 3] = parseFloat(kk[xi]) - origin[0];
      xyz[pi * 3 + 1] = parseFloat(kk[yi]) - origin[1];
      xyz[pi * 3 + 2] = parseFloat(kk[zi]) - origin[2];
      if (rgb) { rgb[pi * 3] = parseInt(kk[ri], 10); rgb[pi * 3 + 1] = parseInt(kk[gi], 10); rgb[pi * 3 + 2] = parseInt(kk[bi], 10); }
      pi++;
    }
  } else {
    var dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    var stride = 0;
    for (var i = 0; i < h.props.length; i++) stride += BIM_PC_PLYSIZE[h.props[i].type];
    if (bytes.length < h.headerBytes + h.count * stride) return { error: 'truncated' };
    var pi = 0;
    for (var si = 0; si < h.count; si += step) {
      var at = h.headerBytes + si * stride;
      for (var j = 0; j < 3; j++) {
        var pos = j === 0 ? xi : (j === 1 ? yi : zi);
        var ptype = h.props[pos].type;
        var o = offAt(pos);
        xyz[pi * 3 + j] = dv[M[ptype]](at + o, true) - origin[j];
      }
      if (rgb) {
        for (var j = 0; j < 3; j++) {
          var pos = j === 0 ? ri : (j === 1 ? gi : bi);
          var ptype = h.props[pos].type;
          var o = offAt(pos);
          rgb[pi * 3 + j] = dv[M[ptype]](at + o, true);
        }
      }
      pi++;
    }
  }
  return { n: n, xyz: xyz, cls: null, rgb: rgb };
}

var BIM_PC_CLASS = {
  0: 'Never classified', 1: 'Unclassified', 2: 'Ground', 3: 'Low vegetation',
  4: 'Medium vegetation', 5: 'High vegetation', 6: 'Building', 7: 'Low point',
  9: 'Water', 10: 'Rail', 11: 'Road surface', 13: 'Wire guard',
  14: 'Wire conductor', 15: 'Transmission tower', 17: 'Bridge deck', 18: 'High noise'
};

function bimPcClassName(c) {
  var n = BIM_PC_CLASS[c];
  return n !== undefined ? n : 'Class ' + c;
}
