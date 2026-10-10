"""patch_phase161a.py -- V161: Site analysis SA4, access and people: the data, the walk times, the findings.

reference/research-access-people.md. Asked only when asked, from two free sources, no key:
- OpenStreetMap, in one Overpass request: every street and path with its nodes, the transit stops
  and the routes that serve them, and the places of daily needs around the site;
- the US Census Bureau: TIGERweb names the census tract, county and state at the site, and the
  American Community Survey's 5-year estimates give their people, with margins of error.

From the network the app works out walk times from the lot (Dijkstra along the streets at 80 m a
minute, steps at half speed), leaving the lot anywhere along its frontage. Then, as Network
Analyst's service-area lines are:
- the network reached within 5, 10 and 15 minutes, as rings;
- each daily-needs place's walk time, a park's to the nearest point of its edge, in seven kinds;
- the stops, grouped by name, with the lines that serve them; the nearest bus and rail;
- the streets the lot fronts, measured along its line, with their class, speed, lanes and sidewalks;
- connectivity: intersections within 400 m of the lot (dead ends off, a divided road's corners as
  one), as LEED ND counts them, and how direct the walks are.
The census gives the key facts with their margins of error for the tract, its county and state, and
the age and sex structure. What is kept is what was worked out, so it opens offline.

Each result is a finding under Access and circulation or People and place, with its source and date;
the walk times become a layer under Analysis in Layers (V148), drawn on the plan. A source that fails
is named, and what did come is kept. All of it is one undo step. The board is patch 161b."""
NAME = 'patch_phase161a.py'
BASE = '2a04374b678742d62079a7052b76552ecebe061592a121f97bf4edd30a278246'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


# ---- the Site analysis takes the access and people findings, and the section ----
rep("""    return A.concat(bimClimAuto()).concat(bimZnAuto());   /* __acad3dV159: climate and risk; __acad3dV160: zoning */""",
    """    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto());   /* __acad3dV159: climate and risk; __acad3dV160: zoning; __acad3dV161: access and people */""")
rep("""      bimZnSaHtml()+    /* __acad3dV160 */""", """      bimZnSaHtml()+    /* __acad3dV160 */
      bimAccSaHtml()+   /* __acad3dV161 */""")
rep("""    if(c==='znboard')return bimClbOpen('zoning');""", """    if(c==='znboard')return bimClbOpen('zoning');
    if(c==='accget')return bimAccFetch();   /* __acad3dV161 */
    if(c==='accboard')return bimClbOpen('access');
    if(c==='acclayer')return bimResultLayerAdd('walk');""")

# ---- the walk times, a result layer that follows the access data (as a terrain layer follows its surface) ----
rep("""    var c=R.kind==='sunhours'?BIM_SIM_RAMP:R.kind==='rain'?""",
    """    if(R.kind==='walk')return 'linear-gradient(90deg,#cde2fb,#5598e7,#1c5cab)';   /* __acad3dV161 */
    var c=R.kind==='sunhours'?BIM_SIM_RAMP:R.kind==='rain'?""")
rep("""    if(R.kind!=='terrain'||bimResGone(R))return '';""",
    """    if(R.kind==='walk')return bimResGone(R)?'':'<div class="a3d-lyleg">'+['5 min or less','5 to 10 min','10 to 15 min'].map(function(n,j){return '<span><i class="ln" style="background:'+['#cde2fb','#5598e7','#1c5cab'][j]+'"></i>'+n+'</span>';}).join('')+
      '<span><i style="background:#fff;border:1.5px solid #111;border-radius:1px"></i>Bus or tram stop</span><span><i style="background:#fff;border:1.5px solid #111;border-radius:50%"></i>Rail or metro</span></div>';   /* __acad3dV161 */
    if(R.kind!=='terrain'||bimResGone(R))return '';""")
rep("""    else if(R.kind==='terrain')s=bimResGone(R)?""",
    """    else if(R.kind==='walk'){var S=A3D.site&&A3D.site.access;s=bimResGone(R)?'The access data it showed is gone: Get access and people in Site analysis brings it back.':
      'Walk times from the '+(S.lot&&S.lot.ring?'lot':'site point')+' along the streets at '+S.speed+' m a minute, from OpenStreetMap data of '+S.fetched+': 5, 10 and 15 minutes. It follows the access data, so a refresh in Site analysis updates it.';}   /* __acad3dV161 */
    else if(R.kind==='terrain')s=bimResGone(R)?""")
rep("""    if(R.kind!=='terrain'&&bimResStale(R))s+=""", """    if(R.kind!=='terrain'&&R.kind!=='walk'&&bimResStale(R))s+=""")
rep("""(gone?'<span class="a3d-lybadge gone" title="The surface it showed is gone">Gone</span>'""",
    """(gone?'<span class="a3d-lybadge gone" title="'+(R.kind==='walk'?'The access data it showed is gone':'The surface it showed is gone')+'">Gone</span>'""")
rep("""      (R.kind!=='terrain'?'<button type="button" data-lyresupd=""", """      (R.kind!=='terrain'&&R.kind!=='walk'?'<button type="button" data-lyresupd=""")
rep("""    }else return null;
    pushUndo();
    R.id='res-'""", """    }else if(kind==='walk'){   /* __acad3dV161 */
      if(!bimAccHas()){a3dToast('Get access and people first (Site analysis), then add the walk times as a layer');return null;}
      if(bimResLayers().some(function(x){return x.kind==='walk';})){a3dToast('The walk times are a layer already, in Layers under Analysis');return null;}
      R={kind:'walk',name:'Walk times',src:'access',opacity:0.9};
    }else return null;
    pushUndo();
    R.id='res-'""")
rep("""    a3dToast(R.name+' is a layer now, in Layers under Analysis');""", """    if(!opts.quiet)a3dToast(R.name+' is a layer now, in Layers under Analysis');""")
rep("""    if(R.kind==='terrain'){a3dToast(R.name+' follows its surface: it is up to date');return true;}""",
    """    if(R.kind==='terrain'){a3dToast(R.name+' follows its surface: it is up to date');return true;}
    if(R.kind==='walk'){a3dToast(R.name+' follows the access data: it is up to date');return true;}   /* __acad3dV161 */""")
rep("""  function bimResStale(R){return !!(R&&R.kind!=='terrain'&&R.key&&R.key!==bimResKey(R.kind));}""",
    """  function bimResStale(R){return !!(R&&R.kind!=='terrain'&&R.kind!=='walk'&&R.key&&R.key!==bimResKey(R.kind));}   /* __acad3dV161: walk times follow their data */""")
rep("""    if(R.kind!=='terrain')return false;
    var o=objById(R.src);""", """    if(R.kind==='walk')return !bimAccHas();   /* __acad3dV161 */
    if(R.kind!=='terrain')return false;
    var o=objById(R.src);""")
rep("""      if(R.kind==='terrain')return typeof R.src==='string'&&/^(slope|elevation|aspect|cutfill)$/.test(R.mode);""",
    """      if(R.kind==='terrain')return typeof R.src==='string'&&/^(slope|elevation|aspect|cutfill)$/.test(R.mode);
      if(R.kind==='walk')return R.src==='access';   /* __acad3dV161 */""")
rep("""    if(R.kind!=='terrain'||bimResGone(R))return false;
    o=objById(R.src);tin=bimTerrainTin(o);""", """    if(R.kind==='walk')return bimResGone(R)?false:bimAccDrawPlan(ctx,V,W,H,op);   /* __acad3dV161 */
    if(R.kind!=='terrain'||bimResGone(R))return false;
    o=objById(R.src);tin=bimTerrainTin(o);""")

