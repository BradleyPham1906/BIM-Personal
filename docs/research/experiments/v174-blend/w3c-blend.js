// V174 research (2026-11-08): our own implementation of the W3C Compositing and Blending
// Level 1 formulas (CRD 2024-03-21, sections 5.1, 6, 10.1, 10.2), used as the reference the
// browser's canvas is measured against. Research data, not the app's code. ES5.
'use strict';

function clamp01(x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }

// Separable B(cb, cs) on one channel in [0, 1].
function multiply(cb, cs) { return cb * cs; }
function screen(cb, cs) { return cb + cs - cb * cs; }
function hardLight(cb, cs) { return cs <= 0.5 ? multiply(cb, 2 * cs) : screen(cb, 2 * cs - 1); }
function softLightD(cb) { return cb <= 0.25 ? ((16 * cb - 12) * cb + 4) * cb : Math.sqrt(cb); }

var SEPARABLE = {
  'normal': function (cb, cs) { return cs; },
  'multiply': multiply,
  'screen': screen,
  'overlay': function (cb, cs) { return hardLight(cs, cb); },
  'darken': function (cb, cs) { return Math.min(cb, cs); },
  'lighten': function (cb, cs) { return Math.max(cb, cs); },
  'color-dodge': function (cb, cs) {
    if (cb === 0) return 0;
    if (cs === 1) return 1;
    return Math.min(1, cb / (1 - cs));
  },
  'color-burn': function (cb, cs) {
    if (cb === 1) return 1;
    if (cs === 0) return 0;
    return 1 - Math.min(1, (1 - cb) / cs);
  },
  'hard-light': hardLight,
  'soft-light': function (cb, cs) {
    if (cs <= 0.5) return cb - (1 - 2 * cs) * cb * (1 - cb);
    return cb + (2 * cs - 1) * (softLightD(cb) - cb);
  },
  'difference': function (cb, cs) { return Math.abs(cb - cs); },
  'exclusion': function (cb, cs) { return cb + cs - 2 * cb * cs; }
};

// Non-separable helpers on [r, g, b].
function lum(c) { return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]; }
function clipColor(c) {
  var l = lum(c), n = Math.min(c[0], c[1], c[2]), x = Math.max(c[0], c[1], c[2]), i, o = c.slice();
  if (n < 0) for (i = 0; i < 3; i++) o[i] = l + ((o[i] - l) * l) / (l - n);
  if (x > 1) for (i = 0; i < 3; i++) o[i] = l + ((o[i] - l) * (1 - l)) / (x - l);
  return o;
}
function setLum(c, l) { var d = l - lum(c); return clipColor([c[0] + d, c[1] + d, c[2] + d]); }
function sat(c) { return Math.max(c[0], c[1], c[2]) - Math.min(c[0], c[1], c[2]); }
function setSat(c, s) {
  var idx = [0, 1, 2].sort(function (a, b) { return c[a] - c[b]; });
  var mn = idx[0], md = idx[1], mx = idx[2], o = [0, 0, 0];
  if (c[mx] > c[mn]) {
    o[md] = ((c[md] - c[mn]) * s) / (c[mx] - c[mn]);
    o[mx] = s;
  } else { o[md] = 0; o[mx] = 0; }
  o[mn] = 0;
  return o;
}
var NONSEPARABLE = {
  'hue': function (cb, cs) { return setLum(setSat(cs, sat(cb)), lum(cb)); },
  'saturation': function (cb, cs) { return setLum(setSat(cb, sat(cs)), lum(cb)); },
  'color': function (cb, cs) { return setLum(cs, lum(cb)); },
  'luminosity': function (cb, cs) { return setLum(cb, lum(cs)); }
};

var MODES = ['normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten', 'color-dodge',
  'color-burn', 'hard-light', 'soft-light', 'difference', 'exclusion',
  'hue', 'saturation', 'color', 'luminosity'];

// Blend B(Cb, Cs) for a mode on [r, g, b] in [0, 1]; result clamped (section 10).
function blend(mode, cb, cs) {
  var out;
  if (NONSEPARABLE[mode]) out = NONSEPARABLE[mode](cb, cs);
  else out = [0, 1, 2].map(function (i) { return SEPARABLE[mode](cb[i], cs[i]); });
  return out.map(clamp01);
}

// Source-over with blending (section 10, note): non-premultiplied in, non-premultiplied out.
// b, s: {c: [r, g, b] in [0, 1], a: alpha in [0, 1]}.
function composite(mode, b, s) {
  var ab = b.a, as = s.a, ao = as + ab * (1 - as), m = blend(mode, b.c, s.c), co = [], i;
  for (i = 0; i < 3; i++) {
    var v = as * (1 - ab) * s.c[i] + as * ab * m[i] + (1 - as) * ab * b.c[i];
    co.push(ao > 0 ? v / ao : 0);
  }
  return { c: co, a: ao };
}

module.exports = { MODES: MODES, blend: blend, composite: composite, lum: lum };
