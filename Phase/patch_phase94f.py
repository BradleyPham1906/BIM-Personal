"""patch_phase94f.py -- __acad3dV94: the commands, and the surface the suite drives.

XLINE was already a row in the shared registry pointing at an act nothing implemented, so it
never appeared in the palette (the V86 filter derives the list from BIM_CMD_MAP and had been
hiding it correctly). RAY had no row at all. Both land here.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'f80000f4737ae8d0b66c53a2ae4e0b87e4081934a26a3e81a3905075d277daa3'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""    ['SPLINE',['SPL'],'spline','Spline through fit points'],['XLINE',['XL'],'xline','Construction line'],""",
     """    ['SPLINE',['SPL'],'spline','Spline through fit points'],
    ['XLINE',['XL'],'xline','Construction line, infinite both ways'],
    ['RAY',[],'ray','Construction ray, infinite one way'],"""),

    ("""    polygon:function(){openPolygonDlg();},    /* __acad3dV93 */""",
     """    polygon:function(){openPolygonDlg();},    /* __acad3dV93 */
    xline:function(){startClineTool(false);}, /* __acad3dV94 */
    ray:function(){startClineTool(true);},    /* __acad3dV94 */"""),

    ("""  /* __acad3dV93 */
  window.__a3dPointAtLength=bimPointAtLength;""",
     """  /* __acad3dV94 */
  window.__a3dClipInfinite=bimClipInfinite;
  window.__a3dClineSegIntersect=bimClineSegIntersect;
  window.__a3dClineArcIntersect=bimClineArcIntersect;
  window.__a3dClineCrossings=bimClineCrossings;
  window.__a3dClineDir=bimClineDir;
  window.__a3dClineModeLabels=bimClineModeLabels;
  window.__a3dClineModeForKey=bimClineModeForKey;
  window.__a3dDrawingExtent2D=bimDrawingExtent2D;
  window.__a3dIsCline=function(id){return bimIsCline(objById(id));};
  window.__a3dClineVisibleSeg=function(id){var o=objById(id);return o?bimClineVisibleSeg(o,null):null;};
  window.__a3dClinesOnPlane=bimClinesOnPlane;
  window.__a3dAddCline=function(p,dir,ray,y){
    var o=bimAddCline(p,dir,ray,y);
    if(o){refreshTree();paint();}
    return o?o.id:null;
  };
  window.__a3dSkCline=function(){
    var sk=A3D.sk;
    if(!sk||sk.tool!=='xline')return null;
    return {mode:sk.mode||null,angle:(typeof sk.angle==='number')?sk.angle:null,
            ray:!!sk.ray,pts:sk.pts.length,readyDir:bimClineReadyDir(sk)};
  };
  window.__a3dPickAt=function(x,y){var o=pick(x,y);return o?o.id:null;};
  window.__acad3dV94='xline,ray,liangbarskyclip,derivedextent,clinecrossingsnap,clinepick,pointpickfix';
  /* __acad3dV93 */
  window.__a3dPointAtLength=bimPointAtLength;"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
