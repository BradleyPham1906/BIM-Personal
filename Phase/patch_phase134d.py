"""patch_phase134d.py -- V134d: the site context tries Overpass's public mirrors.

The owner: "i cant get any context". The terrain came; overpass-api.de "could not be reached". The
main Overpass server turns some requests away (busy, or a client it cannot identify -- a page opened
as a file sends no Referer), and its refusal carries no CORS header, so the browser reports only a
network failure. CONTEXT now asks with a plain GET (the simplest request a browser can make) and,
when the server it is set to fails, tries Overpass's other public instances in turn; only when all
fail does it say so, naming each."""
NAME = 'patch_phase134d.py'
BASE = '93989dbdb03290f3c6a2836060cc659f787e90082677db2cb24c5ccdd708e190'
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


rep("""    var pOsm=q?fetch(st.overpass,{method:'POST',body:'data='+encodeURIComponent(q),headers:{'Content-Type':'application/x-www-form-urlencoded'}})
      .then(function(r){
        if(!r.ok)throw {http:r.status};
        return r.text();
      }).then(function(tx){
        var js;
        try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
        if(!js||!js.elements)throw {bad:true};
        return {ok:true,js:js};
      }).then(null,function(e){return {ok:false,err:e};}):Promise.resolve(null);""",
    """    var pOsm=q?bimCtxOverpass(q,st.overpass):Promise.resolve(null);   /* __acad3dV134d */""")
rep("""  function bimCtxApply(a,st,osm,ter){""", """  /* __acad3dV134d: Overpass's public instances, the one set first, each asked with a plain GET until
     one answers; every failure kept, to be named if none does */
  var BIM_OVERPASS_MIRRORS=['https://overpass-api.de/api/interpreter','https://overpass.private.coffee/api/interpreter',
    'https://maps.mail.ru/osm/tools/overpass/api/interpreter','https://overpass.kumi.systems/api/interpreter'];
  function bimCtxOverpass(q,first){
    var list=[first],tried=[];
    BIM_OVERPASS_MIRRORS.forEach(function(u){if(list.indexOf(u)<0)list.push(u);});
    function one(i){
      if(i>=list.length)return Promise.resolve({ok:false,msgs:tried});
      var u=list[i];
      return fetch(u+(u.indexOf('?')<0?'?':'&')+'data='+encodeURIComponent(q)).then(function(r){
        if(!r.ok)throw {http:r.status};
        return r.text();
      }).then(function(tx){
        var js;
        try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
        if(!js||!js.elements)throw {bad:true};
        return {ok:true,js:js,server:u,msgs:tried};
      },function(e){throw e;}).then(null,function(e){
        tried.push(bimCtxErr(bimMapHost(u),e));
        return one(i+1);
      });
    }
    return one(0);
  }
  function bimCtxApply(a,st,osm,ter){""")
rep("""      else bad.push(bimCtxErr(bimMapHost(st.overpass),osm.err));""",
    """      else bad=bad.concat(osm.msgs&&osm.msgs.length?osm.msgs:[bimCtxErr(bimMapHost(st.overpass),osm.err)]);   /* __acad3dV134d: each server tried */""")
rep("""      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc};""",
    """      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc,server:osm&&osm.ok?bimMapHost(osm.server):null};""")
rep("""  window.__acad3dV134='""", """  window.__acad3dV134d='overpassmirrors,overpassget';
  window.__a3dOverpassMirrors=function(){return BIM_OVERPASS_MIRRORS.slice();};
  window.__acad3dV134='""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
