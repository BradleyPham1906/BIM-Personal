// W1 walkthrough research, experiment e01: two WebAssembly physics engines' character controllers, and three.js's
// own Octree with no engine, on the same course, in Node. Data, never a suite. Run from a folder where the three packages are installed:
//
//   npm install --ignore-scripts @dimforge/rapier3d-compat@0.21.0 jolt-physics@1.1.1 cannon-es@0.20.0 three@0.186.1
//   node <repo>/docs/research/experiments/w1-walk/physics-bench.mjs [--boxes 5000] [--runs 3]
//
// The course (metres, y up): a flat ground; a step of 0.18 m (a stair riser, IBC 1011.5.2's 7 in maximum);
// a curb of 0.40 m (taller than a step, must stop the walker); a ramp at 1:12 (ADA 405.2's steepest); a slope
// of 40 degrees (steeper than the walker may climb); a wall 3 m tall walked into at 10 m/s (tunnelling).
// The walker: a capsule 1.75 m tall, radius 0.25 m; it may step up 0.30 m and climb 35 degrees.
// Then the speed test: a town of N boxes as one triangle mesh (12 triangles each) walked through for 600 frames
// at 60 Hz, the time per frame measured. Each case starts its walker from the same place with the same input.
import { createRequire } from 'node:module';
import { performance } from 'node:perf_hooks';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
const require = createRequire(path.join(process.cwd(), 'x.js'));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? Number(process.argv[i + 1]) : d; };
const BOXES = arg('--boxes', 5000), RUNS = arg('--runs', 3), DT = 1 / 60;
const H = 1.75, R = 0.25, HALF = (H - 2 * R) / 2, STEP = 0.30, SLOPE = 35 * Math.PI / 180, WALK = 1.4;

