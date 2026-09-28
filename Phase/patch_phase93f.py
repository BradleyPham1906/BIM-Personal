"""patch_phase93f.py -- __acad3dV93: the POINT node.

AutoCAD's POINT is a node entity: no length, no area, drawn as a marker, and there to be
snapped to. DIVIDE and MEASURE exist to place them, so POINT is their prerequisite and is built
first.

It is a sketch carrying exactly one vertex, tagged kind:'point'. That is not a shortcut, it is
the cheapest correct place for it: the sketch family already IS this build's 2D entity family,
so a point is persisted, layered, levelled, selected, marquee-tested, moved, copied, mirrored
and node-snapped by code that already exists and already guards on vertex count. The renderers
skipped it (their guards are >=2), so a marker branch is added to each of the four -- viewport,
DXF, SVG, sheet -- all drawing from bimPointMarkerSegs so no two can disagree about what a
point looks like.

Three operations have no meaning on a point and now refuse it by name rather than by tripping
a guard meant for something else: Pad, Pocket and Offset.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '5583538d409a00d0dafb528fcf1b668cfaa4615bca4f548e8ddd375a25a056e2'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # ---- core: the predicate, the marker and the constructor
    ("""  /* __acad3dV93: what shape is this sketch. The ONE answer, so the five consumers that""",
     """  /* ================= __acad3dV93: the POINT node ================= */
  var BIM_POINT_MARK=0.15;          /* half-length of the marker cross, in model units */
  function bimIsPoint(o){
    return !!(o&&o.t==='sketch'&&o.kind==='point'&&o.pts&&o.pts.length===1);
  }
  /* The marker, as line segments in the plan. Every renderer draws from this one function, so
     the viewport, the DXF, the SVG and the sheet cannot show four different points. */
  function bimPointMarkerSegs(p){
    var m=BIM_POINT_MARK;
    return [[[p[0]-m,p[1]],[p[0]+m,p[1]]],
            [[p[0],p[1]-m],[p[0],p[1]+m]]];
  }
  /* Placed directly rather than through addSketchObj, because DIVIDE and MEASURE place many at
     once and addSketchObj clears the active sketch, selects what it made and toasts per
     object. The caller decides selection and what to say. */
  function bimAddPoint(x,z,y,layer){
    A3D.counts.point=(A3D.counts.point||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'sketch',kind:'point',name:'Point '+A3D.counts.point,col:'#ffd479',
      pos:[0,0,0],pts:[[x,z]],y:(typeof y==='number')?y:bimGetActiveLevel().elev,
      closed:false,layer:(layer===undefined?A3D.activeLayer:layer)
    };
    A3D.objs.push(o);
    return o;
  }
  function startPointTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'point',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();
    paint();
    a3dToast('Point: click to place a node; Escape or Enter when finished');
  }
  /* __acad3dV93: what shape is this sketch. The ONE answer, so the five consumers that"""),

    ("""  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',poly:'Polyline',""",
     """  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',point:'Point',poly:'Polyline',"""),

    # ---- the point handler: POINT repeats until cancelled, as AutoCAD's does
    ("""    if(sk.tool==='rect'||sk.tool==='circle'||sk.tool==='polygon'){""",
     """    if(sk.tool==='point'){                      /* __acad3dV93 */
      pushUndo();
      var np=bimAddPoint(gx,gz,sk.y);
      A3D.sel=np.id;A3D.sel2=null;
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast(np.name+' placed at '+gx.toFixed(3)+', '+gz.toFixed(3));
      return;                                   /* sk stays live: POINT keeps placing */
    }
    if(sk.tool==='rect'||sk.tool==='circle'||sk.tool==='polygon'){"""),

    ("""    if(sk.tool==='polygon')return n?('Specify radius of circle ('+""",
     """    if(sk.tool==='point')return 'Specify a point (Escape when finished):';   /* __acad3dV93 */
    if(sk.tool==='polygon')return n?('Specify radius of circle ('+"""),

    # ---- viewport: a 1-vertex sketch stroked nothing, so draw the marker
    ("""      if(o.t!=='sketch')continue;
      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':'#5ec4b8',(o.closed!==false),false,bimObjOffset(o),o.bulges);""",
     """      if(o.t!=='sketch')continue;
      if(bimIsPoint(o)){                        /* __acad3dV93 */
        var pmSeg=bimPointMarkerSegs(o.pts[0]),pmQ=bimObjOffset(o),pmK;
        for(pmK=0;pmK<pmSeg.length;pmK++)
          drawSketchPath(ctx,V,W,H,pmSeg[pmK],o.y,(o.id===A3D.sel)?'#4ea1ff':'#ffd479',false,false,pmQ,null);
        continue;
      }
      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':'#5ec4b8',(o.closed!==false),false,bimObjOffset(o),o.bulges);"""),

    # ---- DXF
    ("""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        /* __acad3dV88: DXF carries the arc itself.""",
     """      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var dxPM=bimPointMarkerSegs(o.pts[0]),dxPK;
        for(dxPK=0;dxPK<dxPM.length;dxPK++)line(dxPM[dxPK][0],dxPM[dxPK][1],lay);
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        /* __acad3dV88: DXF carries the arc itself."""),

    # ---- SVG export
    ("""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,lay,o.id,rg,false);   /* __acad3dV88 */""",
     """      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var svPM=bimPointMarkerSegs(o.pts[0]),svPK;
        for(svPK=0;svPK<svPM.length;svPK++)line(svPM[svPK][0],svPM[svPK][1],lay,o.id,rg);
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,lay,o.id,rg,false);   /* __acad3dV88 */"""),

    # ---- sheet viewport SVG
    ("""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,o.id,o.y,rg,false);   /* __acad3dV88 */""",
     """      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var shPM=bimPointMarkerSegs(o.pts[0]),shPK;
        for(shPK=0;shPK<shPM.length;shPK++)ln(shPM[shPK][0],shPM[shPK][1],o.id,o.y,rg);
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,o.id,o.y,rg,false);   /* __acad3dV88 */"""),

    # ---- Pad and Pocket take a sketch; a point is not one
    ("""  function selSketch(){""",
     """  /* __acad3dV93: a point is a sketch by storage and not by nature. Pad, Pocket and the
     sketch-constraint panel all reach the selection through here, so excluding it once keeps
     every one of them from offering an operation a node cannot carry. */
  function selSketch(){"""),

    ("""    return (o&&o.t==='sketch')?o:null;""",
     """    return (o&&o.t==='sketch'&&!bimIsPoint(o))?o:null;"""),

    # ---- Offset refuses by name
    ("""    if(o.t==='sketch'){
      /* __acad3dV90: same treatment for a sketch that carries arcs. */""",
     """    if(bimIsPoint(o))return {error:'Offset: a point has no side to offset to'};   /* __acad3dV93 */
    if(o.t==='sketch'){
      /* __acad3dV90: same treatment for a sketch that carries arcs. */"""),

    # ---- properties and the schedule label
    ("""    }else if(o.t==='sketch'){
      dims+=bimPropText('Points',o.pts.length);
      dims+=bimPropText('Closed',o.closed!==false?'Yes':'No');""",
     """    }else if(bimIsPoint(o)){                    /* __acad3dV93 */
      dims+=bimPropText('X',o.pts[0][0].toFixed(3));
      dims+=bimPropText('Y',o.pts[0][1].toFixed(3));
    }else if(o.t==='sketch'){
      dims+=bimPropText('Points',o.pts.length);
      dims+=bimPropText('Closed',o.closed!==false?'Yes':'No');"""),

    ("""    if(o.t==='sketch')return 'Lines : Model Lines';""",
     """    if(bimIsPoint(o))return 'Points : Nodes';   /* __acad3dV93 */
    if(o.t==='sketch')return 'Lines : Model Lines';"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
