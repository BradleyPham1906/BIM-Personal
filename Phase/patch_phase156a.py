"""patch_phase156a.py -- V156: the frame's upkeep cut down (from the owner's BENCHMARK).

The owner's computer: 5,000 elements 3.1 ms a frame with WebGPU, 4.1 with WebGL; 20,000, 9.3 and 10.5.
At 20,000 the two engines close up, because most of the frame is the upkeep they share: the walk
over every object that keeps the table current. Measured here, 19 ms of that walk was spent outside
the per-object questions themselves, much of it building a fresh 20,000-key "seen" object each
frame and walking every tracked object again to find the ones gone.
- Each tracked object now carries the frame it was last seen in, kept between frames; the objects
  are counted as they are walked, and the search for the ones gone runs only when the count says
  some are gone.
- A colour by type is looked up once a frame per type, not per object."""
NAME = 'patch_phase156a.py'
BASE = '327e9572ce8ca631cd458f60eb7df8a56ba7037bda7e242cc60c701aa6346b2e'
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
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


rep("""    return A3D_SCENE||(A3D_SCENE={cap:0,data:null,slots:{},free:[],next:0,chunks:[],of:{},dirty:{},cells:{},""",
    """    return A3D_SCENE||(A3D_SCENE={cap:0,data:null,slots:{},free:[],next:0,chunks:[],of:{},dirty:{},cells:{},mark:{},n:0,""")
rep("""    var B=bimScene(),i,o,m,id,c,seen={},totalFaces=0,hasTrans=false,sel=A3D.sel,sel2=A3D.sel2,v=[0,0,0,0,0,0,0,0],t0=performance.now(),rgbOf={};""",
    """    var B=bimScene(),i,o,m,id,c,seenN=0,mark=B.mark,totalFaces=0,hasTrans=false,sel=A3D.sel,sel2=A3D.sel2,v=[0,0,0,0,0,0,0,0],t0=performance.now(),rgbOf={},typeCol={};   /* __acad3dV156 */""")
rep("""      id=o.id;seen[id]=1;B.st.objects++;""", """      id=o.id;if(mark[id]!==B.frame){mark[id]=B.frame;seenN++;}B.st.objects++;   /* __acad3dV156: seen this frame, counted */""")
rep("""        last.ids.push(id);last.refs[id]=m;last.lb[id]=lb;last.verts+=nv;last.dirty=true;B.of[id]=last;c=last;""",
    """        last.ids.push(id);last.refs[id]=m;last.lb[id]=lb;last.verts+=nv;last.dirty=true;B.of[id]=last;c=last;B.n++;""")
rep("""        var hx=bimLensCol(o)||o.col||(TYPES[o.t]||{}).c||'#7f9db8';col=rgbOf[hx]||(rgbOf[hx]=bimHexToRgb(hx));""",
    """        var hx=bimLensCol(o)||o.col;
        if(!hx){hx=typeCol[o.t];if(hx===undefined)hx=typeCol[o.t]=(TYPES[o.t]&&TYPES[o.t].c)||'#7f9db8';}   /* __acad3dV156: a type's colour once a frame */
        col=rgbOf[hx]||(rgbOf[hx]=bimHexToRgb(hx));""")
rep("""    /* the objects gone: out of their chunk, their slot free */
    for(id in B.of)if(B.of.hasOwnProperty(id)&&!seen[id]){""",
    """    /* the objects gone: out of their chunk, their slot free; looked for only when the count says some are */
    if(seenN!==B.n)B.st.scanned=1;
    if(seenN!==B.n)for(id in B.of)if(B.of.hasOwnProperty(id)&&mark[id]!==B.frame){""")
rep("""      delete B.of[id];B.free.push(B.slots[id]);bimGbPut(B,B.slots[id],[0,0,0,-1,0,0,0,0]);delete B.slots[id];""",
    """      delete B.of[id];delete mark[id];B.n--;B.free.push(B.slots[id]);bimGbPut(B,B.slots[id],[0,0,0,-1,0,0,0,0]);delete B.slots[id];""")
rep("""  window.__acad3dV155='spatialchunks,""", """  window.__acad3dV156='seencount,typecolour';
  window.__acad3dV155='spatialchunks,""")
rep("""  var BIM_APP_VERSION={v:'V155',date:'2026-10-04'};   /* __acad3dV155 */""",
    """  var BIM_APP_VERSION={v:'V156',date:'2026-10-04'};   /* __acad3dV156 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
