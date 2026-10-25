  /* ================= __acad3dV171: traffic and people around the site: the network =================
     reference/research-traffic.md, sections 5 and 8. The streets V166 keeps (mv), within the simulation's reach of the
     lot: every way a car may use, cut at the reach and split at its junctions into edges, each edge a link for each way
     it may be driven, with its lanes, speed and width; the junctions with their arms, turns, right of way, stops and
     signals; the lot's entry and doors; the footways and the sidewalks walkers use. Built at the start of a run from what
     the project holds, never saved. Plan coordinates [x, z], x east and z south. */
  var BIM_TR_FOOT=/^(footway|path|pedestrian|steps|track|living_street)$/;
  function bimTrHw(t){return String(t&&t.highway||'');}
  function bimTrBase(t){return bimTrHw(t).replace(/_link$/,'');}
  /* a car may use it: a street from a motorway to a service road, not where motor vehicles are refused; a private one
     only where it reaches the lot (its driveway) */
  function bimTrCarWay(t,nearLot){
    var hw=bimTrHw(t),cls=bimMvClassOf(hw);
    if(!cls||cls.id==='pa'||hw==='living_street'&&t.motor_vehicle==='no')return false;
    if(/^(no)$/.test(String(t.motor_vehicle||''))||/^(no)$/.test(String(t.motorcar||'')))return false;
    if(/^(no|private)$/.test(String(t.access||''))&&!nearLot)return false;
    return true;
  }
  /* a walker may use it: a car's street (its sidewalks) or a way for people on foot */
  function bimTrFootWay(t){
    var hw=bimTrHw(t);
    if(/^(no)$/.test(String(t.foot||'')))return false;
    if(BIM_TR_FOOT.test(hw))return !/^(no|private)$/.test(String(t.access||''))||/^(yes|designated|permissive)$/.test(String(t.foot||''));
    if(hw==='cycleway'||hw==='bridleway')return /^(yes|designated|permissive)$/.test(String(t.foot||''));
    return false;
  }
  function bimTrBearing(dx,dz){var b=Math.atan2(dx,-dz)*180/Math.PI;return b<0?b+360:b;}   /* clockwise from the plan's north (-z) */
  function bimTrTurnAng(bin,bout){return ((bout-bin)%360+540)%360-180;}                    /* positive: a right turn */
  /* the roadway's width: mapped, else its lanes at a lane's width, else its class's (as the context draws it) */
  function bimTrWidth(t,lanes){
    var w=String(t.width||'').replace(/^\s+|\s+$/g,''),m=/^(\d+(?:\.\d+)?)\s*(m)?$/.exec(w);
    if(m&&parseFloat(m[1])>0&&parseFloat(m[1])<80)return {v:parseFloat(m[1]),src:'mapped'};
    if(lanes>0)return {v:lanes*bimStd('app.traffic','lane_w'),src:'lanes'};
    return {v:bimRoadW()[bimTrHw(t)]||bimStd('app.traffic','lane_w')*2,src:'class'};
  }
  /* the lanes each way: per direction where mapped, else half of them each way (the odd one forward); capped by a mapped
     width at a lane's width, never under one each way */
  function bimTrLanes(t){
    var base=bimTrBase(t),ow=bimMvOneway(t),rev=String(t.oneway||'')==='-1',n=bimMvLanes(t,base).v,f=parseInt(t['lanes:forward'],10),b=parseInt(t['lanes:backward'],10),cap,wm;
    if(!(n>0))n=ow?1:2;
    if(ow){f=n;b=0;}
    else if(f>0||b>0){f=f>0?f:Math.max(1,n-(b>0?b:0));b=b>0?b:Math.max(1,n-f);}
    else{f=Math.ceil(n/2);b=Math.max(1,n-f);}
    wm=bimTrWidth(t,0);
    if(wm.src==='mapped'){
      cap=Math.max(1,Math.round(wm.v/bimStd('app.traffic','lane_w')));
      if(f+b>cap){if(ow)f=cap;else{var f2=Math.max(1,Math.round(f*cap/(f+b)));b=Math.max(1,cap-f2);f=f2;}}
    }
    f=Math.min(4,f);b=Math.min(4,b);
    if(rev){var x=f;f=b;b=x;}
    return {f:f,b:b,ow:ow,rev:rev,cap:wm.src==='mapped'};
  }
  /* the sidewalks of a street, each side of its drawn direction: mapped, or both where not (said) */
  function bimTrSidewalk(t){
    var s=String(t.sidewalk||t['sidewalk:both']||''),l=t['sidewalk:left'],r=t['sidewalk:right'];
    if(/^(no|none)$/.test(s))return {l:false,r:false,src:'mapped'};
    if(s==='left')return {l:true,r:false,src:'mapped'};
    if(s==='right')return {l:false,r:true,src:'mapped'};
    if(/^(both|yes|separate)$/.test(s))return {l:true,r:true,src:'mapped'};
    if(l!==undefined||r!==undefined)return {l:!/^(no|none)$/.test(String(l||'yes')),r:!/^(no|none)$/.test(String(r||'yes')),src:'mapped'};
    return {l:true,r:true,src:'assumed'};
  }
  /* the point where a segment from inside the reach to outside it crosses it */
  function bimTrCut(L,ax,az,bx,bz,R){
    var lo=0,hi=1,k;
    for(k=0;k<30;k++){var m=(lo+hi)/2;if(bimAccLotDist(L,ax+(bx-ax)*m,az+(bz-az)*m)<=R)lo=m;else hi=m;}
    return [ax+(bx-ax)*lo,az+(bz-az)*lo];
  }
  function bimTrPolyLen(P){var c=[0],i;for(i=1;i<P.length;i++)c.push(c[i-1]+Math.sqrt((P[i][0]-P[i-1][0])*(P[i][0]-P[i-1][0])+(P[i][1]-P[i-1][1])*(P[i][1]-P[i-1][1])));return c;}
  /* the point at s along a polyline with its cumulative lengths, and its direction */
  function bimTrAt(P,C,s,out){
    var n=P.length,lo=0,hi=n-1,i;
    if(s<=0){i=0;}else if(s>=C[n-1]){i=n-2;}
    else{while(hi-lo>1){var m=(lo+hi)>>1;if(C[m]<=s)lo=m;else hi=m;}i=lo;}
    if(i<0)i=0;
    var a=P[i],b=P[i+1]||P[i],sl=C[i+1]-C[i],f=sl>1e-9?Math.max(0,Math.min(1,(s-C[i])/sl)):0,dx=b[0]-a[0],dz=b[1]-a[1],l=Math.sqrt(dx*dx+dz*dz)||1;
    out[0]=a[0]+dx*f;out[1]=a[1]+dz*f;out[2]=dx/l;out[3]=dz/l;
    return out;
  }
  /* ---- the network ---- */
  function bimTrNet(){
    var mv=bimMvOf(),A=A3D.site&&A3D.site.access,L=bimAccLot(),R=bimStd('app.traffic','radius'),N,i,j,k;
    if(!mv)return {err:bimMvWhyNot()};
    N={L:L,R:R,x:mv.x.slice(),z:mv.z.slice(),bnd:{},edges:[],links:[],J:[],jAt:{},lot:null,doors:[],notes:[],sigOff:0,sw:{assumed:0,mapped:0},lanesCapped:0,src:bimMvSrc(A)};
    function node(x,z){N.x.push(x);N.z.push(z);return N.x.length-1;}
    /* the runs of each way within the reach, cut at it */
    var runs=[],use={};
    for(i=0;i<mv.w.length;i++){
      var rec=mv.w[i],t=mv.t[rec[0]]||{},near=Infinity;
      for(k=1;k<rec.length;k++)near=Math.min(near,bimAccLotDist(L,mv.x[rec[k]],mv.z[rec[k]]));
      var car=bimTrCarWay(t,near<=3),foot=!car&&bimTrFootWay(t);
      if(!car&&!foot)continue;
      var cur=null;
      for(k=1;k<rec.length;k++){
        var id=rec[k],inR=bimAccLotDist(L,mv.x[id],mv.z[id])<=R;
        if(k>1){
          var pid=rec[k-1],pin=bimAccLotDist(L,mv.x[pid],mv.z[pid])<=R;
          if(pin&&!inR){var c1=bimTrCut(L,mv.x[pid],mv.z[pid],mv.x[id],mv.z[id],R),n1=node(c1[0],c1[1]);N.bnd[n1]=1;cur.push(n1);cur=null;}
          else if(!pin&&inR){var c2=bimTrCut(L,mv.x[id],mv.z[id],mv.x[pid],mv.z[pid],R),n2=node(c2[0],c2[1]);N.bnd[n2]=1;cur={t:t,car:car,way:i,ids:[n2]};runs.push(cur);}
        }
        if(inR){if(!cur){cur={t:t,car:car,way:i,ids:[]};runs.push(cur);}cur.ids.push(id);}
      }
    }
    runs=runs.filter(function(r){return r.ids.length>=2;});
    runs.forEach(function(r){r.ids.forEach(function(id,q){use[id]=(use[id]||0)+(q===0||q===r.ids.length-1?1:2);});});
    /* split where runs meet, and at their ends */
    function split(id,q,r){return q===0||q===r.ids.length-1||use[id]>2;}
    runs.forEach(function(r){
      var a=0;
      for(var q=1;q<r.ids.length;q++){
        if(!split(r.ids[q],q,r))continue;
        var ids=r.ids.slice(a,q+1),P=ids.map(function(id){return [N.x[id],N.z[id]];}),C=bimTrPolyLen(P);
        if(C[C.length-1]>0.5)N.edges.push({a:ids[0],b:ids[ids.length-1],ids:ids,P:P,C:C,len:C[C.length-1],t:r.t,car:r.car,way:r.way});
        a=q;
      }
    });
    bimTrLot(N,mv,A);
    /* the links, each way a car may drive an edge */
    N.edges.forEach(function(e,ei){
      if(!e.car)return;
      var Ln=bimTrLanes(e.t),sp=bimMvSpeed(e.t,bimTrBase(e.t)),w=bimTrWidth(e.t,Ln.f+Ln.b),cls=bimMvClassOf(bimTrHw(e.t));
      if(Ln.cap)N.lanesCapped++;
      e.w=w.v;e.lanes=Ln;e.sw=bimTrSidewalk(e.t);
      if(e.sw.src==='assumed')N.sw.assumed++;else N.sw.mapped++;
      var mk=function(fw,lanes){
        if(!(lanes>0))return -1;
        var P=fw?e.P:e.P.slice().reverse(),li=N.links.length;
        N.links.push({i:li,e:ei,a:fw?e.a:e.b,b:fw?e.b:e.a,P:P,C:bimTrPolyLen(P),len:e.len,lanes:lanes,v0:Math.max(2,sp.v/3.6),vsrc:sp.src,w:w.v,ow:Ln.ow,
          rank:BIM_MV_CLASSES.length-BIM_MV_CLASSES.indexOf(cls),hw:bimTrHw(e.t),base:bimTrBase(e.t),name:String(e.t.name||e.t.ref||''),q:0,rev:-1,lot:!!e.lot});
        return li;
      };
      var f=mk(true,Ln.f),b=mk(false,Ln.b);
      if(f>=0&&b>=0){N.links[f].rev=b;N.links[b].rev=f;}
      e.lf=f;e.lb=b;
    });
    bimTrJunctions(N,mv);
    return N;
  }
  /* the lot's entry: the driveway that reaches it (a service way within 3 m), else a provisional entry on the lot's
     lowest street at its longest frontage, as V166 marks one; its doors, or its middle where none is mapped */
  function bimTrLot(N,mv,A){
    var L=N.L,i,best=null,bd=Infinity,cx=0,cz=0;
    if(L.ring){L.ring.forEach(function(p){cx+=p[0];cz+=p[1];});cx/=L.ring.length;cz/=L.ring.length;}else{cx=L.pt[0];cz=L.pt[1];}
    N.lotC=[cx,cz];
    (mv.en||[]).forEach(function(d,q){if(bimAccLotDist(L,d[0],d[1])<=(L.ring?3:30))N.doors.push({i:N.doors.length,x:d[0],z:d[1],name:(d[3]||'')||('Entrance'+(d[2]&&d[2]!=='yes'?' ('+d[2]+')':'')),mapped:true});});
    if(!N.doors.length)N.doors.push({i:0,x:cx,z:cz,name:L.ring?'The lot':'The site',mapped:false});
    for(i=0;i<N.edges.length;i++){
      var e=N.edges[i];
      if(!e.car||bimTrHw(e.t)!=='service')continue;
      [e.a,e.b].forEach(function(n){var d=bimAccLotDist(L,N.x[n],N.z[n]);if(d<=3&&d<bd){bd=d;best={n:n,e:i};}});
    }
    if(best){var de=N.edges[best.e];de.lot=true;N.lot={n:best.n,prov:false,name:'Driveway',at:de.a===best.n?de.b:de.a};return;}   /* at: where it meets the street */
    var fs=(A&&A.streets)||[],pref={s:0,l:1,c:2,a:3},bf=null;
    fs.forEach(function(f){if(!(f.c in pref)||!f.pcs||!f.pcs.length)return;if(!bf||pref[f.c]<pref[bf.c]||(pref[f.c]===pref[bf.c]&&f.len>bf.len))bf=f;});
    if(!bf||!L.ring){N.notes.push('No driveway reaches the lot and no street fronts it: the design\'s own trips are not simulated');return;}
    var pc=bf.pcs[0],bl=0;
    bf.pcs.forEach(function(q){var ql=Math.sqrt((q[2]-q[0])*(q[2]-q[0])+(q[3]-q[1])*(q[3]-q[1]));if(ql>bl){bl=ql;pc=q;}});
    var mx=(pc[0]+pc[2])/2,mz=(pc[1]+pc[3])/2,eb=-1,es=0,ed=Infinity,ek=0;
    for(i=0;i<N.edges.length;i++){
      var g=N.edges[i];if(!g.car||bimTrHw(g.t)==='service')continue;
      for(var q=1;q<g.P.length;q++){
        var ax=g.P[q-1][0],az=g.P[q-1][1],dx=g.P[q][0]-ax,dz=g.P[q][1]-az,l2=dx*dx+dz*dz,u=l2>1e-12?((mx-ax)*dx+(mz-az)*dz)/l2:0;u=Math.max(0,Math.min(1,u));
        var px=ax+u*dx,pz=az+u*dz,d2=(px-mx)*(px-mx)+(pz-mz)*(pz-mz);
        if(d2<ed){ed=d2;eb=i;ek=q;es=g.C[q-1]+u*Math.sqrt(l2);}
      }
    }
    if(eb<0||Math.sqrt(ed)>40){N.notes.push('The lot\'s street is beyond the simulated streets: the design\'s own trips are not simulated');return;}
    /* the edge split where the entry meets it, and a driveway from there to the lot line */
    var E=N.edges[eb],at=[0,0,0,0];bimTrAt(E.P,E.C,es,at);
    var mid=N.x.length;N.x.push(at[0]);N.z.push(at[1]);
    var P1=[],P2=[],ids1=[],ids2=[];
    for(var k=0;k<E.P.length;k++){if(E.C[k]<es-0.01){P1.push(E.P[k]);ids1.push(E.ids[k]);}}
    P1.push([at[0],at[1]]);ids1.push(mid);P2.push([at[0],at[1]]);ids2.push(mid);
    for(k=0;k<E.P.length;k++){if(E.C[k]>es+0.01){P2.push(E.P[k]);ids2.push(E.ids[k]);}}
    if(P1.length<2||P2.length<2){N.notes.push('The provisional entry falls at a junction: the design\'s own trips are not simulated');return;}
    var e1={a:E.a,b:mid,ids:ids1,P:P1,C:bimTrPolyLen(P1),t:E.t,car:true,way:E.way},e2={a:mid,b:E.b,ids:ids2,P:P2,C:bimTrPolyLen(P2),t:E.t,car:true,way:E.way};
    e1.len=e1.C[e1.C.length-1];e2.len=e2.C[e2.C.length-1];
    N.edges[eb]=e1;N.edges.push(e2);
    var lp=bimMvLotPt(L,at[0],at[1]),dl=Math.sqrt((lp[0]-at[0])*(lp[0]-at[0])+(lp[1]-at[1])*(lp[1]-at[1]));
    if(dl<3){var dd=Math.sqrt((cx-at[0])*(cx-at[0])+(cz-at[1])*(cz-at[1]))||1;lp=[at[0]+(cx-at[0])/dd*3,at[1]+(cz-at[1])/dd*3];dl=3;}   /* the driveway at least 3 m long, toward the lot's middle */
    var ln=N.x.length;N.x.push(lp[0]);N.z.push(lp[1]);
    var PD=[[at[0],at[1]],[lp[0],lp[1]]];
    N.edges.push({a:mid,b:ln,ids:[mid,ln],P:PD,C:bimTrPolyLen(PD),len:dl,t:{highway:'service',service:'driveway',oneway:'no',lanes:'2',sidewalk:'no'},car:true,way:-1,lot:true,prov:true});
    N.lot={n:ln,prov:true,name:'Provisional entry from '+(bf.n||'the lot\'s street'),at:mid};
  }
  /* ---- the junctions: arms, turns, right of way, stops and signals ---- */
  function bimTrJunctions(N,mv){
    var at={},i,k,sr=bimStd('app.traffic','sig_r');
    function J(n){
      if(!at.hasOwnProperty(n)){at[n]=N.J.length;N.J.push({i:N.J.length,n:n,x:N.x[n],z:N.z[n],arms:[],ins:[],outs:[],kind:'pass',sig:false,stop:{},major:{},tr:{},bnd:!!N.bnd[n],lot:!!(N.lot&&N.lot.n===n),cw:0});}
      return N.J[at[n]];
    }
    N.edges.forEach(function(e,ei){
      [0,1].forEach(function(end){
        var n=end?e.b:e.a,P=end?e.P.slice().reverse():e.P,q=1;
        while(q<P.length-1&&Math.abs(P[q][0]-P[0][0])+Math.abs(P[q][1]-P[0][1])<1)q++;
        var j=J(n);
        j.arms.push({e:ei,bear:bimTrBearing(P[q][0]-P[0][0],P[q][1]-P[0][1]),w:e.car?e.w:0,car:e.car,
          lin:e.car?(end?e.lf:e.lb):-1,lout:e.car?(end?e.lb:e.lf):-1,end:end});
      });
    });
    N.J.forEach(function(j){
      j.arms.sort(function(p,q){return p.bear-q.bear;});
      j.arms.forEach(function(a,ai){a.k=ai;if(a.lin>=0){j.ins.push(a.lin);N.links[a.lin].jb=j.i;N.links[a.lin].arm=ai;}if(a.lout>=0){j.outs.push(a.lout);N.links[a.lout].ja=j.i;N.links[a.lout].armOut=ai;}});
      var wmax=0;j.arms.forEach(function(a){if(a.w>wmax)wmax=a.w;});
      j.cw=wmax/2+bimStd('app.traffic','cw');   /* the crossings, this far from the junction's middle */
      var carArms=j.arms.filter(function(a){return a.car;}).length;
      if(j.ins.length&&carArms>=3)j.kind='yield';
    });
    N.jAt=at;
    /* the stops and signals V166 kept, each to the junction it stands at */
    (mv.xs||[]).forEach(function(x){
      var f=String(x[2]||''),best=null,bd=Infinity;
      if(!/[sap]/.test(f))return;
      N.J.forEach(function(j){if(j.kind==='pass'&&!/[a]/.test(f))return;var d=Math.sqrt((j.x-x[0])*(j.x-x[0])+(j.z-x[1])*(j.z-x[1]));if(d<bd){bd=d;best=j;}});
      if(!best||bd>sr||best.kind==='pass'){if(f.indexOf('s')>=0)N.sigOff++;return;}
      if(f.indexOf('s')>=0){best.sig=true;best.kind='signal';return;}
      if(f.indexOf('a')>=0){if(best.kind!=='signal')best.kind='allstop';return;}
      if(best.kind==='signal'||best.kind==='allstop')return;
      /* a stop on one approach: the arm whose line passes nearest the sign */
      var ba=null,bad=Infinity;
      best.arms.forEach(function(a){if(a.lin<0)return;var Lk=N.links[a.lin],P=Lk.P,dmin=Infinity;for(var q=1;q<P.length;q++)dmin=Math.min(dmin,bimPointSegDist(x[0],x[1],P[q-1][0],P[q-1][1],P[q][0],P[q][1]));if(dmin<bad){bad=dmin;ba=a;}});
      if(ba)best.stop[ba.lin]=1;
    });
    /* right of way where nothing signals it: the two approaches ranked highest by class, then speed, then lanes (SUMO's
       ranking), from different arms, are major; ties keep the order the arms are in, and that is said */
    N.J.forEach(function(j){
      if(j.kind!=='yield')return;
      var L=j.ins.map(function(li){return N.links[li];}).sort(function(p,q){return (q.rank-p.rank)||(q.v0-p.v0)||(q.lanes-p.lanes)||(p.arm-q.arm);});
      if(L.length)j.major[L[0].i]=1;
      for(k=1;k<L.length;k++)if(L[k].arm!==L[0].arm){j.major[L[k].i]=1;break;}
      if(L.length>2&&L[1].rank===L[2].rank&&L[1].v0===L[2].v0&&L[1].lanes===L[2].lanes)j.tie=true;
      Object.keys(j.stop).forEach(function(li){delete j.major[li];});
    });
    /* the turns: every exit but back the way it came, which is taken only where nothing else is (a dead end) */
    N.J.forEach(function(j){
      j.ins.forEach(function(li){
        var Lk=N.links[li],ain=j.arms[Lk.arm],bin=(ain.bear+180)%360,T=[];
        j.outs.forEach(function(lo){if(lo!==Lk.rev)T.push({o:lo,ang:bimTrTurnAng(bin,j.arms[N.links[lo].armOut].bear),p:0});});
        if(!T.length&&Lk.rev>=0&&!j.bnd&&!j.lot)T.push({o:Lk.rev,ang:180,p:1,u:true});
        j.tr[li]=T;
      });
    });
  }
