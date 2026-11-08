/* V174 experiment e03: grid convergence on UTM three ways.
   (a) the spherical formula gamma = atan(tan(dlon) sin(lat)) (Wikipedia, Transverse Mercator, "Convergence");
   (b) Krueger's series as Karney (2011) gives it, eq. (24): gamma = gamma' + gamma'',
       gamma' = atan(tau'/sqrt(1+tau'^2) tan(dlon)), gamma'' = atan(q'/p'), third order in n like the app's
       bimUtmFwd (src/js/engine/map/cityjson.js);
   (c) a finite difference: project the point and a point 1e-6 degree north of it and take the bearing
       of the second from the first (QGIS's QgsBearingUtils::bearingTrueNorth does this, read as text).
   Our own ES5 code. Run: node convergence.js */
'use strict';
var D2R = Math.PI / 180, A = 6378137, F = 1 / 298.257223563, K0 = 0.9996;
function sinh(x) { return (Math.exp(x) - Math.exp(-x)) / 2; }
function cosh(x) { return (Math.exp(x) + Math.exp(-x)) / 2; }
function atanh(x) { return 0.5 * Math.log((1 + x) / (1 - x)); }
var n = F / (2 - F), n2 = n * n, n3 = n2 * n, E = Math.sqrt(F * (2 - F));
var AA = A / (1 + n) * (1 + n2 / 4 + n2 * n2 / 64);
var AL = [n / 2 - 2 * n2 / 3 + 5 * n3 / 16, 13 * n2 / 48 - 3 * n3 / 5, 61 * n3 / 240];
function fwd(lat, lon, lon0) {
  var ph = lat * D2R, dl = (lon - lon0) * D2R, j;
  var tau = Math.tan(ph), tp = sinh(atanh(Math.sin(ph)) - E * atanh(E * Math.sin(ph)));   /* tau' */
  var xi = Math.atan2(tp, Math.cos(dl)), et = atanh(Math.sin(dl) / Math.sqrt(1 + tp * tp)), x = et, y = xi, p = 1, q = 0;
  for (j = 1; j <= 3; j++) {
    x += AL[j - 1] * Math.cos(2 * j * xi) * sinh(2 * j * et);
    y += AL[j - 1] * Math.sin(2 * j * xi) * cosh(2 * j * et);
    p += 2 * j * AL[j - 1] * Math.cos(2 * j * xi) * cosh(2 * j * et);
    q += 2 * j * AL[j - 1] * Math.sin(2 * j * xi) * sinh(2 * j * et);
  }
  var g1 = Math.atan(tp / Math.sqrt(1 + tp * tp) * Math.tan(dl)), g2 = Math.atan2(q, p);
  return { E: 500000 + K0 * AA * x, N: K0 * AA * y, gamma: (g1 + g2) / D2R, gSphere1: g1 / D2R, tau: tau };
}
function numeric(lat, lon, lon0) {
  var a = fwd(lat, lon, lon0), b = fwd(lat + 1e-6, lon, lon0);
  /* bearing of true north on the grid, clockwise from grid north; convergence (grid north from true north) is its negative */
  return -Math.atan2(b.E - a.E, b.N - a.N) / D2R;
}
var CASES = [
  ['Philadelphia City Hall, zone 18 (CM -75)', 39.9526, -75.1636, -75],
  ['Same latitude, 1 degree east of the CM', 39.9526, -74, -75],
  ['Zone edge at 40 N (3 degrees from the CM)', 40, -72, -75],
  ['Zone edge at 60 N', 60, -72, -75],
  ['On the equator, 3 degrees off', 0, -72, -75],
  ['On the central meridian at 60 N', 60, -75, -75],
  ['80 N, 3 degrees off (UTM\'s northern limit is 84 N)', 80, -72, -75],
  ['Southern hemisphere, 33.9 S, 2 degrees east', -33.9, 153, 151]
];
console.log('case | (a) spherical | (b) Karney/Krueger | (c) finite difference | (b)-(c) arcsec | (a)-(b) arcsec');
CASES.forEach(function (c) {
  var dl = (c[2] - c[3]) * D2R, ga = Math.atan(Math.tan(dl) * Math.sin(c[1] * D2R)) / D2R;
  var r = fwd(c[1], c[2], c[3]), gc = numeric(c[1], c[2], c[3]);
  console.log(c[0] + ' | ' + ga.toFixed(6) + ' | ' + r.gamma.toFixed(6) + ' | ' + gc.toFixed(6) + ' | ' + ((r.gamma - gc) * 3600).toFixed(3) + ' | ' + ((ga - r.gamma) * 3600).toFixed(3));
});
/* what this means for an arrow: the angle between true and grid north across a site 1 km wide */
var w = fwd(39.9526, -75.1636 - 0.0059, -75).gamma, e = fwd(39.9526, -75.1636 + 0.0059, -75).gamma;
console.log('\nChange of convergence across 1 km east-west at Philadelphia: ' + ((e - w) * 3600).toFixed(2) + ' arcsec');