ENGINE = r"""  /* ================= __acad3dV161: Site analysis SA4, access and people: the data =================
     reference/research-access-people.md. Asked only when asked, from two free sources, no key:
     - OpenStreetMap, in one Overpass request: the streets and paths with their nodes, the transit
       stops and the routes that serve them, and the places of daily needs around the site;
     - the US Census Bureau: TIGERweb names the census tract, county and state at the site, and the
       American Community Survey's 5-year estimates give their people, with margins of error.
     What is kept with the project (A3D.site.access, A3D.site.people) is what was worked out -- the
     walk times along the network, the places, stops, frontage and connectivity, the census figures
     -- not the raw data, so the board opens offline. */
  var BIM_ACC_SPEED=80,BIM_ACC_BANDS=[5,10,15],BIM_ACC_MAXT=20,BIM_ACC_FRONT=30,BIM_ACC_STEPS=2,BIM_ACC_IXR=400,BIM_ACC_IXMERGE=12,BIM_ACC_CUT=5;
  var A3D_ACC={busy:false};
  var BIM_ACC_SHOP='supermarket|greengrocer|bakery|butcher|deli|convenience';
  var BIM_ACC_AMEN='marketplace|pharmacy|clinic|doctors|hospital|dentist|kindergarten|childcare|school|college|university|library|cafe|restaurant|fast_food|pub|bank|post_office|community_centre|place_of_worship';
  var BIM_ACC_LEIS='park|playground|sports_centre|fitness_centre';
  var BIM_ACC_RE={shop:new RegExp('^('+BIM_ACC_SHOP+')$'),amenity:new RegExp('^('+BIM_ACC_AMEN+')$'),leisure:new RegExp('^('+BIM_ACC_LEIS+')$')};
  /* the seven kinds of daily need, after the 15-minute city's functions and Walk Score's categories */
  var BIM_ACC_KINDS=[
    {id:'food',name:'Food shopping',sub:{supermarket:'Supermarket',greengrocer:'Greengrocer',bakery:'Bakery',butcher:'Butcher',deli:'Delicatessen',convenience:'Convenience store',marketplace:'Market'}},
    {id:'health',name:'Health',sub:{pharmacy:'Pharmacy',clinic:'Clinic',doctors:'Doctors',hospital:'Hospital',dentist:'Dentist'}},
    {id:'learn',name:'Schools and learning',sub:{kindergarten:'Kindergarten',childcare:'Childcare',school:'School',college:'College',university:'University',library:'Library'}},
    {id:'parks',name:'Parks and play',sub:{park:'Park',playground:'Playground',sports_centre:'Sports centre',fitness_centre:'Fitness centre'}},
    {id:'eat',name:'Cafés and restaurants',sub:{cafe:'Café',restaurant:'Restaurant',fast_food:'Fast food',pub:'Pub'}},
    {id:'services',name:'Banks and post',sub:{bank:'Bank',post_office:'Post office'}},
    {id:'community',name:'Community and worship',sub:{community_centre:'Community centre',place_of_worship:'Place of worship'}}];
  /* OpenStreetMap's highway values by the FHWA's functional classes, as the usual crosswalk has them */
  var BIM_ACC_CLS={trunk:'a',trunk_link:'a',primary:'a',primary_link:'a',secondary:'c',secondary_link:'c',tertiary:'c',tertiary_link:'c',
    residential:'l',unclassified:'l',living_street:'l',road:'l',service:'s',
    pedestrian:'p',footway:'p',path:'p',cycleway:'p',steps:'p',bridleway:'p',track:'p',corridor:'p',platform:'p'};
  var BIM_ACC_CLASS_NAME={a:'Arterial',c:'Collector',l:'Local',s:'Service',p:'Path',w:'Sidewalk or crossing'};
  var BIM_ACC_RANK={a:5,c:4,l:3,p:2,s:1,w:0};
  var BIM_ACC_MODES={metro:'Metro',rail:'Rail',light:'Light rail',tram:'Tram',bus:'Bus',ferry:'Ferry'};
  var BIM_ACC_MODE_ORDER=['metro','rail','light','tram','bus','ferry'];
  var BIM_ACC_ROUTE_MODE={bus:'bus',trolleybus:'bus',tram:'tram',subway:'metro',light_rail:'light',monorail:'light',train:'rail',ferry:'ferry'};
  function bimAccKind(id){var i;for(i=0;i<BIM_ACC_KINDS.length;i++)if(BIM_ACC_KINDS[i].id===id)return BIM_ACC_KINDS[i];return null;}
  function bimAccKindOf(tg){
    var v=null,i;
    if(tg.shop&&BIM_ACC_RE.shop.test(tg.shop))v=tg.shop;
    else if(tg.amenity&&BIM_ACC_RE.amenity.test(tg.amenity))v=tg.amenity;
    else if(tg.leisure&&BIM_ACC_RE.leisure.test(tg.leisure))v=tg.leisure;
    if(!v)return null;
    for(i=0;i<BIM_ACC_KINDS.length;i++)if(BIM_ACC_KINDS[i].sub.hasOwnProperty(v))return {k:BIM_ACC_KINDS[i].id,sub:v};
    return null;
  }
  /* a way's class for walking, or '' where no one may walk: motorways, foot=no, private */
  function bimAccWalkClass(tg){
    var c=BIM_ACC_CLS[tg.highway],f=tg.foot||'';
    if(!c)return '';
    if(/^(no|private|use_sidepath)$/.test(f))return '';
    if(/^(no|private)$/.test(tg.access||'')&&!/^(yes|designated|permissive|destination)$/.test(f))return '';
    if(tg.motorroad==='yes'&&!/^(yes|designated|permissive)$/.test(f))return '';
    if(c==='p'&&/^(sidewalk|crossing|traffic_island)$/.test(tg.footway||tg.path||tg.cycleway||''))return 'w';
    return c;
  }
  /* a stop's mode, from its own tags */
  function bimAccStopMode(tg){
    if(tg.railway==='subway_entrance')return 'metro';
    if(tg.amenity==='ferry_terminal')return 'ferry';
    if(tg.railway==='station'||tg.railway==='halt'){
      if(tg.station==='subway'||tg.subway==='yes')return 'metro';
      if(tg.station==='light_rail'||tg.light_rail==='yes'||tg.station==='monorail'||tg.monorail==='yes')return 'light';
      return 'rail';
    }
    if(tg.railway==='tram_stop')return 'tram';
    if(tg.highway==='bus_stop')return 'bus';
    if(/^(platform|stop_position|station)$/.test(tg.public_transport||'')){
      if(tg.subway==='yes')return 'metro';
      if(tg.train==='yes')return 'rail';
      if(tg.light_rail==='yes'||tg.monorail==='yes')return 'light';
      if(tg.tram==='yes')return 'tram';
      if(tg.ferry==='yes')return 'ferry';
      if(tg.bus==='yes'||tg.trolleybus==='yes'||tg.amenity==='bus_station')return 'bus';
      return 'stop';
    }
    return '';
  }
  /* the one Overpass request: the network around (rn), the places and stops nearer (rp) */
  function bimAccQuery(lat,lon,rn,rp){
    var c=lat.toFixed(6)+','+lon.toFixed(6),N='(around:'+Math.round(rn)+','+c+')',P='(around:'+Math.round(rp)+','+c+')';
    return '[out:json][timeout:120];'+
      'way["highway"]'+N+';out body geom qt;'+
      '(nwr["shop"~"^('+BIM_ACC_SHOP+')$"]'+P+';nwr["amenity"~"^('+BIM_ACC_AMEN+')$"]'+P+';nwr["leisure"~"^(playground|sports_centre|fitness_centre)$"]'+P+';)->.p;'+
      'node.p;out body qt;(way.p;rel.p;);out tags center qt;'+
      'nwr["leisure"="park"]'+P+';out geom qt;'+
      '(node["highway"="bus_stop"]'+P+';node["public_transport"~"^(platform|stop_position|station)$"]'+P+';node["railway"~"^(station|halt|tram_stop|subway_entrance)$"]'+P+';node["amenity"="ferry_terminal"]'+P+';)->.s;'+
      '.s out body qt;'+
      'rel(bn.s)["type"="route"]["route"~"^(bus|trolleybus|tram|subway|light_rail|monorail|train|ferry)$"];out body qt;';
  }
  /* ---- the lot: the property line, or the site's point when there is none ---- */
  function bimAccLot(){
    var P=bimZnProperty(),g;
    if(P){g=bimPropertyGeometry(P);if(g.ring&&g.ring.length>=3)return {ring:g.ring.map(function(p){return [p[0],p[1]];}),name:P.name||'',area:g.area,perimeter:g.perimeter};}
    return {ring:null,pt:[0,0],name:''};
  }
  function bimAccLotKey(L){return L.ring?L.ring.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join(' '):'site point';}
  function bimAccLotReach(L){var r=0;if(L.ring)L.ring.forEach(function(p){r=Math.max(r,Math.sqrt(p[0]*p[0]+p[1]*p[1]));});return r;}
  function bimAccLotBox(L,m){
    if(!L.ring)return [L.pt[0]-m,L.pt[1]-m,L.pt[0]+m,L.pt[1]+m];
    var b=[Infinity,Infinity,-Infinity,-Infinity];
    L.ring.forEach(function(p){b[0]=Math.min(b[0],p[0]-m);b[1]=Math.min(b[1],p[1]-m);b[2]=Math.max(b[2],p[0]+m);b[3]=Math.max(b[3],p[1]+m);});
    return b;
  }
  function bimAccLotDist(L,x,z){
    if(!L.ring)return Math.sqrt((x-L.pt[0])*(x-L.pt[0])+(z-L.pt[1])*(z-L.pt[1]));
    if(bimPointInPoly([x,z],L.ring))return 0;
    var d=Infinity,n=L.ring.length,i;
    for(i=0;i<n;i++){var A=L.ring[i],B=L.ring[(i+1)%n];d=Math.min(d,bimPointSegDist(x,z,A[0],A[1],B[0],B[1]));}
    return d;
  }
  function bimAccPerim(r){var s=0,i;for(i=0;i<r.length;i++){var A=r[i],B=r[(i+1)%r.length];s+=Math.sqrt((B[0]-A[0])*(B[0]-A[0])+(B[1]-A[1])*(B[1]-A[1]));}return s;}
  /* where segment ab crosses segment cd: the parameter along ab, or null */
  function bimAccSegX(ax,az,bx,bz,cx,cz,dx,dz){
    var rx=bx-ax,rz=bz-az,sx=dx-cx,sz=dz-cz,den=rx*sz-rz*sx;
    if(Math.abs(den)<1e-12)return null;
    var t=((cx-ax)*sz-(cz-az)*sx)/den,u=((cx-ax)*rz-(cz-az)*rx)/den;
    return t>=0&&t<=1&&u>=0&&u<=1?t:null;
  }
  function bimAccSegLotDist(L,ax,az,bx,bz){
    if(!L.ring)return bimPointSegDist(L.pt[0],L.pt[1],ax,az,bx,bz);
    var r=L.ring,n=r.length,d=Math.min(bimAccLotDist(L,ax,az),bimAccLotDist(L,bx,bz)),i;
    if(d===0)return 0;
    for(i=0;i<n;i++){
      var A=r[i],B=r[(i+1)%n];
      if(bimAccSegX(ax,az,bx,bz,A[0],A[1],B[0],B[1])!==null)return 0;
      d=Math.min(d,bimPointSegDist(A[0],A[1],ax,az,bx,bz));
    }
    return d;
  }
  /* where to cut an edge beside the lot: every 5 m, where the lot's corners come nearest it, and
     where it crosses the lot line -- so the walk can leave the lot anywhere along its frontage */
  function bimAccCuts(L,ax,az,bx,bz){
    var dx=bx-ax,dz=bz-az,len=Math.sqrt(dx*dx+dz*dz),T=[],k,n,Pt=L.ring||[L.pt],i,out=[];
    if(len<1e-6)return [];
    n=Math.ceil(len/BIM_ACC_CUT);
    for(k=1;k<n;k++)T.push(k/n);
    for(i=0;i<Pt.length;i++){var t=((Pt[i][0]-ax)*dx+(Pt[i][1]-az)*dz)/(len*len);if(t>0&&t<1)T.push(t);}
    if(L.ring)for(i=0;i<Pt.length;i++){var B=Pt[(i+1)%Pt.length],x=bimAccSegX(ax,az,bx,bz,Pt[i][0],Pt[i][1],B[0],B[1]);if(x!==null&&x>0&&x<1)T.push(x);}
    T.sort(function(a,b){return a-b;});
    T.forEach(function(t){if(t*len<0.5||(1-t)*len<0.5)return;if(out.length&&(t-out[out.length-1])*len<0.5)return;out.push(t);});
    return out;
  }
  /* ---- the network ---- */
  /* every walkable way, its nodes in model plan metres; a bridge or a tunnel is not the ground */
  function bimAccNet(els,org){
    var X=[],Z=[],G=[],id={},W=[],seen={},i,j,e,c,ns,g,k,p;
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||e.type!=='way'||!e.tags||!e.tags.highway||!Array.isArray(e.nodes)||!Array.isArray(e.geometry)||e.nodes.length!==e.geometry.length||e.nodes.length<2)continue;
      if(seen[e.id])continue;
      seen[e.id]=1;
      c=bimAccWalkClass(e.tags);
      if(!c)continue;
      ns=[];
      for(j=0;j<e.nodes.length;j++){
        g=e.geometry[j];
        if(!g||typeof g.lat!=='number'||typeof g.lon!=='number'||!isFinite(g.lat)||!isFinite(g.lon)){ns=null;break;}
        k=id[e.nodes[j]];
        if(k===undefined){p=bimGeoToModel(g.lon,g.lat,org);k=X.length;id[e.nodes[j]]=k;X.push(p[0]);Z.push(p[1]);G.push(0);}
        ns.push(k);
      }
      if(!ns)continue;
      var lev=!!((e.tags.bridge&&e.tags.bridge!=='no')||(e.tags.tunnel&&e.tags.tunnel!=='no'));
      if(!lev)for(j=0;j<ns.length;j++)G[ns[j]]=1;
      W.push({id:e.id,c:c,t:e.tags,ns:ns,m:e.tags.highway==='steps'?BIM_ACC_STEPS:1,lev:lev});
    }
    return {N:{x:X,z:Z,g:G},W:W};
  }
  /* the edges, once the ways are cut: each with its length and its time factor */
  function bimAccEdges(net){
    var N=net.N,W=net.W,A=[],B=[],L=[],M=[],Wi=[],wi,j;
    for(wi=0;wi<W.length;wi++){
      var ns=W[wi].ns;
      for(j=1;j<ns.length;j++){
        var a=ns[j-1],b=ns[j];
        if(a===b)continue;
        A.push(a);B.push(b);L.push(Math.sqrt((N.x[b]-N.x[a])*(N.x[b]-N.x[a])+(N.z[b]-N.z[a])*(N.z[b]-N.z[a])));M.push(W[wi].m);Wi.push(wi);
      }
    }
    net.E={a:A,b:B,l:L,m:M,w:Wi,n:A.length};
  }
  /* the walk times, in minutes, from every seed at once; a binary heap; nothing past maxT settled */
  function bimAccDijkstra(net,seeds,maxT){
    var n=net.N.x.length,E=net.E,head=[],nxt=[],to=[],cost=[],D=[],hk=[],hv=[],i,k=0;
    for(i=0;i<n;i++){head.push(-1);D.push(Infinity);}
    for(i=0;i<E.n;i++){
      var c=E.l[i]*E.m[i]/BIM_ACC_SPEED;
      to[k]=E.b[i];cost[k]=c;nxt[k]=head[E.a[i]];head[E.a[i]]=k;k++;
      to[k]=E.a[i];cost[k]=c;nxt[k]=head[E.b[i]];head[E.b[i]]=k;k++;
    }
    function push(key,v){
      var j=hk.length;hk.push(key);hv.push(v);
      while(j>0){var q=(j-1)>>1;if(hk[q]<=key)break;hk[j]=hk[q];hv[j]=hv[q];j=q;}
      hk[j]=key;hv[j]=v;
    }
    function pop(){   /* takes the least off; the caller has read it from hk[0], hv[0] */
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
    for(i=0;i<seeds.length;i++)if(seeds[i][1]<D[seeds[i][0]]){D[seeds[i][0]]=seeds[i][1];push(seeds[i][1],seeds[i][0]);}
    while(hk.length){
      var t=hk[0],u=hv[0],e;
      pop();
      if(t>D[u])continue;
      if(t>maxT)break;
      for(e=head[u];e>=0;e=nxt[e]){var nt=t+cost[e],w=to[e];if(nt<D[w]){D[w]=nt;push(nt,w);}}
    }
    return D;
  }
  /* the edges by cell, for finding the nearest */
  function bimAccGrid(net,cell){
    var N=net.N,E=net.E,G={},i,p,q;
    for(i=0;i<E.n;i++){
      var ax=N.x[E.a[i]],az=N.z[E.a[i]],bx=N.x[E.b[i]],bz=N.z[E.b[i]];
      var i0=Math.floor(Math.min(ax,bx)/cell),i1=Math.floor(Math.max(ax,bx)/cell),j0=Math.floor(Math.min(az,bz)/cell),j1=Math.floor(Math.max(az,bz)/cell);
      for(p=i0;p<=i1;p++)for(q=j0;q<=j1;q++){var k=p+','+q;if(G[k])G[k].push(i);else G[k]=[i];}
    }
    net.grid={g:G,cell:cell};
  }
  function bimAccProj(net,e,x,z){
    var N=net.N,E=net.E,ax=N.x[E.a[e]],az=N.z[E.a[e]],dx=N.x[E.b[e]]-ax,dz=N.z[E.b[e]]-az,l2=dx*dx+dz*dz,t=l2>1e-12?((x-ax)*dx+(z-az)*dz)/l2:0;
    t=Math.max(0,Math.min(1,t));
    var px=ax+t*dx,pz=az+t*dz;
    return {e:e,s:t*E.l[e],d:Math.sqrt((x-px)*(x-px)+(z-pz)*(z-pz)),x:px,z:pz};
  }
  /* the nearest edge within maxR, ring by ring of cells until no nearer one can be left */
  function bimAccSnap(net,x,z,maxR,ok){
    var G=net.grid,cell=G.cell,ci=Math.floor(x/cell),cj=Math.floor(z/cell),best=null,seen={},R=Math.ceil(maxR/cell)+1,r,p,q,k;
    for(r=0;r<=R;r++){
      for(p=ci-r;p<=ci+r;p++)for(q=cj-r;q<=cj+r;q++){
        if(Math.abs(p-ci)!==r&&Math.abs(q-cj)!==r)continue;
        var Lc=G.g[p+','+q];
        if(!Lc)continue;
        for(k=0;k<Lc.length;k++){
          var e=Lc[k];
          if(seen[e])continue;
          seen[e]=1;
          if(ok&&!ok(e))continue;
          var pr=bimAccProj(net,e,x,z);
          if(pr.d<=maxR&&(!best||pr.d<best.d))best=pr;
        }
      }
      if(best&&best.d<=r*cell)break;
    }
    return best;
  }
  /* the time at s metres along edge e: the nearer of its two ends' walks */
  function bimAccTimeOn(net,D,e,s){
    var E=net.E,c=E.m[e]/BIM_ACC_SPEED;
    return Math.min(D[E.a[e]]+s*c,D[E.b[e]]+(E.l[e]-s)*c);
  }
  /* a point's walk time: the network's where it meets it, and the straight step from there; where
     it meets the network beside the lot, the straight step from the lot is a start of its own */
  function bimAccPointTime(net,D,x,z,maxR){
    var sn=bimAccSnap(net,x,z,maxR||300),t,dl;
    if(!sn)return null;
    t=bimAccTimeOn(net,D,sn.e,sn.s);
    if(net.L&&!net.W[net.E.w[sn.e]].lev){dl=bimAccLotDist(net.L,sn.x,sn.z);if(dl<=BIM_ACC_FRONT)t=Math.min(t,dl/BIM_ACC_SPEED);}
    t+=sn.d/BIM_ACC_SPEED;
    return isFinite(t)?{t:t,x:x,z:z}:null;
  }
  /* the first edge a ray from (px, pz) along (nx, nz) meets within len (from half a metre behind it) */
  function bimAccRay(net,px,pz,nx,nz,len,ok){
    var G=net.grid,cell=G.cell,N=net.N,E=net.E,x0=px-0.5*nx,z0=pz-0.5*nz,x1=px+len*nx,z1=pz+len*nz,best=null,seen={},p,q,k;
    var i0=Math.floor(Math.min(x0,x1)/cell),i1=Math.floor(Math.max(x0,x1)/cell),j0=Math.floor(Math.min(z0,z1)/cell),j1=Math.floor(Math.max(z0,z1)/cell);
    for(p=i0;p<=i1;p++)for(q=j0;q<=j1;q++){
      var Lc=G.g[p+','+q];
      if(!Lc)continue;
      for(k=0;k<Lc.length;k++){
        var e=Lc[k];
        if(seen[e])continue;
        seen[e]=1;
        if(ok&&!ok(e))continue;
        var t=bimAccSegX(x0,z0,x1,z1,N.x[E.a[e]],N.z[E.a[e]],N.x[E.b[e]],N.z[E.b[e]]);
        if(t!==null&&(!best||t<best.t))best={e:e,t:t};
      }
    }
    if(best)best.d=best.t*(len+0.5)-0.5;
    return best;
  }
  /* the metres of an edge no more than T minutes away: from a, from b, at most the whole */
  function bimAccLenWithin(ta,tb,len,c,T){
    if(!(c>0))return Math.min(ta,tb)<=T?len:0;
    var a=ta<=T?Math.min(len,(T-ta)/c*len):0,b=tb<=T?Math.min(len,(T-tb)/c*len):0;
    return Math.min(len,a+b);
  }
  /* a way as [x, z, minutes], with a point added where the walks from its two ends meet */
  function bimAccWayLine(net,D,wi){
    var w=net.W[wi],N=net.N,P=[],j;
    for(j=1;j<w.ns.length;j++){
      var a=w.ns[j-1],b=w.ns[j];
      if(a===b)continue;
      var ax=N.x[a],az=N.z[a],bx=N.x[b],bz=N.z[b],c=Math.sqrt((bx-ax)*(bx-ax)+(bz-az)*(bz-az))*w.m/BIM_ACC_SPEED;
      var ta=Math.min(D[a],D[b]+c),tb=Math.min(D[b],D[a]+c);
      if(!P.length)P.push([ax,az,ta]);
      var s=(tb-ta+c)/2;
      if(c>0&&isFinite(s)&&s>1e-6&&s<c-1e-6){var f=s/c;P.push([ax+f*(bx-ax),az+f*(bz-az),ta+s]);}
      P.push([bx,bz,tb]);
    }
    return P;
  }
  /* the parts of a line no more than T minutes away, cut exactly at T */
  function bimAccRuns(P,T){
    var R=[],cur=null,i;
    for(i=0;i<P.length;i++){
      var p=P[i];
      if(i===0){if(p[2]<=T)cur=[p];continue;}
      var q=P[i-1];
      if(p[2]<=T&&q[2]<=T){if(!cur)cur=[q];cur.push(p);continue;}
      if(p[2]>T&&q[2]>T)continue;
      var f=isFinite(p[2])&&isFinite(q[2])&&p[2]!==q[2]?(T-q[2])/(p[2]-q[2]):0,m=[q[0]+f*(p[0]-q[0]),q[1]+f*(p[1]-q[1]),T];
      if(q[2]<=T){if(!cur)cur=[q];cur.push(m);R.push(cur);cur=null;}
      else cur=[m,p];
    }
    if(cur&&cur.length>1)R.push(cur);
    return R.filter(function(r){return r.length>1;});
  }
  /* Douglas-Peucker on (x, z, minutes as metres walked): a straight run at an even pace is two points */
  function bimAccD3(p,a,b){
    var v=BIM_ACC_SPEED,dx=b[0]-a[0],dz=b[1]-a[1],dt=(b[2]-a[2])*v,px=p[0]-a[0],pz=p[1]-a[1],pt=(p[2]-a[2])*v,l2=dx*dx+dz*dz+dt*dt,u=l2>1e-12?(px*dx+pz*dz+pt*dt)/l2:0;
    u=Math.max(0,Math.min(1,u));
    var ex=px-u*dx,ez=pz-u*dz,et=pt-u*dt;
    return Math.sqrt(ex*ex+ez*ez+et*et);
  }
  function bimAccDP(P,tol){
    var n=P.length,keep=[],st=[[0,n-1]],k,out=[];
    if(n<3)return P;
    for(k=0;k<n;k++)keep.push(k===0||k===n-1);
    while(st.length){
      var r=st.pop(),a=r[0],b=r[1],best=-1,bd=tol;
      for(k=a+1;k<b;k++){var d=bimAccD3(P[k],P[a],P[b]);if(d>bd){bd=d;best=k;}}
      if(best>=0){keep[best]=true;st.push([a,best],[best,b]);}
    }
    for(k=0;k<n;k++)if(keep[k])out.push(P[k]);
    return out;
  }
  function bimAccR1(v){return Math.round(v*10)/10;}
  function bimAccR2(v){return Math.round(v*100)/100;}
  /* a place's point: a node's, a way's or relation's centre, or the middle of its outline */
  function bimAccElPoint(e,org){
    var ll=null,g;
    if(e.type==='node'&&typeof e.lat==='number')ll=[e.lon,e.lat];
    else if(e.center&&typeof e.center.lat==='number')ll=[e.center.lon,e.center.lat];
    else if(Array.isArray(e.geometry)&&e.geometry.length){var sx=0,sy=0,n=0;e.geometry.forEach(function(q){if(q&&typeof q.lat==='number'){sx+=q.lon;sy+=q.lat;n++;}});if(n)ll=[sx/n,sy/n];}
    if(!ll)return null;
    g=bimGeoToModel(ll[0],ll[1],org);
    return g;
  }
  /* a park's walk time: to the nearest point of its edge, sampled every 15 m; its area where it closes */
  function bimAccParkTime(net,D,e,org){
    var lines=[],best=null,area=0;
    if(e.type==='way'&&Array.isArray(e.geometry))lines.push({g:e.geometry,outer:true});
    else if(e.type==='relation'&&Array.isArray(e.members))e.members.forEach(function(m){if(m&&Array.isArray(m.geometry))lines.push({g:m.geometry,outer:m.role!=='inner'});});
    lines.forEach(function(L){
      var P=[];
      L.g.forEach(function(q){if(q&&typeof q.lat==='number')P.push(bimGeoToModel(q.lon,q.lat,org));});
      if(P.length<2)return;
      var cl=Math.abs(P[0][0]-P[P.length-1][0])<0.01&&Math.abs(P[0][1]-P[P.length-1][1])<0.01;
      if(cl&&P.length>3)area+=(L.outer?1:-1)*bimPolyArea(P);
      var j,k;
      for(j=1;j<P.length;j++){
        var ax=P[j-1][0],az=P[j-1][1],bx=P[j][0],bz=P[j][1],len=Math.sqrt((bx-ax)*(bx-ax)+(bz-az)*(bz-az)),n=Math.max(1,Math.ceil(len/15));
        for(k=0;k<=n;k++){
          if(k===0&&j>1)continue;
          var x=ax+(bx-ax)*k/n,z=az+(bz-az)*k/n,r=bimAccPointTime(net,D,x,z,60);
          if(r&&(!best||r.t<best.t))best=r;
        }
      }
    });
    if(!best){var c=bimAccElPoint(e,org);if(c)best=bimAccPointTime(net,D,c[0],c[1],300);}
    if(best&&area>0)best.a=Math.round(area/1000)/10;   /* hectares, to the tenth */
    return best;
  }
  /* the frontage: the lot's line, metre by metre, given to the street that faces it within 30 m */
  function bimAccFrontage(net,L){
    if(!L.ring)return [];
    var r=L.ring,n=r.length,W=net.W,E=net.E,sa=0,i,k,S={},order=[],byId={},out=[];
    for(i=0;i<n;i++){var A0=r[i],B0=r[(i+1)%n];sa+=A0[0]*B0[1]-B0[0]*A0[1];}
    W.forEach(function(w){byId[w.id]=w;});
    function road(e){var w=W[E.w[e]];return !w.lev&&(/^[acls]$/.test(w.c)||w.t.highway==='pedestrian');}
    function walk(e){return W[E.w[e]].c==='w';}
    for(i=0;i<n;i++){
      var A=r[i],B=r[(i+1)%n],dx=B[0]-A[0],dz=B[1]-A[1],len=Math.sqrt(dx*dx+dz*dz);
      if(len<0.01)continue;
      var nx=(sa>0?dz:-dz)/len,nz=(sa>0?-dx:dx)/len,m=Math.max(1,Math.round(len)),st=len/m;
      for(k=0;k<m;k++){
        var f=(k+0.5)/m,px=A[0]+f*dx,pz=A[1]+f*dz,h=bimAccRay(net,px,pz,nx,nz,BIM_ACC_FRONT,road);
        if(!h)continue;
        var w=W[E.w[h.e]],key=w.t.name?'n:'+w.t.name:'w:'+w.id,o=S[key];
        if(!o){o=S[key]={n:w.t.name||'',len:0,dsum:0,cnt:0,ways:{},side:0,pcs:[]};order.push(key);}
        o.len+=st;o.dsum+=Math.max(0,h.d);o.cnt++;o.ways[w.id]=(o.ways[w.id]||0)+1;
        if(bimAccRay(net,px,pz,nx,nz,Math.max(0.5,h.d),walk))o.side++;
        var p0=[A[0]+(k/m)*dx,A[1]+(k/m)*dz],p1=[A[0]+((k+1)/m)*dx,A[1]+((k+1)/m)*dz],lp=o.pcs[o.pcs.length-1];
        if(lp&&lp[2]===p0[0]&&lp[3]===p0[1]){lp[2]=p1[0];lp[3]=p1[1];}else o.pcs.push([p0[0],p0[1],p1[0],p1[1]]);
      }
    }
    order.forEach(function(key){
      var o=S[key],bw=null,bc=-1,cls='s',id;
      for(id in o.ways)if(o.ways.hasOwnProperty(id)){var w=byId[id];if(!w)continue;if(o.ways[id]>bc){bc=o.ways[id];bw=w;}if(BIM_ACC_RANK[w.c]>BIM_ACC_RANK[cls])cls=w.c;}
      if(o.len<2||!bw)return;
      var tg=bw.t;
      out.push({n:o.n,c:cls,hw:tg.highway,sv:String(tg.service||''),len:bimAccR1(o.len),d:bimAccR1(o.dsum/o.cnt),sp:String(tg.maxspeed||''),ln:String(tg.lanes||''),
        sw:String(tg.sidewalk||tg['sidewalk:both']||(o.side>=o.cnt*0.3?'separate':'')),
        cy:String(tg.cycleway||tg['cycleway:both']||tg['cycleway:right']||tg['cycleway:left']||''),ow:String(tg.oneway||''),
        pcs:o.pcs.map(function(p){return p.map(bimAccR1);})});
    });
    out.sort(function(a,b){return b.len-a.len||BIM_ACC_RANK[b.c]-BIM_ACC_RANK[a.c];});
    return out.slice(0,8);
  }
  /* connectivity as LEED ND counts it: the intersections of streets and paths (not sidewalks,
     crossings or service roads) within 400 m of the lot; dead ends taken off until none is left, so
     a junction leading only to culs-de-sac does not count; corners within 12 m of each other (a
     divided road's) are one */
  function bimAccConn(net,L){
    var N=net.N,E=net.E,W=net.W,n=N.x.length,deg=[],inc=[],alive=[],Q=[],i,e,R=BIM_ACC_IXR,M=BIM_ACC_IXMERGE;
    for(i=0;i<n;i++){deg.push(0);inc.push(null);}
    for(e=0;e<E.n;e++){
      var w=W[E.w[e]],on=/^[aclp]$/.test(w.c)&&w.t.area!=='yes';
      alive.push(on);
      if(!on)continue;
      deg[E.a[e]]++;deg[E.b[e]]++;
      (inc[E.a[e]]||(inc[E.a[e]]=[])).push(e);(inc[E.b[e]]||(inc[E.b[e]]=[])).push(e);
    }
    for(i=0;i<n;i++)if(deg[i]===1)Q.push(i);
    while(Q.length){
      var u=Q.pop(),k,ee=-1;
      if(deg[u]!==1)continue;
      for(k=0;k<inc[u].length;k++)if(alive[inc[u][k]]){ee=inc[u][k];break;}
      if(ee<0){deg[u]=0;continue;}
      alive[ee]=false;deg[u]=0;
      var v=E.a[ee]===u?E.b[ee]:E.a[ee];
      deg[v]--;
      if(deg[v]===1)Q.push(v);
    }
    var C=[],cell={},done={},pts=[];
    for(i=0;i<n;i++)if(deg[i]>=3&&bimAccLotDist(L,N.x[i],N.z[i])<=R+M){C.push(i);var ck=Math.floor(N.x[i]/M)+','+Math.floor(N.z[i]/M);if(cell[ck])cell[ck].push(i);else cell[ck]=[i];}
    C.forEach(function(s0){
      if(done[s0])return;
      var grp=[s0],j=0,sx=0,sz=0;
      done[s0]=1;
      while(j<grp.length){
        var a=grp[j++],ci=Math.floor(N.x[a]/M),cj=Math.floor(N.z[a]/M),p,q,t;
        for(p=ci-1;p<=ci+1;p++)for(q=cj-1;q<=cj+1;q++){
          var Lc=cell[p+','+q];
          if(!Lc)continue;
          for(t=0;t<Lc.length;t++){var b=Lc[t];if(done[b])continue;var dx=N.x[b]-N.x[a],dz=N.z[b]-N.z[a];if(dx*dx+dz*dz<=M*M){done[b]=1;grp.push(b);}}
        }
      }
      grp.forEach(function(a){sx+=N.x[a];sz+=N.z[a];});
      sx/=grp.length;sz/=grp.length;
      if(bimAccLotDist(L,sx,sz)<=R)pts.push([bimAccR1(sx),bimAccR1(sz)]);
    });
    var area=(L.ring?bimPolyArea(L.ring)+bimAccPerim(L.ring)*R:0)+Math.PI*R*R,km2=area/1e6;   /* the lot and 400 m around it (Steiner's formula) */
    return {ix:pts.length,area:Math.round(km2*1000)/1000,dens:bimAccR1(pts.length/km2),sqmi:bimAccR1(pts.length/km2*2.589988),r:R,pts:pts};
  }
  function bimAccNat(a,b){   /* lines in their natural order: 2 before 10, M15 before M101 */
    var x=/^(\D*)(\d+)(.*)$/.exec(a),y=/^(\D*)(\d+)(.*)$/.exec(b);
    if(x&&y&&x[1]===y[1]&&+x[2]!==+y[2])return +x[2]-+y[2];
    return a<b?-1:(a>b?1:0);
  }
  /* ---- all of it, from Overpass's answer ---- */
  function bimAccWork(js,org,L){
    var els=(js&&js.elements)||[],v=BIM_ACC_SPEED,MAXT=BIM_ACC_MAXT,i,e;
    if(js&&js.remark&&/error/i.test(String(js.remark)))return {error:'the request stopped short ('+String(js.remark).slice(0,120)+')'};
    var net=bimAccNet(els,org),N=net.N,W=net.W;
    if(!W.length)return {error:'no streets or paths came back around the site'};
    net.L=L;
    /* the edges beside the lot cut, then every ground node within 30 m of the lot a start, its
       time the straight step from the lot line */
    var bb=bimAccLotBox(L,BIM_ACC_FRONT),seeds=[],near=Infinity;
    W.forEach(function(w){
      if(w.lev)return;
      var out=[w.ns[0]],j;
      for(j=1;j<w.ns.length;j++){
        var a=w.ns[j-1],b=w.ns[j],ax=N.x[a],az=N.z[a],bx=N.x[b],bz=N.z[b];
        if(a!==b&&Math.max(ax,bx)>=bb[0]&&Math.min(ax,bx)<=bb[2]&&Math.max(az,bz)>=bb[1]&&Math.min(az,bz)<=bb[3]&&bimAccSegLotDist(L,ax,az,bx,bz)<=BIM_ACC_FRONT)
          bimAccCuts(L,ax,az,bx,bz).forEach(function(t){out.push(N.x.length);N.x.push(ax+t*(bx-ax));N.z.push(az+t*(bz-az));N.g.push(1);});
        out.push(b);
      }
      w.ns=out;
    });
    for(i=0;i<N.x.length;i++){
      if(!N.g[i]||N.x[i]<bb[0]||N.x[i]>bb[2]||N.z[i]<bb[1]||N.z[i]>bb[3])continue;
      var d0=bimAccLotDist(L,N.x[i],N.z[i]);
      if(d0<=BIM_ACC_FRONT){seeds.push([i,d0/v]);if(d0<near)near=d0;}
    }
    var far=!seeds.length;
    if(far){   /* no street within 30 m: the walk starts where the nearest one comes nearest */
      var bw=null,bj=-1,bd=Infinity;
      W.forEach(function(w){
        if(w.lev)return;
        for(var j=1;j<w.ns.length;j++){var a=w.ns[j-1],b=w.ns[j];if(a===b)continue;var d=bimAccSegLotDist(L,N.x[a],N.z[a],N.x[b],N.z[b]);if(d<bd){bd=d;bw=w;bj=j;}}
      });
      if(!bw)return {error:'no street or path on the ground came back around the site'};
      var a1=bw.ns[bj-1],b1=bw.ns[bj],ax1=N.x[a1],az1=N.z[a1],bx1=N.x[b1],bz1=N.z[b1],cand=[0,1],P1=L.ring||[L.pt],tb=0,tdb=Infinity;
      P1.forEach(function(p){var l2=(bx1-ax1)*(bx1-ax1)+(bz1-az1)*(bz1-az1);if(l2>1e-12)cand.push(Math.max(0,Math.min(1,((p[0]-ax1)*(bx1-ax1)+(p[1]-az1)*(bz1-az1))/l2)));});
      cand.forEach(function(t){var d=bimAccLotDist(L,ax1+t*(bx1-ax1),az1+t*(bz1-az1));if(d<tdb){tdb=d;tb=t;}});
      var sv;
      if(tb<=1e-9)sv=a1;else if(tb>=1-1e-9)sv=b1;
      else{sv=N.x.length;N.x.push(ax1+tb*(bx1-ax1));N.z.push(az1+tb*(bz1-az1));N.g.push(1);bw.ns.splice(bj,0,sv);}
      seeds.push([sv,tdb/v]);near=tdb;
    }
    bimAccEdges(net);
    var D=bimAccDijkstra(net,seeds,MAXT+1),E=net.E;
    bimAccGrid(net,60);
    /* the network reached, in the bands, and drawn: sidewalks and crossings walked, not drawn */
    var bl=[0,0,0,0],bc={},T4=[5,10,15,20],segs=[];
    for(e=0;e<E.n;e++){
      var we=W[E.w[e]];
      if(we.c==='w')continue;
      var ta=D[E.a[e]],tbb=D[E.b[e]];
      if(!(Math.min(ta,tbb)<=MAXT))continue;
      var ce=E.l[e]*E.m[e]/v,prev=0,k;
      if(!bc[we.c])bc[we.c]=[0,0,0,0];
      for(k=0;k<4;k++){var lw=bimAccLenWithin(ta,tbb,E.l[e],ce,T4[k]);bl[k]+=lw-prev;bc[we.c][k]+=lw-prev;prev=lw;}
    }
    W.forEach(function(w,wi){
      if(w.c==='w')return;
      bimAccRuns(bimAccWayLine(net,D,wi),MAXT).forEach(function(run){
        var o=[w.c];
        bimAccDP(run,0.75).forEach(function(p){o.push(bimAccR1(p[0]),bimAccR1(p[1]),bimAccR2(p[2]));});
        segs.push(o);
      });
    });
    /* the places of daily needs */
    var seenEl={},plc={},nPl=0;
    BIM_ACC_KINDS.forEach(function(K){plc[K.id]=[];});
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||!e.tags||(e.type==='way'&&e.tags.highway))continue;
      var kd=bimAccKindOf(e.tags);
      if(!kd)continue;
      var key=e.type+e.id;
      if(seenEl[key])continue;
      seenEl[key]=1;
      if(kd.k==='parks'&&/^(private|no)$/.test(e.tags.access||''))continue;
      var rr=null;
      if(kd.sub==='park')rr=bimAccParkTime(net,D,e,org);
      else{var pp=bimAccElPoint(e,org);if(pp)rr=bimAccPointTime(net,D,pp[0],pp[1],300);}
      if(!rr||rr.t>MAXT)continue;
      nPl++;
      plc[kd.k].push({n:String(e.tags.name||'').replace(/\s+/g,' ').slice(0,80),sub:kd.sub,t:rr.t,d:bimAccLotDist(L,rr.x,rr.z),x:rr.x,z:rr.z,a:rr.a||null});
    }
    var places=BIM_ACC_KINDS.map(function(K){
      var L2=plc[K.id].sort(function(a,b){return a.t-b.t;}),cnt=[0,0,0,0];
      L2.forEach(function(p){if(p.t<=5)cnt[0]++;if(p.t<=10)cnt[1]++;if(p.t<=15)cnt[2]++;cnt[3]++;});
      return {k:K.id,n:cnt,near:L2.slice(0,8).map(function(p){return {n:p.n,sub:p.sub,t:bimAccR2(p.t),d:Math.round(p.d),x:bimAccR1(p.x),z:bimAccR1(p.z),a:p.a};})};
    });
    /* the stops, the routes that serve them, grouped by name: a stop's two sides, a station's
       entrances, one stop */
    var raw=[],byId={},nR=0;
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||e.type!=='node'||!e.tags||byId[e.id])continue;
      var md=bimAccStopMode(e.tags);
      if(!md)continue;
      var sp=bimGeoToModel(e.lon,e.lat,org),st=bimAccPointTime(net,D,sp[0],sp[1],300);
      var so={id:e.id,n:String(e.tags.name||'').replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,80),ref:String(e.tags.ref||''),m:md,x:sp[0],z:sp[1],t:st?st.t:Infinity,d:bimAccLotDist(L,sp[0],sp[1]),routes:[]};
      raw.push(so);byId[e.id]=so;
    }
    for(i=0;i<els.length;i++){
      e=els[i];
      if(!e||e.type!=='relation'||!e.tags||e.tags.type!=='route'||!Array.isArray(e.members))continue;
      var rm=BIM_ACC_ROUTE_MODE[e.tags.route],lab=String(e.tags.ref||e.tags.name||'').replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,28);
      if(!rm||!lab)continue;
      nR++;
      e.members.forEach(function(mb){if(mb&&mb.type==='node'&&byId[mb.ref])byId[mb.ref].routes.push([rm,lab]);});
    }
    raw.sort(function(a,b){return a.t-b.t;});
    var groups=[];
    function dist(a,b){return Math.sqrt((a.x0-b.x)*(a.x0-b.x)+(a.z0-b.z)*(a.z0-b.z));}
    function join(g,s){
      if(s.t<g.t||g.k===0){g.t=s.t;g.x=s.x;g.z=s.z;}
      if(s.d<g.d)g.d=s.d;
      if(s.m!=='stop')g.ms[s.m]=1;
      s.routes.forEach(function(r){g.ls[r[0]+'|'+r[1]]=r;g.ms[r[0]]=1;});
      if(!g.ref&&s.ref)g.ref=s.ref;
      g.k++;
    }
    function make(s){var g={key:s.n.toLowerCase(),n:s.n,t:Infinity,d:Infinity,x:s.x,z:s.z,x0:s.x,z0:s.z,ms:{},ls:{},k:0,ref:''};groups.push(g);return g;}
    raw.forEach(function(s){
      if(!s.n)return;
      var g=null,kk=s.n.toLowerCase();
      groups.forEach(function(G2){if(!g&&G2.key===kk&&dist(G2,s)<=300)g=G2;});
      join(g||make(s),s);
    });
    raw.forEach(function(s){
      if(s.n)return;
      var g=null,best=Infinity,rail=/^(metro|light|rail)$/.test(s.m);
      groups.forEach(function(G2){var dd=dist(G2,s);if(((rail&&(G2.ms.metro||G2.ms.light||G2.ms.rail)&&dd<=300)||dd<=40)&&dd<best){best=dd;g=G2;}});
      join(g||make(s),s);
    });
    var stops=groups.filter(function(g){return g.t<=MAXT;}).sort(function(a,b){return a.t-b.t;}).slice(0,40).map(function(g){
      var ms=BIM_ACC_MODE_ORDER.filter(function(m){return g.ms[m];}),ls=[],k2;
      for(k2 in g.ls)if(g.ls.hasOwnProperty(k2))ls.push(g.ls[k2]);
      ls.sort(function(a,b){return BIM_ACC_MODE_ORDER.indexOf(a[0])-BIM_ACC_MODE_ORDER.indexOf(b[0])||bimAccNat(a[1],b[1]);});
      if(!ms.length)ms=['bus'];
      return {n:g.n||(g.ref?'Stop '+g.ref:'Unnamed '+BIM_ACC_MODES[ms[0]].toLowerCase()+' stop'),m:ms,l:ls,t:bimAccR2(g.t),d:Math.round(g.d),x:bimAccR1(g.x),z:bimAccR1(g.z)};
    });
    var nb=-1,nr=-1,l10={},nl10=0;
    stops.forEach(function(s,j){
      if(nb<0&&(s.m.indexOf('bus')>=0||s.m.indexOf('tram')>=0))nb=j;
      if(nr<0&&(s.m.indexOf('metro')>=0||s.m.indexOf('rail')>=0||s.m.indexOf('light')>=0))nr=j;
      if(s.t<=10)s.l.forEach(function(l){var kl=l[0]+'|'+l[1];if(!l10[kl]){l10[kl]=1;nl10++;}});
    });
    /* how direct the walks are: along the streets over the straight line, the median of every
       place and stop 150 m or more from the lot */
    var rat=[];
    places.forEach(function(p){p.near.forEach(function(q){if(q.d>=150)rat.push(q.t*v/q.d);});});
    stops.forEach(function(s){if(s.d>=150)rat.push(s.t*v/s.d);});
    rat.sort(function(a,b){return a-b;});
    var conn=bimAccConn(net,L);
    conn.dir=rat.length>=5?bimAccR2(rat.length%2?rat[(rat.length-1)/2]:(rat[rat.length/2-1]+rat[rat.length/2])/2):null;
    conn.ndir=rat.length;
    conn.rats=rat.map(bimAccR2);
    var cls={},ck;
    for(ck in bc)if(bc.hasOwnProperty(ck))cls[ck]=bc[ck].map(function(x){return Math.round(x)/1000;});
    return {speed:v,bands:BIM_ACC_BANDS.slice(),maxT:MAXT,front:BIM_ACC_FRONT,
      lot:{ring:L.ring?L.ring.map(function(p){return [bimAccR1(p[0]),bimAccR1(p[1])];}):null,name:L.name||'',key:bimAccLotKey(L)},
      start:{n:seeds.length,d:bimAccR1(near),far:far},
      segs:segs,reach:{len:bl.map(function(x){return Math.round(x)/1000;}),cls:cls},
      places:places,stops:stops,bus:nb,rail:nr,lines10:nl10,streets:bimAccFrontage(net,L),conn:conn,
      counts:{ways:W.length,edges:E.n,nodes:N.x.length,places:nPl,stops:raw.length,routes:nR}};
  }
  /* ---- the people: the US Census Bureau ---- */
  var BIM_CEN_TIGER='https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/';
  var BIM_CEN_API='https://api.census.gov/data/';
  /* the key facts: ACS 5-year cells, each an estimate (E) and its 90% margin of error (M) */
  var BIM_CEN_VARS={pop:'B01003_001',age:'B01002_001',inc:'B19013_001',hhs:'B25010_001',hh:'B11001_001',
    ten:'B25003_001',own:'B25003_002',rent:'B25003_003',
    wrk:'B08301_001',drv:'B08301_003',cpl:'B08301_004',trn:'B08301_010',txi:'B08301_016',mcy:'B08301_017',bik:'B08301_018',wlk:'B08301_019',oth:'B08301_020',wfh:'B08301_021',
    vht:'B08201_001',vh0:'B08201_002',hu:'B25001_001',vac:'B25002_003'};
  /* the age pyramid's 18 five-year bands, from B01001: men in cells 3 to 25, women 24 cells on */
  var BIM_CEN_BANDS=[[3],[4],[5],[6,7],[8,9,10],[11],[12],[13],[14],[15],[16],[17],[18,19],[20,21],[22],[23],[24],[25]];
  var BIM_CEN_BAND_NAMES=['0–4','5–9','10–14','15–19','20–24','25–29','30–34','35–39','40–44','45–49','50–54','55–59','60–64','65–69','70–74','75–79','80–84','85+'];
  function bimCenInUS(lat,lon){return (lat>=17.5&&lat<=71.6&&lon>=-179.3&&lon<=-64.4)||(lat>=51&&lat<=53.2&&lon>=172.4);}
  /* the newest 5-year estimates: out each December, for the year before last until then */
  function bimCenYear(){var d=new Date();return d.getFullYear()-(d.getMonth()===11?1:2);}
  function bimCen3(i){return (i<10?'00':(i<100?'0':''))+i;}
  function bimCenKeyVars(){var o=[],k;for(k in BIM_CEN_VARS)if(BIM_CEN_VARS.hasOwnProperty(k))o.push(BIM_CEN_VARS[k]+'E',BIM_CEN_VARS[k]+'M');return o;}
  function bimCenPyrVars(){var o=[],i;for(i=3;i<=25;i++)o.push('B01001_'+bimCen3(i)+'E');for(i=27;i<=49;i++)o.push('B01001_'+bimCen3(i)+'E');return o;}
  function bimCenIdUrl(svc,lat,lon){
    return BIM_CEN_TIGER+svc+'/MapServer/identify?'+bimClimQs({geometry:lon.toFixed(6)+','+lat.toFixed(6),geometryType:'esriGeometryPoint',sr:'4326',layers:'all',tolerance:'1',
      mapExtent:(lon-0.01).toFixed(6)+','+(lat-0.01).toFixed(6)+','+(lon+0.01).toFixed(6)+','+(lat+0.01).toFixed(6),imageDisplay:'400,400,96',returnGeometry:'false',f:'json'});
  }
  function bimCenAcsUrl(y,vars,lev,G){
    return BIM_CEN_API+y+'/acs/acs5?get=NAME,'+vars.join(',')+'&'+(lev==='tract'?'for=tract:'+G.tr+'&in=state:'+G.st+'%20county:'+G.co:(lev==='county'?'for=county:'+G.co+'&in=state:'+G.st:'for=state:'+G.st));
  }
  function bimCenUrls(lat,lon,y,G){
    G=G||{st:'00',co:'000',tr:'000000'};
    var kv=bimCenKeyVars(),pv=bimCenPyrVars();
    return {tract:bimCenIdUrl('Tracts_Blocks',lat,lon),countyState:bimCenIdUrl('State_County',lat,lon),
      acsTract:bimCenAcsUrl(y,kv,'tract',G),acsCounty:bimCenAcsUrl(y,kv,'county',G),acsState:bimCenAcsUrl(y,kv,'state',G),
      pyrTract:bimCenAcsUrl(y,pv,'tract',G),pyrCounty:bimCenAcsUrl(y,pv,'county',G)};
  }
  /* one request: its JSON, or why not by its host's name, with the HTTP status */
  function bimAccGet(url){
    return fetch(url).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
      var js;
      try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
      if(!js||typeof js!=='object'||(!Array.isArray(js)&&js.error))throw {bad:true};
      return {ok:true,js:js};
    }).then(null,function(e){return {ok:false,http:(e&&e.http)||0,err:bimCtxErr(bimMapHost(url),e)};});
  }
  function bimCenNum(v){
    if(v===null||v===undefined||v==='')return null;
    var n=typeof v==='number'?v:parseFloat(String(v).replace(/,/g,''));
    return isFinite(n)?n:null;
  }
  /* the ACS's special values are negative: no estimate; a margin of -555555555 is a controlled
     total's, which has none */
  function bimCenE(v){var n=bimCenNum(v);return n===null||n<0?null:n;}
  function bimCenM(v){var n=bimCenNum(v);return n===-555555555?0:(n===null||n<0?null:n);}
  function bimCenIdent(js,re,no){
    var R=(js&&js.results)||[],i,nm;
    for(i=0;i<R.length;i++){nm=String((R[i]&&R[i].layerName)||'');if(re.test(nm)&&!(no&&no.test(nm)))return R[i].attributes||{};}
    return null;
  }
  function bimCenRow(js){
    if(!Array.isArray(js)||js.length<2||!Array.isArray(js[0])||!Array.isArray(js[1]))return null;
    var o={},i;
    for(i=0;i<js[0].length;i++)o[js[0][i]]=js[1][i];
    return o;
  }
  function bimCenFacts(row){var o={},k;for(k in BIM_CEN_VARS)if(BIM_CEN_VARS.hasOwnProperty(k))o[k]=[bimCenE(row[BIM_CEN_VARS[k]+'E']),bimCenM(row[BIM_CEN_VARS[k]+'M'])];return o;}
  function bimCenPyr(row){
    var m=[],f=[];
    BIM_CEN_BANDS.forEach(function(b){
      var sm=0,sf=0,ok=true;
      b.forEach(function(i){var a=bimCenE(row['B01001_'+bimCen3(i)+'E']),c=bimCenE(row['B01001_'+bimCen3(i+24)+'E']);if(a===null||c===null)ok=false;else{sm+=a;sf+=c;}});
      m.push(ok?sm:null);f.push(ok?sf:null);
    });
    return {m:m,f:f};
  }
  /* a share and its margin of error, by the Census Bureau's formula for a derived proportion; where
     the term under the root is negative, its formula for a ratio */
  function bimCenShare(X,Y){
    if(!X||!Y||X[0]===null||Y[0]===null||!(Y[0]>0))return null;
    var p=X[0]/Y[0],r;
    if(X[1]===null||Y[1]===null)return [p,null];
    r=X[1]*X[1]-p*p*Y[1]*Y[1];
    if(r<0)r=X[1]*X[1]+p*p*Y[1]*Y[1];
    return [p,Math.sqrt(r)/Y[0]];
  }
  /* a sum and its margin of error: the root of the sum of the squares */
  function bimCenSum(L){
    var e=0,m=0,i;
    for(i=0;i<L.length;i++){if(!L[i]||L[i][0]===null)return null;e+=L[i][0];m=m===null||L[i][1]===null?null:m+L[i][1]*L[i][1];}
    return [e,m===null?null:Math.sqrt(m)];
  }
  /* the tract's ACS: this year's, or the year before's when this year's is not out */
  function bimCenAcs(y,G,again){
    var kv=bimCenKeyVars(),pv=bimCenPyrVars();
    return bimAccGet(bimCenAcsUrl(y,kv,'tract',G)).then(function(r0){
      if(!r0.ok&&r0.http&&!again)return bimCenAcs(y-1,G,true);
      if(!r0.ok)return {error:r0.err};
      return Promise.all([bimAccGet(bimCenAcsUrl(y,kv,'county',G)),bimAccGet(bimCenAcsUrl(y,kv,'state',G)),
        bimAccGet(bimCenAcsUrl(y,pv,'tract',G)),bimAccGet(bimCenAcsUrl(y,pv,'county',G))]).then(function(R){return {y:y,r:[r0].concat(R)};});
    });
  }
  function bimCenFetch(lat,lon){
    if(!bimCenInUS(lat,lon))return Promise.resolve({outside:true,errors:[]});
    return Promise.all([bimAccGet(bimCenIdUrl('Tracts_Blocks',lat,lon)),bimAccGet(bimCenIdUrl('State_County',lat,lon))]).then(function(R){
      var bad=[],tr=R[0].ok?bimCenIdent(R[0].js,/tract/i,/block/i):null,co=R[1].ok?bimCenIdent(R[1].js,/count/i):null,st=R[1].ok?bimCenIdent(R[1].js,/state/i,/count/i):null;
      if(!R[0].ok)bad.push(R[0].err);
      if(!R[1].ok)bad.push(R[1].err);
      if(!tr)return R[0].ok?{outside:true,errors:bad}:{error:bad.join('; '),errors:bad};
      var gid=String(tr.GEOID||''),G={st:String(tr.STATE||gid.slice(0,2)),co:String(tr.COUNTY||gid.slice(2,5)),tr:String(tr.TRACT||gid.slice(5,11))};
      if(!/^\d{2}$/.test(G.st)||!/^\d{3}$/.test(G.co)||!/^\d{6}$/.test(G.tr)){var m0='tigerweb.geo.census.gov named a tract without its codes';return {error:m0,errors:bad.concat([m0])};}
      var geo={tract:{name:String(tr.NAME||('Census Tract '+(tr.BASENAME||G.tr))),geoid:G.st+G.co+G.tr,aland:bimCenNum(tr.AREALAND)},
        county:{name:co?String(co.NAME||co.BASENAME||''):'',geoid:G.st+G.co,aland:co?bimCenNum(co.AREALAND):null},
        state:{name:st?String(st.NAME||st.BASENAME||''):'',geoid:G.st,aland:st?bimCenNum(st.AREALAND):null}};
      return bimCenAcs(bimCenYear(),G,false).then(function(A){
        if(A.error)return {error:A.error,errors:bad.concat([A.error])};
        var rows=A.r.map(function(r){if(!r.ok){bad.push(r.err);return null;}var row=bimCenRow(r.js);if(!row)bad.push('api.census.gov sent an answer that does not read');return row;});
        if(!rows[0]){var m1='api.census.gov sent no figures for the tract';return {error:m1,errors:bad.concat([m1])};}
        var nm=String(rows[0].NAME||'').split(/;\s*|,\s*/);
        if(!geo.county.name)geo.county.name=nm[1]||(rows[1]&&String(rows[1].NAME||'').split(/,\s*/)[0])||'';
        if(!geo.state.name)geo.state.name=nm[2]||(rows[2]&&String(rows[2].NAME||''))||'';
        var P={year:A.y,geo:geo,v:{tract:bimCenFacts(rows[0])},pyr:{},errors:bad,
          src:'U.S. Census Bureau, American Community Survey 5-year estimates, '+(A.y-4)+'–'+A.y,geoSrc:'U.S. Census Bureau, TIGERweb'};
        if(rows[1])P.v.county=bimCenFacts(rows[1]);
        if(rows[2])P.v.state=bimCenFacts(rows[2]);
        if(rows[3])P.pyr.tract=bimCenPyr(rows[3]);
        if(rows[4])P.pyr.county=bimCenPyr(rows[4]);
        return P;
      });
    });
  }
  /* ACCESSGET: the two sources at once; what comes is placed in one undo step */
  function bimAccHas(){var S=A3D.site&&A3D.site.access;return !!(S&&Array.isArray(S.segs));}
  function bimAccFetch(){
    if(A3D_ACC.busy){a3dToast('The access and people data are already on their way');return null;}
    var st=bimSunSettings(),org=bimMapOrigin();
    if(!org){a3dToast('Set the site latitude and longitude first (Properties, Site, Location): the walk times start at the site');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot fetch the access data');return null;}
    var L=bimAccLot(),rl=bimAccLotReach(L);
    if(rl>1500){a3dToast('The property line is '+bimClimFmt(rl/1000,1)+' km from the site\'s latitude and longitude: put the site at the lot first (FINDADDRESS, or Properties, Site)');return null;}
    var rn=BIM_ACC_MAXT*BIM_ACC_SPEED+rl+BIM_ACC_FRONT+50,rp=BIM_ACC_MAXT*BIM_ACC_SPEED+rl+BIM_ACC_FRONT;
    A3D_ACC.busy=true;
    a3dToast('Getting the streets, transit and daily needs within a '+BIM_ACC_MAXT+'-minute walk, and the census tract\'s people ...');
    return Promise.all([bimCtxOverpass(bimAccQuery(st.lat,st.lon,rn,rp),bimCtxSettings().overpass),bimCenFetch(st.lat,st.lon)]).then(function(R){
      A3D_ACC.busy=false;
      try{return bimAccApply(st.lat,st.lon,org,L,R[0],R[1]);}
      catch(eA){console.warn('[BIM] access and people',eA);a3dToast('The access data could not be worked out - see the console');return {error:String(eA)};}
    },function(e){A3D_ACC.busy=false;return {error:String(e)};});
  }
  function bimAccApply(lat,lon,org,L,osm,cen){
    var today=bimSaToday(),bad=[],A=null,P=null;
    if(osm&&osm.ok){A=bimAccWork(osm.js,org,L);if(A.error){bad.push(bimMapHost(osm.server)+': '+A.error);A=null;}else A.server=bimMapHost(osm.server);}
    else bad=bad.concat(osm&&osm.msgs&&osm.msgs.length?osm.msgs:['no Overpass server answered']);
    if(cen&&cen.error)bad=bad.concat(cen.errors&&cen.errors.length?cen.errors:[cen.error]);
    else if(cen){P=cen;bad=bad.concat(cen.errors||[]);}
    if(!A&&!P){a3dToast('No access or people data: '+bad.join('; '));return {error:bad.join('; ')};}
    pushUndo();
    undoSuspend=true;
    try{
      A3D.site=A3D.site||{};
      if(A){A.lat=lat;A.lon=lon;A.fetched=today;A.errors=bad.slice();A.src='OpenStreetMap contributors (ODbL), via Overpass ('+A.server+')';A3D.site.access=A;}
      if(P){delete P.errors;P.lat=lat;P.lon=lon;P.fetched=today;P.errors=bad.slice();A3D.site.people=P;}
      if(A&&!bimResLayers().some(function(R){return R.kind==='walk';}))bimResultLayerAdd('walk',{quiet:true});
      bimSaFill(true);
    }finally{undoSuspend=false;}
    refreshProps();refreshLayers();paint();saveSoon();
    if(typeof bimSaRefresh==='function')bimSaRefresh(true);
    if(typeof bimClbRefresh==='function')bimClbRefresh();
    var got=[];
    if(A){var w10=A.places.filter(function(p){return p.near.length&&p.near[0].t<=10;}).length;got.push('walk times, '+w10+' of '+A.places.length+' daily needs within 10 minutes, '+bimSaN(A.stops.length,'stop'));}
    if(P)got.push(P.outside?'the census covers US sites only':'census tract '+P.geo.tract.name);
    a3dToast('Access and people: '+got.join('; ')+(bad.length?'. Not available: '+bad.join('; '):'')+(A?'. The walk times are on the plan (Layers, Analysis)':''));
    return {access:!!A,people:!!(P&&!P.outside),outside:!!(P&&P.outside),stops:A?A.stops.length:null,errors:bad};
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
      A.push({auto:'access.transit',cat:'access',title:'Transit',value:tv.join('; ')+'. Stops and lines from OpenStreetMap; how often they run needs the operator\'s timetable (GTFS).',cls:cl,sev:sv,source:src,date:dt});
      if(S.lot.ring){
        var fs=S.streets||[];
        if(fs.length)A.push({auto:'access.frontage',cat:'access',title:'Frontage',value:'The lot fronts '+fs.map(function(f){var tx=bimAccStreetText(f);return bimAccStreetName(f)+(tx?' ('+tx+')':'')+' for '+bimClimFmt(f.len,0)+' m';}).join('; ')+'.',
          cls:fs.some(function(f){return f.c==='a';})?'constraint':'neutral',sev:1,source:S.src,date:dt});
        else A.push({auto:'access.frontage',cat:'access',title:'Frontage',value:'No street faces the lot line within '+S.front+' m: access must be secured another way (an easement or a private road).',cls:'constraint',sev:2,source:S.src,date:dt});
      }
      var C=S.conn;
      A.push({auto:'access.connectivity',cat:'access',title:'Connectivity',value:bimSaN(C.ix,'intersection')+' within '+C.r+' m of the '+(S.lot.ring?'lot':'site')+': '+bimClimFmt(C.dens,0)+' per km² ('+bimClimFmt(C.sqmi,0)+' per square mile), '+
        (C.sqmi>=90?'at or above':'below')+' LEED ND\'s 90 per square mile'+(C.dir!==null?'; the walks are '+C.dir.toFixed(2)+' times the straight line (the median of '+C.ndir+')':''),
        cls:C.sqmi>=300?'opportunity':(C.sqmi>=90?'neutral':'constraint'),sev:1,source:src+'; LEED ND v4 Neighborhood Pattern and Design',date:dt});
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
        '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="accboard">Open the board</button>'+
        (S?'<button type="button" class="a3d-anzbtn" data-saact="acclayer"'+(lay?' disabled title="The walk times are a layer already (Layers, Analysis)"':' title="Draw the walk times on the plan, under Analysis in Layers"')+'>Walk times layer</button>':'')+
        '<button type="button" class="a3d-anzbtn" data-saact="accget">Refresh</button></div>';
    }else s+='<p class="a3d-clsum">Walk times along the streets to daily needs and transit, the streets the lot fronts and how well they connect, and the census tract\'s people with their margins of error: from OpenStreetMap and the US Census, free.</p>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="accget">Get access and people</button><button type="button" class="a3d-anzbtn" data-saact="accboard">Open the board</button></div>';
    return s+'</div>';
  }"""

