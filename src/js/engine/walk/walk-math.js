  /* ================= __acad3dV203: Walkthrough W1, the walk's arithmetic =================
     The pure arithmetic of walking through the model (docs/research/research-walkthrough.md;
     docs/work-orders/v203/SPEC.md part 4): the step a walker climbs, the walker's capsule, looking, the velocity
     from what is held, the camera from the walker (first and third person), and the on-screen joystick. No state,
     no page, no physics and no other engine name: each function answers from its arguments alone, so its test loads
     this file by itself (docs/work-orders/v203/v203.test.mjs). Lengths in metres, angles in radians; the model's
     y is up; yaw and pitch as the app's camera holds them (core/mesh-primitives.js camVecs: the eye is the focus
     plus d * dist, d = [cos(pitch) sin(yaw), sin(pitch), cos(pitch) cos(yaw)], so a walker looks along -d). */
