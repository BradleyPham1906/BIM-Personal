  /* ================= __acad3dV123: PUSH AND PULL =================

     A push drag is one record (drag.pp). The press only arms it: a press that never travels is a
     click, which opens the face's value box. The first movement takes the undo step and a snapshot
     of the object; every frame after restores the snapshot and applies the drag's TOTAL distance,
     the way the gizmo's rotations do, so a long drag cannot drift. */
  function bimPushPress(xy,ev,entry){
    return {pp:true,x0:xy[0],y0:xy[1],x:xy[0],y:xy[1],moved:false,entry:!!entry,
            fine:!!(ev&&ev.shiftKey&&!(ev.ctrlKey||ev.metaKey)),cx:ev?ev.clientX:0,cy:ev?ev.clientY:0};
  }
  /* Begins a push of the held face. needArrow: a drag reads the cursor along the arrow, so a face
     whose arrow points at the camera cannot be dragged -- a typed value needs no arrow. */
  function bimPushBegin(d,needArrow){
    var cur=bimFaceCurrent();
    if(!cur)return false;
    var f=cur.f,o=cur.o;
    if(!f.ok){a3dToast(f.why);return false;}
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),ar=bimFaceArrow(f,cur.region,V,W,H);
    if(needArrow&&!ar){
      a3dToast('This face points straight at you - turn the view to pull it, or click it and type');
      return false;
    }
    d.id=o.id;d.f=f;d.N=f.N.slice();d.C0=cur.region.C.slice();
    d.sx=ar?ar.sx:0;d.sy=ar?ar.sy:0;d.len2=ar?ar.len2:1;
    d.snap0=JSON.parse(JSON.stringify(o));
    d.seed0=A3D.face&&A3D.face.seed?A3D.face.seed.slice():d.C0.slice();
    d.dist=0;d.lastOk=0;d.limit=null;d.snapAt=null;d.snapLevel=null;
    d.snaps=bimPushSnapSetup(o,f,V,W,H);
    d.range=bimPushRange(d,o);
    if(f.kind==='sketch'){
      d.sketchId=o.id;d.sketchAt=A3D.objs.indexOf(o);
      d.padId='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      d.padName='Pad '+((A3D.counts.pad||0)+1);
    }
    A3D_MATERIALIZED=[];
    pushUndo();
    d.undoAt=UNDO_STACK.length;
    return true;
  }
  /* What a push can land on: the points of everything else, as they are on screen when the drag
     begins (the view does not move during a drag), and for a horizontal face the levels. */
  function bimPushSnapSetup(o,f,V,W,H){
    var out={pts:[],levels:[]},i,j,MAX=4000;
    if(!A3D_SNAP.point)return out;
    for(i=0;i<A3D.objs.length&&out.pts.length<MAX;i++){
      var ob=A3D.objs[i];
      if(ob.id===o.id||!bimLayerShown(ob)||!bimObjectVisibleOnLevel(ob))continue;
      var m=meshOf(ob),q=bimObjOffset(ob),P,s;
      if(m&&m.v){
        for(j=0;j<m.v.length&&out.pts.length<MAX;j++){
          P=[m.v[j][0]+q[0],m.v[j][1]+q[1],m.v[j][2]+q[2]];s=toScreen(P,V,W,H);
          if(isFinite(s[0])&&isFinite(s[1]))out.pts.push({x:s[0],y:s[1],P:P});
        }
      }else if(ob.t==='sketch'&&ob.pts){
        for(j=0;j<ob.pts.length&&out.pts.length<MAX;j++){
          P=bimWorldPt(ob,ob.pts[j],ob.y);s=toScreen(P,V,W,H);
          if(isFinite(s[0])&&isFinite(s[1]))out.pts.push({x:s[0],y:s[1],P:P});
        }
      }
    }
    if(Math.abs(f.N[1])>0.999)
      for(i=0;i<A3D.levels.length;i++)out.levels.push({elev:A3D.levels[i].elev,name:A3D.levels[i].name});
    return out;
  }
  /* A point under the cursor puts the face's plane through it -- SketchUp's inference; failing
     that, a level within the snap distance of where the face would be. */
  function bimPushSnap(d,xy,dist){
    var sn=d.snaps,best=null,bd=A3D_SNAP.pxThreshold,i;
    if(!sn)return null;
    for(i=0;i<sn.pts.length;i++){
      var p=sn.pts[i],dd=Math.sqrt((p.x-xy[0])*(p.x-xy[0])+(p.y-xy[1])*(p.y-xy[1]));
      if(dd<bd){bd=dd;best={d:vdot([p.P[0]-d.C0[0],p.P[1]-d.C0[1],p.P[2]-d.C0[2]],d.N),at:p.P,level:null};}
    }
    if(best)return best;
    var px=Math.sqrt(d.len2),bl=null,bld=A3D_SNAP.pxThreshold;
    for(i=0;i<sn.levels.length;i++){
      var dl=(sn.levels[i].elev-d.C0[1])*d.N[1],gap=Math.abs(dl-dist)*px;
      if(gap<bld){bld=gap;bl={d:dl,at:null,level:sn.levels[i].name};}
    }
    return bl;
  }
  function bimPushApply(xy){
    var d=drag,dx=xy[0]-d.x0,dy=xy[1]-d.y0;
    if(d.fine){dx*=A3D_GIZ.fine;dy*=A3D_GIZ.fine;}
    var dist=(dx*d.sx+dy*d.sy)/d.len2;
    if(A3D_SNAP.grid&&A3D_SNAP.gridSize>0)dist=Math.round(dist/A3D_SNAP.gridSize)*A3D_SNAP.gridSize;
    var sn=bimPushSnap(d,xy,dist);
    d.snapAt=sn&&sn.at?sn.at:null;d.snapLevel=sn&&sn.level?sn.level:null;
    if(sn)dist=sn.d;
    bimPushTo(dist);
  }
  /* HOW FAR A FACE CAN GO, worked out once from the object as the push found it: a size never below
     A3D_PUSH.min; a tube's radii in their order; a wall end no nearer its next corner than 5 cm; a
     solid's face never past a corner it is joined to -- behind it by less than A3D_PUSH.min, ahead of
     it at all, where it would be level with the face beyond. A drag stops there exactly; a typed
     value beyond it is refused with the reason. */
  function bimPushRange(d,o){
    var f=d.f,mn=A3D_PUSH.min,r={lo:-Infinity,hi:Infinity,whyLo:'',whyHi:''};
    function lo(v,why){if(v>r.lo){r.lo=v;r.whyLo=why;}}
    function hi(v,why){if(v<r.hi){r.hi=v;r.whyHi=why;}}
    if(f.kind==='prm'){
      var p=mergePrm(o.t,o.prm),size=f.dim,nm=f.dimName.toLowerCase();
      if(f.dsign>0)lo(mn-size,'The '+nm+' cannot be less than '+bimFmtLen(mn));
      else hi(size-mn,'The '+nm+' cannot be less than '+bimFmtLen(mn));
      if(f.param==='OuterRadius')lo(p.InnerRadius*SCALE+mn-size,'The outer radius has to stay larger than the inner');
      if(f.param==='InnerRadius')lo(size-(p.OuterRadius*SCALE-mn),'The inner radius has to stay smaller than the outer');
    }else if(f.kind==='wallTop'||f.kind==='colTop'){
      lo(mn-o.bim.height,(f.kind==='wallTop'?'A wall':'A column')+' cannot be lower than '+bimFmtLen(mn));
    }else if(f.kind==='wallEnd'){
      var e=bimWallEndInfo(o,f.key);
      if(e)lo(0.05-e.L,'The end of the wall cannot come nearer than '+bimFmtLen(0.05)+' to its next corner');
    }else if(f.kind==='solid'){
      var sr=bimPushSolidRange(o,f);
      lo(sr.lo,'The face can come in '+bimFmtLen(-sr.lo)+' at most - the solid would be thinner than '+bimFmtLen(mn));
      hi(sr.hi,'The face can go out '+bimFmtLen(sr.hi)+' at most - there it is level with the face beyond');
    }else if(f.kind==='sketch'&&f.on){
      var on=objById(f.on);
      lo(0,'This sketch is drawn on '+(on?on.name:'a solid')+' - Pocket, in the Sketch tools, cuts into it');
    }
    return r;
  }
  function bimPushSolidRange(o,f){
    var m=o.mesh,keys={},mv,i,k,lo=-Infinity,hi=Infinity,N=f.N;
    if(!m||!m.v||!f.fis)return {lo:lo,hi:hi};
    for(i=0;i<f.fis.length;i++){var fc=m.f[f.fis[i]];for(k=0;k<fc.length;k++)keys[bimPosKey(m.v[fc[k]])]=1;}
    mv=m.v.map(function(v){return !!keys[bimPosKey(v)];});
    for(i=0;i<m.f.length;i++){
      var fc2=m.f[i];
      if(!fc2)continue;
      for(k=0;k<fc2.length;k++){
        var a=fc2[k],b=fc2[(k+1)%fc2.length];
        if(mv[a]===mv[b])continue;
        var mi=mv[a]?a:b,ui=mv[a]?b:a;
        var c=(m.v[ui][0]-m.v[mi][0])*N[0]+(m.v[ui][1]-m.v[mi][1])*N[1]+(m.v[ui][2]-m.v[mi][2])*N[2];
        if(c<-1e-9)lo=Math.max(lo,c+A3D_PUSH.min);
        else if(c>1e-9)hi=Math.min(hi,c);
      }
    }
    return {lo:lo,hi:hi};
  }
  /* The push, by a TOTAL distance along the outward normal: from the snapshot, every time. A drag past
     the range stops at its end and says so; strict (a typed value) refuses instead. A distance the
     object still will not take leaves it at the last one it did. */
  function bimPushTo(dist,strict){
    var d=drag;
    if(!d||!d.pp||!d.f)return false;
    var rg=d.range||{lo:-Infinity,hi:Infinity},lim=null;
    if(dist<rg.lo-1e-12){lim=rg.whyLo;if(strict){d.limit=lim;return false;}dist=rg.lo;}
    else if(dist>rg.hi+1e-12){lim=rg.whyHi;if(strict){d.limit=lim;return false;}dist=rg.hi;}
    var r=bimPushApplyDist(d,dist);
    if(r.ok){d.lastOk=dist;d.dist=dist;d.limit=lim;}
    else{
      d.limit=r.why||'That is as far as this face goes';
      if(d.lastOk!==dist)bimPushApplyDist(d,d.lastOk);
      d.dist=d.lastOk;
    }
    bimPushFollow(d);
    paint();
    return r.ok&&!(strict&&lim);
  }
  /* the held face goes where the push put it */
  function bimPushFollow(d){
    if(!A3D.face)return;
    if(d.f.kind==='sketch'){
      var sk=d.snap0,q=bimObjOffset(sk),y=(sk.y||0)+q[1];
      if(Math.abs(d.dist)<1e-9)A3D.face={id:d.sketchId,key:'region',N:[0,1,0],outward:true,seed:d.seed0.slice()};
      else A3D.face={id:d.padId,key:'solid',N:[0,d.dist>0?1:-1,0],outward:true,
                     seed:[d.C0[0],y+d.dist,d.C0[2]]};
      return;
    }
    if(d.f.kind==='solid')
      A3D.face.seed=[d.seed0[0]+d.N[0]*d.dist,d.seed0[1]+d.N[1]*d.dist,d.seed0[2]+d.N[2]*d.dist];
  }
  function bimPushApplyDist(d,dist){
    var f=d.f;
    if(f.kind==='sketch')return bimPushSketchTo(d,dist);
    bimGizmoRestoreObjs([d.id],[d.snap0]);
    var o=objById(d.id);
    if(!o)return {ok:false,why:'The object is gone'};
    if(f.kind==='prm')return bimPushPrm(o,f,dist);
    if(f.kind==='wallTop'||f.kind==='wallEnd')return bimPushWall(o,f,dist);
    if(f.kind==='colTop')return bimPushColumn(o,f,dist);
    if(f.kind==='solid')return bimPushSolid(o,f,dist);
    return {ok:false,why:f.why||'This face does not move'};
  }
  function bimPushPrm(o,f,dist){
    var p=mergePrm(o.t,o.prm);
    p[f.param]=p[f.param]+f.psign*dist/SCALE;
    var err=validatePrm(o.t,p);
    if(err)return {ok:false,why:err};
    var size=(f.param==='Ymax'||f.param==='Ymin')?(p.Ymax-p.Ymin)*SCALE:p[f.param]*SCALE;
    if(!(size>=A3D_PUSH.min))return {ok:false,why:f.dimName+' cannot be less than '+bimFmtLen(A3D_PUSH.min)};
    o.prm=p;
    if(f.oneSided){
      if(!o.pos)o.pos=[0,0,0];
      o.pos=[o.pos[0]+f.N[0]*dist/2,o.pos[1]+f.N[1]*dist/2,o.pos[2]+f.N[2]*dist/2];
    }
    return {ok:true};
  }
  function bimPushWall(o,f,dist){
    var b=o.bim,res;
    if(f.kind==='wallTop'){
      var h=b.height+dist;
      if(!(h>=A3D_PUSH.min))return {ok:false,why:'A wall cannot be lower than '+bimFmtLen(A3D_PUSH.min)};
      res=bimBuildWallGeometry(b.centerline,b.baseY,h,b.thickness,b.align,b.closed,b.bulges);
    }else{
      var e=bimWallEndInfo(o,f.key);
      if(!e)return {ok:false,why:'This end has no length to pull'};
      if(!(e.L+dist>=0.05))return {ok:false,why:'The end of the wall cannot come closer than '+bimFmtLen(0.05)+' to the next corner'};
      var cl=b.centerline.map(function(p){return p.slice();});
      cl[e.i]=[cl[e.i][0]+e.N[0]*dist,cl[e.i][1]+e.N[2]*dist];
      res=bimBuildWallGeometry(cl,b.baseY,b.height,b.thickness,b.align,b.closed,b.bulges);
    }
    if(res.error)return {ok:false,why:res.error};
    o.mesh=res.mesh;
    o.bim=bimCarryBim(b,res.bim);
    bimPropagateFrom([o.id],'rebuild');   /* live, as a grip drag is: openings, rooms and clones follow */
    return {ok:true};
  }
  function bimPushColumn(o,f,dist){
    var b=o.bim,h=b.height+dist;
    if(!(h>=A3D_PUSH.min))return {ok:false,why:'A column cannot be shorter than '+bimFmtLen(A3D_PUSH.min)};
    var res=bimBuildColumnGeometry(b.center,b.baseY,b.width,b.depth,h,b.rotation||0,b.section||null);   /* __acad3dV126 */
    if(res.error)return {ok:false,why:res.error};
    o.mesh=res.mesh;b.height=h;
    bimPropagateFrom([o.id],'rebuild');
    return {ok:true};
  }
  function bimNewell(pts){
    var n=[0,0,0],i;
    for(i=0;i<pts.length;i++){
      var p=pts[i],q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);n[1]+=(p[2]-q[2])*(p[0]+q[0]);n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return n;
  }
  /* A solid's face: every corner at one of the face's corner positions moves along the normal -- by
     position, because an imported mesh repeats its corners per face -- and every face that shares
     one stretches. A face that would turn over or flatten refuses the move. */
  function bimPushSolid(o,f,dist){
    var m=o.mesh,keys={},i,k;
    if(!m||!m.v||!f.fis||!f.fis.length)return {ok:false,why:'This solid has no face there'};
    for(i=0;i<f.fis.length;i++){
      var fc=m.f[f.fis[i]];
      for(k=0;k<fc.length;k++)keys[bimPosKey(m.v[fc[k]])]=1;
    }
    var mv=m.v.map(function(v){return !!keys[bimPosKey(v)];});
    var nv=m.v.map(function(v,j){return mv[j]?[v[0]+f.N[0]*dist,v[1]+f.N[1]*dist,v[2]+f.N[2]*dist]:v.slice();});
    for(i=0;i<m.f.length;i++){
      var fc2=m.f[i],touched=false;
      if(!fc2||fc2.length<3)continue;
      for(k=0;k<fc2.length;k++)if(mv[fc2[k]]){touched=true;break;}
      if(!touched)continue;
      var a=bimNewell(fc2.map(function(ix){return m.v[ix];})),b=bimNewell(fc2.map(function(ix){return nv[ix];}));
      var la=Math.sqrt(vdot(a,a)),lb=Math.sqrt(vdot(b,b));
      if(la<1e-12)continue;
      /* level with the face beyond flattens the face between them, which is allowed; past it, no */
      if(vdot(a,b)<0)return {ok:false,why:'That would turn '+o.name+' inside out - this is as far as the face goes'};
    }
    o.mesh={v:nv,f:m.f.map(function(fc3){return fc3.slice();})};
    return {ok:true};
  }
  /* A closed sketch pulled: a Pad of the pulled height, above the sketch or below it, at the sketch
     where it is; the sketch comes back when the pull returns to nought. A sketch drawn on a solid
     is not pushed into it -- that is Pocket, which cuts. */
  function bimPushSketchTo(d,dist){
    var sk=d.snap0,i;
    if(d.f.on&&dist<0){
      var on=objById(d.f.on);
      return {ok:false,why:'This sketch is drawn on '+(on?on.name:'a solid')+' - Pocket, in the Sketch tools, cuts into it'};
    }
    var si=-1,pi=-1;
    for(i=0;i<A3D.objs.length;i++){if(A3D.objs[i].id===d.sketchId)si=i;if(A3D.objs[i].id===d.padId)pi=i;}
    if(Math.abs(dist)<1e-9){
      if(pi>=0){A3D.objs.splice(pi,1,JSON.parse(JSON.stringify(sk)));}
      else if(si<0)A3D.objs.splice(Math.min(Math.max(0,d.sketchAt),A3D.objs.length),0,JSON.parse(JSON.stringify(sk)));
      A3D.sel=d.sketchId;A3D.selSet=[d.sketchId];
      return {ok:true};
    }
    var P=sketchCCW(bimSketchOutline(sk));
    if(P.length<3)return {ok:false,why:'The sketch needs at least 3 points'};
    var mesh=padMesh(P,(sk.y||0)+Math.min(0,dist),Math.abs(dist));
    if(pi>=0)A3D.objs[pi].mesh=mesh;
    else{
      var pad={id:d.padId,t:'solid',name:d.padName,col:'#9db4c8',pos:bimObjOffset(sk),mesh:mesh};
      if(sk.layer)pad.layer=sk.layer;
      if(si>=0)A3D.objs.splice(si,1,pad);else A3D.objs.push(pad);
    }
    A3D.sel=d.padId;A3D.selSet=[d.padId];
    return {ok:true};
  }
  /* Enter, or the release: what depends on the object catches up once, and the face stays held
     where the push left it. */
  function bimPushEnd(d){
    var f=d.f,o;
    if(f.kind==='sketch'){
      o=objById(d.padId);
      if(o){
        A3D.counts.pad=(A3D.counts.pad||0)+1;
        a3dToast(o.name+' pulled from '+d.snap0.name+', '+bimFmtLen(Math.abs(d.dist))+(d.dist<0?' down':' up'));
      }
    }else{
      o=objById(d.id);
      /* a wall or column caught its openings, rooms and clones up on every frame of the push (its
         last frame is this state); cutting its openings again would cut an opening already cut */
      if(o&&f.kind!=='wallTop'&&f.kind!=='wallEnd'&&f.kind!=='colTop')bimPropagateFrom([o.id],'rebuild');
    }
    if(d.limit)a3dToast(d.limit);
    A3D.meshes={};   /* the drag's parameter frames are not worth keeping */
    bimFlushMaterialized();
    refreshTree();refreshProps();paint();saveSoon();
  }
  /* Escape: the object -- or the sketch -- exactly as the press found it, and the undo step the push
     took is given back. */
  function bimPushCancel(d,quiet){
    if(!d||!d.f)return false;
    if(d.f.kind==='sketch'){
      var i,pi=-1,si=-1;
      for(i=0;i<A3D.objs.length;i++){if(A3D.objs[i].id===d.padId)pi=i;if(A3D.objs[i].id===d.sketchId)si=i;}
      if(pi>=0)A3D.objs.splice(pi,1,JSON.parse(JSON.stringify(d.snap0)));
      else if(si<0)A3D.objs.splice(Math.min(Math.max(0,d.sketchAt),A3D.objs.length),0,JSON.parse(JSON.stringify(d.snap0)));
      A3D.sel=d.sketchId;A3D.selSet=[d.sketchId];
      A3D.face={id:d.sketchId,key:'region',N:[0,1,0],outward:true,seed:d.seed0.slice()};
    }else if(d.f.kind==='wallTop'||d.f.kind==='wallEnd'||d.f.kind==='colTop'){
      /* built again at nought, so its openings are cut once and what follows it catches up */
      bimPushApplyDist(d,0);
    }else{
      bimGizmoRestoreObjs([d.id],[d.snap0]);
      if(A3D.face&&d.f.kind==='solid')A3D.face.seed=d.seed0.slice();
    }
    if(d.undoAt&&UNDO_STACK.length===d.undoAt)UNDO_STACK.pop();
    if(!quiet)a3dToast('Cancelled');
    refreshTree();refreshProps();paint();saveSoon();
    return true;
  }
  /* The read-out while a face is pushed: its size as it is now, how far it has gone, what it landed on. */
  function bimPushReadout(d){
    var typed=bimGizmoTyping(),f=d.f;
    if(typed!==null)return 'DISTANCE  '+typed+'_ '+bimUnitLabel();
    var o=objById(f.kind==='sketch'?d.padId:d.id),size='';
    if(f.kind==='sketch')size='HEIGHT '+bimFmtLen(Math.abs(d.dist))+'  ';
    else if(o&&f.kind==='prm')size=f.dimName.toUpperCase()+' '+bimFmtLen(bimPrmDim(o,f.param))+'  ';
    else if(o&&(f.kind==='wallTop'||f.kind==='colTop'))size='HEIGHT '+bimFmtLen(o.bim.height)+'  ';
    else if(o&&f.kind==='wallEnd')size='LENGTH '+bimFmtLen(bimWallLength(o.bim.centerline,o.bim.closed,o.bim.bulges))+'  ';
    var s=size+(d.dist>=0?'+':'')+bimFmtLen(d.dist);
    if(d.snapLevel)s+='   '+String(d.snapLevel).toUpperCase();
    else if(d.snapAt)s+='   SNAP';
    if(d.limit)s+='   LIMIT';
    return s;
  }
  /* THE FACE'S VALUE BOX -- a click on the face or its arrow, or a digit typed while it is held. A
     named size takes the new size, as a Revit temporary dimension does; any other face takes how
     far to move, out along its arrow (a minus is in). Applied as one push, one undo step. */
  function bimFaceValueBox(prefill,cx,cy){
    var cur=bimFaceCurrent();
    if(!cur)return false;
    var f=cur.f;
    if(!f.ok){a3dToast(f.why);return false;}
    var named=!!(f.dimName&&f.dim!==null&&f.dim!==undefined);
    if(cx===undefined||cy===undefined){
      var fd=A3D.faceDraw,r=el.cv?el.cv.getBoundingClientRect():{left:0,top:0};
      var sp=fd?(fd.arrow?[fd.arrow.x1,fd.arrow.y1]:fd.c):[0,0];
      cx=r.left+sp[0];cy=r.top+sp[1];
    }
    bimValueBox({x:cx,y:cy,label:named?f.dimName:(f.kind==='sketch'?'Pull to a height':'Push or pull by'),
      unit:bimUnitLabel(),value:(prefill!==undefined&&prefill!==null)?prefill:(named?bimDispLen(f.dim):''),
      hint:named?('The new '+f.dimName.toLowerCase()+'; Enter to apply, Esc to cancel'):
        (f.kind==='sketch'?'Up is positive, down negative; Enter to apply':'Out along the arrow; a minus pushes in. Enter to apply'),
      submit:function(text){
        var p=bimGizmoParseValue('len',text);
        if(p.error)return p.error;
        var now=bimFaceCurrent();
        if(!now||now.o.id!==cur.o.id||now.f.key!==f.key)return 'The face has changed - take it again';
        var v=p.v[0],dist;
        if(named){
          if(!(v>0))return f.dimName+' has to be more than nought';
          dist=(v-now.f.dim)*(now.f.dsign||1);
        }else dist=v;
        return bimPushValue(dist);
      }});
    return true;
  }
  function bimPushValue(dist){
    var rec=bimPushPress([0,0],null);
    rec.moved=true;
    drag=rec;
    if(!bimPushBegin(rec,false)){drag=null;return 'This face cannot move now';}
    if(!bimPushTo(dist,true)){
      var why=rec.limit;
      bimPushCancel(rec,true);drag=null;
      return why||'That is further than this face can go';
    }
    drag=null;
    bimPushEnd(rec);
    return null;
  }
  /* a click on the held face asks for its value, once a double-click can no longer be under way */
  function bimFaceClickValue(rec){
    if(A3D_CLICKBOX_T)clearTimeout(A3D_CLICKBOX_T);
    A3D_CLICKBOX_T=setTimeout(function(){
      A3D_CLICKBOX_T=null;
      if(drag)return;
      bimFaceValueBox(null,rec.cx,rec.cy);
    },A3D_GIZ.clickWait);
  }
  function bimPickGrip(x,y){
    if(!A3D.grips)return null;
    var i,best=null,bestD=8;
    for(i=0;i<A3D.grips.length;i++){
      var g=A3D.grips[i];
      /* __acad3dV97: A3D.grips is whatever the LAST paint drew. After a selection change with
         no repaint in between, it still holds the previous object's grips, and a press there
         acted on an object that was no longer selected. Only the selection's grips are live. */
      if(g.kind==='grid'){   /* __acad3dV98: live only while that grid is the selection */
        var sgG=bimSelectedGrid();
        if(!sgG||sgG.id!==g.objId)continue;
      }else if(g.objId!==A3D.sel)continue;
      var dx=g.x-x,dy=g.y-y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<bestD){bestD=d;best=g;}
    }
    return best;
  }
