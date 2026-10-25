  /* ================= __acad3dV171: traffic and people around the site: the walkers' ways =================
     reference/research-traffic.md, section 8. Walkers keep to the sidewalks of the streets they follow, each side a
     line beyond the roadway's edge, and to footways and paths along their line. At a junction they cross what lies
     between their way in and their way out, the short way round: each arm of the junction has a crossing this far from
     its middle (the junction's crossings), its two ends on the arm's two sidewalks. A way is a polyline, with the
     crossings marked on it; the ways are worked out once a run, between where people come from and the doors. */
  /* a point of an arm: its crossing's end on one side (sg +1 the side clockwise of it, -1 the other) */
  function bimTrArmPt(N,j,a,sg,out){
    var r=a.bear*Math.PI/180,dx=Math.sin(r),dz=-Math.cos(r),off=a.car?a.w/2+bimStd('app.traffic','sw_off'):0;
    out[0]=j.x+dx*j.cw+(-dz)*sg*off;out[1]=j.z+dz*j.cw+dx*sg*off;
    return out;
  }
  /* the nearest point of the walkable edges to a point: the edge, the distance along it, the point */
  function bimTrSnap(N,x,z){
    var best=null,bd=Infinity,i,q;
    for(i=0;i<N.edges.length;i++){
      var e=N.edges[i];
      if(!e.car&&!bimTrFootWay(e.t))continue;
      if(e.car&&!e.sw.l&&!e.sw.r&&!e.lot)continue;
      for(q=1;q<e.P.length;q++){
        var ax=e.P[q-1][0],az=e.P[q-1][1],dx=e.P[q][0]-ax,dz=e.P[q][1]-az,l2=dx*dx+dz*dz,u=l2>1e-12?((x-ax)*dx+(z-az)*dz)/l2:0;u=Math.max(0,Math.min(1,u));
        var px=ax+u*dx,pz=az+u*dz,d2=(px-x)*(px-x)+(pz-z)*(pz-z);
        if(d2<bd){bd=d2;best={e:i,s:e.C[q-1]+u*Math.sqrt(l2),x:px,z:pz,d:0};}
      }
    }
    if(best)best.d=Math.sqrt(bd);
    return best;
  }
  /* the walk: Dijkstra over the edges' ends, a street with no sidewalk three times as long (walked at its edge) */
  function bimTrWalkPath(N,o,d){
    if(o.e===d.e)return [{e:o.e,s0:o.s,s1:d.s}];
    var adj={},D={},P={},hk=[],hv=[],i;
    N.edges.forEach(function(e,ei){
      if(!e.car&&!bimTrFootWay(e.t))return;
      var c=e.len*(e.car&&!e.sw.l&&!e.sw.r?3:1);
      (adj[e.a]||(adj[e.a]=[])).push([e.b,c,ei]);(adj[e.b]||(adj[e.b]=[])).push([e.a,c,ei]);
    });
    function push(k,v){var q=hk.length;hk.push(k);hv.push(v);while(q>0){var p=(q-1)>>1;if(hk[p]<=k)break;hk[q]=hk[p];hv[q]=hv[p];q=p;}hk[q]=k;hv[q]=v;}
    function pop(){var lk=hk.pop(),lv=hv.pop(),m=hk.length,q=0;if(!m)return;for(;;){var l=2*q+1,r=l+1,s=-1,sk=lk;if(l<m&&hk[l]<sk){s=l;sk=hk[l];}if(r<m&&hk[r]<sk){s=r;sk=hk[r];}if(s<0)break;hk[q]=hk[s];hv[q]=hv[s];q=s;}hk[q]=lk;hv[q]=lv;}
    var eo=N.edges[o.e],ed=N.edges[d.e];
    D[eo.a]=o.s;P[eo.a]=null;push(o.s,eo.a);
    if(!(eo.b in D)||eo.len-o.s<D[eo.b]){D[eo.b]=eo.len-o.s;P[eo.b]=null;push(eo.len-o.s,eo.b);}
    var goal=null,gd=Infinity;
    while(hk.length){
      var t=hk[0],u=hv[0];pop();
      if(t>D[u])continue;
      if(t>=gd)break;
      if(u===ed.a&&t+d.s<gd){gd=t+d.s;goal=u;}
      if(u===ed.b&&t+ed.len-d.s<gd){gd=t+ed.len-d.s;goal=u;}
      (adj[u]||[]).forEach(function(x){var nt=t+x[1];if(!(x[0] in D)||nt<D[x[0]]){D[x[0]]=nt;P[x[0]]=[u,x[2]];push(nt,x[0]);}});
    }
    if(goal===null)return null;
    var legs=[],n=goal;
    legs.push({e:d.e,s0:n===ed.a?0:ed.len,s1:d.s});
    while(P[n]){var p=P[n],e=N.edges[p[1]];legs.push({e:p[1],s0:p[0]===e.a?0:e.len,s1:p[0]===e.a?e.len:0});n=p[0];}
    legs.push({e:o.e,s0:o.s,s1:n===eo.a?0:eo.len});
    return legs.reverse().filter(function(g,gi,arr){return Math.abs(g.s1-g.s0)>1e-6||arr.length===1;});
  }
  /* a leg's line, on its side (+1 right of the way walked), trimmed at each end that is a junction's crossing */
  function bimTrLegLine(N,g,side,trim0,trim1,out){
    var e=N.edges[g.e],fw=g.s1>=g.s0,lo=Math.min(g.s0,g.s1),hi=Math.max(g.s0,g.s1),off=e.car?side*(e.w/2+bimStd('app.traffic','sw_off')):0,P=[],k,a=[0,0,0,0];
    if(fw){lo+=trim0;hi-=trim1;}else{lo+=trim1;hi-=trim0;}
    if(hi<lo){var m=(lo+hi)/2;lo=m;hi=m;}
    bimTrAt(e.P,e.C,lo,a);P.push([a[0],a[1],a[2],a[3]]);
    for(k=1;k<e.P.length-1;k++)if(e.C[k]>lo&&e.C[k]<hi){var dxa=e.P[k+1][0]-e.P[k-1][0],dza=e.P[k+1][1]-e.P[k-1][1],la=Math.sqrt(dxa*dxa+dza*dza)||1;P.push([e.P[k][0],e.P[k][1],dxa/la,dza/la]);}
    bimTrAt(e.P,e.C,hi,a);P.push([a[0],a[1],a[2],a[3]]);
    if(!fw)P.reverse();
    P.forEach(function(p){var dx=fw?p[2]:-p[2],dz=fw?p[3]:-p[3];out.push([p[0]+(-dz)*off,p[1]+dx*off]);});   /* right of the way walked: (-dz, dx) */
  }
  /* which side of a way a point is on: +1 right of it as walked */
  function bimTrSideOf(N,g,x,z){
    var e=N.edges[g.e],a=[0,0,0,0],fw=g.s1>=g.s0;
    bimTrAt(e.P,e.C,g.s0,a);
    var dx=fw?a[2]:-a[2],dz=fw?a[3]:-a[3],c=dx*(z-a[1])-dz*(x-a[0]);
    return c>=0?1:-1;
  }
  /* round a junction from one arm's side to another's: the crossings, the short way (fewest streets crossed) */
  function bimTrRound(N,j,ai,si,bo,need){
    var n=j.arms.length,best=null,dirs=[1,-1],sides=need?[need]:[1,-1];
    function corner(k,sg){return sg>0?k:(k-1+n)%n;}
    var c0=corner(ai,si);
    sides.forEach(function(sb){
      var c1=corner(bo,sb);
      dirs.forEach(function(dr){
        var cr=[],c=c0,g=0,cars=0;
        while(c!==c1&&g++<n){var m=dr>0?(c+1)%n:c;cr.push({k:m,from:dr>0?-1:1});if(j.arms[m].car)cars++;c=dr>0?(c+1)%n:(c-1+n)%n;}
        if(c!==c1)return;
        var sc=cars*100+cr.length+(sb>0?0:0.5);
        if(!best||sc<best.sc)best={sc:sc,cr:cr,sb:sb};
      });
    });
    return best;
  }
  /* a way between two points: [x, z] pairs, the distance along it, and its crossings {i (the point it starts at),
     j, k (the arm), len, sig} */
  function bimTrWalkRoute(N,O,Dp){
    var so=bimTrSnap(N,O[0],O[1]),sd=bimTrSnap(N,Dp[0],Dp[1]);
    if(!so||!sd)return null;
    var legs=bimTrWalkPath(N,so,sd);
    if(!legs||!legs.length)return null;
    var pts=[[O[0],O[1]]],cr=[],side=bimTrSideOf(N,legs[0],O[0],O[1]),i,tmp=[0,0];
    var e0=N.edges[legs[0].e];
    if(e0.car&&!(side>0?(legs[0].s1>=legs[0].s0?e0.sw.r:e0.sw.l):(legs[0].s1>=legs[0].s0?e0.sw.l:e0.sw.r))&&(e0.sw.l||e0.sw.r))side=-side;
    for(i=0;i<legs.length;i++){
      var g=legs[i],e=N.edges[g.e],fw=g.s1>=g.s0,nEnd=fw?e.b:e.a,j=N.jAt.hasOwnProperty(nEnd)?N.J[N.jAt[nEnd]]:null,last=i===legs.length-1;
      var nStart=fw?e.a:e.b,jS=N.jAt.hasOwnProperty(nStart)?N.J[N.jAt[nStart]]:null,atStart=(fw?g.s0<1e-6:Math.abs(g.s0-e.len)<1e-6);
      bimTrLegLine(N,g,side,atStart&&jS?jS.cw:0,!last&&j?j.cw:0,pts);
      if(last||!j)continue;
      /* round the junction to the next leg's side */
      var gn=legs[i+1],en=N.edges[gn.e],ain=-1,aout=-1,k;
      for(k=0;k<j.arms.length;k++){if(j.arms[k].e===g.e&&j.arms[k].end===(fw?1:0))ain=k;if(j.arms[k].e===gn.e&&j.arms[k].end===(gn.s1>=gn.s0?0:1))aout=k;}
      if(ain<0||aout<0)continue;
      var need=null;
      if(en.car&&(en.sw.l||en.sw.r)&&!(en.sw.l&&en.sw.r))need=(gn.s1>=gn.s0?(en.sw.r?1:-1):(en.sw.l?1:-1));
      var R=bimTrRound(N,j,ain,-side,aout,need);
      if(!R)continue;
      R.cr.forEach(function(c){
        var a=j.arms[c.k];
        bimTrArmPt(N,j,a,c.from,tmp);pts.push([tmp[0],tmp[1]]);
        if(a.car)cr.push({i:pts.length-1,j:j.i,k:c.k,sig:j.kind==='signal'});
        bimTrArmPt(N,j,a,-c.from,tmp);pts.push([tmp[0],tmp[1]]);
      });
      side=R.sb;
    }
    pts.push([Dp[0],Dp[1]]);
    /* the points, and the distance along them; repeated points dropped, the crossings kept on theirs */
    var P=[pts[0]],map=[0];
    for(i=1;i<pts.length;i++){var q=P[P.length-1];if(Math.abs(pts[i][0]-q[0])+Math.abs(pts[i][1]-q[1])>1e-3)P.push(pts[i]);map.push(P.length-1);}
    var C=bimTrPolyLen(P);
    cr.forEach(function(c){c.i=map[c.i];c.s0=C[c.i];c.s1=C[Math.min(C.length-1,c.i+1)];c.len=c.s1-c.s0;});
    return {P:P,C:C,len:C[C.length-1],cr:cr.filter(function(c){return c.len>0.1;})};
  }
