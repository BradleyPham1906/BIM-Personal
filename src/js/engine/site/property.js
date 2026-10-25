  /* ================= __acad3dV103: the property ================= */
  function bimIsProperty(o){return !!(o&&o.t==='property'&&o.start&&o.legs&&o.legs.length);}
  /* The ONE derivation: corners, closure, area and setback line, in WORLD plan terms. */
  function bimPropertyGeometry(o){
    var q=bimObjOffset(o);
    var tr=bimTraverse([o.start[0]+q[0],o.start[1]+q[2]],o.legs);
    var sb=bimSetbackRing(tr.ring,o.setbacks||[]),any=false,i;
    for(i=0;i<(o.setbacks||[]).length;i++)if(o.setbacks[i]>0)any=true;
    tr.setback=any?sb:null;
    return tr;
  }
  /* Building elements whose plan footprint leaves the setback line. A vertex ON the line is in. */
  var BIM_SETBACK_TYPES={wall:1,column:1,floor:1,roof:1,beam:1,stair:1,ceiling:1,footing:1,stripfooting:1};
  function bimSetbackViolations(o){
    var g=bimPropertyGeometry(o);
    if(!g.setback||g.setback.error)return {list:[],marks:[]};
    var ring=g.setback.ring,list=[],marks=[],i,j,b,q,v,p,bad;
    function onEdge(pt){
      var k;
      for(k=0;k<ring.length;k++){
        var A=ring[k],B=ring[(k+1)%ring.length];
        if(bimPointSegDist(pt[0],pt[1],A[0],A[1],B[0],B[1])<1e-6)return true;
      }
      return false;
    }
    for(i=0;i<A3D.objs.length;i++){
      b=A3D.objs[i];
      if(!(b.t==='solid'&&b.bim&&BIM_SETBACK_TYPES[b.bim.type]&&b.mesh&&b.mesh.v))continue;
      q=bimObjOffset(b);bad=false;
      for(j=0;j<b.mesh.v.length;j++){
        v=b.mesh.v[j];p=[v[0]+q[0],v[2]+q[2]];
        if(!bimPointInPoly(p,ring)&&!onEdge(p)){bad=true;marks.push(p);}
      }
      if(bad)list.push({id:b.id,name:b.name});
    }
    return {list:list,marks:marks};
  }
  function bimPropertyScreenSegs(o,V,W,H){
    var g=bimPropertyGeometry(o),y=(o.y||0)+bimObjOffset(o)[1],out=[],i;
    for(i=0;i<g.pts.length-1;i++)
      out.push([toScreen([g.pts[i][0],y,g.pts[i][1]],V,W,H),toScreen([g.pts[i+1][0],y,g.pts[i+1][1]],V,W,H)]);
    return {segs:out,g:g,y:y};
  }
  function drawProperties(ctx,V,W,H){
    if(A3D.section)return;
    var i,o,S,k,sel;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsProperty(o))continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      S=bimPropertyScreenSegs(o,V,W,H);
      sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      ctx.save();
      ctx.globalAlpha*=bimLayerAlpha(o);   /* __acad3dV121: the layer's transparency */
      ctx.strokeStyle=sel?'#4ea1ff':'#d8a657';ctx.lineWidth=sel?2.2:1.8;
      ctx.setLineDash([16,4,3,4,3,4]);
      ctx.beginPath();
      for(k=0;k<S.segs.length;k++){ctx.moveTo(S.segs[k][0][0],S.segs[k][0][1]);ctx.lineTo(S.segs[k][1][0],S.segs[k][1][1]);}
      ctx.stroke();ctx.setLineDash([]);
      if(S.g.misclosure>0.001){
        var e1=toScreen([S.g.end[0],S.y,S.g.end[1]],V,W,H),e0=toScreen([S.g.pts[0][0],S.y,S.g.pts[0][1]],V,W,H);
        ctx.strokeStyle='#ff5f56';ctx.lineWidth=2;
        ctx.beginPath();ctx.moveTo(e1[0],e1[1]);ctx.lineTo(e0[0],e0[1]);ctx.stroke();
      }
      ctx.font='10px system-ui,sans-serif';ctx.fillStyle=sel?'#9ec1ff':'#e8c887';
      ctx.textAlign='center';ctx.textBaseline='bottom';
      for(k=0;k<S.segs.length&&k<o.legs.length;k++){
        var a=S.segs[k][0],b=S.segs[k][1],ang=Math.atan2(b[1]-a[1],b[0]-a[0]);
        if(ang>Math.PI/2)ang-=Math.PI;else if(ang<-Math.PI/2)ang+=Math.PI;
        ctx.save();
        ctx.translate((a[0]+b[0])/2,(a[1]+b[1])/2);ctx.rotate(ang);
        ctx.fillText(bimFormatBearing(o.legs[k].az)+'   '+o.legs[k].d.toFixed(2)+' m',0,-3);
        ctx.restore();
      }
      if(S.g.setback&&S.g.setback.ring){
        var r=S.g.setback.ring;
        ctx.strokeStyle='#c07b50';ctx.lineWidth=1;ctx.setLineDash([6,4]);
        ctx.beginPath();
        for(k=0;k<r.length;k++){
          var sp=toScreen([r[k][0],S.y,r[k][1]],V,W,H);
          if(k===0)ctx.moveTo(sp[0],sp[1]);else ctx.lineTo(sp[0],sp[1]);
        }
        ctx.closePath();ctx.stroke();ctx.setLineDash([]);
        var vi=bimSetbackViolations(o);
        ctx.strokeStyle='#ff5f56';ctx.lineWidth=2;
        for(k=0;k<vi.marks.length;k++){
          var mp=toScreen([vi.marks[k][0],S.y,vi.marks[k][1]],V,W,H);
          ctx.beginPath();ctx.moveTo(mp[0]-4,mp[1]-4);ctx.lineTo(mp[0]+4,mp[1]+4);
          ctx.moveTo(mp[0]+4,mp[1]-4);ctx.lineTo(mp[0]-4,mp[1]+4);ctx.stroke();
        }
      }
      ctx.restore();
    }
  }
  function bimPickProperty(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),best=null,bd=6,i,o,S,k,d;
    for(i=A3D.objs.length-1;i>=0;i--){
      o=A3D.objs[i];
      if(!bimIsProperty(o))continue;
      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */
      S=bimPropertyScreenSegs(o,V,W,H);
      for(k=0;k<S.segs.length;k++){
        d=bimPointSegDist(x,y,S.segs[k][0][0],S.segs[k][0][1],S.segs[k][1][0],S.segs[k][1][1]);
        if(d<bd){bd=d;best=o;}
      }
    }
    return best;
  }
  /* The north arrow: through the camera, so it points at true north in any view. */
  function drawNorthArrow(ctx,V,W,H){
    A3D.lastNorth=null;   /* __acad3dV119: what the hook reports is what this frame drew */
    if(!bimCameraIsPlan())return;   /* __acad3dV119: flat is not plan -- an elevation is flat */
    var tn=bimTrueNorthDeg()*Math.PI/180,c=A3D.cam;
    var p0=toScreen([c.tx,0,c.tz],V,W,H),p1=toScreen([c.tx+Math.sin(tn),0,c.tz-Math.cos(tn)],V,W,H);
    var dx=p1[0]-p0[0],dy=p1[1]-p0[1],L=Math.sqrt(dx*dx+dy*dy);
    if(!(L>1e-9))return;
    dx/=L;dy/=L;
    var cx=W-48,cy=78,R=22;
    ctx.save();
    ctx.fillStyle='rgba(20,22,26,0.8)';ctx.beginPath();ctx.arc(cx,cy,R+6,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='#8f97a3';ctx.lineWidth=1;ctx.stroke();
    ctx.fillStyle='#dfe4ea';
    ctx.beginPath();
    ctx.moveTo(cx+dx*R,cy+dy*R);
    ctx.lineTo(cx-dy*7-dx*R*0.55,cy+dx*7-dy*R*0.55);
    ctx.lineTo(cx-dx*R*0.3,cy-dy*R*0.3);
    ctx.lineTo(cx+dy*7-dx*R*0.55,cy-dx*7-dy*R*0.55);
    ctx.closePath();ctx.fill();
    ctx.font='bold 11px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText('N',cx+dx*(R+14),cy+dy*(R+14));
    ctx.restore();
    A3D.lastNorth={dx:dx,dy:dy};
  }
  function bimNewProperty(start,legs){
    A3D.counts.property=(A3D.counts.property||0)+1;
    var s=[],i;
    for(i=0;i<legs.length;i++)s.push(0);
    return {id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'property',name:'Property_'+A3D.counts.property,
      col:'#d8a657',pos:[0,0,0],start:[start[0],start[1]],y:0,
      legs:legs.map(function(l){return {b:l.b,az:l.az,d:l.d};}),setbacks:s,layer:A3D.activeLayer};
  }
  function bimClosureText(g){
    return (g.misclosure<0.0005?'closes':'misclosure '+g.misclosure.toFixed(3)+' m, 1:'+Math.round(g.precision))+
      ', perimeter '+g.perimeter.toFixed(2)+' m, area '+g.area.toFixed(2)+' m\u00b2 ('+(g.area/10000).toFixed(4)+' ha)';
  }
  /* The property dialog: new, or editing an existing parcel. Parses and shows closure as you type. */
  function openPropertyDlg(existing){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    var st=existing?existing.start:[0,0];
    var legsTxt=existing?existing.legs.map(function(l){return l.b+' '+l.d.toFixed(3);}).join('\n'):'';
    d.innerHTML='<div class="a3d-dlghd">'+(existing?'Edit Property Line':'Property Line')+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Point of beginning X</label><input type="number" step="any" data-a3dp="sx" value="'+st[0]+'"></div>'+
      '<div class="a3d-dlgrow"><label>Point of beginning Y</label><input type="number" step="any" data-a3dp="sy" value="'+st[1]+'"></div>'+
      '<div class="a3d-dlgrow"><label>Legs: bearing distance, one per line</label></div>'+
      '<textarea data-a3dp="legs" rows="7" style="width:100%;font:12px monospace" placeholder="N 45 30 00 E 120.00">'+bimEsc(legsTxt)+'</textarea>'+
      '<div data-a3dp="closure" class="a3d-propnote"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var sx=d.querySelector('[data-a3dp="sx"]'),sy=d.querySelector('[data-a3dp="sy"]'),lt=d.querySelector('[data-a3dp="legs"]');
    var cl=d.querySelector('[data-a3dp="closure"]'),eb=d.querySelector('#a3d-dlgerr');
    function read(){
      var p=bimParseLegs(lt.value),x=parseFloat(sx.value),y=parseFloat(sy.value);
      if(!isFinite(x)||!isFinite(y))p.errors.unshift('the point of beginning must be two numbers');
      return {p:p,start:[x,y]};
    }
    function show(){
      var r=read();
      eb.textContent=r.p.errors.join('; ');
      cl.textContent=r.p.errors.length?'':bimClosureText(bimTraverse(r.start,r.p.legs));
    }
    function submit(){
      var r=read();
      if(r.p.errors.length){eb.textContent=r.p.errors.join('; ');return;}
      closeDlg();
      try{
        pushUndo();
        var o;
        if(existing&&objById(existing.id)){
          o=objById(existing.id);
          o.start=r.start;o.legs=r.p.legs;
          if(!o.setbacks||o.setbacks.length!==o.legs.length){o.setbacks=o.legs.map(function(){return 0;});}
        }else{
          o=bimNewProperty(r.start,r.p.legs);
          A3D.objs.push(o);
        }
        A3D.sel=o.id;A3D.selSet=[o.id];
        refreshTree();paint();saveSoon();
        a3dToast(o.name+': '+bimClosureText(bimPropertyGeometry(o)));
      }catch(eP){
        console.warn('[BIM] Property line failed',eP);
        a3dToast('The property line could not be created - see the console');
      }
    }
    lt.addEventListener('input',show);sx.addEventListener('input',show);sy.addEventListener('input',show);
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    show();
    lt.focus();
  }
  /* A parcel from a drawn closed shape: its corners become the legs. The shape is kept. */
  function bimPropertyFromSketch(o){
    if(!o||o.t!=='sketch'||o.closed===false||!o.pts||o.pts.length<3){a3dToast('Select a closed shape to make a property from');return null;}
    if(bimHasBulge(o.bulges)){a3dToast('Property lines are straight legs; this shape has arcs');return null;}
    var q=bimObjOffset(o),ring=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
    var legs=bimLegsFromRing(ring);
    if(legs.length<3){a3dToast('That shape has fewer than 3 sides');return null;}
    pushUndo();
    var pr=bimNewProperty(ring[0],legs);
    A3D.objs.push(pr);
    A3D.sel=pr.id;A3D.selSet=[pr.id];
    refreshTree();paint();saveSoon();
    a3dToast(pr.name+' from '+o.name+': '+bimClosureText(bimPropertyGeometry(pr)));
    return pr;
  }
