  /* ================= __acad3dV203: Walkthrough W1, the walk's arithmetic =================
     The pure arithmetic of walking through the model (docs/research/research-walkthrough.md;
     docs/work-orders/v203/SPEC.md part 4): the step a walker climbs, the walker's capsule, looking, the velocity
     from what is held, the camera from the walker (first and third person), and the on-screen joystick. No state,
     no page, no physics and no other engine name: each function answers from its arguments alone, so its test loads
     this file by itself (docs/work-orders/v203/v203.test.mjs). Lengths in metres, angles in radians; the model's
     y is up; yaw and pitch as the app's camera holds them (core/mesh-primitives.js camVecs: the eye is the focus
     plus d * dist, d = [cos(pitch) sin(yaw), sin(pitch), cos(pitch) cos(yaw)], so a walker looks along -d). */

/* WO-01 bimWalkStepUp(riserMm, varMm): the step a walker climbs, millimetres in, metres out */
function bimWalkStepUp(riserMm, varMm) {
    if (typeof riserMm !== 'number' || !isFinite(riserMm) || riserMm <= 0) {
        return 0;
    }
    if (typeof varMm !== 'number' || !isFinite(varMm) || varMm <= 0) {
        varMm = 0;
    }
    return Math.round(riserMm + varMm) / 1000;
}

function bimWalkCapsule(B, R) {
    var h, r, half, eye;
    h = (typeof B.top === 'number' && isFinite(B.top) && B.top > 0) ? B.top : 1.75;
    r = Math.min(0.35, Math.max(0.2, ((typeof B.sh === 'number' && isFinite(B.sh)) ? B.sh : 0) / 2));
    half = Math.max(0.05, (h - 2 * r) / 2);
    eye = (typeof B.eye === 'number' && isFinite(B.eye) && B.eye > 0) ? B.eye : h - 0.12;
    return {h: h, r: r, half: half, eye: eye, step: B.chair ? 0 : R.stepUp, slope: B.chair ? Math.atan(R.chairSlope) : R.slopeDeg * Math.PI / 180};
}

/* WO-03 bimWalkLook(v, dx, dy, k): mouse/finger look, yaw wrapped, pitch clamped */
function bimWalkLook(v, dx, dy, k) {
    var yaw = v.yaw - dx * k;
    while (yaw > Math.PI) {
        yaw = yaw - 2 * Math.PI;
    }
    while (yaw <= -Math.PI) {
        yaw = yaw + 2 * Math.PI;
    }
    var pitch = v.pitch + dy * k;
    if (pitch > 1.5) {
        pitch = 1.5;
    }
    if (pitch < -1.5) {
        pitch = -1.5;
    }
    return {yaw: yaw, pitch: pitch};
}

/* WO-04 bimWalkMove(inp, yaw, speed, fly): velocity from what is held */
function bimWalkMove(inp, yaw, speed, fly) {
    var forward = [-Math.sin(yaw), 0, -Math.cos(yaw)];
    var right = [Math.cos(yaw), 0, -Math.sin(yaw)];
    var vx = inp.f * forward[0] + inp.s * right[0];
    var vz = inp.f * forward[2] + inp.s * right[2];
    var len = Math.sqrt(vx * vx + vz * vz);
    if (len > 1) {
        vx = vx / len;
        vz = vz / len;
    }
    var mult = inp.run ? 2 : 1;
    vx = vx * speed * mult;
    vz = vz * speed * mult;
    var vy = fly ? inp.up * speed * mult : 0;
    return [vx, vy, vz];
}

/* WO-05 bimWalkCamFirst(p, eye, yaw, pitch): first-person camera at the walker's eyes */
function bimWalkCamFirst(p, eye, yaw, pitch) {
    var cp = Math.cos(pitch);
    var d = [cp * Math.sin(yaw), Math.sin(pitch), cp * Math.cos(yaw)];
    return {tx: p[0] - d[0], ty: p[1] + eye - d[1], tz: p[2] - d[2], yaw: yaw, pitch: pitch, dist: 1};
}

/* WO-06 bimWalkCamThird(p, eye, yaw, pitch, boom, hit): third-person camera behind the walker */
function bimWalkCamThird(p, eye, yaw, pitch, boom, hit) {
    var dist = boom;
    if (typeof hit === 'number' && isFinite(hit) && hit - 0.2 < boom) {
        dist = Math.max(0.3, hit - 0.2);
    }
    return {tx: p[0], ty: p[1] + eye, tz: p[2], yaw: yaw, pitch: pitch, dist: dist};
}

/* WO-07 bimWalkJoy(cx, cy, x, y, R, dead): the on-screen joystick as {s, f} */
function bimWalkJoy(cx, cy, x, y, R, dead) {
    if (typeof R !== 'number' || !isFinite(R) || R <= 0) {
        return {s: 0, f: 0};
    }
    var s = (x - cx) / R, f = (cy - y) / R;
    var l = Math.sqrt(s * s + f * f);
    if (l < dead) {
        return {s: 0, f: 0};
    }
    if (l > 1) {
        s /= l; f /= l;
    }
    return {s: s, f: f};
}

/* WO-08 bimWalkKeys(held, joy): keyboard and joystick to velocity */
function bimWalkKeys(h, j) {
    var f = 0, s = 0, up = 0, run = false, ghost = false;
    h = h || {};
    j = j || {};
    if (h.KeyW || h.ArrowUp) { f++; }
    if (h.KeyS || h.ArrowDown) { f--; }
    if (h.KeyD || h.ArrowRight) { s++; }
    if (h.KeyA || h.ArrowLeft) { s--; }
    run = !!(h.ShiftLeft || h.ShiftRight);   /* running is bimWalkMove's speed, never the direction */
    f = Math.max(-1, Math.min(1, f + (j.f || 0)));
    s = Math.max(-1, Math.min(1, s + (j.s || 0)));
    up = (h.Space ? 1 : 0) - (h.KeyC ? 1 : 0);   /* both held cancel */
    ghost = !!(h.AltLeft || h.AltRight);
    return {f: f, s: s, run: run, up: up, ghost: ghost};
}
