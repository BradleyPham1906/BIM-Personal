"""patch_phase135b.py -- V135: find open data, in the Data Layers group.

- Portal: every portal of BIM_DATA_PORTALS, grouped (federal; each state; its cities and counties),
  first guessed from the site's address, then remembered.
- Find: words, Search (or Enter), Near the site only. Each result names its kind and owner, links to
  its page, and has Add; a service with several layers lists them to add one by one. More continues.
- The credit to GeoLibre for the list and the searches.
- FINDDATA (OPENDATA, PORTAL) opens the group at the search."""
NAME = 'patch_phase135b.py'
BASE = 'ae3aab71b665a5160cf30a131dbe85371377e58fda8d155e3a7822a77ba47c39'
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


UI = r"""  /* ================= __acad3dV135: find open data, in Properties ================= */
  function bimFindHtml(){
    var P=bimFindCurrent(),o='<option value="">Pick a portal ...</option>',r='',g,i,G,it,k,pk,ad;
    for(g=0;g<BIM_DATA_PORTALS.length;g++){
      G=BIM_DATA_PORTALS[g];o+='<optgroup label="'+bimEsc(G[0])+'">';
      for(i=0;i<G[1].length;i++)o+='<option value="'+bimEsc(G[1][i][1])+'"'+(P&&P.host===G[1][i][1]?' selected':'')+'>'+bimEsc(G[1][i][0])+'</option>';
      o+='</optgroup>';
    }
    r+=bimPropRow('Find data','<select data-propfind="portal" aria-label="Open-data portal to search">'+o+'</select>');
    r+=bimPropRow('','<div class="a3d-ukv"><input type="text" data-propfind="q" value="'+bimEsc(A3D_FIND.q)+'" placeholder="parcels, zoning, trees ..." spellcheck="false" aria-label="Words to find">'+
      '<button type="button" class="a3d-pedit" data-propfindact="search"'+(A3D_FIND.busy?' disabled':'')+'>Search</button></div>');
    r+=bimPropRow('','<label class="a3d-ctxk"><input type="checkbox" data-propfind="near"'+(A3D_FIND.near?' checked':'')+'> Near the site only</label>');
    if(A3D_FIND.err)r+=bimPropRow('','<span class="a3d-pstatic a3d-uerr">'+bimEsc(A3D_FIND.err)+'</span>');
    else if(A3D_FIND.said)r+=bimPropRow('','<span class="a3d-pstatic">'+bimEsc(A3D_FIND.said)+'</span>');
    for(i=0;i<A3D_FIND.res.length;i++){
      it=A3D_FIND.res[i];ad=bimFindAdded(it);
      r+='<div class="a3d-fdrow"><div class="a3d-fdt"><a class="a3d-ctxlink" href="'+bimEsc(it.page)+'" target="_blank" rel="noopener noreferrer" title="'+bimEsc(it.snippet||it.title)+'">'+bimEsc(it.title)+'</a>'+
        '<span class="a3d-fdk">'+bimEsc(it.type+(it.owner?' - '+it.owner:''))+'</span></div>'+
        (ad?'<span class="a3d-fdk">added</span>':'<button type="button" class="a3d-pedit" data-propfindact="add:'+i+'">Add</button>')+'</div>';
      pk=A3D_FIND.pick;
      if(pk&&pk.ix===i)for(k=0;k<pk.layers.length;k++){
        var lu=String(it.url||'').split('?')[0].replace(/\/+$/,'')+'/'+pk.layers[k].id,had=false,L=bimDataList(),j;
        for(j=0;j<L.length;j++)if(L[j].url===lu)had=true;
        r+='<div class="a3d-fdrow a3d-fdsub"><div class="a3d-fdt">'+bimEsc(pk.layers[k].name)+'</div>'+
          (had?'<span class="a3d-fdk">added</span>':'<button type="button" class="a3d-pedit" data-propfindact="layer:'+i+':'+k+'">Add</button>')+'</div>';
      }
    }
    if(A3D_FIND.next&&!A3D_FIND.busy)r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propfindact="more">More results</button>');
    r+=bimPropText('Portals',BIM_FIND_CREDIT);
    return r;
  }
  function bimFindPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propfind]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propfind');
    if(k==='q'){A3D_FIND.q=String(f.value||'').slice(0,120);return true;}   /* searched by Search, never as it is typed */
    if(k==='near'){A3D_FIND.near=!!f.checked;return true;}
    if(k==='portal'){bimFindSetPortal(f.value);refreshProps();return true;}
    return false;
  }
  function bimFindPropClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-propfindact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-propfindact'),b=a.split(':'),q;
    if(a==='search'){q=el.propsbody.querySelector('[data-propfind="q"]');bimFindSearch(q?q.value:'');return true;}
    if(a==='more'){bimFindSearch(null,true);return true;}
    if(b[0]==='add'){bimFindAdd(parseInt(b[1],10));return true;}
    if(b[0]==='layer'){
      var pk=A3D_FIND.pick,ix=parseInt(b[1],10),ly=pk&&pk.ix===ix?pk.layers[parseInt(b[2],10)]:null;
      if(ly)bimFindAdd(ix,ly);
      return true;
    }
    return false;
  }
  /* FINDDATA: the Data Layers group, at the search */
  function bimFindCommand(){
    bimDataCommand();
    var q=el.propsbody&&el.propsbody.querySelector('[data-propfind="q"]');
    if(q){try{q.focus();q.scrollIntoView({block:'center'});}catch(eF){}}
    a3dToast('Find data: pick a city, county, state or agency portal, type what you need, and Search');
    return true;
  }
"""

