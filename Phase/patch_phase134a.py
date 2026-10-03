"""patch_phase134a.py -- V134: data layers, the engine.

- A data layer is an ArcGIS REST layer (FeatureServer or MapServer with its number), a WFS (with
  its typeNames), or a GeoJSON file, read for V133's area around the site; three presets (FEMA's
  flood zones, Philadelphia's parcels and zoning).
- The layers live in A3D.site.dataLayers (undo, the project); their features, at most 2000 a layer,
  in A3D.dataFeatures -- saved with the project, the browser store and the tabs, kept out of undo.
- Each shown layer is drawn on the plan: areas filled faintly and outlined (holes respected),
  lines, points; not on paper. A click that hits nothing in the model reads the data under it:
  points, then lines, then the smallest area. An area becomes a property line.
- Failures are named; the credit line carries each shown layer's credit."""
NAME = 'patch_phase134a.py'
BASE = '8df5aba2a0f27fc27d56373d16861e3e19a2e5cbb35fbc527d2998aaadfe6950'
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


ENGINE = r"""  /* ================= __acad3dV134: data layers =================
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
  /* a layer added is one undo step, and fetched at once */
  function bimDataAdd(url,name,color,credit){
    var u=String(url==null?'':url).replace(/^\s+|\s+$/g,''),k=bimDataKind(u),L=bimDataList(),i,lyr;
    if(k.error){a3dToast(k.error);return null;}
    for(i=0;i<L.length;i++)if(L[i].url===u){a3dToast('That layer is here already: '+L[i].name);return null;}
    pushUndo();
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    if(!Array.isArray(A3D.site.dataLayers))A3D.site.dataLayers=[];
    lyr={id:'data-'+Date.now().toString(36)+'-'+(A3D.seq++),name:String(name||bimDataNameFromUrl(u)).slice(0,60),kind:k.kind,url:u,
      color:/^#[0-9a-fA-F]{6}$/.test(color||'')?color.toLowerCase():BIM_SCHEME_COLS[A3D.site.dataLayers.length%BIM_SCHEME_COLS.length],
      visible:true,credit:String(credit||bimMapHost(u)).slice(0,160)};
    A3D.site.dataLayers.push(lyr);
    refreshProps();saveSoon();
    if(bimCtxArea())bimDataFetch(lyr.id);
    else a3dToast(lyr.name+' added: set the site latitude and longitude, then Refresh it');
    return lyr.id;
  }
  function bimDataRemove(id){
    var L=bimDataList(),i;
    for(i=0;i<L.length;i++)if(L[i].id===id)break;
    if(i>=L.length)return false;
    pushUndo();
    var nm=L[i].name;
    L.splice(i,1);
    /* its features stay stored, so an undo brings the layer back whole; a load drops orphans */
    delete A3D_DATA.cache[id];
    if(A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();
    a3dToast(nm+' removed');
    return true;
  }
  function bimDataSet(id,field,val){
    var L=bimDataById(id),v;
    if(!L)return false;
    if(field==='visible'){v=!!val&&val!=='false';if(L.visible===v)return true;}
    else if(field==='name'){v=String(val==null?'':val).replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,60);if(!v){a3dToast('A data layer needs a name');refreshProps();return false;}}
    else if(field==='color'){v=String(val||'');if(!/^#[0-9a-fA-F]{6}$/.test(v)){a3dToast('That is not a colour');refreshProps();return false;}v=v.toLowerCase();}
    else return false;
    if(L[field]===v)return true;
    pushUndo();
    L[field]=v;
    if(field==='visible'&&!v&&A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();
    return true;
  }
  /* a layer's features in model terms, kept until the site's place, true north or the features change */
  function bimDataModel(L){
    var org=bimMapOrigin(),F=bimDataFeats(L.id),key,c;
    if(!org)return null;
    key=org.lat+','+org.lon+','+bimTrueNorthDeg();
    c=A3D_DATA.cache[L.id];
    if(c&&c.key===key&&c.F===F)return c;
    c={key:key,F:F,feats:[]};
    F.forEach(function(f,fi){
      var x={fi:fi,rings:[],lines:[],points:[],area:0};
      bimGeoParts(f.g).forEach(function(pp){
        var pt=bimGeoPositions(pp.pts),m;
        if(!pt)return;
        m=pt.map(function(q){return bimGeoToModel(q[0],q[1],org);});
        if(pp.kind==='ring'){
          if(m.length>1&&m[0][0]===m[m.length-1][0]&&m[0][1]===m[m.length-1][1])m.pop();
          if(m.length>=3){x.rings.push({pts:m,hole:!!pp.hole});x.area+=(pp.hole?-1:1)*bimPolyArea(m);}
        }else if(pp.kind==='line'){if(m.length>=2)x.lines.push(m);}
        else if(pp.kind==='point')x.points.push(m[0]);
      });
      c.feats.push(x);
    });
    A3D_DATA.cache[L.id]=c;
    return c;
  }
  /* on the plan, under the model's linework: never on paper */
  function drawDataLayers(ctx,V,W,H){
    A3D.lastDataDrawn=0;
    if(A3D.sheetCapture||A3D_PLOT.on)return;
    var L=bimDataList(),y=bimShadowGround(),i,j,c,f,sel,n=0;
    function S(p){return toScreen([p[0],y,p[1]],V,W,H);}
    function path(pts,close){
      var p=S(pts[0]),k;
      ctx.moveTo(p[0],p[1]);
      for(k=1;k<pts.length;k++){p=S(pts[k]);ctx.lineTo(p[0],p[1]);}
      if(close)ctx.closePath();
    }
    for(i=0;i<L.length;i++){
      if(!L[i].visible)continue;
      c=bimDataModel(L[i]);
      if(!c)continue;
      ctx.save();
      ctx.strokeStyle=L[i].color;ctx.fillStyle=L[i].color;
      for(j=0;j<c.feats.length;j++){
        f=c.feats[j];
        sel=!!(A3D_DATA.sel&&A3D_DATA.sel.layer===L[i].id&&A3D_DATA.sel.fi===f.fi);
        ctx.lineWidth=sel?2.6:1.2;
        if(f.rings.length){
          ctx.beginPath();
          f.rings.forEach(function(r){path(r.pts,true);});
          ctx.globalAlpha=sel?0.34:0.16;ctx.fill('evenodd');ctx.globalAlpha=1;ctx.stroke();
        }
        if(f.lines.length){ctx.beginPath();f.lines.forEach(function(l){path(l,false);});ctx.stroke();}
        f.points.forEach(function(q){var p=S(q);ctx.beginPath();ctx.arc(p[0],p[1],sel?5:3.5,0,Math.PI*2);ctx.fill();});
        n++;
      }
      ctx.restore();
    }
    A3D.lastDataDrawn=n;
  }
  /* what data is under a screen point: a point, then a line, then the smallest area; later layers first */
  function bimDataPick(sx,sy){
    var L=bimDataList(),y=bimShadowGround(),g=groundPoint(sx,sy,y),P,tol,i,j,k,c,f,best=null,bestA=Infinity,pass,inside;
    if(!g)return null;
    P=[g[0],g[2]];
    tol=6*Math.max(A3D.cam.dist,0.5)/(Math.max(1,cvH())*1.2);
    for(pass=0;pass<3;pass++){
      for(i=L.length-1;i>=0;i--){
        if(!L[i].visible)continue;
        c=bimDataModel(L[i]);
        if(!c)continue;
        for(j=c.feats.length-1;j>=0;j--){
          f=c.feats[j];
          if(pass===0){
            for(k=0;k<f.points.length;k++)if(Math.hypot(f.points[k][0]-P[0],f.points[k][1]-P[1])<=tol)return {layer:L[i].id,fi:f.fi};
          }else if(pass===1){
            for(k=0;k<f.lines.length;k++){
              var l=f.lines[k],m;
              for(m=0;m+1<l.length;m++)if(bimPointSegDist(P[0],P[1],l[m][0],l[m][1],l[m+1][0],l[m+1][1])<=tol)return {layer:L[i].id,fi:f.fi};
            }
          }else if(f.rings.length){
            inside=0;
            for(k=0;k<f.rings.length;k++)if(bimPointInPoly(P,f.rings[k].pts))inside++;
            if(inside%2===1&&f.area<bestA){bestA=f.area;best={layer:L[i].id,fi:f.fi};}
          }
        }
      }
    }
    return best;
  }
  /* the picked area's largest outer ring as a property line: one undo step */
  function bimDataToProperty(){
    var s=A3D_DATA.sel,L=s?bimDataById(s.layer):null,c=L?bimDataModel(L):null,f=null,outer=null,i,legs,pr;
    if(c)for(i=0;i<c.feats.length;i++)if(c.feats[i].fi===s.fi)f=c.feats[i];
    if(!f||!f.rings.length){a3dToast('Pick an area, such as a parcel, to make a property line from');return null;}
    f.rings.forEach(function(r){if(!r.hole&&(!outer||bimPolyArea(r.pts)>bimPolyArea(outer)))outer=r.pts;});
    if(!outer){a3dToast('That area has no outer ring');return null;}
    legs=bimLegsFromRing(outer);
    if(legs.length<3){a3dToast('That area has fewer than 3 sides');return null;}
    pushUndo();
    pr=bimNewProperty(outer[0],legs);
    pr.dataSource={layer:L.name,credit:L.credit,props:JSON.parse(JSON.stringify(bimDataFeats(L.id)[s.fi].p||{}))};
    A3D.objs.push(pr);
    A3D.sel=pr.id;A3D.selSet=[pr.id];A3D_DATA.sel=null;
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(pr.name+' from '+L.name+': '+bimClosureText(bimPropertyGeometry(pr)));
    return pr;
  }
  /* the shown layers' credits, for the line over the viewport */
  function bimDataCreditHtml(){
    var L=bimDataList(),c=[],i;
    for(i=0;i<L.length;i++)if(L[i].visible&&bimDataFeats(L[i].id).length&&c.indexOf(L[i].credit)<0)c.push(L[i].credit);
    return c.length?'Data: '+bimEsc(c.join('; ')):'';
  }
"""

