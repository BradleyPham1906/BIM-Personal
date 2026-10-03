"""patch_phase139c.py -- V139 (LOD-A): in the app.

- A selected building (a context building or part, or a CityJSON object) has an LOD group: its LOD
  and what that means, how it was made, and its solid check.
- The Site Context group: Check LODs, Export CityJSON, Import CityJSON.
- Commands: CITYJSONOUT, CITYJSONIN, LODCHECK. Hooks for the suites; the marker."""
NAME = 'patch_phase139c.py'
BASE = '7facd0ef2911c166d536cf6755ae1bffad1af426680c78607ec724b4644f00f2'
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


UI = r"""  /* ================= __acad3dV139: the LOD group ================= */
  function bimLodHtml(o){
    var L=bimLodOf(o),r='',chk=bimObjSolidCheck(o),cj=o.cityjson,c=o.context;
    if(!L)return '';
    r+='<div class="a3d-prow" data-lodrow="lod"><div class="a3d-plabel">LOD</div><div class="a3d-pval"><span class="a3d-lodtag">LOD'+bimEsc(L.lod||'?')+'</span> '+
      '<span class="a3d-pstatic">'+bimEsc(bimLodText(L.lod))+'</span></div></div>';
    r+='<div class="a3d-prow" data-lodrow="how"><div class="a3d-plabel">How Made</div><div class="a3d-pval"><span class="a3d-pstatic">'+bimEsc(L.how)+'</span></div></div>';
    if(chk)r+='<div class="a3d-prow a3d-svrow" data-lodrow="solid"><div class="a3d-plabel">'+(chk.surface?'Surfaces':'Solid')+'</div><div class="a3d-pval">'+
      '<span class="a3d-svck a3d-svck-'+(chk.valid?'pass':'fail')+'">'+(chk.valid?'✓':'✗')+'</span> <span class="a3d-pstatic">'+bimEsc(bimSolidCheckText(chk))+'</span></div></div>';
    if(c&&c.building)r+=bimPropText('Building',(c.building.name||'unnamed')+' ('+c.building.osm+' '+c.building.id+')');
    if(cj){
      r+=bimPropText('CityJSON',cj.type+' '+cj.id+(cj.geomType?', '+cj.geomType:''));
      if(cj.parent)r+=bimPropText('Part Of',(cj.parentAttributes&&cj.parentAttributes.name?cj.parentAttributes.name+' ':'')+'('+cj.parent+')');
      r+=bimPropText('File',cj.file+(cj.crs?', '+cj.crs:'')+(cj.placed==='centred'?', placed by its centre':''));
      var k,n=0;
      for(k in cj.attributes)if(cj.attributes.hasOwnProperty(k)&&n<40&&k!=='lodMethod'){n++;r+=bimPropText(k,cj.attributes[k]===null?'':String(cj.attributes[k]));}
    }
    return r;
  }
"""
rep("""  function bimCtxPropsHtml(o){""", UI + """  function bimCtxPropsHtml(o){""")
rep("""    if(o.context)h+=bimCtxPropsHtml(o);                 /* __acad3dV133 */""",
    """    if(bimLodOf(o))h+=bimPropGroup('LOD',bimLodHtml(o));   /* __acad3dV139 */
    if(o.context)h+=bimCtxPropsHtml(o);                 /* __acad3dV133 */""")
rep("""      if(c.standY)r+=bimPropText('Stands at',bimDispNum(c.standY,2)+' m: the lowest ground under it');   /* __acad3dV137 */""",
    """      if(c.standY)r+=bimPropText('Stands at',bimDispNum(c.standY,2)+' m: the lowest ground under '+(c.standFp?'its building':'it'));   /* __acad3dV137 */
      if(c.minHeight)r+=bimPropText('Base',bimDispNum(c.minHeight,2)+' m up, '+(c.minFrom==='levels'?'its min level at '+BIM_CTX_LEVEL_H+' m each':'from its min_height tag'));   /* __acad3dV139 */""")
rep("""    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propctxact="get">Get Context</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="remove">Remove Context</button>');""",
    """    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propctxact="get">Get Context</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="remove">Remove Context</button>');
    r+=bimPropRow('LOD','<button type="button" class="a3d-pedit" data-propctxact="lodcheck" title="Every building\\'s LOD, and whether it is a valid solid">Check LODs</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="cjout" title="The buildings as CityJSON 2.0, in the site\\'s UTM zone">Export CityJSON</button> '+
      '<button type="button" class="a3d-pedit" data-propctxact="cjin">Import CityJSON</button>');   /* __acad3dV139 */""")
