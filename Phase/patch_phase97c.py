"""patch_phase97c.py -- __acad3dV97: dependents record their source when they are made.

A link can only be followed if it was recorded. Four creation paths dropped it:

  - the Floor tool had the boundary's sourceType and sourceId in hand and passed only pts and y
    on to the dialog;
  - Floor from a selected sketch or wall built a profile with no source at all, and read the
    sketch in LOCAL coordinates, so a moved sketch floored at its old position;
  - Ceiling received the full boundary and stored only its points;
  - Hatch on a selected sketch or room copied the points, again in local coordinates.

Each now records its source, and the selected-object paths read the boundary through the source
contract, so what is created is exactly what a later edit will re-derive.

A hatch made by PICKING a point is deliberately left unlinked. Its region comes from the whole
arrangement -- possibly four different lines that merely cross -- and there is no single
object it could follow. Its properties say so rather than implying a link that is not there.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '81f717b4696e78d5aba0ab733670ebd6f10bc10cb98165d8e38b7fce3f8feb9f'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # --- floor tool: pass the source on
    ("""      openFloorDlg({pts:sketchCCW(flB.pts),y:flB.y});""",
     """      openFloorDlg({pts:sketchCCW(flB.pts),y:flB.y,sourceType:flB.sourceType,sourceId:flB.sourceId});   /* __acad3dV97 */"""),

    # --- floor from a selection: the contract, and the source
    ("""    if(o.t==='sketch'){
      var P=sketchCCW(bimSketchOutline(o));   /* __acad3dV93 */
      if(P.length<3)return null;
      return {pts:P,y:o.y};
    }
    if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed&&o.bim.innerLoop&&o.bim.innerLoop.length>=3){
      return {pts:sketchCCW(o.bim.innerLoop),y:o.bim.baseY};
    }
    return null;""",
     """    /* __acad3dV97: through the source contract, in world coordinates, and carrying the
       source so the floor follows it. This read a moved sketch at its old position and
       recorded nothing about where the profile came from. */
    if((o.t==='sketch'&&!bimIsPoint(o))||
       (o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed)){
      var sb=bimSourceBoundaryWorld(o);
      if(sb.error)return null;
      return {pts:sketchCCW(sb.ring),y:sb.y,sourceType:sb.type,sourceId:o.id};
    }
    return null;"""),

    # --- buildFloorSolid stores it
    ("""      bim:{type:'floor',thickness:thickness,material:material,levelId:lvl.id,baseY:prof.y,profile:prof.pts.slice()}};
    A3D.objs.push(o);""",
     """      bim:{type:'floor',thickness:thickness,material:material,levelId:lvl.id,baseY:prof.y,profile:prof.pts.slice()}};
    if(prof.sourceId&&(prof.sourceType==='sketch'||prof.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=prof.sourceId;o.sourceType=prof.sourceType;
    }
    A3D.objs.push(o);"""),

    # --- buildCeilingSolid stores it
    ("""      bim:{type:'ceiling',thickness:thickness,heightAbove:heightAbove,levelId:lvl.id,baseY:ceilY,profile:sketchCCW(boundary.pts)},layer:A3D.activeLayer};
    bimEnsureObjType(o);""",
     """      bim:{type:'ceiling',thickness:thickness,heightAbove:heightAbove,levelId:lvl.id,baseY:ceilY,profile:sketchCCW(boundary.pts)},layer:A3D.activeLayer};
    if(boundary.sourceId&&(boundary.sourceType==='sketch'||boundary.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=boundary.sourceId;o.sourceType=boundary.sourceType;
    }
    bimEnsureObjType(o);"""),

    # --- hatch on a selection: the contract, and the source
    ("""    if(o.t==='sketch'&&!bimIsPoint(o)&&o.closed!==false&&o.pts&&o.pts.length>=2)
      return {pts:o.pts,bulges:o.bulges||null,y:o.y,from:o.name};
    if(o.t==='room'&&o.pts&&o.pts.length>=3)
      return {pts:o.pts,bulges:null,y:o.y,from:o.name};
    return null;""",
     """    /* __acad3dV97: world coordinates through the source contract, and the source recorded so
       the hatch follows the sketch or room it was put on. A room is a valid source: hatch on a
       room on a sketch is a chain, and the graph visits the room before the hatch. */
    if((o.t==='sketch'&&!bimIsPoint(o)&&o.closed!==false)||o.t==='room'){
      var sb=bimSourceBoundaryWorld(o);
      if(sb.error)return null;
      return {pts:sb.pts,bulges:sb.bulges,y:sb.y,from:o.name,sourceType:sb.type,sourceId:o.id};
    }
    return null;"""),

    ("""        var ho=bimAddHatch(selObj.pts,selObj.bulges,selObj.y,opts);""",
     """        var ho=bimAddHatch(selObj.pts,selObj.bulges,selObj.y,
          {pattern:opts.pattern,patternAngle:opts.patternAngle,patternScale:opts.patternScale,
           patternColor:opts.patternColor,sourceType:selObj.sourceType,sourceId:selObj.sourceId});"""),

    ("""    if(bimHasBulge(bulges))o.bulges=bulges.slice();
    A3D.objs.push(o);
    return o;
  }
  /* ================= __acad3dV94: construction lines =================""",
     """    if(bimHasBulge(bulges))o.bulges=bulges.slice();
    if(opts.sourceId){o.sourceId=opts.sourceId;o.sourceType=opts.sourceType||null;}   /* __acad3dV97 */
    A3D.objs.push(o);
    return o;
  }
  /* ================= __acad3dV94: construction lines ================="""),

    # --- the hatch's properties say whether it follows anything
    ("""      dims+=bimPropText('Boundary points',o.pts.length);""",
     """      dims+=bimPropText('Boundary points',o.pts.length);
      dims+=bimPropText('Follows',o.sourceId?(((objById(o.sourceId)||{}).name)||'(missing)'):
        'Nothing - traced from the arrangement, so there is no single source to follow');"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
