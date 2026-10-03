"""patch_phase133b.py -- V133: site context in Properties, and the commands.

- With nothing selected, a Site Context group after the Map: the radius, which kinds to get (all
  six by default), the Overpass server, Get Context and Remove Context, what the last fetch
  brought, and the sources.
- A context object's page has a Context group: source and credit, the OSM id with a link, a
  building's height and where it came from, its courtyards, the ground under it, and its tags.
- CONTEXT (SITECONTEXT, OSM) gets it; CONTEXTREMOVE (CONTEXTCLEAR) removes it. Site Context is on
  the ribbon beside the map's tools, so the tools panel and the search list it."""
NAME = 'patch_phase133b.py'
BASE = '052b10e0c961d2fcb31085eed4a58b760cbd917a2590ab9907679abbe2a67d3a'
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


UI = r"""  /* ================= __acad3dV133: site context in Properties ================= */
  function bimCtxCountsText(c){
    var s=[],i,k;
    for(i=0;i<BIM_CTX_KINDS.length;i++){k=BIM_CTX_KINDS[i];if(c&&c[k])s.push(c[k]+' '+(k==='terrain'?'surface':BIM_CTX_LABEL[k].toLowerCase()));}
    return s.length?s.join(', '):'nothing';
  }
  function bimCtxModelHtml(){
    var st=bimCtxSettings(),r='',i,k,ck='',last=A3D.site&&A3D.site.context&&A3D.site.context.last;
    r+=bimPropRow('Radius (m)','<input type="number" min="50" max="1000" step="10" data-propctx="radius" value="'+st.radius+'" title="How far around the property lines, or around model 0,0">');
    for(i=0;i<BIM_CTX_KINDS.length;i++){
      k=BIM_CTX_KINDS[i];
      ck+='<label class="a3d-ctxk"><input type="checkbox" data-propctx="kind:'+k+'"'+(st.kinds[k]?' checked':'')+'> '+BIM_CTX_LABEL[k]+'</label>';
    }
    r+=bimPropRow('Get','<div class="a3d-ctxks">'+ck+'</div>');
    r+=bimPropRow('Overpass','<input type="text" data-propctx="overpass" value="'+bimEsc(st.overpass)+'" spellcheck="false" title="The Overpass API server OpenStreetMap is read from">');
    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propctxact="get">Get Context</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="remove">Remove Context</button>');
    if(last)r+=bimPropText('Last Fetch',last.date+': '+bimCtxCountsText(last.counts)+(last.errors&&last.errors.length?'; '+last.errors.join('; '):''));
    r+=bimPropText('Sources','OpenStreetMap (ODbL) through Overpass; AWS Terrain Tiles');
    return r;
  }
  function bimCtxPropsHtml(o){
    var c=o.context,r='',k,n=0;
    r+=bimPropText('Source',c.source+(c.osm?' '+c.osm+' '+c.id:'')+(c.fetched?', '+c.fetched:''));
    r+=bimPropText('Credit',c.credit||'');
    if(c.osm)r+=bimPropRow('On OSM','<a class="a3d-ctxlink" href="https://www.openstreetmap.org/'+bimEsc(c.osm)+'/'+bimEsc(String(c.id))+'" target="_blank" rel="noopener">openstreetmap.org/'+bimEsc(c.osm)+'/'+bimEsc(String(c.id))+'</a>');
    if(c.kind==='buildings'){
      r+=bimPropText('Height',bimDispNum(c.height,2)+' m, '+({height:'from its height tag',levels:'its levels at '+BIM_CTX_LEVEL_H+' m each',
        assumed:'assumed: OSM gives no height or levels'})[c.heightFrom]);
      if(c.courtyards)r+=bimPropText('Courtyards',c.courtyards+' filled in');
      if(c.ground!=null)r+=bimPropText('Ground',bimDispNum(c.ground,2)+' m from model y 0, on the terrain');
    }
    if(c.part==='hole')r+=bimPropText('Ring','a hole in the area before it');
    if(c.kind==='terrain'){
      r+=bimPropText('Zoom',String(c.zoom));
      if(c.datum!=null)r+=bimPropText('Datum','model y 0 is '+bimDispNum(c.datum,2)+' m above sea level');
    }
    for(k in c.tags)if(c.tags&&c.tags.hasOwnProperty(k)&&n<60){n++;r+=bimPropText(k,c.tags[k]);}
    return bimPropGroup('Context',r);
  }
  function bimCtxPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propctx]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propctx');
    bimCtxSet(k,k.indexOf('kind:')===0?f.checked:f.value);
    return true;
  }
  function bimCtxPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-propctxact]'):null;
    if(!b)return false;
    var a=b.getAttribute('data-propctxact');
    if(a==='get'){bimCtxFetch();return true;}
    if(a==='remove'){bimCtxRemove();return true;}
    return false;
  }
"""

