"""patch_phase166b.py -- V166: movement, the six analyses, each a layer of Analyze site.

reference/research-site-analysis-in-model.md, section 4. Each reads the access data Analyze site keeps
(V161's walk times, places and stops; V166's mv), so each runs again offline:
  streets   the street hierarchy: every street and path within 800 m by its class, the heavier the line
            the higher the class; names and speeds on the main ones; the lot's frontage named
  cycling   level of traffic stress (Mekuria, Furth and Nixon, 2012) from the tags, speed and lanes
            assumed by class where unmapped (as the noise analysis assumes); the uncontrolled crossings
            of main streets by the 2016 table; the low-stress reach: the streets the lot reaches at
            LTS 2 or less within a 25% detour. Off at first: it colours the same streets
  transit   the stops within 8 minutes (bus) and 12 (rail, metro, light rail, tram), their lines; the
            catchment along the streets; the bus and tram routes along their streets; the way to the
            nearest stop and station; PTAL (TfL's method) where every line's headway is mapped, a floor
            where some are, else why not
  walk      the streets and paths reached in 5, 10 and 15 minutes. Off at first: it colours the same
            streets as the hierarchy
  needs     the way to the nearest of each daily need, its minutes, the design guides' 400 and 800 m
  vehicles  the driveways and service roads at the lot with an arrow where each enters it, or a
            provisional entry on the frontage of its lowest street; the doors on the lot; car parks and
            garage entrances within 400 m; parking along the streets by side
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '64b40f3cb3d5239c2a1447a9fa86dd4ffe6615a754aa137ee91d08d86401d2d4'   # after patch_phase166a.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimMvWork(' in txt, 'run patch_phase166a.py first'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


MOVE = r"""  /* ================= __acad3dV166: site analysis in the model III, movement: the six analyses =================
     reference/research-site-analysis-in-model.md, section 4. Each reads A3D.site.access: V161's walk times,
     places and stops, and mv, the streets with their tags, the crossings, doors, car parks, lines and paths. */
  /* the classes, by OpenStreetMap's highway value as the usual crosswalk to the FHWA's has them; one hue,
     the higher class the brighter on the dark plan and the darker on a light map (both checked) */
  var BIM_MV_CLASSES=[
    {id:'mt',name:'Motorway and trunk',re:/^(motorway|trunk)(_link)?$/,w:5.5,dk:'#f6c780',lt:'#6e2a0a'},
    {id:'ar',name:'Arterial',re:/^primary(_link)?$/,w:4.4,dk:'#e99d4c',lt:'#9e4313'},
    {id:'co',name:'Collector',re:/^(secondary|tertiary)(_link)?$/,w:3.3,dk:'#cf7a33',lt:'#c2641d'},
    {id:'lo',name:'Local street',re:/^(residential|unclassified|living_street|road)$/,w:2.2,dk:'#a85a26',lt:'#d98a2b'},
    {id:'sv',name:'Service road',re:/^service$/,w:1.2,dk:'#8b9098',lt:'#7a7f87'},
    {id:'pa',name:'Path',re:/^(pedestrian|footway|path|cycleway|bridleway|steps|track)$/,w:1.3,dk:'#6fc6a0',lt:'#2e8a62',dash:[5,4]}];
  /* level of traffic stress: the reference palette's blue, aqua, yellow and red, checked for colour
     blindness on the dark plan and on a light map; each level is named in words on its streets too */
  var BIM_MV_LTS=[null,{n:'LTS 1',w:'carefree',dk:'#3987e5',lt:'#2a78d6'},{n:'LTS 2',w:'easygoing',dk:'#199e70',lt:'#1baf7a'},
    {n:'LTS 3',w:'tense',dk:'#c98500',lt:'#eda100'},{n:'LTS 4',w:'white knuckles',dk:'#e34948',lt:'#e34948'}];
  /* the 2016 table for an unsignalized crossing without a refuge: rows by the crossed street's speed (up to
     25 mph, 30, 35, 40 and over), columns by its lanes (up to 3, 4 to 5, 6 or more). In km/h the rows end at
     41, 51 and 61, so 40, 50 and 60 km/h and 25, 30 and 35 mph each fall in their own (bimMvRow) */
  var BIM_MV_XTAB=[[1,2,4],[1,2,4],[2,3,4],[3,4,4]];
  /* the daily needs in the reference palette's fixed order */
  var BIM_MV_NEED_COLS={dk:['#3987e5','#d95926','#199e70','#c98500','#d55181','#008300','#9085e9'],lt:['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#6250d6']};
  /* the design guides' walks: 400 m to green space, 800 m to shops and a primary school */
  var BIM_MV_GUIDE={food:800,learn:800,parks:400};
  /* PTAL: the walk to a stop (8 minutes to a bus, 12 to rail; trams and light rail taken as rail, TfL's own
     figures for them not read), the reliability allowance, and the bands of the accessibility index */
  var BIM_MV_PTAL_WALK={bus:8,tram:12,metro:12,rail:12,light:12},BIM_MV_PTAL_K={bus:2,tram:0.75,metro:0.75,rail:0.75,light:0.75};
  var BIM_MV_PTAL=[[2.5,'1a'],[5,'1b'],[10,'2'],[15,'3'],[20,'4'],[25,'5'],[40,'6a'],[Infinity,'6b']];
  function bimMvOf(){var S=A3D.site&&A3D.site.access;return S&&S.mv&&Array.isArray(S.mv.w)&&Array.isArray(S.mv.x)&&Array.isArray(S.mv.t)?S.mv:null;}
  function bimMvWhyNot(){
    var S=A3D.site&&A3D.site.access;
    if(!S)return 'Not fetched yet: Analyze site gets the streets and their tags from OpenStreetMap';
    if(S.mv&&S.mv.error)return 'The movement data could not be worked out: '+String(S.mv.error).slice(0,160);
    return 'The access data is from before V166: Analyze site again for the streets\' details';
  }
  function bimMvLight(){var s=bimMapSettings().style;return s==='street'||s==='custom';}
  function bimMvCol(o){return bimMvLight()?o.lt:o.dk;}
  function bimMvClassOf(hw){var i;hw=String(hw||'');for(i=0;i<BIM_MV_CLASSES.length;i++)if(BIM_MV_CLASSES[i].re.test(hw))return BIM_MV_CLASSES[i];return null;}
  function bimMvPts(mv,rec,y){var L=[],k;for(k=1;k<rec.length;k++)L.push([mv.x[rec[k]],y,mv.z[rec[k]]]);return L;}
  function bimMvSeg(mv,a,b){return Math.sqrt((mv.x[b]-mv.x[a])*(mv.x[b]-mv.x[a])+(mv.z[b]-mv.z[a])*(mv.z[b]-mv.z[a]));}
  function bimMvLen(mv,rec){var s=0,k;for(k=2;k<rec.length;k++)s+=bimMvSeg(mv,rec[k-1],rec[k]);return s;}
  function bimMvKm(m){return m<1000?Math.round(m)+' m':bimClimFmt(m/1000,1)+' km';}
  function bimMvSrc(A){return 'OpenStreetMap contributors (ODbL), via Overpass ('+((A&&A.server)||'Overpass')+'), '+((A&&A.fetched)||'');}
  function bimMvLotOf(A){return A&&A.lot&&A.lot.ring?{ring:A.lot.ring}:{ring:null,pt:[0,0]};}
  /* the point of some lines nearest a plan point */
  function bimMvNearest(lines,c){
    var best=null,bd=Infinity,i,k;
    for(i=0;i<lines.length;i++)for(k=0;k<lines[i].length;k++){var p=lines[i][k],d=(p[0]-c[0])*(p[0]-c[0])+(p[2]-c[1])*(p[2]-c[1]);if(d<bd){bd=d;best=p;}}
    return best;
  }
  /* a speed limit in km/h: a number (km/h), with mph, walk, none, or a country's urban, rural or zone */
  function bimMvKmhOf(s){
    s=String(s==null?'':s).replace(/^\s+|\s+$/g,'');
    if(!s)return null;
    var m=/^(\d+(?:\.\d+)?)\s*(mph|km\/h|kmh|kph)?$/i.exec(s);
    if(m){var v=parseFloat(m[1]);return v>0?(m[2]&&/mph/i.test(m[2])?v*1.609344:v):null;}
    if(/^walk$/i.test(s))return 7;
    if(/^none$/i.test(s))return 130;
    if(/^GB:nsl_single$/i.test(s))return 96.6;
    if(/^GB:(nsl_dual|motorway)$/i.test(s))return 112.7;
    if(/:living_street$/i.test(s))return 20;
    if(/:urban$/i.test(s))return 50;
    if(/:rural$/i.test(s))return 90;
    if(/:motorway$/i.test(s))return 120;
    m=/:zone:?(\d+)$/i.exec(s);
    return m?parseFloat(m[1]):null;
  }
  function bimMvSpeedText(t){
    var s=String(t.maxspeed||'').replace(/^\s+|\s+$/g,''),v;
    if(!s)return '';
    if(/^\d+(\.\d+)?$/.test(s))return s+' km/h';
    if(/^\d+(\.\d+)?\s*mph$/i.test(s))return s.replace(/\s*mph$/i,' mph');
    v=bimMvKmhOf(s);
    return v?s+' ('+Math.round(v)+' km/h)':s;
  }
  function bimMvRow(v){return v<=41?0:(v<=51?1:(v<=61?2:3));}
  function bimMvOneway(t){return /^(yes|1|true|-1)$/.test(String(t.oneway||''))||t.junction==='roundabout';}
  /* the speed: mapped, or the class's as the noise analysis assumes it */
  function bimMvSpeed(t,base){
    var v=bimMvKmhOf(t.maxspeed),z;
    if(v)return {v:v,src:'mapped'};
    z=/:(\d+)$/.exec(String(t['zone:maxspeed']||''));
    if(z)return {v:parseFloat(z[1]),src:'mapped as a zone'};
    var rc=BIM_DG_ROADS[base];
    return {v:rc?rc.v:(base==='service'?20:(base==='track'?30:40)),src:'assumed'};
  }
  /* the lanes, both ways: mapped, or the class's (half of them on one carriageway of a divided road) */
  function bimMvLanes(t,base){
    var n=parseInt(t.lanes,10),f=parseInt(t['lanes:forward'],10),b=parseInt(t['lanes:backward'],10),rc=BIM_DG_ROADS[base],ow=bimMvOneway(t);
    if(n>0&&n<20)return {v:n,src:'mapped'};
    if(f>0||b>0)return {v:(f>0?f:0)+(b>0?b:0),src:'mapped'};
    if(rc)return {v:ow?Math.max(1,Math.ceil(rc.l/2)):rc.l,src:'assumed'};
    return {v:ow?1:2,src:'assumed'};
  }
  /* the bike facility: a track (separated), a lane, or none */
  function bimMvFacility(t){
    var K=['cycleway','cycleway:both','cycleway:left','cycleway:right'],lane=false,i,v;
    for(i=0;i<K.length;i++){v=String(t[K[i]]||'');if(/^(track|opposite_track)$/.test(v))return 'track';if(/^(lane|opposite_lane)$/.test(v))lane=true;}
    if(t['shoulder:access:bicycle']==='yes')lane=true;
    return lane?'lane':'';
  }
  function bimMvLaneWidth(t){
    var K=['cycleway:width','cycleway:both:width','cycleway:right:width','cycleway:left:width'],i,v;
    for(i=0;i<K.length;i++){v=parseFloat(t[K[i]]);if(v>0&&v<10)return v;}
    return null;
  }
  /* parking by side: true, false or null where not mapped; the street parking scheme and the older lanes */
  function bimMvParking(t){
    function side(s){
      var v=t['parking:'+s];if(v===undefined)v=t['parking:both'];
      if(v!==undefined){v=String(v);if(/^(lane|street_side|on_kerb|half_on_kerb|shoulder|yes|parallel|diagonal|perpendicular)$/.test(v))return true;if(/^(no|separate)$/.test(v))return false;}
      var o=t['parking:lane:'+s];if(o===undefined)o=t['parking:lane:both'];
      if(o!==undefined){o=String(o);if(/^(parallel|diagonal|perpendicular|marked|yes|inline|orthogonal)$/.test(o))return true;if(/^(no|no_parking|no_stopping|fire_lane|separate)$/.test(o))return false;}
      return null;
    }
    return {l:side('left'),r:side('right')};
  }
  function bimMvParkText(p){
    if(p.l===null&&p.r===null)return 'not mapped';
    function w(v){return v===true?'parking':(v===false?'none':'not mapped');}
    return p.l===p.r?w(p.l)+' on both sides':'left: '+w(p.l)+'; right: '+w(p.r);
  }
  /* a street's level of traffic stress by the 2012 criteria (MTI report 11-19): 0 where a bicycle may not
     ride; the why in words, and what was assumed */
  function bimMvLts(t){
    var hw=String(t.highway||''),base=hw.replace(/_link$/,''),bi=String(t.bicycle||''),r={lts:0,why:'',sp:null,ln:null,fac:'',pk:null};
    if(/^(no|use_sidepath|dismount)$/.test(bi)){r.why='cycling is not allowed (bicycle='+bi+')';return r;}
    if(base==='motorway'&&!/^(yes|designated|permissive)$/.test(bi)){r.why='a motorway';return r;}
    if(/^(no|private)$/.test(String(t.access||''))&&!/^(yes|designated|permissive|destination)$/.test(bi)){r.why='no public access';return r;}
    if(hw==='steps'){r.why='steps';return r;}
    if(hw==='cycleway'){r.lts=1;r.why='a cycleway, separated from traffic';r.fac='separated path';return r;}
    if(hw==='path'){r.lts=1;r.why='a path, separated from traffic';r.fac='separated path';return r;}
    if(/^(footway|pedestrian|bridleway)$/.test(hw)){
      if(/^(yes|designated|permissive)$/.test(bi)){r.lts=1;r.why='a '+(hw==='pedestrian'?'pedestrian street':hw)+' where cycling is allowed';r.fac='separated path';}
      else r.why='a '+(hw==='pedestrian'?'pedestrian street':hw)+', cycling not signed as allowed';
      return r;
    }
    if(hw==='track'){r.lts=2;r.why='a track';return r;}
    if(t.motor_vehicle==='no'||t.motorcar==='no'){r.lts=1;r.why='closed to motor traffic';return r;}
    if(hw==='living_street'||t.bicycle_road==='yes'||t.cyclestreet==='yes'){r.lts=1;r.why=hw==='living_street'?'a living street':'a cycle street';return r;}
    var fac=bimMvFacility(t),sp=bimMvSpeed(t,base),ln=bimMvLanes(t,base),pk=bimMvParking(t),v=sp.v,n=ln.v,ow=bimMvOneway(t),pd=ow?n:Math.ceil(n/2);
    r.fac=fac==='track'?'cycle track':(fac==='lane'?'bike lane':'none');r.sp=sp;r.ln=ln;r.pk=pk;
    if(fac==='track'){r.lts=1;r.why='a cycle track, separated from traffic';return r;}
    if(base==='service'&&bimMvRow(v)===0){r.lts=2;r.why='a service road';return r;}
    var kmh=Math.round(v)+' km/h';
    if(fac==='lane'){
      if(pk.l===true||pk.r===true){   /* a bike lane beside parking: the lanes each way, the speed */
        var a1=pd<=1?1:3,a2=[1,2,3,4][bimMvRow(v)];
        r.lts=Math.max(a1,a2);
        r.why='a bike lane beside parking: '+(pd<=1?'one lane':pd+' lanes')+' each way (LTS '+a1+'), '+kmh+' (LTS '+a2+'); the lane and parking widths not counted';
      }else{   /* a bike lane with no parking: the lanes each way (two on a divided road's carriageway), the width, the speed */
        var b1=pd<=1?1:((pd===2&&ow)?2:3),bw=bimMvLaneWidth(t),b3=bw===null?1:(bw>=1.8?1:2),b2=[1,1,3,4][bimMvRow(v)];
        r.lts=Math.max(b1,b2,b3);
        r.why='a bike lane, no parking: '+(pd<=1?'one lane':pd+' lanes')+' each way (LTS '+b1+'), '+(bw===null?'its width not mapped':bimDispNum(bw,1)+' m wide (LTS '+b3+')')+', '+kmh+' (LTS '+b2+')';
      }
      return r;
    }
    /* mixed traffic: the speed and the lanes, the lower level on a residential street of under 3 lanes */
    var res=(/^(residential|unclassified)$/.test(base)||t.lane_markings==='no')&&n<=2,lv;
    var row=bimMvRow(v);
    if(row===0)lv=n<=3?(res?1:2):(n<=5?3:4);
    else if(row===1)lv=n<=3?(res?2:3):4;
    else lv=4;
    r.lts=lv;
    r.why='mixed traffic: '+kmh+', '+n+' lane'+(n===1?'':'s')+(res?(t.lane_markings==='no'?', no centre line':', a '+base+' street'):'')+' (LTS '+lv+')';
    return r;
  }
  /* every way's level, and the crossings: where a street at LTS 2 or less meets a main street (trunk,
     primary, secondary, tertiary) of another name with no signal or all-way stop within 20 m, the 2016
     table by the main street's speed and lanes; past LTS 2 it bars the minor street's way through */
  function bimMvStress(mv){
    var W=[],inc={},X=[],pen={},i,k;
    for(i=0;i<mv.w.length;i++){var rec=mv.w[i];W.push(bimMvLts(mv.t[rec[0]]||{}));for(k=1;k<rec.length;k++)(inc[rec[k]]||(inc[rec[k]]=[])).push(i);}
    var sig=(mv.xs||[]).filter(function(c){return /[sa]/.test(c[2]);});
    Object.keys(inc).forEach(function(key){
      var nd=+key,L=inc[key],mains=[],minors=[];
      if(L.length<2)return;
      L.forEach(function(wi){if(mains.indexOf(wi)>=0||minors.indexOf(wi)>=0)return;var t=mv.t[mv.w[wi][0]]||{};if(/^(trunk|primary|secondary|tertiary)$/.test(String(t.highway||'')))mains.push(wi);else if(W[wi].lts>=1&&W[wi].lts<=2)minors.push(wi);});
      if(!mains.length||!minors.length)return;
      var mn=mains.map(function(wi){return String((mv.t[mv.w[wi][0]]||{}).name||'');});
      minors=minors.filter(function(wi){var n=String((mv.t[mv.w[wi][0]]||{}).name||'');return !n||mn.indexOf(n)<0;});
      if(!minors.length)return;
      var x=mv.x[nd],z=mv.z[nd],ctl=sig.some(function(c){return (c[0]-x)*(c[0]-x)+(c[1]-z)*(c[1]-z)<=400;}),lv=0,top=null;
      mains.forEach(function(wi){
        var t=mv.t[mv.w[wi][0]]||{},base=String(t.highway),sp=bimMvSpeed(t,base),ln=bimMvLanes(t,base),
          v=BIM_MV_XTAB[bimMvRow(sp.v)][ln.v<=3?0:(ln.v<=5?1:2)];
        if(v>lv){lv=v;top={t:t,sp:sp,ln:ln};}
      });
      X.push({n:nd,x:x,z:z,lts:ctl?1:lv,ctl:ctl,main:top,minors:minors});
      if(!ctl&&lv>2)pen[nd]={lts:lv,minors:minors};
    });
    return {W:W,X:X,pen:pen};
  }
  /* Dijkstra by distance over the edges at or under a level */
  function bimMvDij(n,G,maxLv,seeds){
    var D=[],hk=[],hv=[],i;
    for(i=0;i<n;i++)D.push(Infinity);
    function push(key,v){var j=hk.length;hk.push(key);hv.push(v);while(j>0){var q=(j-1)>>1;if(hk[q]<=key)break;hk[j]=hk[q];hv[j]=hv[q];j=q;}hk[j]=key;hv[j]=v;}
    function pop(){var lk=hk.pop(),lv=hv.pop(),m=hk.length,j=0;if(!m)return;for(;;){var l=2*j+1,r=l+1,s=-1,sk=lk;if(l<m&&hk[l]<sk){s=l;sk=hk[l];}if(r<m&&hk[r]<sk){s=r;sk=hk[r];}if(s<0)break;hk[j]=hk[s];hv[j]=hv[s];j=s;}hk[j]=lk;hv[j]=lv;}
    seeds.forEach(function(s){if(s[1]<D[s[0]]){D[s[0]]=s[1];push(s[1],s[0]);}});
    while(hk.length){
      var t=hk[0],u=hv[0],e;pop();
      if(t>D[u])continue;
      for(e=G.head[u];e>=0;e=G.nxt[e]){if(G.lv[e]>maxLv)continue;var nt=t+G.len[e],w=G.to[e];if(nt<D[w]){D[w]=nt;push(nt,w);}}
    }
    return D;
  }
  /* the low-stress reach: from the lot over every street a bicycle may use, and over those at LTS 2 or less
     with their crossings; a piece is reached when both its ends are, the low-stress way at most 1.25
     times the shortest (Furth's detour). One-way streets are ridden both ways: a simplification */
  function bimMvReach(mv,ST,L){
    var n=mv.x.length,G={head:[],nxt:[],to:[],len:[],lv:[]},lvE={},i,k,seeds=[];
    for(i=0;i<n;i++)G.head.push(-1);
    function add(a,b,l,v){G.to.push(b);G.len.push(l);G.lv.push(v);G.nxt.push(G.head[a]);G.head[a]=G.to.length-1;}
    for(i=0;i<mv.w.length;i++){
      var rec=mv.w[i],w=ST.W[i].lts;
      if(!(w>=1))continue;
      for(k=2;k<rec.length;k++){
        var a=rec[k-1],b=rec[k],l=bimMvSeg(mv,a,b),v=w,pa=ST.pen[a],pb=ST.pen[b];
        if(pa&&pa.minors.indexOf(i)>=0)v=Math.max(v,pa.lts);
        if(pb&&pb.minors.indexOf(i)>=0)v=Math.max(v,pb.lts);
        lvE[i+':'+k]=v;add(a,b,l,v);add(b,a,l,v);
      }
    }
    for(i=0;i<n;i++){var d=bimAccLotDist(L,mv.x[i],mv.z[i]);if(d<=BIM_ACC_FRONT)seeds.push([i,d]);}
    if(!seeds.length){var bi=-1,bd=Infinity;for(i=0;i<n;i++){var d2=bimAccLotDist(L,mv.x[i],mv.z[i]);if(d2<bd&&G.head[i]>=0){bd=d2;bi=i;}}if(bi>=0)seeds.push([bi,bd]);}
    var Da=bimMvDij(n,G,4,seeds),Dl=bimMvDij(n,G,2,seeds),ok={};
    function fine(x){return isFinite(Dl[x])&&Dl[x]<=1.25*Da[x]+0.5;}
    for(i=0;i<mv.w.length;i++){
      var r2=mv.w[i];
      for(k=2;k<r2.length;k++){var vv=lvE[i+':'+k];if(vv>=1&&vv<=2&&fine(r2[k-1])&&fine(r2[k]))(ok[i]||(ok[i]={}))[k]=1;}
    }
    return {Da:Da,Dl:Dl,ok:ok,seeds:seeds};
  }
  /* PTAL, TfL's method: each line at its nearest stop within reach, its walk, half its headway and the
     reliability allowance its total access time; 30 over that its doorstep frequency; per mode the best in
     full, the rest at half; the sum the index. Lines without a mapped headway are left out and said */
  function bimMvPtalBand(ai){var i;if(!(ai>0))return '0';for(i=0;i<BIM_MV_PTAL.length;i++)if(ai<=BIM_MV_PTAL[i][0])return BIM_MV_PTAL[i][1];return '6b';}
  function bimMvPtal(A,mv){
    var best={},keys=[],modes={},ai=0,m;
    (A.stops||[]).forEach(function(s){
      (s.l||[]).forEach(function(l){
        var md=l[0],lim=BIM_MV_PTAL_WALK[md],k=md+'|'+l[1];
        if(!lim||!(s.t<=lim))return;
        if(!best[k]){best[k]={m:md,l:l[1],t:s.t,stop:s.n};keys.push(k);}
        else if(s.t<best[k].t){best[k].t=s.t;best[k].stop=s.n;}
      });
    });
    var L=keys.map(function(k){
      var b=best[k],iv=mv&&mv.iv?mv.iv[k]:null;
      b.iv=iv>0?iv:null;
      if(b.iv){b.k=BIM_MV_PTAL_K[b.m];b.tat=b.t+0.5*b.iv+b.k;b.edf=30/b.tat;}
      return b;
    });
    L.forEach(function(b){if(b.iv)(modes[b.m]||(modes[b.m]=[])).push(b.edf);});
    for(m in modes)if(modes.hasOwnProperty(m)){var E=modes[m].sort(function(a,b){return b-a;}),s=E[0],i;for(i=1;i<E.length;i++)s+=0.5*E[i];ai+=s;}
    var have=L.filter(function(b){return b.iv;}).length;
    return {lines:L,have:have,ai:Math.round(ai*100)/100,band:bimMvPtalBand(ai),floor:have>0&&have<L.length};
  }
  /* ---- 1. the street hierarchy ---- */
  function bimDgStreetsRun(S){
    var mv=bimMvOf(),A=A3D.site&&A3D.site.access,E=[],G={},order=[],cnt={},front={},y=S.y+0.06,i;
    if(!mv)return {E:[],run:{note:bimMvWhyNot()}};
    (A.streets||[]).forEach(function(f){if(f.n)front[f.n]=f;});
    for(i=0;i<mv.w.length;i++){
      var rec=mv.w[i],t=mv.t[rec[0]]||{},C=bimMvClassOf(t.highway);
      if(!C)continue;
      var nm=String(t.name||t.ref||'').slice(0,60),key=C.id+'|'+nm;
      if(!G[key]){G[key]={C:C,n:nm,lines:[],len:0,t:t};order.push(key);}
      G[key].lines.push(bimMvPts(mv,rec,y));G[key].len+=bimMvLen(mv,rec);
    }
    order.forEach(function(key){
      var g=G[key],C=g.C,t=g.t,fr=g.n?front[g.n]:null,sp=bimMvSpeedText(t),lb=[],nm=g.n||'Unnamed '+C.name.toLowerCase()+'s',cl=C.name.toLowerCase();
      cnt[C.id]=(cnt[C.id]||0)+1;
      var near=bimMvNearest(g.lines,S.c);
      if(fr)lb.push({t:'Frontage: '+g.n+', '+cl+(sp?', '+sp:''),p:near,sz:11,col:'#f4efe6',pri:1});
      else if(g.n&&/^(mt|ar|co)$/.test(C.id))lb.push({t:g.n+(sp?' \u00b7 '+sp:''),p:near,sz:10,col:'#e8e2d6',pri:3});
      var rows=[['Class',C.name+' (OpenStreetMap '+t.highway+')'],['Speed limit',sp||'not mapped'],['Lanes',t.lanes?String(t.lanes):'not mapped'],['One-way',bimMvOneway(t)?'yes':'no'],
        ['Sidewalks',String(t.sidewalk||t['sidewalk:both']||'not mapped')],['Length within '+(mv.cut||mv.r)+' m',bimMvKm(g.len)]];
      if(fr)rows.push(['The lot','fronts it for '+bimClimFmt(fr.len,0)+' m']);
      E.push({k:'street:'+key,name:nm+', '+cl,g:{kind:'lines',lines:g.lines},s:{stroke:bimMvCol(C),w:C.w+(fr?1.5:0),dash:C.dash||null,op:0.95},lb:lb,
        info:{title:nm+': '+cl+(fr?', the lot\'s frontage':''),rows:rows,
          method:'OpenStreetMap\'s highway value by the usual crosswalk to the FHWA\'s functional classes; the heavier the line, the higher the class',source:bimMvSrc(A)}});
    });
    return {E:E,run:{legend:BIM_MV_CLASSES.filter(function(C){return cnt[C.id];}).map(function(C){return {name:C.name,short:C.id==='mt'?'motorway':C.name.split(' ')[0].toLowerCase(),col:bimMvCol(C),kind:C.dash?'dash':'line'};}),
      source:'OpenStreetMap streets by class',note:E.length?(mv.cut?'The streets kept to '+mv.cut+' m of the lot, the nearest first':''):'No streets within '+mv.r+' m'}};
  }
  /* ---- 2. cycling: level of traffic stress, the crossings, the low-stress reach ---- */
  function bimDgCyclingRun(S){
    var mv=bimMvOf(),A=A3D.site&&A3D.site.access,E=[],y=S.y+0.07,light=bimMvLight(),i,k;
    if(!mv)return {E:[],run:{note:bimMvWhyNot()}};
    var ST=bimMvStress(mv),L=bimMvLotOf(A),R=bimMvReach(mv,ST,L),rl=[],okLen=0,allLen=0,front={},cnt=[0,0,0,0,0];
    (A.streets||[]).forEach(function(f){if(f.n)front[f.n]=1;});
    for(i=0;i<mv.w.length;i++){
      var rec=mv.w[i],cur=null;
      if(!(ST.W[i].lts>=1))continue;
      for(k=2;k<rec.length;k++){
        var a=rec[k-1],b=rec[k],l=bimMvSeg(mv,a,b);
        allLen+=l;
        if(R.ok[i]&&R.ok[i][k]){okLen+=l;if(!cur){cur=[[mv.x[a],y-0.01,mv.z[a]]];rl.push(cur);}cur.push([mv.x[b],y-0.01,mv.z[b]]);}
        else cur=null;
      }
    }
    var within=(mv.cut||mv.r)+' m',reachTitle='Reached from the lot at LTS 2 or less: '+bimMvKm(okLen)+' of the '+bimMvKm(allLen)+' of streets and paths a bicycle may use within '+within;
    if(rl.length)E.push({k:'reach',name:'Low-stress reach',g:{kind:'lines',lines:rl},s:{stroke:light?'#2a78d6':'#3987e5',w:11,op:0.22},
      info:{title:reachTitle,rows:[['Detour allowed','25% more than the shortest ride (Mekuria, Furth and Nixon)'],['Crossings','an uncontrolled crossing of a main street at LTS 3 or 4 breaks it'],['One-way streets','ridden both ways: a simplification']],
        method:'Two Dijkstras by distance from the lot: over every street a bicycle may use, and over those at LTS 2 or less with their crossings; a piece is reached when the low-stress distance to both its ends is at most 1.25 times the shortest',source:bimMvSrc(A)}});
    var G={},order=[];
    for(i=0;i<mv.w.length;i++){
      var r=ST.W[i];if(!(r.lts>=1))continue;
      var t=mv.t[mv.w[i][0]]||{},C=bimMvClassOf(t.highway)||BIM_MV_CLASSES[3],nm=String(t.name||t.ref||'').slice(0,60),key=r.lts+'|'+(nm||'u:'+C.id)+'|'+r.why;
      if(!G[key]){G[key]={lv:r.lts,n:nm,r:r,C:C,lines:[],len:0};order.push(key);}
      G[key].lines.push(bimMvPts(mv,mv.w[i],y));G[key].len+=bimMvLen(mv,mv.w[i]);
    }
    order.forEach(function(key){
      var g=G[key],r=g.r,Lv=BIM_MV_LTS[g.lv],nm=g.n||'Unnamed '+g.C.name.toLowerCase()+'s',lb=[];
      cnt[g.lv]++;
      if(g.n&&front[g.n])lb.push({t:g.n+': '+Lv.n+', '+Lv.w,p:bimMvNearest(g.lines,S.c),sz:11,col:'#eef3f8',pri:1});
      var rows=[['Level',Lv.n+' ('+Lv.w+')'],['Why',r.why]];
      if(r.sp)rows.push(['Speed',Math.round(r.sp.v)+' km/h, '+r.sp.src+(r.sp.src==='assumed'?' for the class (as the noise analysis assumes)':'')]);
      if(r.ln)rows.push(['Lanes',r.ln.v+', '+r.ln.src]);
      if(r.fac)rows.push(['Bike facility',r.fac]);
      if(r.pk)rows.push(['Parking',bimMvParkText(r.pk)]);
      rows.push(['Length',bimMvKm(g.len)]);
      E.push({k:'lts:'+key,name:nm+', '+Lv.n,g:{kind:'lines',lines:g.lines},s:{stroke:bimMvCol(Lv),w:Math.max(1.6,g.C.w*0.7+0.6),op:0.95},lb:lb,
        info:{title:nm+': '+Lv.n+', '+Lv.w,rows:rows,
          method:'Mekuria, Furth and Nixon\'s 2012 criteria (MTI report 11-19) from the OpenStreetMap tags: separated paths, bike lanes with and without parking, mixed traffic by speed and lanes; a street as stressful as its worst feature',source:bimMvSrc(A)}});
    });
    var xs=ST.X.filter(function(c){return !c.ctl&&c.lts>2;}).map(function(c){c.d=bimAccLotDist(L,c.x,c.z);return c;}).sort(function(a,b){return a.d-b.d;});
    if(xs.length)E.push({k:'crossings',name:'Stressful crossings',g:{kind:'line',pts:[],marks:xs.map(function(c,j){return {p:[c.x,y+0.02,c.z],t:j<3?'Crossing '+String(c.main.t.name||c.main.t.highway)+': LTS '+c.lts:''};})},
      s:{mark:BIM_MV_LTS[4].dk,markText:'#ffd9d6'},
      info:{title:xs.length+' crossing'+(xs.length===1?'':'s')+' of a main street with no signal or all-way stop, at LTS 3 or 4',
        rows:xs.slice(0,8).map(function(c){return [String(c.main.t.name||c.main.t.highway),'LTS '+c.lts+': '+Math.round(c.main.sp.v)+' km/h ('+c.main.sp.src+'), '+c.main.ln.v+' lanes ('+c.main.ln.src+'); '+Math.round(c.d)+' m from the lot'];}),
        method:'Furth, Mekuria and Nixon\'s 2016 table for an unsignalized crossing without a refuge, by the crossed street\'s speed and lanes; a refuge is not counted, which errs stressful; a signal or an all-way stop within 20 m controls it',source:bimMvSrc(A)}});
    var fs=(A.streets||[]).filter(function(f){return f.n;}).map(function(f){var j;for(j=0;j<order.length;j++)if(G[order[j]].n===f.n)return f.n+' '+BIM_MV_LTS[G[order[j]].lv].n;return '';}).filter(function(x){return x;});
    E.push({k:'site',name:'Cycling at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:[S.c[0],y,S.c[1]],r:4,col:bimMvCol(BIM_MV_LTS[1])},
      lb:[{t:'Low-stress reach: '+bimMvKm(okLen)+' of '+bimMvKm(allLen),p:[S.c[0],y,S.c[1]-S.r*0.35],col:'#cfe3ff',pri:1}],
      info:{title:reachTitle,rows:[['Frontage',fs.length?fs.join('; '):'no named street'],['Stressful crossings',String(xs.length)],['Streets by level',[1,2,3,4].map(function(v){return BIM_MV_LTS[v].n+' '+cnt[v];}).join(', ')]],
        method:'As the streets\' levels and the reach',source:bimMvSrc(A)}});
    var leg=[1,2,3,4].filter(function(v){return cnt[v];}).map(function(v){var Lv=BIM_MV_LTS[v];return {name:Lv.n+', '+Lv.w,short:Lv.n,col:bimMvCol(Lv),kind:'line'};});
    if(rl.length)leg.push({name:'Reached at low stress',short:'reach',col:light?'#2a78d6':'#3987e5',kind:'fill'});
    if(xs.length)leg.push({name:'Stressful crossing',short:'crossing',col:BIM_MV_LTS[4].dk,kind:'dot'});
    return {E:E,run:{legend:leg,source:'Level of traffic stress (Mekuria, Furth and Nixon) from OpenStreetMap'}};
  }
  /* the walk network's pieces between two walk times, as segments */
  function bimMvWalkBand(A,t0,t1,y){
    var out=[];
    (A.segs||[]).forEach(function(g){
      for(var i=4;i+2<g.length;i+=3){
        var x1=g[i-3],z1=g[i-2],a=g[i-1],x2=g[i],z2=g[i+1],b=g[i+2],cuts=[0,1],k;
        [t0,t1].forEach(function(T){if((a-T)*(b-T)<0)cuts.push((T-a)/(b-a));});
        cuts.sort(function(p,q){return p-q;});
        for(k=1;k<cuts.length;k++){
          var u=cuts[k-1],v=cuts[k],tm=a+(u+v)/2*(b-a);
          if(v-u<1e-9||tm<t0||tm>t1)continue;
          out.push([x1+u*(x2-x1),y,z1+u*(z2-z1)],[x1+v*(x2-x1),y,z1+v*(z2-z1)]);
        }
      }
    });
    return out;
  }
  function bimMvPathPts(p,y){var o=[],i;for(i=0;i+1<p.pts.length;i+=2)o.push([p.pts[i],y,p.pts[i+1]]);return o;}
  function bimMvPathLen(P){var s=0,i;for(i=1;i<P.length;i++)s+=Math.sqrt((P[i][0]-P[i-1][0])*(P[i][0]-P[i-1][0])+(P[i][2]-P[i-1][2])*(P[i][2]-P[i-1][2]));return s;}
  /* ---- 3. transit ---- */
  function bimDgTransitRun(S){
    var A=A3D.site&&A3D.site.access,mv=bimMvOf(),E=[],y=S.y+0.08,light=bimMvLight(),cR=light?'#2a78d6':'#3987e5',cB=light?'#eb6834':'#d95926',leg=[];
    if(!A||!Array.isArray(A.stops))return {E:[],run:{note:'Not fetched yet: Analyze site finds the stops and their lines'}};
    var c8=bimMvWalkBand(A,0,8,y-0.02),c12=bimMvWalkBand(A,8,12,y-0.02);
    if(c8.length)E.push({k:'catch8',name:'Within an 8-minute walk',g:{kind:'segs',pts:c8},s:{stroke:light?'#5d7fa8':'#9fb7d4',w:2.4,op:0.75},
      info:{title:'The streets within an 8-minute walk: PTAL\'s reach to a bus stop',rows:[['Speed','4.8 km/h (80 m a minute)']],method:'The walk times along the streets (V161)',source:A.src}});
    if(c12.length)E.push({k:'catch12',name:'8 to 12 minutes\' walk',g:{kind:'segs',pts:c12},s:{stroke:light?'#5d7fa8':'#9fb7d4',w:1.2,dash:[4,3],op:0.7},
      info:{title:'The streets 8 to 12 minutes\' walk away: PTAL\'s reach to a station',rows:[['Speed','4.8 km/h (80 m a minute)']],method:'The walk times along the streets (V161)',source:A.src}});
    /* the bus and tram routes along their streets, the heavier the more lines on a street */
    if(mv&&mv.rt){
      var on={},names={};
      mv.rt.forEach(function(rt){if(!/^(bus|tram)$/.test(rt.m))return;rt.w.forEach(function(wi){on[wi]=(on[wi]||0)+1;(names[wi]||(names[wi]=[])).push(rt.l);});});
      [[1,1,2],[2,3,3.4],[4,1e9,4.8]].forEach(function(b){
        var lines=[],j;
        Object.keys(on).forEach(function(k){var c=on[k];if(c>=b[0]&&c<=b[1]&&mv.w[+k])lines.push(bimMvPts(mv,mv.w[+k],y-0.01));});
        if(!lines.length)return;
        E.push({k:'routes'+b[0],name:'Bus and tram routes ('+(b[0]===b[1]?'one line':(b[1]>100?b[0]+' or more lines':b[0]+' to '+b[1]+' lines'))+')',g:{kind:'lines',lines:lines},s:{stroke:cB,w:b[2],op:0.55},
          info:{title:'Streets with '+(b[0]===b[1]?'one bus or tram line':(b[1]>100?b[0]+' or more lines':b[0]+' to '+b[1]+' lines')),rows:[['Pieces',String(lines.length)]],method:'The ways in each route relation that reaches the stops, within the streets kept',source:bimMvSrc(A)}});
        j=0;
      });
      if(Object.keys(on).length)leg.push({name:'Bus and tram routes',short:'routes',col:cB,kind:'line'});
    }
    /* the stops within reach */
    var shown=0;
    A.stops.forEach(function(s,j){
      var rail=s.m.some(function(m){return /^(metro|rail|light|tram)$/.test(m);}),lim=rail?12:8;
      if(!(s.t<=lim))return;
      shown++;
      var ln=s.l.map(function(l){return l[1];}),lt=ln.length>4?ln.slice(0,4).join(', ')+' +'+(ln.length-4):ln.join(', '),p=[s.x,y,s.z];
      E.push({k:'stop:'+s.n,name:s.n,g:{kind:'line',pts:[]},sym:{type:'dot',p:p,r:5,col:rail?cR:cB},
        lb:[{t:s.n+', '+bimAccMin(s.t)+(lt?': '+lt:''),p:p,sz:10,col:'#f1f4f8',al:'left',pri:2}],
        info:{title:s.n+': '+bimAccModesText(s)+', '+bimAccMin(s.t)+' on foot',rows:[['Lines',ln.length?ln.join(', '):'none mapped'],['Walk',bimAccMin(s.t)+' ('+s.d+' m as the crow flies)'],
          ['Within PTAL\'s reach',(rail?'12':'8')+' minutes for '+(rail?'rail, metro, light rail and tram':'a bus')]],method:'The stop\'s nodes grouped by name; the walk along the streets (V161)',source:A.src}});
    });
    if(shown){leg.push({name:'Bus stop',short:'bus',col:cB,kind:'dot'});if(A.stops.some(function(s){return s.m.some(function(m){return /^(metro|rail|light|tram)$/.test(m);});}))leg.push({name:'Rail, metro, light rail or tram',short:'rail',col:cR,kind:'dot'});}
    /* the way to the nearest stop and station */
    if(mv&&mv.paths)mv.paths.forEach(function(p){
      if(p.k!=='bus'&&p.k!=='rail')return;
      var P=bimMvPathPts(p,y);
      E.push({k:'way:'+p.k,name:'The way to the nearest '+(p.k==='bus'?'bus or tram stop':'station'),g:{kind:'line',pts:P},s:{stroke:p.k==='bus'?cB:cR,w:1.6,dash:[6,4],op:0.9},
        info:{title:'The nearest '+(p.k==='bus'?'bus or tram stop':'rail or metro station')+': '+bimAccMin(p.t)+' on foot, '+Math.round(bimMvPathLen(P))+' m along the streets',rows:[['Walk',bimAccMin(p.t)]],method:'The walk times traced back along the streets to the lot',source:A.src}});
    });
    if(c8.length)leg.push({name:'Within 8 minutes',short:'8 min',col:light?'#5d7fa8':'#9fb7d4',kind:'line'});
    if(c12.length)leg.push({name:'8 to 12 minutes',short:'12 min',col:light?'#5d7fa8':'#9fb7d4',kind:'dash'});
    /* PTAL at the site */
    var P=bimMvPtal(A,mv),lab,title;
    if(!P.lines.length){lab='No stop within PTAL\'s reach: PTAL 0';title='No bus stop within 8 minutes or station within 12: PTAL 0';}
    else if(!P.have){lab='No PTAL: how often the lines run is not mapped';title='PTAL needs each line\'s headway; OpenStreetMap maps it for none of the '+P.lines.length+' lines within reach';}
    else{lab='PTAL '+(P.floor?'at least ':'')+P.band+' (index '+bimDispNum(P.ai,1)+')';title=lab+(P.floor?': '+P.have+' of the '+P.lines.length+' lines within reach have a mapped headway; the rest are left out':'');}
    E.push({k:'ptal',name:'PTAL at the site',g:{kind:'line',pts:[]},sym:{type:'dot',p:[S.c[0],y,S.c[1]],r:4,col:cR},
      lb:[{t:lab,p:[S.c[0],y,S.c[1]+S.r*0.6],col:'#d9e9ff',pri:1}],
      info:{title:title,rows:P.lines.slice(0,12).map(function(b){return [BIM_ACC_MODES[b.m]+' '+b.l,b.stop+', '+bimAccMin(b.t)+(b.iv?'; every '+bimDispNum(b.iv,1)+' min; doorstep frequency '+bimDispNum(b.edf,2):'; headway not mapped')];}),
        method:'TfL\'s PTAL: the walk at 4.8 km/h (8 minutes to a bus, 12 to rail), half the headway, and 2 minutes (bus) or 0.75 (rail) for reliability make the access time; 30 over it the doorstep frequency; per mode the best in full and the rest at half. Headways from OpenStreetMap\'s interval',
        source:'OpenStreetMap stops and routes; TfL\'s method'}});
    return {E:E,run:{legend:leg,source:'Transit from OpenStreetMap; PTAL by TfL\'s method',note:shown?'':'No stop within reach'}};
  }
  /* ---- 4. walk times ---- */
  function bimDgWalkRun(S){
    var A=A3D.site&&A3D.site.access,E=[],cols=bimAccPlanCols(),y=S.y+0.05,names=['5 minutes or less','5 to 10 minutes','10 to 15 minutes'];
    if(!A||!Array.isArray(A.segs))return {E:[],run:{note:'Not fetched yet: Analyze site works out the walk times'}};
    names.forEach(function(nm,b){
      var P=bimMvWalkBand(A,b*5,(b+1)*5,y),far=null,bd=-1,i;
      if(!P.length)return;
      for(i=1;i<P.length;i+=2){var d=(P[i][0]-S.c[0])*(P[i][0]-S.c[0])+(P[i][2]-S.c[1])*(P[i][2]-S.c[1]);if(d>bd){bd=d;far=P[i];}}
      E.push({k:'w'+(b+1)*5,name:'Walk, '+nm,g:{kind:'segs',pts:P},s:{stroke:cols[b],w:b?2.4:3,op:0.95},lb:far?[{t:((b+1)*5)+' min',p:far,sz:10,col:'#e3eefb',pri:2}]:[],
        info:{title:'Streets and paths reached on foot in '+nm+' from the '+(A.lot&&A.lot.ring?'lot':'site'),rows:[['Length',bimMvKm(((A.reach&&A.reach.len&&A.reach.len[b])||0)*1000)],['Speed',bimClimFmt(A.speed*0.06,1)+' km/h ('+A.speed+' m a minute)']],
          method:'Dijkstra along the streets and paths from every point of the network within '+A.front+' m of the lot; sidewalks walked, not drawn',source:A.src}});
    });
    return {E:E,run:{legend:names.map(function(nm,b){return {name:nm,short:((b+1)*5)+' min',col:cols[b],kind:'line'};}),source:'Walk times along the streets (V161)'}};
  }
  /* ---- 5. daily needs: the way to the nearest of each kind ---- */
  function bimDgNeedsRun(S){
    var A=A3D.site&&A3D.site.access,mv=bimMvOf(),E=[],y=S.y+0.09,cols=BIM_MV_NEED_COLS[bimMvLight()?'lt':'dk'],leg=[];
    if(!A||!Array.isArray(A.places))return {E:[],run:{note:'Not fetched yet: Analyze site finds the daily needs'}};
    if(!mv)return {E:[],run:{note:bimMvWhyNot()}};
    BIM_ACC_KINDS.forEach(function(K,j){
      var P=null,path=null,q,col=cols[j%cols.length];
      A.places.forEach(function(p){if(p.k===K.id)P=p;});
      q=P&&P.near[0];
      if(!q)return;
      mv.paths.forEach(function(p){if(p.k===K.id)path=p;});
      var pts=path?bimMvPathPts(path,y):[],len=bimMvPathLen(pts),sub=K.sub[q.sub]||K.name,nm=q.n||sub,gd=BIM_MV_GUIDE[K.id],rows;
      rows=[['Kind',K.name],['Nearest',sub+(q.n?', '+q.n:'')],['Walk',bimAccMin(q.t)],['Along the streets',len?Math.round(len)+' m':'not traced'],['As the crow flies',q.d+' m'],['Within 10 minutes',String(P.n[1])+' of this kind']];
      if(gd)rows.push(['Design guides',(len&&len<=gd?'within':'beyond')+' the '+gd+' m they check'+(K.id==='parks'?' to green space':(K.id==='food'?' to shops':' to a primary school'))]);
      E.push({k:'need:'+K.id,name:K.name+': '+nm,g:{kind:'line',pts:pts},s:{stroke:col,w:2.2,op:0.95},sym:{type:'dot',p:[q.x,y,q.z],r:5,col:col},
        lb:[{t:sub+(q.n?', '+q.n:'')+': '+bimAccMin(q.t),p:[q.x,y,q.z],sz:10,col:'#f1f4f8',al:'left',pri:2}],
        info:{title:'The nearest '+sub.toLowerCase()+(q.n?', '+q.n:'')+': '+bimAccMin(q.t)+' on foot',rows:rows,method:'The walk times traced back along the streets from the place to the lot',source:A.src}});
      leg.push({name:K.name,short:K.id,col:col,kind:'line'});
    });
    return {E:E,run:{legend:leg,source:'Daily needs from OpenStreetMap; the walks along the streets',note:E.length?'':'No daily need within '+A.maxT+' minutes'}};
  }
  /* a line offset to one side in plan: left of its direction (side 1) or right (side -1) */
  function bimMvOffset(P,d,side){
    var o=[],i;
    for(i=0;i<P.length;i++){
      var a=P[Math.max(0,i-1)],b=P[Math.min(P.length-1,i+1)],dx=b[0]-a[0],dz=b[2]-a[2],l=Math.sqrt(dx*dx+dz*dz)||1;
      o.push([P[i][0]+side*d*dz/l,P[i][1],P[i][2]-side*d*dx/l]);
    }
    return o;
  }
  /* ---- 6. vehicle access and parking ---- */
  function bimDgVehiclesRun(S){
    var A=A3D.site&&A3D.site.access,mv=bimMvOf(),E=[],y=S.y+0.1,leg=[],i,k;
    if(!mv)return {E:[],run:{note:bimMvWhyNot()}};
    var L=bimMvLotOf(A),dw=[],arrows=[];
    for(i=0;i<mv.w.length;i++){
      var rec=mv.w[i],t=mv.t[rec[0]]||{};
      if(t.highway!=='service'||/^(parking_aisle|drive-through)$/.test(String(t.service||'')))continue;
      var near=Infinity,bk=-1;
      for(k=1;k<rec.length;k++){var d=bimAccLotDist(L,mv.x[rec[k]],mv.z[rec[k]]);if(d<near){near=d;bk=k;}}
      if(near>40)continue;
      dw.push({rec:rec,t:t,d:near,k:bk});
      if(near<=3){   /* it reaches the lot: an arrow into it where it does, from 10 m back along it */
        var nd=rec[bk],pin=bimMvLotPt(L,mv.x[nd],mv.z[nd]),nb=bk>1?rec[bk-1]:(rec.length>bk+1?rec[bk+1]:null);
        if(bk>1&&rec.length>bk+1&&bimAccLotDist(L,mv.x[rec[bk+1]],mv.z[rec[bk+1]])>bimAccLotDist(L,mv.x[rec[bk-1]],mv.z[rec[bk-1]]))nb=rec[bk+1];
        if(nb!==null){var dx=mv.x[nb]-pin[0],dz=mv.z[nb]-pin[1],l=Math.sqrt(dx*dx+dz*dz)||1,f=Math.min(1,10/l);arrows.push({from:[pin[0]+dx*f,y+0.02,pin[1]+dz*f],to:[pin[0],y+0.02,pin[1]],t:t,prov:false});}
      }
    }
    if(dw.length)E.push({k:'driveways',name:'Driveways and service roads at the lot',g:{kind:'lines',lines:dw.map(function(w){return bimMvPts(mv,w.rec,y);})},s:{stroke:'#aab3be',w:2,op:0.9},
      info:{title:dw.length+' driveway'+(dw.length===1?'':'s')+' or service road'+(dw.length===1?'':'s')+' within 40 m of the lot',rows:dw.slice(0,8).map(function(w){return [String(w.t.name||(w.t.service?w.t.service:'service road')),Math.round(w.d)+' m from the lot'+(w.t.access?', access '+w.t.access:'')];}),method:'OpenStreetMap\'s service roads (driveways and alleys among them), parking aisles left out',source:bimMvSrc(A)}});
    /* no driveway reaches the lot: a provisional entry on the frontage of its lowest street, as a parameter plan marks one */
    if(!arrows.length&&L.ring&&A.streets&&A.streets.length){
      var pref={s:0,l:1,c:2,a:3},best=null;
      A.streets.forEach(function(f){if(!(f.c in pref)||!f.pcs||!f.pcs.length)return;if(!best||pref[f.c]<pref[best.c]||(pref[f.c]===pref[best.c]&&f.len>best.len))best=f;});
      if(best){
        var pc=best.pcs[0],bl=0;best.pcs.forEach(function(q){var ql=Math.sqrt((q[2]-q[0])*(q[2]-q[0])+(q[3]-q[1])*(q[3]-q[1]));if(ql>bl){bl=ql;pc=q;}});
        var mx=(pc[0]+pc[2])/2,mz=(pc[1]+pc[3])/2,ex=pc[2]-pc[0],ez=pc[3]-pc[1],el=Math.sqrt(ex*ex+ez*ez)||1,nx=-ez/el,nz=ex/el;
        if(bimPointInPoly([mx+nx*2,mz+nz*2],L.ring)){nx=-nx;nz=-nz;}
        arrows.push({from:[mx+nx*10,y+0.02,mz+nz*10],to:[mx,y+0.02,mz],t:{name:best.n},prov:true,f:best});
      }
    }
    arrows.forEach(function(ar,j){
      var cls=ar.f?bimAccStreetClass(ar.f):'';
      E.push({k:'entry:'+j,name:ar.prov?'Vehicle entry, provisional':'Vehicle entry',g:{kind:'line',pts:[ar.from,ar.to]},s:{stroke:'#f2f5f8',w:2.6,head:true,dash:ar.prov?[5,3]:null},
        lb:[{t:ar.prov?'Entry, provisional: from '+(ar.t.name||'the '+cls)+(ar.f&&ar.f.c==='a'?' (an arterial: an entry may be refused)':''):'Entry'+(ar.t.name?': '+ar.t.name:''),p:ar.from,sz:10,col:'#f2f5f8',al:'left',pri:2}],
        info:{title:ar.prov?'A provisional vehicle entry from '+(ar.t.name||'the '+cls)+', the lot\'s lowest street':'Where a driveway enters the lot',rows:ar.prov?[['Street',(ar.t.name||'unnamed')+', '+cls],['Why here','the lowest class of street the lot fronts, at its longest frontage: an entry on an arterial may be refused']]:[['Driveway',String(ar.t.name||ar.t.service||'service road')]],
          method:ar.prov?'Parameter plans mark vehicle entries provisional until the detailed design; the lot\'s frontage from the walk network (V161)':'The driveway\'s point nearest the lot',source:bimMvSrc(A)}});
    });
    if(dw.length)leg.push({name:'Driveway or service road',short:'driveway',col:'#aab3be',kind:'line'});
    if(arrows.length)leg.push({name:arrows[0].prov?'Vehicle entry, provisional':'Vehicle entry',short:'entry',col:'#f2f5f8',kind:arrows[0].prov?'dash':'line'});
    /* the doors on the lot */
    if(mv.en&&mv.en.length){
      E.push({k:'doors',name:'Entrances on the lot',g:{kind:'line',pts:[],marks:mv.en.map(function(d){return {p:[d[0],y+0.03,d[1]],t:'Entrance'+(d[2]&&d[2]!=='yes'?' ('+d[2]+')':'')+(d[3]?' '+d[3]:'')};})},s:{mark:'#ffffff',markText:'#f2f5f8'},
        info:{title:mv.en.length+' entrance'+(mv.en.length===1?'':'s')+' mapped on the lot',rows:mv.en.slice(0,8).map(function(d){return ['Entrance',(d[2]||'yes')+(d[3]?', '+d[3]:'')];}),method:'OpenStreetMap\'s entrance nodes on the lot',source:bimMvSrc(A)}});
      leg.push({name:'Entrance',short:'door',col:'#ffffff',kind:'dot'});
    }
    /* car parks within 400 m */
    (mv.cp||[]).forEach(function(c,j){
      var ring=[];for(i=0;i+1<c.ring.length;i+=2)ring.push([c.ring[i],y-0.04,c.ring[i+1]]);
      if(ring.length<3)return;
      var kind=c.k?c.k.replace(/_/g,' '):'car park',priv=/^(private|no|customers|permit)$/.test(c.ac),cx=0,cz=0;
      ring.forEach(function(p){cx+=p[0];cz+=p[2];});cx/=ring.length;cz/=ring.length;
      E.push({k:'carpark:'+j,name:'Car park'+(c.n?', '+c.n:''),g:{kind:'line',pts:ring,closed:true,bands:[{lv:0,col:'#7d8a9c',rings:[ring]}]},s:{stroke:'#9aa6b6',w:1,fill:'#7d8a9c',fop:0.38},
        lb:[{t:'Car park'+(c.n?' '+c.n:'')+': '+kind+(c.cap?', '+c.cap+' spaces':'')+(c.t!==null?', '+bimAccMin(c.t):'')+(priv?' ('+c.ac+')':''),p:[cx,y,cz],sz:10,col:'#e6ebf1',pri:3}],
        info:{title:'Car park'+(c.n?' '+c.n:'')+', '+c.d+' m from the lot',rows:[['Kind',kind],['Spaces',c.cap?String(c.cap):'not mapped'],['Access',c.ac||'not mapped'],['Fee',c.fee||'not mapped'],['Walk',c.t!==null?bimAccMin(c.t):'not reached'],['Area',bimDispNum(c.a,0)+' m\u00b2']],
          method:'OpenStreetMap\'s amenity=parking areas within 400 m; the walk to the nearest point of the edge',source:bimMvSrc(A)}});
    });
    if(mv.cp&&mv.cp.length)leg.push({name:'Car park',short:'car park',col:'#7d8a9c',kind:'fill'});
    if(mv.pe&&mv.pe.length){
      E.push({k:'garages',name:'Garage entrances',g:{kind:'line',pts:[],marks:mv.pe.map(function(g){return {p:[g[0],y+0.03,g[1]],t:'Garage entrance'+(g[3]?' '+g[3]:'')};})},s:{mark:'#c9d1db',markText:'#e6ebf1'},
        info:{title:mv.pe.length+' garage entrance'+(mv.pe.length===1?'':'s')+' within 400 m',rows:mv.pe.slice(0,8).map(function(g){return [g[3]||'Garage entrance',(g[2]!==null?bimAccMin(g[2]):'not reached')+(g[4]?', access '+g[4]:'')];}),method:'OpenStreetMap\'s amenity=parking_entrance nodes',source:bimMvSrc(A)}});
      leg.push({name:'Garage entrance',short:'garage',col:'#c9d1db',kind:'dot'});
    }
    /* parking along the streets within 150 m, by side */
    var ol=[];
    for(i=0;i<mv.w.length;i++){
      var r2=mv.w[i],t2=mv.t[r2[0]]||{},pk=bimMvParking(t2),dmin=Infinity;
      if(pk.l!==true&&pk.r!==true)continue;
      for(k=1;k<r2.length;k++)dmin=Math.min(dmin,bimAccLotDist(L,mv.x[r2[k]],mv.z[r2[k]]));
      if(dmin>150)continue;
      var P2=bimMvPts(mv,r2,y-0.02);
      if(pk.l===true)ol.push(bimMvOffset(P2,4.5,1));
      if(pk.r===true)ol.push(bimMvOffset(P2,4.5,-1));
    }
    if(ol.length){
      E.push({k:'onstreet',name:'Parking along the streets',g:{kind:'lines',lines:ol},s:{stroke:'#c9d1db',w:1.4,dash:[3,3],op:0.85},
        info:{title:'Parking along '+ol.length+' street side'+(ol.length===1?'':'s')+' within 150 m of the lot',rows:[['Mapped as','parking:left, :right or :both (and the older parking:lane)']],method:'OpenStreetMap\'s street parking tags, each side drawn 4.5 m off the street\'s line',source:bimMvSrc(A)}});
      leg.push({name:'Parking along the street',short:'on-street',col:'#c9d1db',kind:'dash'});
    }
    return {E:E,run:{legend:leg,source:'Vehicle access and parking from OpenStreetMap',note:E.length?'':'No driveway, door or car park mapped near the lot'}};
  }
