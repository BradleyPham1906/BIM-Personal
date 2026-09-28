"""patch_phase97b.py -- __acad3dV97: every boundary-derived object follows its source.

Rooms were the only thing in the graph that followed a boundary. Floors, ceilings and hatches
recorded nothing about where they came from, and roofs recorded their source and were then
ignored -- the data was stored, the edge was never built, and the visitor had no branch for
them. Edit the sketch under a floor slab and the slab stayed where it was.

Three changes, and each replaces a room-only rule with a general one:

  - THE EDGE. bimGraphBuild linked a source only `if(o.t==='room')`. It now links whenever an
    object records a source -- derived from the data rather than from a list of types that is
    already out of date.
  - THE VISITOR. bimFollowSource rebuilds a hatch, floor, ceiling or roof from its source's
    current boundary, through the V97 source contract, into the dependent's own frame.
  - THE CUT. Moving a dependent on its own detaches it from its source: it no longer matches
    that boundary, so following it would snap it back. That rule existed for rooms and nothing
    else, and it was SILENT -- sourceId was nulled and the user was never told the room had
    become a snapshot. It is now general, and it says so.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'e29562044bfee42feef427919dfb8aaf25bd0bb111c8a1e9a3b4cc7906bf05c4'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # --- the accessor is general now, and says so; one writer to go with it
    ("""  function bimGraphRoomSourceId(o){
    if(!o)return null;
    if(o.sourceId)return o.sourceId;
    if(o.bim&&o.bim.sourceId)return o.bim.sourceId;
    return null;
  }""",
     """  /* __acad3dV97: the source of ANY boundary-derived object, not only a room's. Rooms, floors,
     ceilings and hatches keep it at the top level; a roof has always kept it in bim. */
  function bimGraphRoomSourceId(o){
    if(!o)return null;
    if(o.sourceId)return o.sourceId;
    if(o.bim&&o.bim.sourceId)return o.bim.sourceId;
    return null;
  }
  function bimSourceTypeOf(o){
    if(!o)return null;
    return o.sourceType||(o.bim&&o.bim.sourceType)||null;
  }
  /* Detach a dependent from its source, and SAY so. Before this the cut was silent: the id was
     nulled and the room quietly became a snapshot of the shape it had when it was moved. */
  function bimCutSource(o,why){
    if(!o||!bimGraphRoomSourceId(o))return false;
    var srcName=(objById(bimGraphRoomSourceId(o))||{}).name||'its source';
    o.sourceId=null;o.sourceType=null;
    if(o.bim){o.bim.sourceId=null;o.bim.sourceType=null;}
    a3dToast(o.name+' is no longer linked to '+srcName+(why?(' ('+why+')'):'')+
      ' - it keeps its current shape');
    return true;
  }"""),

    # --- THE EDGE: derived from the data, not from o.t==='room'
    ("""        if(o.t==='room'&&srcId)link(bimGraphObjKey(srcId),key,'source');""",
     """        /* __acad3dV97: any object that records a source depends on it. This was room-only,
           so a roof that stored its source was never linked to it. */
        if(srcId&&srcId!==o.id)link(bimGraphObjKey(srcId),key,'source');"""),

    # --- THE VISITOR
    ("""      bimRemeasureRoomFromSource(o,ctx);
      return;
    }
    if(o.linkSourceId){""",
     """      bimRemeasureRoomFromSource(o,ctx);
      return;
    }
    /* __acad3dV97: every other boundary-derived object follows its source the same way. */
    if(bimGraphRoomSourceId(o)){
      bimFollowSource(o,ctx);
      return;
    }
    if(o.linkSourceId){"""),

    ("""  function bimGraphVisit(node,g,ctx){""",
     """  /* __acad3dV97: rebuild a hatch, floor, ceiling or roof from its source's CURRENT boundary.
     Reads the boundary through the source contract and writes it in the dependent's own frame,
     so a dependent that has been moved together with its source does not get its offset twice.
     A failure leaves the object exactly as it was and says why -- never half-rebuilt. */
  function bimFollowSource(o,ctx){
    var sid=bimGraphRoomSourceId(o);
    if(!sid)return false;
    if(o.t==='room')return bimRemeasureRoomFromSource(o,ctx);
    var b=bimSourceBoundaryWorld(objById(sid));
    function fail(msg){
      console.warn('[BIM] '+o.name+': '+msg+'; it was NOT updated.');
      if(ctx)ctx.dependentsFailed=(ctx.dependentsFailed||0)+1;
      return false;
    }
    if(b.error)return fail(b.error);
    var q=bimObjOffset(o),res,prof;
    try{
      if(bimIsHatch(o)){
        o.pts=bimToFrame(o,b.pts);
        if(b.bulges)o.bulges=b.bulges.slice();else delete o.bulges;
        o.y=b.y-q[1];
      }else if(o.t==='solid'&&o.bim&&o.bim.type==='floor'){
        prof=sketchCCW(bimToFrame(o,b.ring));
        res=bimBuildFloorGeometry(prof,o.bim.baseY,o.bim.thickness);
        if(res.error)return fail(res.error);
        o.mesh=res.mesh;o.bim.profile=prof;
      }else if(o.t==='solid'&&o.bim&&o.bim.type==='ceiling'){
        prof=sketchCCW(bimToFrame(o,b.ring));
        res=bimBuildFloorGeometry(prof,o.bim.baseY+o.bim.thickness,o.bim.thickness);
        if(res.error)return fail(res.error);
        o.mesh=res.mesh;o.bim.profile=prof;
      }else if(o.t==='solid'&&o.bim&&o.bim.type==='roof'){
        var fp=bimToFrame(o,b.ring);
        /* Gable choices are edge INDICES, so they only survive a change that kept the edge
           count; otherwise they would name edges that are no longer the same edges. */
        var keepG=(o.bim.footprint&&o.bim.footprint.length===fp.length)?(o.bim.gables||[]):[];
        res=bimBuildRoofGeometry(fp,o.bim.baseY,o.bim.pitch,o.bim.slopeDir,o.bim.thickness,
          {style:o.bim.style||'shed',gables:keepG});
        if(res.error)return fail(res.error);
        var k,old=o.bim;
        for(k in res.bim)if(res.bim.hasOwnProperty(k))old[k]=res.bim[k];
        o.mesh=res.mesh;
      }else{
        return fail('this kind of object does not know how to follow a boundary');
      }
    }catch(eF){
      console.warn('[BIM] Following a source failed for '+o.name,eF);
      return fail('its rebuild raised an error');
    }
    A3D.meshes={};
    if(ctx)ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;
    return true;
  }
  function bimGraphVisit(node,g,ctx){"""),

    # --- THE CUT: general, and audible
    ("""      if(origin&&origin.t==='room'&&origin.sourceId&&objIds.indexOf(origin.sourceId)<0){origin.sourceId=null;origin.sourceType=null;}""",
     """      /* __acad3dV97: general, and no longer silent. This was rooms only, and nulled the id
         without a word, so the user could not tell a room had stopped following its sketch. */
      var oSrc=origin?bimGraphRoomSourceId(origin):null;
      if(oSrc&&objIds.indexOf(oSrc)<0)bimCutSource(origin,'moved on its own');"""),

    # --- rotate-in-place and scale-in-place cut through the same helper
    ("""    else if(g.kind==='room'){o.pts=g.pts;o.sourceType=null;o.sourceId=null;}""",
     """    else if(g.kind==='room'){o.pts=g.pts;bimCutSource(o,'rotated on its own');}   /* __acad3dV97 */"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

# scale-in-place: same cut, one more field on the line
OLD_SC = """    else if(g.kind==='room'){o.pts=g.pts;o.sourceType=null;o.sourceId=null;"""
assert txt.count(OLD_SC) == 1, 'scale cut count %d' % txt.count(OLD_SC)
txt = txt.replace(OLD_SC, """    else if(g.kind==='room'){o.pts=g.pts;bimCutSource(o,'scaled on its own');   /* __acad3dV97 */""", 1)

assert txt.count("o.sourceType=null;o.sourceId=null") == 0, 'a silent cut survives'

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
