"""patch_phase140b.py -- V140 (LOD-B): the roof in Properties; hooks; the marker."""
NAME = 'patch_phase140b.py'
BASE = '87a3c190ff1b1af95d16879136dafde7da1f4181620f25f62a3c0348dd8c69e1'
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


rep("""    if(c&&c.building)r+=bimPropText('Building',(c.building.name||'unnamed')+' ('+c.building.osm+' '+c.building.id+')');""",
    """    if(c&&c.building)r+=bimPropText('Building',(c.building.name||'unnamed')+' ('+c.building.osm+' '+c.building.id+')');
    if(c&&c.roof)r+='<div class="a3d-prow" data-lodrow="roof"><div class="a3d-plabel">Roof</div><div class="a3d-pval"><span class="a3d-pstatic">'+   /* __acad3dV140 */
      bimEsc(c.roof.shape+(c.roof.shape==='flat'?'':', '+bimDispNum(c.roof.height,2)+' m, '+c.roof.faces+' plane'+(c.roof.faces===1?'':'s'))+', eaves at '+bimDispNum((c.minHeight||0)+c.roof.eave,2)+' m')+'</span></div></div>';
    else if(c&&c.roofSkipped)r+='<div class="a3d-prow a3d-svrow" data-lodrow="roof"><div class="a3d-plabel">Roof</div><div class="a3d-pval"><span class="a3d-svck a3d-svck-warn">!</span> '+
      '<span class="a3d-pstatic">'+bimEsc('roof:shape='+c.roofSkipped.shape+' not built: '+c.roofSkipped.why)+'</span></div></div>';""")
rep("""    if(last)r+=bimPropText('Last Fetch',last.date+': '+bimCtxCountsText(last.counts)+(last.parts?' ('+last.parts+' building part'+(last.parts===1?'':'s')+', LOD1.3)':'')+   /* __acad3dV139 */""",
    """    if(last)r+=bimPropText('Last Fetch',last.date+': '+bimCtxCountsText(last.counts)+(last.parts?' ('+last.parts+' building part'+(last.parts===1?'':'s')+', LOD1.3)':'')+   /* __acad3dV139 */
      (last.roofs?' ('+last.roofs+' LOD2 roof'+(last.roofs===1?'':'s')+')':'')+   /* __acad3dV140 */""")
rep("""  window.__acad3dV139='""", """  /* __acad3dV140: LOD2 roofs */
  window.__a3dOsmRoof=function(fp,tags,base,h,from){var r=bimOsmRoof(sketchCCW(fp),tags,base||0,h,from||'height');return r?JSON.parse(JSON.stringify(r)):null;};
  window.__a3dRoofDir=function(s){return bimRoofDir(s);};
  window.__acad3dV140='roofshapes,roofgabled,roofhipped,roofpyramidal,roofskillion,roofhalfhipped,roofgambrel,roofmansard,roofflat,roofheights,roofdirection,lod20,roofrow,roofcityjson';
  window.__acad3dV139='""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
