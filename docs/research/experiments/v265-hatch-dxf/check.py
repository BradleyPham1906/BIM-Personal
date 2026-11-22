import json, sys, math, ezdxf
from ezdxf.render import hatching
data = json.load(open(sys.argv[1]))
bad = 0
for key, d in data.items():
    doc = ezdxf.new('R2018'); msp = doc.modelspace()
    h = msp.add_hatch()
    h.paths.add_polyline_path([(0, 0), (3, 0), (3, 3), (0, 3)], is_closed=True)
    h.set_pattern_fill('CUSTOM', definition=[(f['angle'], tuple(f['base']), tuple(f['offset']), f['dashes']) for f in d['fam']])
    # the pattern stored as written: no extra scale or angle on top of the lines
    segs = list(hatching.hatch_entity(h))
    W, H, a = d['W'], d['H'], math.radians(d['ang'])
    c, s = math.cos(-a), math.sin(-a)
    def on_tile(px, py):
        # back into the unturned tile, then into the unit cell
        x, y = px * c - py * s, px * s + py * c
        u, v = (x / W) % 1.0, (y / H) % 1.0
        for (x0, y0, x1, y1) in d['lines']:
            for du in (-1, 0, 1):
                for dv in (-1, 0, 1):
                    ax, ay, bx, by = (x0 + du) * W, (y0 + dv) * H, (x1 + du) * W, (y1 + dv) * H
                    qx, qy = u * W, v * H
                    vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
                    t = 0 if L2 == 0 else max(0, min(1, ((qx - ax) * vx + (qy - ay) * vy) / L2))
                    if math.hypot(ax + vx * t - qx, ay + vy * t - qy) < 6e-3 * max(W, H): return True
        for (x0, y0, r) in d['dots']:
            for du in (-1, 0, 1):
                for dv in (-1, 0, 1):
                    if math.hypot((x0 + du) * W - u * W, (y0 + dv) * H - v * H) < 6e-3 * max(W, H): return True
        return False
    n = len(segs); miss = 0; covered = 0.0
    for (p, q) in segs:
        mx, my = (p.x + q.x) / 2, (p.y + q.y) / 2
        if not on_tile(mx, my) or not on_tile(p.x, p.y) or not on_tile(q.x, q.y): miss += 1
        covered += math.hypot(q.x - p.x, q.y - p.y)
    # expected drawn length inside the 3 x 3 square: the tile's segment length per tile area, times 9
    per = sum(math.hypot((x1 - x0) * W, (y1 - y0) * H) for (x0, y0, x1, y1) in d['lines']) / (W * H)
    want = per * 9
    ok = miss == 0 and (abs(covered - want) / max(want, 1e-9) < 0.03 if d['lines'] else n > 0)
    bad += 0 if ok else 1
    print(('OK  ' if ok else 'BAD ') + key.ljust(22), 'segments', n, 'off-pattern', miss, 'length %.3f of %.3f' % (covered, want))
print('ezdxf', ezdxf.__version__, 'patterns failing:', bad)
