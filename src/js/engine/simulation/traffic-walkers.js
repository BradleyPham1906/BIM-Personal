  /* ================= __acad3dV171: traffic and people around the site: the walkers' ways =================
     reference/research-traffic.md, section 8. Walkers keep to the sidewalks of the streets they follow, each side a
     line beyond the roadway's edge, and to footways and paths along their line. At a junction they cross what lies
     between their way in and their way out, the short way round: each arm of the junction has a crossing this far from
     its middle (the junction's crossings), its two ends on the arm's two sidewalks. A way is a polyline, with the
     crossings marked on it; the ways are worked out once a run, between where people come from and the doors, over the
     junctions' corners: a walker changes sides only where a crossing is, and ends on the side its door is on. */
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
      if(e.car&&(!e.sw.l&&!e.sw.r&&!e.lot||!bimTrStreetWalk(e.t)))continue;
      for(q=1;q<e.P.length;q++){
        var ax=e.P[q-1][0],az=e.P[q-1][1],dx=e.P[q][0]-ax,dz=e.P[q][1]-az,l2=dx*dx+dz*dz,u=l2>1e-12?((x-ax)*dx+(z-az)*dz)/l2:0;u=Math.max(0,Math.min(1,u));
        var px=ax+u*dx,pz=az+u*dz,d2=(px-x)*(px-x)+(pz-z)*(pz-z);
        if(d2<bd){bd=d2;best={e:i,s:e.C[q-1]+u*Math.sqrt(l2),x:px,z:pz,d:0};}
      }
    }
    if(best)best.d=Math.sqrt(bd);
    return best;
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
  /* which side of an edge a point is on: +1 right of it as drawn (a to b), -1 left */
  function bimTrSideOf(N,sn,x,z){
    var e=N.edges[sn.e],a=[0,0,0,0];
    bimTrAt(e.P,e.C,sn.s,a);
    return a[2]*(z-a[1])-a[3]*(x-a[0])>=0?1:-1;
  }
  /* the corners: each junction's, between each arm and the next clockwise (a dead end's two, one each side of its arm,
     so that going round it is a crossing); a walker at a corner is on the sidewalks that meet there */
  function bimTrCornerOf(j,k,sg){var n=j.arms.length;if(n===1)return j.cb+(sg>0?0:1);return j.cb+(sg>0?k:(k-1+n)%n);}
  function bimTrArmOf(j,e,end){for(var k=0;k<j.arms.length;k++)if(j.arms[k].e===e&&j.arms[k].end===end)return k;return -1;}
  /* an edge end's corner on side sd of the edge (+1 right of a to b): at a, the arm points along the edge, so its
     right is clockwise of it; at b, it points back */
  function bimTrEndCorner(N,e,end,sd){var E=N.edges[e],j=N.J[N.jAt[end?E.b:E.a]];return bimTrCornerOf(j,bimTrArmOf(j,e,end),end?-sd:sd);}
  /* where a walker may cross an arm, and what it costs in metres walked (-1: not there): a footway's arm at no cost; a
     street where it makes a junction, a signal's wait or each lane crossed where nothing signals it; never a street at
     a driveway's mouth, a bend or the edge of the reach, where no crossing is */
  function bimTrCrossCost(N,j,a){
    if(!a.car)return 0;
    if(j.bnd)return -1;
    var E=N.edges[a.e],sv=bimTrHw(E.t)==='service'||!!E.lot,v=bimStd('hm.walk','mean'),n=0,ln=0;
    j.arms.forEach(function(b){if(b.car&&bimTrHw(N.edges[b.e].t)!=='service'&&!N.edges[b.e].lot)n++;});
    if(j.kind==='signal')return a.w+bimStd('app.traffic','x_sig')*v;
    if(!sv&&n<3&&j.arms.length>1)return -1;
    if(a.lin>=0)ln+=N.links[a.lin].lanes;
    if(a.lout>=0)ln+=N.links[a.lout].lanes;
    return a.w+ln*bimStd('app.traffic','x_lane')*v;
  }
  /* the corners joined: each side of each walkable edge (a street's side with no sidewalk three times its length,
     walked at its edge), and each crossing; once a network */
  function bimTrCorners(N){
    var nc=0,adj=[],i;
    N.J.forEach(function(j){j.cb=nc;nc+=Math.max(2,j.arms.length);});
    for(i=0;i<nc;i++)adj.push([]);
    N.edges.forEach(function(e,ei){
      if(e.car?!bimTrStreetWalk(e.t):!bimTrFootWay(e.t))return;
      [1,-1].forEach(function(sd){
        var f=e.car&&!(sd>0?e.sw.r:e.sw.l)?3:1,ca=bimTrEndCorner(N,ei,0,sd),cb=bimTrEndCorner(N,ei,1,sd);
        adj[ca].push([cb,e.len*f,{e:ei,sd:sd,fw:true}]);adj[cb].push([ca,e.len*f,{e:ei,sd:sd,fw:false}]);
      });
    });
    N.J.forEach(function(j){
      j.arms.forEach(function(a,k){
        var c=bimTrCrossCost(N,j,a),p=bimTrCornerOf(j,k,1),q=bimTrCornerOf(j,k,-1);
        if(c<0||p===q)return;
        adj[p].push([q,c,{j:j.i,k:k,from:1}]);adj[q].push([p,c,{j:j.i,k:k,from:-1}]);
      });
    });
    N.cadj=adj;N.nc=nc;
  }
  /* a way between two points: [x, z] pairs, the distance along it, and its crossings {i (the point it starts at), j,
     k (the arm), len, sig, from (the side of the arm it starts on)}. Dijkstra over the corners, from the side of the street the start is on to the side the end
     is on: each point snapped to its nearest walkable edge, the first and last legs part of their edges */
  function bimTrWalkRoute(N,O,Dp){
    var so=bimTrSnap(N,O[0],O[1]),sn=bimTrSnap(N,Dp[0],Dp[1]),i;
    if(!so||!sn)return null;
    if(!N.cadj)bimTrCorners(N);
    var eo=N.edges[so.e],ed=N.edges[sn.e];
    /* each end's sides: its own, or both on a footway (one line) */
    var sdo=eo.car?[bimTrSideOf(N,so,O[0],O[1])]:[1,-1],sdd=ed.car?[bimTrSideOf(N,sn,Dp[0],Dp[1])]:[1,-1];
    function fOf(e,sd){return e.car&&!(sd>0?e.sw.r:e.sw.l)?3:1;}
    var D=new Float64Array(N.nc),Pv=[],hk=[],hv=[];
    for(i=0;i<N.nc;i++){D[i]=Infinity;Pv.push(null);}
    function push(k,v){var q=hk.length;hk.push(k);hv.push(v);while(q>0){var p=(q-1)>>1;if(hk[p]<=k)break;hk[q]=hk[p];hv[q]=hv[p];q=p;}hk[q]=k;hv[q]=v;}
    function pop(){var lk=hk.pop(),lv=hv.pop(),m=hk.length,q=0;if(!m)return;for(;;){var l=2*q+1,r=l+1,x=-1,sk=lk;if(l<m&&hk[l]<sk){x=l;sk=hk[l];}if(r<m&&hk[r]<sk){x=r;sk=hk[r];}if(x<0)break;hk[q]=hk[x];hv[q]=hv[x];q=x;}hk[q]=lk;hv[q]=lv;}
    sdo.forEach(function(sd){
      [0,1].forEach(function(end){
        var c=bimTrEndCorner(N,so.e,end,sd),t=(end?eo.len-so.s:so.s)*fOf(eo,sd);
        if(t<D[c]){D[c]=t;Pv[c]={start:true,end:end,sd:sd};push(t,c);}
      });
    });
    while(hk.length){
      var t=hk[0],u=hv[0];pop();
      if(t>D[u])continue;
      N.cadj[u].forEach(function(x){var nt=t+x[1];if(nt<D[x[0]]){D[x[0]]=nt;Pv[x[0]]={from:u,m:x[2]};push(nt,x[0]);}});
    }
    /* the end: from a corner of its edge on its side, or straight along the start's edge where both are on its side */
    var best=Infinity,bc=-1,bend=0,bsd=sdd[0],direct=null;
    sdd.forEach(function(sd){
      [0,1].forEach(function(end){
        var c=bimTrEndCorner(N,sn.e,end,sd),t=D[c]+(end?ed.len-sn.s:sn.s)*fOf(ed,sd);
        if(t<best){best=t;bc=c;bend=end;bsd=sd;}
      });
      if(so.e===sn.e&&sdo.indexOf(sd)>=0){var td=Math.abs(sn.s-so.s)*fOf(eo,sd);if(td<=best){best=td;direct=sd;}}
    });
    if(best===Infinity)return null;
    var pts=[[O[0],O[1]]],cr=[],tmp=[0,0];
    function cwAt(e,end){var E=N.edges[e];return N.J[N.jAt[end?E.b:E.a]].cw;}
    function leg(e,s0,s1,sd,tr0,tr1){bimTrLegLine(N,{e:e,s0:s0,s1:s1},s1>=s0?sd:-sd,tr0,tr1,pts);}
    if(direct!==null)leg(so.e,so.s,sn.s,direct,0,0);
    else{
      var mv=[],c=bc;
      while(c>=0&&Pv[c]&&!Pv[c].start){mv.push(Pv[c].m);c=Pv[c].from;}
      var st=Pv[c];
      mv.reverse();
      leg(so.e,so.s,st.end?eo.len:0,st.sd,0,cwAt(so.e,st.end));
      mv.forEach(function(m){
        if(m.e!==undefined){var E=N.edges[m.e];leg(m.e,m.fw?0:E.len,m.fw?E.len:0,m.sd,cwAt(m.e,m.fw?0:1),cwAt(m.e,m.fw?1:0));return;}
        var j=N.J[m.j],a=j.arms[m.k];
        bimTrArmPt(N,j,a,m.from,tmp);pts.push([tmp[0],tmp[1]]);
        if(a.car)cr.push({i:pts.length-1,j:j.i,k:m.k,sig:j.kind==='signal',from:m.from});
        bimTrArmPt(N,j,a,-m.from,tmp);pts.push([tmp[0],tmp[1]]);
      });
      leg(sn.e,bend?ed.len:0,sn.s,bsd,cwAt(sn.e,bend),0);
    }
    pts.push([Dp[0],Dp[1]]);
    /* the points, and the distance along them; repeated points dropped, the crossings kept on theirs */
    var P=[pts[0]],map=[0];
    for(i=1;i<pts.length;i++){var q=P[P.length-1];if(Math.abs(pts[i][0]-q[0])+Math.abs(pts[i][1]-q[1])>1e-3)P.push(pts[i]);map.push(P.length-1);}
    var C=bimTrPolyLen(P);
    cr.forEach(function(x){x.i=map[x.i];x.s0=C[x.i];x.s1=C[Math.min(C.length-1,x.i+1)];x.len=x.s1-x.s0;});
    return {P:P,C:C,len:C[C.length-1],cost:best,cr:cr.filter(function(x){return x.len>0.1;})};
  }