"""

# the analyses, after V165's six; cycling and walk times colour the same streets as the hierarchy, so they start hidden
rep("    {id:'flood',name:'Flood zones',col:'#3d85d8'}];\n",
    "    {id:'flood',name:'Flood zones',col:'#3d85d8'},\n"
    "    /* __acad3dV166: movement; cycling and walk times colour the streets the hierarchy does, so they start hidden */\n"
    "    {id:'streets',name:'Street hierarchy',col:'#e99d4c'},\n"
    "    {id:'cycling',name:'Cycling stress',col:'#3987e5',hidden:true},\n"
    "    {id:'transit',name:'Transit',col:'#d95926'},\n"
    "    {id:'walk',name:'Walk times',col:'#5598e7',hidden:true},\n"
    "    {id:'needs',name:'Daily needs',col:'#199e70'},\n"
    "    {id:'vehicles',name:'Vehicle access',col:'#aab3be'}];\n")
rep("    contours:bimDgContoursRun,slope:bimDgSlopeRun,aspect:bimDgAspectRun,flow:bimDgFlowRun,ponds:bimDgPondsRun,flood:bimDgFloodRun};   /* __acad3dV165 */\n",
    "    contours:bimDgContoursRun,slope:bimDgSlopeRun,aspect:bimDgAspectRun,flow:bimDgFlowRun,ponds:bimDgPondsRun,flood:bimDgFloodRun,   /* __acad3dV165 */\n"
    "    streets:bimDgStreetsRun,cycling:bimDgCyclingRun,transit:bimDgTransitRun,walk:bimDgWalkRun,needs:bimDgNeedsRun,vehicles:bimDgVehiclesRun};   /* __acad3dV166 */\n")
rep("  /* ================= __acad3dV165: site analysis in the model II, land and water =================\n",
    MOVE + "  /* ================= __acad3dV165: site analysis in the model II, land and water =================\n")

assert all(ord(ch) < 128 for ch in MOVE), 'non-ASCII in the movement analyses'
out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
