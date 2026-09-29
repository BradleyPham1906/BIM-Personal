"""patch_phase127e.py -- V127: test hooks and the marker."""
NAME = 'patch_phase127e.py'
BASE = '1217616e34befb08d0fbbfcaf59ec97396bbe77f0e84e09e80ce8712bf100e40'
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


rep("""  /* __acad3dV126: section profiles */""", """  /* __acad3dV127: the alignment */
  function bimJ(x){return x===null||x===undefined?null:JSON.parse(JSON.stringify(x));}
  window.__a3dAlignFromPts=function(pts,radii,sta0){
    var al=bimNewAlignment(pts,[0,0,0],0);
    if(radii)al.radii=radii.slice();
    if(isFinite(sta0))al.sta0=sta0;
    pushUndo();A3D.objs.push(al);refreshTree();paint();saveSoon();
    return al.id;
  };
  /* an OPEN polyline, as the polyline tool ends one on Enter */
  window.__a3dOpenPolyline=function(pts,bulges){
    startSketch('poly');if(!A3D.sk)return null;
    A3D.sk.pts=(pts||[]).slice();
    if(bulges)A3D.sk.bulges=bulges.slice();
    var o=finishPoly(true);
    return o?A3D.sel:null;
  };
  window.__a3dAlignEditFor=function(id,patch){
    var o=objById(id);if(!bimIsAlignment(o))return false;
    return bimAlignEdit(o,function(c){for(var k in patch)if(patch.hasOwnProperty(k))c[k]=bimJ(patch[k]);});
  };
  window.__a3dAlignGeom=function(id){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignGeom(o)):null;};
  window.__a3dAlignPointAt=function(id,s){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignPointAt(bimAlignGeom(o),s)):null;};
  window.__a3dStationOffset=function(id,p){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignStationOffset(bimAlignGeom(o),p)):null;};
  window.__a3dProfileGeom=function(id){var o=objById(id);return bimIsAlignment(o)&&o.profile?bimJ(bimProfileGeom(o.profile,bimAlignGeom(o))):null;};
  window.__a3dProfileElevAt=function(id,s){var o=objById(id);if(!bimIsAlignment(o)||!o.profile)return null;return bimJ(bimProfileElevAt(bimProfileGeom(o.profile,bimAlignGeom(o)),s));};
  window.__a3dTinHeightAt=function(tid,x,z){var o=objById(tid);return o&&o.t==='terrain'?bimTinHeightAt(bimTerrainTin(o),x,z):null;};
  window.__a3dAlignGround=function(id){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignGround(o,bimAlignGeom(o))):null;};
  window.__a3dAlignDrawn=function(){paint();return bimJ(A3D.lastAlignDrawn||{});};
  window.__a3dFmtStation=function(s){return bimFmtStation(s);};
  window.__a3dStationMark=function(){return bimJ(A3D.stationMark||null);};
  window.__acad3dV127='alignmentobject,pidesign,circularcurves,overlaprefused,stationing,stationoffset,profile,verticalcurves,'+
    'highlowpoint,kvalue,tinheight,groundprofile,alignmentdrawing,stationticks,profileview,alignmentprops,profileprops,'+
    'alignmentcommand,profileviewcommand,stationcommand,alignmentbutton,alignmentschedule,profileschedule,alignmentexport,alignmenttransform';
  /* __acad3dV126: section profiles */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
