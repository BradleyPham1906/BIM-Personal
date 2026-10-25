  /* ================= __acad3dV105: room colour fill =================
     Off by default, so a drawing made before this phase looks exactly as it did. When on, each
     room is filled by the value of ONE of its fields, Department or Occupancy. Colours go to the
     values the whole project has, in name order, so a department is one colour on every level.
     The legend lists what the last paint drew, recorded by the pass that drew it, so it cannot
     disagree with the plan. Past twelve values the colours repeat, and the legend shows it. */
  var BIM_SCHEME_COLS=['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#d9d9d9','#bc80bd','#ccebc5','#ffed6f'];
  var BIM_SCHEME_ALPHA=0.5;   /* the canvas only: the technical plan draws rooms over the model */
  function bimRoomSchemeLabel(by){return by==='dept'?'Department':(by==='occupancy'?'Occupancy':'');}
  function bimRoomSchemeValue(o,by){
    if(!o||o.t!=='room'||(by!=='dept'&&by!=='occupancy'))return '';
    return String(o[by]==null?'':o[by]).replace(/\s+/g,' ').replace(/^ | $/g,'');
  }
  function bimRoomSchemeValues(by){
    var seen={},out=[],i,v;
    for(i=0;i<A3D.objs.length;i++){
      v=bimRoomSchemeValue(A3D.objs[i],by);
      if(v&&!seen['k'+v.toLowerCase()]){seen['k'+v.toLowerCase()]=1;out.push(v);}
    }
    out.sort(function(a,b){a=a.toLowerCase();b=b.toLowerCase();return a<b?-1:(a>b?1:0);});
    return out;
  }
  function bimRoomSchemeMap(by){
    var vals=bimRoomSchemeValues(by),m={},i;
    for(i=0;i<vals.length;i++)m['k'+vals[i].toLowerCase()]={name:vals[i],col:BIM_SCHEME_COLS[i%BIM_SCHEME_COLS.length]};
    return m;
  }
  function bimRoomSchemeEntry(o,map){
    var v=bimRoomSchemeValue(o,A3D.roomScheme);
    if(!v)return null;
    return (map||bimRoomSchemeMap(A3D.roomScheme))['k'+v.toLowerCase()]||null;
  }
  /* The vector sinks: the same colour, opaque, because both draw room fills under the model. */
  function bimRoomSchemeGraphics(o,rg,pres){
    var e=bimRoomSchemeEntry(o,null),g;
    if(!e)return rg;
    g=bimResolveGraphics(o,pres?'presentation':'technical');
    g.fill=e.col;g.explicit=true;
    return g;
  }
  /* One undo step of its own: without it, undoing the colour fill would also undo the edit
     before it, because the snapshot that edit pushed is the one carrying the old setting. */
  function bimSetRoomScheme(by){
    by=(by==='dept'||by==='occupancy')?by:'';
    if(by!==(A3D.roomScheme||'')){pushUndo();A3D.roomScheme=by;}
    paint();saveSoon();
    var n=by?bimRoomSchemeValues(by).length:0;
    a3dToast(!by?'Room colour fill off':('Rooms filled by '+bimRoomSchemeLabel(by)+' — '+(n?(n+' value'+(n===1?'':'s')):'no room has one yet')));
    return by;
  }
  function bimCycleRoomScheme(){   /* ROOMCOLOR: Department, then Occupancy, then off */
    return bimSetRoomScheme(A3D.roomScheme==='dept'?'occupancy':(A3D.roomScheme==='occupancy'?'':'dept'));
  }
  function drawRoomSchemeLegend(ctx,V,W,H){
    var lg=A3D.pendingRoomLegend;
    A3D.pendingRoomLegend=null;A3D.lastRoomLegend=null;
    if(!lg||!lg.by||!lg.items.length||A3D.sheetCapture)return;
    ctx.save();
    try{
      var sr=bimSafeViewRect(),i,rowH=16,pad=8,sw=11,w,tw,h,x,y,ry;
      var title='Rooms by '+bimRoomSchemeLabel(lg.by);
      var rows=lg.items.slice().sort(function(a,b){a=a.name.toLowerCase();b=b.name.toLowerCase();return a<b?-1:(a>b?1:0);}).map(function(it){
        var r=lg.by==='occupancy'?bimOccLoadRow(it.name):null;
        return {name:it.name,col:it.col,note:r?(r.m2.toFixed(2)+' m²/p '+r.basis):''};
      });
      ctx.font='11px sans-serif';ctx.textBaseline='middle';ctx.textAlign='left';   /* the tag pass leaves it centred */
      w=ctx.measureText(title).width;
      for(i=0;i<rows.length;i++){tw=sw+6+ctx.measureText(rows[i].name).width+(rows[i].note?10+ctx.measureText(rows[i].note).width:0);if(tw>w)w=tw;}
      w=Math.ceil(w+pad*2);h=pad*2+rowH*(rows.length+1);
      x=sr.x+12;y=sr.y+12;
      ctx.globalAlpha=1;
      ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(x,y,w,h);
      ctx.strokeStyle='rgba(255,255,255,0.18)';ctx.lineWidth=1;ctx.strokeRect(x+0.5,y+0.5,w-1,h-1);
      ctx.fillStyle='#e8edf2';ctx.fillText(title,x+pad,y+pad+rowH/2);
      for(i=0;i<rows.length;i++){
        ry=y+pad+rowH*(i+1);
        ctx.globalAlpha=BIM_SCHEME_ALPHA;ctx.fillStyle=rows[i].col;ctx.fillRect(x+pad,ry+(rowH-sw)/2,sw,sw);
        ctx.globalAlpha=1;ctx.fillStyle='#e8edf2';ctx.fillText(rows[i].name,x+pad+sw+6,ry+rowH/2);
        if(rows[i].note){ctx.fillStyle='#9aa7b4';ctx.fillText(rows[i].note,x+pad+sw+6+ctx.measureText(rows[i].name).width+10,ry+rowH/2);}
      }
      A3D.lastRoomLegend={by:lg.by,title:title,items:rows,box:[x,y,w,h],align:ctx.textAlign};
    }catch(e){
      console.warn('[BIM] room legend',e);
      if(!A3D.roomLegendWarned){A3D.roomLegendWarned=true;a3dToast('The room colour legend could not be drawn');}
    }
    ctx.restore();
  }
  /* 101, 102 ... on the first level, 201 ... on the second: the next free number in that
     level's hundred. Past 99 rooms on a level, one past the highest number anywhere. */
  function bimNextRoomNumber(levelId){
    var li=0,i,base,top=0,n,any=0;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===levelId){li=i;break;}
    base=(li+1)*100;
    for(i=0;i<A3D.objs.length;i++){
      if(A3D.objs[i].t!=='room')continue;
      n=parseInt(A3D.objs[i].number,10);
      if(!isFinite(n))continue;
      if(n>any)any=n;
      if(n>base&&n<base+100&&n>top)top=n;
    }
    if(!top)return String(base+1);
    if(top<base+99)return String(top+1);
    return String(any+1);
  }
  /* Other rooms already using this number. */
  function bimRoomsWithNumber(num,exceptId){
    var out=[],i;
    if(!num)return out;
    for(i=0;i<A3D.objs.length;i++){
      var r=A3D.objs[i];
      if(r.t==='room'&&r.id!==exceptId&&String(r.number||'')===String(num))out.push(r);
    }
    return out;
  }
  /* Set one room field, with undo, and say when a number is already taken. */
  function bimSetRoomField(room,k,val){
    var f=null,i;
    for(i=0;i<BIM_ROOM_FIELDS.length;i++)if(BIM_ROOM_FIELDS[i].k===k)f=BIM_ROOM_FIELDS[i];
    if(k==='name')f={k:'name',label:'Name'};   /* a tag renames its room */
    if(!room||room.t!=='room'||!f){a3dToast('That room field does not exist');return false;}
    val=String(val===undefined||val===null?'':val).replace(/^\s+|\s+$/g,'').slice(0,80);
    if(k==='name'&&!val){a3dToast('A room needs a name');return false;}
    if(bimRoomField(room,k)===val)return true;
    pushUndo();
    room[k]=val;
    if(k==='number'&&val){
      var dup=bimRoomsWithNumber(val,room.id);
      if(dup.length)a3dToast('Number '+val+' is also used by '+dup.map(function(r){return r.name;}).join(', '));
    }
    refreshTree();paint();saveSoon();
    return true;
  }
  /* __acad3dV105b: a room is bounded by the FACES of the walls around it, not by their
     centerlines.

     The bug this fixes: a plan drawn as one closed wall measured its inner loop, and the SAME
     plan drawn as four separate walls measured the centerline rectangle -- larger by a wall
     thickness all round. Nothing caught it until a level reported a net area bigger than its
     gross, which cannot happen. The inset is the one the gross ring uses, taken to the left of
     travel because an interior face traces counter-clockwise.

     Only the room takes it. A floor or a foundation slab placed in the same region still runs to
     the centerlines, because a slab genuinely does run under the walls that sit on it. */
  function bimRoomFaceRing(reg){
    if(!reg||!reg.pts||!reg.srcs||!reg.srcs.length)return null;
    var ring;
    try{ring=bimInsetFaceRing(reg.pts,reg.bulges||[],reg.srcs,{},-1);}
    catch(eRF){console.warn('[BIM] Room face inset failed: ',eRF);return null;}
    if(!ring||ring.length<3)return null;
    if(!(bimPolyArea(ring)>1e-6))return null;
    return ring;
  }
  function bimCreateRoom(boundary){
    pushUndo();
    A3D.counts.room=(A3D.counts.room||0)+1;
    var rpts=boundary.roomPts||boundary.pts;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:'#7fd4c4',
      pos:[0,0,0],pts:rpts,y:boundary.y,area:bimPolyArea(rpts),levelId:A3D.activeLevel,
      sourceType:boundary.sourceType,sourceId:boundary.sourceId,layer:A3D.activeLayer};
    if(boundary.region)o.region=bimCloneRegion(boundary.region);   /* __acad3dV99 */
    o.number=bimNextRoomNumber(o.levelId);   /* __acad3dV101 */
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' ('+o.number+') created \u2014 '+o.area.toFixed(2)+' m\u00b2');
    return o;
  }
