/* Phase 42 beam kernel prototype. Mirrors the in-app ES5 style exactly. */
function beamMesh(p1,p2,topY,w,dep){
  var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
  var L=Math.sqrt(dx*dx+dz*dz);
  if(!(L>1e-9))return null;
  var ux=dx/L,uz=dz/L;      /* axis unit */
  var nx=-uz,nz=ux;         /* left normal in plan */
  var hw=w/2;
  var yTop=topY,yBot=topY-dep;
  /* Cross-section corners in plan at each end: left/right of the axis */
  var aL=[p1[0]+nx*hw,p1[1]+nz*hw],aR=[p1[0]-nx*hw,p1[1]-nz*hw];
  var bL=[p2[0]+nx*hw,p2[1]+nz*hw],bR=[p2[0]-nx*hw,p2[1]-nz*hw];
  var v=[
    [aR[0],yBot,aR[1]],[aL[0],yBot,aL[1]],[bL[0],yBot,bL[1]],[bR[0],yBot,bR[1]], /* 0-3 bottom */
    [aR[0],yTop,aR[1]],[aL[0],yTop,aL[1]],[bL[0],yTop,bL[1]],[bR[0],yTop,bR[1]]  /* 4-7 top   */
  ];
  var f=[
    [0,3,2,1], /* bottom, faces -Y */
    [4,5,6,7], /* top, faces +Y */
    [0,1,5,4], /* start cap */
    [3,7,6,2], /* end cap */
    [1,2,6,5], /* left side */
    [0,4,7,3]  /* right side */
  ];
  return {v:v,f:f};
}
function topo(m){
  var und={},dir={},dup=0,bad=0,vol=0,i,k;
  m.f.forEach(function(f){
    for(i=0;i<f.length;i++){
      var a=f[i],b=f[(i+1)%f.length];
      if(a===b)bad++;
      var uk=Math.min(a,b)+'-'+Math.max(a,b);
      und[uk]=(und[uk]||0)+1;
      var dk=a+'>'+b; dir[dk]=(dir[dk]||0)+1;
    }
    for(i=1;i+1<f.length;i++){
      var A=m.v[f[0]],B=m.v[f[i]],C=m.v[f[i+1]];
      vol+=(A[0]*(B[1]*C[2]-B[2]*C[1])-A[1]*(B[0]*C[2]-B[2]*C[0])+A[2]*(B[0]*C[1]-B[1]*C[0]))/6;
    }
  });
  for(k in dir)if(dir[k]>1)dup++;
  for(k in und)if(und[k]!==2)bad++;
  return {dup:dup,bad:bad,vol:vol};
}
module.exports={beamMesh:beamMesh,topo:topo};
