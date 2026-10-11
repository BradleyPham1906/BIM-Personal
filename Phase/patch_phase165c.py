"""patch_phase165c.py -- V165: land and water in Analyze site, the rows, the findings.

  Analyze site   a step of its own, Ground and water, beside the context and the climate: the tiles
                 every 5 m for 150 m around the site (AWS Terrain Tiles) and FEMA's flood zones for US
                 sites; what fails is named and the rest stands
  the rows       contours, slope and aspect in Landform; water flow, ponds and flood zones in Water
  findings       the site's slope (Horn's method on the fine ground), its drainage (where it drains,
                 what drains onto it, the ponds), FEMA's zone at the site
  ANALYZESITE    says the new analyses; found by their words
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'bb1a51d422a44424f44ebe920559fd9fedc3f28069bb8f35aee0a1b689f866aa'   # after patch_phase165b.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimDgFloodRun(S){' in txt, 'run patch_phase165b.py first'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- Analyze site: the ground and its water, beside the context and the climate ----
rep("var BIM_SITERUN_STEPS=[['place','The site'],['context','Context'],['climate','Climate and time zone'],",
    "var BIM_SITERUN_STEPS=[['place','The site'],['context','Context'],['land','Ground and water'],['climate','Climate and time zone'],")
rep("      var pc=bimSiteOne('context',bimCtxFetch(),function(r){\n",
    "      /* __acad3dV165: the ground every 5 m and FEMA's zones, from AWS and FEMA: beside the context, not after it */\n"
    "      bimSiteStep('land','busy','The ground every '+BIM_LAND_CELL+' m for '+BIM_LAND_HALF+' m around, and the flood zones ...');\n"
    "      var pl=bimSiteOne('land',bimLandFetch(),function(r){\n"
    "        var got=[];\n"
    "        if(r.dem)got.push('the ground every '+r.dem.cell+' m for '+BIM_LAND_HALF+' m around');\n"
    "        if(r.flood&&r.flood.outside)got.push('FEMA maps US sites only');\n"
    "        else if(r.flood&&r.flood.features)got.push(r.flood.features.length?bimSaN(r.flood.features.length,'flood zone')+' from FEMA':'no flood zone mapped within '+BIM_LAND_HALF+' m');\n"
    "        return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];\n"
    "      });\n"
    "      var pc=bimSiteOne('context',bimCtxFetch(),function(r){\n")
rep("      return Promise.all([pc,pk]).then(function(){\n",
    "      return Promise.all([pc,pk,pl]).then(function(){\n")

# ---- the rows: land in Landform, water in Water ----
rep("dgnoise:'risk'};   /* __acad3dV164: the analyses in the model */\n",
    "dgnoise:'risk'};   /* __acad3dV164: the analyses in the model */\n"
    "  /* __acad3dV165: land and water */\n"
    "  BIM_ANZ_GROUP_OF.dgcontours='landform';BIM_ANZ_GROUP_OF.dgslope='landform';BIM_ANZ_GROUP_OF.dgaspect='landform';\n"
    "  BIM_ANZ_GROUP_OF.dgflow='water';BIM_ANZ_GROUP_OF.dgponds='water';BIM_ANZ_GROUP_OF.dgflood='water';\n")

# ---- the findings the ground and its water write ----
rep("    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto());   /* __acad3dV159: climate and risk; __acad3dV160: zoning; __acad3dV161: access and people */\n",
    "    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto()).concat(bimLandAuto());   /* __acad3dV159: climate and risk; __acad3dV160: zoning; __acad3dV161: access and people; __acad3dV165: land and water */\n")
FIND = r"""  /* __acad3dV165: what the ground and its water say about the site, as findings */
  function bimLandAuto(){
    var A=[],LD=A3D.site&&A3D.site.land,today=bimSaToday(),S,D;
    if(!LD)return A;
    try{S=bimDgSite();D=bimLandGround(S);}catch(eG){console.warn('[BIM] The ground could not be read',eG);return A;}
    if(D){
      var hn=bimLandHornOf(D),M=bimLandSiteMask(D,S),Y=bimLandHydroOf(D),n=0,sum=0,mx=0,flat=0,steep=0,k,a2=D.cell*D.cell;
      for(k=0;k<M.length;k++)if(M[k]&&isFinite(hn.slope[k])){n++;sum+=hn.slope[k];if(hn.slope[k]>mx)mx=hn.slope[k];if(hn.slope[k]<5)flat++;if(hn.slope[k]>=15)steep++;}
      if(n){
        var heavy=steep/n>0.25;
        A.push({auto:'landform.slope',cat:'landform',title:'Slope at the site',value:'Mean '+bimDispNum(sum/n,1)+'%, steepest '+bimDispNum(mx,1)+'%; '+bimLandPct(flat,n)+' under 5%'+(steep?', '+bimLandPct(steep,n)+' at 15% or more':''),
          cls:heavy?'constraint':(flat/n>=0.75?'opportunity':'neutral'),sev:heavy?2:1,source:D.srcShort+', Horn\'s method',date:today});
      }
      var U=bimLandUpstream(D,Y,M),nu=0,ex=bimLandExits(D,Y,M),pin=0,parts=[];
      for(k=0;k<U.length;k++)if(U[k]&&!M[k])nu++;
      Y.ponds.forEach(function(p){for(var i=0;i<p.cells.length;i++)if(M[p.cells[i]]){pin++;break;}});
      if(ex.length){var P0=bimLandP(D,ex[0].path[0]),P1=bimLandP(D,ex[0].path[ex[0].path.length-1]);parts.push('drains to the '+BIM_LAND_DIRNAME[BIM_LAND_DIRS[bimLandDir8(bimLandAz(P1[0]-P0[0],P1[2]-P0[2]))]]);}
      parts.push(nu?bimLandHa(nu*a2)+' around drains onto it':'nothing around drains onto it');
      if(Y.ponds.length)parts.push(bimSaN(Y.ponds.length,'pond')+' within '+BIM_LAND_HALF+' m'+(pin?', '+pin+' on the site':''));
      var v=parts.join('; ');
      A.push({auto:'water.drainage',cat:'water',title:'Drainage',value:v.charAt(0).toUpperCase()+v.slice(1),cls:(nu*a2>=10000||pin)?'constraint':'neutral',sev:pin?2:1,source:D.srcShort+', Priority-Flood and D8',date:today});
    }
    var Z=bimLandFloodZones(S),F=Z.F;
    if(F&&F.features){
      var zc=Z.site?Z.site.zc:null,zn=Z.site?String(Z.site.p.FLD_ZONE||Z.site.p.fld_zone||''):'',bfe=Z.site?bimLandBfe(Z.site.p):null,
        near=BIM_LAND_ZORDER.filter(function(z){return Z.present[z]&&z!==zc;}).map(function(z){return BIM_LAND_ZONES[z].short;});
      A.push({auto:'water.fema',cat:'water',title:'Flood zone (FEMA)',
        value:(zc?'The site is in zone '+zn+', '+BIM_LAND_ZONES[zc].site+(bfe?'; base flood elevation '+bfe.text:''):'The site is outside FEMA\'s mapped flood zones')+(near.length?'; within '+BIM_LAND_HALF+' m: '+near.join(', '):''),
        cls:zc==='floodway'?'redflag':(zc?'constraint':'neutral'),sev:(zc==='floodway'||zc==='sfha'||zc==='coastal')?3:1,source:'FEMA National Flood Hazard Layer, '+F.fetched,date:today});
    }
    return A;
  }
