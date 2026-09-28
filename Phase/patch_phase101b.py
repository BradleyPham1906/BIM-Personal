"""patch_phase101b.py -- __acad3dV101: the room tag.

A tag is an ANNOTATION that points at a room and shows the room's number, name and area. It
stores where it sits and which room it tags -- nothing else. Every word it shows is read from the
room when it is drawn, so renumbering or renaming a room changes every one of its tags, and a tag
cannot say something its room does not.

It is a first-class annotation from V98 on: picked where it is drawn (before the model), a grip
to move it, dragged by its body, view-scoped like a dimension. One layout function,
bimRoomTagLayout, is used by both the painter and the picker, so the box you click is the box
you see.

Relationships (law 7): the graph links room -> tag ('tag'). A tag follows its room when the room
is MOVED (it keeps its offset, as Revit's does); deleting a room deletes its tags, the way
deleting a wall deletes its openings; and any tag whose room has gone some other way is swept
at saveSoon and the removal is said. While a room is tagged in the current view, the room's own
plan label steps aside, so the drawing does not say the same thing twice.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = 'f8353abb4940a99e312f22f105739e728b6f99779f97b15380d251d8a98a21ed'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

TAGFNS = """  /* ================= __acad3dV101: room tags ================= */
  function bimIsRoomTag(o){return !!(o&&o.t==='roomtag'&&o.pt&&o.roomId);}
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
    if(o.showArea!==false)lines.push({t:(r.area||0).toFixed(2)+' m2',font:'10px system-ui,sans-serif',col:'#9ec1ff'});
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
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
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
    var todo=[],i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room'||!o.pts||o.pts.length<3)continue;
      if(bimObjectLevelId(o)&&bimObjectLevelId(o)!==A3D.activeLevel)continue;
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(!bimRoomTagged(o.id))todo.push(o);
    }
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
"""

EDITS = [
    ("""  function startRoomTool(){
    closeDlg();""", TAGFNS + """  function startRoomTool(){
    closeDlg();"""),
    # draw
    ("""    drawTextLabels(ctx,V,W,H);""",
     """    drawTextLabels(ctx,V,W,H);
    drawRoomTags(ctx,V,W,H);       /* __acad3dV101 */"""),
    # annotation machinery
    ("""    if(!o||(o.t!=='dim'&&o.t!=='text'))return false;""",
     """    if(!o||(o.t!=='dim'&&o.t!=='text'&&o.t!=='roomtag'))return false;
    if(o.t==='roomtag'&&!objById(o.roomId))return false;   /* __acad3dV101 */"""),
    ("""    function seg(a,b,tol){segs.push([a[0],a[1],b[0],b[1],tol]);}
    if(o.t==='text'){""",
     """    function seg(a,b,tol){segs.push([a[0],a[1],b[0],b[1],tol]);}
    if(o.t==='roomtag'){   /* __acad3dV101: the drawn box, from the one layout */
      var TL=bimRoomTagLayout(o,V,W,H);
      if(TL)boxes.push(TL.box);
      return {segs:segs,boxes:boxes};
    }
    if(o.t==='text'){"""),
    ("""  function bimPickAnnotation(x,y){return bimPickText(x,y)||bimPickDim(x,y);}""",
     """  function bimPickAnnotation(x,y){
    /* __acad3dV101: tags are drawn after text, so they are tested first */
    return bimPickAnnotOfType(x,y,'roomtag')||bimPickText(x,y)||bimPickDim(x,y);
  }"""),
    ("""    if(o.t==='text')return o.pt?[o.pt]:null;""",
     """    if(o.t==='text'||o.t==='roomtag')return o.pt?[o.pt]:null;   /* __acad3dV101 */"""),
    ("""      if(o.t==='text'){
        if(idx!==0)return false;
        o.pt=p;return true;
      }
      if(o.t!=='dim')return false;""",
     """      if(o.t==='text'||o.t==='roomtag'){   /* __acad3dV101 */
        if(idx!==0)return false;
        o.pt=p;return true;
      }
      if(o.t!=='dim')return false;"""),
    # the room's own label steps aside when tagged
    ("""      /* __acad3dV101: at a point INSIDE the room -- the vertex average lies outside an L */""",
     """      if(bimRoomTagged(o.id)){ctx.restore();continue;}   /* __acad3dV101: the tag says it */
      /* __acad3dV101: at a point INSIDE the room -- the vertex average lies outside an L */"""),
    # graph
    ("""    region:{fwd:'Bounded by',rev:'Bounds this region'},   /* __acad3dV99 */""",
     """    region:{fwd:'Bounded by',rev:'Bounds this region'},   /* __acad3dV99 */
    tag:{fwd:'Tags',rev:'Tagged by'},                    /* __acad3dV101 */"""),
    ("""        if(o.linkSourceId)link(bimGraphObjKey(o.linkSourceId),key,'link');""",
     """        if(o.linkSourceId)link(bimGraphObjKey(o.linkSourceId),key,'link');
        if(o.t==='roomtag'&&o.roomId)link(bimGraphObjKey(o.roomId),key,'tag');   /* __acad3dV101 */"""),
    ("""  function bimGraphVisit(node,g,ctx){
    var o=node.obj;
    if(!o)return;""",
     """  function bimGraphVisit(node,g,ctx){
    var o=node.obj;
    if(!o)return;
    /* __acad3dV101: a tag keeps its offset from a room that was MOVED -- only then. A room that
       re-traced because a wall moved has not been moved, and its tag stays put. */
    if(o.t==='roomtag'){
      if(ctx&&ctx.reason==='transform'&&ctx.delta&&ctx.movedIds&&
         ctx.movedIds.indexOf(o.roomId)>=0&&ctx.movedIds.indexOf(o.id)<0){
        if(!o.pos)o.pos=[0,0,0];
        o.pos[0]+=ctx.delta[0];o.pos[2]+=ctx.delta[2];
      }
      return;
    }"""),
    ("""    var keys=[],i,regionOrigins=[];   /* __acad3dV99 */""",
     """    var keys=[],i,regionOrigins=[];   /* __acad3dV99 */
    ctx.movedIds=objIds.slice();      /* __acad3dV101 */"""),
    # delete with the room; sweep the rest
    ("""      if(oo.t==='opening'&&oo.bim&&idSet[oo.bim.hostWallId])idSet[oo.id]=true;""",
     """      if(oo.t==='opening'&&oo.bim&&idSet[oo.bim.hostWallId])idSet[oo.id]=true;
      if(oo.t==='roomtag'&&idSet[oo.roomId])idSet[oo.id]=true;   /* __acad3dV101 */"""),
    ("""    bimRegenerateRegions();
    if(saveT)clearTimeout(saveT);""",
     """    bimSweepOrphanTags();   /* __acad3dV101 */
    bimRegenerateRegions();
    if(saveT)clearTimeout(saveT);"""),
    # properties and names
    ("""    if(o.t==='room')return 'Rooms : Room';""",
     """    if(o.t==='room')return 'Rooms : Room';
    if(o.t==='roomtag')return 'Room Tags : Room Tag';   /* __acad3dV101 */"""),
    ("""    var finRows='';   /* __acad3dV101: the room's own data, from the one field list */
    if(o.t==='room'){""",
     """    var finRows='';   /* __acad3dV101: the room's own data, from the one field list */
    if(o.t==='roomtag'){
      var tRoom=objById(o.roomId);
      if(tRoom){
        idd+=bimPropText('Tags',tRoom.name);
        idd+=bimPropRow('Room Number','<input type="text" data-roomf="number" value="'+bimEsc(bimRoomField(tRoom,'number'))+'">');
        idd+=bimPropRow('Room Name','<input type="text" data-roomf="name" value="'+bimEsc(tRoom.name||'')+'">');
      }
      idd+=bimPropRow('Show Area','<input type="checkbox" data-tagf="showArea"'+(o.showArea!==false?' checked':'')+'>');
    }
    if(o.t==='room'){"""),
    # a tag edits its room; 'name' is allowed through the tag
    ("""    for(i=0;i<BIM_ROOM_FIELDS.length;i++)if(BIM_ROOM_FIELDS[i].k===k)f=BIM_ROOM_FIELDS[i];""",
     """    for(i=0;i<BIM_ROOM_FIELDS.length;i++)if(BIM_ROOM_FIELDS[i].k===k)f=BIM_ROOM_FIELDS[i];
    if(k==='name')f={k:'name',label:'Name'};   /* a tag renames its room */"""),
    ("""    if(bimRoomField(room,k)===val)return true;""",
     """    if(k==='name'&&!val){a3dToast('A room needs a name');return false;}
    if(bimRoomField(room,k)===val)return true;"""),
    ("""    /* __acad3dV101: room fields. A field shown on a TAG edits the tag's room. */""",
     """    /* __acad3dV101: a tag's own switch */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var ti=ev.target&&ev.target.closest?ev.target.closest('[data-tagf]'):null;
      if(!ti)return;
      var tg=objById(A3D.sel);
      if(!tg||tg.t!=='roomtag')return;
      pushUndo();
      tg.showArea=!!ti.checked;
      paint();saveSoon();
    });
    /* __acad3dV101: room fields. A field shown on a TAG edits the tag's room. */"""),
    # bounds (align, zoom-to)
    ("""    else if(o.t==='text')pts=[o.pt];""",
     """    else if(o.t==='text'||o.t==='roomtag')pts=[o.pt];   /* __acad3dV101 */"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
