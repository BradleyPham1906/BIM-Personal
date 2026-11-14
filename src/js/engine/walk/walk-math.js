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
