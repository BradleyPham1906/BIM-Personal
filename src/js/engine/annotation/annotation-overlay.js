  /* ================= __acad3dV82: the annotation overlay =================

     The Assets library, back, as real objects layered over the 2D and 3D views.

     Notes, callouts and markers are the annotation a drawing needs.

     These are world-ANCHORED and screen-DRAWN, the same shape as the text labels this app already
     had: anchored to a point at a level elevation, painted at a constant pixel size so they stay
     legible at any zoom, and living in A3D.objs so selection, the move gizmo, layers, levels, undo
     and persistence all work without a second implementation of any of them. */
  var BIM_NOTE_KINDS=[
    {k:'note',   label:'Note card',  w:170,h:96, why:'a titled card'},
    {k:'rect',   label:'Rectangle',  w:150,h:90, why:'a rectangle'},
    {k:'ellipse',label:'Ellipse',    w:150,h:90, why:'an ellipse'},
    {k:'line',   label:'Rule / line',w:170,h:0,  why:'a straight rule'},
    {k:'image',  label:'Image',      w:180,h:120,why:'a placed picture'},
    {k:'table',  label:'Table',      w:220,h:96, why:'a grid of cells'}
  ];
  function bimNoteDef(kind){
    var i;
    for(i=0;i<BIM_NOTE_KINDS.length;i++)if(BIM_NOTE_KINDS[i].k===kind)return BIM_NOTE_KINDS[i];
    return BIM_NOTE_KINDS[0];
  }
  var BIM_NOTE_STYLE={fill:'#f6e7a8',stroke:'#3a4048',color:'#1b1f24',lineWidth:1.2,fontSize:12};
  function bimCreateNote(kind,ptXZ,opts){
    var def=bimNoteDef(kind);
    var lvl=bimGetActiveLevel();
    A3D.counts.note=(A3D.counts.note||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'note',kind:def.k,
      name:def.label+'_'+A3D.counts.note,
      pt:[ptXZ[0],ptXZ[1]],
      y:lvl?lvl.elev:0,
      pos:[0,0,0],
      w:def.w,h:def.h,
      title:(def.k==='note')?'Note':'',
      body:(def.k==='note')?'Double-click the Text field in Properties to edit.':'',
      cells:(def.k==='table')?'Item\tQty\nBeam\t4\nColumn\t6':'',
      src:'',
      style:{fill:BIM_NOTE_STYLE.fill,stroke:BIM_NOTE_STYLE.stroke,color:BIM_NOTE_STYLE.color,
             lineWidth:BIM_NOTE_STYLE.lineWidth,fontSize:BIM_NOTE_STYLE.fontSize},
      layer:A3D.activeLayer,
      bim:{type:'note',kind:def.k,levelId:A3D.activeLevel}
    };
    if(opts&&opts.src)o.src=opts.src;
    if(def.k==='rect'||def.k==='ellipse'){o.style.fill='rgba(78,161,255,0.16)';o.style.stroke='#4ea1ff';}
    if(def.k==='line'){o.style.stroke='#e05c4a';o.style.lineWidth=2;}
    if(def.k==='table'){o.style.fill='rgba(255,255,255,0.94)';}
    if(def.k==='image'){o.style.fill='rgba(255,255,255,0.06)';}
    A3D.objs.push(o);
    return o;
  }
  /* The screen rectangle an overlay item occupies right now. One place, so draw, pick and the
     resize handles cannot disagree about where the thing is. */
  function bimNoteRect(o,V,W,H){
    var q=bimObjOffset(o);
    var sp=toScreen([o.pt[0]+q[0],(o.y||0)+q[1],o.pt[1]+q[2]],V,W,H);
    if(!isFinite(sp[0])||!isFinite(sp[1]))return null;
    return {ax:sp[0],ay:sp[1],x:sp[0],y:sp[1]-(o.h||0),w:o.w||10,h:o.h||0};
  }
  function bimNoteImageEl(o){
    if(!o.src)return null;
    if(!A3D._noteImgs)A3D._noteImgs={};
    var cached=A3D._noteImgs[o.id];
    if(cached&&cached.__src===o.src)return cached.complete?cached:null;
    var im=new Image();
    im.__src=o.src;
    im.onload=function(){paint();};
    im.onerror=function(){console.warn('[BIM] Overlay image failed to decode for '+o.name);};
    im.src=o.src;
    A3D._noteImgs[o.id]=im;
    return im.complete?im:null;
  }
  function drawNotes(ctx,V,W,H){
    if(A3D.section)return;
    var i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='note')continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(o))continue;
      var r=bimNoteRect(o,V,W,H);
      if(!r)continue;
      var sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      var st=o.style||BIM_NOTE_STYLE;
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      ctx.lineWidth=st.lineWidth||1.2;
      ctx.strokeStyle=sel?'#4ea1ff':(st.stroke||'#3a4048');
      ctx.fillStyle=st.fill||'#f6e7a8';
      if(o.kind==='line'){
        ctx.beginPath();ctx.moveTo(r.ax,r.ay);ctx.lineTo(r.ax+r.w,r.ay);ctx.stroke();
      }else if(o.kind==='ellipse'){
        ctx.beginPath();
        ctx.ellipse(r.x+r.w/2,r.y+r.h/2,Math.abs(r.w/2),Math.abs(r.h/2),0,0,Math.PI*2);
        ctx.fill();ctx.stroke();
      }else{
        ctx.beginPath();
        if(ctx.roundRect)ctx.roundRect(r.x,r.y,r.w,r.h,o.kind==='note'?6:3);
        else ctx.rect(r.x,r.y,r.w,r.h);
        ctx.fill();ctx.stroke();
      }
      ctx.fillStyle=st.color||'#1b1f24';
      ctx.textBaseline='top';ctx.textAlign='left';
      if(o.kind==='note'){
        ctx.font='700 '+((st.fontSize||12)+1)+'px Inter,system-ui,sans-serif';
        ctx.fillText(bimNoteClip(ctx,o.title||'',r.w-16),r.x+8,r.y+7);
        ctx.font=(st.fontSize||12)+'px Inter,system-ui,sans-serif';
        bimNoteWrap(ctx,o.body||'',r.x+8,r.y+7+(st.fontSize||12)+7,r.w-16,
                    (st.fontSize||12)+4,r.h-20);
      }else if(o.kind==='table'){
        bimNoteTable(ctx,o,r,st);
      }else if(o.kind==='image'){
        var im=bimNoteImageEl(o);
        if(im){
          try{ctx.drawImage(im,r.x,r.y,r.w,r.h);}catch(eD){}
          ctx.strokeStyle=sel?'#4ea1ff':(st.stroke||'#3a4048');
          ctx.strokeRect(r.x,r.y,r.w,r.h);
        }else{
          ctx.font='11px Inter,system-ui,sans-serif';
          ctx.fillStyle='#9aa3ad';
          ctx.fillText(o.src?'loading image...':'no image chosen',r.x+8,r.y+8);
        }
      }
      // the anchor dot: this overlay item belongs to a POINT in the model, not to the screen
      ctx.fillStyle=sel?'#4ea1ff':'rgba(140,150,162,0.9)';
      ctx.beginPath();ctx.arc(r.ax,r.ay,2.6,0,Math.PI*2);ctx.fill();
      ctx.restore();
    }
  }
  function bimNoteClip(ctx,s,maxW){
    if(ctx.measureText(s).width<=maxW)return s;
    var t=s;
    while(t.length>1&&ctx.measureText(t+'\u2026').width>maxW)t=t.slice(0,-1);
    return t+'\u2026';
  }
  function bimNoteWrap(ctx,text,x,y,maxW,lh,maxH){
    var words=String(text).split(/\s+/),line='',yy=y,i;
    for(i=0;i<words.length;i++){
      var probe=line?(line+' '+words[i]):words[i];
      if(ctx.measureText(probe).width>maxW&&line){
        ctx.fillText(line,x,yy);yy+=lh;line=words[i];
        if(yy-y+lh>maxH)return;
      }else line=probe;
    }
    if(line&&yy-y<=maxH)ctx.fillText(line,x,yy);
  }
  function bimNoteTable(ctx,o,r,st){
    var rows=String(o.cells||'').split('\n').filter(function(s){return s.length;});
    if(!rows.length)return;
    var grid=rows.map(function(l){return l.split('\t');});
    var nc=0,i,j;
    for(i=0;i<grid.length;i++)if(grid[i].length>nc)nc=grid[i].length;
    if(!nc)return;
    var cw=r.w/nc,ch=r.h/grid.length;
    ctx.font=(st.fontSize||12)+'px Inter,system-ui,sans-serif';
    ctx.strokeStyle='rgba(60,68,78,0.55)';
    ctx.lineWidth=0.8;
    for(i=0;i<grid.length;i++){
      for(j=0;j<nc;j++){
        var cx=r.x+j*cw,cy=r.y+i*ch;
        ctx.strokeRect(cx,cy,cw,ch);
        ctx.fillStyle=(i===0)?'#0f1216':(st.color||'#1b1f24');
        ctx.font=((i===0)?'700 ':'')+(st.fontSize||12)+'px Inter,system-ui,sans-serif';
        ctx.fillText(bimNoteClip(ctx,grid[i][j]||'',cw-8),cx+4,cy+Math.max(2,(ch-(st.fontSize||12))/2));
      }
    }
  }
  function bimPickNote(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var i,o;
    // back to front: the last drawn is the one on top, and it is the one a click should reach
    for(i=A3D.objs.length-1;i>=0;i--){
      o=A3D.objs[i];
      if(o.t!=='note')continue;
      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(o))continue;
      var r=bimNoteRect(o,V,W,H);
      if(!r)continue;
      if(o.kind==='line'){
        if(bimPointSegDist(x,y,r.ax,r.ay,r.ax+r.w,r.ay)<7)return o;
        continue;
      }
      if(x>=r.x-2&&x<=r.x+r.w+2&&y>=r.y-2&&y<=r.y+r.h+2)return o;
    }
    return null;
  }
  /* Placed at the centre of the SAFE view rectangle (V79), un-projected onto the active level --
     so a new note lands where the user is looking and not behind the tool dock. */
  function bimPlaceNoteAtViewCentre(kind,opts,atPt){
    var s=bimSafeViewRect();
    var lvl=bimGetActiveLevel();
    /* __acad3dV124: a note dropped from the library goes where it was dropped */
    var g=atPt?[atPt[0],lvl?lvl.elev:0,atPt[1]]:groundPoint(s.x+s.w/2,s.y+s.h/2,lvl?lvl.elev:0);
    if(!g){
      console.warn('[BIM] Could not un-project the view centre; placing the '+kind+' at the origin.');
      g=[0,0,0];
    }
    pushUndo();
    var o=bimCreateNote(kind,[g[0],g[2]],opts);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' placed \u2014 drag it, or edit it in Properties');
    return o;
  }
  /* The one kind that needs a file. Read as a data URI so the drawing stays self-contained and
     keeps working with no server and no external reference (Principle 5). */
  function bimPlaceImageNote(atPt){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='image/*';
    inp.onchange=function(){
      var f=inp.files&&inp.files[0];
      if(!f)return;
      if(f.size>4*1024*1024){
        a3dToast('That image is larger than 4 MB \u2014 pick a smaller one');
        return;
      }
      var rd=new FileReader();
      rd.onload=function(){bimPlaceNoteAtViewCentre('image',{src:String(rd.result)},atPt);};
      rd.onerror=function(){
        console.warn('[BIM] Could not read the chosen image file.');
        a3dToast('That image could not be read');
      };
      rd.readAsDataURL(f);
    };
    inp.click();
    return true;
  }
