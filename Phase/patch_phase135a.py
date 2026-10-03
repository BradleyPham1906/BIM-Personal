"""patch_phase135a.py -- V135: find open data, the engine.

The portal list and the two searches are ported from GeoLibre (github.com/opengeos/GeoLibre, MIT
licence, (c) 2026 Qiusheng Wu, commit 4ec853f): packages/plugins/src/plugins/
us-{federal,state,local}-gis-catalogs.ts, arcgis-hub-api.ts and socrata-api.ts.

- BIM_DATA_PORTALS: 238 US open-data portals, federal, state, and city and county, made by
  tools/geolibre_portals.py into Phase/geolibre_portals_phase135.json.
- An ArcGIS Hub portal is searched through ArcGIS Online's item search, scoped to the Hub site's
  catalog groups (read once from the site item), or to its organisation when there are none.
- A Socrata portal is searched through the Socrata Discovery API, keeping its spatial datasets.
- Near the site: the Hub search is limited to items whose extent meets the site's area.
- A result is added as a V134 data layer: an ArcGIS layer (a whole service lists its layers to pick
  from), a GeoJSON item, or a Socrata dataset, which is asked for the site's box only."""
NAME = 'patch_phase135a.py'
BASE = '9632fa60cd5e98df2445af587c7985dec6ef6ebda108e34182e32872051c12d0'
import hashlib, json, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')
PORTALS = (pathlib.Path(__file__).resolve().parent / 'geolibre_portals_phase135.json').read_text().strip()
json.loads(PORTALS)


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


