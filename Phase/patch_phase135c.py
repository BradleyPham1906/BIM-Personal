"""patch_phase135c.py -- V135: hooks for the suite, and the marker."""
NAME = 'patch_phase135c.py'
BASE = '404c18f41f7f7f7591fa5155be5dc42751a9c10322f323926d6e3cc8e5f4586c'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""  window.__acad3dV134d='overpassmirrors,overpassget';""", """  /* __acad3dV135: find open data */
  window.__a3dFindPortals=function(){return JSON.parse(JSON.stringify(BIM_DATA_PORTALS));};
  window.__a3dFindPortal=function(h){if(h!==undefined)bimFindSetPortal(h);var P=bimFindCurrent();return P?JSON.parse(JSON.stringify(P)):null;};
  window.__a3dFindGuess=function(){return bimFindGuess();};
  window.__a3dFindReset=function(){A3D_FIND.portal='';A3D_FIND.res=[];A3D_FIND.next=0;A3D_FIND.err='';A3D_FIND.said='';A3D_FIND.pick=null;A3D_FIND.groups={};A3D_FIND.busy=false;A3D_FIND.q='';A3D_FIND.near=true;return true;};
  window.__a3dFindHubUrl=function(q,o){return bimHubSearchUrl(q,o||{});};
  window.__a3dFindSocrataUrl=function(d,q,off){return bimSocrataSearchUrl(d,q,off||0);};
  window.__a3dFindSearch=function(q,more){return Promise.resolve(bimFindSearch(q,more));};
  window.__a3dFindState=function(){return JSON.parse(JSON.stringify({portal:A3D_FIND.portal,q:A3D_FIND.q,near:A3D_FIND.near,busy:A3D_FIND.busy,res:A3D_FIND.res,
    next:A3D_FIND.next,total:A3D_FIND.total,err:A3D_FIND.err,said:A3D_FIND.said,pick:A3D_FIND.pick,groups:A3D_FIND.groups}));};
  window.__a3dFindNear=function(v){A3D_FIND.near=!!v;return A3D_FIND.near;};
  window.__a3dFindAdd=function(ix,ly){return Promise.resolve(bimFindAdd(ix,ly)).then(function(r){
    var L=bimDataList(),id=typeof r==='string'?r:null;return Promise.resolve(id?A3D_DATA.pending[id]:null).then(function(f){return {id:id,result:r&&typeof r==='object'?r:null,fetch:f||null,layers:L.length};});});};
  window.__a3dFindCommand=function(){return bimFindCommand();};
  window.__a3dSetSiteAddress=function(a){if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};A3D.site.address=String(a||'');return true;};
  window.__acad3dV135='portallist,portalguess,portalremembered,hubsearch,hubgroups,hubbbox,socratasearch,socrataspatial,socratabox,'+
    'addfeaturelayer,addservicelayers,addgeojsonitem,addsocrata,more,failuresnamed,findcredit,findpanel,findcommand';
  window.__acad3dV134d='overpassmirrors,overpassget';""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
