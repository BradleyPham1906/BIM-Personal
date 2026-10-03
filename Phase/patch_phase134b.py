"""patch_phase134b.py -- V134: data layers in Properties, and the command.

- With nothing selected, a Data Layers group after the Site Context: each layer with a box to show
  it, its colour, what it holds or why it failed, Refresh and Remove; a preset list and an address
  to add one.
- A data feature clicked on the plan heads the page: its layer, its source, its attributes, and for
  an area, Make Property Line.
- DATALAYERS (DATA, PARCELS, ZONING, FLOOD) opens the group; it is on the Site panel."""
NAME = 'patch_phase134b.py'
BASE = '19bc0811ef082076b5d9df533ac5636c62531d072ea158fce8612670259a96b8'
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


UI = r"""  /* ================= __acad3dV134: data layers in Properties ================= */
  function bimDataStatusText(L){
    var s=L.status;
    if(A3D_DATA.busy[L.id])return 'getting ...';
    if(!s)return 'not fetched yet';
    if(s.error)return s.error;
    return s.count+' feature'+(s.count===1?'':'s')+(s.more?' (more on the server)':'')+', '+s.date;
  }
  function bimDataModelHtml(){
    var L=bimDataList(),r='',i,o='';
    for(i=0;i<L.length;i++){
      var id=bimEsc(L[i].id);
      r+='<div class="a3d-prow a3d-uhead a3d-dlrow"><div class="a3d-plabel"><label class="a3d-ctxk"><input type="checkbox" data-propdata="vis:'+id+'"'+(L[i].visible?' checked':'')+
        ' aria-label="Show '+bimEsc(L[i].name)+'"> <input type="color" data-propdata="color:'+id+'" value="'+bimEsc(L[i].color)+'" aria-label="Colour"> '+bimEsc(L[i].name)+'</label></div>'+
        '<div class="a3d-pval"><span class="a3d-pstatic'+(L[i].status&&L[i].status.error?' a3d-uerr':'')+'">'+bimEsc(bimDataStatusText(L[i]))+'</span> '+
        '<button type="button" class="a3d-pedit" data-propdataact="refresh:'+id+'">Refresh</button> '+
        '<button type="button" class="a3d-bdel" data-propdataact="remove:'+id+'" title="Remove this data layer">×</button></div></div>';
    }
    if(!L.length)r+=bimPropText('None yet','parcels, zoning or flood zones: add a preset or a web address');
    for(i=0;i<BIM_DATA_PRESETS.length;i++)o+='<option value="'+i+'">'+bimEsc(BIM_DATA_PRESETS[i].name)+'</option>';
    r+=bimPropRow('Preset','<select data-propdata="preset"><option value="">Add a preset ...</option>'+o+'</select>');
    r+=bimPropRow('Address','<div class="a3d-ukv"><input type="text" data-propdata="url" placeholder="ArcGIS .../FeatureServer/0, a WFS, or GeoJSON" spellcheck="false" aria-label="Data layer address">'+
      '<button type="button" class="a3d-pedit" data-propdataact="add">Add</button></div>');
    r+=bimPropText('Area','the site context radius, '+bimCtxSettings().radius+' m');
    return r;
  }
  /* the feature clicked on the plan */
  function bimDataFeatureHtml(){
    var s=A3D_DATA.sel,L=s?bimDataById(s.layer):null,F=L?bimDataFeats(L.id)[s.fi]:null,r='',k,n=0,c;
    if(!F)return '';
    r+=bimPropText('Layer',L.name);
    r+=bimPropText('Source',L.credit);
    for(k in F.p)if(F.p.hasOwnProperty(k)&&n<60){n++;r+=bimPropText(k,F.p[k]===null?'':String(F.p[k]));}
    if(!n)r+=bimPropText('Attributes','none');
    c=bimDataModel(L);
    var f=null,i;
    if(c)for(i=0;i<c.feats.length;i++)if(c.feats[i].fi===s.fi)f=c.feats[i];
    if(f&&f.rings.length)r+=bimPropText('Area',bimDispNum(f.area,2)+' m²');
    r+=bimPropRow('',(f&&f.rings.length?'<button type="button" class="a3d-pedit" data-propdataact="toprop">Make Property Line</button> ':'')+
      '<button type="button" class="a3d-pedit" data-propdataact="clear">Close</button>');
    return bimPropGroup('Data Feature',r);
  }
  function bimDataPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propdata]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propdata'),b=k.split(':');
    if(k==='url')return true;   /* added by Add, never as it is typed */
    if(k==='preset'){
      var p=BIM_DATA_PRESETS[parseInt(f.value,10)];
      if(p)bimDataAdd(p.url,p.name,p.color,p.credit);
      return true;
    }
    if(b[0]==='vis')return bimDataSet(b[1],'visible',f.checked);
    if(b[0]==='color')return bimDataSet(b[1],'color',f.value);
    return false;
  }
  function bimDataPropClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-propdataact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-propdataact'),b=a.split(':');
    if(a==='add'){var u=el.propsbody.querySelector('[data-propdata="url"]');bimDataAdd(u?u.value:'');return true;}
    if(a==='toprop'){bimDataToProperty();return true;}
    if(a==='clear'){A3D_DATA.sel=null;refreshProps();paint();return true;}
    if(b[0]==='refresh'){bimDataFetch(b[1]);refreshProps();return true;}
    if(b[0]==='remove'){bimDataRemove(b[1]);return true;}
    return false;
  }
  /* DATALAYERS: the group, with nothing selected */
  function bimDataCommand(){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D_PROP_GROUPS_OPEN['Data Layers']=true;
    refreshTree();refreshProps();paint();
    var g=el.propsbody&&el.propsbody.querySelector('[data-a3dpgrp="Data Layers"]');
    if(g){try{g.scrollIntoView({block:'start'});}catch(eS){}}
    a3dToast('Data layers are in Properties: add a preset, or the web address of an ArcGIS layer, a WFS or a GeoJSON file');
    return true;
  }
"""

