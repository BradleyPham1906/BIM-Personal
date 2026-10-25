  /* ================= __acad3dV126: section profiles ================= */
  var BIM_PROFILE_SHAPES={rect:'Rectangle',circle:'Round',hss:'Rectangular hollow (HSS)',pipe:'Pipe',ibeam:'I (W, IPE)',channel:'Channel'};
  var BIM_ROUND_N=32;
  /* Is a profile one this app can build and analyse? null when it is, the reason when not. */
  function bimProfileProblem(p){
    if(!p||!BIM_PROFILE_SHAPES[p.shape])return 'not a known section shape';
    var need={rect:['b','d'],circle:['D'],hss:['B','H','t'],pipe:['D','t'],ibeam:['d','bf','tf','tw'],channel:['d','bf','tf','tw']}[p.shape],i;
    for(i=0;i<need.length;i++)if(!(p[need[i]]>0))return 'its '+need[i]+' must be a positive length';
    if(p.shape==='hss'&&!(2*p.t<Math.min(p.B,p.H)))return 'its walls meet: 2t must be less than B and H';
    if(p.shape==='pipe'&&!(2*p.t<p.D))return 'its wall fills it: 2t must be less than D';
    if((p.shape==='ibeam'||p.shape==='channel')&&!(2*p.tf<p.d&&p.tw<p.bf))return 'its flanges or web do not fit its depth and width';
    return null;
  }
  /* The profile's centroidal properties, in m and m^4. y is its depth direction, z across it. */
  function bimProfileProps(p){
    var A,Iz,Iy,J,zc=0,PI=Math.PI;
    if(p.shape==='rect'){
      var s=bimRectSection(p.d,p.b);A=s.A;Iz=s.Iz;Iy=s.Iy;J=s.J;
    }else if(p.shape==='circle'){
      A=PI*p.D*p.D/4;Iz=Iy=PI*Math.pow(p.D,4)/64;J=PI*Math.pow(p.D,4)/32;
    }else if(p.shape==='pipe'){
      var di=p.D-2*p.t;
      A=PI*(p.D*p.D-di*di)/4;Iz=Iy=PI*(Math.pow(p.D,4)-Math.pow(di,4))/64;J=2*Iz;
    }else if(p.shape==='hss'){
      var bi=p.B-2*p.t,hi=p.H-2*p.t,Am=(p.B-p.t)*(p.H-p.t),per=2*((p.B-p.t)+(p.H-p.t));
      A=p.B*p.H-bi*hi;Iz=(p.B*p.H*p.H*p.H-bi*hi*hi*hi)/12;Iy=(p.H*p.B*p.B*p.B-hi*bi*bi*bi)/12;
      J=4*Am*Am*p.t/per;
    }else{
      var hw=p.d-2*p.tf;
      A=2*p.bf*p.tf+hw*p.tw;
      Iz=(p.bf*p.d*p.d*p.d-(p.bf-p.tw)*hw*hw*hw)/12;
      J=(2*p.bf*p.tf*p.tf*p.tf+hw*p.tw*p.tw*p.tw)/3;
      if(p.shape==='ibeam')Iy=(2*p.tf*p.bf*p.bf*p.bf+hw*p.tw*p.tw*p.tw)/12;
      else{
        /* the back of the channel at z = 0, its flanges running to z = bf */
        zc=(2*p.bf*p.tf*p.bf/2+hw*p.tw*p.tw/2)/A;
        Iy=2*(p.tf*p.bf*p.bf*p.bf/12+p.bf*p.tf*Math.pow(p.bf/2-zc,2))+(hw*p.tw*p.tw*p.tw/12+hw*p.tw*Math.pow(p.tw/2-zc,2));
      }
    }
    return {A:A,Iz:Iz,Iy:Iy,J:J,zc:zc};
  }
  /* The outline -- and the hole of a hollow section -- as [y, z] points about the centroid.
     A round is a 32-gon: its solid is that polygon, its properties the true circle's. */
  function bimProfileLoops(p){
    var out,inn=null,i,hd,hb;
    function ring(r){var a=[];for(var k=0;k<BIM_ROUND_N;k++){var th=2*Math.PI*k/BIM_ROUND_N;a.push([r*Math.cos(th),r*Math.sin(th)]);}return a;}
    if(p.shape==='rect'){hd=p.d/2;hb=p.b/2;out=[[-hd,-hb],[hd,-hb],[hd,hb],[-hd,hb]];}
    else if(p.shape==='circle')out=ring(p.D/2);
    else if(p.shape==='pipe'){out=ring(p.D/2);inn=ring(p.D/2-p.t);}
    else if(p.shape==='hss'){
      hd=p.H/2;hb=p.B/2;out=[[-hd,-hb],[hd,-hb],[hd,hb],[-hd,hb]];
      inn=[[-hd+p.t,-hb+p.t],[hd-p.t,-hb+p.t],[hd-p.t,hb-p.t],[-hd+p.t,hb-p.t]];
    }else if(p.shape==='ibeam'){
      var D2=p.d/2,B2=p.bf/2,W2=p.tw/2,F=D2-p.tf;
      out=[[-D2,-B2],[-D2,B2],[-F,B2],[-F,W2],[F,W2],[F,B2],[D2,B2],[D2,-B2],[F,-B2],[F,-W2],[-F,-W2],[-F,-B2]];
    }else{
      var zc=bimProfileProps(p).zc,C2=p.d/2,G=C2-p.tf;
      out=[[-C2,0],[-C2,p.bf],[-G,p.bf],[-G,p.tw],[G,p.tw],[G,p.bf],[C2,p.bf],[C2,0]].map(function(q){return [q[0],q[1]-zc];});
    }
    return {outer:out,inner:inn};
  }
  /* the profile's extent: its depth along y and width across z */
  function bimProfileExtent(p){
    var L=bimProfileLoops(p).outer,mn=[Infinity,Infinity],mx=[-Infinity,-Infinity],i;
    for(i=0;i<L.length;i++){mn[0]=Math.min(mn[0],L[i][0]);mn[1]=Math.min(mn[1],L[i][1]);mx[0]=Math.max(mx[0],L[i][0]);mx[1]=Math.max(mx[1],L[i][1]);}
    return {depth:mx[0]-mn[0],width:mx[1]-mn[1],ymax:mx[0]};
  }
  function bimLoopArea(L){var a=0,i;for(i=0;i<L.length;i++){var q=L[(i+1)%L.length];a+=L[i][0]*q[1]-q[0]*L[i][1];}return a/2;}
  /* Sweep a profile along a length: place(y, z, s) is the world point at (y, z) on the profile, s
     along the member. Closed, and turned outward by its signed volume. */
  function bimSweepMesh(p,len,place){
    var lp=bimProfileLoops(p),out=lp.outer.slice(),inn=lp.inner?lp.inner.slice():null,v=[],f=[],i,j,n,m;
    if(bimLoopArea(out)<0)out.reverse();
    if(inn&&bimLoopArea(inn)<0)inn.reverse();
    n=out.length;
    for(i=0;i<n;i++)v.push(place(out[i][0],out[i][1],0));
    for(i=0;i<n;i++)v.push(place(out[i][0],out[i][1],len));
    for(i=0;i<n;i++){j=(i+1)%n;f.push([i,j,j+n,i+n]);}
    if(inn){
      m=inn.length;var b=2*n;
      for(i=0;i<m;i++)v.push(place(inn[i][0],inn[i][1],0));
      for(i=0;i<m;i++)v.push(place(inn[i][0],inn[i][1],len));
      for(i=0;i<m;i++){j=(i+1)%m;f.push([b+j,b+i,b+i+m,b+j+m]);}
      /* the ends are rings, outer to inner vertex for vertex */
      for(i=0;i<n;i++){j=(i+1)%n;f.push([j,i,b+i,b+j]);f.push([i+n,j+n,b+j+m,b+i+m]);}
    }else{
      var tris=earClip(out);
      for(i=0;i<tris.length;i++){
        f.push([tris[i][2],tris[i][1],tris[i][0]]);
        f.push([tris[i][0]+n,tris[i][1]+n,tris[i][2]+n]);
      }
    }
    var mesh={v:v,f:f};
    if(bimMeshSignedVolume(mesh)<0)mesh.f=mesh.f.map(function(fc){return fc.slice().reverse();});
    return mesh;
  }
  function bimMeshSignedVolume(m){
    var V=0,i,k;
    for(i=0;i<m.f.length;i++){
      var fc=m.f[i],a=m.v[fc[0]];
      for(k=1;k+1<fc.length;k++){
        var b=m.v[fc[k]],c=m.v[fc[k+1]];
        V+=(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
      }
    }
    return V;
  }
  function bimBuildBeamGeometry(p1,p2,topY,w,dep,sec){
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    var L=Math.sqrt(dx*dx+dz*dz);
    if(!(L>1e-9))return {error:'Beam endpoints coincide'};
    /* __acad3dV126: a section, swept -- hung from the level by its top, its web upright */
    if(sec){
      var sp=bimProfileProblem(sec);
      if(sp)return {error:'The beam\'s section cannot be built: '+sp};
      var ex=bimProfileExtent(sec),ux=dx/L,uz=dz/L,ya=topY-ex.ymax;
      var sm=bimSweepMesh(sec,L,function(y,z,s){return [p1[0]+ux*s-uz*z,ya+y,p1[1]+uz*s+ux*z];});
      return {mesh:sm,length:L,
        bim:{type:'beam',p1:[p1[0],p1[1]],p2:[p2[0],p2[1]],width:ex.width,depth:ex.depth,
          baseY:topY-ex.depth,topY:topY,length:L,levelId:A3D.activeLevel,section:JSON.parse(JSON.stringify(sec))}};
    }
    if(!(w>0))return {error:'Beam width must be positive'};
    if(!(dep>0))return {error:'Beam depth must be positive'};
    var ux=dx/L,uz=dz/L,nx=-uz,nz=ux,hw=w/2;
    var yTop=topY,yBot=topY-dep;
    var aL=[p1[0]+nx*hw,p1[1]+nz*hw],aR=[p1[0]-nx*hw,p1[1]-nz*hw];
    var bL=[p2[0]+nx*hw,p2[1]+nz*hw],bR=[p2[0]-nx*hw,p2[1]-nz*hw];
    var v=[
      [aR[0],yBot,aR[1]],[aL[0],yBot,aL[1]],[bL[0],yBot,bL[1]],[bR[0],yBot,bR[1]],
      [aR[0],yTop,aR[1]],[aL[0],yTop,aL[1]],[bL[0],yTop,bL[1]],[bR[0],yTop,bR[1]]
    ];
    var f=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[1,2,6,5],[0,4,7,3]];
    var mesh={v:v,f:f};
    return {mesh:mesh,length:L,
      bim:{type:'beam',p1:[p1[0],p1[1]],p2:[p2[0],p2[1]],width:w,depth:dep,
        baseY:yBot,topY:yTop,length:L,levelId:A3D.activeLevel}};
  }
  function buildBeamSolid(p1,p2,topY,w,dep){
    var res=bimBuildBeamGeometry(p1,p2,topY,w,dep);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    A3D.counts.beam=(A3D.counts.beam||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Beam_'+A3D.counts.beam,
      col:'#9a9384',pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created \u2014 '+res.length.toFixed(2)+' m');
    return o;
  }
  function startBeamTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'beam',pts:[],y:lvl.elev,on:null};
    a3dToast('Beam: click the start and end of the beam on '+lvl.name);
    paint();
  }
  function openBeamDlg(p1,p2,topY){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    var L=Math.sqrt(dx*dx+dz*dz);
    d.innerHTML='<div class="a3d-dlghd">Beam parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Span</label><input type="text" value="'+L.toFixed(3)+' m" disabled></div>'+
      '<div class="a3d-dlgrow"><label>Width</label><input type="number" step="any" min="0.02" data-a3dp="bw" value="0.25"></div>'+
      '<div class="a3d-dlgrow"><label>Depth</label><input type="number" step="any" min="0.02" data-a3dp="bd" value="0.5"></div>'+
      '<div class="a3d-dlgrow"><label>Justification</label><select data-a3dp="bj">'+
        '<option value="top">Top at level</option>'+
        '<option value="center">Centred on level</option>'+
        '<option value="bottom">Bottom at level</option>'+
      '</select></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var wI=d.querySelector('[data-a3dp="bw"]'),dI=d.querySelector('[data-a3dp="bd"]'),jI=d.querySelector('[data-a3dp="bj"]');
    function submit(){
      var w=parseFloat(wI.value),dep=parseFloat(dI.value),just=jI.value;
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(w)||w<=0){eb.textContent='Width must be a positive number';return;}
      if(!isFinite(dep)||dep<=0){eb.textContent='Depth must be a positive number';return;}
      var top=topY;
      if(just==='center')top=topY+dep/2;
      else if(just==='bottom')top=topY+dep;
      closeDlg();
      buildBeamSolid(p1,p2,top,w,dep);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    wI.focus();wI.select();
  }
  function bimSegNormal(a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
    return [-dz/len,dx/len];
  }
  function bimOffsetRing(pts,dist,closed){
    var n=pts.length,out=[],i;
    for(i=0;i<n;i++){
      if(!closed&&(i===0||i===n-1)){
        var a=i===0?pts[0]:pts[n-2],b=i===0?pts[1]:pts[n-1];
        var nrm=bimSegNormal(a,b);
        out.push([pts[i][0]+nrm[0]*dist,pts[i][1]+nrm[1]*dist]);
        continue;
      }
      var prev=pts[(i-1+n)%n],cur=pts[i],next=pts[(i+1)%n];
      var n1=bimSegNormal(prev,cur),n2=bimSegNormal(cur,next);
      var mx=n1[0]+n2[0],mz=n1[1]+n2[1];
      var mlen=Math.sqrt(mx*mx+mz*mz)||1;mx/=mlen;mz/=mlen;
      var cosH=(n1[0]*mx+n1[1]*mz);
      var scale=cosH>0.15?1/cosH:1;scale=Math.min(scale,4);
      out.push([cur[0]+mx*dist*scale,cur[1]+mz*dist*scale]);
    }
    return out;
  }
