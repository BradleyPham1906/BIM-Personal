"""patch_phase166c.py -- V166: movement in Analyze, the rows, the findings, the version.

  the rows       street hierarchy, cycling stress, transit, walk times and vehicle access in Access and
                 circulation; daily needs in People and place
  findings       Transit says PTAL now (or the floor, or why not); Cycling (the frontage streets' levels
                 and the low-stress reach) and Vehicle access (the driveways or a provisional entry, the
                 car parks within 400 m, the parking along the frontage) are new
  ANALYZESITE    says the new analyses; found by their words
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '45f3f72c46051fa85843a9e32e0de7c3a91b2b71ca5ada692e5a9db1bfa8b1f5'   # after patch_phase166b.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimDgVehiclesRun(S){' in txt, 'run patch_phase166b.py first'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- the rows: movement in Access and circulation, daily needs in People and place ----
rep("  BIM_ANZ_GROUP_OF.dgflow='water';BIM_ANZ_GROUP_OF.dgponds='water';BIM_ANZ_GROUP_OF.dgflood='water';\n",
    "  BIM_ANZ_GROUP_OF.dgflow='water';BIM_ANZ_GROUP_OF.dgponds='water';BIM_ANZ_GROUP_OF.dgflood='water';\n"
    "  /* __acad3dV166: movement */\n"
    "  BIM_ANZ_GROUP_OF.dgstreets='access';BIM_ANZ_GROUP_OF.dgcycling='access';BIM_ANZ_GROUP_OF.dgtransit='access';\n"
    "  BIM_ANZ_GROUP_OF.dgwalk='access';BIM_ANZ_GROUP_OF.dgvehicles='access';BIM_ANZ_GROUP_OF.dgneeds='people';\n")

# ---- Transit's finding says PTAL ----
rep("value:tv.join('; ')+'. Stops and lines from OpenStreetMap; how often they run needs the operator\\'s timetable (GTFS).',",
    "value:tv.join('; ')+'. '+bimMvPtalText(S),")   # __acad3dV166

FIND = r"""  /* __acad3dV166: transit's PTAL in words, for its finding; access data from before V166 says what it said */
  function bimMvPtalText(S){
    var mv=S&&S.mv&&Array.isArray(S.mv.w)?S.mv:null,P;
    if(!mv)return 'Stops and lines from OpenStreetMap; how often they run needs the operator\'s timetable (GTFS).';
    P=bimMvPtal(S,mv);
    if(!P.lines.length)return 'No bus stop within 8 minutes or station within 12: PTAL 0 by TfL\'s method.';
    if(!P.have)return 'How often the '+bimSaN(P.lines.length,'line')+' within reach run is not mapped in OpenStreetMap, so no PTAL (TfL\'s method needs each line\'s headway).';
    return 'PTAL '+(P.floor?'at least ':'')+P.band+' by TfL\'s method (index '+bimDispNum(P.ai,1)+')'+(P.floor?', from the '+P.have+' of '+P.lines.length+' lines whose headway OpenStreetMap maps':', from the headways OpenStreetMap maps')+'.';
  }
  /* __acad3dV166: what movement says about the site, as findings */
  function bimMvAuto(){
    var A=[],S=A3D.site&&A3D.site.access,mv=bimMvOf(),dt,src,i;
    if(!S||!mv)return A;
    dt=S.fetched;src=bimMvSrc(S);
    try{
      var ST=bimMvStress(mv),L=bimMvLotOf(S),R=bimMvReach(mv,ST,L),okL=0,allL=0,k,fr=[],worst=0,best=9;
      for(i=0;i<mv.w.length;i++){
        if(!(ST.W[i].lts>=1))continue;
        for(k=2;k<mv.w[i].length;k++){var l=bimMvSeg(mv,mv.w[i][k-1],mv.w[i][k]);allL+=l;if(R.ok[i]&&R.ok[i][k])okL+=l;}
      }
      (S.streets||[]).forEach(function(f){
        if(!f.n)return;
        var lv=0;
        for(i=0;i<mv.w.length;i++){var t=mv.t[mv.w[i][0]]||{};if(String(t.name||'')===f.n&&ST.W[i].lts>lv)lv=ST.W[i].lts;}
        if(lv){fr.push(f.n+' '+BIM_MV_LTS[lv].n+' ('+BIM_MV_LTS[lv].w+')');worst=Math.max(worst,lv);best=Math.min(best,lv);}
      });
      var nx=ST.X.filter(function(c){return !c.ctl&&c.lts>2&&bimAccLotDist(L,c.x,c.z)<=400;}).length,share=allL?okL/allL:0;
      A.push({auto:'access.cycling',cat:'access',title:'Cycling',
        value:(fr.length?'The lot fronts '+fr.join(', ')+'. ':'')+'From the lot, '+bimMvKm(okL)+' of the '+bimMvKm(allL)+' of streets and paths a bicycle may use within '+(mv.cut||mv.r)+' m are reached at low stress (LTS 2 or less, a detour of 25% at most)'+
          (nx?'; '+bimSaN(nx,'uncontrolled crossing')+' of a main street within 400 m '+(nx===1?'is':'are')+' stressful':'')+'. Levels by Mekuria, Furth and Nixon\'s criteria from the OpenStreetMap tags; speeds and lanes the class\'s where not mapped.',
        cls:(fr.length&&best<=2&&share>=0.3)?'opportunity':((fr.length&&best>=3)||share<0.1?'constraint':'neutral'),sev:1,source:src+'; level of traffic stress (MTI report 11-19)',date:dt});
    }catch(eC){console.warn('[BIM] The cycling finding could not be worked out',eC);}
    var dw=0,lowest=null,pref={s:0,l:1,c:2,a:3};
    for(i=0;i<mv.w.length;i++){
      var t2=mv.t[mv.w[i][0]]||{},near=Infinity,k2;
      if(t2.highway!=='service'||/^(parking_aisle|drive-through)$/.test(String(t2.service||'')))continue;
      for(k2=1;k2<mv.w[i].length;k2++)near=Math.min(near,bimAccLotDist(bimMvLotOf(S),mv.x[mv.w[i][k2]],mv.z[mv.w[i][k2]]));
      if(near<=3)dw++;
    }
    (S.streets||[]).forEach(function(f){if((f.c in pref)&&(!lowest||pref[f.c]<pref[lowest.c]))lowest=f;});
    var cps=mv.cp||[],cap=0,nc=0,parts=[];
    cps.forEach(function(c){if(c.cap){cap+=c.cap;nc++;}});
    if(dw)parts.push(bimSaN(dw,'driveway')+' or service road'+(dw===1?'':'s')+' into the lot');
    else if(lowest)parts.push('no driveway mapped into the lot: an entry from '+(lowest.n?lowest.n+' ('+bimAccStreetClass(lowest)+')':'the '+bimAccStreetClass(lowest))+', its lowest street, is marked provisional');
    else parts.push('no driveway mapped into the lot, and no street faces it');
    parts.push(cps.length?bimSaN(cps.length,'car park')+' within 400 m'+(nc?' ('+bimClimInt(cap)+' spaces mapped in '+nc+')':''):'no car park mapped within 400 m');
    if(mv.pe&&mv.pe.length)parts.push(bimSaN(mv.pe.length,'garage entrance')+' within 400 m');
    var fp=(S.streets||[]).filter(function(f){return f.n;}).map(function(f){
      var pk=null;for(i=0;i<mv.w.length;i++){var t3=mv.t[mv.w[i][0]]||{};if(String(t3.name||'')===f.n){var q=bimMvParking(t3);if(q.l!==null||q.r!==null){pk=q;break;}}}
      return pk?f.n+': '+bimMvParkText(pk):'';
    }).filter(function(x){return x;});
    if(fp.length)parts.push('parking along the frontage: '+fp.join('; '));
    var v=parts.join('; ');
    A.push({auto:'access.vehicles',cat:'access',title:'Vehicle access and parking',value:v.charAt(0).toUpperCase()+v.slice(1)+'.',
      cls:(!dw&&lowest&&lowest.c==='a')?'constraint':'neutral',sev:1,source:src,date:dt});
    return A;
  }