rep("""  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""", ENGINE + """

  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""")

# ---- commands ----
rep("""    ['CLIMATEGET',['GETCLIMATE','WEATHERDATA','CLIMATEDATA'],'climateget',""",
    """    ['ACCESSGET',['GETACCESS','CENSUSGET','WALKABILITYDATA'],'accessget','Get walk times to daily needs and transit, the streets the lot fronts, connectivity, and the census tract\\'s people, from OpenStreetMap and the US Census (free, no key)'],   /* __acad3dV161 */
    ['WALKTIMES',['WALKSHED','ISOCHRONES','SERVICEAREA'],'walktimes','Draw the walk times (5, 10 and 15 minutes along the streets from the lot) on the plan, as a layer under Analysis'],
    ['CLIMATEGET',['GETCLIMATE','WEATHERDATA','CLIMATEDATA'],'climateget',""")
rep("""    climateget:function(){bimClimFetch();},                      /* __acad3dV159 */""",
    """    climateget:function(){bimClimFetch();},                      /* __acad3dV159 */
    accessget:function(){bimAccFetch();},                        /* __acad3dV161 */
    walktimes:function(){bimResultLayerAdd('walk');},""")
rep("""    CLIMATEGET:'climate weather data temperature rain wind air quality earthquake fetch download era5 open-meteo usgs',""",
    """    CLIMATEGET:'climate weather data temperature rain wind air quality earthquake fetch download era5 open-meteo usgs',
    ACCESSGET:'access walk walking walkability transit bus stop train station subway metro tram ferry streets frontage census demographics population acs openstreetmap overpass fetch get data',   /* __acad3dV161 */
    WALKTIMES:'walk times walk shed walkshed isochrone isochrones service area network 5 10 15 minutes pedestrian catchment layer plan',""")

