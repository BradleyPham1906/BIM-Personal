"""patch_phase166a.py -- V166: movement, the data. The access step's one Overpass request asks for
what the six movement analyses read, and keeps it with the project.

reference/research-site-analysis-in-model.md, section 4. V161's request already returns every street
and path with all its tags, and the routes that serve the stops with theirs; V161 kept a summary (the
walk times, the places, the stops). V166 keeps, as A3D.site.access.mv:
  streets   every street and path within 800 m of the lot: its tags that movement reads (class,
            name, speed, lanes, one-way, the bike facility, parking by side, who may use it) and its
            nodes, junctions shared, thinned to 0.75 m between them; the farthest dropped first past
            6,000 nodes, said
  crossings the junctions' controls: signals, an all-way stop, a marked crossing, an island
  doors     the entrances on the lot; garage entrances and car parks within 400 m, with their walks
  lines     each line's headway from its route's interval, where mapped; the streets it runs along
  paths     the way from the lot to the nearest of each daily need, and to the nearest stop and
            station: the walk's own Dijkstra, with the edge each node was reached by
And V161's Walk times layer is no longer added on its own: Analyze site draws the walk times in the
model now (V161's layer is still there on request, WALKTIMES).
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'e8ec917e636002dc97278233a4ea7770f0530d2a3d7159d54b1707863ca95cb2'   # V165 as merged

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


MV = r"""  /* ================= __acad3dV166: site analysis in the model III, movement: the data =================
     reference/research-site-analysis-in-model.md, section 4. Kept with the access data as mv, so the six
     movement analyses run again offline. Coordinates in model metres to the decimetre. */
  var BIM_MV_R=800,BIM_MV_DOOR=3,BIM_MV_CAR=400,BIM_MV_NODES=6000,BIM_MV_TOL=0.75,BIM_MV_CARS=24;
  /* the tags movement reads; the rest of a way's tags stay in OpenStreetMap */
  var BIM_MV_KEYS=/^(highway|name|ref|maxspeed|maxspeed:type|zone:maxspeed|source:maxspeed|lanes|lanes:forward|lanes:backward|oneway|oneway:bicycle|junction|cycleway(:[a-z_:]+)?|parking(:[a-z_:]+)?|sidewalk(:[a-z_:]+)?|service|access|bicycle|motor_vehicle|motorcar|foot|segregated|lane_markings|bridge|tunnel|layer|bicycle_road|cyclestreet|shoulder(:[a-z_:]+)?)$/;
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
      var c=E.l[i]*E.m[i]/BIM_ACC_SPEED;
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
    var e=sn.e,c=E.m[e]/BIM_ACC_SPEED,ta=R.D[E.a[e]]+sn.s*c,tb=R.D[E.b[e]]+(E.l[e]-sn.s)*c;
    pts=[[x,z],[sn.x,sn.z]];
    if(net.L&&!net.W[E.w[e]].lev){var dl=bimAccLotDist(net.L,sn.x,sn.z);if(dl<=BIM_ACC_FRONT&&dl/BIM_ACC_SPEED<=Math.min(ta,tb)){pts.push(bimMvLotPt(net.L,sn.x,sn.z));return pts.reverse();}}
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
"""

# the request: the crossings, the doors and the car parks, after the routes
rep("      'rel(bn.s)[\"type\"=\"route\"][\"route\"~\"^(bus|trolleybus|tram|subway|light_rail|monorail|train|ferry)$\"];out body qt;';\n  }\n",
    "      'rel(bn.s)[\"type\"=\"route\"][\"route\"~\"^(bus|trolleybus|tram|subway|light_rail|monorail|train|ferry)$\"];out body qt;'+\n"
    "      bimMvQuery(c,Math.max(0,rp-BIM_ACC_MAXT*BIM_ACC_SPEED-BIM_ACC_FRONT));   /* __acad3dV166 */\n  }\n"
    "  /* __acad3dV166: movement's part of the request: the crossings' controls within the window, the\n"
    "     doors on the lot, the garage entrances and car parks within 400 m */\n"
    "  function bimMvQuery(c,rl){\n"
    "    var M='(around:'+Math.round(BIM_MV_R+rl+50)+','+c+')',Dr='(around:'+Math.round(rl+BIM_ACC_FRONT+5)+','+c+')',Cr='(around:'+Math.round(BIM_MV_CAR+rl)+','+c+')';\n"
    "    return '(node[\"highway\"~\"^(traffic_signals|stop|crossing)$\"]'+M+';node[\"crossing\"]'+M+';);out body qt;'+\n"
    "      '(node[\"entrance\"]'+Dr+';node[\"amenity\"=\"parking_entrance\"]'+Cr+';);out body qt;'+\n"
    "      'way[\"amenity\"=\"parking\"]'+Cr+';out tags geom qt;';\n"
    "  }\n")

# the walk's starts, kept on the network for the paths
rep("    bimAccEdges(net);\n    var D=bimAccDijkstra(net,seeds,MAXT+1),E=net.E;\n",
    "    bimAccEdges(net);\n    net.seeds=seeds;   /* __acad3dV166: the paths start where the walks do */\n    var D=bimAccDijkstra(net,seeds,MAXT+1),E=net.E;\n")

# the movement data, worked out once the stops are
rep("    var conn=bimAccConn(net,L);\n    conn.dir=",
    "    var mv=null;   /* __acad3dV166 */\n"
    "    try{mv=bimMvWork(els,org,L,net,D,places,stops,nb,nr);}\n"
    "    catch(eM){console.warn('[BIM] The movement data could not be worked out',eM);a3dToast('The movement data could not be worked out - see the console');mv={error:String(eM&&eM.message||eM)};}\n"
    "    var conn=bimAccConn(net,L);\n    conn.dir=")
rep("      counts:{ways:W.length,edges:E.n,nodes:N.x.length,places:nPl,stops:raw.length,routes:nR}};\n",
    "      counts:{ways:W.length,edges:E.n,nodes:N.x.length,places:nPl,stops:raw.length,routes:nR},mv:mv};   /* __acad3dV166 */\n")

# V161's Walk times layer, on request only: Analyze site draws the walk times in the model
rep("      if(A&&!bimResLayers().some(function(R){return R.kind==='walk';}))bimResultLayerAdd('walk',{quiet:true});\n",
    "      /* __acad3dV166: V161's Walk times layer is no longer added here: Analyze site draws the walk times in the\n"
    "         model, on Layers, Site analysis; WALKTIMES still adds V161's layer */\n")
rep("+(A?'. The walk times are on the plan (Layers, Analysis)':''));\n",
    "+(A?'. Analyze site draws them in the model (Layers, Site analysis)':''));   /* __acad3dV166 */\n")

# the block, before the findings V161 writes
rep("  /* ---- the walk times on the plan: the board's ramp, darker over a light map ---- */\n",
    MV + "  /* ---- the walk times on the plan: the board's ramp, darker over a light map ---- */\n")

assert all(ord(ch) < 128 for ch in MV), 'non-ASCII in the movement block'
out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
