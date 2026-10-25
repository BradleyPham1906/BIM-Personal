  /* ================= __acad3dV132: the map in Properties, the address, site data ================= */
  function bimGeoFmt(v,pos,neg){return Math.abs(v).toFixed(6)+'\u00b0 '+(v>=0?pos:neg);}
  function bimMapPropsHtml(){
    var st=bimMapSettings(),org=bimMapOrigin(),r='',k,nm;
    var opts='<option value="off"'+(st.style==='off'?' selected':'')+'>Off</option>';
    for(k=1;k<BIM_MAP_ORDER.length;k++){
      nm=BIM_MAP_ORDER[k];
      opts+='<option value="'+nm+'"'+(st.style===nm?' selected':'')+'>'+bimEsc(BIM_MAP_STYLES[nm].name)+'</option>';
    }
    r+=bimPropRow('Basemap','<select data-propmap="style">'+opts+'</select>');
    r+=bimPropRow('Opacity (%)','<input type="number" min="10" max="100" step="5" data-propmap="opacity" value="'+Math.round(st.opacity*100)+'">');
    if(st.style==='custom'){
      r+=bimPropRow('Tile URL','<input type="text" data-propmap="url" value="'+bimEsc(st.url)+'" placeholder="https://tiles.example.org/{z}/{x}/{y}.png" spellcheck="false">');
      r+=bimPropRow('Credit','<input type="text" data-propmap="credit" value="'+bimEsc(st.credit)+'" placeholder="Who the tiles are from">');
    }else if(st.style!=='off')r+=bimPropText('Credit',bimMapCredit(st));
    r+=bimPropRow('Address','<div class="a3d-ukv"><input type="text" data-propmap="addr" enterkeyhint="search" value="'+bimEsc(A3D_MAP_DRAFT!==null?A3D_MAP_DRAFT:((A3D.site&&A3D.site.address)||''))+
      '" placeholder="Street, town" aria-label="Address to find"><button type="button" class="a3d-pedit" data-propmapact="find">Find</button></div>');
    r+=bimPropText('Model 0,0',org?(bimGeoFmt(org.lat,'N','S')+', '+bimGeoFmt(org.lon,'E','W')):'not placed: set the latitude and longitude, or find an address');
    r+=bimPropRow('Site Data','<button type="button" class="a3d-pedit" data-propmapact="import">Import GeoJSON or KML</button> '+
      '<button type="button" class="a3d-pedit" data-propmapact="export">Export GeoJSON</button>');
    return r;
  }
  /* what the map is now, said once a style changes */
  function bimMapSaid(){
    var st=bimMapSettings(),nm;
    if(st.style==='off'){a3dToast('Map off');return;}
    nm=BIM_MAP_STYLES[st.style].name;
    if(!bimMapOrigin()){a3dToast(nm+': set the site latitude and longitude in Properties, or find an address (FINDADDRESS)');return;}
    if(!bimMapTemplate(st)){a3dToast(nm+': give the tile URL in Properties');return;}
    a3dToast('Map: '+nm+(bimMapCredit(st)?' - '+bimMapCredit(st):''));
  }
  function bimMapPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propmap]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propmap');
    if(k==='addr')return true;   /* looked up by Find, never as it is typed */
    if(bimMapSet(k,f.value)&&k==='style')bimMapSaid();
    return true;
  }
  function bimMapPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-propmapact]'):null;
    if(!b)return false;
    var a=b.getAttribute('data-propmapact');
    if(a==='find'){var q=el.propsbody.querySelector('[data-propmap="addr"]'),qv=q?q.value:'';
      if(!/\S/.test(qv)&&A3D_MAP_DRAFT)qv=A3D_MAP_DRAFT;   /* __acad3dV149c: the field drawn again empty under the tap */
      bimMapFind(qv);return true;}
    if(a==='import'){bimGeoImportPick();return true;}
    if(a==='export'){bimGeoExport();return true;}
    return false;
  }
  /* MAP: the next basemap -- off, street, satellite, and the custom tiles once they have a URL */
  function bimMapCommand(){
    var st=bimMapSettings(),i=BIM_MAP_ORDER.indexOf(st.style),nx;
    do{i=(i+1)%BIM_MAP_ORDER.length;nx=BIM_MAP_ORDER[i];}while(nx==='custom'&&!st.url);
    bimMapSet('style',nx);
    bimMapSaid();
    return nx;
  }
  /* ---- the address: Nominatim, one request per Find. Its policy is a request a second at most and
     no search as you type, so a second Find inside the second is refused, with the reason. ---- */
  var BIM_GEOCODE_URL='https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&addressdetails=1&q=';   /* __acad3dV167: addressdetails, for the place */
  /* __acad3dV149c: the address as it is typed. Properties is drawn again when the screen changes
     size -- on a phone, when the keyboard goes as Find is tapped -- and a field that kept nothing of
     its own came back empty. */
  var A3D_MAP_DRAFT=null;
  function bimMapFind(q){
    q=String(q==null?'':q).replace(/\s+/g,' ').replace(/^ | $/g,'');
    if(!q){a3dToast('Type an address or a place to find');return null;}
    var now=Date.now();
    if(A3D_MAP.lastFind&&now-A3D_MAP.lastFind<1000){a3dToast('One search a second: Nominatim asks for no more');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot search: set the latitude and longitude in Properties');return null;}
    A3D_MAP.lastFind=now;
    a3dToast('Finding '+q+' ...');
    return fetch(BIM_GEOCODE_URL+encodeURIComponent(q)).then(function(res){
      if(!res.ok)throw {http:res.status};   /* __acad3dV133d */
      return res.json();
    }).then(function(js){
      var hit=(js&&js.length)?js[0]:null,lat=hit?parseFloat(hit.lat):NaN,lon=hit?parseFloat(hit.lon):NaN;
      if(!isFinite(lat)||!isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180){a3dToast('Nothing found for '+q);return {found:false,q:q};}
      var nm=String(hit.display_name||q).slice(0,300);
      try{bimMapPlace(lat,lon,nm,hit.address);}   /* __acad3dV167 */
      catch(eP){console.warn('[BIM] placing the site',eP);a3dToast('The site could not be placed - see the console');return {found:false,q:q,error:String(eP)};}
      return {found:true,q:q,lat:lat,lon:lon,name:nm};
    },function(err){
      var hs=err&&err.http;
      a3dToast('Address search failed: nominatim.openstreetmap.org '+(hs===403?'refused it (HTTP 403): it asks for the app to be opened from a website, not a file -- set the latitude and longitude in Properties instead':
        (hs===429?'is busy (HTTP 429): try again in a minute':(hs?'answered HTTP '+hs:'could not be reached (offline, or it does not allow browser access)'))));
      return {found:false,q:q,error:hs?'HTTP '+hs:String(err&&err.message?err.message:err)};
    });
  }
  /* the site goes where the address is: model 0,0 there, the view on it, the street map on if the
     map was off. One undo step. */
  function bimMapPlace(lat,lon,name,addr){
    pushUndo();
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    A3D.site.sun=A3D.site.sun||{};
    A3D.site.sun.lat=Math.round(lat*1e7)/1e7;
    A3D.site.sun.lon=Math.round(lon*1e7)/1e7;
    if(name)A3D.site.address=name;
    /* __acad3dV167: the place found is the site's place, for the standards in force there (one undo step with the move) */
    if(addr&&typeof addr==='object'&&addr.country_code){try{bimStdPlaceFromAddress(addr);}catch(eSt){console.warn('[BIM] The site\'s place could not be kept',eSt);}}
    A3D.site.map=A3D.site.map||{};
    if(!BIM_MAP_STYLES[A3D.site.map.style])A3D.site.map.style='street';
    bimMapForgetFailures();
    A3D.cam.tx=0;A3D.cam.tz=0;
    refreshProps();paint();saveSoon();
    a3dToast('Found '+(name||(lat.toFixed(5)+', '+lon.toFixed(5)))+'. Model 0,0 is there now. Search: Nominatim, \u00a9 OpenStreetMap contributors');
  }
  function openFindAddressDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg a3d-dlgwide';
    d.innerHTML='<div class="a3d-dlghd">Find Address</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><input type="text" data-a3dp="q" value="'+bimEsc((A3D.site&&A3D.site.address)||'')+'" placeholder="Street, town" aria-label="Address or place"></div>'+
      '<div class="a3d-propnote">The place found becomes the site: model 0,0. Search: Nominatim, \u00a9 OpenStreetMap contributors.</div>'+
      '<div id="a3d-dlgerr"></div></div><div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Find</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var qI=d.querySelector('[data-a3dp="q"]');
    function submit(){
      var v=qI.value;
      if(!String(v).replace(/\s+/g,'')){d.querySelector('#a3d-dlgerr').textContent='Type an address or a place';return;}
      closeDlg();bimMapFind(v);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
      else ev.stopPropagation();
    });
    qI.focus();qI.select();
  }
  /* ---- site data in: GeoJSON (RFC 7946) or KML, as a flat list of {props, geom} ---- */
  function bimGeoFeatures(text,name){
    var s=String(text||'').replace(/^\ufeff/,''),js;
    if(s.replace(/^\s+/,'').charAt(0)==='<')return bimKmlFeatures(s);
    try{js=JSON.parse(s);}catch(eJ){return {error:name+' is not GeoJSON or KML: '+(eJ&&eJ.message?eJ.message:'it does not read')};}
    return bimGeoJsonFeatures(js);
  }
  function bimGeoJsonFeatures(js){
    var out=[];
    if(!js||typeof js!=='object'||!js.type)return {error:'That is not GeoJSON: it has no "type"'};
    var crs=js.crs&&js.crs.properties&&js.crs.properties.name;
    if(crs&&!/(CRS84|4326)$/i.test(String(crs)))
      return {error:'The file is in '+crs+': only longitude and latitude (WGS84, EPSG:4326) can be placed. Export it as WGS84 and import it again.'};
    function add(g,props){
      if(!g||!g.type)return;
      if(g.type==='GeometryCollection'){(g.geometries||[]).forEach(function(x){add(x,props);});return;}
      out.push({props:(props&&typeof props==='object')?props:{},geom:g});
    }
    if(js.type==='FeatureCollection')(js.features||[]).forEach(function(f){if(f&&f.type==='Feature')add(f.geometry,f.properties);});
    else if(js.type==='Feature')add(js.geometry,js.properties);
    else add(js,{});
    return {features:out};
  }
  function bimKmlFeatures(s){
    var doc=null,out=[],i;
    try{doc=new DOMParser().parseFromString(s,'application/xml');}catch(eX){doc=null;}
    if(!doc||doc.getElementsByTagName('parsererror').length)return {error:'The KML does not read: it is not well-formed XML'};
    function all(n,tag){var r=[],j,c=n.getElementsByTagName(tag);for(j=0;j<c.length;j++)r.push(c[j]);return r;}
    function txt(n,tag){var c=n.getElementsByTagName(tag)[0];return c?String(c.textContent||'').replace(/^\s+|\s+$/g,''):'';}
    function coords(n){
      var c=n.getElementsByTagName('coordinates')[0],r=[];
      String(c?c.textContent:'').replace(/^\s+|\s+$/g,'').split(/\s+/).forEach(function(tu){
        if(!tu)return;
        var a=tu.split(',');
        r.push([parseFloat(a[0]),parseFloat(a[1])]);
      });
      return r;
    }
    var pms=all(doc,'Placemark');
    for(i=0;i<pms.length;i++){
      var pm=pms[i],props={},nm=txt(pm,'name'),ds=txt(pm,'description');
      if(nm)props.name=nm;
      if(ds)props.description=ds;
      all(pm,'Data').forEach(function(d){props[d.getAttribute('name')||'value']=txt(d,'value');});
      all(pm,'SimpleData').forEach(function(d){props[d.getAttribute('name')||'value']=String(d.textContent||'');});
      all(pm,'Point').forEach(function(p){out.push({props:props,geom:{type:'Point',coordinates:coords(p)[0]}});});
      all(pm,'LineString').forEach(function(p){out.push({props:props,geom:{type:'LineString',coordinates:coords(p)}});});
      all(pm,'Polygon').forEach(function(p){
        var rings=[];
        all(p,'outerBoundaryIs').forEach(function(b){rings.unshift(coords(b));});
        all(p,'innerBoundaryIs').forEach(function(b){all(b,'LinearRing').forEach(function(r){rings.push(coords(r));});});
        if(rings.length)out.push({props:props,geom:{type:'Polygon',coordinates:rings}});
      });
    }
    return {features:out};
  }
  /* a geometry as its parts: each ring of a polygon (holes too), each line, each point */
  function bimGeoParts(g){
    var P=[],c=g.coordinates;
    function ring(r,i){P.push({kind:'ring',pts:r,hole:i>0});}
    if(g.type==='Point')P.push({kind:'point',pts:[c]});
    else if(g.type==='MultiPoint')(c||[]).forEach(function(p){P.push({kind:'point',pts:[p]});});
    else if(g.type==='LineString')P.push({kind:'line',pts:c});
    else if(g.type==='MultiLineString')(c||[]).forEach(function(l){P.push({kind:'line',pts:l});});
    else if(g.type==='Polygon')(c||[]).forEach(ring);
    else if(g.type==='MultiPolygon')(c||[]).forEach(function(pg){(pg||[]).forEach(ring);});
    else P.push({kind:'unknown',type:String(g.type)});
    return P;
  }
  /* a part's positions as [lon, lat]: null when one is not two numbers */
  function bimGeoPositions(pts){
    var out=[],i,p;
    if(!pts||!pts.length)return null;
    for(i=0;i<pts.length;i++){
      p=pts[i];
      if(!p||typeof p[0]!=='number'||typeof p[1]!=='number'||!isFinite(p[0])||!isFinite(p[1]))return null;
      out.push([p[0],p[1]]);
    }
    return out;
  }
  function bimGeoCleanProps(p){
    var o={},k,n=0,v;
    for(k in p)if(p.hasOwnProperty(k)&&n<40){
      v=p[k];n++;
      if(v===null||typeof v==='number'||typeof v==='boolean')o[String(k).slice(0,60)]=v;
      else if(typeof v==='string')o[String(k).slice(0,60)]=v.slice(0,500);
      else{try{o[String(k).slice(0,60)]=JSON.stringify(v).slice(0,500);}catch(eS){}}
    }
    return o;
  }
  function bimGeoImportPick(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.geojson,.json,.kml';
    inp.onchange=function(){var f=inp.files&&inp.files[0];if(f)bimGeoImportFile(f);};
    inp.click();
    return true;
  }
  function bimGeoImportFile(file){
    var name=(file&&file.name)||'site data',ext=(name.split('.').pop()||'').toLowerCase();
    if(ext==='kmz'){a3dToast('A KMZ is a zipped KML: unzip it and import the .kml inside');return;}
    var rd=new FileReader();
    rd.onerror=function(){a3dToast('Failed to read '+name);};
    rd.onload=function(ev){
      try{bimGeoImportText(String(ev.target.result||''),name);}
      catch(eG){console.warn('[BIM] site data import',eG);a3dToast('Site data import failed: '+(eG&&eG.message?eG.message:eG));}
    };
    rd.readAsText(file);
  }
  /* The features become sketches and points on the "Site data" layer at the lowest level, each with
     its properties. Positions must be longitude and latitude: a projected grid is refused, never
     placed. With no site place yet, the data's centre becomes it. One undo step. */
  function bimGeoImportText(text,name){
    name=String(name||'site data');
    var res=bimGeoFeatures(text,name);
    if(res.error){a3dToast(res.error);return {error:res.error};}
    var parts=[],bad=0,odd={},i,j,k,ps,pt,lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity;
    for(i=0;i<res.features.length;i++){
      ps=bimGeoParts(res.features[i].geom);
      for(j=0;j<ps.length;j++){
        if(ps[j].kind==='unknown'){odd[ps[j].type]=1;continue;}
        pt=bimGeoPositions(ps[j].pts);
        if(!pt){bad++;continue;}
        for(k=0;k<pt.length;k++){
          if(Math.abs(pt[k][0])>180||Math.abs(pt[k][1])>90){
            var em='The positions are not longitude and latitude ('+pt[k][0]+', '+pt[k][1]+' is a projected grid). Export the file as WGS84 (EPSG:4326) and import it again.';
            a3dToast(em);return {error:em};
          }
          lo0=Math.min(lo0,pt[k][0]);lo1=Math.max(lo1,pt[k][0]);la0=Math.min(la0,pt[k][1]);la1=Math.max(la1,pt[k][1]);
        }
        if(ps[j].kind==='ring'){
          var a0=pt[0],aN=pt[pt.length-1];
          if(pt.length>1&&a0[0]===aN[0]&&a0[1]===aN[1])pt.pop();
          if(pt.length<3){bad++;continue;}
        }else if(ps[j].kind==='line'&&pt.length<2){bad++;continue;}
        parts.push({kind:ps[j].kind,hole:!!ps[j].hole,pts:pt,props:res.features[i].props});
      }
    }
    if(!parts.length){
      var none='Nothing in '+name+' to place'+(bad?' ('+bad+' part'+(bad===1?'':'s')+' could not be read)':'')+(Object.keys(odd).length?' (not read: '+Object.keys(odd).join(', ')+')':'');
      a3dToast(none);return {error:none};
    }
    var placed=false,org=bimMapOrigin(),ids=[],nShapes=0,nPts=0;
    pushUndo();
    undoSuspend=true;
    try{
      if(!org){
        if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
        A3D.site.sun=A3D.site.sun||{};
        A3D.site.sun.lat=Math.round((la0+la1)/2*1e7)/1e7;
        A3D.site.sun.lon=Math.round((lo0+lo1)/2*1e7)/1e7;
        org=bimMapOrigin();placed=true;
      }
      var was=A3D.activeLayer,ly=addLayer('Site data','#d9a441'),y=bimShadowGround();
      if(bimLayerById(was))A3D.activeLayer=was;
      for(i=0;i<parts.length;i++){
        var pp=parts[i],m=pp.pts.map(function(q){return bimGeoToModel(q[0],q[1],org);}),o,pr=bimGeoCleanProps(pp.props);
        if(pp.kind==='point'){o=bimAddPoint(m[0][0],m[0][1],y,ly.id);nPts++;}
        else{o=bimMakeImportedSketch(m,y,pp.kind==='ring');nShapes++;}
        if(!o)continue;
        o.layer=ly.id;o.col=ly.color||'#d9a441';
        if(typeof pr.name==='string'&&pr.name.replace(/\s+/g,''))o.name=pr.name.slice(0,60);
        o.geo={source:name.slice(0,120),props:pr};
        if(pp.hole)o.geo.part='hole';
        ids.push(o.id);
      }
    }finally{undoSuspend=false;}
    refreshTree();refreshLayers();refreshProps();fitScene();paint();saveSoon();
    a3dToast('Site data: '+nShapes+' shape'+(nShapes===1?'':'s')+' and '+nPts+' point'+(nPts===1?'':'s')+' from '+name+' on the Site data layer'+
      (placed?'; the site latitude and longitude were set to the data\'s centre':'')+
      (bad?'; '+bad+' part'+(bad===1?'':'s')+' could not be read':'')+
      (Object.keys(odd).length?'; not read: '+Object.keys(odd).join(', '):''));
    return {ids:ids,shapes:nShapes,points:nPts,placedSite:placed,skipped:bad};
  }
  function bimGeoPropsHtml(o){
    var g=o.geo||{},r='',k,n=0;
    r+=bimPropText('Source',g.source||'');
    if(g.part==='hole')r+=bimPropText('Ring','a hole in the shape before it');
    for(k in g.props)if(g.props&&g.props.hasOwnProperty(k)&&n<40){n++;r+=bimPropText(k,g.props[k]===null?'':String(g.props[k]));}
    if(!n)r+=bimPropText('Properties','none in the file');
    return bimPropGroup('Site Data',r);
  }
  /* ---- the plan out, as GeoJSON in longitude and latitude ---- */
  function bimGeoRound(v){return Math.round(v*1e8)/1e8;}
  /* a mass's footprint: its cross-section at the middle of its first floor, holes inside their outer */
  function bimMassFootprint(o){
    var bb=objBBox(o);
    if(!bb)return [];
    var u=o.usage?bimUsageById(o.usage):null,ftf=(u&&u.ftf>0)?u.ftf:3,h=bb.mx[1]-bb.mn[1];
    var L=bimMeshSliceLoops(o,bb.mn[1]+Math.min(ftf,h)/2).filter(function(l){return l.length>=3&&bimPolyArea(l)>1e-9;});
    var depth=L.map(function(l,i){var d=0,j;for(j=0;j<L.length;j++)if(j!==i&&bimPointInPoly(l[0],L[j]))d++;return d;});
    var polys=[],i,j,best;
    for(i=0;i<L.length;i++)if(depth[i]%2===0)polys.push({outer:i,rings:[L[i]]});
    for(i=0;i<L.length;i++)if(depth[i]%2===1){
      best=null;
      for(j=0;j<polys.length;j++)if(depth[polys[j].outer]===depth[i]-1&&bimPointInPoly(L[i][0],L[polys[j].outer]))best=polys[j];
      if(best)best.rings.push(L[i]);
    }
    return polys.map(function(p){return p.rings;});
  }
  function bimGeoExportFC(){
    var org=bimMapOrigin();
    if(!org)return {error:'Set the site latitude and longitude first, or find an address: they put model 0,0 on the earth'};
    var F=[],i,o,b,q,kind,geom,lv,ap;
    function P(x,z){var g=bimModelToGeo(x,z,org);return [bimGeoRound(g[0]),bimGeoRound(g[1])];}
    function ring(pts,off){var r=pts.map(function(p){return P(p[0]+off[0],p[1]+off[2]);});if(r.length)r.push(r[0].slice());return r;}
    function line(pts,off){return pts.map(function(p){return P(p[0]+off[0],p[1]+off[2]);});}
    var Z=[0,0,0];
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];b=o.bim;q=bimExportOffset(o);kind='';geom=null;ap=null;
      if(b&&b.type==='wall'&&b.centerline&&b.centerline.length>=2){
        kind='wall';geom={type:'LineString',coordinates:b.closed?ring(b.centerline,q):line(b.centerline,q)};
      }else if(o.t==='room'&&o.pts&&o.pts.length>=3){
        kind='room';geom={type:'Polygon',coordinates:[ring(o.pts,q)]};
      }else if(bimIsProperty(o)){
        ap=bimPropertyGeometry(o).ring;kind='property';geom={type:'Polygon',coordinates:[ring(ap,Z)]};
      }else if(bimIsAlignment(o)){
        kind='alignment';geom={type:'LineString',coordinates:line(bimAlignExport(o).pts,Z)};
      }else if(bimIsPoint(o)){
        kind=o.geo?'site data':'point';geom={type:'Point',coordinates:P(o.pts[0][0]+q[0],o.pts[0][1]+q[2])};
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2&&!bimIsHatch(o)&&!bimIsCline(o)){
        var fl=bimFlattenSketch(o)||o.pts,cl=o.closed!==false&&fl.length>=3;
        kind=o.geo?'site data':'sketch';geom=cl?{type:'Polygon',coordinates:[ring(fl,q)]}:{type:'LineString',coordinates:line(fl,q)};
        if(cl)ap=fl;
      }else if(b&&(b.type==='floor'||b.type==='ceiling'||b.type==='roof')&&(b.profile||b.footprint)){
        ap=b.profile||b.footprint;kind=b.type;geom={type:'Polygon',coordinates:[ring(ap,q)]};
      }else if(b&&b.type==='column'&&b.center){
        ap=bimRectFootprint(b.center,b.width,b.depth,b.rotation||0);kind='column';geom={type:'Polygon',coordinates:[ring(ap,q)]};
      }else if(bimIsFooting(o)&&b.plan&&b.plan.length){
        kind='footing';geom={type:'MultiPolygon',coordinates:b.plan.map(function(pl){return [ring(pl,q)];})};
      }else if(o.context&&o.context.footprint){   /* __acad3dV133 */
        ap=o.context.footprint;kind='context';geom={type:'Polygon',coordinates:[ring(ap,q)]};
      }else if(bimUsageTarget(o)==='mass'){
        var fp=bimMassFootprint(o);
        if(fp.length){kind='mass';geom={type:'MultiPolygon',coordinates:fp.map(function(rs){return rs.map(function(r){return ring(r,q);});})};}
      }
      if(!geom)continue;
      var pr={},k,ly=bimLayerOf(o),u=o.usage?bimUsageById(o.usage):null;
      if(o.geo&&o.geo.props)for(k in o.geo.props)if(o.geo.props.hasOwnProperty(k))pr[k]=o.geo.props[k];
      pr.name=o.name||'';pr.kind=kind;
      if(o.context){   /* __acad3dV133: the source's tags, and its credit with them */
        for(k in o.context.tags)if(o.context.tags.hasOwnProperty(k)&&!pr.hasOwnProperty(k))pr[k]=o.context.tags[k];
        pr.name=o.name||'';pr.kind='context '+o.context.kind;pr.source=o.context.source;pr.credit=o.context.credit;
        if(o.context.osm){pr.osm_type=o.context.osm;pr.osm_id=o.context.id;}
        if(o.context.height)pr.height=o.context.height;
      }
      if(ly)pr.layer=ly.name;
      lv=bimObjectLevelId(o);
      for(k=0;k<A3D.levels.length;k++)if(A3D.levels[k].id===lv)pr.level=A3D.levels[k].name;
      if(u)pr.usage=u.name;
      if(kind==='room'&&o.area>0)pr.area=Math.round(o.area*100)/100;
      else if(kind==='mass'){var mm=bimUsageMeasure(o);pr.area=Math.round(mm.footprint*100)/100;pr.height=Math.round(mm.height*100)/100;if(u)pr.gfa=Math.round(mm.GFA*100)/100;}
      else if(ap&&kind!=='site data')pr.area=Math.round(bimPolyArea(ap)*100)/100;
      if(o.geo&&o.geo.source)pr.source=o.geo.source;
      F.push({type:'Feature',id:o.id,properties:pr,geometry:geom});
    }
    return {type:'FeatureCollection',name:bimFileStem(),
      bim_site:{latitude:org.lat,longitude:org.lon,trueNorth:bimTrueNorthDeg(),note:'model 0,0 is at this latitude and longitude'},features:F};
  }
  function bimGeoExport(){
    var fc=bimGeoExportFC();
    if(fc.error){a3dToast(fc.error);return fc;}
    if(!fc.features.length){a3dToast('Nothing with a plan shape to export');return fc;}
    var fn=bimFileStem()+'.geojson';
    try{bimTriggerDownload(JSON.stringify(fc),fn,'application/geo+json');}
    catch(eX){console.warn('[BIM] GeoJSON export failed',eX);a3dToast('GeoJSON export failed - see the console');return {error:String(eX)};}
    a3dToast('Exported '+fn+' ('+fc.features.length+' feature'+(fc.features.length===1?'':'s')+', in longitude and latitude)');
    return fc;
  }