// ---- the course as triangles: [x,y,z, x,y,z, x,y,z] each ----
function box(tris, x0, y0, z0, x1, y1, z1) {
  const v = [[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
  const f = [[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]];
  for (const t of f) tris.push([...v[t[0]], ...v[t[1]], ...v[t[2]]]);
}
function quad(tris, a, b, c, d) { tris.push([...a, ...b, ...c], [...a, ...c, ...d]); }
// each lane runs along +x from x=0, lanes 10 m apart in z; the obstacle starts at x=3
function lane(kind, z) {
  const t = [];
  quad(t, [-5,0,z-3], [-5,0,z+3], [30,0,z+3], [30,0,z-3]);   // ground, facing up
  if (kind === 'step') box(t, 3, 0, z-3, 30, 0.18, z+3);
  if (kind === 'curb') box(t, 3, 0, z-3, 30, 0.40, z+3);
  if (kind === 'wall') box(t, 3, 0, z-3, 3.2, 3, z+3);
  if (kind === 'ramp' || kind === 'slope') {
    const g = kind === 'ramp' ? 1 / 12 : Math.tan(40 * Math.PI / 180), L = 12;
    quad(t, [3,0,z-3], [3,0,z+3], [3+L,L*g,z+3], [3+L,L*g,z-3]);
  }
  return t;
}
const LANES = ['step', 'curb', 'ramp', 'slope', 'wall'];
function course() { const t = []; LANES.forEach((k, i) => t.push(...lane(k, i * 10))); return t; }
function town(n) {   // n boxes 8-20 m wide, 3-60 m tall, on a grid with 12 m streets; a fixed seed
  let s = 12345; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const t = [], side = Math.ceil(Math.sqrt(n)), cell = 32;
  quad(t, [-50,0,-50], [-50,0,side*cell+50], [side*cell+50,0,side*cell+50], [side*cell+50,0,-50]);
  for (let i = 0; i < n; i++) {
    const cx = (i % side) * cell + 12, cz = Math.floor(i / side) * cell + 12, w = 8 + rnd() * 12, d = 8 + rnd() * 12;
    box(t, cx, 0, cz, cx + w, 3 + rnd() * 57, cz + d);
  }
  return { tris: t, side, cell };
}
const flat = (tris) => { const v = new Float32Array(tris.length * 9); tris.forEach((tr, i) => v.set(tr, i * 9)); return v; };

// ---- the course run: walk +x at speed for 5 s; returns the walker's end ----
function runCourse(make) {
  const out = {};
  LANES.forEach((k, i) => {
    const w = make(course(), [0, 0, i * 10]);
    const speed = k === 'wall' ? 10 : WALK;
    for (let f = 0; f < 300; f++) w.move(speed, 0, DT);
    const p = w.pos(); out[k] = { x: +p[0].toFixed(3), feetY: +p[1].toFixed(3) }; w.free();
  });
  return out;
}
function judge(o) {   // what each lane must show
  return {
    step: o.step.x > 6 && Math.abs(o.step.feetY - 0.18) < 0.05,
    curb: o.curb.x < 3,
    ramp: o.ramp.x > 6 && o.ramp.feetY > 0.2,
    slope: o.slope.feetY < 1.0,
    wall: o.wall.x < 3,
  };
}
// the speed test: from a street crossing, a square of four 10 m legs (5 m/s for 2 s) repeated for 600
// frames; the second leg leaves the street and runs into a building's wall, so the time includes contacts
function runTown(make, T) {
  const t0 = performance.now(); const w = make(T.tris, [T.cell + 4, 0, T.cell + 4]); /* a street crossing: streets run in (32k+32, 32k+44) */ const built = performance.now() - t0;
  const dirs = [[1,0],[0,1],[-1,0],[0,-1]], times = [];
  for (let f = 0; f < 600; f++) {
    const d = dirs[Math.floor(f / 120) % 4], a = performance.now();
    w.move(5 * d[0], 5 * d[1], DT); times.push(performance.now() - a);
  }
  const end = w.pos().map((x) => +x.toFixed(2)); w.free(); times.sort((a, b) => a - b);
  return { end, buildMs: +built.toFixed(1), frameMeanMs: +(times.reduce((a, b) => a + b, 0) / times.length).toFixed(4),
    frameP95Ms: +times[Math.floor(times.length * 0.95)].toFixed(4), frameMaxMs: +times[times.length - 1].toFixed(4) };
}

// ---- Rapier 0.21: a kinematic capsule moved by its KinematicCharacterController ----
async function rapier() {
  const t0 = performance.now(); const RAPIER = require('@dimforge/rapier3d-compat'); await RAPIER.init(); const init = performance.now() - t0;
  const make = (tris, at) => {
    const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
    const v = flat(tris), idx = new Uint32Array(v.length / 3).map((_, i) => i);
    world.createCollider(RAPIER.ColliderDesc.trimesh(v, idx));
    const body = world.createRigidBody(RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(at[0], at[1] + HALF + R + 0.02, at[2]));
    const col = world.createCollider(RAPIER.ColliderDesc.capsule(HALF, R), body);
    const cc = world.createCharacterController(0.02);
    cc.setUp({ x: 0, y: 1, z: 0 }); cc.enableAutostep(STEP, 0.2, false); cc.enableSnapToGround(0.3);
    cc.setMaxSlopeClimbAngle(SLOPE); cc.setMinSlopeSlideAngle(SLOPE);
    let vy = 0; world.step();
    return {
      move(vx, vz, dt) {
        vy = cc.computedGrounded() ? -0.5 : vy - 9.81 * dt;
        const a = performance.now();
        cc.computeColliderMovement(col, { x: vx * dt, y: vy * dt, z: vz * dt });
        const m = cc.computedMovement(), p = body.translation(), b = performance.now();
        body.setNextKinematicTranslation({ x: p.x + m.x, y: p.y + m.y, z: p.z + m.z }); world.step();
        SPLIT.cc += b - a; SPLIT.step += performance.now() - b; SPLIT.n++;
      },
      pos() { const p = body.translation(); return [p.x, p.y - HALF - R, p.z]; },
      free() { world.free(); },
    };
  };
  return { init, make };
}

// ---- Jolt 1.1.1: CharacterVirtual with ExtendedUpdate (stairs and floor stick) ----
async function jolt() {
  const t0 = performance.now(); const Jolt = await (await import(require.resolve('jolt-physics/wasm-compat'))).default(); const init = performance.now() - t0;
  const make = (tris, at) => {
    const pairs = new Jolt.ObjectLayerPairFilterTable(2); pairs.EnableCollision(0, 1); pairs.EnableCollision(1, 1);
    const bpi = new Jolt.BroadPhaseLayerInterfaceTable(2, 2);
    bpi.MapObjectToBroadPhaseLayer(0, new Jolt.BroadPhaseLayer(0)); bpi.MapObjectToBroadPhaseLayer(1, new Jolt.BroadPhaseLayer(1));
    const st = new Jolt.JoltSettings(); st.mObjectLayerPairFilter = pairs; st.mBroadPhaseLayerInterface = bpi;
    st.mObjectVsBroadPhaseLayerFilter = new Jolt.ObjectVsBroadPhaseLayerFilterTable(bpi, 2, pairs, 2);
    const ji = new Jolt.JoltInterface(st); Jolt.destroy(st); const ps = ji.GetPhysicsSystem(), bi = ps.GetBodyInterface();
    const tl = new Jolt.TriangleList(); tl.resize(tris.length);
    tris.forEach((tr, i) => { const t = tl.at(i); for (let k = 0; k < 3; k++) { const v = t.get_mV(k); v.x = tr[k*3]; v.y = tr[k*3+1]; v.z = tr[k*3+2]; } });
    const shape = new Jolt.MeshShapeSettings(tl, new Jolt.PhysicsMaterialList()).Create().Get(); Jolt.destroy(tl);
    const bcs = new Jolt.BodyCreationSettings(shape, new Jolt.RVec3(0, 0, 0), Jolt.Quat.prototype.sIdentity(), Jolt.EMotionType_Static, 0);
    bi.AddBody(bi.CreateBody(bcs).GetID(), Jolt.EActivation_DontActivate); Jolt.destroy(bcs);
    const cs = new Jolt.CharacterVirtualSettings(); cs.mMass = 80; cs.mMaxSlopeAngle = SLOPE; cs.mUp = new Jolt.Vec3(0, 1, 0);
    cs.mShape = new Jolt.RotatedTranslatedShapeSettings(new Jolt.Vec3(0, HALF + R, 0), Jolt.Quat.prototype.sIdentity(), new Jolt.CapsuleShapeSettings(HALF, R)).Create().Get();
    cs.mSupportingVolume = new Jolt.Plane(Jolt.Vec3.prototype.sAxisY(), -R);
    const ch = new Jolt.CharacterVirtual(cs, new Jolt.RVec3(at[0], at[1] + 0.02, at[2]), Jolt.Quat.prototype.sIdentity(), ps);
    const us = new Jolt.ExtendedUpdateSettings(); us.mWalkStairsStepUp = new Jolt.Vec3(0, STEP, 0); us.mStickToFloorStepDown = new Jolt.Vec3(0, -0.3, 0);
    const bpf = new Jolt.DefaultBroadPhaseLayerFilter(ji.GetObjectVsBroadPhaseLayerFilter(), 1), olf = new Jolt.DefaultObjectLayerFilter(ji.GetObjectLayerPairFilter(), 1);
    const bf = new Jolt.BodyFilter(), sf = new Jolt.ShapeFilter(), g = new Jolt.Vec3(0, -9.81, 0), vel = new Jolt.Vec3(0, 0, 0);
    ps.OptimizeBroadPhase();
    return {
      move(vx, vz, dt) {
        const grounded = ch.GetGroundState() === Jolt.EGroundState_OnGround, vy = grounded ? 0 : ch.GetLinearVelocity().GetY() - 9.81 * dt;
        vel.Set(vx, vy, vz); ch.SetLinearVelocity(vel);
        ch.ExtendedUpdate(dt, g, us, bpf, olf, bf, sf, ji.GetTempAllocator());
      },
      pos() { const p = ch.GetPosition(); return [p.GetX(), p.GetY(), p.GetZ()]; },
      free() { Jolt.destroy(ch); Jolt.destroy(ji); },
    };
  };
  return { init, make };
}

// ---- three.js 0.186.1's own Octree and Capsule (no physics engine), moved as its games_fps example moves them:
// the velocity integrated in 5 substeps, the capsule pushed out of the triangles, on the floor when pushed up ----
async function octree() {
  const t0 = performance.now(); const THREE = await import(path.join(process.cwd(), 'node_modules/three/build/three.module.js'));
  const { Octree } = await import(require.resolve('three/examples/jsm/math/Octree.js'));
  const { Capsule } = await import(require.resolve('three/examples/jsm/math/Capsule.js')); const init = performance.now() - t0;
  const make = (tris, at) => {
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(flat(tris), 3));
    const oc = new Octree().fromGraphNode(new THREE.Mesh(g, new THREE.MeshBasicMaterial()));
    const cap = new Capsule(new THREE.Vector3(at[0], at[1] + R + 0.02, at[2]), new THREE.Vector3(at[0], at[1] + H - R + 0.02, at[2]), R);
    const v = new THREE.Vector3(); let floor = false; const SUB = 5;
    return {
      move(vx, vz, dt) {
        for (let k = 0; k < SUB; k++) {
          const h = dt / SUB; v.x = vx; v.z = vz; if (!floor) v.y -= 9.81 * h; else v.y = 0;
          cap.translate(v.clone().multiplyScalar(h));
          const r = oc.capsuleIntersect(cap); floor = false;
          if (r) { floor = r.normal.y > 0; if (!floor) v.addScaledVector(r.normal, -r.normal.dot(v)); cap.translate(r.normal.multiplyScalar(r.depth)); }
        }
      },
      pos() { return [cap.start.x, cap.start.y - R, cap.start.z]; },
      free() { g.dispose(); },
    };
  };
  return { init, make };
}

function sizes() {   // what would ship: the file the browser loads, raw and gzipped
  const nm = path.join(process.cwd(), 'node_modules'), z = (f) => { const b = fs.readFileSync(f); return { file: path.relative(nm, f), bytes: b.length, gzip: zlib.gzipSync(b, { level: 9 }).length }; };
  return [z(path.join(nm, '@dimforge/rapier3d-compat/dist/rapier.cjs')),
    z(path.join(nm, '@dimforge/rapier3d-compat/dist/rapier_wasm3d_bg.wasm')),
    z(path.join(nm, 'jolt-physics/dist/jolt-physics.wasm-compat.js')),
    z(path.join(nm, 'jolt-physics/dist/jolt-physics.wasm.wasm')),
    z(path.join(nm, 'cannon-es/dist/cannon-es.js'))];
}

const SPLIT = { cc: 0, step: 0, n: 0 };   // Rapier's frame split: the controller's query and the world's step
const T = town(BOXES), report = { node: process.version, boxes: BOXES, triangles: T.tris.length, runs: RUNS, sizes: sizes(), engines: {} };
for (const [name, load] of [['rapier 0.21.0', rapier], ['jolt-physics 1.1.1', jolt], ['three 0.186.1 Octree', octree]]) {
  const e = await load(), rec = { initMs: +e.init.toFixed(1), course: null, pass: null, town: [] };
  try { rec.course = runCourse(e.make); rec.pass = judge(rec.course); SPLIT.cc = SPLIT.step = SPLIT.n = 0; /* the split is the town's only */ } catch (err) { rec.courseError = String(err && err.stack || err); }
  for (let r = 0; r < RUNS; r++) { try { rec.town.push(runTown(e.make, T)); } catch (err) { rec.townError = String(err && err.stack || err); break; } }
  if (SPLIT.n) { rec.splitMeanMs = { controller: +(SPLIT.cc / SPLIT.n).toFixed(4), worldStep: +(SPLIT.step / SPLIT.n).toFixed(4), frames: SPLIT.n }; SPLIT.cc = SPLIT.step = SPLIT.n = 0; }
  report.engines[name] = rec;
}
console.log(JSON.stringify(report, null, 1));
