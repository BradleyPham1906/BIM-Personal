"""patch_phase105bd.py"""
NAME = 'patch_phase105bd'
BASE = '3e3d9cdc19a72e4d6bb908730f60ae8f9e14f6beedcede03eb9d1f8742a782b3'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
# --- patch d: Areas by Level, as a registered schedule.

rep("""concat(BIM_MAT_COLS)}
  };""","""concat(BIM_MAT_COLS)},
    arealevel:{label:'Areas by Level',build:bimBuildAreaSchedule,cols:[{key:'level',label:'Level'},{key:'gross',label:'Gross (m\\u00b2)',fmt:2},{key:'net',label:'Net (m\\u00b2)',fmt:2},{key:'efficiency',label:'Efficiency (%)',fmt:1},{key:'rooms',label:'Rooms'},{key:'occupants',label:'Occupant Load'},{key:'note',label:'Note'}]}   /* __acad3dV105b */
  };""",1)

rep("""  function bimBuildDoorSchedule(){""","""  function bimBuildAreaSchedule(){
    var out=[],i,a;
    for(i=0;i<A3D.levels.length;i++){
      a=bimLevelAreas(A3D.levels[i].id);
      out.push({level:a.level,gross:a.gross,net:a.rooms?a.net:null,efficiency:a.efficiency,
                rooms:a.rooms,occupants:(a.occupants===null?'':a.occupants),note:a.note});
    }
    return out;
  }
  function bimBuildDoorSchedule(){""",1)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