rep("""    if(last)r+=bimPropText('Last Fetch',last.date+': '+bimCtxCountsText(last.counts)+(last.errors&&last.errors.length?'; '+last.errors.join('; '):''));""",
    """    if(last)r+=bimPropText('Last Fetch',last.date+': '+bimCtxCountsText(last.counts)+(last.parts?' ('+last.parts+' building part'+(last.parts===1?'':'s')+', LOD1.3)':'')+   /* __acad3dV139 */
      (last.errors&&last.errors.length?'; '+last.errors.join('; '):''));""")
rep("""    if(a==='remove'){bimCtxRemove();return true;}
    return false;""", """    if(a==='remove'){bimCtxRemove();return true;}
    if(a==='lodcheck'){bimLodCheck();return true;}       /* __acad3dV139 */
    if(a==='cjout'){bimCityJsonExport();return true;}
    if(a==='cjin'){bimCityJsonPick();return true;}
    return false;""")
rep("""    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],""",
    """    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],
    /* __acad3dV139: LOD and CityJSON */
    ['LODCHECK',['CHECKSOLIDS','VALIDATESOLIDS','VAL3DITY'],'lodcheck','Check every building: its LOD, and whether it is a valid solid (closed, outward, flat faces, one piece)'],
    ['CITYJSONOUT',['EXPORTCITYJSON','CITYJSON'],'cityjsonout','Export the buildings as CityJSON 2.0, in the site\\'s UTM zone'],
    ['CITYJSONIN',['IMPORTCITYJSON'],'cityjsonin','Import a CityJSON file\\'s buildings, placed by their UTM coordinates'],""")
rep("""    contextremove:function(){bimCtxRemove();},""", """    contextremove:function(){bimCtxRemove();},
    lodcheck:function(){bimLodCheck();},              /* __acad3dV139 */
    cityjsonout:function(){bimCityJsonExport();},
    cityjsonin:function(){bimCityJsonPick();},""")
rep("""    CONTEXTREMOVE:'delete clear neighbours context',""", """    CONTEXTREMOVE:'delete clear neighbours context',
    LODCHECK:'lod level of detail validate valid solid closed watertight val3dity buildings check citygml',   /* __acad3dV139 */
    CITYJSONOUT:'cityjson citygml 3d city model export buildings lod utm 3dbag',
    CITYJSONIN:'cityjson citygml 3d city model import buildings lod 3dbag',""")
rep(""".a3d-svrow .a3d-pstatic{white-space:normal}""", """.a3d-svrow .a3d-pstatic{white-space:normal}
.a3d-lodtag{display:inline-block;padding:0 5px;border-radius:3px;background:#3a4656;color:#e8eef5;font-weight:700;font-size:11px}""")
rep("""  window.__a3dCtxHeight=function(tags){return bimOsmHeight(tags);};""", """  window.__a3dCtxHeight=function(tags){return bimOsmHeight(tags);};
  /* __acad3dV139: LOD, solids, UTM, CityJSON */
  window.__a3dCtxPartRange=function(tags){return bimOsmPartRange(tags);};
  window.__a3dLodOf=function(id){var o=objById(id);return o?bimLodOf(o):null;};
  window.__a3dSolidCheck=function(id){var o=objById(id);return o?bimObjSolidCheck(o):null;};
  window.__a3dSolidCheckMesh=function(m,surface){return bimSolidCheck(m,{surface:!!surface});};
  window.__a3dLodCheck=function(){return bimLodCheck();};
  window.__a3dUtm=function(lon,lat,zone,south){return bimUtmFwd(lon,lat,zone||bimUtmZone(lon),!!south);};
  window.__a3dUtmInv=function(E,N,zone,south){return bimUtmInv(E,N,zone,!!south);};
  window.__a3dCityJson=function(){return bimCityJsonDoc();};
  window.__a3dCityJsonExport=function(){var d=bimCityJsonExport();return d&&d.error?d:{ok:true};};
  window.__a3dCityJsonImport=function(text,name){return bimCityJsonImportText(text,name);};
  window.__a3dImportFileText=function(text,name){bimHandleImportFile(new File([text],name));return true;};
  window.__acad3dV139='buildingparts,lod13,lodlabels,lodgroup,solidcheck,lodcheck,utm,cityjsonout,cityjsonin,cityjsonfile,cityjsoncommands';""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
