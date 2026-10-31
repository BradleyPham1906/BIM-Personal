  /* __acad3dV172: the site analysis tools, for the suite */
  window.__acad3dV172='grid,extent,raster,dt,buffer,distance,slopeclasses,exclusions,restricted,suitability,transforms,weights,locate,capacity,ratios,overlap,synthesis,history,rerun,pane,checks,layers,stale,wetlands,commands,phone';
  function bimTlArr(a){return a?Array.prototype.map.call(a,function(x){return typeof x==='number'&&!isFinite(x)?null:x;}):null;}
  window.__a3dTlGrid=function(){var G=bimTlGrid();return {x0:G.x0,z0:G.z0,cell:G.cell,nx:G.nx,nz:G.nz,n:G.n,lotArea:G.lotArea,ring:G.ring,lot:bimTlArr(G.lot),key:G.key,margin:BIM_TL_MARGIN};};
  window.__a3dTlSource=function(id){var s=bimTlSourceOf(bimTlGrid(),id);return s.why?{why:s.why}:{m:bimTlArr(s.m),v:bimTlArr(s.v),none:!!s.none,src:s.src||null};};
  window.__a3dTlDistance=function(mask){var G=bimTlGrid(),m=new Uint8Array(G.n),k,D;for(k=0;k<G.n;k++)m[k]=mask[k]?1:0;D=bimTlDistance(G,m);return bimTlArr(D);};
  window.__a3dTlDt1=function(f){var n=f.length,d=new Float64Array(n),v=new Int32Array(n),z=new Float64Array(n+1),F=new Float64Array(n),i;for(i=0;i<n;i++)F[i]=f[i]===null?BIM_TL_BIG:f[i];bimTlDt1(F,n,d,v,z);return bimTlArr(d);};
  window.__a3dTlFill=function(ring){var G=bimTlGrid(),m=new Uint8Array(G.n);bimTlFillPoly(G,ring,m,1);return bimTlArr(m);};
  window.__a3dTlStroke=function(a,b){var G=bimTlGrid(),m=new Uint8Array(G.n);bimTlStroke(G,a,b,m,1);return bimTlArr(m);};
  window.__a3dTlCode=function(lv){var e=bimTlEncode(lv),d={rc:e.rc,rn:e.rn,nx:lv.length,nz:1},back=bimTlDecode(d);return {rc:e.rc,rn:e.rn,back:bimTlArr(back),alph:BIM_TL_ALPH};};
  window.__a3dTlTools=function(){return bimTlOrder().map(function(t){return {id:t.id,name:t.name,cmd:t.cmd,sum:t.sum,how:t.how,params:t.params.map(function(p){return {id:p.id,label:p.label,t:p.t,req:!!p.req,unit:p.unit||'',of:p.of||null};})};});};
  window.__a3dTlParams=function(id,over){var t=bimTlTool(id);return t?JSON.parse(JSON.stringify(bimTlParams(t,over||undefined))):null;};
  window.__a3dTlCheck=function(id,over){var t=bimTlTool(id),G=bimTlGrid(),P=bimTlParams(t,over||undefined),C=bimTlCheck(t,P,G);return JSON.parse(JSON.stringify({E:C.E,W:C.W,err:C.err,first:C.first}));};
  window.__a3dTlSet=function(key,v){return bimTlSetField(key,v);};
  window.__a3dTlRun=function(id,over){var h=bimTlRun(id,over?{params:over,quiet:true}:{quiet:true});return h?JSON.parse(JSON.stringify(h)):null;};
  window.__a3dTlHistory=function(){return JSON.parse(JSON.stringify(bimTlState().history));};
  window.__a3dTlAct=function(a){return bimTlAct(String(a||''));};
  window.__a3dTlLayer=function(id){
    var R=bimResById(id),lv,d;
    if(!R)return null;
    d=R.data;lv=bimTlDecode(d);
    return {id:R.id,name:R.name,kind:R.kind,tool:R.tool||null,visible:R.visible!==false,run:R.run||null,stale:bimTlStale(R),opacity:bimResOpacity(R),
      data:{x0:d.x0,z0:d.z0,cell:d.cell,nx:d.nx,nz:d.nz,n:d.n,pal:d.pal,keys:d.keys,lo:d.lo===undefined?null:d.lo,hi:d.hi===undefined?null:d.hi,rest:d.rest,cats:d.cats,unit:d.unit,gkey:d.gkey},
      lv:bimTlArr(lv),vals:lv?Array.prototype.map.call(lv,function(q){return bimTlValue(d,q);}):null};
  };
  /* a criterion's transform, on given values: o its settings, xs the criterion's values, sc the scale */
  window.__a3dTlTransform=function(o,xs,sc,kind){
    var V=new Float64Array(xs.length),i,T;
    for(i=0;i<xs.length;i++)V[i]=xs[i]===null?NaN:xs[i];
    T=bimTlTransformOf(o,{name:'x',unit:'',kind:kind||'value'},V,sc||[1,10]);
    return {lo:T.lo===undefined?null:T.lo,hi:T.hi===undefined?null:T.hi,mid:T.mid===undefined?null:T.mid,spread:T.spread===undefined?null:T.spread,flat:!!T.flat,vals:T.vals||null,
      out:Array.prototype.map.call(V,function(x){var y=isFinite(x)?T.f(x):NaN;return isFinite(y)?y:null;})};
  };
  window.__a3dTlWetlands=function(){return new Promise(function(res){bimTlWetlandsFetch(function(ok){res({ok:ok,w:JSON.parse(JSON.stringify(bimTlState().wetlands||null))});});});};
  window.__a3dTlForgetGrid=function(){A3D_TL.grid=null;A3D_TL.gkey=null;A3D_TL.memo=null;return true;};
  window.__a3dTlGroundGrid=function(){var D=bimLandGround(bimDgSite());return D?{x0:D.x0,z0:D.z0,cell:D.cell,nx:D.nx,nz:D.nz}:null;};
