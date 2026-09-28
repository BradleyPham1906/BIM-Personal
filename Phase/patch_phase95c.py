"""patch_phase95c.py -- __acad3dV95: the BOUNDARY command.

Pick an internal point, get the closed polyline around it. The tool stays live afterwards, as
AutoCAD's does, because the normal use is picking several regions in a row.

Every curve on the plan takes part -- sketches, wall centrelines and construction lines -- which
is the point of the command: the region a drafter wants is usually bounded by things that were
never drawn as one closed shape.

Islands are named in the toast. The polyline cannot carry a hole, so a region with something
inside it gets a boundary whose area overstates the region, and saying so is the only honest
option short of building multi-loop regions, which this build has no storage for.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '230a731c695120cc678e4bb3499a62577c86ace313924096bca8697e4692eddd'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1,xline:1};""",
     """  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1,xline:1,boundary:1};"""),

    ("""  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',point:'Point',xline:'Construction line',poly:'Polyline',""",
     """  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',point:'Point',xline:'Construction line',boundary:'Boundary',poly:'Polyline',"""),

    ("""  function startPointTool(){""",
     """  /* __acad3dV95 */
  function startBoundaryTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'boundary',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();
    paint();
    a3dToast('Boundary: click inside a region to trace it; Escape when finished');
  }
  function bimApplyBoundary(pt,y){
    var edges=bimBoundaryEdges(y,{walls:true,sketches:true,clines:true});
    if(!edges.length){a3dToast('Boundary: there is nothing on this plan to trace');return null;}
    var res=bimTraceBoundary(edges,pt);
    if(res.error){a3dToast('Boundary: '+res.error);return null;}
    pushUndo();
    /* addSketchObj reads the active sketch for its plane and host and then clears it, so the
       state is put back afterwards and the command stays live for the next pick. */
    var sk=A3D.sk,keep=sk?{tool:sk.tool,pts:[],y:sk.y,on:sk.on}:null;
    A3D.sk={tool:'boundary',pts:[],y:y,on:keep?keep.on:null};
    var msg='Boundary traced, area '+res.area.toFixed(3)+' m2';
    if(res.islands)
      msg+=' - NOTE: this region has something inside it, and a polyline cannot carry a hole, '+
           'so the area above counts the island in';
    var o=addSketchObj(res.pts,{bulges:res.bulges,toast:msg});
    A3D.sk=keep;
    bimSyncStatusHint();paint();
    return o;
  }
  function startPointTool(){"""),

    ("""    if(sk.tool==='xline'){                      /* __acad3dV94 */""",
     """    if(sk.tool==='boundary'){                   /* __acad3dV95 */
      bimApplyBoundary([gx,gz],sk.y);
      return;                                   /* sk stays live: BOUNDARY keeps picking */
    }
    if(sk.tool==='xline'){                      /* __acad3dV94 */"""),

    ("""    if(sk.tool==='point')return 'Specify a point (Escape when finished):';   /* __acad3dV93 */""",
     """    if(sk.tool==='boundary')return 'Pick an internal point (Escape when finished):';  /* __acad3dV95 */
    if(sk.tool==='point')return 'Specify a point (Escape when finished):';   /* __acad3dV93 */"""),

    ("""    ['XLINE',['XL'],'xline','Construction line, infinite both ways'],""",
     """    ['BOUNDARY',['BO','BPOLY'],'boundary','Trace the closed region around a picked point'],
    ['XLINE',['XL'],'xline','Construction line, infinite both ways'],"""),

    ("""    xline:function(){startClineTool(false);}, /* __acad3dV94 */""",
     """    boundary:function(){startBoundaryTool();},/* __acad3dV95 */
    xline:function(){startClineTool(false);}, /* __acad3dV94 */"""),

    ("""  /* __acad3dV94: asked by the Canvas-era shortcut gate before it swallows a plain letter.""",
     """  /* __acad3dV95 */
  window.__a3dBulgedSignedArea=bimBulgedSignedArea;
  window.__a3dEdgeDirAt=bimEdgeDirAt;
  window.__a3dSplitEdge=bimSplitEdge;
  window.__a3dArrangeEdges=bimArrangeEdges;
  window.__a3dTraceBoundary=bimTraceBoundary;
  window.__a3dBoundaryEdges=bimBoundaryEdges;
  window.__a3dApplyBoundary=bimApplyBoundary;
  window.__acad3dV95='planararrangement,edgesplitatcrossings,tangentangularkey,signedbulgedarea,boundarycommand,islandreported,wallfacetracerreplaced';
  /* __acad3dV94: asked by the Canvas-era shortcut gate before it swallows a plain letter."""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
