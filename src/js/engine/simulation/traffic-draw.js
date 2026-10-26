  /* ================= __acad3dV171: traffic and people around the site: drawn =================
     On the drawing's overlay while V170's clock plays or holds a moment, in plan and 3D, with the analysis's layer;
     between two steps each car and walker drawn where it is between them. In plan a car is a rectangle of the design
     car's size turned to its heading, a walker a dot, the lot's own in their own colour; anything too small to read
     is a dot. In 3D a car is V169's design car without its wheels (at Light, its box), a walker a column with a head,
     sorted by depth; drawn over the model, so a car behind a building shows through it (said). The stop lines show
     their signal. Never on a sheet, a print or an export. */
  var BIM_TR_COL={dk:{car:'#d6dde6',lot:'#ffb454',walk:'#7fd3e6',edge:'rgba(12,14,17,0.7)'},lt:{car:'#3b4450',lot:'#c25e00',walk:'#0b6e8a',edge:'rgba(255,255,255,0.85)'},
    g:'#2fbf71',y:'#f5c542',r:'#e5484d'};
  var A3D_TRD={mesh:null,box:null,body:null,drawn:{cars:0,walkers:0,dots:0,lines:0,faces:0}};
  /* the design car as V169 builds it, without its wheels; and its plain box for Light */
  function bimTrCarMesh(){
    if(!A3D_TRD.mesh){
      var V=bimEntVeh({v:'P'}),m=bimEntVehMesh(V,true);
      A3D_TRD.mesh={v:m.v.slice(2),f:m.f.map(function(fc){return fc.map(function(i){return i-2;});})};
      var b=mkBoxP(V.w,V.h,V.l);A3D_TRD.box={v:b.v.map(function(p){return [p[0],p[1]+V.h/2,p[2]];}),f:b.f};
      A3D_TRD.body=bimEntBody({who:'man',pose:'standing'});
    }
    return A3D_TRD;
  }
  function bimTrShown(){
    var D=bimDgState(),ly=bimLayerById(D.layers.traffic);
    return !ly||bimLayerEff(ly).on;
  }
  /* __acad3dV171b: the cars and walkers on Analyze's ground take its mode's colours, elsewhere the map's */
  function bimTrLight(){var L=bimAwLook();return L?L.light:bimMvLight();}
  function bimTrDraw(ctx,V,W,H){
    var R=A3D_TR.run,dw=A3D_TRD.drawn;
    dw.cars=0;dw.walkers=0;dw.dots=0;dw.lines=0;dw.faces=0;
    if(!R||!bimAnimLive()||!bimTrShown())return;
    var K=bimTrLight()?BIM_TR_COL.lt:BIM_TR_COL.dk,f=Math.max(0,Math.min(1,R.acc/R.step)),y=R.y||0;
    ctx.save();
    try{
      bimTrDrawSignals(ctx,V,W,H,R,y);
      if(bimCameraIsPlan())bimTrDrawPlan(ctx,V,W,H,R,K,f,y);
      else bimTrDraw3D(ctx,V,W,H,R,K,f,y);
    }finally{ctx.restore();}
  }
  /* the stop lines of each signalled approach, across its lanes, in its signal's colour */
  function bimTrDrawSignals(ctx,V,W,H,R,y){
    var N=R.N,o={},a=[0,0,0,0];
    ctx.lineWidth=3;ctx.lineCap='butt';
    Object.keys(R.plans).forEach(function(ji){
      var P=R.plans[ji],j=N.J[ji];
      j.ins.forEach(function(l){
        var Lk=N.links[l];if(!P.of.hasOwnProperty(l))return;
        bimTrSig(P,P.of[l],R.t,o);
        bimTrAt(Lk.P,Lk.C,bimTrStopLine(N,Lk),a);
        var w=Lk.ow?Lk.w:Lk.w/2,x0=a[0],z0=a[1],rx=-a[3],rz=a[2],e0=Lk.ow?-Lk.w/2:0;
        var p=toScreen([x0+rx*e0,y+0.05,z0+rz*e0],V,W,H),q=toScreen([x0+rx*(e0+w),y+0.05,z0+rz*(e0+w)],V,W,H);
        if(p[2]<=0.5||q[2]<=0.5)return;
        ctx.strokeStyle=BIM_TR_COL[o.s];ctx.beginPath();ctx.moveTo(p[0],p[1]);ctx.lineTo(q[0],q[1]);ctx.stroke();
        A3D_TRD.drawn.lines++;
      });
    });
  }
  function bimTrDrawPlan(ctx,V,W,H,R,K,f,y){
    var C=R.c,Wk=R.w,dw=A3D_TRD.drawn,L=bimStd('aashto.vehicles','P_l'),Wc=bimStd('aashto.vehicles','P_w'),c,i;
    var p0=toScreen([0,y,0],V,W,H),p1=toScreen([1,y,0],V,W,H),k=Math.sqrt((p1[0]-p0[0])*(p1[0]-p0[0])+(p1[1]-p0[1])*(p1[1]-p0[1]));   /* pixels a metre */
    ctx.lineWidth=1;ctx.strokeStyle=K.edge;
    for(c=0;c<C.n;c++){
      if(C.L[c]<0)continue;
      var x=C.px[c]+(C.x[c]-C.px[c])*f,z=C.pz[c]+(C.z[c]-C.pz[c])*f,s=toScreen([x,y+0.1,z],V,W,H);
      ctx.fillStyle=C.k[c]?K.lot:K.car;
      if(L*k<3){ctx.beginPath();ctx.arc(s[0],s[1],1.5,0,Math.PI*2);ctx.fill();dw.dots++;dw.cars++;continue;}
      var hx=C.hx[c],hz=C.hz[c],rx=-hz,rz=hx,P=[[L/2,Wc/2],[L/2,-Wc/2],[-L/2,-Wc/2],[-L/2,Wc/2]];
      ctx.beginPath();
      for(i=0;i<4;i++){var q=toScreen([x+hx*P[i][0]+rx*P[i][1],y+0.1,z+hz*P[i][0]+rz*P[i][1]],V,W,H);if(i)ctx.lineTo(q[0],q[1]);else ctx.moveTo(q[0],q[1]);}
      ctx.closePath();ctx.fill();ctx.stroke();dw.cars++;
    }
    var rw=Math.max(1.6,0.3*k);
    ctx.fillStyle=K.walk;
    for(i=0;i<Wk.n;i++){
      if(Wk.R[i]<0)continue;
      var wx=Wk.px[i]+(Wk.x[i]-Wk.px[i])*f,wz=Wk.pz[i]+(Wk.z[i]-Wk.pz[i])*f,ws=toScreen([wx,y+0.1,wz],V,W,H);
      ctx.beginPath();ctx.arc(ws[0],ws[1],rw,0,Math.PI*2);ctx.fill();dw.walkers++;if(rw<=1.6)dw.dots++;
    }
  }
  /* 3D: every car's faces and every walker, far to near */
  function bimTrDraw3D(ctx,V,W,H,R,K,f,y){
    var C=R.c,Wk=R.w,dw=A3D_TRD.drawn,M=bimTrCarMesh(),det=R.cap.detail,items=[],c,i,k;
    for(c=0;c<C.n;c++){
      if(C.L[c]<0)continue;
      var x=C.px[c]+(C.x[c]-C.px[c])*f,z=C.pz[c]+(C.z[c]-C.pz[c])*f,s=toScreen([x,y,z],V,W,H);
      if(s[2]<=0.5||s[0]<-50||s[0]>W+50||s[1]<-50||s[1]>H+50)continue;
      items.push({t:0,i:c,x:x,z:z,d:s[2],s:s});
    }
    for(i=0;i<Wk.n;i++){
      if(Wk.R[i]<0)continue;
      var wx=Wk.px[i]+(Wk.x[i]-Wk.px[i])*f,wz=Wk.pz[i]+(Wk.z[i]-Wk.pz[i])*f,ws=toScreen([wx,y,wz],V,W,H);
      if(ws[2]<=0.5||ws[0]<-20||ws[0]>W+20||ws[1]<-20||ws[1]>H+20)continue;
      items.push({t:1,i:i,x:wx,z:wz,d:ws[2],s:ws});
    }
    items.sort(function(p,q){return q.d-p.d;});
    var hgt=M.body.st;
    items.forEach(function(it){
      if(it.t===1){
        var top=toScreen([it.x,y+hgt,it.z],V,W,H),hp=Math.abs(top[1]-it.s[1]);
        ctx.fillStyle=K.walk;ctx.strokeStyle=K.walk;
        if(hp<6){ctx.beginPath();ctx.arc(it.s[0],it.s[1],1.6,0,Math.PI*2);ctx.fill();dw.dots++;dw.walkers++;return;}
        ctx.lineWidth=Math.max(1.5,hp*0.16);ctx.lineCap='round';
        ctx.beginPath();ctx.moveTo(it.s[0],it.s[1]);ctx.lineTo(top[0],top[1]+hp*0.16);ctx.stroke();
        ctx.beginPath();ctx.arc(top[0],top[1]+hp*0.08,Math.max(1.5,hp*0.09),0,Math.PI*2);ctx.fill();
        dw.walkers++;return;
      }
      var cc=it.i,hx=C.hx[cc],hz=C.hz[cc],rx=-hz,rz=hx,col=C.k[cc]?K.lot:K.car;
      var sz=toScreen([it.x+hx*2.9,y,it.z+hz*2.9],V,W,H),pl=Math.abs(sz[0]-it.s[0])+Math.abs(sz[1]-it.s[1]);
      if(pl<3){ctx.fillStyle=col;ctx.beginPath();ctx.arc(it.s[0],it.s[1],1.6,0,Math.PI*2);ctx.fill();dw.dots++;dw.cars++;return;}
      var m=det?M.mesh:M.box,P=[],Wp=[];
      for(k=0;k<m.v.length;k++){var v=m.v[k],wp=[it.x+rx*v[0]+hx*v[2],y+v[1],it.z+rz*v[0]+hz*v[2]];Wp.push(wp);P.push(toScreen(wp,V,W,H));}
      var F=[];
      m.f.forEach(function(fc){
        var a=Wp[fc[0]],b=Wp[fc[1]],c2=Wp[fc[2]],n=vnorm(vcross(vsub(b,a),vsub(c2,a))),zz=0;   /* every face, far to near: a box needs no culling */
        fc.forEach(function(q){zz+=P[q][2];});F.push({fc:fc,z:zz/fc.length,n:n});
      });
      F.sort(function(p,q){return q.z-p.z;});
      ctx.lineWidth=0.6;ctx.strokeStyle='rgba(0,0,0,0.35)';
      F.forEach(function(o){
        ctx.beginPath();o.fc.forEach(function(q,j){if(j)ctx.lineTo(P[q][0],P[q][1]);else ctx.moveTo(P[q][0],P[q][1]);});ctx.closePath();
        ctx.fillStyle=shade(col,0.45+0.55*Math.abs(vdot(o.n,LIGHT)));ctx.fill();ctx.stroke();dw.faces++;
      });
      dw.cars++;
    });
  }
