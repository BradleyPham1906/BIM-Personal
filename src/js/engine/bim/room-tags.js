  /* ================= __acad3dV101: room tags ================= */
  /* A room's own label, for every place that writes one (plan exports). LOCAL coordinates, like
     the room's points, so an exporter treats it exactly as it treats them. */
  function bimRoomLabelText(o){return (o.number?o.number+' ':'')+o.name+' '+(o.area||0).toFixed(2)+'m2';}
  function bimRoomLabelPoint(o){
    var ip=bimInteriorPoint(o.pts);
    if(ip)return ip;
    var cx=0,cz=0,i;
    for(i=0;i<o.pts.length;i++){cx+=o.pts[i][0];cz+=o.pts[i][1];}
    return [cx/o.pts.length,cz/o.pts.length];
  }
  function bimRoomTagText(o){
    var r=objById(o.roomId);
    if(!r)return '';
    return (r.number?r.number+' ':'')+r.name;
  }
  /* Tagged in the view being looked at: a tag that is drawn here. */
  function bimRoomTagged(roomId){
    var i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t==='roomtag'&&o.roomId===roomId&&bimAnnotDrawable(o))return true;
    }
    return false;
  }
  /* The ONE layout of a tag, in screen pixels -- drawn from, and picked from. */
  function bimRoomTagLayout(o,V,W,H){
    var r=objById(o.roomId);
    if(!r)return null;
    var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
    var sp=toScreen([o.pt[0]+ox,(o.y||0)+oy,o.pt[1]+oz],V,W,H);
    var lines=[{t:r.number||'-',font:'bold 13px system-ui,sans-serif',col:'#ffffff'},
               {t:r.name||'',font:'11px system-ui,sans-serif',col:'#dfe4ea'}];
    if(o.showArea!==false)lines.push({t:(r.area||0).toFixed(2)+' m\u00b2',font:'10px system-ui,sans-serif',col:'#9ec1ff'});
    var w=0,i;
    for(i=0;i<lines.length;i++)w=Math.max(w,bimMeasureLabel(lines[i].t,lines[i].font));
    w+=14;
    var lh=14,h=lines.length*lh+6;
    var x0=sp[0]-w/2,y0=sp[1]-h/2;
    for(i=0;i<lines.length;i++)lines[i].y=y0+3+lh*i+lh/2;
    return {box:[x0,y0,x0+w,y0+h],lines:lines,cx:sp[0],room:r};
  }
  function drawRoomTags(ctx,V,W,H){
    if(A3D.section)return;
    var i,o,L,j,sel;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='roomtag'||!bimAnnotDrawable(o))continue;
      L=bimRoomTagLayout(o,V,W,H);
      if(!L)continue;
      sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      ctx.fillStyle='rgba(20,22,26,0.88)';
      ctx.fillRect(L.box[0],L.box[1],L.box[2]-L.box[0],L.box[3]-L.box[1]);
      ctx.strokeStyle=sel?'#4ea1ff':'#7fd4c4';ctx.lineWidth=sel?1.6:1;
      ctx.strokeRect(L.box[0]+0.5,L.box[1]+0.5,L.box[2]-L.box[0]-1,L.box[3]-L.box[1]-1);
      ctx.textAlign='center';ctx.textBaseline='middle';
      for(j=0;j<L.lines.length;j++){
        ctx.font=L.lines[j].font;ctx.fillStyle=sel?'#9ec1ff':L.lines[j].col;
        ctx.fillText(L.lines[j].t,L.cx,L.lines[j].y);
      }
      ctx.restore();
    }
  }
  /* Visible rooms on the active level containing a WORLD plan point, smallest first. */
  function bimRoomsAt(pt){
    var out=[],i,o,q,ring;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room'||!o.pts||o.pts.length<3)continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(bimObjectLevelId(o)&&bimObjectLevelId(o)!==A3D.activeLevel)continue;
      q=bimObjOffset(o);
      ring=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
      if(bimPointInPoly(pt,ring))out.push(o);
    }
    out.sort(function(a,b){return a.area-b.area;});
    return out;
  }
  function bimNewRoomTag(room,pt){
    A3D.counts.roomtag=(A3D.counts.roomtag||0)+1;
    var q=bimObjOffset(room);
    return {id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'roomtag',name:'Room Tag_'+A3D.counts.roomtag,
      col:'#7fd4c4',pos:[0,0,0],roomId:room.id,pt:[pt[0],pt[1]],y:(room.y||0)+q[1],
      levelId:bimObjectLevelId(room)||A3D.activeLevel,layer:A3D.activeLayer,viewId:A3D.activeViewId,showArea:true};
  }
  /* Tag the room under a WORLD point, the tag placed at that point. */
  function bimTagRoomAt(pt){
    var rs=bimRoomsAt(pt);
    if(!rs.length){a3dToast('Tag Room: there is no room here');return null;}
    var room=rs[0],had=bimRoomTagged(room.id);
    pushUndo();
    var t=bimNewRoomTag(room,pt);
    A3D.objs.push(t);
    refreshTree();paint();saveSoon();
    a3dToast('Tagged '+bimRoomTagText(t)+(had?' (it already had a tag in this view)':''));
    return t;
  }
  /* Revit's Tag All Not Tagged: every room on the active level without a tag in this view,
     tagged at a point inside it. One undo step for the lot. */
  function bimTagAllRooms(){
    var todo=[],i,o,seen=0;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room'||!o.pts||o.pts.length<3)continue;
      if(bimObjectLevelId(o)&&bimObjectLevelId(o)!==A3D.activeLevel)continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      seen++;
      if(!bimRoomTagged(o.id))todo.push(o);
    }
    if(!seen){a3dToast('There are no rooms on '+bimGetActiveLevel().name+' to tag');return [];}
    if(!todo.length){a3dToast('Every room on '+bimGetActiveLevel().name+' is already tagged in this view');return [];}
    pushUndo();
    var made=[];
    for(i=0;i<todo.length;i++){
      var q=bimObjOffset(todo[i]);
      var ip=bimInteriorPoint(todo[i].pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];}));
      if(!ip){console.warn('[BIM] No point inside '+todo[i].name+' to put its tag');continue;}
      var t=bimNewRoomTag(todo[i],ip);
      A3D.objs.push(t);made.push(t.id);
    }
    refreshTree();paint();saveSoon();
    a3dToast('Tagged '+made.length+' room'+(made.length===1?'':'s')+
      (made.length<todo.length?' ('+(todo.length-made.length)+' could not be placed - see console)':''));
    return made;
  }
  /* A tag whose room has gone some other way than Delete (undo of a room, a purge, an import)
     would draw nothing and stay selectable in the browser. Removed, and said. */
  function bimSweepOrphanTags(){
    var keep=[],gone=0,i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t==='roomtag'&&!objById(o.roomId)){gone++;if(A3D.sel===o.id)A3D.sel=null;continue;}
      keep.push(o);
    }
    if(!gone)return 0;
    A3D.objs=keep;
    if(A3D.selSet)A3D.selSet=A3D.selSet.filter(function(id){return !!objById(id);});
    a3dToast(gone+' room tag'+(gone===1?'':'s')+' removed - the room was deleted');
    return gone;
  }
  function startRoomTagTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'roomtag',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();paint();
    a3dToast('Tag Room: click inside a room to tag it; Escape when finished');
  }
  function startRoomTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'room',pts:[],y:lvl.elev,on:null};
    a3dToast('Room: click inside an enclosed wall loop or closed sketch on '+lvl.name);
    paint();
  }