"""
rep("  /* ---- Properties: what it is, how it was worked out, how it looks ---- */\n",
    FIND + "  /* ---- Properties: what it is, how it was worked out, how it looks ---- */\n")

# ---- ANALYZESITE says them, and is found by their words ----
rep("draw each analysis in the model -- compass, sun paths, shadows, winds, views, noise -- on Layers, Site analysis; one undo step'],   /* __acad3dV164 */\n",
    "draw each analysis in the model -- compass, sun paths, shadows, winds, views, noise, contours, slope, aspect, water flow, ponds, flood zones -- on Layers, Site analysis; one undo step'],   /* __acad3dV164; __acad3dV165 */\n")
rep("climate context fill findings',   /* __acad3dV164 */\n",
    "climate context fill findings contours slope aspect terrain ground drainage flow catchment watershed ponds flood floodplain fema',   /* __acad3dV164; __acad3dV165 */\n")

# ---- the hooks the tests read ----
rep("  window.__acad3dV164='",
    "  /* __acad3dV165: land and water, for the tests */\n"
    "  window.__a3dLandFetch=function(){return bimLandFetch();};\n"
    "  window.__a3dLandDem=function(){var D=bimLandGround(bimDgSite()),H=[],k;if(!D)return null;for(k=0;k<D.H.length;k++)H.push(D.ok[k]?D.H[k]:null);\n"
    "    return {x0:D.x0,z0:D.z0,cell:D.cell,nx:D.nx,nz:D.nz,H:H,from:D.from,datum:D.datum,src:D.src};};\n"
    "  window.__a3dLandHorn=function(){var D=bimLandGround(bimDgSite()),h,s=[],a=[],k;if(!D)return null;h=bimLandHornOf(D);\n"
    "    for(k=0;k<D.H.length;k++){s.push(isFinite(h.slope[k])?h.slope[k]:null);a.push(isFinite(h.aspect[k])?h.aspect[k]:null);}return {slope:s,aspect:a};};\n"
    "  window.__a3dLandHydro=function(){var S=bimDgSite(),D=bimLandGround(S),Y,M;if(!D)return null;Y=bimLandHydroOf(D);M=bimLandSiteMask(D,S);\n"
    "    function A(v){return Array.prototype.slice.call(v);}\n"
    "    return {F:A(Y.F),down:A(Y.down),acc:A(Y.acc),order:A(Y.order),lab:A(Y.lab),stream:A(Y.stream),site:A(M),upstream:A(bimLandUpstream(D,Y,M)),exits:bimLandExits(D,Y,M),\n"
    "      ponds:Y.ponds.map(function(p){return {cells:p.cells.slice(),volume:p.volume,depth:p.depth,deep:p.deep,level:p.level,area:p.area};}),pondsAll:Y.pondsAll,\n"
    "      links:bimLandLinks(D,Y).map(function(l){return {from:l.from,to:l.to,order:l.order,outlet:l.outlet,n:l.nodes.length};})};};\n"
    "  window.__a3dLandMs=function(V,nx,nz,lev,pad){return bimLandMs(V,nx,nz,lev,pad);};\n"
    "  window.__a3dLandGet=function(){var L=A3D.site&&A3D.site.land;return L?JSON.parse(JSON.stringify(L)):null;};\n"
    "  window.__a3dLandSet=function(v){A3D.site=A3D.site||{};if(v===null)delete A3D.site.land;else A3D.site.land=JSON.parse(JSON.stringify(v));A3D_LAND.key=null;A3D_LAND.D=null;return true;};\n"
    "  window.__a3dLandZoneOf=function(p){return bimLandZoneOf(p||{});};\n"
    "  window.__a3dLandBfe=function(p){return bimLandBfe(p||{});};\n"
    "  window.__a3dLandUS=function(lat,lon){return bimLandUS({lat:lat,lon:lon});};\n"
    "  window.__a3dLandWarm=function(d8,lat){return bimLandWarm(d8,lat);};\n"
    "  window.__acad3dV165='landgrid,landfetch,ownsurface,contextfallback,horn,marchingsquares,contours,hypsometric,slopeclasses,aspectwarmth,priorityflood,d8,strahler,catchments,divides,'+\n"
    "    'upstream,exits,ponds,fema,floodzones,bfe,sitezone,bandrings,bandgroups,bandpick,lines,coverhidden,legendcompact,landstep,landfindings';\n"
    "  window.__acad3dV164='")

rep("  var BIM_APP_VERSION={v:'V164',date:'2026-10-11'};   /* __acad3dV162; __acad3dV163; __acad3dV164 */\n",
    "  var BIM_APP_VERSION={v:'V165',date:'2026-10-11'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165 */\n")

assert all(ord(ch) < 128 for ch in FIND), 'non-ASCII in the findings'
out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
