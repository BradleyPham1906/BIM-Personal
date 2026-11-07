/* V172c experiment: an any-hit ray test over a bounding-volume hierarchy of triangles, ES5, typed arrays.
   The same Moller-Trumbore test and thresholds as the app's bimRayTri (det 1e-12, t > 1e-6). Built by median split
   on the longest axis of the centroids' box, leaves of up to 4 triangles. */
function bimBvhBuild(tris){
  var n=tris.length,T=new Float64Array(n*9),C=new Float64Array(n*3),idx=new Int32Array(n),i,k;
  for(i=0;i<n;i++){for(k=0;k<3;k++){T[i*9+k]=tris[i][0][k];T[i*9+3+k]=tris[i][1][k];T[i*9+6+k]=tris[i][2][k];
    C[i*3+k]=(tris[i][0][k]+tris[i][1][k]+tris[i][2][k])/3;}idx[i]=i;}
  var B=[],L=[],R=[],S=[],N=[];   /* per node: box (6), left, right, first, count */
  function node(a,b){
    var id=N.length,bx=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity],cb=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity],j,q,t;
    N.push(0);L.push(-1);R.push(-1);S.push(a);
    for(j=a;j<b;j++){t=idx[j];for(q=0;q<9;q++){var v=T[t*9+q],ax=q%3;if(v<bx[ax])bx[ax]=v;if(v>bx[ax+3])bx[ax+3]=v;}
      for(q=0;q<3;q++){if(C[t*3+q]<cb[q])cb[q]=C[t*3+q];if(C[t*3+q]>cb[q+3])cb[q+3]=C[t*3+q];}}
    for(q=0;q<6;q++)B[id*6+q]=bx[q];
    if(b-a<=4){N[id]=b-a;return id;}
    var ax2=0,ex=cb[3]-cb[0];if(cb[4]-cb[1]>ex){ax2=1;ex=cb[4]-cb[1];}if(cb[5]-cb[2]>ex)ax2=2;
    var part=Array.prototype.slice.call(idx.subarray(a,b));
    part.sort(function(u,v){return C[u*3+ax2]-C[v*3+ax2];});
    for(j=0;j<part.length;j++)idx[a+j]=part[j];
    var m=(a+b)>>1;
    var l=node(a,m),r=node(m,b);L[id]=l;R[id]=r;return id;
  }
  if(n)node(0,n);
  return {T:T,idx:idx,B:new Float64Array(B),L:new Int32Array(L),R:new Int32Array(R),S:new Int32Array(S),N:new Int32Array(N),stack:new Int32Array(128)};
}
function bimBvhBlocked(H,o,d){
  if(!H.N.length)return false;
  var st=H.stack,sp=0,B=H.B,T=H.T,id,k,t0,t1,a,c,inv,j,tr,
      ix=Math.abs(d[0])<1e-12?0:1/d[0],iy=Math.abs(d[1])<1e-12?0:1/d[1],iz=Math.abs(d[2])<1e-12?0:1/d[2];
  st[sp++]=0;
  while(sp){
    id=st[--sp];t0=0;t1=Infinity;var miss=false,q=id*6;
    for(k=0;k<3&&!miss;k++){
      var dk=k===0?d[0]:k===1?d[1]:d[2],ok=o[k],iv=k===0?ix:k===1?iy:iz;
      if(Math.abs(dk)<1e-12){if(ok<B[q+k]||ok>B[q+k+3])miss=true;continue;}
      a=(B[q+k]-ok)*iv;c=(B[q+k+3]-ok)*iv;if(a>c){var tt=a;a=c;c=tt;}
      if(a>t0)t0=a;if(c<t1)t1=c;if(t0>t1)miss=true;
    }
    if(miss)continue;
    if(H.L[id]<0){
      for(j=H.S[id];j<H.S[id]+H.N[id];j++){
        tr=H.idx[j]*9;
        var e1x=T[tr+3]-T[tr],e1y=T[tr+4]-T[tr+1],e1z=T[tr+5]-T[tr+2],e2x=T[tr+6]-T[tr],e2y=T[tr+7]-T[tr+1],e2z=T[tr+8]-T[tr+2];
        var px=d[1]*e2z-d[2]*e2y,py=d[2]*e2x-d[0]*e2z,pz=d[0]*e2y-d[1]*e2x,det=e1x*px+e1y*py+e1z*pz;
        if(Math.abs(det)<1e-12)continue;
        var id2=1/det,sx=o[0]-T[tr],sy=o[1]-T[tr+1],sz=o[2]-T[tr+2],u=(sx*px+sy*py+sz*pz)*id2;
        if(u<0||u>1)continue;
        var qx=sy*e1z-sz*e1y,qy=sz*e1x-sx*e1z,qz=sx*e1y-sy*e1x,v=(d[0]*qx+d[1]*qy+d[2]*qz)*id2;
        if(v<0||u+v>1)continue;
        if((e2x*qx+e2y*qy+e2z*qz)*id2>1e-6)return true;
      }
    }else{st[sp++]=H.L[id];st[sp++]=H.R[id];}
  }
  return false;
}
if(typeof module!=="undefined"&&module)module.exports={build:bimBvhBuild,blocked:bimBvhBlocked};
