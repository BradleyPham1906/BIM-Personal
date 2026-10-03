"""patch_phase133a.py -- V133: site context in one click, its engine.

- The area: a square of the context radius around the property lines, or model 0,0, turned into
  longitude and latitude by V132's georeferencing.
- OpenStreetMap through the Overpass API, one POST: buildings (ways and multipolygons), roads,
  water, green and trees. Buildings are extruded to their height tag, levels x 3 m, or an assumed
  6 m, said so; roads, water, green as sketches; trees as points.
- AWS Terrain Tiles (Terrarium): the tiles over the area decoded (R*256 + G + B/256 - 32768),
  sampled bilinearly on a grid into a V108 surface; the datum is the survey base's, or the ground
  at model 0,0, kept on the site.
- Everything on Context layers under one Context layer, pinned, with its source, credit, OSM id and
  tags; a fresh fetch replaces the kinds it brings, in one undo step; failures named per source.
- The credit line carries the context's credits; GeoJSON export writes context with its credit;
  context is not a mass for the usages."""
NAME = 'patch_phase133a.py'
BASE = 'e7d1a6001309b6bbced71d75664ae37b4cb1a1127af038c80783a31273e15de3'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


ENGINE = r"""  /* ================= __acad3dV133: site context in one click =================
     The buildings, roads, water, green and trees around the site from OpenStreetMap (through the
     Overpass API), and the ground from AWS Terrain Tiles, as ordinary pinned objects on Context
     layers -- saved with the project, so it opens offline. Nothing is asked until someone asks. */
  var BIM_CTX_KINDS=['buildings','roads','water','green','trees','terrain'];
  var BIM_CTX_LABEL={buildings:'Buildings',roads:'Roads',water:'Water',green:'Green',trees:'Trees',terrain:'Terrain'};
  var BIM_CTX_COL={buildings:'#c9ccd1',roads:'#8a8f98',water:'#4f8fd6',green:'#6dbb73',trees:'#3f9a52',terrain:'#b08559'};
  var BIM_OVERPASS_URL='https://overpass-api.de/api/interpreter';
  var BIM_TERRARIUM_URL='https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
  var BIM_CTX_OSM_CREDIT='© OpenStreetMap contributors (ODbL)';
  var BIM_CTX_TERRAIN_CREDIT='Terrain Tiles: Mapzen, AWS';
  var BIM_CTX_LEVEL_H=3,BIM_CTX_DEFAULT_H=6,BIM_CTX_MAX_FEATURES=5000,BIM_CTX_GRID=25,BIM_CTX_TZ=15;
  var A3D_CTX={busy:false};
  function bimCtxSettings(){
    var c=(A3D.site&&A3D.site.context)||{},k={},i;
    for(i=0;i<BIM_CTX_KINDS.length;i++)k[BIM_CTX_KINDS[i]]=!(c.kinds&&c.kinds[BIM_CTX_KINDS[i]]===false);
    return {radius:(typeof c.radius==='number'&&c.radius>=50&&c.radius<=1000)?c.radius:150,kinds:k,
      overpass:(typeof c.overpass==='string'&&c.overpass)?c.overpass:BIM_OVERPASS_URL};
  }
  /* one setting, one undo step; refused with its reason */
  function bimCtxSet(field,val){
    var st=bimCtxSettings(),nv,v,kk=null;
    if(field==='radius'){
      v=parseFloat(val);
      if(!isFinite(v)||v<50||v>1000){a3dToast('The context radius is from 50 to 1000 m');refreshProps();return false;}
      nv=Math.round(v);
      if(nv===st.radius)return true;
    }else if(field.indexOf('kind:')===0){
      kk=field.slice(5);
      if(BIM_CTX_KINDS.indexOf(kk)<0)return false;
      nv=!!val&&val!=='false'&&val!=='0';
      if(nv===st.kinds[kk])return true;
    }else if(field==='overpass'){
      nv=String(val==null?'':val).replace(/^\s+|\s+$/g,'')||BIM_OVERPASS_URL;
      if(!/^https?:\/\/[^\s\/]+\/\S*$/i.test(nv)){a3dToast('An Overpass server is a web address, like '+BIM_OVERPASS_URL);refreshProps();return false;}
      if(nv===st.overpass)return true;
    }else return false;
    pushUndo();
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    A3D.site.context=A3D.site.context||{};
    if(kk){A3D.site.context.kinds=A3D.site.context.kinds||{};A3D.site.context.kinds[kk]=nv;}
    else A3D.site.context[field]=nv;
    refreshProps();saveSoon();
    return true;
  }
  /* The area: a square, the context radius beyond the property lines (or around model 0,0), in
     model terms and as the longitude and latitude box that holds it. */
  function bimCtxArea(){
    var st=bimCtxSettings(),org=bimMapOrigin(),i,j,o,g,n=0,x0=Infinity,x1=-Infinity,z0=Infinity,z1=-Infinity;
    if(!org)return null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsProperty(o))continue;
      g=bimPropertyGeometry(o).ring||[];
      for(j=0;j<g.length;j++){x0=Math.min(x0,g[j][0]);x1=Math.max(x1,g[j][0]);z0=Math.min(z0,g[j][1]);z1=Math.max(z1,g[j][1]);n++;}
    }
    var cx=n?(x0+x1)/2:0,cz=n?(z0+z1)/2:0,h=(n?Math.max(x1-x0,z1-z0)/2:0)+st.radius;
    var C=[[cx-h,cz-h],[cx+h,cz-h],[cx+h,cz+h],[cx-h,cz+h]],lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,q;
    for(i=0;i<4;i++){
      q=bimModelToGeo(C[i][0],C[i][1],org);
      lo0=Math.min(lo0,q[0]);lo1=Math.max(lo1,q[0]);la0=Math.min(la0,q[1]);la1=Math.max(la1,q[1]);
    }
    return {cx:cx,cz:cz,half:h,s:la0,w:lo0,n:la1,e:lo1,org:org,fromProperty:n>0};
  }
  /* the Overpass QL for the kinds asked, each statement on the area's box; '' when none */
  function bimCtxQuery(a,k){
    var b='('+a.s.toFixed(7)+','+a.w.toFixed(7)+','+a.n.toFixed(7)+','+a.e.toFixed(7)+')',q=[];
    if(k.buildings)q.push('way["building"]'+b+';','relation["building"]["type"="multipolygon"]'+b+';');
    if(k.roads)q.push('way["highway"]'+b+';');
    if(k.water)q.push('way["natural"="water"]'+b+';','relation["natural"="water"]'+b+';','way["water"]'+b+';','way["waterway"]'+b+';');
    if(k.green)q.push('way["leisure"="park"]'+b+';','way["landuse"~"^(grass|forest|meadow|recreation_ground|village_green)$"]'+b+';',
      'way["natural"~"^(wood|scrub|grassland)$"]'+b+';');
    if(k.trees)q.push('node["natural"="tree"]'+b+';');
    return q.length?'[out:json][timeout:25];('+q.join('')+');out geom;':'';
  }
  function bimOsmKind(el){
    var t=el.tags||{};
    if(el.type==='node')return t.natural==='tree'?'trees':'';
    if(t.building&&t.building!=='no')return 'buildings';
    if(t.highway)return 'roads';
    if(t.natural==='water'||t.water||t.waterway)return 'water';
    if(t.leisure==='park'||/^(grass|forest|meadow|recreation_ground|village_green)$/.test(t.landuse||'')||/^(wood|scrub|grassland)$/.test(t.natural||''))return 'green';
    return '';
  }
  /* a multipolygon's member ways of one role, joined end to end into closed rings of [lon, lat] */
  function bimOsmRings(members,role){
    var segs=[],rings=[],i,r,s,e,grew;
    (members||[]).forEach(function(m){
      if(m&&m.type==='way'&&(m.role||'outer')===role&&m.geometry&&m.geometry.length>1)
        segs.push(m.geometry.map(function(g){return [g.lon,g.lat];}));
    });
    function same(p,q){return p[0]===q[0]&&p[1]===q[1];}
    while(segs.length){
      r=segs.shift();grew=true;
      while(!same(r[0],r[r.length-1])&&grew){
        grew=false;
        for(i=0;i<segs.length;i++){
          s=segs[i];e=r[r.length-1];
          if(same(s[0],e))r=r.concat(s.slice(1));
          else if(same(s[s.length-1],e))r=r.concat(s.slice(0,-1).reverse());
          else if(same(s[s.length-1],r[0]))r=s.slice(0,-1).concat(r);
          else if(same(s[0],r[0]))r=s.slice(1).reverse().concat(r);
          else continue;
          segs.splice(i,1);grew=true;break;
        }
      }
      if(r.length>=4&&same(r[0],r[r.length-1]))rings.push(r);
    }
    return rings;
  }
  /* a building's height: its height tag (metres, or feet when it says so), else levels x 3 m, else assumed */
  function bimOsmHeight(t){
    t=t||{};
    var m=/^\s*([0-9]*\.?[0-9]+)\s*(m|metres|meters|ft|feet|')?\s*$/i.exec(String(t.height||'').replace(/,/g,'.')),v,L;
    if(m){
      v=parseFloat(m[1]);
      if(m[2]&&/^(ft|feet|')$/i.test(m[2]))v*=0.3048;
      if(v>0&&v<1000)return {h:v,from:'height'};
    }
    L=parseFloat(t['building:levels']);
    if(isFinite(L)&&L>0&&L<300)return {h:L*BIM_CTX_LEVEL_H,from:'levels'};
    return {h:BIM_CTX_DEFAULT_H,from:'assumed'};
  }
  /* Overpass's answer as features in model terms: areas (outer and inner rings), a line, a point */
  function bimCtxFeatures(js,org){
    var out=[],els=(js&&js.elements)||[],i;
    function M(p){var m=bimGeoToModel(p[0],p[1],org);return [m[0],m[1]];}
    for(i=0;i<els.length&&out.length<BIM_CTX_MAX_FEATURES;i++){
      var el=els[i]||{},kind=bimOsmKind(el),f,g,cl;
      if(!kind)continue;
      f={kind:kind,osm:el.type,id:el.id,tags:el.tags||{},outer:[],inner:[],line:null,point:null};
      if(el.type==='node'){if(isFinite(el.lat)&&isFinite(el.lon))f.point=M([el.lon,el.lat]);}
      else if(el.type==='way'&&el.geometry&&el.geometry.length>1){
        g=el.geometry.map(function(p){return [p.lon,p.lat];});
        cl=g.length>=4&&g[0][0]===g[g.length-1][0]&&g[0][1]===g[g.length-1][1];
        if(cl&&(kind==='buildings'||kind==='green'||(kind==='water'&&!f.tags.waterway)))f.outer.push(g.slice(0,-1).map(M));
        else f.line={pts:(cl?g.slice(0,-1):g).map(M),closed:cl};
      }else if(el.type==='relation'){
        bimOsmRings(el.members,'outer').forEach(function(r){f.outer.push(r.slice(0,-1).map(M));});
        bimOsmRings(el.members,'inner').forEach(function(r){f.inner.push(r.slice(0,-1).map(M));});
      }
      if(f.point||(f.line&&f.line.pts.length>=2)||f.outer.length)out.push(f);
    }
    return {features:out,truncated:i<els.length};
  }
  /* ---- the ground: Terrarium tiles, decoded and sampled ---- */
  function bimCtxTerrainRange(a){
    var z,x0,x1,y0,y1;
    for(z=BIM_CTX_TZ;z>1;z--){
      x0=Math.floor(bimLonToTileX(a.w,z));x1=Math.floor(bimLonToTileX(a.e,z));
      y0=Math.floor(bimLatToTileY(a.n,z));y1=Math.floor(bimLatToTileY(a.s,z));
      if((x1-x0+1)*(y1-y0+1)<=9)break;
    }
    return {z:z,x0:x0,x1:x1,y0:y0,y1:y1};
  }
  /* a tile's pixels as metres: R*256 + G + B/256 - 32768 */
  function bimCtxDecode(blob){
    function read(img){
      var c=document.createElement('canvas'),w=img.width,h=img.height,x,d,e,i;
      c.width=w;c.height=h;
      x=c.getContext('2d',{willReadFrequently:true});
      x.drawImage(img,0,0);
      d=x.getImageData(0,0,w,h).data;e=new Float32Array(w*h);
      for(i=0;i<w*h;i++)e[i]=d[i*4]*256+d[i*4+1]+d[i*4+2]/256-32768;
      return {w:w,h:h,elev:e};
    }
    if(typeof createImageBitmap==='function')return createImageBitmap(blob,{premultiplyAlpha:'none',colorSpaceConversion:'none'}).then(read);
    return new Promise(function(res,rej){
      var u=URL.createObjectURL(blob),im=new Image();
      im.onload=function(){URL.revokeObjectURL(u);try{res(read(im));}catch(eR){rej(eR);}};
      im.onerror=function(){URL.revokeObjectURL(u);rej({bad:true});};
      im.src=u;
    });
  }
  function bimCtxTerrain(a){
    var R=bimCtxTerrainRange(a),jobs=[],T={},src={},x,y;
    function one(x,y){
      var u=BIM_TERRARIUM_URL.split('{z}').join(String(R.z)).split('{x}').join(String(x)).split('{y}').join(String(y));
      jobs.push(fetch(u).then(function(r){
        if(!r.ok)throw {http:r.status};
        var s=r.headers.get('x-amz-meta-x-imagery-sources')||'';
        String(s).split(/\s*,\s*/).forEach(function(v){if(v)src[v]=1;});
        return r.blob();
      }).then(bimCtxDecode).then(function(tl){T[x+'_'+y]=tl;}));
    }
    try{for(y=R.y0;y<=R.y1;y++)for(x=R.x0;x<=R.x1;x++)one(x,y);}
    catch(eF){return Promise.resolve({ok:false,err:eF});}
    return Promise.all(jobs).then(function(){return {ok:true,tiles:T,range:R,sources:Object.keys(src).sort()};},
      function(e){return {ok:false,err:e};});
  }
  /* the ground at a longitude and latitude, bilinear between pixel centres; NaN off the tiles */
  function bimCtxElevAt(ter,lon,lat){
    var R=ter.range,any=ter.tiles[R.x0+'_'+R.y0],S=any?any.w:256;
    var gx=bimLonToTileX(lon,R.z)*S-0.5,gy=bimLatToTileY(lat,R.z)*S-0.5,ix=Math.floor(gx),iy=Math.floor(gy),fx=gx-ix,fy=gy-iy;
    function px(i,j){
      i=Math.max(R.x0*S,Math.min((R.x1+1)*S-1,i));j=Math.max(R.y0*S,Math.min((R.y1+1)*S-1,j));
      var tl=ter.tiles[Math.floor(i/S)+'_'+Math.floor(j/S)];
      return tl?tl.elev[(j-Math.floor(j/S)*S)*tl.w+(i-Math.floor(i/S)*S)]:NaN;
    }
    return (px(ix,iy)*(1-fx)+px(ix+1,iy)*fx)*(1-fy)+(px(ix,iy+1)*(1-fx)+px(ix+1,iy+1)*fx)*fy;
  }
  /* the elevation at model y 0: the survey base's when V108 set one, else the one kept from the first fetch */
  function bimCtxDatum(){
    var b=A3D.site&&A3D.site.surveyBase;
    if(b&&isFinite(b.z))return b.z*(BIM_SURVEY_UNITS[b.units]||1);
    return (A3D.site&&isFinite(A3D.site.terrainBase))?A3D.site.terrainBase:null;
  }
  /* ---- the layers: one Context layer, a sub-layer for each kind ---- */
  function bimCtxLayers(){
    var par=bimLayerByName('Context')||bimLayerNew({name:'Context',color:'#9aa3ad'})||A3D.layers[0],L={},i,k,ly;
    for(i=0;i<BIM_CTX_KINDS.length;i++){
      k=BIM_CTX_KINDS[i];
      ly=bimLayerByName('Context '+k)||bimLayerNew({name:'Context '+k,color:BIM_CTX_COL[k],parent:par.id});
      L[k]=ly?ly.id:par.id;
    }
    return L;
  }
  function bimCtxCleanTags(t){
    var o={},k,n=0;
    for(k in t)if(t.hasOwnProperty(k)&&n<60){n++;o[String(k).slice(0,60)]=String(t[k]).slice(0,300);}
    return o;
  }
  function bimCtxErr(host,e){
    if(e&&(e.http===429||e.http===504))return host+' is busy (HTTP '+e.http+'): try again in a minute';
    if(e&&e.http)return host+' answered HTTP '+e.http;
    if(e&&e.bad)return host+' sent an answer that does not read';
    return host+' could not be reached (offline, or it does not allow browser access)';
  }
  /* CONTEXT: one press, one request to each source; what comes is placed in one undo step */
  function bimCtxFetch(){
    if(A3D_CTX.busy){a3dToast('The site context is already on its way');return null;}
    var a=bimCtxArea(),st=bimCtxSettings(),k=st.kinds,q,names=[],i;
    if(!a){a3dToast('Set the site latitude and longitude first, or find an address: the context is placed around the site');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot fetch the context');return null;}
    q=bimCtxQuery(a,k);
    if(!q&&!k.terrain){a3dToast('Tick at least one kind of context to get');return null;}
    for(i=0;i<BIM_CTX_KINDS.length;i++)if(k[BIM_CTX_KINDS[i]])names.push(BIM_CTX_LABEL[BIM_CTX_KINDS[i]].toLowerCase());
    A3D_CTX.busy=true;
    a3dToast('Getting the site context: '+names.join(', ')+', '+st.radius+' m around the '+(a.fromProperty?'property':'site')+' ...');
    var pOsm=q?fetch(st.overpass,{method:'POST',body:'data='+encodeURIComponent(q),headers:{'Content-Type':'application/x-www-form-urlencoded'}})
      .then(function(r){
        if(!r.ok)throw {http:r.status};
        return r.text();
      }).then(function(tx){
        var js;
        try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
        if(!js||!js.elements)throw {bad:true};
        return {ok:true,js:js};
      }).then(null,function(e){return {ok:false,err:e};}):Promise.resolve(null);
    var pTer=k.terrain?bimCtxTerrain(a):Promise.resolve(null);
    return Promise.all([pOsm,pTer]).then(function(r){
      A3D_CTX.busy=false;
      try{return bimCtxApply(a,st,r[0],r[1]);}
      catch(eA){console.warn('[BIM] site context',eA);a3dToast('The site context could not be placed - see the console');return {error:String(eA)};}
    },function(e){A3D_CTX.busy=false;console.warn('[BIM] site context',e);return {error:String(e)};});
  }
  function bimCtxApply(a,st,osm,ter){
    var k=st.kinds,bad=[],feats=null,trunc=false,i,j,f,o,c,n={buildings:0,roads:0,water:0,green:0,trees:0,terrain:0},ids=[],assumed=0,yards=0;
    if(osm){
      if(osm.ok){var fr=bimCtxFeatures(osm.js,a.org);feats=fr.features;trunc=fr.truncated;}
      else bad.push(bimCtxErr(bimMapHost(st.overpass),osm.err));
    }
    if(ter&&!ter.ok)bad.push(bimCtxErr('s3.amazonaws.com',ter.err));
    var terOk=!!(ter&&ter.ok);
    if(!feats&&!terOk){a3dToast('No site context: '+bad.join('; '));return {error:bad.join('; ')};}
    var repl={};
    if(feats)for(i=0;i<5;i++)if(k[BIM_CTX_KINDS[i]])repl[BIM_CTX_KINDS[i]]=1;
    if(terOk)repl.terrain=1;
    var L=null,y0=bimShadowGround(),base=null,date=new Date().toISOString().slice(0,10);
    function ground(p){
      if(!terOk||base===null)return null;
      var gg2=bimModelToGeo(p[0],p[1],a.org),e2=bimCtxElevAt(ter,gg2[0],gg2[1]);
      return isFinite(e2)?Math.round((e2-base)*100)/100:null;
    }
    function rec(kind,f2){return {kind:kind,source:'OpenStreetMap',credit:BIM_CTX_OSM_CREDIT,osm:f2.osm,id:f2.id,tags:bimCtxCleanTags(f2.tags),fetched:date};}
    function place(x,kind){x.layer=L[kind];x.col=BIM_CTX_COL[kind];x.locked=true;n[kind]++;ids.push(x.id);}
    var selWas=A3D.sel,setWas=(A3D.selSet||[]).slice();
    pushUndo();
    undoSuspend=true;
    try{
      /* what this fetch brings replaces what an earlier one brought, kind by kind */
      A3D.objs=A3D.objs.filter(function(x){return !(x.context&&repl[x.context.kind]);});
      if(A3D.sel&&!objById(A3D.sel)){A3D.sel=null;A3D.selSet=[];}
      L=bimCtxLayers();   /* new layers are not made current, so the current one stays */
      if(terOk){
        base=bimCtxDatum();
        if(base===null){
          var e0=bimCtxElevAt(ter,a.org.lon,a.org.lat);
          if(isFinite(e0)){base=Math.round(e0*100)/100;A3D.site.terrainBase=base;}
        }
        var pts=[],N=BIM_CTX_GRID,gx,gz,gg,ev;
        for(i=0;i<N;i++)for(j=0;j<N;j++){
          gx=a.cx-a.half+2*a.half*i/(N-1);gz=a.cz-a.half+2*a.half*j/(N-1);
          gg=bimModelToGeo(gx,gz,a.org);ev=bimCtxElevAt(ter,gg[0],gg[1]);
          if(isFinite(ev)&&base!==null)pts.push([gx,gz,Math.round((ev-base)*1000)/1000,'','Terrain Tiles']);
        }
        o=pts.length>=3?bimCreateTerrain(pts,{format:'Terrarium',units:'m',source:'AWS Terrain Tiles',zoom:ter.range.z},true):null;
        if(o){
          o.name='Terrain';o.layer=L.terrain;o.locked=true;
          o.context={kind:'terrain',source:'AWS Terrain Tiles',credit:BIM_CTX_TERRAIN_CREDIT+(ter.sources.length?' ('+ter.sources.join(', ')+')':''),
            zoom:ter.range.z,sources:ter.sources,datum:base,fetched:date};
          n.terrain=1;ids.push(o.id);
        }
      }
      for(i=0;feats&&i<feats.length;i++){
        f=feats[i];
        if(f.kind==='buildings'){
          var hh=bimOsmHeight(f.tags);
          for(j=0;j<f.outer.length;j++){
            var Pp=sketchCCW(f.outer[j]),mesh=null;
            if(Pp.length<3)continue;
            try{mesh=padMesh(Pp,y0,hh.h);}catch(eM){mesh=null;}
            if(!mesh)continue;
            var cx=0,cz=0,q2;
            for(q2=0;q2<Pp.length;q2++){cx+=Pp[q2][0];cz+=Pp[q2][1];}
            o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',pos:[0,0,0],mesh:mesh,
              name:String(f.tags.name||((f.tags['addr:housenumber']&&f.tags['addr:street'])?f.tags['addr:housenumber']+' '+f.tags['addr:street']:('Building '+(n.buildings+1)))).slice(0,60)};
            c=rec('buildings',f);c.height=Math.round(hh.h*100)/100;c.heightFrom=hh.from;c.footprint=Pp;
            c.ground=ground([cx/Pp.length,cz/Pp.length]);
            if(f.inner.length){c.courtyards=f.inner.length;yards+=f.inner.length;}
            o.context=c;A3D.objs.push(o);place(o,'buildings');
            if(hh.from==='assumed')assumed++;
          }
        }else if(f.kind==='trees'&&f.point){
          o=bimAddPoint(f.point[0],f.point[1],y0,L.trees);
          o.name='Tree '+(n.trees+1);o.context=rec('trees',f);place(o,'trees');
        }else{
          var label=f.tags.name||f.tags.ref||(BIM_CTX_LABEL[f.kind]+' '+(n[f.kind]+1));
          if(f.line){
            o=bimMakeImportedSketch(f.line.pts,y0,f.line.closed);
            if(o){o.name=String(label).slice(0,60);o.context=rec(f.kind,f);place(o,f.kind);}
          }
          for(j=0;j<f.outer.length+f.inner.length;j++){
            var ring=j<f.outer.length?f.outer[j]:f.inner[j-f.outer.length];
            if(ring.length<3)continue;
            o=bimMakeImportedSketch(ring,y0,true);
            if(!o)continue;
            o.name=String(label).slice(0,60);o.context=rec(f.kind,f);
            if(j>=f.outer.length)o.context.part='hole';
            place(o,f.kind);
          }
        }
      }
      A3D.site.context=A3D.site.context||{};
      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc};
    }finally{undoSuspend=false;}
    /* the selection stays what it was: the surface maker selects what it makes */
    A3D.sel=objById(selWas)?selWas:null;A3D.sel2=null;
    A3D.selSet=setWas.filter(function(id){return !!objById(id);});
    refreshTree();refreshLayers();refreshProps();paint();saveSoon();
    var said=[],kk;
    for(i=0;i<BIM_CTX_KINDS.length;i++){kk=BIM_CTX_KINDS[i];if(repl[kk])said.push(n[kk]+' '+(kk==='terrain'?(n[kk]?'surface':'surfaces'):BIM_CTX_LABEL[kk].toLowerCase()));}
    a3dToast('Site context: '+said.join(', ')+(assumed?'; '+assumed+' building height'+(assumed===1?'':'s')+' assumed ('+BIM_CTX_DEFAULT_H+' m)':'')+
      (yards?'; '+yards+' courtyard'+(yards===1?'':'s')+' filled':'')+(trunc?'; stopped at '+BIM_CTX_MAX_FEATURES+' features':'')+
      (bad.length?'; '+bad.join('; '):''));
    return {counts:n,ids:ids,errors:bad,truncated:trunc,assumed:assumed,courtyards:yards};
  }
  /* CONTEXTREMOVE: every context object, in one undo step */
  function bimCtxRemove(){
    var n=0,i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].context)n++;
    if(!n){a3dToast('There is no site context to remove');return 0;}
    pushUndo();
    A3D.objs=A3D.objs.filter(function(o){return !o.context;});
    if(A3D.sel&&!objById(A3D.sel)){A3D.sel=null;A3D.sel2=null;A3D.selSet=[];}
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast('Site context removed: '+n+' object'+(n===1?'':'s'));
    return n;
  }
  /* the context's credits, for the line over the viewport; OSM's left out when the map already gives it */
  function bimCtxCreditHtml(skipOsm){
    var osm=false,ter=null,i,o,p=[];
    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(!o.context)continue;if(o.context.kind==='terrain')ter=o.context;else osm=true;}
    if(osm&&!skipOsm)p.push('Context <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">© OpenStreetMap contributors</a>');
    if(ter)p.push(bimEsc(ter.credit||BIM_CTX_TERRAIN_CREDIT));
    return p.join(' · ');
  }
"""