# ---- hooks, marker, version ----
rep("""  window.__acad3dV160='zoningrecord""", """  window.__acad3dV161='accessfetch,walknetwork,walktimes,frontageseeds,dailyneeds,parkedges,transitstops,routes,frontage,connectivity,directness,census,acs,moe,pyramid,accessfindings,walklayer';
  window.__a3dAccQuery=function(lat,lon,rn,rp){return bimAccQuery(lat,lon,rn,rp);};
  window.__a3dAccFetch=function(){return bimAccFetch();};
  window.__a3dAccBusy=function(){return !!A3D_ACC.busy;};
  window.__a3dAcc=function(){return JSON.parse(JSON.stringify({access:(A3D.site&&A3D.site.access)||null,people:(A3D.site&&A3D.site.people)||null}));};
  window.__a3dAccWork=function(js){var org=bimMapOrigin();if(!org)return {error:'no site place'};return JSON.parse(JSON.stringify(bimAccWork(js,org,bimAccLot())));};
  window.__a3dAccLot=function(){return bimAccLot();};
  window.__a3dAccAuto=function(){return bimAccAuto();};
  window.__a3dCenUrls=function(lat,lon,y,G){return bimCenUrls(lat,lon,y||bimCenYear(),G);};
  window.__a3dCenYear=function(){return bimCenYear();};
  window.__a3dCenShare=function(X,Y){return bimCenShare(X,Y);};
  window.__a3dCenSum=function(L){return bimCenSum(L);};
  window.__acad3dV160='zoningrecord""")
rep("""  var BIM_APP_VERSION={v:'V160',date:'2026-10-10'};   /* __acad3dV160 */""",
    """  var BIM_APP_VERSION={v:'V161',date:'2026-10-10'};   /* __acad3dV161 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
