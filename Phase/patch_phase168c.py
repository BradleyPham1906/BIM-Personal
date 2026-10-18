#!/usr/bin/env python3
"""V168c: land -- the findings, the rows, a council layer's colours, the hooks and the version.

- Four findings: the land use mix (Location), density and form (Location), 3-30-300 (Ecology), the
  zoning around (Legal); each names its standards (V167) and works out again on a change.
- The four analyses' rows sit in their categories: land use and the figure-ground in Location, green
  and trees in Ecology, the zoning around in Legal.
- Analyze site reads each ArcGIS data layer's own colours once (its description, ?f=json): what its
  drawing info gives, kept with the layer; a failure is named and the districts drawn in the app's.
- Hooks for the suite; V168.

Run from the repository root: python3 Phase/patch_phase168c.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '65c7f7e4be08c10a3b0052b4935ba0be52a8a72a24ede2bf038af12df9bd639b'   # after patch_phase168b.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


AUTO = r'''  /* __acad3dV168: what the land says about the site, as findings */
  function bimLdAuto(){
    var A=[],ctx=A3D.site&&A3D.site.context&&A3D.site.context.last,osm='OpenStreetMap (ODbL), via Overpass',S,Ar,B,dt,ws;
    if(!ctx)return A;
    dt=ctx.date||bimSaToday();
    try{S=bimDgSite();Ar=bimLdAreas();B=bimLdBuildings();ws=bimStdSay('app.land','window');}catch(eL){console.warn('[BIM] The land could not be read',eL);return A;}
    try{
      if(Ar.some(function(a){return a.cls;})||B.some(function(b){return b.cls;})){
        var MX=bimLdMix(S,B,Ar),pt=MX.sh.slice().sort(function(p,q){return q.n-p.n;}).map(function(x){return bimLdFam(x.c).short.toLowerCase()+' '+bimLdPct(x.p);}),rest=MX.none+MX.un;
        A.push({auto:'location.landuse',cat:'location',title:'Land use mix',
          value:MX.n?'In the '+ws+' square around the site, by area: '+pt.join(', ')+'; the mix '+(MX.ix===null?'not worked out':bimDispNum(MX.ix,2))+' (Shannon\'s entropy over '+bimSaN(MX.N,'LBCS family','LBCS families')+': 1 an even balance, 0 one use)'+
            (rest?'; '+bimLdPct(rest/MX.tot)+' of the square says no activity, or nothing, and is left out':'')+'.':'No land use is mapped in the '+ws+' square around the site.',
          cls:'neutral',sev:1,source:osm+'; LBCS\'s activities (APA)',date:dt});
      }
    }catch(e1){console.warn('[BIM] The land use finding could not be worked out',e1);}
    try{
      if(B.length){
        var W=bimLdWin(S),F=bimLdForm(B,W.x0,W.z0,W.x1,W.z1),gr=bimLdGrain(B,W);
        A.push({auto:'location.density',cat:'location',title:'Density and form',
          value:'In the '+ws+' square around the site: GSI '+bimDispNum(F.gsi,2)+' (the ground the buildings cover), FSI '+bimDispNum(F.fsi,2)+' (their floor area over the land)'+(F.osr===null?'':', OSR '+bimDispNum(F.osr,2))+
            (F.l===null?'':', '+bimDispNum(F.l,1)+' storeys on average')+'; '+bimSaN(gr.n,'building')+', '+bimDispNum(gr.ha,1)+' a hectare, '+bimLandHa(gr.mean)+' a footprint on average. Storeys from building:levels for '+gr.lev+' footprints, from the height at '+
            bimStdSay('app.context','storey')+' a storey for '+gr.hgt+'.'+(gr.yards?' '+bimSaN(gr.yards,'building')+' fetched before V168 with courtyards counted as built.':''),
          cls:'neutral',sev:1,source:osm+'; Spacematrix\'s measures',date:dt});
      }
    }catch(e2){console.warn('[BIM] The density finding could not be worked out',e2);}
    try{
      var Q=bimLd33300(S);
      if(Q.T.length||Q.Ar.some(bimLdWood)||Q.G.length){
        var met=[Q.ok3,Q.ok30,Q.ok300].filter(function(x){return x;}).length;
        A.push({auto:'ecology.33300',cat:'ecology',title:'3-30-300',
          value:met+' of 3 met. '+bimLd33300Rows(Q).map(function(r){return r[0]+': '+r[1];}).join('. ')+'. The trees seen by the site\'s sight lines, a window view\'s stand-in; the canopy from mapped trees and woods, not a land cover map.',
          cls:met===3?'opportunity':(met<=1?'constraint':'neutral'),sev:met<=1?2:1,source:osm+'; Browning et al. (2024)',date:dt});
      }
    }catch(e3){console.warn('[BIM] The 3-30-300 finding could not be worked out',e3);}
    try{
      var Z=bimLdZnAround(S);
      if(Z&&Z.order.length)A.push({auto:'legal.zoningaround',cat:'legal',title:'Zoning around',
        value:(Z.lot?'The site is in district '+Z.lot:'The site is in none of the layer\'s districts')+'; the zoned ground in the '+ws+' square: '+Z.order.slice(0,6).map(function(v){return v+' '+bimLdPct(Z.by[v]/Z.tot);}).join(', ')+
          (Z.order.length>6?', and '+(Z.order.length-6)+' more':'')+'.',cls:'neutral',sev:1,source:Z.src,date:bimSaToday()});
    }catch(e4){console.warn('[BIM] The zoning around could not be worked out',e4);}
    return A;
  }
'''

FETCH = r'''  /* __acad3dV168: an ArcGIS layer's own colours, read once from its description (?f=json) and kept with
     it; a failure named, its districts then drawn in the app's colours */
  function bimZnDrawingFetch(){
    var L=bimDataList().filter(function(x){return x&&x.kind==='arcgis'&&!x.drawing;}).slice(0,3);
    if(!L.length||typeof fetch!=='function')return Promise.resolve(0);
    return Promise.all(L.map(function(x){
      var u=String(x.url).replace(/\/?(\?.*)?$/,'')+'?f=json',done=false;
      return new Promise(function(res){
        function fail(e){
          if(done)return;
          done=true;clearTimeout(tm);
          console.warn('[BIM] The colours of '+x.name+' could not be read',e);
          a3dToast(x.name+': its own colours could not be read ('+bimCtxErr(bimMapHost(u),e)+'); its districts are drawn in the app\'s');
          res(0);
        }
        var tm=setTimeout(function(){fail({timeout:true});},15000);
        try{
          fetch(u).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
            if(done)return;
            var js;
            try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
            done=true;clearTimeout(tm);
            x.drawing=bimZnDrawing(js);
            res(1);
          }).then(null,fail);
        }catch(eF){fail(eF);}
      });
    })).then(function(r){return r.reduce(function(a,b){return a+b;},0);});
  }
'''

HOOKS = r'''
  window.__acad3dV168='lbcs,crosswalk,landuse,mix,entropy,figureground,spacematrix,cells,grain,courtyards,green,canopy,treesseen,greenwalk,33300,zoningaround,drawinginfo,textures,lids,findings,registry';
  window.__a3dLand=function(){
    try{
      var S=bimDgSite(),Ar=bimLdAreas(),B=bimLdBuildings(),W=bimLdWin(S),Q=bimLd33300(S),Z=bimLdZnAround(S);
      return JSON.parse(JSON.stringify({S:{c:S.c,y:S.y,r:S.r},W:W,reach:bimLdReach(),
        areas:Ar.map(function(a){return {key:a.key,cls:a.cls,area:a.area,name:a.name,outer:a.outer.length,holes:a.holes.length};}),
        buildings:B.map(function(b){return {id:b.id,name:b.name,cls:b.cls,s:b.s,from:b.from,area:b.area,ground:b.ground,whole:b.whole,holes:b.holes.length,yards:b.yards};}),
        mix:bimLdMix(S,B,Ar),form:bimLdForm(B,W.x0,W.z0,W.x1,W.z1),grain:bimLdGrain(B,W),seen:Q.seen,canopy:Q.can,
        greens:Q.G.map(function(g){return {key:g.key,name:g.name,area:g.area,big:g.big,walk:Q.walks[g.key]||null};}),best:Q.best?{key:Q.best.g.key,d:Q.best.d,p:Q.best.p}:null,
        ok:[Q.ok3,Q.ok30,Q.ok300],walkData:Q.walkData,
        zn:Z?{attr:Z.Z.attr,layer:Z.Z.L.name,lot:Z.lot,by:Z.by,order:Z.order,tot:Z.tot,col:Z.col,drawing:Z.Z.L.drawing||null}:null}));
    }catch(e){console.warn('[BIM] __a3dLand',e);return {error:String(e&&e.message||e)};}
  };
  window.__a3dLandClass=function(t,b){return bimLdClassOf(t||{},!!b);};
  window.__a3dLandCell=function(pts){var S=bimDgSite(),G=bimLdRaster(S,bimLdBuildings(),bimLdAreas());return pts.map(function(p){var i=Math.floor((p[0]-G.W.x0)/G.rc),j=Math.floor((p[1]-G.W.z0)/G.rc);return (i<0||j<0||i>=G.nx||j>=G.nx)?null:G.R[j*G.nx+i];});};
  window.__a3dLandForm=function(x0,z0,x1,z1){return JSON.parse(JSON.stringify(bimLdForm(bimLdBuildings(),x0,z0,x1,z1)));};
  window.__a3dZnDrawing=function(js){return bimZnDrawing(js);};
  window.__a3dZnStyleOf=function(D,p){return bimZnStyleOf(D,p||{});};
  window.__a3dZnDrawingFetch=function(){return bimZnDrawingFetch();};
  window.__a3dDgTexCss=function(k,i){return bimDgTexCss(k,i);};'''

rep("  /* __acad3dV166: what movement says about the site, as findings */", AUTO + "  /* __acad3dV166: what movement says about the site, as findings */")
rep("    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto()).concat(bimLandAuto()).concat(bimMvAuto());",
    "    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto()).concat(bimLandAuto()).concat(bimMvAuto()).concat(bimLdAuto());   /* __acad3dV168: land */")
rep("'water.fema':['fema.zones'],'location.built':['app.context']};",
    "'water.fema':['fema.zones'],'location.built':['app.context'],\n"
    "    'location.landuse':['lbcs.activity','app.land'],'location.density':['spacematrix','app.land','app.context'],'ecology.33300':['green.33300','app.land'],'legal.zoningaround':['app.land']};   /* __acad3dV168 */")
rep("'risk.air':'air','location.built':'context'};", "'risk.air':'air','location.built':'context','location.landuse':'context','location.density':'context','ecology.33300':'context'};")
rep("  BIM_ANZ_GROUP_OF.dgwalk='access';BIM_ANZ_GROUP_OF.dgvehicles='access';BIM_ANZ_GROUP_OF.dgneeds='people';",
    "  BIM_ANZ_GROUP_OF.dgwalk='access';BIM_ANZ_GROUP_OF.dgvehicles='access';BIM_ANZ_GROUP_OF.dgneeds='people';\n"
    "  /* __acad3dV168: land */\n"
    "  BIM_ANZ_GROUP_OF.dglanduse='location';BIM_ANZ_GROUP_OF.dgfigure='location';BIM_ANZ_GROUP_OF.dggreen='ecology';BIM_ANZ_GROUP_OF.dgzoning='legal';")
rep("      return Promise.all([pc,pk,pl]).then(function(){\n        bimSiteZoning();",
    "      return Promise.all([pc,pk,pl]).then(function(){return bimZnDrawingFetch();}).then(function(){   /* __acad3dV168: a council layer's own colours, once */\n        bimSiteZoning();")
rep("  /* the zoning, where a council's layer loaded in Data Layers covers the property */",
    FETCH + "  /* the zoning, where a council's layer loaded in Data Layers covers the property */")
rep("  var BIM_APP_VERSION={v:'V167',date:'2026-10-18'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167 */",
    "  var BIM_APP_VERSION={v:'V168',date:'2026-10-18'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168 */")
rep("dm2unread,classeswhole,groupclosed';", "dm2unread,classeswhole,groupclosed';" + HOOKS)

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
