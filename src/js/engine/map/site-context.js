  /* ================= __acad3dV133: site context in one click =================
     The buildings, roads, water, green and trees around the site from OpenStreetMap (through the
     Overpass API), and the ground from AWS Terrain Tiles, as ordinary pinned objects on Context
     layers -- saved with the project, so it opens offline. Nothing is asked until someone asks. */
  var BIM_CTX_KINDS=['buildings','roads','water','green','trees','rail','airports','power','landuse','terrain'];   /* __acad3dV157: rail, airports, power, land use */
  var BIM_CTX_LABEL={buildings:'Buildings',roads:'Roads',water:'Water',green:'Green',trees:'Trees',rail:'Railways',airports:'Airports',power:'Power',landuse:'Land use',terrain:'Terrain'};
  var BIM_CTX_COL={buildings:'#c9ccd1',roads:'#8a8f98',water:'#4f8fd6',green:'#6dbb73',trees:'#3f9a52',rail:'#8d7b68',airports:'#5d6168',power:'#b9bec6',landuse:'#d9cfb4',terrain:'#b08559'};
  var BIM_OVERPASS_URL='https://overpass-api.de/api/interpreter';
  var BIM_TERRARIUM_URL='https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
  var BIM_CTX_OSM_CREDIT='\u00a9 OpenStreetMap contributors (ODbL)';
  var BIM_CTX_TERRAIN_CREDIT='Terrain Tiles: Mapzen, AWS';
  var BIM_CTX_MAX_FEATURES=5000,BIM_CTX_GRID=25,BIM_CTX_TZ=15;   /* __acad3dV167: a storey's and a building's height are the registry's (app.context) */
  var A3D_CTX={busy:false};
  function bimCtxSettings(){
    var c=(A3D.site&&A3D.site.context)||{},k={},i;
    for(i=0;i<BIM_CTX_KINDS.length;i++)k[BIM_CTX_KINDS[i]]=!(c.kinds&&c.kinds[BIM_CTX_KINDS[i]]===false);
    return {radius:(typeof c.radius==='number'&&c.radius>=50&&c.radius<=1000)?c.radius:150,kinds:k,
      overpass:(typeof c.overpass==='string'&&c.overpass)?c.overpass:BIM_OVERPASS_URL,
      onGround:c.onGround!==false};   /* __acad3dV137: buildings on the terrain */
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
    }else if(field==='onGround'){   /* __acad3dV137 */
      nv=!!val&&val!=='false'&&val!=='0';
      if(nv===st.onGround)return true;
    }else return false;
    pushUndo();
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    A3D.site.context=A3D.site.context||{};
    if(kk){A3D.site.context.kinds=A3D.site.context.kinds||{};A3D.site.context.kinds[kk]=nv;}
    else A3D.site.context[field]=nv;
    if(field==='onGround'){   /* __acad3dV137: in the same undo step */
      var nst=bimCtxStand(nv);paint();
      a3dToast(nv?(nst?'Context buildings stand on the terrain: '+nst:'No context terrain to stand the buildings on: get it with CONTEXT'):'Context buildings back on the level');
    }
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
    if(k.buildings)q.push('way["building"]'+b+';','relation["building"]["type"="multipolygon"]'+b+';',
      'way["building:part"]'+b+';','relation["building:part"]["type"="multipolygon"]'+b+';');   /* __acad3dV139: LOD1.3 */
    if(k.roads)q.push('way["highway"]'+b+';');
    if(k.water)q.push('way["natural"="water"]'+b+';','relation["natural"="water"]'+b+';','way["water"]'+b+';','way["waterway"]'+b+';');
    if(k.green)q.push('way["leisure"="park"]'+b+';','way["landuse"~"^(grass|forest|meadow|recreation_ground|village_green)$"]'+b+';',
      'way["natural"~"^(wood|scrub|grassland)$"]'+b+';');
    if(k.trees)q.push('node["natural"="tree"]'+b+';','way["natural"="tree_row"]'+b+';');
    if(k.rail)q.push('way["railway"~"^(rail|light_rail|narrow_gauge|subway|tram|monorail|platform)$"]'+b+';');   /* __acad3dV157 */
    if(k.airports)q.push('way["aeroway"~"^(runway|taxiway|apron|aerodrome|helipad)$"]'+b+';','relation["aeroway"="aerodrome"]'+b+';');
    if(k.power)q.push('way["power"="line"]'+b+';','node["power"="tower"]'+b+';');
    if(k.landuse)q.push('way["landuse"~"^('+BIM_CTX_LANDUSE+')$"]'+b+';','relation["landuse"~"^('+BIM_CTX_LANDUSE+')$"]["type"="multipolygon"]'+b+';',
      'way["amenity"~"^('+BIM_CTX_LAND_AREAS.amenity+')$"]'+b+';','way["leisure"~"^('+BIM_CTX_LAND_AREAS.leisure+')$"]'+b+';','way["tourism"~"^('+BIM_CTX_LAND_AREAS.tourism+')$"]'+b+';');   /* __acad3dV168 */
    return q.length?'[out:json][timeout:25];('+q.join('')+');out geom;':'';
  }
  function bimOsmKind(el){
    var t=el.tags||{};
    if(el.type==='node')return t.natural==='tree'?'trees':(t.power==='tower'?'power':'');   /* __acad3dV157 */
    if(t.railway&&/^(rail|light_rail|narrow_gauge|subway|tram|monorail|platform)$/.test(t.railway))return 'rail';
    if(t.aeroway&&/^(runway|taxiway|apron|aerodrome|helipad)$/.test(t.aeroway))return 'airports';
    if(t.power==='line')return 'power';
    if(t.natural==='tree_row')return 'trees';
    if(t.building&&t.building!=='no')return 'buildings';
    if(t['building:part']&&t['building:part']!=='no')return 'buildings';   /* __acad3dV139: a part */
    if(t.highway)return 'roads';
    if(t.natural==='water'||t.water||t.waterway)return 'water';
    if(t.leisure==='park'||/^(grass|forest|meadow|recreation_ground|village_green)$/.test(t.landuse||'')||/^(wood|scrub|grassland)$/.test(t.natural||''))return 'green';
    if(t.landuse&&new RegExp('^('+BIM_CTX_LANDUSE+')$').test(t.landuse))return 'landuse';   /* __acad3dV157 */
    if(['amenity','leisure','tourism'].some(function(k2){return t[k2]&&new RegExp('^('+BIM_CTX_LAND_AREAS[k2]+')$').test(t[k2]);}))return 'landuse';   /* __acad3dV168: an amenity's, a pitch's, a hotel's grounds */
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
    if(isFinite(L)&&L>0&&L<300)return {h:L*bimCtxLevelH(),from:'levels'};
    return {h:bimCtxDefaultH(),from:'assumed'};
  }
  /* Overpass's answer as features in model terms: areas (outer and inner rings), a line, a point */
  function bimCtxFeatures(js,org){
    var out=[],els=(js&&js.elements)||[],i;
    function M(p){var m=bimGeoToModel(p[0],p[1],org);return [m[0],m[1]];}
    for(i=0;i<els.length&&out.length<BIM_CTX_MAX_FEATURES;i++){
      var el=els[i]||{},kind=bimOsmKind(el),f,g,cl;
      if(!kind)continue;
      f={kind:kind,osm:el.type,id:el.id,tags:el.tags||{},outer:[],inner:[],line:null,point:null};
      if(kind==='buildings'&&!(f.tags.building&&f.tags.building!=='no'))f.part=true;   /* __acad3dV139 */
      if(el.type==='node'){if(isFinite(el.lat)&&isFinite(el.lon))f.point=M([el.lon,el.lat]);}
      else if(el.type==='way'&&el.geometry&&el.geometry.length>1){
        g=el.geometry.map(function(p){return [p.lon,p.lat];});
        cl=g.length>=4&&g[0][0]===g[g.length-1][0]&&g[0][1]===g[g.length-1][1];
        if(cl&&(kind==='buildings'||kind==='green'||kind==='landuse'||(kind==='water'&&!f.tags.waterway)||
          (kind==='airports'&&/^(apron|aerodrome|helipad)$/.test(f.tags.aeroway||''))||(kind==='rail'&&f.tags.railway==='platform')))f.outer.push(g.slice(0,-1).map(M));   /* __acad3dV157 */
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