ENGINE = r"""  /* ================= __acad3dV135: find open data ================= */
  /* US open-data portals, [group, [[name, host, Hub site id, ArcGIS organisation id, Socrata], ...]].
     The list, and the searches below, are ported from GeoLibre (github.com/opengeos/GeoLibre):
       MIT License
       Copyright (c) 2026 Qiusheng Wu
       Permission is hereby granted, free of charge, to any person obtaining a copy of this software
       and associated documentation files (the "Software"), to deal in the Software without
       restriction, including without limitation the rights to use, copy, modify, merge, publish,
       distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
       Software is furnished to do so, subject to the following conditions:
       The above copyright notice and this permission notice shall be included in all copies or
       substantial portions of the Software.
       THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
       BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
       NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
       DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
       OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. */
  var BIM_DATA_PORTALS=""" + PORTALS + r""";
  var BIM_FIND_CREDIT='Portal list and searches: GeoLibre (MIT licence)';
  var BIM_FIND_TYPES=['Feature Service','Map Service','GeoJson'];
  var BIM_FIND_GEOM={point:1,multipoint:1,line:1,multiline:1,polygon:1,multipolygon:1,location:1};
  var BIM_FIND_NUM=20;
  var A3D_FIND={portal:'',q:'',near:true,busy:false,res:[],next:0,total:0,err:'',said:'',groups:{},pick:null,pending:null};
  function bimFindPortal(host){
    var g,i,P;
    for(g=0;g<BIM_DATA_PORTALS.length;g++)for(i=0;i<BIM_DATA_PORTALS[g][1].length;i++){
      P=BIM_DATA_PORTALS[g][1][i];
      if(P[1]===host)return {group:BIM_DATA_PORTALS[g][0],name:P[0],host:P[1],site:P[2],org:P[3],socrata:!!P[4]};
    }
    return null;
  }
  /* a first guess from the address found for the site: its city or county, else its state */
  function bimFindGuess(){
    var ad=' '+String((A3D.site&&A3D.site.address)||'').toLowerCase().replace(/[^a-z0-9]+/g,' ')+' ',g,i,G,st,best='',stHost='';
    if(ad.length<3)return '';
    function has(w){return ad.indexOf(' '+String(w).toLowerCase().replace(/[^a-z0-9]+/g,' ').replace(/^ | $/g,'')+' ')>=0;}
    for(g=0;g<BIM_DATA_PORTALS.length;g++){
      G=BIM_DATA_PORTALS[g];st=G[0].split(':')[0];
      if(G[0].indexOf('Federal')===0||!has(st))continue;
      if(/: state$/.test(G[0])){if(!stHost)stHost=G[1][0][1];continue;}
      for(i=0;i<G[1].length;i++)if(!best&&has(G[1][i][0].replace(/^(City|County|Town) of /i,'')))best=G[1][i][1];
    }
    return best||stHost;
  }
  function bimFindCurrent(){
    if(!A3D_FIND.portal){
      var pr={};try{pr=bimLoadUIPanelPrefs()||{};}catch(eP){}
      A3D_FIND.portal=bimFindGuess()||(bimFindPortal(pr.dataPortal)?pr.dataPortal:'');
    }
    return bimFindPortal(A3D_FIND.portal);
  }
  function bimFindSetPortal(host){
    if(host&&!bimFindPortal(host))return false;
    A3D_FIND.portal=host||'';A3D_FIND.res=[];A3D_FIND.next=0;A3D_FIND.total=0;A3D_FIND.err='';A3D_FIND.said='';A3D_FIND.pick=null;
    try{var pr=bimLoadUIPanelPrefs()||{};pr.dataPortal=host||'';bimSaveUIPanelPrefs(pr);}catch(eS){}
    return true;
  }
  /* ArcGIS Online's item search: the words, the types read here, the catalog's groups or the
     organisation, public items only; words that are Lucene syntax are dropped, not escaped */
  function bimHubText(q){
    return String(q==null?'':q).replace(/["\\\/(){}\[\]\^~:!?+]|&&|\|\|/g,' ').replace(/\b(?:AND|OR|NOT)\b/gi,' ').replace(/\s+/g,' ').replace(/^ | $/g,'');
  }
  function bimHubSearchUrl(q,o){
    var text=bimHubText(q),i,ty=[],gr=[];
    for(i=0;i<BIM_FIND_TYPES.length;i++)ty.push('type:"'+BIM_FIND_TYPES[i]+'"');
    for(i=0;o.groups&&i<o.groups.length;i++)if(/^[0-9a-f]{32}$/i.test(o.groups[i]))gr.push('group:'+o.groups[i]);
    var qq=(text?'('+text+') AND ':'')+'('+ty.join(' OR ')+')'+(gr.length?' AND ('+gr.join(' OR ')+')':'')+
      (!gr.length&&o.org&&/^[0-9A-Za-z]{16}$/.test(o.org)?' AND orgid:'+o.org:'')+' AND access:public';
    return 'https://www.arcgis.com/sharing/rest/search?q='+encodeURIComponent(qq)+'&f=json&start='+(o.start||1)+'&num='+(o.num||BIM_FIND_NUM)+
      '&sortField='+(text?'relevance':'title')+'&sortOrder='+(text?'desc':'asc')+
      (o.bbox?'&bbox='+o.bbox.map(function(v){return v.toFixed(5);}).join(','):'');
  }
  /* a Hub site's catalog is the groups its site item names (catalogV2 on current sites, catalog on older) */
  function bimHubGroups(js){
    var out=[],seen={},i,j,f,p;
    function add(v){
      if(typeof v==='string'){if(/^[0-9a-f]{32}$/i.test(v)&&!seen[v]){seen[v]=1;out.push(v);}return;}
      if(Array.isArray(v)){for(var k=0;k<v.length;k++)add(v[k]);return;}
      if(v&&typeof v==='object'){add(v.any);add(v.all);}
    }
    f=js&&js.catalogV2&&js.catalogV2.scopes&&js.catalogV2.scopes.item&&js.catalogV2.scopes.item.filters;
    if(Array.isArray(f))for(i=0;i<f.length;i++){p=f[i]&&f[i].predicates;if(Array.isArray(p))for(j=0;j<p.length;j++)add(p[j]&&p[j].group);}
    if(!out.length&&js&&js.catalog)add(js.catalog.groups);
    return out;
  }
  function bimHubSiteGroups(site){
    if(!site)return Promise.resolve([]);
    if(A3D_FIND.groups[site])return Promise.resolve(A3D_FIND.groups[site]);
    return fetch('https://www.arcgis.com/sharing/rest/content/items/'+site+'/data?f=json').then(function(r){
      if(!r.ok)throw {http:r.status};return r.json();
    }).then(function(js){var g=bimHubGroups(js);A3D_FIND.groups[site]=g;return g;},function(){return [];});   /* the organisation is the fallback */
  }
  function bimSocrataSearchUrl(dom,q,offset){
    var text=String(q==null?'':q).replace(/^\s+|\s+$/g,'');
    return 'https://api.us.socrata.com/api/catalog/v1?search_context='+encodeURIComponent(dom)+'&domains='+encodeURIComponent(dom)+'&only=dataset'+
      (text?'&q='+encodeURIComponent(text):'&order=name')+'&offset='+offset+'&limit=100';
  }
  /* one catalog entry as a result, if it is a spatial dataset of this portal; the addresses are
     built from the portal's own host, never taken from the answer */
  function bimSocrataItem(en,dom){
    var r=en&&en.resource,id=r&&String(r.id||'').toLowerCase(),ty,fn,i,geom='';
    if(!r||!/^[a-z0-9]{4}-[a-z0-9]{4}$/.test(id))return null;
    if(!en.metadata||en.metadata.domain!==dom)return null;
    ty=Array.isArray(r.columns_datatype)?r.columns_datatype:[];fn=Array.isArray(r.columns_field_name)?r.columns_field_name:[];
    for(i=0;i<ty.length;i++)if(typeof ty[i]==='string'&&BIM_FIND_GEOM[ty[i].toLowerCase()]){geom=String(fn[i]||'');break;}
    if(i>=ty.length)return null;
    if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(geom))geom='';
    return {src:'socrata',id:id,title:String(r.name||id).slice(0,120),type:'Socrata dataset',
      owner:String((en.classification&&en.classification.domain_category)||r.attribution||dom).slice(0,80),
      snippet:String(r.description||'').slice(0,200),data:'https://'+dom+'/resource/'+id+'.geojson',geom:geom,page:'https://'+dom+'/d/'+id};
  }
  function bimHubItem(it){
    if(!it||!/^[0-9a-f]{32}$/i.test(String(it.id||'')))return null;
    return {src:'hub',id:it.id,title:String(it.title||it.id).slice(0,120),type:String(it.type||''),owner:String(it.owner||'').slice(0,80),
      snippet:String(it.snippet||'').slice(0,200),url:String(it.url||''),page:'https://www.arcgis.com/home/item.html?id='+it.id};
  }
  /* one press, one search; More continues it */
  function bimFindSearch(q,more){
    var P=bimFindCurrent(),a,start;
    if(!P){a3dToast('Pick a portal to search: a city, county, state or federal agency');return null;}
    if(A3D_FIND.busy){a3dToast('A search is already on its way');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot search');return null;}
    if(!more){A3D_FIND.q=String(q==null?A3D_FIND.q:q).replace(/^\s+|\s+$/g,'').slice(0,120);A3D_FIND.res=[];A3D_FIND.next=0;A3D_FIND.pick=null;}
    else if(!A3D_FIND.next)return null;
    start=more?A3D_FIND.next:1;
    a=A3D_FIND.near?bimCtxArea():null;
    A3D_FIND.busy=true;A3D_FIND.err='';A3D_FIND.said='searching '+P.name+' ...';
    refreshProps();
    var host=P.socrata?'api.us.socrata.com':'www.arcgis.com',p;
    function fin(){A3D_FIND.busy=false;refreshProps();}
    if(P.socrata){
      var got=[],off=start-1,total=0,b=0;
      p=(function batch(){
        return fetch(bimSocrataSearchUrl(P.host,A3D_FIND.q,off)).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
          var js,i,it;
          try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
          if(js.error)throw {said:String(js.error).slice(0,160)};
          if(!Array.isArray(js.results))throw {bad:true};
          total=js.resultSetSize||0;
          for(i=0;i<js.results.length;i++){it=bimSocrataItem(js.results[i],P.host);if(it)got.push(it);}
          off+=js.results.length;b++;
          if(!js.results.length||off>=total)return 0;
          if(got.length<BIM_FIND_NUM&&b<5)return batch();
          return off+1;
        });
      })().then(function(next){return {items:got,next:next,total:total};});
    }else{
      p=bimHubSiteGroups(P.site).then(function(gr){
        return fetch(bimHubSearchUrl(A3D_FIND.q,{groups:gr,org:P.org,start:start,bbox:a?[a.w,a.s,a.e,a.n]:null}));
      }).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
        var js,i,it,out=[];
        try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
        if(js.error)throw {said:String(js.error.message||'an error').slice(0,160)};
        if(!Array.isArray(js.results))throw {bad:true};
        for(i=0;i<js.results.length;i++){it=bimHubItem(js.results[i]);if(it)out.push(it);}
        return {items:out,next:js.nextStart>0?js.nextStart:0,total:js.total||0};
      });
    }
    p=p.then(function(r){
      A3D_FIND.res=A3D_FIND.res.concat(r.items);A3D_FIND.next=r.next;A3D_FIND.total=r.total;
      A3D_FIND.said=A3D_FIND.res.length?(A3D_FIND.res.length+' found'+(r.next?', more to see':'')):
        ('nothing found'+(a&&!P.socrata?' near the site: untick Near the site to search the whole portal':''));
      fin();
      return {count:A3D_FIND.res.length,next:r.next};
    },function(e){
      A3D_FIND.err=e&&e.said?host+' said: '+e.said:bimCtxErr(host,e);A3D_FIND.said='';
      fin();a3dToast('Search: '+A3D_FIND.err);
      return {error:A3D_FIND.err};
    });
    A3D_FIND.pending=p;
    return p;
  }
  /* is a result already a data layer? */
  function bimFindAdded(it){
    var L=bimDataList(),i,u=it.src==='socrata'?it.data:it.type==='GeoJson'?bimFindItemData(it.id):String(it.url||'').replace(/\/+$/,'');
    for(i=0;i<L.length;i++)if(u&&(L[i].url===u||L[i].url.indexOf(u+'/')===0))return true;
    return false;
  }
  function bimFindItemData(id){return 'https://www.arcgis.com/sharing/rest/content/items/'+id+'/data';}
  function bimFindCreditFor(){var P=bimFindCurrent();return P?P.name+' open data ('+P.host+')':'';}
  /* a result becomes a V134 data layer; a whole service lists its feature layers to pick from */
  function bimFindAdd(ix,layer){
    var it=A3D_FIND.res[ix],u,cr=bimFindCreditFor(),m;
    if(!it)return null;
    if(it.src==='socrata')return Promise.resolve(bimDataAdd(it.data,it.title,null,cr,{geom:it.geom}));
    if(it.type==='GeoJson')return Promise.resolve(bimDataAdd(bimFindItemData(it.id),it.title,null,cr));
    u=String(it.url||'').split('?')[0].replace(/\/+$/,'');
    if(layer!=null)return Promise.resolve(bimDataAdd(u+'/'+layer.id,(it.title+' - '+layer.name).slice(0,60),null,cr));
    if(/\/(FeatureServer|MapServer)\/\d+$/i.test(u))return Promise.resolve(bimDataAdd(u,it.title,null,cr));
    if(!/^https:\/\/\S+\/(FeatureServer|MapServer)$/i.test(u)){a3dToast(it.title+' has no ArcGIS layer address to read');return Promise.resolve(null);}
    var host=bimMapHost(u);
    a3dToast('Reading the layers of '+it.title+' ...');
    return fetch(u+'?f=json').then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
      var js,i,ls=[],l;
      try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
      if(js.error)throw {said:String(js.error.message||'an error').slice(0,160)};
      for(i=0;Array.isArray(js.layers)&&i<js.layers.length;i++){
        l=js.layers[i];
        if(l&&typeof l.id==='number'&&isFinite(l.id)&&!l.subLayerIds&&(!l.type||/feature layer/i.test(l.type)))ls.push({id:l.id,name:String(l.name||('Layer '+l.id)).slice(0,60)});
      }
      if(!ls.length){a3dToast(it.title+': '+host+' lists no feature layers (it may be imagery)');return null;}
      if(ls.length===1)return bimDataAdd(u+'/'+ls[0].id,it.title,null,cr);
      A3D_FIND.pick={ix:ix,layers:ls};refreshProps();
      a3dToast(it.title+' holds '+ls.length+' layers: pick the ones to add');
      return {pick:ls.length};
    }).then(null,function(e){
      var msg=e&&e.said?host+' said: '+e.said:bimCtxErr(host,e);
      a3dToast(it.title+': '+msg);
      return {error:msg};
    });
  }
"""

