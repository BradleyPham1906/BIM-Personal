

  /* ================= __acad3dV211: Walkthrough W5, record and replay, the pure part =================
     docs/research/research-walkthrough.md (W5) and docs/work-orders/v211/SPEC.md. A recorded path: the shortest turn, a pose
     kept when it changed enough, the pose at a time, the path's length and duration. Each function is a work order, added
     below as it is built; none uses another file's names. */


function bimRecAngle(a, b) {
  var d = b - a;
  d = d % (2 * Math.PI);
  if (d > Math.PI) {
    d = d - 2 * Math.PI;
  }
  if (d < -Math.PI) {
    d = d + 2 * Math.PI;
  }
  return d;
}


function bimRecAdd(path, pose, t, minDist, minTurn) {
  var copy = path.slice();
  minDist = minDist === undefined ? 0.05 : minDist;
  minTurn = minTurn === undefined ? 0.02 : minTurn;
  var last = copy[copy.length - 1];
  if (last) {
    var dx = pose.p[0] - last.p[0];
    var dy = pose.p[1] - last.p[1];
    var dz = pose.p[2] - last.p[2];
    var d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    var turn = Math.abs(bimRecAngle(last.yaw, pose.yaw));
    var pitch = pose.pitch === undefined ? 0 : pose.pitch;
    var dpitch = Math.abs(pitch - last.pitch);
    if (d < minDist && turn < minTurn && dpitch < minTurn) {
      return copy;
    }
  }
  copy.push({ t: t, p: [pose.p[0], pose.p[1], pose.p[2]], yaw: pose.yaw, pitch: pose.pitch === undefined ? 0 : pose.pitch });
  return copy;
}
