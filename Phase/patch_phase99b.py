"""patch_phase99b.py -- __acad3dV99: region dependents follow, and the graph links every member.

  * bimRemeasureRoomFromSource and bimFollowSource read a region dependent through
    bimRegionBoundaryWorld, the same way they read a single source through
    bimSourceBoundaryWorld, and write it in the dependent's own frame.
  * bimGraphBuild links EVERY member of a region to it (rel 'region'), so editing any one of the
    shapes that bound a room re-traces the room, in dependency order, before anything built on
    the room.
  * A region room moved on its own RE-BOUNDS where it now is (a Revit room is a point that finds
    its boundary). Any other region dependent moved without all of its members is detached, and
    says so, the V97 rule.
  * bimCutSource knows how to detach a region.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'a5aaf51b22d17b2ad5e4f820cb8785de6ba1e9236e2ef45a0696bdde05a2bfa6'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""    source:{fwd:'Source shape',rev:'Room bounded by this'},""",
     """    source:{fwd:'Source shape',rev:'Room bounded by this'},
    region:{fwd:'Bounded by',rev:'Bounds this region'},   /* __acad3dV99 */"""),
    ("""  function bimCutSource(o,why){
    if(!o||!bimGraphRoomSourceId(o))return false;""",
     """  function bimCutSource(o,why){
    if(o&&bimIsRegionDep(o)){   /* __acad3dV99: a region is detached from ALL of its members */
      var nm=(o.region.members||[]).length;
      delete o.region;
      o.sourceId=null;o.sourceType=null;
      if(o.bim){o.bim.sourceId=null;o.bim.sourceType=null;}
      a3dToast(o.name+' is no longer linked to the '+nm+' shape'+(nm===1?'':'s')+' that bounded it'+
        (why?(' ('+why+')'):'')+' - it keeps its current shape');
      return true;
    }
    if(!o||!bimGraphRoomSourceId(o))return false;"""),
    ("""        if(srcId&&srcId!==o.id)link(bimGraphObjKey(srcId),key,'source');""",
     """        if(srcId&&srcId!==o.id)link(bimGraphObjKey(srcId),key,'source');
        /* __acad3dV99: a region depends on every shape its last trace walked */
        if(bimIsRegionDep(o)&&o.region.members){
          var rm;
          for(rm=0;rm<o.region.members.length;rm++)
            if(o.region.members[rm]!==o.id)link(bimGraphObjKey(o.region.members[rm]),key,'region');
        }"""),
    ("""  function bimRemeasureRoomFromSource(room,ctx){
    if(!room||room.t!=='room')return false;
    var st=room.sourceType,sid=room.sourceId;""",
     """  function bimRemeasureRoomFromSource(room,ctx){
    if(!room||room.t!=='room')return false;
    if(bimIsRegionDep(room)){   /* __acad3dV99 */
      var rb=bimRegionBoundaryWorld(room);
      if(rb.error){
        if(rb.unenclosed)return bimRegionNoteOpen(room,rb,ctx);
        console.warn('[BIM] '+room.name+': '+rb.error+'; its boundary was NOT updated.');
        if(ctx){ctx.roomsFailed++;ctx.dependentsFailed=(ctx.dependentsFailed||0)+1;}
        return false;
      }
      var rq=bimObjOffset(room);
      room.pts=bimToFrame(room,rb.ring);
      room.y=rb.y-rq[1];
      room.area=bimPolyArea(room.pts);
      bimRegionRecord(room,rb);
      if(ctx){ctx.roomsUpdated++;ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;}
      return true;
    }
    var st=room.sourceType,sid=room.sourceId;"""),
    ("""  function bimFollowSource(o,ctx){
    var sid=bimGraphRoomSourceId(o);
    if(!sid)return false;
    if(o.t==='room')return bimRemeasureRoomFromSource(o,ctx);
    var b=bimSourceBoundaryWorld(objById(sid));""",
     """  function bimFollowSource(o,ctx){
    var sid=bimGraphRoomSourceId(o),isReg=bimIsRegionDep(o);   /* __acad3dV99 */
    if(!sid&&!isReg)return false;
    if(o.t==='room')return bimRemeasureRoomFromSource(o,ctx);
    var b=isReg?bimRegionBoundaryWorld(o):bimSourceBoundaryWorld(objById(sid));"""),
    ("""    if(b.error)return fail(b.error);
    var q=bimObjOffset(o),res,prof;""",
     """    if(b.error){
      if(isReg&&b.unenclosed)return bimRegionNoteOpen(o,b,ctx);
      return fail(b.error);
    }
    var q=bimObjOffset(o),res,prof;"""),
    ("""    A3D.meshes={};
    if(ctx)ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;
    return true;
  }""",
     """    if(isReg)bimRegionRecord(o,b);   /* __acad3dV99 */
    A3D.meshes={};
    if(ctx)ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;
    return true;
  }"""),
    ("""    /* __acad3dV97: every other boundary-derived object follows its source the same way. */
    if(bimGraphRoomSourceId(o)){""",
     """    /* __acad3dV97: every other boundary-derived object follows its source the same way.
       __acad3dV99: and so does one bounded by a region. */
    if(bimGraphRoomSourceId(o)||bimIsRegionDep(o)){"""),
    ("""      var oSrc=origin?bimGraphRoomSourceId(origin):null;
      if(oSrc&&objIds.indexOf(oSrc)<0)bimCutSource(origin,'moved on its own');
    }""",
     """      var oSrc=origin?bimGraphRoomSourceId(origin):null;
      if(oSrc&&objIds.indexOf(oSrc)<0)bimCutSource(origin,'moved on its own');
      /* __acad3dV99: a region dependent that was itself edited. A room re-bounds where it now
         is. Anything else re-derives only when every one of its members moved with it, and is
         otherwise detached. Re-derived HERE because the propagation below skips the nodes it
         starts from, and it must happen before anything built on it is visited. */
      if(origin&&bimIsRegionDep(origin)){
        var allIn=true,mi,mem=origin.region.members||[];
        for(mi=0;mi<mem.length;mi++)if(objIds.indexOf(mem[mi])<0){allIn=false;break;}
        if(origin.t==='room'||allIn)regionOrigins.push(origin);
        else bimCutSource(origin,'moved on its own');
      }
    }
    for(i=0;i<regionOrigins.length;i++)bimFollowSource(regionOrigins[i],ctx);"""),
    ("""    var ctx={reason:reason||'rebuild',delta:delta||null,recut:0,failed:0,recutWalls:{},wallsRebaked:{},roomsUpdated:0,roomsFailed:0,clonesUpdated:0,clonesFailed:0,openingsShifted:0};
    var keys=[],i;""",
     """    var ctx={reason:reason||'rebuild',delta:delta||null,recut:0,failed:0,recutWalls:{},wallsRebaked:{},roomsUpdated:0,roomsFailed:0,clonesUpdated:0,clonesFailed:0,openingsShifted:0};
    var keys=[],i,regionOrigins=[];   /* __acad3dV99 */"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