"""
rep("    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto()).concat(bimLandAuto());   /* __acad3dV159: climate and risk; __acad3dV160: zoning; __acad3dV161: access and people; __acad3dV165: land and water */\n",
    "    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto()).concat(bimLandAuto()).concat(bimMvAuto());   /* __acad3dV159: climate and risk; __acad3dV160: zoning; __acad3dV161: access and people; __acad3dV165: land and water; __acad3dV166: movement */\n")
rep("  /* __acad3dV165: what the ground and its water say about the site, as findings */\n",
    FIND + "  /* __acad3dV165: what the ground and its water say about the site, as findings */\n")

# ---- ANALYZESITE says them, and is found by their words ----
rep("contours, slope, aspect, water flow, ponds, flood zones -- on Layers, Site analysis; one undo step'],   /* __acad3dV164; __acad3dV165 */\n",
    "contours, slope, aspect, water flow, ponds, flood zones, street hierarchy, cycling stress, transit, walk times, daily needs, vehicle access -- on Layers, Site analysis; one undo step'],   /* __acad3dV164; __acad3dV165; __acad3dV166 */\n")
rep("climate context fill findings contours slope aspect terrain ground drainage flow catchment watershed ponds flood floodplain fema',   /* __acad3dV164; __acad3dV165 */\n",
    "climate context fill findings contours slope aspect terrain ground drainage flow catchment watershed ponds flood floodplain fema street hierarchy streets roads cycling bicycle bike stress lts transit bus rail ptal walk walking times daily needs vehicle access driveway entry parking car park',   /* __acad3dV164; __acad3dV165; __acad3dV166 */\n")

# ---- the hooks the tests read ----
rep("  window.__acad3dV165='",
    "  /* __acad3dV166: movement, for the tests */\n"
    "  window.__a3dMvGet=function(){var S=A3D.site&&A3D.site.access;return S&&S.mv?JSON.parse(JSON.stringify(S.mv)):null;};\n"
    "  window.__a3dMvSet=function(v){var S=A3D.site&&A3D.site.access;if(!S)return false;if(v===null)delete S.mv;else S.mv=JSON.parse(JSON.stringify(v));return true;};\n"
    "  window.__a3dMvLts=function(t){var r=bimMvLts(t||{});return {lts:r.lts,why:r.why,sp:r.sp,ln:r.ln,fac:r.fac,pk:r.pk};};\n"
    "  window.__a3dMvKmh=function(s){return bimMvKmhOf(s);};\n"
    "  window.__a3dMvRow=function(v){return bimMvRow(v);};\n"
    "  window.__a3dMvInterval=function(v){return bimMvInterval(v);};\n"
    "  window.__a3dMvParking=function(t){return bimMvParking(t||{});};\n"
    "  window.__a3dMvStress=function(){var mv=bimMvOf();if(!mv)return null;var ST=bimMvStress(mv);\n"
    "    return {W:ST.W.map(function(r){return r.lts;}),X:ST.X.map(function(c){return {n:c.n,x:c.x,z:c.z,lts:c.lts,ctl:c.ctl,minors:c.minors.slice(),main:c.main?String(c.main.t.name||c.main.t.highway):''};})};};\n"
    "  window.__a3dMvReach=function(){var S=A3D.site&&A3D.site.access,mv=bimMvOf();if(!mv)return null;var ST=bimMvStress(mv),R=bimMvReach(mv,ST,bimMvLotOf(S));\n"
    "    function f(D){return D.map(function(v){return isFinite(v)?Math.round(v*1000)/1000:null;});}\n"
    "    return {Da:f(R.Da),Dl:f(R.Dl),ok:R.ok,seeds:R.seeds};};\n"
    "  window.__a3dMvPtal=function(){var S=A3D.site&&A3D.site.access;if(!S)return null;return JSON.parse(JSON.stringify(bimMvPtal(S,bimMvOf())));};\n"
    "  window.__a3dMvPtalBand=function(ai){return bimMvPtalBand(ai);};\n"
    "  window.__acad3dV166='mvquery,mvdata,mvstreets,mvthin,mvbudget,crossings,doors,carparks,garages,intervals,routeways,paths,walklayeronrequest,'+\n"
    "    'hierarchy,lts2012,crossings2016,lowstressreach,ptal,catchments,routes,walkbands,needs,vehicleentry,provisionalentry,onstreetparking,maprgb,ptalfinding,cyclingfinding,vehiclesfinding';\n"
    "  window.__acad3dV165='")

rep("  var BIM_APP_VERSION={v:'V165',date:'2026-10-11'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165 */\n",
    "  var BIM_APP_VERSION={v:'V166',date:'2026-10-12'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166 */\n")

assert all(ord(ch) < 128 for ch in FIND), 'non-ASCII in the findings'
out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