rep("""  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the""",
    UI + """  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the""")
rep("""    h+=bimPropGroup('Map',bimMapPropsHtml());   /* __acad3dV132 */""",
    """    h+=bimPropGroup('Map',bimMapPropsHtml());   /* __acad3dV132 */
    h+=bimPropGroup('Site Context',bimCtxModelHtml());   /* __acad3dV133 */""")
rep("""    if(o.geo)h+=bimGeoPropsHtml(o);                     /* __acad3dV132 */""",
    """    if(o.geo)h+=bimGeoPropsHtml(o);                     /* __acad3dV132 */
    if(o.context)h+=bimCtxPropsHtml(o);                 /* __acad3dV133 */""")
rep("""    /* __acad3dV132: the Map group */""", """    /* __acad3dV133: the Site Context group */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimCtxPropChange(ev);}catch(eXC){console.warn('[BIM] Context setting failed',eXC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimCtxPropClick(ev);}catch(eXK){console.warn('[BIM] Context action failed',eXK);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV132: the Map group */""")

# ---- commands, ribbon, search
rep("""    ['GEOEXPORT',['EXPORTGEOJSON'],'geoexport',""", """    /* __acad3dV133: site context */
    ['CONTEXT',['SITECONTEXT','OSM'],'context','Get the buildings, roads, water, green, trees and terrain around the site, from OpenStreetMap and AWS Terrain Tiles'],
    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],
    ['GEOEXPORT',['EXPORTGEOJSON'],'geoexport',""")
rep("""    geoexport:function(){bimGeoExport();},""", """    geoexport:function(){bimGeoExport();},
    context:function(){bimCtxFetch();},                          /* __acad3dV133 */
    contextremove:function(){bimCtxRemove();},""")
rep("""    if(act==='m:exportgeojson'){bimGeoExport();return;}""", """    if(act==='m:exportgeojson'){bimGeoExport();return;}
    if(act==='bim:context'){bimCtxFetch();return;}                      /* __acad3dV133 */""")
rep("""'bim:geoimport':'geoimport',""", """'bim:geoimport':'geoimport','bim:context':'context',""")
rep("""'bim:geoimport':'Import GeoJSON',""", """'bim:geoimport':'Import GeoJSON','bim:context':'Site Context',""")
rep("""'bim:map','bim:findaddress','bim:geoimport',""", """'bim:map','bim:findaddress','bim:geoimport','bim:context',""")
rep("""    GEOEXPORT:'geojson gis export longitude latitude',""", """    GEOEXPORT:'geojson gis export longitude latitude',
    CONTEXT:'neighbours neighbors surrounding buildings osm openstreetmap overpass roads streets water rivers parks trees terrain elevation contours ground giraffe',   /* __acad3dV133 */
    CONTEXTREMOVE:'delete clear neighbours context',""")
rep("""    'bim:usage':ric(""", """    'bim:context':ric('<path d="M3 21h18"/><rect x="4" y="11" width="5" height="10"/><rect x="10" y="5" width="6" height="16"/><rect x="17" y="13" width="4" height="8"/><path d="M12 9h2M12 13h2"/>'),   /* __acad3dV133 */
    'bim:usage':ric(""")

rep(""".a3d-dlgwide{width:330px}""", """.a3d-dlgwide{width:330px}
.a3d-ctxks{display:flex;flex-wrap:wrap;gap:3px 10px}
.a3d-ctxk{display:inline-flex;align-items:center;gap:3px;white-space:nowrap;font-size:11.5px;color:inherit}
.a3d-ctxlink{color:#9cc4ff;text-decoration:none}
.a3d-ctxlink:hover{text-decoration:underline}
body.light-theme .a3d-ctxlink{color:#0b5cad}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
