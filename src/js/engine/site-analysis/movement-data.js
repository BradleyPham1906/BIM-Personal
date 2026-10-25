  /* ================= __acad3dV166: site analysis in the model III, movement: the data =================
     reference/research-site-analysis-in-model.md, section 4. Kept with the access data as mv, so the six
     movement analyses run again offline. Coordinates in model metres to the decimetre. */
  var BIM_MV_R=800,BIM_MV_DOOR=3,BIM_MV_CAR=400,BIM_MV_NODES=6000,BIM_MV_TOL=0.75,BIM_MV_CARS=24;
  /* the tags movement reads; the rest of a way's tags stay in OpenStreetMap */
  var BIM_MV_KEYS=/^(highway|name|ref|maxspeed|maxspeed:type|zone:maxspeed|source:maxspeed|lanes|lanes:forward|lanes:backward|oneway|oneway:bicycle|junction|cycleway(:[a-z_:]+)?|parking(:[a-z_:]+)?|sidewalk(:[a-z_:]+)?|service|access|bicycle|motor_vehicle|motorcar|foot|segregated|lane_markings|bridge|tunnel|layer|bicycle_road|cyclestreet|shoulder(:[a-z_:]+)?|width)$/;   /* __acad3dV171: width, which caps a street's lanes */
  var BIM_MV_HW=/^((motorway|trunk|primary|secondary|tertiary)(_link)?|unclassified|residential|living_street|road|service|pedestrian|track|footway|path|cycleway|bridleway|steps)$/;
  function bimMvR1(v){return Math.round(v*10)/10;}
  function bimMvTags(t){var o={},k,n=0;for(k in t)if(t.hasOwnProperty(k)&&n<40&&BIM_MV_KEYS.test(k)){o[k]=String(t[k]).slice(0,120);n++;}return o;}
  /* a way movement keeps: a street or a path, not a sidewalk or a crossing drawn on its own, not a car
     park's aisle, not an area */
  function bimMvKeepWay(t){
    if(!t||!BIM_MV_HW.test(String(t.highway||''))||t.area==='yes')return false;
    if(/^(footway|path|cycleway)$/.test(t.highway)&&/^(sidewalk|crossing|traffic_island|access_aisle)$/.test(String(t.footway||t.path||t.cycleway||'')))return false;
    if(t.highway==='service'&&/^(parking_aisle|drive-through)$/.test(String(t.service||'')))return false;
    return true;
  }
  /* a route's interval (the headway, OpenStreetMap's estimate) in minutes: HH:MM:SS, HH:MM, MM or M */
  function bimMvInterval(v){
    var s=String(v==null?'':v).replace(/^\s+|\s+$/g,''),m=/^(\d+):(\d{1,2})(?::(\d{1,2}))?$/.exec(s),t=null;
    if(m)t=parseInt(m[1],10)*60+parseInt(m[2],10)+(m[3]?parseInt(m[3],10)/60:0);
    else if(/^\d+(\.\d+)?$/.test(s))t=parseFloat(s);
    return t!==null&&t>0&&t<=720?Math.round(t*100)/100:null;
  }
  /* a crossing's controls: s signals, a all-way stop, p a stop on its approach, c marked, i an island */
  function bimMvCross(t){
    var f='',cr=String(t.crossing||''),hw=String(t.highway||'');
    if(hw==='traffic_signals'||cr==='traffic_signals'||t['crossing:signals']==='yes')f+='s';
    if(hw==='stop')f+=(t.stop==='all'?'a':'p');
    if(/^(marked|zebra|uncontrolled)$/.test(cr)||/^(yes|zebra|lines|surface|dashes|dots|ladder)/.test(String(t['crossing:markings']||'')))f+='c';
    if(t['crossing:island']==='yes'||cr==='island'||t.crossing_ref==='island')f+='i';
    return f;
  }
  /* the nearest point of the lot to a point: its line, or the site's point */
  function bimMvLotPt(L,x,z){
    if(!L.ring)return [L.pt[0],L.pt[1]];
    if(bimPointInPoly([x,z],L.ring))return [x,z];
    var r=L.ring,n=r.length,best=null,bd=Infinity,i;
    for(i=0;i<n;i++){
      var A=r[i],B=r[(i+1)%n],dx=B[0]-A[0],dz=B[1]-A[1],l2=dx*dx+dz*dz,t=l2>1e-12?((x-A[0])*dx+(z-A[1])*dz)/l2:0;
      t=Math.max(0,Math.min(1,t));
      var px=A[0]+t*dx,pz=A[1]+t*dz,d=(x-px)*(x-px)+(z-pz)*(z-pz);
      if(d<bd){bd=d;best=[px,pz];}
    }
    return best;
  }
  /* the walk's Dijkstra again, its costs exactly as bimAccDijkstra's, keeping the edge each node was
     reached by */
  function bimMvPred(net,seeds,maxT){
    var n=net.N.x.length,E=net.E,head=[],nxt=[],to=[],cost=[],eid=[],D=[],P=[],hk=[],hv=[],i,k=0;
    for(i=0;i<n;i++){head.push(-1);D.push(Infinity);P.push(-1);}
    for(i=0;i<E.n;i++){
      var c=E.l[i]*E.m[i]/bimAccSpeed();
      to[k]=E.b[i];cost[k]=c;eid[k]=i;nxt[k]=head[E.a[i]];head[E.a[i]]=k;k++;
      to[k]=E.a[i];cost[k]=c;eid[k]=i;nxt[k]=head[E.b[i]];head[E.b[i]]=k;k++;
    }
    function push(key,v){
      var j=hk.length;hk.push(key);hv.push(v);
      while(j>0){var q=(j-1)>>1;if(hk[q]<=key)break;hk[j]=hk[q];hv[j]=hv[q];j=q;}
      hk[j]=key;hv[j]=v;
    }
    function pop(){
      var lk=hk.pop(),lv=hv.pop(),m=hk.length,j=0;
      if(!m)return;
      for(;;){
        var l=2*j+1,r=l+1,s=-1,sk=lk;
        if(l<m&&hk[l]<sk){s=l;sk=hk[l];}
        if(r<m&&hk[r]<sk){s=r;sk=hk[r];}
        if(s<0)break;
        hk[j]=hk[s];hv[j]=hv[s];j=s;
      }
      hk[j]=lk;hv[j]=lv;
    }
    for(i=0;i<seeds.length;i++)if(seeds[i][1]<D[seeds[i][0]]){D[seeds[i][0]]=seeds[i][1];P[seeds[i][0]]=-1;push(seeds[i][1],seeds[i][0]);}
    while(hk.length){
      var t=hk[0],u=hv[0],e;
      pop();
      if(t>D[u])continue;
      if(t>maxT)break;
      for(e=head[u];e>=0;e=nxt[e]){var nt=t+cost[e],w=to[e];if(nt<D[w]){D[w]=nt;P[w]=eid[e];push(nt,w);}}
    }
    return {D:D,P:P};
  }
  /* the way from the lot to a point, as the walk times found it: the step onto the network, back along
     the edges each node was reached by to a start, and the step from the lot; or straight from the lot
     where the network beside it is nearer that way (as bimAccPointTime) */
  function bimMvPathTo(net,R,x,z){
    var sn=bimAccSnap(net,x,z,300),E=net.E,N=net.N,pts,u,guard=0;
    if(!sn)return null;
    var e=sn.e,c=E.m[e]/bimAccSpeed(),ta=R.D[E.a[e]]+sn.s*c,tb=R.D[E.b[e]]+(E.l[e]-sn.s)*c;
    pts=[[x,z],[sn.x,sn.z]];
    if(net.L&&!net.W[E.w[e]].lev){var dl=bimAccLotDist(net.L,sn.x,sn.z);if(dl<=BIM_ACC_FRONT&&dl/bimAccSpeed()<=Math.min(ta,tb)){pts.push(bimMvLotPt(net.L,sn.x,sn.z));return pts.reverse();}}
    if(!isFinite(Math.min(ta,tb)))return null;
    u=ta<=tb?E.a[e]:E.b[e];
    while(u>=0&&guard++<200000){pts.push([N.x[u],N.z[u]]);var pe=R.P[u];if(pe<0)break;u=E.a[pe]===u?E.b[pe]:E.a[pe];}
    var last=pts[pts.length-1];
    pts.push(bimMvLotPt(net.L,last[0],last[1]));
    return pts.reverse();
  }
  function bimMvFlat(P){var o=[];bimAccDP(P.map(function(p){return [p[0],p[1],0];}),1).forEach(function(p){o.push(bimMvR1(p[0]),bimMvR1(p[1]));});return o;}
  /* Douglas-Peucker in plan between the nodes a way must keep */
  function bimMvThin(P,must,tol){
    var n=P.length,keep=[],st=[],k,a=0;
    for(k=0;k<n;k++)keep.push(k===0||k===n-1||must[k]);
    for(k=1;k<n;k++)if(keep[k]){if(k-a>1)st.push([a,k]);a=k;}
    while(st.length){
      var r=st.pop(),i0=r[0],i1=r[1],best=-1,bd=tol,ax=P[i0][0],az=P[i0][1],dx=P[i1][0]-ax,dz=P[i1][1]-az,l2=dx*dx+dz*dz;
      for(k=i0+1;k<i1;k++){
        var u=l2>1e-12?((P[k][0]-ax)*dx+(P[k][1]-az)*dz)/l2:0;u=Math.max(0,Math.min(1,u));
        var ex=P[k][0]-ax-u*dx,ez=P[k][1]-az-u*dz,d=Math.sqrt(ex*ex+ez*ez);
        if(d>bd){bd=d;best=k;}
      }
      if(best>=0){keep[best]=true;st.push([i0,best],[best,i1]);}
    }
    return keep;
  }
  /* all of it, from the answer V161 worked the walks out of */
  function bimMvWork(els,org,L,net,D0,places,stops,nb,nr){
    var mv={r:BIM_MV_R,x:[],z:[],t:[],w:[],xs:[],en:[],pe:[],cp:[],rt:[],iv:{},paths:[],cut:null,n:{ways:0,dropped:0}},RW=BIM_MV_R+50,i,j,e,k;
    var runs=[],uses={},must={},tagKey={},byWay={},seen={};
    /* the crossings first: their nodes are kept on the streets they are on */
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||e.type!=='node'||!e.tags||typeof e.lat!=='number'||typeof e.lon!=='number')continue;
      var tg=e.tags,p=bimGeoToModel(e.lon,e.lat,org),dl=bimAccLotDist(L,p[0],p[1]);
      if(/^(traffic_signals|stop|crossing)$/.test(String(tg.highway||''))||tg.crossing){
        var f=bimMvCross(tg);
        if(f&&dl<=RW){mv.xs.push([bimMvR1(p[0]),bimMvR1(p[1]),f]);must[e.id]=1;}
      }
      if(tg.entrance&&dl<=(L.ring?BIM_MV_DOOR:BIM_ACC_FRONT))mv.en.push([bimMvR1(p[0]),bimMvR1(p[1]),String(tg.entrance).slice(0,30),String(tg.name||tg.ref||'').slice(0,60)]);
      if(tg.amenity==='parking_entrance'&&dl<=BIM_MV_CAR){
        var pt=bimAccPointTime(net,D0,p[0],p[1],200);
        mv.pe.push([bimMvR1(p[0]),bimMvR1(p[1]),pt?bimAccR2(pt.t):null,String(tg.name||'').slice(0,60),String(tg.access||'').slice(0,20),String(tg.parking||'').slice(0,20)]);
      }
    }
    /* the streets and paths: each way's runs of nodes within the window, a node beyond at each end so
       the line reaches the edge */
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||e.type!=='way'||!e.tags||!e.tags.highway||seen[e.id]||!Array.isArray(e.nodes)||!Array.isArray(e.geometry)||e.nodes.length!==e.geometry.length||e.nodes.length<2)continue;
      seen[e.id]=1;
      if(!bimMvKeepWay(e.tags))continue;
      var P=[],ins=[],ok=true;
      for(j=0;j<e.nodes.length;j++){
        var g=e.geometry[j];
        if(!g||typeof g.lat!=='number'||typeof g.lon!=='number'||!isFinite(g.lat)||!isFinite(g.lon)){ok=false;break;}
        var q=bimGeoToModel(g.lon,g.lat,org);P.push(q);ins.push(bimAccLotDist(L,q[0],q[1])<=RW);
      }
      if(!ok)continue;
      var tk=JSON.stringify(bimMvTags(e.tags));
      if(!tagKey.hasOwnProperty(tk)){tagKey[tk]=mv.t.length;mv.t.push(JSON.parse(tk));}
      j=0;
      while(j<P.length){
        if(!ins[j]){j++;continue;}
        var a=j;while(j<P.length&&ins[j])j++;
        var s0=Math.max(0,a-1),s1=Math.min(P.length-1,j);
        if(s1-s0<1)continue;
        var R={ti:tagKey[tk],ids:e.nodes.slice(s0,s1+1),P:P.slice(s0,s1+1),way:e.id,d:Infinity};
        for(k=0;k<R.P.length;k++)R.d=Math.min(R.d,bimAccLotDist(L,R.P[k][0],R.P[k][1]));
        R.ids.forEach(function(id){uses[id]=(uses[id]||0)+1;});
        runs.push(R);
      }
    }
    /* nearest first; past the budget the farthest go, and the window kept is said */
    runs.sort(function(x,y){return x.d-y.d;});
    var idx={},nn=0;
    for(i=0;i<runs.length;i++){
      var Rr=runs[i],mk=[];
      for(k=0;k<Rr.ids.length;k++)mk.push(uses[Rr.ids[k]]>1||!!must[Rr.ids[k]]||(k>0&&Rr.ids[k]===Rr.ids[0]));
      var kp=bimMvThin(Rr.P,mk,BIM_MV_TOL),add=0;
      for(k=0;k<Rr.ids.length;k++)if(kp[k]&&!idx.hasOwnProperty(Rr.ids[k]))add++;
      if(nn+add>BIM_MV_NODES){mv.cut=Math.round(Rr.d);mv.n.dropped=runs.length-i;break;}
      var rec=[Rr.ti];
      for(k=0;k<Rr.ids.length;k++){
        if(!kp[k])continue;
        var id=Rr.ids[k];
        if(!idx.hasOwnProperty(id)){idx[id]=mv.x.length;mv.x.push(bimMvR1(Rr.P[k][0]));mv.z.push(bimMvR1(Rr.P[k][1]));nn++;}
        if(rec.length===1||rec[rec.length-1]!==idx[id])rec.push(idx[id]);
      }
      if(rec.length<3)continue;
      (byWay[Rr.way]||(byWay[Rr.way]=[])).push(mv.w.length);
      mv.w.push(rec);
    }
    mv.n.ways=mv.w.length;
    /* the lines: each one's headway, the least over its relations, and the streets it runs along */
    var lines={},order=[];
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||e.type!=='relation'||!e.tags||e.tags.type!=='route'||!Array.isArray(e.members))continue;
      var rm=BIM_ACC_ROUTE_MODE[e.tags.route],lab=String(e.tags.ref||e.tags.name||'').replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,28);
      if(!rm||!lab)continue;
      var key=rm+'|'+lab,iv=bimMvInterval(e.tags.interval),o=lines[key];
      if(!o){o=lines[key]={m:rm,l:lab,iv:null,w:{}};order.push(key);}
      if(iv!==null&&(o.iv===null||iv<o.iv))o.iv=iv;
      e.members.forEach(function(mb){if(mb&&mb.type==='way'&&byWay[mb.ref])byWay[mb.ref].forEach(function(wi){o.w[wi]=1;});});
    }
    order.forEach(function(key){
      var o=lines[key],ws=Object.keys(o.w).map(function(x){return +x;}).sort(function(a2,b2){return a2-b2;});
      mv.iv[key]=o.iv;
      mv.rt.push({m:o.m,l:o.l,iv:o.iv,w:ws});
    });
    /* the car parks within 400 m, nearest first, with their walks to their edges */
    var cps=[];
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||e.type!=='way'||!e.tags||e.tags.amenity!=='parking'||!Array.isArray(e.geometry)||e.geometry.length<4)continue;
      var ring=[],dd=Infinity;
      e.geometry.forEach(function(g2){if(g2&&typeof g2.lat==='number'){var q2=bimGeoToModel(g2.lon,g2.lat,org);ring.push(q2);dd=Math.min(dd,bimAccLotDist(L,q2[0],q2[1]));}});
      if(ring.length<4||dd>BIM_MV_CAR)continue;
      if(Math.abs(ring[0][0]-ring[ring.length-1][0])<0.01&&Math.abs(ring[0][1]-ring[ring.length-1][1])<0.01)ring.pop();
      var tm=bimAccParkTime(net,D0,e,org),t2=e.tags,cap=parseInt(t2.capacity,10);
      cps.push({n:String(t2.name||'').slice(0,60),k:String(t2.parking||'').slice(0,20),cap:cap>0?cap:null,ac:String(t2.access||'').slice(0,20),fee:String(t2.fee||'').slice(0,10),
        t:tm?bimAccR2(tm.t):null,d:Math.round(dd),a:bimMvR1(Math.abs(bimPolyArea(ring))),ring:bimMvFlat(ring.concat([ring[0]])).slice(0,-2)});
    }
    cps.sort(function(x,y){return x.d-y.d;});
    mv.cp=cps.slice(0,BIM_MV_CARS);
    /* the paths: to the nearest of each daily need, and to the nearest stop and station */
    var Rp=bimMvPred(net,net.seeds||[],BIM_ACC_MAXT+1);
    places.forEach(function(pl){
      var q3=pl.near[0];if(!q3)return;
      var pp=bimMvPathTo(net,Rp,q3.x,q3.z);
      if(pp&&pp.length>1)mv.paths.push({k:pl.k,t:q3.t,pts:bimMvFlat(pp)});
    });
    [['bus',nb],['rail',nr]].forEach(function(b){
      if(!(b[1]>=0))return;
      var s=stops[b[1]],pp=bimMvPathTo(net,Rp,s.x,s.z);
      if(pp&&pp.length>1)mv.paths.push({k:b[0],t:s.t,pts:bimMvFlat(pp)});
    });
    return mv;
  }
  /* ---- the walk times on the plan: the board's ramp, darker over a light map ---- */
  function bimAccPlanCols(){var s=bimMapSettings().style;return (s==='street'||s==='custom')?['#104281','#2a78d6','#86b6ef']:['#cde2fb','#5598e7','#1c5cab'];}
  var BIM_ACC_PLAN_W={a:4,c:3.5,l:3,s:2,p:2};
  /* a piece P to Q with its times at the ends, cut where it crosses 5, 10 and 15 minutes */
  function bimAccSplitBands(x1,z1,t1,x2,z2,t2,fn){
    var cuts=[0,1],k,T;
    for(k=0;k<3;k++){T=BIM_ACC_BANDS[k];if((t1-T)*(t2-T)<0)cuts.push((T-t1)/(t2-t1));}
    cuts.sort(function(a,b){return a-b;});
    for(k=1;k<cuts.length;k++){
      var a=cuts[k-1],b=cuts[k];
      if(b-a<1e-9)continue;
      var tm=t1+(a+b)/2*(t2-t1);
      fn(tm<=BIM_ACC_BANDS[0]?0:(tm<=BIM_ACC_BANDS[1]?1:(tm<=BIM_ACC_BANDS[2]?2:3)),x1+a*(x2-x1),z1+a*(z2-z1),x1+b*(x2-x1),z1+b*(z2-z1));
    }
  }
  function bimAccDrawPlan(ctx,V,W,H,op){
    var S=A3D.site&&A3D.site.access,cols=bimAccPlanCols(),B=[{},{},{}],j,b,c,pass,light;
    if(!S||!Array.isArray(S.segs))return false;
    light=cols[0]==='#104281';
    S.segs.forEach(function(g){
      var cl=g[0];
      for(var i=4;i+2<g.length;i+=3)bimAccSplitBands(g[i-3],g[i-2],g[i-1],g[i],g[i+1],g[i+2],function(bd,x1,z1,x2,z2){if(bd<3){if(!B[bd][cl])B[bd][cl]=[];B[bd][cl].push(x1,z1,x2,z2);}});
    });
    ctx.save();
    ctx.globalAlpha=op;ctx.lineCap='round';ctx.lineJoin='round';
    for(pass=0;pass<2;pass++)for(b=2;b>=0;b--)for(c in B[b])if(B[b].hasOwnProperty(c)){
      var L=B[b][c];
      ctx.beginPath();
      for(j=0;j<L.length;j+=4){var p=toScreen([L[j],0,L[j+1]],V,W,H),q=toScreen([L[j+2],0,L[j+3]],V,W,H);if(!p||!q)continue;ctx.moveTo(p[0],p[1]);ctx.lineTo(q[0],q[1]);}
      ctx.lineWidth=(BIM_ACC_PLAN_W[c]||2)+(pass?0:2.5);
      ctx.strokeStyle=pass?cols[b]:(light?'rgba(255,255,255,.85)':'rgba(12,14,17,.85)');
      ctx.stroke();
    }
    ctx.globalAlpha=Math.min(1,op+0.1);ctx.lineWidth=1.5;ctx.strokeStyle='#111';ctx.fillStyle='#fff';
    (S.stops||[]).forEach(function(s){
      if(s.t>BIM_ACC_BANDS[2])return;
      var p=toScreen([s.x,0,s.z],V,W,H);
      if(!p||!isFinite(p[0])||!isFinite(p[1]))return;
      ctx.beginPath();
      if(s.m.indexOf('metro')>=0||s.m.indexOf('rail')>=0||s.m.indexOf('light')>=0)ctx.arc(p[0],p[1],5,0,Math.PI*2);
      else ctx.rect(p[0]-4,p[1]-4,8,8);
      ctx.fill();ctx.stroke();
    });
    ctx.restore();
    return true;
  }
  /* ---- the findings, for the Site analysis ---- */
  function bimAccMin(t){return t<0.5?'under a minute':Math.round(t)+' min';}
  function bimAccKm(m){return bimClimFmt(m,1)+' km';}
  /* a street's class in words; an unnamed one is called by it */
  function bimAccStreetClass(f){return f.hw==='pedestrian'?'pedestrian street':(f.c==='s'?(f.sv==='alley'?'alley':'service road'):BIM_ACC_CLASS_NAME[f.c].toLowerCase());}
  function bimAccStreetName(f){var c=bimAccStreetClass(f);return f.n||(f.c==='s'||f.hw==='pedestrian'?'an unnamed '+c:'an unnamed '+c+' street');}
  function bimAccStreetText(f){
    var s=f.n?[bimAccStreetClass(f)]:[],sw={both:'sidewalks on both sides',left:'a sidewalk on one side',right:'a sidewalk on one side',
      no:'no sidewalk',none:'no sidewalk',separate:'sidewalks mapped separately',yes:'sidewalks'}[f.sw];
    if(f.sp)s.push(/^\d+$/.test(f.sp)?f.sp+' km/h':f.sp);
    if(f.ln)s.push(f.ln+' lane'+(f.ln==='1'?'':'s'));
    if(sw)s.push(sw);
    if(f.cy&&!/^(no|none)$/.test(f.cy))s.push('cycleway '+f.cy.replace(/_/g,' '));
    return s.join(', ');
  }
  function bimCenFmt(v,d){return v===null||v===undefined?'not available':(d?bimClimFmt(v,d):bimClimInt(v));}
  function bimCenPM(X,d){if(!X||X[0]===null)return 'not available';return bimCenFmt(X[0],d)+(X[1]!==null?' (± '+bimCenFmt(X[1],d)+')':'');}
  function bimCenMoney(X){if(!X||X[0]===null)return 'not available';return '$'+bimClimInt(X[0])+(X[1]!==null?' (± $'+bimClimInt(X[1])+')':'');}
  function bimCenPct(S){if(!S)return 'not available';var m=S[1]===null?'':(S[1]*100<1?' (± <1)':' (± '+Math.round(S[1]*100)+')');return Math.round(S[0]*100)+'%'+m;}
  function bimCenDens(X,aland){return X&&X[0]!==null&&aland>0?X[0]/(aland/1e6):null;}
  function bimAccAuto(){
    var A=[],S=A3D.site&&A3D.site.access,P=A3D.site&&A3D.site.people,src,dt;
    if(S&&Array.isArray(S.segs)){
      src=S.src+'; walk times along the network in this app';dt=S.fetched;
      var R=S.reach.len,c5=R[0],c10=R[0]+R[1],c15=R[0]+R[1]+R[2];
      A.push({auto:'access.walk',cat:'access',title:'Walk times',value:'Along the streets from the '+(S.lot.ring?'lot':'site point')+' at '+bimClimFmt(S.speed*0.06,1)+' km/h: 5 minutes reach '+bimAccKm(c5)+' of streets and paths, 10 minutes '+
        bimAccKm(c10)+', 15 minutes '+bimAccKm(c15)+'. '+(S.start.far?'The nearest street or path is '+bimClimFmt(S.start.d,0)+' m from the '+(S.lot.ring?'lot':'site point')+'.':'The walk starts at the '+(S.lot.ring?'lot line':'site')+', on the streets and paths within '+S.front+' m of it.'),
        cls:S.start.far&&S.start.d>100?'constraint':'neutral',sev:1,source:src,date:dt});
      var nb=S.bus>=0?S.stops[S.bus]:null,nr=S.rail>=0?S.stops[S.rail]:null,tv=[],cl='neutral',sv=1;
      function stopTxt(s){return s.n+', '+bimAccMin(s.t)+(s.l.length?' ('+s.l.slice(0,4).map(function(l){return l[1];}).join(', ')+(s.l.length>4?' and '+(s.l.length-4)+' more':'')+')':'');}
      tv.push(nb?'Nearest bus or tram stop: '+stopTxt(nb):'No bus or tram stop within a '+S.maxT+'-minute walk');
      tv.push(nr?'nearest rail or metro station: '+stopTxt(nr):'no rail or metro station within '+S.maxT+' minutes');
      tv.push(bimSaN(S.lines10,'line')+' within a 10-minute walk');
      if((nb&&nb.t<=5)||(nr&&nr.t<=10))cl='opportunity';
      else if(!(nb&&nb.t<=10)&&!(nr&&nr.t<=10)){cl='constraint';sv=2;}
      A.push({auto:'access.transit',cat:'access',title:'Transit',value:tv.join('; ')+'. '+bimMvPtalText(S),cls:cl,sev:sv,source:src,date:dt});
      if(S.lot.ring){
        var fs=S.streets||[];
        if(fs.length)A.push({auto:'access.frontage',cat:'access',title:'Frontage',value:'The lot fronts '+fs.map(function(f){var tx=bimAccStreetText(f);return bimAccStreetName(f)+(tx?' ('+tx+')':'')+' for '+bimClimFmt(f.len,0)+' m';}).join('; ')+'.',
          cls:fs.some(function(f){return f.c==='a';})?'constraint':'neutral',sev:1,source:S.src,date:dt});
        else A.push({auto:'access.frontage',cat:'access',title:'Frontage',value:'No street faces the lot line within '+S.front+' m: access must be secured another way (an easement or a private road).',cls:'constraint',sev:2,source:S.src,date:dt});
      }
      var C=S.conn;
      A.push({auto:'access.connectivity',cat:'access',title:'Connectivity',value:bimSaN(C.ix,'intersection')+' within '+C.r+' m of the '+(S.lot.ring?'lot':'site')+': '+bimClimFmt(C.dens,0)+' per km² ('+bimClimFmt(C.sqmi,0)+' per square mile), '+
        (C.sqmi>=bimStd('leed.nd','case1')?'at or above':'below')+' LEED ND\'s '+bimStd('leed.nd','case1')+' per square mile'+(C.dir!==null?'; the walks are '+C.dir.toFixed(2)+' times the straight line (the median of '+C.ndir+')':''),
        cls:C.sqmi>=bimStd('leed.nd','pt1')?'opportunity':(C.sqmi>=bimStd('leed.nd','case1')?'neutral':'constraint'),sev:1,source:src+'; LEED ND v4 Neighborhood Pattern and Design',date:dt});
      var w10=S.places.filter(function(p){return p.near.length&&p.near[0].t<=10;}).length;
      A.push({auto:'people.daily',cat:'people',title:'Daily needs within a walk',value:w10+' of '+S.places.length+' kinds within a 10-minute walk: '+S.places.map(function(p){var K=bimAccKind(p.k),q=p.near[0];
        return K.name.toLowerCase()+' '+(q?bimAccMin(q.t)+' ('+(q.n||K.sub[q.sub])+')':'none within '+S.maxT+' min');}).join('; '),
        cls:w10>=6?'opportunity':(w10<=3?'constraint':'neutral'),sev:1,source:src,date:dt});
    }
    if(P&&!P.outside&&P.v&&P.v.tract){
      var T=P.v.tract,G=P.geo,dens=bimCenDens(T.pop,G.tract.aland),Cv=P.v.county,where=G.tract.name+(G.county.name?', '+G.county.name:'')+(G.state.name?', '+G.state.name:'');
      A.push({auto:'people.population',cat:'people',title:'Who lives here',value:where+': '+bimCenPM(T.pop,0)+' people'+(dens!==null?', '+bimClimInt(dens)+' per km²':'')+(T.age[0]!==null?'; median age '+bimCenPM(T.age,1):''),
        source:P.src+(dens!==null?'; land area from TIGERweb':''),date:P.fetched});
      var rent=bimCenShare(T.rent,T.ten);
      A.push({auto:'people.households',cat:'people',title:'Households',value:bimCenPM(T.hh,0)+' households'+(T.hhs[0]!==null?' of '+bimClimFmt(T.hhs[0],2)+' people on average':'')+(rent?'; '+bimCenPct(rent)+' rent':'')+
        '; median household income '+bimCenMoney(T.inc)+(Cv&&Cv.inc&&Cv.inc[0]!==null?' (the county\'s $'+bimClimInt(Cv.inc[0])+')':''),source:P.src,date:P.fetched});
      var nv=bimCenShare(T.vh0,T.vht),wk=T.wrk,trn=bimCenShare(T.trn,wk),act=bimCenShare(bimCenSum([T.wlk,T.bik]),wk);
      var parts=[['drove alone',T.drv],['carpooled',T.cpl],['transit',T.trn],['walked',T.wlk],['cycled',T.bik],['worked from home',T.wfh]].map(function(x){var s2=bimCenShare(x[1],wk);return s2?Math.round(s2[0]*100)+'% '+x[0]:'';}).filter(function(x){return x;});
      A.push({auto:'people.mobility',cat:'people',title:'How people move',value:(nv?bimCenPct(nv)+' of households have no car':'Households without a car: not available')+(wk[0]?'; of '+bimClimInt(wk[0])+' workers, '+parts.join(', '):''),
        cls:(nv&&nv[0]>=0.3)||(trn&&act&&trn[0]+act[0]>=0.3)?'opportunity':'neutral',sev:1,source:P.src,date:P.fetched});
    }
    return A;
  }
  /* the Site analysis view's section */
  function bimAccStaleText(S){
    var st=bimSunSettings();
    if(bimSunNum(st.lat)&&bimSunNum(st.lon)&&(Math.abs(st.lat-S.lat)>1e-6||Math.abs(st.lon-S.lon)>1e-6))return 'The site has moved since: refresh for the new place.';
    if(S.lot&&S.lot.key!==bimAccLotKey(bimAccLot()))return 'The lot has changed since: refresh to walk from it.';
    return '';
  }
  function bimAccSaHtml(){
    var S=bimAccHas()?A3D.site.access:null,P=A3D.site&&A3D.site.people,s='<div class="a3d-clsec" data-accsec="1"><div class="a3d-sasechd">Access and people</div>';
    if(S||P){
      var p=[];
      if(S){
        p.push(S.places.filter(function(q){return q.near.length&&q.near[0].t<=10;}).length+' of '+S.places.length+' daily needs within 10 min');
        if(S.bus>=0)p.push('bus '+bimAccMin(S.stops[S.bus].t));
        if(S.rail>=0)p.push('rail '+bimAccMin(S.stops[S.rail].t));
        p.push(bimClimFmt(S.conn.dens,0)+' intersections per km²');
      }
      if(P&&P.outside)p.push('the census covers US sites only');
      else if(P&&P.v&&P.v.tract&&P.v.tract.pop[0]!==null)p.push(P.geo.tract.name+': '+bimClimInt(P.v.tract.pop[0])+' people');
      var stl=S?bimAccStaleText(S):'',lay=bimResLayers().some(function(R){return R.kind==='walk';});
      s+='<p class="a3d-clsum">'+bimEsc(p.join(' · '))+'. Data of '+bimEsc((S&&S.fetched)||(P&&P.fetched))+'.'+(stl?' '+bimEsc(stl):'')+'</p>'+
        '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="accboard" title="The board is a page of the set: it opens here and presents and prints with the sheets">Show in Presentation</button>'+
        (S?'<button type="button" class="a3d-anzbtn" data-saact="acclayer"'+(lay?' disabled title="The walk times are a layer already (Layers, Analysis)"':' title="Draw the walk times on the plan, under Analysis in Layers"')+'>Walk times layer</button>':'')+
        '<button type="button" class="a3d-anzbtn" data-saact="accget">Refresh</button></div>';
    }else s+='<p class="a3d-clsum">Walk times along the streets to daily needs and transit, the streets the lot fronts and how well they connect, and the census tract\'s people with their margins of error: from OpenStreetMap and the US Census, free.</p>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="accget">Get access and people</button><button type="button" class="a3d-anzbtn" data-saact="accboard" title="The board is a page of the set: it opens here and presents and prints with the sheets">Show in Presentation</button></div>';
    return s+'</div>';
  }

