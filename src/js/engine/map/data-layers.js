  /* ================= __acad3dV134: data layers =================
     The public record of a site -- parcels, zoning, flood zones -- from the GIS servers councils and
     agencies publish: an ArcGIS REST layer, a WFS, or a GeoJSON file. Read for the site's area, kept
     with the project so it opens offline, drawn on the plan, read by a click. */
  var BIM_DATA_PRESETS=[
    {name:'Flood zones (FEMA NFHL, US)',url:'https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28',color:'#3d7fd6',credit:'FEMA National Flood Hazard Layer'},
    {name:'Parcels (Philadelphia Water Dept.)',url:'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/PWD_PARCELS/FeatureServer/0',color:'#e0a040',credit:'City of Philadelphia (OpenDataPhilly)'},
    {name:'Zoning base districts (Philadelphia)',url:'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/Zoning_BaseDistricts/FeatureServer/0',color:'#b067d6',credit:'City of Philadelphia (OpenDataPhilly)'}
  ];
  var BIM_DATA_MAX=2000;
  var A3D_DATA={busy:{},pending:{},sel:null,cache:{}};
  function bimDataList(){return (A3D.site&&Array.isArray(A3D.site.dataLayers))?A3D.site.dataLayers:[];}
  function bimDataById(id){var L=bimDataList(),i;for(i=0;i<L.length;i++)if(L[i].id===id)return L[i];return null;}
  function bimDataFeats(id){return (A3D.dataFeatures&&A3D.dataFeatures[id])||[];}
  /* what an address is: an ArcGIS layer, a WFS, or a GeoJSON file -- or why it is none */
  function bimDataKind(url){
    var u=String(url==null?'':url).replace(/^\s+|\s+$/g,'');
    if(!/^https?:\/\/[^\s\/]+\/\S*$/i.test(u))return {error:'A data layer is a web address, starting https://'};
    if(/\/(FeatureServer|MapServer)\/\d+\/?(\?.*)?$/i.test(u))return {kind:'arcgis'};
    if(/^https?:\/\/[^\/]+\/resource\/[a-z0-9]{4}-[a-z0-9]{4}\.geojson(\?.*)?$/i.test(u))return {kind:'socrata'};   /* __acad3dV135 */
    if(/\/(FeatureServer|MapServer)\/?(\?.*)?$/i.test(u))return {error:'That is a whole ArcGIS service: add the layer\'s number, like .../FeatureServer/0'};
    if(/[?&]service=wfs(&|$)/i.test(u)||/\/wfs\/?(\?|$)/i.test(u)){
      if(!/[?&]typenames?=[^&]+/i.test(u))return {error:'A WFS address needs its layer: add typeNames=... to it'};
      return {kind:'wfs'};
    }
    return {kind:'geojson'};
  }
  function bimDataNameFromUrl(u){
    var m=/\/services\/(?:[^\/]+\/)*?([^\/]+)\/(?:FeatureServer|MapServer)\/(\d+)/i.exec(u);
    if(m)return m[1].replace(/_/g,' ')+(m[2]!=='0'?' '+m[2]:'');
    m=/[?&]typenames?=([^&]+)/i.exec(u);
    if(m)return decodeURIComponent(m[1]).replace(/^[^:]*:/,'');
    m=/\/resource\/([a-z0-9]{4}-[a-z0-9]{4})\.geojson/i.exec(u);   /* __acad3dV135 */
    if(m)return 'Dataset '+m[1];
    m=/\/([^\/?#]+?)(\.geo)?(\.json)?(\?|#|$)/i.exec(u);
    return m?decodeURIComponent(m[1]):'Data';
  }
  /* the request for the area: ArcGIS's query, WFS's GetFeature in CRS:84 (longitude first), or the file */
  function bimDataQueryUrl(L,a){
    var b=[a.w,a.s,a.e,a.n].map(function(v){return v.toFixed(7);}).join(',');
    if(L.kind==='arcgis')return L.url.replace(/\/?(\?.*)?$/,'')+'/query?where=1%3D1&geometry='+encodeURIComponent(b)+
      '&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=true&outSR=4326&resultRecordCount='+BIM_DATA_MAX+'&f=geojson';
    if(L.kind==='wfs'){
      var m=/[?&]typenames?=([^&]+)/i.exec(L.url),base=L.url.split('?')[0];
      return base+'?service=WFS&version=2.0.0&request=GetFeature&typeNames='+m[1]+'&outputFormat=application%2Fjson&srsName=CRS%3A84&bbox='+
        encodeURIComponent(b+',CRS:84')+'&count='+BIM_DATA_MAX;
    }
    if(L.kind==='socrata'){   /* __acad3dV135: SoQL within_box(column, north, west, south, east) */
      var sb=L.url.split('?')[0];
      return sb+'?'+(L.geom?'$where='+encodeURIComponent('within_box('+L.geom+','+a.n.toFixed(7)+','+a.w.toFixed(7)+','+a.s.toFixed(7)+','+a.e.toFixed(7)+')')+'&':'')+
        '$limit='+BIM_DATA_MAX;
    }
    return L.url;
  }
  /* an answer as stored features: longitude and latitude only, touching the area, at most BIM_DATA_MAX */
  function bimDataParse(js,a){
    if(js&&js.error&&!js.type)return {error:'said: '+String(js.error.message||js.error.code||'an error').slice(0,160)};
    var r=bimGeoJsonFeatures(js),out=[],i,j,k,ps,pt,bb,okf,bad=0;
    if(r.error)return r;
    for(i=0;i<r.features.length&&out.length<BIM_DATA_MAX;i++){
      ps=bimGeoParts(r.features[i].geom);bb=[Infinity,Infinity,-Infinity,-Infinity];okf=ps.length>0;
      for(j=0;okf&&j<ps.length;j++){
        if(ps[j].kind==='unknown'){okf=false;break;}
        pt=bimGeoPositions(ps[j].pts);
        if(!pt){okf=false;break;}
        for(k=0;k<pt.length;k++){
          if(Math.abs(pt[k][0])>180||Math.abs(pt[k][1])>90)return {error:'answered in a projected grid ('+pt[k][0]+', '+pt[k][1]+'), not longitude and latitude'};
          bb[0]=Math.min(bb[0],pt[k][0]);bb[1]=Math.min(bb[1],pt[k][1]);bb[2]=Math.max(bb[2],pt[k][0]);bb[3]=Math.max(bb[3],pt[k][1]);
        }
      }
      if(!okf){bad++;continue;}
      if(bb[2]<a.w||bb[0]>a.e||bb[3]<a.s||bb[1]>a.n)continue;   /* not in the area */
      out.push({g:r.features[i].geom,p:bimGeoCleanProps(r.features[i].props||{})});
    }
    return {features:out,skipped:bad,more:!!(js&&(js.exceededTransferLimit||(js.properties&&js.properties.exceededTransferLimit)))||i<r.features.length};
  }
  /* one request; what comes replaces the layer's features */
  function bimDataFetch(id){
    var L=bimDataById(id),a=bimCtxArea(),url,host,p;
    if(!L)return null;
    if(!a){a3dToast('Set the site latitude and longitude first, or find an address: data is read around the site');return null;}
    if(A3D_DATA.busy[id]){a3dToast(L.name+' is already on its way');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot fetch data');return null;}
    url=bimDataQueryUrl(L,a);host=bimMapHost(url);
    A3D_DATA.busy[id]=true;
    a3dToast('Getting '+L.name+' from '+host+' ...');
    function done(st){var L2=bimDataById(id);if(L2){L2.status=st;}A3D_DATA.busy[id]=false;}
    p=fetch(url).then(function(r){
      if(!r.ok)throw {http:r.status};
      return r.text();
    }).then(function(tx){
      var js,res,L2,date=new Date().toISOString().slice(0,10);
      try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
      res=bimDataParse(js,a);
      if(res.error){
        done({date:date,error:host+' '+res.error});
        refreshProps();saveSoon();
        a3dToast(L.name+': '+host+' '+res.error);
        return {error:host+' '+res.error};
      }
      L2=bimDataById(id);
      if(!L2){A3D_DATA.busy[id]=false;return {error:'removed'};}
      A3D.dataFeatures=A3D.dataFeatures||{};
      A3D.dataFeatures[id]=res.features;
      delete A3D_DATA.cache[id];
      if(A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
      done({date:date,count:res.features.length,more:res.more});
      refreshProps();paint();saveSoon();
      a3dToast(L2.name+': '+res.features.length+' feature'+(res.features.length===1?'':'s')+' around the site'+
        (res.more?' (the first '+res.features.length+'; there are more)':'')+(res.skipped?'; '+res.skipped+' could not be read':''));
      return {count:res.features.length,more:res.more,skipped:res.skipped};
    }).then(null,function(e){
      var m=bimCtxErr(host,e);
      done({date:new Date().toISOString().slice(0,10),error:m});
      refreshProps();saveSoon();
      a3dToast(L.name+': '+m);
      return {error:m};
    });
    A3D_DATA.pending[id]=p;
    return p;
  }
