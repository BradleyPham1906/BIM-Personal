

  /* ================= __acad3dV208: Walkthrough W2, drive, the pure part =================
     docs/research/research-walkthrough.md (W2) and docs/work-orders/v208/SPEC.md. Driving: a kinematic bicycle-model step,
     the turning radius, the chase camera, km/h. Each function is a work order, added below as it is built; none uses
     another file's names. */

/* WO-01 bimDrvStep(s, inp, dt, P): one kinematic-bicycle-model step; SPEC 5 WO-01 */
function bimDrvStep(s, inp, dt, P) {
  var wheelbase = P && P.wheelbase > 0 ? P.wheelbase : 2.7;
  var maxSteer = P && P.maxSteer > 0 ? P.maxSteer : 0.6;
  var accel = P && P.accel > 0 ? P.accel : 3;
  var decel = P && P.decel > 0 ? P.decel : 7;
  var drag = P && P.drag !== undefined ? P.drag : 0.05;
  var vmax = P && P.vmax > 0 ? P.vmax : 13.9;
  var throttle = inp && inp.throttle !== undefined ? inp.throttle : 0;
  var brake = inp && inp.brake !== undefined ? inp.brake : 0;
  var steer = inp && inp.steer !== undefined ? inp.steer : 0;
  var angle = steer * maxSteer;
  if (angle > maxSteer) {
    angle = maxSteer;
  }
  if (angle < -maxSteer) {
    angle = -maxSteer;
  }
  var speed = s.speed + (throttle * accel - drag * s.speed) * dt;
  speed = speed - brake * decel * dt;
  if (speed < 0) {
    speed = 0;
  }
  if (speed > vmax) {
    speed = vmax;
  }
  var h = s.heading + speed / wheelbase * Math.tan(angle) * dt;
  return {
    x: s.x + speed * Math.cos(h) * dt,
    z: s.z + speed * Math.sin(h) * dt,
    heading: h,
    speed: speed
  };
}

/* WO-02 bimDrvTurnRadius(L, steer): the turning radius at a steering angle; Infinity when straight */
function bimDrvTurnRadius(L, steer) {
  var s = steer < 0 ? -steer : steer;
  if (s < 1e-9) {
    return Infinity;
  }
  return L / Math.tan(s);
}

/* WO-03 bimDrvChase(s, dist, height): the chase camera behind the car at a height */
function bimDrvChase(s, dist, height) {
  return {
    eye: [s.x - dist * Math.cos(s.heading), height, s.z - dist * Math.sin(s.heading)],
    target: [s.x, 0.4 * height, s.z]
  };
}

/* WO-04 bimDrvKmh(ms): metres per second to kilometres per hour for the dashboard */
function bimDrvKmh(ms) {
  return Math.round(ms * 3.6);
}
