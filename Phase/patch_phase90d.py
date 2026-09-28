"""patch_phase90d.py -- Phase 90 part 4: WALL is a command.

Found while writing the suite: the command line cannot start the WALL tool. It is this app's
primary BIM drawing tool, it has worked from the ribbon since V5, and no registry row ever
pointed at it - so typing WALL did nothing, and Enter could not repeat it either.

This is the V87 finding again (ROTATE, ARRAYRECT, ARRAYPOLAR were all built and unreachable). The
same fix: a row, an act, and it appears in the palette automatically because pool() filters by
__a3dCmdSupported rather than by a hand-kept list.
"""
import hashlib, pathlib, sys

BASE = 'd567c43e849d93bb5e910263e0ee7b81c64bcd5fe58636e2c7db72a7ca7ebacb'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

reps.append(("""    ['LINE',['L'],'line','Draw a line'],['PLINE',['PL','POLYLINE','POLY'],'poly','Draw a polyline'],""",
"""    ['LINE',['L'],'line','Draw a line'],['PLINE',['PL','POLYLINE','POLY'],'poly','Draw a polyline'],
    ['WALL',['WA'],'wall','Draw a wall (A for arc segments)'],""", 1))

reps.append(("""    arc:function(){startArcTool();},          /* __acad3dV88 */""",
"""    arc:function(){startArcTool();},          /* __acad3dV88 */
    wall:function(){startWallTool();},        /* __acad3dV90: built in V5, unreachable until now */""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
