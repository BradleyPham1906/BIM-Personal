

  /* ================= __acad3dV210: Walkthrough W4, swim, the pure part =================
     docs/research/research-walkthrough.md (W4) and docs/work-orders/v210/SPEC.md. Swimming: under the surface or not, a
     step with thrust, drag and buoyancy, the haze by depth, staying under the surface. Each function is a work order, added
     below as it is built; none uses another file's names. */

/* WO-01 bimSwmUnder(eyeY, waterY): true when waterY is a number and eyeY < waterY; SPEC 5 WO-01 */
function bimSwmUnder(eyeY, waterY) {
  return typeof waterY === 'number' && eyeY < waterY;
}

/* WO-02 bimSwmStep(v, inp, dt, P): each axis i: v_i + (inp_i thrust - drag v_i + (buoy on the y axis)) dt; SPEC 5 WO-02 */
function bimSwmStep(v, inp, dt, P) {
  var drag = P && P.drag > 0 ? P.drag : 2;
  var thrust = P && P.thrust > 0 ? P.thrust : 1.5;
  var buoy = P && typeof P.buoy === 'number' ? P.buoy : 0.3;
  var out = [];
  var i;
  for (i = 0; i < v.length; i++) {
    var input = inp && i < inp.length && typeof inp[i] === 'number' ? inp[i] : 0;
    var b = i === 1 ? buoy : 0;
    out[i] = v[i] + (input * thrust - drag * v[i] + b) * dt;
  }
  return out;
}

/* WO-03 bimSwmFog(depth, clear): depth / clear clamped to 0..1; clear defaults to 8 unless positive; SPEC 5 WO-03 */
function bimSwmFog(depth, clear) {
  var c = clear > 0 ? clear : 8;
  var f = depth / c;
  if (f < 0) {
    f = 0;
  }
  if (f > 1) {
    f = 1;
  }
  return f;
}

/* WO-04 bimSwmSurface(pos, waterY, eye): when pos[1] > waterY - eye, the point at waterY - eye; else a copy; SPEC 5 WO-04 */
function bimSwmSurface(pos, waterY, eye) {
  var e = eye > 0 ? eye : 0.2;
  var surface = waterY - e;
  if (pos[1] > surface) {
    return [pos[0], surface, pos[2]];
  }
  return [pos[0], pos[1], pos[2]];
}
