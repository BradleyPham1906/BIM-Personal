"""patch_phase136b.py -- V136: the lens in Properties, and the command.

- View group: Colour by (Off, Usage, Level, Type, Layer, Material, Height, Property), and for
  Property the property to colour by, from the ones the model's objects carry.
- Each data layer holding features: Colour by (one of its attributes) and Opacity (%).
- COLOURBY (COLORBY, LENS) opens the View group at Colour by."""
NAME = 'patch_phase136b.py'
BASE = '0892a22bc6facb575dd63695bf87e1374e591eed725a8a93bc71873370c06230'
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


UI = r"""  /* ================= __acad3dV136: the lens in Properties ================= */
  function bimLensHtml(){
    var st=bimLensSettings(),o='<option value=""'+(st.by?'':' selected')+'>Off</option>',i,r='',keys,k;
    for(i=0;i<BIM_LENS_BY.length;i++)o+='<option value="'+BIM_LENS_BY[i]+'"'+(st.by===BIM_LENS_BY[i]?' selected':'')+'>'+BIM_LENS_LABEL[BIM_LENS_BY[i]]+'</option>';
    r+=bimPropRow('Colour by','<select data-proplens="by" aria-label="Colour the model by">'+o+'</select>');
    if(st.by==='prop'){
      keys=bimLensPropKeys();
      if(st.prop&&keys.indexOf(st.prop)<0)keys.unshift(st.prop);
      o='<option value="">Pick a property ...</option>';
      for(k=0;k<keys.length;k++)o+='<option value="'+bimEsc(keys[k])+'"'+(keys[k]===st.prop?' selected':'')+'>'+bimEsc(keys[k])+'</option>';
      r+=bimPropRow('Property',keys.length?'<select data-proplens="prop" aria-label="Property to colour by">'+o+'</select>':
        '<span class="a3d-pstatic">no object carries one yet: get the site context, or import GeoJSON</span>');
    }
    return r;
  }
  function bimDataLensRow(L){
    var keys=bimDataAttrKeys(L.id),o='<option value="">Its colour</option>',k,id=bimEsc(L.id);
    if(!keys.length)return '';
    for(k=0;k<keys.length;k++)o+='<option value="'+bimEsc(keys[k])+'"'+(keys[k]===L.by?' selected':'')+'>'+bimEsc(keys[k])+'</option>';
    return '<div class="a3d-prow a3d-dllens"><div class="a3d-plabel">Colour by</div><div class="a3d-pval"><div class="a3d-ukv">'+
      '<select data-propdata="by:'+id+'" aria-label="Colour '+bimEsc(L.name)+' by">'+o+'</select>'+
      '<input type="number" min="10" max="100" step="10" data-propdata="opacity:'+id+'" value="'+Math.round(bimDataOpacity(L)*100)+'" aria-label="Opacity (%)" title="Opacity (%)"></div></div></div>';
  }
  function bimLensPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-proplens]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-proplens'),st=bimLensSettings();
    if(k==='by'){bimLensSet(f.value,f.value==='prop'?st.prop:'');return true;}
    if(k==='prop'){bimLensSet('prop',f.value);return true;}
    return false;
  }
  /* COLOURBY: the View group, at Colour by */
  function bimLensCommand(){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D_PROP_GROUPS_OPEN['View']=true;
    refreshTree();refreshProps();paint();
    var s=el.propsbody&&el.propsbody.querySelector('[data-proplens="by"]');
    if(s){try{s.focus();s.scrollIntoView({block:'center'});}catch(eF){}}
    a3dToast('Colour by is in the View group: usage, level, type, layer, material, height or any property, with a legend');
    return true;
  }
"""

rep("""  /* DATALAYERS: the group, with nothing selected */""", UI + """  /* DATALAYERS: the group, with nothing selected */""")
rep("""        '<button type="button" class="a3d-bdel" data-propdataact="remove:'+id+'" title="Remove this data layer">\\u00d7</button></div></div>';
    }""", """        '<button type="button" class="a3d-bdel" data-propdataact="remove:'+id+'" title="Remove this data layer">\\u00d7</button></div></div>';
      r+=bimDataLensRow(L[i]);   /* __acad3dV136 */
    }""")
rep("""    if(b[0]==='color')return bimDataSet(b[1],'color',f.value);""", """    if(b[0]==='color')return bimDataSet(b[1],'color',f.value);
    if(b[0]==='by')return bimDataSet(b[1],'by',f.value);             /* __acad3dV136 */
    if(b[0]==='opacity')return bimDataSet(b[1],'opacity',f.value);""")
rep("""    vrows+=bimPropRow('Appearance','<select data-propmodel="present">'+""", """    vrows+=bimLensHtml();   /* __acad3dV136: the lens */
    vrows+=bimPropRow('Appearance','<select data-propmodel="present">'+""")
rep("""    /* __acad3dV135: find open data */""", """    /* __acad3dV136: the lens */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimLensPropChange(ev);}catch(eLC){console.warn('[BIM] Colour by failed',eLC);a3dToast('That could not be changed - see the console');}
    });
    /* __acad3dV135: find open data */""")
rep("""    ['ROOMCOLOR',['COLORFILL','ROOMCOLOUR'],'roomcolor',""", """    ['COLOURBY',['COLORBY','LENS'],'colourby','Colour the model by usage, level, type, layer, material, height or any property, with a legend'],   /* __acad3dV136 */
    ['ROOMCOLOR',['COLORFILL','ROOMCOLOUR'],'roomcolor',""")
rep("""    roomcolor:function(){bimCycleRoomScheme();},       /* __acad3dV105 */""", """    colourby:function(){bimLensCommand();},          /* __acad3dV136 */
    roomcolor:function(){bimCycleRoomScheme();},       /* __acad3dV105 */""")
rep("""ROOMCOLOR:'color fill scheme department',""", """ROOMCOLOR:'color fill scheme department',COLOURBY:'color colour lens legend scheme theme thematic height usage heatmap',""")
rep(""".a3d-fdrow .a3d-pedit{flex:none}""", """.a3d-fdrow .a3d-pedit{flex:none}
.a3d-dllens .a3d-ukv select{flex:1;min-width:0}
.a3d-dllens .a3d-ukv input[type=number]{width:54px}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