# the engine sits after V134's data layers
rep("""  /* a layer added is one undo step, and fetched at once */
  function bimDataAdd(url,name,color,credit){""", ENGINE + """  /* a layer added is one undo step, and fetched at once */
  function bimDataAdd(url,name,color,credit,extra){""")
rep("""      visible:true,credit:String(credit||bimMapHost(u)).slice(0,160)};
    A3D.site.dataLayers.push(lyr);""", """      visible:true,credit:String(credit||bimMapHost(u)).slice(0,160)};
    if(extra&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(extra.geom||''))lyr.geom=extra.geom;   /* __acad3dV135: a Socrata dataset's geometry column */
    A3D.site.dataLayers.push(lyr);""")
# a Socrata dataset is its own kind: asked for the site's box when its geometry column is known
rep("""    if(/\\/(FeatureServer|MapServer)\\/\\d+\\/?(\\?.*)?$/i.test(u))return {kind:'arcgis'};""",
    """    if(/\\/(FeatureServer|MapServer)\\/\\d+\\/?(\\?.*)?$/i.test(u))return {kind:'arcgis'};
    if(/^https?:\\/\\/[^\\/]+\\/resource\\/[a-z0-9]{4}-[a-z0-9]{4}\\.geojson(\\?.*)?$/i.test(u))return {kind:'socrata'};   /* __acad3dV135 */""")
rep("""    return L.url;
  }
  /* an answer as stored features""", """    if(L.kind==='socrata'){   /* __acad3dV135: SoQL within_box(column, north, west, south, east) */
      var sb=L.url.split('?')[0];
      return sb+'?'+(L.geom?'$where='+encodeURIComponent('within_box('+L.geom+','+a.n.toFixed(7)+','+a.w.toFixed(7)+','+a.s.toFixed(7)+','+a.e.toFixed(7)+')')+'&':'')+
        '$limit='+BIM_DATA_MAX;
    }
    return L.url;
  }
  /* an answer as stored features""")
rep("""    m=/[?&]typenames?=([^&]+)/i.exec(u);
    if(m)return decodeURIComponent(m[1]).replace(/^[^:]*:/,'');""", """    m=/[?&]typenames?=([^&]+)/i.exec(u);
    if(m)return decodeURIComponent(m[1]).replace(/^[^:]*:/,'');
    m=/\\/resource\\/([a-z0-9]{4}-[a-z0-9]{4})\\.geojson/i.exec(u);   /* __acad3dV135 */
    if(m)return 'Dataset '+m[1];""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
