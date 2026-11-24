

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


function bimRecAt(path, t) {
  if (path.length === 0) {
    return null;
  }
  var last = path[path.length - 1];
  if (t >= last.t) {
    return last;
  }
  var first = path[0];
  if (t <= first.t) {
    return first;
  }
  var i;
  for (i = 0; i < path.length - 1; i = i + 1) {
    var a = path[i];
    var b = path[i + 1];
    if (t >= a.t && t <= b.t) {
      var u = (t - a.t) / (b.t - a.t);
      var p = [
        a.p[0] + (b.p[0] - a.p[0]) * u,
        a.p[1] + (b.p[1] - a.p[1]) * u,
        a.p[2] + (b.p[2] - a.p[2]) * u
      ];
      var pitch = a.pitch + (b.pitch - a.pitch) * u;
      var yaw = a.yaw + bimRecAngle(a.yaw, b.yaw) * u;
      return { t: t, p: p, yaw: yaw, pitch: pitch };
    }
  }
  return last;
}