rep("""  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the""",
    UI + """  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the""")
rep("""    h+=bimPropGroup('Identity Data',rows);""", """    h+=bimDataFeatureHtml();   /* __acad3dV134: the data clicked on the plan, first */
    h+=bimPropGroup('Identity Data',rows);""")
rep("""    h+=bimPropGroup('Site Context',bimCtxModelHtml());   /* __acad3dV133 */""",
    """    h+=bimPropGroup('Site Context',bimCtxModelHtml());   /* __acad3dV133 */
    h+=bimPropGroup('Data Layers',bimDataModelHtml());   /* __acad3dV134 */""")
rep("""    /* __acad3dV133: the Site Context group */""", """    /* __acad3dV134: the Data Layers group and a data feature */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimDataPropChange(ev);}catch(eDC){console.warn('[BIM] Data layer setting failed',eDC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimDataPropClick(ev);}catch(eDK){console.warn('[BIM] Data layer action failed',eDK);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV133: the Site Context group */""")
rep("""    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],""",
    """    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],
    /* __acad3dV134: data layers */
    ['DATALAYERS',['DATA','PARCELS','ZONING','FLOOD'],'datalayers','Parcels, zoning, flood zones: ArcGIS, WFS or GeoJSON data around the site, drawn on the plan and read by a click'],""")
rep("""    contextremove:function(){bimCtxRemove();},""", """    contextremove:function(){bimCtxRemove();},
    datalayers:function(){bimDataCommand();},                    /* __acad3dV134 */""")
rep("""    if(act==='bim:context'){bimCtxFetch();return;}                      /* __acad3dV133 */""",
    """    if(act==='bim:context'){bimCtxFetch();return;}                      /* __acad3dV133 */
    if(act==='bim:datalayers'){bimDataCommand();return;}                /* __acad3dV134 */""")
rep("""'bim:context':'context',""", """'bim:context':'context','bim:datalayers':'datalayers',""")
rep("""'bim:context':'Site Context',""", """'bim:context':'Site Context','bim:datalayers':'Data Layers',""")
rep("""'bim:geoimport','bim:context',""", """'bim:geoimport','bim:context','bim:datalayers',""")
rep("""    CONTEXTREMOVE:'delete clear neighbours context',""", """    CONTEXTREMOVE:'delete clear neighbours context',
    DATALAYERS:'gis arcgis wfs geojson parcels lots zoning flood fema council open data layers attributes lookup',   /* __acad3dV134 */""")
rep("""    'bim:context':ric(""", """    'bim:datalayers':ric('<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 16l9 5 9-5"/>'),   /* __acad3dV134 */
    'bim:context':ric(""")
rep(""".a3d-ctxlink:hover{text-decoration:underline}""", """.a3d-ctxlink:hover{text-decoration:underline}
.a3d-dlrow input[type=color]{width:18px;height:16px;padding:0;border:none;background:none;vertical-align:-3px}
.a3d-dlrow .a3d-pstatic{display:inline-block;max-width:160px;white-space:normal}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
