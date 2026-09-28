#!/usr/bin/env python3
"""patch_phase105d.py -- V105 the room colour fill is saved: in the undo snapshot, the project
file and local storage, restored by all three."""
NAME = 'patch_phase105d.py'
BASE = '70c3cf1733d363d7fa5fb859bf9d7c05197ee454031126880067ca2b9c549365'
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
rep("site:A3D.site,classificat", "site:A3D.site,roomScheme:A3D.roomScheme||'',classificat", 3)
rep(r"""      if(st&&st.site&&typeof st.site==='object'&&typeof st.site.name==='string')A3D.site=st.site;
""", r"""      if(st&&st.site&&typeof st.site==='object'&&typeof st.site.name==='string')A3D.site=st.site;
      if(st&&(st.roomScheme==='dept'||st.roomScheme==='occupancy'))A3D.roomScheme=st.roomScheme;   /* __acad3dV105 */
""")
rep(r"""    A3D.site=(st.site&&typeof st.site==='object')?st.site:A3D.site;
""", r"""    A3D.site=(st.site&&typeof st.site==='object')?st.site:A3D.site;
    A3D.roomScheme=(st.roomScheme==='dept'||st.roomScheme==='occupancy')?st.roomScheme:'';   /* __acad3dV105 */
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
