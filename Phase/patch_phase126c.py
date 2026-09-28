"""patch_phase126c.py -- V126: the section in the model.

A column or beam whose type has a profile carries a copy of it as o.bim.section -- under bim, so
bimCarryBim takes it through every rebuild and copy (the V123 rule) -- and its solid is the profile
swept along it (bimSweepMesh): a W beam is an I, a pipe a tube.

Every place a column or beam solid is built passes the section on, so none of them can straighten a
section back into a box: the type change, a column's height, its turn (Properties and the gizmo), its
copy, its mirror, and V123's push on its top. A beam hangs from its level by the top of its section,
its web upright; a column's section turns with the column.

A profiled member's width and depth are its section's extent and cannot be typed: Properties refuses
a new width or depth and says to choose another type, as a wall's thickness is its type's (V123)."""
NAME = 'patch_phase126c.py'
BASE = '8c67e083c6e5d508a9e8f8f742f827647eb418b0500a1ed9edeea14b8a3c7990'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---- the builders take a section
rep("""  function bimBuildBeamGeometry(p1,p2,topY,w,dep){
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    var L=Math.sqrt(dx*dx+dz*dz);
    if(!(L>1e-9))return {error:'Beam endpoints coincide'};""", """  function bimBuildBeamGeometry(p1,p2,topY,w,dep,sec){
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    var L=Math.sqrt(dx*dx+dz*dz);
    if(!(L>1e-9))return {error:'Beam endpoints coincide'};
    /* __acad3dV126: a section, swept -- hung from the level by its top, its web upright */
    if(sec){
      var sp=bimProfileProblem(sec);
      if(sp)return {error:'The beam\\'s section cannot be built: '+sp};
      var ex=bimProfileExtent(sec),ux=dx/L,uz=dz/L,ya=topY-ex.ymax;
      var sm=bimSweepMesh(sec,L,function(y,z,s){return [p1[0]+ux*s-uz*z,ya+y,p1[1]+uz*s+ux*z];});
      return {mesh:sm,length:L,
        bim:{type:'beam',p1:[p1[0],p1[1]],p2:[p2[0],p2[1]],width:ex.width,depth:ex.depth,
          baseY:topY-ex.depth,topY:topY,length:L,levelId:A3D.activeLevel,section:JSON.parse(JSON.stringify(sec))}};
    }""")
rep("""  function bimBuildColumnGeometry(center,y0,w,dep,h,rot){
    var quad=bimRectFootprint(center,w,dep,rot);""", """  function bimBuildColumnGeometry(center,y0,w,dep,h,rot,sec){
    /* __acad3dV126: a section, swept up the column and turned with it */
    if(sec){
      var sp=bimProfileProblem(sec);
      if(sp)return {error:'The column\\'s section cannot be built: '+sp};
      if(!(h>0))return {error:'Column height must be positive'};
      var c=Math.cos(rot||0),sn=Math.sin(rot||0);
      return {mesh:bimSweepMesh(sec,h,function(y,z,s){return [center[0]+y*c-z*sn,y0+s,center[1]+y*sn+z*c];})};
    }
    var quad=bimRectFootprint(center,w,dep,rot);""")

# ---- a type change sets or clears the instance's section
rep("""      var r4=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,t.params.width,t.params.depth,o.bim.height,o.bim.rotation||0);
      if(r4.error)return false;
      o.mesh=r4.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;""", """      var tp4=t.params.profile||null;   /* __acad3dV126 */
      var r4=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,t.params.width,t.params.depth,o.bim.height,o.bim.rotation||0,tp4);
      if(r4.error)return false;
      o.mesh=r4.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;
      if(tp4)o.bim.section=JSON.parse(JSON.stringify(tp4));else delete o.bim.section;""")
rep("""      var r5=bimBuildBeamGeometry(o.bim.p1,o.bim.p2,o.bim.topY,t.params.width,t.params.depth);
      if(r5.error)return false;
      o.mesh=r5.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;o.bim.baseY=r5.bim.baseY;""", """      var tp5=t.params.profile||null;   /* __acad3dV126 */
      var r5=bimBuildBeamGeometry(o.bim.p1,o.bim.p2,o.bim.topY,t.params.width,t.params.depth,tp5);
      if(r5.error)return false;
      o.mesh=r5.mesh;o.bim.width=r5.bim.width;o.bim.depth=r5.bim.depth;o.bim.baseY=r5.bim.baseY;
      if(tp5)o.bim.section=JSON.parse(JSON.stringify(tp5));else delete o.bim.section;""")

# ---- every other place a column is rebuilt passes its section
rep("""    // __acad3dV81: orientation is carried through a resize; editing width must not straighten it.
    var res=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,newW,newDep,newH,o.bim.rotation||0);""", """    // __acad3dV81: orientation is carried through a resize; editing width must not straighten it.
    /* __acad3dV126: a section's size is the section's */
    if(o.bim.section&&(Math.abs(newW-o.bim.width)>1e-9||Math.abs(newDep-o.bim.depth)>1e-9)){
      a3dToast(o.name+'\\'s size is set by its section ('+(bimTypeNameOf(o)||'its type')+'): choose another type to change it');
      return false;
    }
    var res=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,newW,newDep,newH,o.bim.rotation||0,o.bim.section||null);""")
rep("""    var res=bimBuildColumnGeometry(b.center,b.baseY,b.width,b.depth,h,b.rotation||0);""",
    """    var res=bimBuildColumnGeometry(b.center,b.baseY,b.width,b.depth,h,b.rotation||0,b.section||null);   /* __acad3dV126 */""")
rep("""      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height,o.bim.rotation||0);""",
    """      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height,o.bim.rotation||0,o.bim.section||null);   /* __acad3dV126 */""")
rep("""      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height,rotN);""",
    """      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height,rotN,o.bim.section||null);   /* __acad3dV126 */""")
rep("""        var crRes=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,o.bim.width,o.bim.depth,
          o.bim.height,cr*Math.PI/180);""", """        var crRes=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,o.bim.width,o.bim.depth,
          o.bim.height,cr*Math.PI/180,o.bim.section||null);   /* __acad3dV126 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
