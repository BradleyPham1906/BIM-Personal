#!/usr/bin/env python3
"""patch_phase105f.py -- V105 test-observable APIs and the phase marker."""
NAME = 'patch_phase105f.py'
BASE = '9882394f65c1dbeb81f7bbaefb1eae72f5de700bcd87474aa76d9c9ebf02c35f'
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
rep(r"""    return (A3D.lastRoomStyle&&A3D.lastRoomStyle[roomId])?A3D.lastRoomStyle[roomId]:null;
  };
""", r"""    return (A3D.lastRoomStyle&&A3D.lastRoomStyle[roomId])?A3D.lastRoomStyle[roomId]:null;
  };
  /* __acad3dV105: occupant load and the room colour fill, read from the same functions the
     schedule, the Properties panel and every sink read. */
  window.__a3dOccLoads=function(){return BIM_OCC_LOADS.map(function(r){return {name:r[0],ft2:r[1],basis:r[2]};});};
  window.__a3dRoomLoad=function(id){
    var o=objById(id);
    if(!o||o.t!=='room')return null;
    return {area:o.area,factor:bimRoomLoadFactor(o),occupants:bimRoomOccupants(o),text:bimRoomOccupantsText(o),hint:bimRoomLoadFactorHint(o)};
  };
  window.__a3dRoomScheme=function(by){if(by!==undefined)bimSetRoomScheme(by);return A3D.roomScheme||'';};
  window.__a3dRoomLegend=function(){return A3D.lastRoomLegend||null;};
  window.__acad3dV105='occupantload,ibc1004_5,roomloadfactor,roomcopyfields,roomcolourfill,roomlegend,schemesinks';
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
