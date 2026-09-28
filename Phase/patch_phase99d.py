"""patch_phase99d.py -- __acad3dV99: changes to WHICH shapes bound a region.

The graph carries an edit of a member to its region. It cannot carry a shape that is NOT yet a
member -- a line drawn across a room, a wall added to close it, a sketch deleted out of its
boundary -- because there is no edge from a shape to a region it does not bound yet.

saveSoon() is the one call every model mutation already makes (152 sites), so the check runs
there: for each plane that has region dependents, the signature of its edges is compared with
the one each dependent recorded at its last trace. Only a dependent whose plane changed is
re-traced, then everything built on it is propagated in dependency order.

Two more things are settled in the same pass:
  * A room saved by an older build as 'wallgroup' is ADOPTED: given a seed inside its current
    shape and its members, without changing its shape. It follows from then on.
  * A dependent whose single source was deleted is detached and told, instead of keeping a
    sourceId that names nothing.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'fb31031f14bd88ffe04700ad3cf3cf80d61110fb293e3e41aae00023ed2c2559'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """  function saveSoon(){
    if(saveT)clearTimeout(saveT);
    saveT=setTimeout(save3d,300);
  }"""
NEW = """  /* ================= __acad3dV99: regenerate regions whose plane changed ================= */
  var A3D_REGEN_BUSY=false;
  function bimRegenerateRegions(){
    if(A3D_REGEN_BUSY||!A3D.objs||!A3D.objs.length)return 0;
    A3D_REGEN_BUSY=true;
    var changed=[],ctx=null,i,o,sid,planes={},key,want,y,edges,sig,b,ip,cut=0,adopted=0;
    try{
      for(i=0;i<A3D.objs.length;i++){
        o=A3D.objs[i];
        /* a single source that no longer exists */
        sid=bimGraphRoomSourceId(o);
        if(sid&&!bimIsRegionDep(o)&&!objById(sid)){
          if(bimCutSource(o,'its source was deleted'))cut++;
          continue;
        }
        /* an older build's multi-wall room: adopt it without changing its shape */
        if(o.t==='room'&&!bimIsRegionDep(o)&&o.sourceType==='wallgroup'&&o.pts&&o.pts.length>=3){
          var q0=bimObjOffset(o),cur=o.pts.map(function(p){return [p[0]+q0[0],p[1]+q0[2]];});
          ip=bimInteriorPoint(cur);
          if(ip){
            var yw=(o.y||0)+q0[1],tr=bimRegionTraceAt(ip,yw,BIM_REGION_WANT.walls);
            o.region={seed:[ip[0]-q0[0],ip[1]-q0[2]],y:o.y||0,want:'walls',
                      members:tr.error?[]:tr.srcIds.slice(),sig:tr.sig||'',open:false};
            adopted++;
          }
          continue;
        }
        if(!bimIsRegionDep(o))continue;
        want=(o.region.want==='walls')?'walls':'all';
        y=bimRegionPlaneY(o);
        key=want+'@'+y.toFixed(4);
        if(!planes[key]){
          edges=bimBoundaryEdges(y,BIM_REGION_WANT[want]);
          planes[key]=bimEdgesSig(edges);
        }
        sig=planes[key];
        if(o.region.sig===sig)continue;
        if(!ctx)ctx={reason:'rebuild',delta:null,recut:0,failed:0,recutWalls:{},wallsRebaked:{},
                     roomsUpdated:0,roomsFailed:0,clonesUpdated:0,clonesFailed:0,openingsShifted:0};
        if(o.t==='room')b=bimRemeasureRoomFromSource(o,ctx);
        else b=bimFollowSource(o,ctx);
        /* whatever happened, this plane state has now been seen */
        if(bimIsRegionDep(o))o.region.sig=sig;
        changed.push(bimGraphObjKey(o.id));
      }
      if(changed.length)bimGraphPropagate(changed,bimGraphVisit,ctx);
    }catch(eRG){
      console.warn('[BIM] Region regeneration failed; regions keep their last shapes.',eRG);
      a3dToast('Some rooms or hatches could not be updated - see the console');
    }
    A3D_REGEN_BUSY=false;
    if(changed.length||cut){
      A3D.meshes={};
      try{refreshTree();paint();}catch(eRP){console.warn('[BIM] Repaint after region update failed',eRP);}
    }
    return changed.length+cut+adopted;
  }
  function saveSoon(){
    /* __acad3dV99: every model mutation passes through here, so this is where a change to
       WHICH shapes bound a region is noticed. */
    bimRegenerateRegions();
    if(saveT)clearTimeout(saveT);
    saveT=setTimeout(save3d,300);
  }"""
assert txt.count(OLD) == 1
txt = txt.replace(OLD, NEW, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
