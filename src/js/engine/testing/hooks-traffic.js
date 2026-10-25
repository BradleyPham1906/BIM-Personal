  /* __acad3dV171: traffic and people around the site, for the suite: the run driven step by step, read as data */
  window.__acad3dV171='trafficrecords,network,lanes,widthkept,junctions,priority,stops,signals,webster,kellfullerton,leastgreens,demand,fdotk,furness,sandiego,'+
    'lotentry,doors,carparks,walkers,sidewalks,crossings,idm,mobil,amber,allstop,yield,walkcross,pools,warmup,tallies,draw2d,draw3d,stoplines,analysis,card,command,results,quality';
  function bimTrArr(a){return Array.prototype.slice.call(a);}
  function bimTrSummary(R){
    if(!R)return null;
    var plans={};
    Object.keys(R.plans).forEach(function(k){var P=R.plans[k];plans[k]={C:P.C,C0:isFinite(P.C0)?P.C0:null,Y:P.Y,L:P.L,grown:P.grown,axis:P.axis,of:P.of,armPh:P.armPh,
      ph:P.ph.map(function(o){return {G:o.G,Y:o.Y,AR:o.AR,y:o.y,gmin:o.gmin,gped:o.gped,gdrv:o.gdrv,arms:o.arms,ins:o.ins,t0:o.t0};})};});
    var res=R.res;
    return {t:R.t,steps:R.steps,warm:R.warm,warmMs:R.warmMs,qk:R.qk,cap:R.cap.name,step:R.step,cars:R.c.na,walkers:R.w.na,plans:plans,trips:R.trips,share:R.share,lotOk:R.lotOk,
      lot:R.N.lot,notes:R.N.notes,sigOff:R.N.sigOff,lanesCapped:R.N.lanesCapped,sw:R.N.sw,srcs:R.srcs.map(function(s){return {l:s.l,q:s.q,pend:s.pend};}),sinks:R.sinks.map(function(s){return {l:s.l,q:s.q};}),
      park:R.park.map(function(p){return {n:p.n,x:p.x,z:p.z,name:p.name,lot:!!p.lot};}),routes:R.routes.length,allocs:A3D_TR.allocs,acres:R.acres,uses:R.uses,
      stops:R.stops,edgeW:R.edgeW,lotQ:(R.lotQ||[]).length,
      res:{t0:res.t0,spawned:res.spawned,exited:res.exited,lotIn:res.lotIn,lotOut:res.lotOut,blocked:res.blocked,red:res.red,redAt:res.redAt,walkBad:res.walkBad,lc:res.lc,carsCap:res.carsCap,walkCap:res.walkCap,
        doors:res.doors,q:res.q,del:bimTrArr(res.del),cw:bimTrArr(res.cw)}};
  }
  window.__a3dTrStart=function(){bimTrStop();var R=bimTrStart();return R?bimTrSummary(R):{err:'not started'};};
  window.__a3dTrStop=function(){bimTrStop();return true;};
  window.__a3dTrSteps=function(n){var R=A3D_TR.run,i;if(!R)return null;for(i=0;i<n;i++)bimTrStep(R);return bimTrSummary(R);};
  window.__a3dTrSummary=function(){return bimTrSummary(A3D_TR.run);};
  /* n steps, watched: each step, the walkers on each junction's crossings and the cars standing on each link, summed */
  window.__a3dTrWatch=function(n){
    var R=A3D_TR.run,i,c,k;if(!R)return null;
    var occ=new Float64Array(R.nArms),st=new Float64Array(R.N.links.length),C=R.c;
    for(i=0;i<n;i++){bimTrStep(R);for(k=0;k<R.nArms;k++)if(R.occ[k]>0)occ[k]++;for(c=0;c<C.n;c++)if(C.L[c]>=0&&C.v[c]<0.5)st[C.L[c]]++;}
    var o={occ:{},st:{}};
    R.N.J.forEach(function(j){j.arms.forEach(function(a,ai){var v=occ[j.armBase+ai];if(v)o.occ[j.i+':'+ai]=v*R.step;});});
    for(k=0;k<st.length;k++)if(st[k])o.st[k]=st[k]*R.step/(n*R.step);
    return o;
  };
  window.__a3dTrNet=function(){
    var N=A3D_TR.run?A3D_TR.run.N:null;
    if(!N){N=bimTrNet();if(N.err)return {err:N.err};bimTrDemand(N);}
    return {R:N.R,lot:N.lot,doors:N.doors,notes:N.notes,sigOff:N.sigOff,lanesCapped:N.lanesCapped,sw:N.sw,x:N.x,z:N.z,
      edges:N.edges.map(function(e){return {a:e.a,b:e.b,len:e.len,car:e.car,hw:bimTrHw(e.t),name:String(e.t.name||''),w:e.w,lanes:e.lanes,sw:e.sw,lot:!!e.lot,way:e.way,P:e.P};}),
      links:N.links.map(function(l){return {i:l.i,e:l.e,a:l.a,b:l.b,len:l.len,lanes:l.lanes,v0:l.v0,w:l.w,ow:l.ow,q:l.q,base:l.base,name:l.name,rank:l.rank,rev:l.rev,jb:l.jb,ja:l.ja,arm:l.arm,armOut:l.armOut,lot:l.lot};}),
      J:N.J.map(function(j){var tr={};Object.keys(j.tr).forEach(function(k){tr[k]=j.tr[k].map(function(t){return [t.o,t.p,t.ang,!!t.u];});});
        return {i:j.i,n:j.n,x:j.x,z:j.z,kind:j.kind,sig:j.sig,ins:j.ins,outs:j.outs,major:Object.keys(j.major).map(Number),stop:Object.keys(j.stop).map(Number),tie:!!j.tie,tr:tr,bnd:j.bnd,lot:j.lot,cw:j.cw,
          arms:j.arms.map(function(a){return {k:a.k,e:a.e,bear:a.bear,w:a.w,car:a.car,lin:a.lin,lout:a.lout,end:a.end};})};})};
  };
  window.__a3dTrCars=function(){var R=A3D_TR.run,C,o=[],c;if(!R)return [];C=R.c;for(c=0;c<C.n;c++)if(C.L[c]>=0)o.push([c,C.L[c],C.ln[c],C.s[c],C.v[c],C.k[c],C.tg[c],C.x[c],C.z[c],C.hx[c],C.hz[c],C.nx[c]]);return o;};
  window.__a3dTrWalkers=function(){var R=A3D_TR.run,W,o=[],i;if(!R)return [];W=R.w;for(i=0;i<W.n;i++)if(W.R[i]>=0)o.push([i,W.R[i],W.p[i],W.v[i],W.x[i],W.z[i],W.cr[i],W.wait[i]]);return o;};
  window.__a3dTrRoutes=function(){var R=A3D_TR.run;if(!R)return [];return R.routes.map(function(r){return {kind:r.kind,door:r.door,extra:r.extra,len:r.len,P:r.P,cr:r.cr};});};
  /* the cars on a link, front first, and what holds each: [car, lane, s, v, a, leader, next link, hold] */
  window.__a3dTrOnLink=function(l){
    var R=A3D_TR.run,C,o=[],c;if(!R)return [];C=R.c;
    for(c=0;c<C.n;c++)if(C.L[c]===l)o.push([c,C.ln[c],C.s[c],C.v[c],C.a[c],C.lead[c],C.nx[c],bimTrHold(R,c)]);
    o.sort(function(p,q){return q[2]-p[2];});
    return o;
  };
  window.__a3dTrIdm=function(v,v0,s,dv){return bimTrIdm(v,v0,s,dv,bimTrIdmP());};
  window.__a3dTrFurness=function(qi,qo,ok,n){return bimTrFurness(qi,qo,ok,n);};
  window.__a3dTrTrips=function(rows,acres,peak){return bimTrTripsOf(rows,acres,peak);};
  window.__a3dTrUses=function(){return bimTrUses();};
  window.__a3dTrPlanOf=function(ap,arms){var P=bimTrPlanOf(ap,arms);if(P&&!isFinite(P.C0))P.C0=null;return P;};
  window.__a3dTrSigAt=function(ji,t){var R=A3D_TR.run,P=R&&R.plans[ji],o={};if(!P)return null;return P.ph.map(function(x,k){bimTrSig(P,k,t,o);return [o.s,o.left];});};
  window.__a3dTrResults=function(){return A3D_TR.run?bimTrResults(A3D_TR.run):A3D_TR.last;};
  window.__a3dTrDrawn=function(){return JSON.parse(JSON.stringify(A3D_TRD.drawn));};
  window.__a3dTrSettings=function(){return bimTrSettings();};
  window.__a3dTrAct=function(v){return bimTrAct(v);};
  window.__a3dTrDeviceQ=function(){return bimTrDeviceQ();};
  /* the pools' bytes, and how many times they were allocated */
  window.__a3dTrPools=function(){
    var R=A3D_TR.run,b=0;if(!R)return {allocs:A3D_TR.allocs,bytes:0};
    [R.c,R.w].forEach(function(o){Object.keys(o).forEach(function(k){if(o[k]&&o[k].BYTES_PER_ELEMENT)b+=o[k].byteLength;});});
    b+=R.occ.byteLength+R.occH.byteLength+R.busy.byteLength;
    return {allocs:A3D_TR.allocs,bytes:b,cars:R.c.n,walkers:R.w.n};
  };
  /* a leader held at a speed and a follower behind it on a straight one-lane road, run by the simulation's own step
     functions (the sort, the IDM's acceleration, the move): the follower's gap and speed each second */
  window.__a3dTrPlatoon=function(o){
    var len=50000,v0=o.v0,P=[[0,0],[len,0]],al=A3D_TR.allocs;
    var N={L:{ring:null,pt:[0,0]},x:[0,len],z:[0,0],edges:[],doors:[],lot:null,notes:[],
      links:[{i:0,e:0,a:0,b:1,P:P,C:[0,len],len:len,lanes:1,v0:v0,w:3.3,ow:true,rank:1,hw:'residential',base:'residential',q:0,rev:-1,jb:1,ja:0,arm:0,armOut:0,slot:0}],
      J:[{i:0,n:0,arms:[{k:0}],ins:[],outs:[0],bnd:true,kind:'pass',tr:{},armBase:0,cw:0,x:0,z:0,stop:{},major:{}},{i:1,n:1,arms:[{k:0}],ins:[0],outs:[],bnd:true,kind:'pass',tr:{0:[]},armBase:1,cw:0,x:len,z:0,stop:{},major:{}}]};
    var R={N:N,set:{speed:1},Q:{cars:4,walk:1},cap:{cars:4,walk:1},rng:bimTrRng(1),P:bimTrIdmP(),t:0,acc:0,step:o.step||bimStd('app.traffic','step'),plans:{},targets:[],routes:[],srcs:[],sinks:[],
      nSlots:1,nArms:2,lotOk:false,park:[],rIn:[],rOut:[],rTin:[],rTout:[],rWin:[],rWout:[],steps:0,y:0};
    bimTrAlloc(R);A3D_TR.allocs=al;
    var C=R.c,mk=function(s,v){var c=C.free[--C.nf];C.na++;C.L[c]=0;C.ln[c]=0;C.s[c]=s;C.v[c]=v;C.len[c]=bimStd('aashto.vehicles','P_l');C.k[c]=0;C.tg[c]=-1;C.nx[c]=-1;C.t0[c]=0;C.ta[c]=0;C.st[c]=0;C.lc[c]=-99;bimTrPlace(R,c);return c;};
    var L=mk(o.s0+o.gap+bimStd('aashto.vehicles','P_l'),o.vl),F=mk(o.s0,o.vf),out=[],n=Math.round(o.secs/R.step),i,per=Math.max(1,Math.round(1/R.step));
    for(i=0;i<n;i++){
      bimTrSortCars(R);
      C.a[F]=bimTrAccOf(R,F);C.a[L]=0;
      bimTrMove(R,F,R.step);bimTrMove(R,L,R.step);
      R.t+=R.step;
      if((i+1)%per===0)out.push([R.t,C.s[L]-C.len[L]-C.s[F],C.v[F]]);
    }
    return out;
  };