rep("""  function bimGlRender(V,W,H){""", ENGINE + """  function bimGlRender(V,W,H){""")
rep("""    if(cc)h=h?h+' \\u00b7 '+cc:cc;""", """    if(cc)h=h?h+' \\u00b7 '+cc:cc;
    var dcr=bimDataCreditHtml();   /* __acad3dV134 */
    if(dcr)h=h?h+' \\u00b7 '+dcr:dcr;""")
rep("""    drawProperties(ctx,V,W,H);     /* __acad3dV103: under the model, like grids */""",
    """    drawDataLayers(ctx,V,W,H);     /* __acad3dV134: the public record, under the property lines */
    drawProperties(ctx,V,W,H);     /* __acad3dV103: under the model, like grids */""")
rep("""      if(gpk)refreshLevels();
""", """      if(gpk)refreshLevels();
      /* __acad3dV134: under them all, the data layers */
      A3D_DATA.sel=(o||gpk)?null:bimDataPick(xy[0],xy[1]);
      if(!o)refreshProps();
""")
# the features travel with the project, outside the undo snapshots
rep("""      if(st&&st.site&&typeof st.site==='object'&&typeof st.site.name==='string')A3D.site=st.site;""",
    """      if(st&&st.site&&typeof st.site==='object'&&typeof st.site.name==='string')A3D.site=st.site;
      A3D.dataFeatures={};   /* __acad3dV134: the features of the project's data layers, orphans dropped */
      if(st&&st.dataFeatures&&typeof st.dataFeatures==='object'&&A3D.site&&Array.isArray(A3D.site.dataLayers))
        A3D.site.dataLayers.forEach(function(L){if(L&&Array.isArray(st.dataFeatures[L.id]))A3D.dataFeatures[L.id]=st.dataFeatures[L.id];});""")
rep("""roomScheme:A3D.roomScheme||'',classifications:A3D.classifications};""",
    """roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{}};""")
rep("""roomScheme:A3D.roomScheme||'',classifications:A3D.classifications}});""",
    """roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{}}});""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
