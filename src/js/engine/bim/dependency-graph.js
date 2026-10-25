  // ---- __acad3dV50: Parametric dependency graph ------------------------------------------
  // Every parametric relationship in this model used to propagate through hand-written code at
  // the point of edit: updateLevel() walked the object list to shift a level's contents, a wall
  // type edit rewrote each instance in place, and delSelection() removed a wall's openings. That
  // works while each relationship is a single hop triggered from a single place, but it does not
  // compose. An edit that should cascade -- move a wall, its openings follow, the room it bounds
  // re-measures, the room schedule changes -- had no path to do so. That is why room boundaries
  // were documented in the Properties palette as frozen snapshots, why Align and arrow-key nudge
  // left a wall's doors behind, and why linked clones only updated when the user pressed a button.
  //
  // This makes the relationships an explicit directed graph, so one change can be propagated in
  // dependency order, exactly once per element, with circular references detected and reported
  // rather than hanging the browser.
  //
  // Edge direction is "depended-on -> depends-on-it": an edge A->B means B must be recomputed
  // after A changes.
  //
  // DELIBERATE DESIGN CHOICE: edges are DERIVED from the live model every time, never stored
  // beside it. A persisted second copy of the relationships would be a second source of truth
  // free to desync from A3D.objs, and would have to be migrated into every project file already
  // saved. Rebuilding is a single O(n) pass over the object list, which is negligible next to one
  // geometry rebuild.
  var BIM_GRAPH_REL_LABELS={
    level:{fwd:'Level',rev:'Hosted on this level'},
    type:{fwd:'Type',rev:'Instance of this type'},
    host:{fwd:'Host wall',rev:'Opening in this wall'},
    source:{fwd:'Source shape',rev:'Room bounded by this'},
    region:{fwd:'Bounded by',rev:'Bounds this region'},   /* __acad3dV99 */
    tag:{fwd:'Tags',rev:'Tagged by'},                    /* __acad3dV101 */
    support:{fwd:'Sits under',rev:'Footing'},            /* __acad3dV102 */
    link:{fwd:'Link source',rev:'Linked clone'},
    targetLevel:{fwd:'Connects to level',rev:'Stair reaching this level'}
  };
  function bimGraphObjKey(id){return 'obj:'+id;}
  function bimGraphLevelKey(id){return 'lvl:'+id;}
  function bimGraphTypeKey(cat,id){return 'type:'+cat+':'+id;}
  /* Rooms created by bimCreateRoom carry sourceType/sourceId at the top level, while rooms that
     come back through the mirror/duplicate path carry them under .bim. Read both rather than
     assuming one, so a mirrored room is not silently treated as having no source. */
  /* __acad3dV97: the source of ANY boundary-derived object, not only a room's. Rooms, floors,
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
    if(o&&bimIsRegionDep(o)){   /* __acad3dV99: a region is detached from ALL of its members */
      var nm=(o.region.members||[]).length;
      delete o.region;
      o.sourceId=null;o.sourceType=null;
      if(o.bim){o.bim.sourceId=null;o.bim.sourceType=null;}
      a3dToast(o.name+' is no longer linked to the '+nm+' shape'+(nm===1?'':'s')+' that bounded it'+
        (why?(' ('+why+')'):'')+' - it keeps its current shape');
      return true;
    }
    if(!o||!bimGraphRoomSourceId(o))return false;
    var srcName=(objById(bimGraphRoomSourceId(o))||{}).name||'its source';
    o.sourceId=null;o.sourceType=null;
    if(o.bim){o.bim.sourceId=null;o.bim.sourceType=null;}
    a3dToast(o.name+' is no longer linked to '+srcName+(why?(' ('+why+')'):'')+
      ' - it keeps its current shape');
    return true;
  }
  function bimGraphTypeCatOf(o){
    if(!o||!o.bim)return null;
    return o.bim.typeCat||o.bim.type||null;
  }
  function bimGraphBuild(){
    try{
      var nodes={},out={},inn={},i,cat,edges=0;
      function ensure(key,kind,id,obj){
        if(!nodes[key]){nodes[key]={key:key,kind:kind,id:id,obj:obj||null};out[key]=[];inn[key]=[];}
        else if(obj&&!nodes[key].obj)nodes[key].obj=obj;
        return nodes[key];
      }
      function link(a,b,rel){
        if(a===b)return;                        // a self-edge is never meaningful here
        if(!nodes[a]||!nodes[b])return;         // dangling reference: skip, do not invent a node
        var list=out[a],j;
        for(j=0;j<list.length;j++)if(list[j].to===b&&list[j].rel===rel)return;   // de-dupe
        out[a].push({to:b,rel:rel});
        inn[b].push({from:a,rel:rel});
        edges++;
      }
      for(i=0;i<A3D.levels.length;i++)ensure(bimGraphLevelKey(A3D.levels[i].id),'level',A3D.levels[i].id,null);
      var types=A3D.types||{};
      for(cat in types){
        if(!types.hasOwnProperty(cat)||!Array.isArray(types[cat]))continue;
        for(i=0;i<types[cat].length;i++)ensure(bimGraphTypeKey(cat,types[cat][i].id),'type',types[cat][i].id,null);
      }
      for(i=0;i<A3D.objs.length;i++)ensure(bimGraphObjKey(A3D.objs[i].id),'object',A3D.objs[i].id,A3D.objs[i]);
      for(i=0;i<A3D.objs.length;i++){
        var o=A3D.objs[i],key=bimGraphObjKey(o.id);
        var lvl=bimObjectLevelId(o);
        if(lvl)link(bimGraphLevelKey(lvl),key,'level');
        var tcat=bimGraphTypeCatOf(o);
        if(tcat&&o.bim&&o.bim.typeId)link(bimGraphTypeKey(tcat,o.bim.typeId),key,'type');
        if(o.t==='opening'&&o.bim&&o.bim.hostWallId)link(bimGraphObjKey(o.bim.hostWallId),key,'host');
        var srcId=bimGraphRoomSourceId(o);
        /* __acad3dV97: any object that records a source depends on it. This was room-only,
           so a roof that stored its source was never linked to it. */
        if(srcId&&srcId!==o.id)link(bimGraphObjKey(srcId),key,'source');
        /* __acad3dV99: a region depends on every shape its last trace walked */
        if(bimIsRegionDep(o)&&o.region.members){
          var rm;
          for(rm=0;rm<o.region.members.length;rm++)
            if(o.region.members[rm]!==o.id)link(bimGraphObjKey(o.region.members[rm]),key,'region');
        }
        if(o.linkSourceId)link(bimGraphObjKey(o.linkSourceId),key,'link');
        if(o.t==='roomtag'&&o.roomId)link(bimGraphObjKey(o.roomId),key,'tag');   /* __acad3dV101 */
        if(bimIsFooting(o)&&o.bim.hostId)link(bimGraphObjKey(o.bim.hostId),key,'support');   /* __acad3dV102 */
        if(o.bim&&o.bim.targetLevelId)link(bimGraphLevelKey(o.bim.targetLevelId),key,'targetLevel');
      }
      return {nodes:nodes,out:out,in:inn,edgeCount:edges};
    }catch(eG){
      console.warn('[BIM] Dependency graph build failed; callers fall back to direct edits.',eG);
      return null;
    }
  }
  /* Every node reachable downstream of the given start keys, INCLUDING the start keys themselves.
     The visited guard means a circular reference terminates here rather than recursing forever;
     the cycle is reported later, by the topological pass, where it can be named. */
  function bimGraphDownstream(g,startKeys){
    var seen={},stack=startKeys.slice(),k,i,neigh;
    while(stack.length){
      k=stack.pop();
      if(seen[k])continue;
      if(!g.nodes[k])continue;
      seen[k]=true;
      neigh=g.out[k]||[];
      for(i=0;i<neigh.length;i++)if(!seen[neigh[i].to])stack.push(neigh[i].to);
    }
    return seen;
  }
  /* Kahn's algorithm restricted to the dirty subset. Anything still holding an in-edge when the
     queue drains is part of a cycle and is returned separately instead of being dropped. */
  function bimGraphTopoOrder(g,dirty){
    var indeg={},k,i,queue=[],order=[],cycle=[];
    for(k in dirty){if(dirty.hasOwnProperty(k))indeg[k]=0;}
    for(k in dirty){
      if(!dirty.hasOwnProperty(k))continue;
      var ins=g.in[k]||[];
      for(i=0;i<ins.length;i++)if(dirty[ins[i].from])indeg[k]++;
    }
    for(k in indeg){if(indeg.hasOwnProperty(k)&&indeg[k]===0)queue.push(k);}
    while(queue.length){
      var cur=queue.shift();
      order.push(cur);
      var outs=g.out[cur]||[];
      for(i=0;i<outs.length;i++){
        var nx=outs[i].to;
        if(!dirty[nx])continue;
        indeg[nx]--;
        if(indeg[nx]===0)queue.push(nx);
      }
    }
    for(k in indeg){if(indeg.hasOwnProperty(k)&&indeg[k]>0)cycle.push(k);}
    return {order:order,cycle:cycle};
  }
  /* Walks everything downstream of startKeys in dependency order, calling visit(node,graph,ctx)
     once per node. The start nodes are skipped -- whoever called this has already applied the
     change that made them dirty. Later phases supply the visitor that actually recomputes
     geometry; this phase ships the traversal itself, verified on its own. */
  function bimGraphPropagate(startKeys,visit,ctx){
    var g=bimGraphBuild();
    if(!g)return {ok:false,visited:0,order:[],cycle:[],reason:'graph unavailable'};
    var starts={},i;
    for(i=0;i<startKeys.length;i++)starts[startKeys[i]]=true;
    var dirty=bimGraphDownstream(g,startKeys);
    var res=bimGraphTopoOrder(g,dirty);
    var order=res.order.slice();
    if(res.cycle.length){
      console.warn('[BIM] Circular dependency detected between: '+res.cycle.join(', ')+
        '. Those elements were updated once each, in model order, rather than in dependency order.');
      a3dToast('Circular dependency: '+res.cycle.length+' element(s) updated in model order');
      order=order.concat(res.cycle);
    }
    var visited=0,failed=0;
    for(i=0;i<order.length;i++){
      if(starts[order[i]])continue;
      var node=g.nodes[order[i]];
      if(!node)continue;
      if(typeof visit==='function'){
        try{visit(node,g,ctx);visited++;}
        catch(eV){
          failed++;
          console.warn('[BIM] Dependency update failed for '+order[i]+'; remaining elements still processed.',eV);
        }
      }else visited++;
    }
    if(failed)a3dToast(failed+' dependent element(s) could not be updated - see console');
    return {ok:true,visited:visited,failed:failed,order:order,cycle:res.cycle,edgeCount:g.edgeCount};
  }
  /* Relationship read-outs for the Properties palette: what this element depends on, and what
     depends on it. Names are resolved here so the panel stays presentation-only. */
  function bimGraphNodeLabel(g,key){
    var n=g.nodes[key];
    if(!n)return key;
    if(n.kind==='level')return bimLevelName(n.id)||'Level';
    if(n.kind==='object')return (n.obj&&n.obj.name)||'Element';
    if(n.kind==='type'){
      var parts=key.split(':'),t=bimFindType(parts[1],parts[2]);
      return (t&&t.name)||'Type';
    }
    return key;
  }
  function bimGraphRelationsOf(objId){
    var g=bimGraphBuild();
    if(!g)return null;
    var key=bimGraphObjKey(objId);
    if(!g.nodes[key])return {depends:[],dependents:[]};
    var depends=[],dependents=[],i,e;
    var ins=g.in[key]||[],outs=g.out[key]||[];
    for(i=0;i<ins.length;i++){
      e=ins[i];
      depends.push({key:e.from,rel:e.rel,label:(BIM_GRAPH_REL_LABELS[e.rel]||{}).fwd||e.rel,
        name:bimGraphNodeLabel(g,e.from),kind:g.nodes[e.from]?g.nodes[e.from].kind:'',
        objId:g.nodes[e.from]&&g.nodes[e.from].kind==='object'?g.nodes[e.from].id:null});
    }
    for(i=0;i<outs.length;i++){
      e=outs[i];
      dependents.push({key:e.to,rel:e.rel,label:(BIM_GRAPH_REL_LABELS[e.rel]||{}).rev||e.rel,
        name:bimGraphNodeLabel(g,e.to),kind:g.nodes[e.to]?g.nodes[e.to].kind:'',
        objId:g.nodes[e.to]&&g.nodes[e.to].kind==='object'?g.nodes[e.to].id:null});
    }
    return {depends:depends,dependents:dependents};
  }
  // ---- __acad3dV51: dependency visitors -- the graph does real work -------------------------
  // Phase 55a shipped the traversal with no visitor. This is the first one, and it closes a
  // silent geometry-loss bug that existed in FOUR separate places.
  //
  // An opening is not a solid: bimBuildWallOpening CSG-subtracts a box from the HOST WALL's mesh
  // and leaves behind only a marker object recording where the hole is (center, dir, width,
  // height, sillHeight). That means the hole lives in the wall's mesh, and any code path that
  // rebuilds that mesh from the centerline destroys every hole in it. Four paths did exactly
  // that -- bimRebuildWall (Properties palette thickness/height/alignment), bimRebuildInstanceForType
  // and bimApplyWallTypeToInstances (type parameter edits), and bimSetWallTypeOf (assigning a type)
  // -- none of them re-cut the openings. The doors and windows stayed in the model tree and in the
  // door/window schedules while their holes vanished from the geometry, so the drawing and the
  // schedule disagreed with each other and nothing reported it.
  //
  // WHY THE REASON FLAG MATTERS: an opening must be re-cut when its host wall's mesh was REBUILT,
  // and must NOT be when the wall was merely translated. bimShiftLevelContents moves a wall by
  // shifting its vertices, and the hole moves with them; re-cutting there would subtract the same
  // box out of an already-empty region and risk degenerate geometry. So callers state why they are
  // propagating and the visitor decides, rather than guessing from the model.
  /* How far an opening's re-cut position may differ from where the user authored it before the
     re-cut is refused, in metres. bimFindWallSegmentAt returns the NEAREST segment with no
     distance limit of its own and clamps the along-segment parameter into [0.08, 0.92], so
     without this check an opening whose recorded centre no longer lies on its host wall would be
     silently relocated to the closest place that does fit. A door quietly sliding along a wall,
     or jumping to a different segment, is a worse failure than an opening that reports it could
     not be placed: the second is visible and undoable, the first is not. The centreline is
     unchanged by a thickness, height or alignment rebuild, so a legitimate re-cut reproduces the
     original centre to floating-point noise -- 0.1 mm is far below any meaningful building
     dimension while still catching real drift. */
  var BIM_OPENING_REPLACE_TOL=1e-4;
  /* __acad3dV62: rewritten onto bimCutOpeningsIntoWall. This used to loop the wall's openings and
     re-cut them one at a time, each subtraction taking the previous one's output as its input --
     the same re-feed that corrupted the solid on the second opening in the "cut a new opening"
     path (see bimCutOpeningsIntoWall for the measured failure). A wall with two openings that
     went through a thickness edit, a Join, a Merge, a type change or a level shift therefore came
     back wrong for exactly the same reason. All of its openings are now cut out of a regenerated
     base in one boolean, so the count of openings a wall carries no longer affects correctness.
     The per-opening fail-safe rules are unchanged in substance -- an opening with no recorded
     position, with no hosting segment, or that has drifted further than BIM_OPENING_REPLACE_TOL
     from where it was authored is skipped, counted, and explained in the console, with its marker
     kept so undo restores a consistent state -- they simply live in the shared function now. */
  function bimReapplyOpeningsToWall(wall,ctx){
    if(!wall||!wall.bim||wall.bim.type!=='wall')return 0;
    var specs=bimOpeningSpecsFor(wall),i;
    if(!specs.length)return 0;
    var res=bimCutOpeningsIntoWall(wall,specs);
    if(res.error){
      console.warn('[BIM] Could not re-cut the opening'+(specs.length===1?'':'s')+' of '+wall.name+': '+res.error+
        ' (the opening markers are kept, so undo restores a consistent state).');
      if(ctx)ctx.failed+=specs.length;
      return 0;
    }
    for(i=0;i<res.skipped.length;i++){
      var sk=res.skipped[i];
      console.warn('[BIM] '+((sk.spec&&sk.spec.op&&sk.spec.op.name)||'An opening')+' could not be re-cut into '+
        wall.name+': '+sk.reason+'; the marker is kept so undo restores a consistent state.');
      if(ctx)ctx.failed++;
    }
    wall.mesh=res.mesh;
    for(i=0;i<res.cut.length;i++){
      var c=res.cut[i];
      if(c.spec&&c.spec.op){c.spec.op.bim.center=c.center;c.spec.op.bim.dir=c.dir;}
      if(ctx)ctx.recut++;
    }
    return res.cut.length;
  }
  /* The visitor handed to bimGraphPropagate. Dispatches on what the dirty node actually is, so
     later phases add cases here rather than adding parallel traversals. */
  /* __acad3dV52: rooms re-measure live from their source. Mirrors bimReapplyOpeningsToWall's
     fail-safe shape: if the source is missing, no longer the right type, no longer closed, or
     would produce degenerate (near-zero-area) geometry, the room is left COMPLETELY unchanged
     and the failure is counted/reported -- never a corrupted boundary.
     __acad3dV99: a room traced from SEVERAL shapes is no longer a frozen snapshot. It is a
     region dependent (o.region), linked in the graph to every shape its trace walked, and
     re-traced from its seed through bimRegionBoundaryWorld -- see the V99 block below. */
