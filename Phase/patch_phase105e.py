#!/usr/bin/env python3
"""patch_phase105e.py -- V105 the room colour fill reaches the vector sinks: plan SVG and sheet
viewports fill each room with the colour the canvas uses. DXF R12 has no fill entity, as V96."""
NAME = 'patch_phase105e.py'
BASE = '9c49fbd7e4be870c88db15644e9186af0143fb3ec06c1964204b476480c9dabb'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)
rep(r"""        poly(o.pts,true,lay,o.id,rg,true);
        if(!bimRoomTagged(o.id))text(""", r"""        poly(o.pts,true,lay,o.id,bimRoomSchemeGraphics(o,rg,pres),true);   /* __acad3dV105: the colour fill, as on the canvas */
        if(!bimRoomTagged(o.id))text(""")
rep(r"""        poly(o.pts,true,o.id,o.y,rg,true);
        curRoom=false;
""", r"""        poly(o.pts,true,o.id,o.y,bimRoomSchemeGraphics(o,rg,pres),true);   /* __acad3dV105 */
        curRoom=false;
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