rep("""  function bimGlRender(V,W,H){""", ENGINE + """  function bimGlRender(V,W,H){""")

# the credit line carries the context's credits
rep("""    var h=bimMapFooterHtml();""", """    var h=bimMapFooterHtml(),cc=bimCtxCreditHtml(h.indexOf('OpenStreetMap contributors')>=0);   /* __acad3dV133 */
    if(cc)h=h?h+' · '+cc:cc;""")

# context is not a mass for the usages
rep("""    if(!o)return '';
    if(o.t==='room'&&o.pts)return 'room';""", """    if(!o)return '';
    if(o.context)return '';   /* __acad3dV133: a neighbour is not the project's */
    if(o.t==='room'&&o.pts)return 'room';""")

# GeoJSON export: a context building as its footprint, and every context object with its credit
rep("""      }else if(bimUsageTarget(o)==='mass'){""", """      }else if(o.context&&o.context.footprint){   /* __acad3dV133 */
        ap=o.context.footprint;kind='context';geom={type:'Polygon',coordinates:[ring(ap,q)]};
      }else if(bimUsageTarget(o)==='mass'){""")
rep("""      pr.name=o.name||'';pr.kind=kind;""", """      pr.name=o.name||'';pr.kind=kind;
      if(o.context){   /* __acad3dV133: the source's tags, and its credit with them */
        for(k in o.context.tags)if(o.context.tags.hasOwnProperty(k)&&!pr.hasOwnProperty(k))pr[k]=o.context.tags[k];
        pr.name=o.name||'';pr.kind='context '+o.context.kind;pr.source=o.context.source;pr.credit=o.context.credit;
        if(o.context.osm){pr.osm_type=o.context.osm;pr.osm_id=o.context.id;}
        if(o.context.height)pr.height=o.context.height;
      }""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
