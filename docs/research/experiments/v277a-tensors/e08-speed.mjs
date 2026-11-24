/* e08 (H8): what a vec3 cross product costs in V8 written three ES5 ways: a new array per result, a Float64Array per
   result, and a caller's output array (no allocation). Inputs vary each iteration and are not chained, so values stay
   in range and the call cannot be hoisted. */
var N = 2e7, i, s = 0;
function crossNew(a, b) { return [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]; }
function crossF64(a, b) { var r = new Float64Array(3); r[0] = a[1]*b[2] - a[2]*b[1]; r[1] = a[2]*b[0] - a[0]*b[2]; r[2] = a[0]*b[1] - a[1]*b[0]; return r; }
function crossOut(o, a, b) { var x = a[1]*b[2] - a[2]*b[1], y = a[2]*b[0] - a[0]*b[2], z = a[0]*b[1] - a[1]*b[0]; o[0] = x; o[1] = y; o[2] = z; return o; }
function bench(name, f) { var best = Infinity, r, t0; for (r = 0; r < 5; r++) { t0 = process.hrtime.bigint(); f(); best = Math.min(best, Number(process.hrtime.bigint() - t0)/N); } return [name, +best.toFixed(2)]; }
var a = [0.1, 0.2, 0.3], b = [0.4, 0.5, 0.6], fa = new Float64Array(a), fb = new Float64Array(b), o = [0, 0, 0], fo = new Float64Array(3);
var res = [
  bench('array, new per call', function () { for (i = 0; i < N; i++) { a[0] = i*1e-9; s += crossNew(a, b)[2]; } }),
  bench('Float64Array, new per call', function () { for (i = 0; i < N; i++) { fa[0] = i*1e-9; s += crossF64(fa, fb)[2]; } }),
  bench('array, caller output', function () { for (i = 0; i < N; i++) { a[0] = i*1e-9; s += crossOut(o, a, b)[2]; } }),
  bench('Float64Array, caller output', function () { for (i = 0; i < N; i++) { fa[0] = i*1e-9; s += crossOut(fo, fa, fb)[2]; } }),
  bench('inline, no call (floor)', function () { for (i = 0; i < N; i++) { a[0] = i*1e-9; s += a[0]*b[1] - a[1]*b[0]; } })
];
console.log(JSON.stringify({ experiment: 'e08', iterations: N, ns_per_cross_best_of_5: res, node: process.version, v8: process.versions.v8, sink: isFinite(s) }));
