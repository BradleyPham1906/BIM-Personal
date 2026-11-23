"""Where the WebXR generic hand's metacarpal joints sit (docs/research/research-xr-interaction.md, E5; V276 WO-01).
Reads @webxr-input-profiles/assets 1.0.20 (MIT, Amazon) dist/profiles/generic-hand/{left,right}.glb as data: the glTF
JSON chunk only, each node's world position from its parents, then each finger's metacarpal joint as a fraction of
the way from the wrist to the finger's proximal phalanx (its knuckle), and its distance off that line.
  npm pack @webxr-input-profiles/assets@1.0.20 && tar xzf webxr-input-profiles-assets-1.0.20.tgz
  python3 -I hand_bind_pose.py package/dist/profiles/generic-hand
Run 2026-11-23: index 0.398 (left) and 0.341 (right), middle 0.320, ring 0.328, pinky 0.502; at most 6.7 mm off the line;
thumb metacarpal 49.5 mm from the wrist."""
import json, math, struct, sys


def load(p):
    b = open(p, 'rb').read()
    assert b[:4] == b'glTF'
    n = struct.unpack('<I', b[12:16])[0]
    return json.loads(b[20:20 + n])


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz)


def rot(q, v):
    return qmul(qmul(q, (v[0], v[1], v[2], 0)), (-q[0], -q[1], -q[2], q[3]))[:3]


for side in ('left', 'right'):
    g = load('%s/%s.glb' % (sys.argv[1], side))
    N, par, W = g['nodes'], {}, {}
    for i, n in enumerate(N):
        for c in n.get('children', []):
            par[c] = i

    def world(i):
        if i not in W:
            n = N[i]; t = n.get('translation', [0, 0, 0]); r = n.get('rotation', [0, 0, 0, 1]); s = n.get('scale', [1, 1, 1])
            if i in par:
                pt, pr, ps = world(par[i]); rt = rot(pr, [t[k]*ps[k] for k in range(3)])
                W[i] = ([pt[k]+rt[k] for k in range(3)], qmul(pr, r), [ps[k]*s[k] for k in range(3)])
            else:
                W[i] = (list(t), tuple(r), list(s))
        return W[i]
    pos = {n.get('name', ''): world(i)[0] for i, n in enumerate(N)}
    w = pos['wrist']
    for f in ('index-finger', 'middle-finger', 'ring-finger', 'pinky-finger'):
        m, p = pos[f + '-metacarpal'], pos[f + '-phalanx-proximal']
        d = [p[k]-w[k] for k in range(3)]; L = math.sqrt(sum(x*x for x in d)); u = [x/L for x in d]
        v = [m[k]-w[k] for k in range(3)]; a = sum(v[k]*u[k] for k in range(3))
        print(side, f, 'along %.3f' % (a/L), 'off %.4f m' % math.sqrt(max(0, sum(x*x for x in v)-a*a)))
    print(side, 'thumb metacarpal from wrist %.4f m' % math.dist(pos['thumb-metacarpal'], w))