rep("""  /* DATALAYERS: the group, with nothing selected */""", UI + """  /* DATALAYERS: the group, with nothing selected */""")
rep("""    r+=bimPropText('Area','the site context radius, '+bimCtxSettings().radius+' m');
    return r;""", """    r+=bimPropText('Area','the site context radius, '+bimCtxSettings().radius+' m');
    r+=bimFindHtml();   /* __acad3dV135 */
    return r;""")
rep("""    /* __acad3dV134: the Data Layers group and a data feature */""", """    /* __acad3dV135: find open data */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimFindPropChange(ev);}catch(eFC){console.warn('[BIM] Find data setting failed',eFC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimFindPropClick(ev);}catch(eFK){console.warn('[BIM] Find data action failed',eFK);a3dToast('That did not work - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      var q=ev.target&&ev.target.closest?ev.target.closest('[data-propfind="q"]'):null;
      if(!q||ev.key!=='Enter')return;
      ev.preventDefault();ev.stopPropagation();
      bimFindSearch(q.value);
    });
    /* __acad3dV134: the Data Layers group and a data feature */""")
rep("""    ['DATALAYERS',['DATA','PARCELS','ZONING','FLOOD'],'datalayers',""", """    ['FINDDATA',['OPENDATA','PORTAL'],'finddata','Find open data: search a US city, county, state or federal portal and add what it holds as a data layer'],   /* __acad3dV135 */
    ['DATALAYERS',['DATA','PARCELS','ZONING','FLOOD'],'datalayers',""")
rep("""    datalayers:function(){bimDataCommand();},                    /* __acad3dV134 */""",
    """    finddata:function(){bimFindCommand();},                      /* __acad3dV135 */
    datalayers:function(){bimDataCommand();},                    /* __acad3dV134 */""")
rep("""    DATALAYERS:'gis arcgis wfs geojson parcels lots zoning flood fema council open data layers attributes lookup',   /* __acad3dV134 */""",
    """    DATALAYERS:'gis arcgis wfs geojson parcels lots zoning flood fema council open data layers attributes lookup',   /* __acad3dV134 */
    FINDDATA:'search catalog portal hub socrata city county state federal datasets browse discover',   /* __acad3dV135 */""")
rep(""".a3d-dlrow .a3d-pstatic{display:inline-block;max-width:160px;white-space:normal}""",
    """.a3d-dlrow .a3d-pstatic{display:inline-block;max-width:160px;white-space:normal}
.a3d-fdrow{display:flex;align-items:center;gap:6px;padding:3px 8px 3px 12px;border-top:1px solid rgba(127,127,127,.15)}
.a3d-fdrow.a3d-fdsub{padding-left:24px}
.a3d-fdt{flex:1;min-width:0;display:flex;flex-direction:column;font-size:11.5px}
.a3d-fdt a{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.a3d-fdk{font-size:10.5px;opacity:.65;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.a3d-fdrow .a3d-pedit{flex:none}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
