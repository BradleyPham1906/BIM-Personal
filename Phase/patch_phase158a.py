"""patch_phase158a.py -- V158: Site analysis SA1, the workspace and the standard.

The owner (V156): "do some research on how professionals do site analysis. i want to standardize the
whole process." The research (reference/research-site-analysis-process.md) gives one standard: six
stages (RIBA Stage 1 and the due-diligence order) and ten fixed categories (Lynch's natural and
cultural factors, McHarg's order, the due-diligence items). Every finding names its source, its date
and how sure it is, and is classed as a constraint, an opportunity, a red flag or a plain fact.

Here it becomes a workspace, a rail tab of its own (Site):
- the stages as a stepper, the one the project is at kept with it;
- Define: the boundary (the property line, V103/V134), the project type and the questions;
- Fill from the model: what the app already knows, as findings (location, context, the property,
  data layers, the terrain's relief and slope, water, the sun's day lengths, trees and green, roads
  by use, rail, airports, power, land use), each with its source and date, refilled in place;
- the ten categories, each with its findings, what to find at the desk and what to check on site;
- a finding: what, class and severity, confidence, source, date, a note, a photograph, and a pin on
  the plan, numbered as in the list.
All of it is saved with the project, in A3D.site.analysis, and every change is one undo step."""
NAME = 'patch_phase158a.py'
BASE = 'ecf72c2ad310634fc282b38b0311df305e3a72c304134263d203f210f6be394f'
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
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


# ---- CSS ----
rep(""".a3d-terrbands{margin:2px 0 8px;display:flex;flex-direction:column;gap:2px}""",
    """.a3d-terrbands{margin:2px 0 8px;display:flex;flex-direction:column;gap:2px}
/* __acad3dV158: the Site analysis tab */
#a3d-shell[data-tab="site"] .a3d-projhead{flex-shrink:0}
#a3d-shell[data-tab="site"] .a3d-sa-wrap{flex:1 1 auto;min-height:0;display:flex;flex-direction:column}
.a3d-sastages{display:flex;flex-wrap:wrap;gap:3px;margin:0 0 4px}
.a3d-sastage{flex:1 0 auto;min-width:34px;border:1px solid rgba(255,255,255,.14);border-radius:6px;background:transparent;color:#9aa3ad;font:inherit;font-size:11px;padding:3px 6px;min-height:26px;cursor:pointer;white-space:nowrap}
.a3d-sastage.done{color:#81c784;border-color:rgba(129,199,132,.35)}
.a3d-sastage.on{background:#2f6fd6;border-color:#2f6fd6;color:#fff}
.a3d-sastagecap{font-size:11.5px;color:#aab4bf;margin:0 2px 10px;line-height:1.4}
.a3d-sasec{border-top:1px solid rgba(255,255,255,.08);padding:8px 2px 10px}
.a3d-sasechd{font-size:11px;font-weight:600;color:#8a96a3;margin:0 0 6px}
.a3d-sarow{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-size:12px}
.a3d-sarow>label,.a3d-sarow>.a3d-salab{flex:0 0 74px;color:#8a96a3;font-size:11.5px}
.a3d-sarow>select,.a3d-sarow>input,.a3d-sarow>textarea,.a3d-sarow>.a3d-saval{flex:1 1 auto;min-width:0}
.a3d-sa select,.a3d-sa input[type=text],.a3d-sa input[type=date],.a3d-sa textarea{box-sizing:border-box;background:#1f2327;border:1px solid #3a4048;border-radius:6px;color:#e6eaef;padding:3px 7px;min-height:26px;font:inherit;font-size:12px}
.a3d-sa textarea{resize:vertical;min-height:44px;line-height:1.35}
.a3d-sa select:focus,.a3d-sa input:focus,.a3d-sa textarea:focus{border-color:#4ea1ff;outline:0}
.a3d-saval{color:#d5dae0;font-size:12px;line-height:1.35}
.a3d-saflags{margin:0 0 6px;padding:7px 9px;border-radius:7px;background:rgba(229,72,77,.12);border:1px solid rgba(229,72,77,.35)}
.a3d-saflags .a3d-sasechd{color:#ef9a9a;margin-bottom:4px}
.a3d-saflag{font-size:12px;color:#f3c4c4;margin:2px 0}
.a3d-sacat .a3d-anzbody{padding-left:20px}
.a3d-saq{color:#8a96a3;font-size:11.5px;margin:0 0 8px;line-height:1.4}
.a3d-safind{border-left:3px solid #8b949e;padding:4px 0 6px 8px;margin:0 0 6px}
.a3d-safind.c-constraint{border-left-color:#f5a524}.a3d-safind.c-opportunity{border-left-color:#30a46c}.a3d-safind.c-redflag{border-left-color:#e5484d}
.a3d-safhd{display:flex;align-items:baseline;gap:6px;font-size:12.5px}
.a3d-safno{color:#8a96a3;font-size:11px;flex:none}
.a3d-saftt{flex:1 1 auto;min-width:0;font-weight:500}
.a3d-safv{font-size:12px;color:#c9d1d9;margin:2px 0;line-height:1.4;white-space:pre-wrap}
.a3d-safm{font-size:10.5px;color:#8a96a3;line-height:1.4}
.a3d-safm b{font-weight:600}
.a3d-safm .k-constraint{color:#f5b54a}.a3d-safm .k-opportunity{color:#5cc48d}.a3d-safm .k-redflag{color:#ef8a8d}
.a3d-safph{display:block;max-width:100%;max-height:150px;border-radius:5px;margin:5px 0 2px}
.a3d-safed{margin:6px 0 2px;padding:7px 8px;border-radius:6px;background:rgba(255,255,255,.04)}
.a3d-sachk{display:flex;align-items:flex-start;gap:7px;font-size:12px;color:#c9d1d9;margin:0 0 4px;line-height:1.35;cursor:pointer}
.a3d-sachk input{margin:2px 0 0;flex:none}
.a3d-sachk.on span{color:#8a96a3;text-decoration:line-through}
.a3d-sachkhd{font-size:11px;color:#8a96a3;margin:8px 0 4px}
.a3d-saacts{display:flex;flex-wrap:wrap;gap:5px;margin:6px 0 0}
.a3d-sanote{font-size:11.5px;color:#8a96a3;margin:0 0 6px;line-height:1.4}
@media(pointer:coarse){
.a3d-sastage{min-height:36px;font-size:12.5px;padding:4px 10px}
.a3d-sa select,.a3d-sa input[type=text],.a3d-sa input[type=date],.a3d-sa textarea{min-height:36px;font-size:16px}
.a3d-sachk{font-size:13.5px;min-height:30px}
.a3d-sachk input{width:20px;height:20px}
}
body.light-theme .a3d-sastage{border-color:rgba(0,0,0,.15);color:#555}
body.light-theme .a3d-sastage.on{color:#fff}
body.light-theme .a3d-sastage.done{color:#2e7d32;border-color:rgba(46,125,50,.35)}
body.light-theme .a3d-sasec{border-top-color:rgba(0,0,0,.08)}
body.light-theme .a3d-sa select,body.light-theme .a3d-sa input[type=text],body.light-theme .a3d-sa input[type=date],body.light-theme .a3d-sa textarea{background:#fff;border-color:#c9ced4;color:#222}
body.light-theme .a3d-saval,body.light-theme .a3d-safv,body.light-theme .a3d-sachk{color:#333}
body.light-theme .a3d-sastagecap,body.light-theme .a3d-saq,body.light-theme .a3d-safm,body.light-theme .a3d-sanote,body.light-theme .a3d-sasechd,body.light-theme .a3d-sachkhd,body.light-theme .a3d-sarow>label,body.light-theme .a3d-sarow>.a3d-salab{color:#6b737c}
body.light-theme .a3d-saflags{background:rgba(229,72,77,.08)}
body.light-theme .a3d-saflag{color:#9b1c20}
body.light-theme .a3d-safed{background:rgba(0,0,0,.035)}""")

# ---- the rail: a Site tab, after Analyze ----
rep("""    analyze:'<path d="M2.5 15.5h13"/><path d="M4.5 13V9.5M8 13V6.5M11.5 13V8.5M15 13V4"/><path d="M3.5 7.5 7.5 4l3.5 2.5 4.5-4" stroke-dasharray="1.6 1.4"/>'
  };""",
    """    analyze:'<path d="M2.5 15.5h13"/><path d="M4.5 13V9.5M8 13V6.5M11.5 13V8.5M15 13V4"/><path d="M3.5 7.5 7.5 4l3.5 2.5 4.5-4" stroke-dasharray="1.6 1.4"/>',
    /* __acad3dV158: a pin on a site outline, the Site analysis tab */
    site:'<path d="M2.5 11.5 6 9.5l3.5 1.5 3-1.5 3 1.8v4.2l-3-1.8-3 1.5L6 13.7l-3.5 2z"/><path d="M9 8.6S6.4 6.2 6.4 4.4a2.6 2.6 0 0 1 5.2 0C11.6 6.2 9 8.6 9 8.6z"/>'
  };""")
rep("""      bimRailIcon('analyze')+'</button>'+""",
    """      bimRailIcon('analyze')+'</button>'+
      '<button type="button" class="a3d-railbtn" data-tab="site" data-short="Site" title="Site analysis" aria-label="Site analysis">'+   /* __acad3dV158 */
      bimRailIcon('site')+'</button>'+""")
rep("""    {sel:'.a3d-railbtn[data-tab="analyze"]',why:'Analyze tab: every analysis, what it shows now, run it or open its settings'},""",
    """    {sel:'.a3d-railbtn[data-tab="analyze"]',why:'Analyze tab: every analysis, what it shows now, run it or open its settings'},
    {sel:'.a3d-railbtn[data-tab="site"]',why:'Site analysis tab: the standard process, the ten categories and every finding'},   /* __acad3dV158 */""")

# ---- the tab's body ----
rep("""    if(shell.dataset.tab!=='analyze'){
      var astale=panel.querySelector('.a3d-analyze-wrap');
      if(astale){astale.parentNode.removeChild(astale);did=true;}
    }""",
    """    if(shell.dataset.tab!=='analyze'){
      var astale=panel.querySelector('.a3d-analyze-wrap');
      if(astale){astale.parentNode.removeChild(astale);did=true;}
    }
    if(shell.dataset.tab==='site'&&!panel.querySelector('.a3d-sa-wrap')){   /* __acad3dV158 */
      var sbox=document.createElement('div');
      sbox.className='a3d-tabbody a3d-sa-wrap';
      sbox.innerHTML=bimSaHtml();
      bimSaWire(sbox);
      panel.appendChild(sbox);
      did=true;
    }
    if(shell.dataset.tab!=='site'){
      var sstale=panel.querySelector('.a3d-sa-wrap');
      if(sstale){sstale.parentNode.removeChild(sstale);A3D_SA.edit=null;did=true;}
    }""")

# ---- refreshed with Properties, unless it is being typed in ----
rep("""    bimAnalyzeRefresh();   /* __acad3dV141 */""",
    """    bimAnalyzeRefresh();   /* __acad3dV141 */
    bimSaRefresh();        /* __acad3dV158 */""")

# ---- the pin tool ----
rep("""    }else if(sk.tool==='profileview'){   /* __acad3dV127 */""",
    """    }else if(sk.tool==='sapin'){   /* __acad3dV158: a finding placed on the plan */
      var saF=sk.fid;
      A3D.sk=null;
      bimSaPlace(saF,[gx,gz]);
    }else if(sk.tool==='profileview'){   /* __acad3dV127 */""")

# ---- the pins on the plan ----
rep("""    drawNotes(ctx,V,W,H);          // __acad3dV82: the annotation overlay, above the model""",
    """    drawNotes(ctx,V,W,H);          // __acad3dV82: the annotation overlay, above the model
    if(!capMode)drawSaPins(ctx,V,W,H);   /* __acad3dV158: the site analysis findings */""")

# ---- the commands ----
rep("""    ['CONTEXT',['SITECONTEXT','OSM'],'context','Get the buildings, roads, water, green, trees and terrain around the site, from OpenStreetMap and AWS Terrain Tiles'],""",
    """    ['CONTEXT',['SITECONTEXT','OSM'],'context','Get the buildings, roads, bridges, tunnels, railways, airports, power lines, land use, water, green, trees and terrain around the site, from OpenStreetMap and AWS Terrain Tiles'],   /* __acad3dV158: V157's kinds named */
    ['SITEANALYSIS',['SA','SITEAN','SITEPROCESS'],'siteanalysis','The Site analysis tab: the standard process, ten categories, findings with their sources, on the plan'],   /* __acad3dV158 */
    ['SAFILL',['SITEANALYSISFILL','SAFROMMODEL'],'safill','Fill the site analysis from what the model already knows: location, context, property, terrain, sun, access'],""")
rep("""    context:function(){bimCtxFetch();},                          /* __acad3dV133 */""",
    """    context:function(){bimCtxFetch();},                          /* __acad3dV133 */
    siteanalysis:function(){bimShellSetTab('site');},            /* __acad3dV158 */
    safill:function(){bimShellSetTab('site');bimSaFill();},""")

# ---- the engine and the panel ----
rep("""  function bimAnalyzeCommandTab(){bimShellSetTab('analyze');return true;}""",
    """  function bimAnalyzeCommandTab(){bimShellSetTab('analyze');return true;}
  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================
     The standard is reference/research-site-analysis-process.md: six stages, ten fixed categories,
     and findings that each name a source, a date and how sure they are, classed as a constraint, an
     opportunity, a red flag or a fact. Kept with the project in A3D.site.analysis. */
  var BIM_SA_STAGES=[
    ['Define','The site boundary, the project type and the questions the analysis must answer.'],
    ['Desktop','Each category filled from open data and the model, every value with its source and date.'],
    ['Visit','Walk the site with each category\\'s checklist; note and photograph what you see, pinned on the plan.'],
    ['Surveys','Where the visit leaves doubt, a survey: topographic, title (ALTA), ground, trees, environmental (Phase I).'],
    ['Analysis','Each finding classed as a constraint, an opportunity or a red flag, with its severity.'],
    ['Synthesis','Constraints and opportunities overlaid: the buildable area, the envelope and the yield.'],
    ['Report','The standard boards, every number credited.']];
  var BIM_SA_CATS=[
    {id:'location',n:'Location and context',q:'Where it is, what surrounds it, figure-ground, land use.',
      desk:['Place the site (latitude and longitude, or an address)','Get the surrounding context (CONTEXT)','Note the neighbourhood character and landmarks'],
      visit:['Photograph each approach and the views out','Check the neighbours against the context model','Note landmarks, edges and nodes']},
    {id:'legal',n:'Legal and regulatory',q:'Zoning, permitted uses, FAR, height, setbacks, coverage, parking, easements, ownership, heritage.',
      desk:['Draw or take the property line','Load the parcel and zoning layers (DATALAYERS)','Note FAR, height, setbacks, coverage and parking','Check easements, title and heritage listings'],
      visit:['Find the boundary markers','Note encroachments and access easements in use']},
    {id:'landform',n:'Landform',q:'Topography, slope, aspect, relief, geology, soils.',
      desk:['Get the terrain (CONTEXT or SURVEY)','Read slope and aspect (Analyze)','Look up soils and geology'],
      visit:['Check the slopes and levels at the boundaries','Note rock, fill and signs of instability']},
    {id:'water',n:'Water',q:'Drainage, flood zones, water bodies, runoff.',
      desk:['Load the flood zones (DATALAYERS)','Run the rain flow (RAINFLOW)','Note water bodies and streams'],
      visit:['Look for ponding, wet ground and outfalls','Note where water leaves the site']},
    {id:'climate',n:'Climate',q:'Temperature, rain, climate zone, sun path, shadows, wind, solar.',
      desk:['Set the site\\'s sun (Location)','Study the shadows (SUNSTUDY) and the sun hours','Get the climate and wind (SA2)'],
      visit:['Note the prevailing wind and exposed corners','Note overshadowing from neighbours']},
    {id:'ecology',n:'Ecology',q:'Vegetation, trees, habitat, protected areas.',
      desk:['Get the trees and green areas (CONTEXT)','Check protected areas and species'],
      visit:['Survey significant trees and their canopies','Note habitats and wildlife']},
    {id:'risk',n:'Environmental risk',q:'Seismic, contamination, air quality, noise, wildfire.',
      desk:['Check seismic history','Check past uses for contamination (Phase I)','Check air quality and noise sources'],
      visit:['Note smells, staining, tanks and dumping','Listen for traffic, rail and aircraft noise']},
    {id:'access',n:'Access and circulation',q:'Street hierarchy, street use, transit, walking and cycling, parking, entries.',
      desk:['Get the roads, rail and transit (CONTEXT)','Note the street hierarchy and possible entries','Check transit stops and walk times'],
      visit:['Check sight lines at the entries','Note how people arrive: on foot, by bike, by car, by transit','Note parking and servicing']},
    {id:'utilities',n:'Utilities',q:'Water, sewer, power, stormwater, telecoms.',
      desk:['Request the utility records','Note overhead lines and substations'],
      visit:['Find manholes, hydrants, poles and meters','Note where the connections would come from']},
    {id:'people',n:'People and place',q:'Demographics, amenities within a walk, history, views, landmarks, noise sources.',
      desk:['Note the land use around (CONTEXT)','Look up the census and the amenities within a walk','Read the site\\'s history'],
      visit:['Talk to neighbours and users','Note activity at different times of day']}];
  var BIM_SA_CLS=[['neutral','Fact'],['opportunity','Opportunity'],['constraint','Constraint'],['redflag','Red flag']];
  var BIM_SA_CONF=[['desktop','Desktop'],['site','Seen on site'],['surveyed','Surveyed']];
  var BIM_SA_SEV=[['1','Low'],['2','Medium'],['3','High']];
  var BIM_SA_TYPES=['','Residential','Commercial','Mixed use','Industrial','Institutional','Public realm and landscape','Infrastructure','Other'];
  var BIM_SA_COL={neutral:'#8b949e',opportunity:'#30a46c',constraint:'#f5a524',redflag:'#e5484d'};
  var BIM_SA_PHOTO_PX=960;
  var A3D_SA={edit:null,open:(function(){try{var v=JSON.parse(localStorage.getItem('acad3dSaOpen')||'{}');return v&&typeof v==='object'&&!Array.isArray(v)?v:{};}catch(eO){return {};}})()};
  function bimSaPair(L,k){var i;for(i=0;i<L.length;i++)if(L[i][0]===k)return L[i][1];return '';}
  function bimSaCat(id){var i;for(i=0;i<BIM_SA_CATS.length;i++)if(BIM_SA_CATS[i].id===id)return BIM_SA_CATS[i];return null;}
  function bimSaToday(){return new Date().toISOString().slice(0,10);}
  /* the record, made when first asked for; read-only callers get the same shape */
  function bimSa(){
    A3D.site=A3D.site||{};
    var s=A3D.site.analysis;
    if(!s||typeof s!=='object')s=A3D.site.analysis={};
    if(!(s.stage>=0&&s.stage<BIM_SA_STAGES.length))s.stage=0;
    if(typeof s.ptype!=='string')s.ptype='';
    if(typeof s.questions!=='string')s.questions='';
    if(!Array.isArray(s.findings))s.findings=[];
    if(!s.checks||typeof s.checks!=='object')s.checks={};
    if(!(s.seq>=0))s.seq=0;
    if(s.pins===undefined)s.pins=true;
    return s;
  }
  function bimSaFind(id){var F=bimSa().findings,i;for(i=0;i<F.length;i++)if(F[i].id===id)return F[i];return null;}
  /* "4.2": the category's number, then the finding's place in it */
  function bimSaNumber(f){
    var F=bimSa().findings,ci=-1,k=0,i;
    for(i=0;i<BIM_SA_CATS.length;i++)if(BIM_SA_CATS[i].id===f.cat)ci=i;
    for(i=0;i<F.length;i++){if(F[i].cat===f.cat)k++;if(F[i]===f)break;}
    return (ci+1)+'.'+k;
  }
  function bimSaOf(cat){return bimSa().findings.filter(function(f){return f.cat===cat;});}
  /* the highest confidence any of a category's findings has */
  function bimSaConfOf(cat){
    var F=bimSaOf(cat),best=-1,i,k;
    for(i=0;i<F.length;i++){for(k=0;k<BIM_SA_CONF.length;k++)if(BIM_SA_CONF[k][0]===F[i].conf&&k>best)best=k;}
    return best<0?'':BIM_SA_CONF[best][0];
  }
  function bimSaNew(cat,f){
    var s=bimSa();
    s.seq++;
    return {id:'saf'+s.seq,cat:cat,title:String(f.title||'Finding').slice(0,120),value:String(f.value||'').slice(0,2000),
      cls:bimSaPair(BIM_SA_CLS,f.cls)?f.cls:'neutral',sev:(f.sev>=1&&f.sev<=3)?+f.sev:1,conf:bimSaPair(BIM_SA_CONF,f.conf)?f.conf:'desktop',
      source:String(f.source||'').slice(0,200),date:/^\\d{4}-\\d{2}-\\d{2}$/.test(f.date||'')?f.date:bimSaToday(),note:String(f.note||'').slice(0,2000),
      at:null,photo:null,auto:f.auto||''};
  }
  function bimSaDone(){refreshProps();paint();saveSoon();bimSaRefresh(true);}
  /* ---- what the model already knows ---- */
  function bimSaN(n,one,many){return n+' '+(n===1?one:(many||one+'s'));}
  function bimSaSlope(tin){
    var T=tin.tris||[],out=tin.outside||{},i,a,b,c,P=tin.P,H=tin.H,area=0,sum=0,mx=0,steep=0;
    for(i=0;i<T.length;i++){
      if(out[i])continue;
      var v=T[i].v||T[i];a=v[0];b=v[1];c=v[2];
      if(!P[a]||!P[b]||!P[c])continue;
      var x1=P[b][0]-P[a][0],z1=P[b][1]-P[a][1],y1=H[b]-H[a],x2=P[c][0]-P[a][0],z2=P[c][1]-P[a][1],y2=H[c]-H[a];
      var nx=z1*y2-y1*z2,ny=x1*z2-z1*x2,nz=y1*x2-x1*y2,A=Math.abs(ny)/2;
      if(!(A>1e-9))continue;
      var g=Math.sqrt(nx*nx+nz*nz)/Math.abs(ny);
      area+=A;sum+=g*A;if(g>mx)mx=g;if(g>0.15)steep+=A;
    }
    return area>0?{mean:sum/area,max:mx,steepShare:steep/area,area:area}:null;
  }
  function bimSaDayLen(lat,lon,md){
    var r=bimSunCalc(lat,lon,0,new Date().getFullYear()+'-'+md,'12:00');
    if(!r)return null;
    if(r.polar==='day')return 'no sunset';
    if(r.polar==='night')return 'no sunrise';
    var m=Math.round(r.sunset-r.sunrise);
    return Math.floor(m/60)+' h '+bimPad2(m%60)+' min';
  }
  function bimSaAuto(){
    var A=[],today=bimSaToday(),st=bimSunSettings(),ctx=(A3D.site&&A3D.site.context&&A3D.site.context.last)||null,i,o,c;
    var cnt={},uses={},lu={},bh=[],nBr=0,nTu=0,ter=null,cterr=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;
      if(o.t==='terrain'&&o.survey&&!o.grading){if(c&&c.kind==='terrain')cterr=o;else if(!ter)ter=o;}
      if(!c)continue;
      cnt[c.kind]=(cnt[c.kind]||0)+(c.part==='hole'?0:1);
      if(c.kind==='buildings'&&c.height>0)bh.push(c.height);
      if(c.use)uses[c.use]=(uses[c.use]||0)+1;
      if(c.bridge)nBr++;if(c.tunnel)nTu++;
      if(c.kind==='landuse'&&c.tags&&c.tags.landuse)lu[c.tags.landuse]=(lu[c.tags.landuse]||0)+1;
    }
    ter=ter||cterr;
    var osm='OpenStreetMap (ODbL), via Overpass',od=ctx?ctx.date:today,rr=ctx?' within '+ctx.radius+' m':'';
    if(bimSunNum(st.lat)&&bimSunNum(st.lon))
      A.push({auto:'location.place',cat:'location',title:'Location',value:Math.abs(st.lat).toFixed(5)+'\\u00b0 '+(st.lat<0?'S':'N')+', '+Math.abs(st.lon).toFixed(5)+'\\u00b0 '+(st.lon<0?'W':'E')+((A3D.site&&A3D.site.name)?' ('+A3D.site.name+')':''),source:'Project location',date:today});
    if(cnt.buildings){
      var hs=0,hm=0;for(i=0;i<bh.length;i++){hs+=bh[i];if(bh[i]>hm)hm=bh[i];}
      A.push({auto:'location.built',cat:'location',title:'Built context',value:bimSaN(cnt.buildings,'building')+rr+(bh.length?'; mean height '+(hs/bh.length).toFixed(1)+' m, tallest '+hm.toFixed(1)+' m':''),source:osm,date:od});
    }
    var P=A3D.objs.filter(bimIsProperty);
    if(P.length){
      var g=bimPropertyGeometry(P[0]);
      A.push({auto:'legal.boundary',cat:'legal',title:'Property line',value:P[0].name+': '+bimDispNum(g.area,1)+' m\\u00b2, perimeter '+bimDispNum(g.perimeter,1)+' m'+(g.misclosure>0.001?'; does not close by '+bimDispNum(g.misclosure,3)+' m':'')+(P.length>1?' ('+P.length+' property lines)':''),
        cls:g.misclosure>0.01?'constraint':'neutral',sev:g.misclosure>0.01?2:1,source:'Property line'+(P[0].source?' ('+P[0].source+')':''),date:today});
    }
    var DL=bimDataList();
    if(DL.length)A.push({auto:'legal.layers',cat:'legal',title:'Data layers',value:DL.map(function(L){return L.name;}).join(', '),source:DL.map(function(L){return L.credit;}).filter(function(x,j,a){return x&&a.indexOf(x)===j;}).join('; ')||'Data layers',date:today});
    var fl=DL.filter(function(L){return /flood/i.test(L.name||'');});
    if(fl.length)A.push({auto:'water.flood',cat:'water',title:'Flood zones',value:'Loaded: '+fl.map(function(L){return L.name;}).join(', ')+'. Read the zone at the site from the layer.',source:fl[0].credit||'Data layer',date:today});
    if(ter){
      var tin=bimTerrainTin(ter),rg=tin?bimTerrainRange(tin):null,sl=tin?bimSaSlope(tin):null,dat=bimCtxDatum();
      if(rg&&isFinite(rg[0])){
        var off=dat!==null&&dat!==undefined?dat:0,mean=sl?sl.mean*100:0,cl='neutral',sv=1;
        if(sl&&mean>=30){cl='constraint';sv=3;}else if(sl&&mean>=15){cl='constraint';sv=2;}else if(sl&&mean<5){cl='opportunity';}
        A.push({auto:'landform.terrain',cat:'landform',title:'Relief and slope',
          value:'Ground '+(rg[0]+off).toFixed(1)+' to '+(rg[1]+off).toFixed(1)+' m'+(dat!==null&&dat!==undefined?' above sea level':'')+' (relief '+(rg[1]-rg[0]).toFixed(1)+' m)'+
            (sl?'; mean slope '+mean.toFixed(1)+'%, steepest '+(sl.max*100).toFixed(0)+'%, '+Math.round(sl.steepShare*100)+'% of it steeper than 15%':''),
          cls:cl,sev:sv,source:(ter.context?ter.context.credit:((ter.source&&ter.source.format)?ter.source.format+' survey':'Survey'))||'Terrain',date:ter.context?ter.context.fetched:today});
      }
    }
    if(cnt.water)A.push({auto:'water.bodies',cat:'water',title:'Water',value:bimSaN(cnt.water,'water feature')+rr+' (water bodies and streams)',source:osm,date:od});
    if(A3D_SIM.rain&&A3D_SIM.rain.ponds)A.push({auto:'water.rain',cat:'water',title:'Rain flow',value:bimSaN(A3D_SIM.rain.ponds.length,'pond')+' where rain collects on the terrain',cls:A3D_SIM.rain.ponds.length?'constraint':'neutral',sev:1,source:'RAINFLOW on the terrain',date:today});
    if(bimSunNum(st.lat)&&bimSunNum(st.lon)){
      var dj=bimSaDayLen(st.lat,st.lon,'06-21'),dd=bimSaDayLen(st.lat,st.lon,'12-21');
      if(dj&&dd)A.push({auto:'climate.sun',cat:'climate',title:'Day length',value:'21 June: '+dj+'; 21 December: '+dd,source:'Sun position (NOAA equations)',date:today});
    }
    if(cnt.trees||cnt.green)A.push({auto:'ecology.green',cat:'ecology',title:'Trees and green',value:bimSaN(cnt.trees||0,'tree')+', '+bimSaN(cnt.green||0,'green area')+rr,cls:cnt.trees?'opportunity':'neutral',source:osm,date:od});
    if(cnt.roads){
      var uw=[],uk;for(uk in uses)if(uses.hasOwnProperty(uk))uw.push(bimSaN(uses[uk],BIM_ROAD_USE_LABEL[uk]||uk));
      A.push({auto:'access.roads',cat:'access',title:'Streets',value:bimSaN(cnt.roads,'road')+rr+(uw.length?': '+uw.join(', '):'')+(nBr?'; '+bimSaN(nBr,'bridge'):'')+(nTu?'; '+bimSaN(nTu,'tunnel'):''),cls:'opportunity',source:osm,date:od});
    }
    if(cnt.rail)A.push({auto:'access.rail',cat:'access',title:'Railways',value:bimSaN(cnt.rail,'railway feature')+rr+' (tracks, trams, platforms): transit, and noise and vibration',cls:'opportunity',source:osm,date:od});
    if(cnt.airports)A.push({auto:'access.airport',cat:'access',title:'Airport',value:bimSaN(cnt.airports,'airport feature')+rr+': aircraft noise and height limits are likely',cls:'constraint',sev:2,source:osm,date:od});
    if(cnt.power)A.push({auto:'utilities.power',cat:'utilities',title:'Overhead power',value:bimSaN(cnt.power,'pylon or line','pylons and lines')+rr+': keep the clearances',cls:'constraint',sev:2,source:osm,date:od});
    var lw=[],lk;for(lk in lu)if(lu.hasOwnProperty(lk))lw.push(bimSaN(lu[lk],lk+' area'));
    if(lw.length)A.push({auto:'people.landuse',cat:'people',title:'Land use around',value:lw.join(', ')+rr,source:osm,date:od});
    return A;
  }
  /* Fill from the model: what it knows, as findings; refilled in place, what was said about them kept */
  function bimSaFill(){
    var s=bimSa(),A=bimSaAuto(),i,f,seen={},add=0,upd=0,del=0;
    pushUndo();
    for(i=0;i<A.length;i++){
      seen[A[i].auto]=1;
      f=null;s.findings.forEach(function(x){if(x.auto===A[i].auto)f=x;});
      if(f){
        if(f.value!==A[i].value||f.title!==A[i].title||f.source!==A[i].source)upd++;
        f.title=A[i].title;f.value=A[i].value;f.source=A[i].source;f.date=A[i].date;f.cat=A[i].cat;
        if(!f.touched){f.cls=bimSaPair(BIM_SA_CLS,A[i].cls)?A[i].cls:'neutral';f.sev=A[i].sev||1;}
      }else{s.findings.push(bimSaNew(A[i].cat,A[i]));add++;}
    }
    s.findings=s.findings.filter(function(x){
      if(!x.auto||seen[x.auto])return true;
      if(x.note||x.photo||x.at||x.touched){x.auto='';return true;}   /* what was said about it stays, no longer refilled */
      del++;return false;
    });
    if(s.stage<1)s.stage=1;
    bimSaDone();
    a3dToast('Site analysis: '+(A.length?bimSaN(add,'finding')+' added, '+upd+' updated'+(del?', '+del+' gone':'')+' from the model':'nothing known yet: place the site and get its context first'));
    return {added:add,updated:upd,removed:del,total:A.length};
  }
  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){
    if(!bimSaCat(cat))return null;
    pushUndo();
    var n=bimSaNew(cat,f||{title:'New finding'});
    bimSa().findings.push(n);
    A3D_SA.edit=n.id;A3D_SA.open[cat]=true;
    bimSaDone();
    return n.id;
  }
  var BIM_SA_FIELDS={title:120,value:2000,source:200,note:2000};
  function bimSaSet(id,k,v){
    var f=bimSaFind(id);
    if(!f)return false;
    if(BIM_SA_FIELDS[k])v=String(v==null?'':v).slice(0,BIM_SA_FIELDS[k]);
    else if(k==='cls'){if(!bimSaPair(BIM_SA_CLS,v))return false;}
    else if(k==='conf'){if(!bimSaPair(BIM_SA_CONF,v))return false;}
    else if(k==='sev'){v=parseInt(v,10);if(!(v>=1&&v<=3))return false;}
    else if(k==='date'){if(!/^\\d{4}-\\d{2}-\\d{2}$/.test(String(v)))return false;}
    else if(k==='cat'){if(!bimSaCat(v))return false;}
    else return false;
    if(f[k]===v)return true;
    pushUndo();
    f[k]=v;
    if(k==='cls'||k==='sev'||k==='conf')f.touched=true;
    bimSaDone();
    return true;
  }
  function bimSaDel(id){
    var s=bimSa(),n=s.findings.length;
    if(!bimSaFind(id))return false;
    pushUndo();
    s.findings=s.findings.filter(function(f){return f.id!==id;});
    if(A3D_SA.edit===id)A3D_SA.edit=null;
    bimSaDone();
    return s.findings.length<n;
  }
  function bimSaSetDefine(k,v){
    var s=bimSa();
    if(k==='stage'){v=parseInt(v,10);if(!(v>=0&&v<BIM_SA_STAGES.length))return false;}
    else if(k==='ptype'){if(BIM_SA_TYPES.indexOf(v)<0)return false;}
    else if(k==='questions')v=String(v==null?'':v).slice(0,2000);
    else if(k==='pins')v=!!v;
    else return false;
    if(s[k]===v)return true;
    pushUndo();
    s[k]=v;
    bimSaDone();
    return true;
  }
  /* a checklist item: "location:d:0" (at the desk) or "location:v:1" (on site) */
  function bimSaCheck(key,on){
    var m=/^([a-z]+):(d|v):(\\d+)$/.exec(String(key||'')),c=m?bimSaCat(m[1]):null;
    if(!c||!(+m[3]<(m[2]==='d'?c.desk:c.visit).length))return false;
    var s=bimSa();
    on=!!on;
    if(!!s.checks[key]===on)return true;
    pushUndo();
    if(on)s.checks[key]=true;else delete s.checks[key];
    bimSaDone();
    return true;
  }
  function bimSaPlace(id,pt){
    var f=bimSaFind(id);
    if(!f){a3dToast('That finding is gone');return false;}
    pushUndo();
    f.at=pt?[Math.round(pt[0]*1000)/1000,Math.round(pt[1]*1000)/1000]:null;
    bimSaDone();
    if(pt)a3dToast('Finding '+bimSaNumber(f)+' pinned on the plan');
    return true;
  }
  function bimSaStartPin(id){
    var f=bimSaFind(id);
    if(!f)return false;
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'sapin',pts:[],y:lvl?lvl.elev:0,on:null,fid:id};
    a3dToast('Finding '+bimSaNumber(f)+': click where it is on the plan');
    paint();
    return true;
  }
  /* a photograph, made at most BIM_SA_PHOTO_PX across, as a JPEG kept with the project */
  function bimSaPhotoFromUrl(id,url){
    return new Promise(function(res){
      var im=new Image();
      im.onload=function(){
        var k=Math.min(1,BIM_SA_PHOTO_PX/Math.max(im.width,im.height)),c=document.createElement('canvas');
        c.width=Math.max(1,Math.round(im.width*k));c.height=Math.max(1,Math.round(im.height*k));
        c.getContext('2d').drawImage(im,0,0,c.width,c.height);
        var f=bimSaFind(id);
        if(!f){res(false);return;}
        pushUndo();
        f.photo=c.toDataURL('image/jpeg',0.72);
        bimSaDone();
        res(true);
      };
      im.onerror=function(){a3dToast('That photograph could not be read');res(false);};
      im.src=url;
    });
  }
  function bimSaPhotoFile(id,file){
    if(!file)return Promise.resolve(false);
    var u=URL.createObjectURL(file);
    return bimSaPhotoFromUrl(id,u).then(function(r){URL.revokeObjectURL(u);return r;});
  }
  function bimSaUnphoto(id){
    var f=bimSaFind(id);
    if(!f||!f.photo)return false;
    pushUndo();f.photo=null;bimSaDone();return true;
  }
  /* ---- the panel ---- */
  function bimSaOpt(L,cur){return L.map(function(p){return '<option value="'+bimEsc(p[0])+'"'+(p[0]===String(cur)?' selected':'')+'>'+bimEsc(p[1])+'</option>';}).join('');}
  function bimSaFindingHtml(f){
    var cl=bimSaPair(BIM_SA_CLS,f.cls),ed=A3D_SA.edit===f.id,h;
    h='<div class="a3d-safind c-'+f.cls+'" data-safind="'+bimEsc(f.id)+'">'+
      '<div class="a3d-safhd"><span class="a3d-safno">'+bimSaNumber(f)+'</span><span class="a3d-saftt">'+bimEsc(f.title)+'</span>'+
      '<button type="button" class="a3d-anzbtn" data-saact="'+(ed?'done':'edit:'+bimEsc(f.id))+'">'+(ed?'Done':'Edit')+'</button></div>'+
      (f.value?'<div class="a3d-safv">'+bimEsc(f.value)+'</div>':'')+
      (f.note?'<div class="a3d-safv"><b>Note:</b> '+bimEsc(f.note)+'</div>':'')+
      '<div class="a3d-safm"><b class="k-'+f.cls+'">'+bimEsc(cl)+(f.cls!=='neutral'?', '+bimSaPair(BIM_SA_SEV,String(f.sev)).toLowerCase():'')+'</b> \\u00b7 '+
      bimEsc(bimSaPair(BIM_SA_CONF,f.conf))+' \\u00b7 '+bimEsc(f.source||'no source given')+' \\u00b7 '+bimEsc(f.date)+(f.at?' \\u00b7 on the plan':'')+(f.auto?' \\u00b7 from the model':'')+'</div>'+
      (f.photo?'<img class="a3d-safph" alt="Photograph of finding '+bimSaNumber(f)+'" src="'+f.photo+'">':'');
    if(ed){
      var id=bimEsc(f.id);
      h+='<div class="a3d-safed">'+
        '<div class="a3d-sarow"><label>Title</label><input type="text" data-saff="'+id+':title" value="'+bimEsc(f.title)+'" maxlength="120"></div>'+
        '<div class="a3d-sarow"><label>Finding</label><textarea data-saff="'+id+':value" maxlength="2000">'+bimEsc(f.value)+'</textarea></div>'+
        '<div class="a3d-sarow"><label>Class</label><select data-saff="'+id+':cls">'+bimSaOpt(BIM_SA_CLS,f.cls)+'</select></div>'+
        '<div class="a3d-sarow"><label>Severity</label><select data-saff="'+id+':sev">'+bimSaOpt(BIM_SA_SEV,String(f.sev))+'</select></div>'+
        '<div class="a3d-sarow"><label>Confidence</label><select data-saff="'+id+':conf">'+bimSaOpt(BIM_SA_CONF,f.conf)+'</select></div>'+
        '<div class="a3d-sarow"><label>Category</label><select data-saff="'+id+':cat">'+bimSaOpt(BIM_SA_CATS.map(function(c,i){return [c.id,(i+1)+'. '+c.n];}),f.cat)+'</select></div>'+
        '<div class="a3d-sarow"><label>Source</label><input type="text" data-saff="'+id+':source" value="'+bimEsc(f.source)+'" maxlength="200" placeholder="Where it comes from"></div>'+
        '<div class="a3d-sarow"><label>Date</label><input type="date" data-saff="'+id+':date" value="'+bimEsc(f.date)+'"></div>'+
        '<div class="a3d-sarow"><label>Note</label><textarea data-saff="'+id+':note" maxlength="2000" placeholder="What you saw, what to do">'+bimEsc(f.note)+'</textarea></div>'+
        '<div class="a3d-saacts">'+
        '<button type="button" class="a3d-anzbtn" data-saact="pin:'+id+'">'+(f.at?'Move on the plan':'Place on the plan')+'</button>'+
        (f.at?'<button type="button" class="a3d-anzbtn" data-saact="unpin:'+id+'">Take off the plan</button>':'')+
        '<label class="a3d-anzbtn" style="display:inline-flex;align-items:center">'+(f.photo?'Replace photograph':'Add photograph')+
        '<input type="file" accept="image/*" data-saphoto="'+id+'" hidden></label>'+
        (f.photo?'<button type="button" class="a3d-anzbtn" data-saact="unphoto:'+id+'">Remove photograph</button>':'')+
        '<button type="button" class="a3d-anzbtn" data-saact="del:'+id+'">Delete</button></div></div>';
    }
    return h+'</div>';
  }
  function bimSaCatHtml(c,i){
    var s=bimSa(),F=bimSaOf(c.id),open=!!A3D_SA.open[c.id],nc=0,no=0,nr=0,cf=bimSaConfOf(c.id),j,dn=0;
    F.forEach(function(f){if(f.cls==='constraint')nc++;else if(f.cls==='opportunity')no++;else if(f.cls==='redflag')nr++;});
    for(j=0;j<c.desk.length;j++)if(s.checks[c.id+':d:'+j])dn++;
    for(j=0;j<c.visit.length;j++)if(s.checks[c.id+':v:'+j])dn++;
    var sum=F.length?bimSaN(F.length,'finding')+(nr?', '+bimSaN(nr,'red flag'):'')+(nc?', '+bimSaN(nc,'constraint'):'')+(no?', '+bimSaN(no,'opportunity','opportunities'):''):'No findings yet';
    sum+=' \\u00b7 '+dn+' of '+(c.desk.length+c.visit.length)+' checked';
    var stt=cf==='surveyed'?'on':cf==='site'?'on':cf==='desktop'?'warn':'';
    var h='<div class="a3d-anzcard a3d-sacat'+(open?' open':'')+'" data-sacat="'+c.id+'">'+
      '<div class="a3d-anzhd"><button type="button" class="a3d-anztog" data-satog="'+c.id+'" aria-expanded="'+open+'">'+
      '<span class="a3d-anzchev">'+BIM_ANZ_CHEV+'</span><span class="a3d-anzname"><span class="a3d-anzttl">'+(i+1)+'. '+bimEsc(c.n)+'</span>'+
      '<span class="a3d-anzsum">'+bimEsc(sum)+'</span></span></button>'+
      (cf?'<span class="a3d-anzstate a3d-anzstate-'+stt+'">'+bimEsc(bimSaPair(BIM_SA_CONF,cf))+'</span>':'')+'</div>'+
      '<div class="a3d-anzbody"><div class="a3d-saq">'+bimEsc(c.q)+'</div>'+
      (F.length?F.map(bimSaFindingHtml).join(''):'<div class="a3d-sanote">No findings yet.</div>')+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn" data-saact="add:'+c.id+'">Add finding</button></div>'+
      '<div class="a3d-sachkhd">At the desk</div>'+c.desk.map(function(t,k){var key=c.id+':d:'+k,on=!!s.checks[key];
        return '<label class="a3d-sachk'+(on?' on':'')+'"><input type="checkbox" data-sachk="'+key+'"'+(on?' checked':'')+'><span>'+bimEsc(t)+'</span></label>';}).join('')+
      '<div class="a3d-sachkhd">On site</div>'+c.visit.map(function(t,k){var key=c.id+':v:'+k,on=!!s.checks[key];
        return '<label class="a3d-sachk'+(on?' on':'')+'"><input type="checkbox" data-sachk="'+key+'"'+(on?' checked':'')+'><span>'+bimEsc(t)+'</span></label>';}).join('')+
      '</div></div>';
    return h;
  }
  function bimSaHtml(){
    var s=bimSa(),F=s.findings,R=F.filter(function(f){return f.cls==='redflag';}),P=A3D.objs.filter(bimIsProperty),bd;
    if(P.length){var g=bimPropertyGeometry(P[0]);bd=bimEsc(P[0].name)+', '+bimDispNum(g.area,1)+' m\\u00b2';}
    else bd='None yet: <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyshape">From a shape</button> <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyline">From bearings</button>';
    var h='<div class="a3d-anz a3d-sa"><div class="a3d-anzhead"><span class="a3d-anzttl0">Site analysis</span><span class="a3d-anzcount">'+
      bimSaN(F.length,'finding')+(R.length?', '+bimSaN(R.length,'red flag'):'')+'</span></div>'+
      '<div class="a3d-sastages" role="group" aria-label="Stage">'+BIM_SA_STAGES.map(function(x,i){
        return '<button type="button" class="a3d-sastage'+(i===s.stage?' on':(i<s.stage?' done':''))+'" data-sastage="'+i+'" aria-pressed="'+(i===s.stage)+'" title="'+bimEsc(x[1])+'">'+i+' '+bimEsc(x[0])+'</button>';}).join('')+'</div>'+
      '<div class="a3d-sastagecap">'+bimEsc(BIM_SA_STAGES[s.stage][1])+'</div>';
    if(R.length)h+='<div class="a3d-saflags"><div class="a3d-sasechd">Red flags first</div>'+R.map(function(f){return '<div class="a3d-saflag">'+bimSaNumber(f)+' '+bimEsc(f.title)+(f.value?': '+bimEsc(f.value):'')+'</div>';}).join('')+'</div>';
    h+='<div class="a3d-sasec"><div class="a3d-sasechd">Define</div>'+
      '<div class="a3d-sarow"><span class="a3d-salab">Boundary</span><span class="a3d-saval">'+bd+'</span></div>'+
      '<div class="a3d-sarow"><label for="a3d-saptype">Project</label><select id="a3d-saptype" data-saf="ptype">'+BIM_SA_TYPES.map(function(x){return '<option value="'+bimEsc(x)+'"'+(x===s.ptype?' selected':'')+'>'+(x?bimEsc(x):'Not set')+'</option>';}).join('')+'</select></div>'+
      '<div class="a3d-sarow"><label for="a3d-saq">Questions</label><textarea id="a3d-saq" data-saf="questions" maxlength="2000" placeholder="What must the analysis answer?">'+bimEsc(s.questions)+'</textarea></div>'+
      '<label class="a3d-sachk'+(s.pins?'':'')+'"><input type="checkbox" data-saf="pins"'+(s.pins?' checked':'')+'><span>Show the findings on the plan</span></label>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="fill" title="Location, context, property, terrain, sun, access: what the model knows, with its sources">Fill from the model</button>'+
      '<button type="button" class="a3d-anzbtn" data-saact="cmd:context">Get the context</button></div></div>'+
      '<div class="a3d-sasec"><div class="a3d-sasechd">The ten categories</div><div class="a3d-anzlist">'+BIM_SA_CATS.map(bimSaCatHtml).join('')+'</div></div></div>';
    return h;
  }
  function bimSaWire(w){
    w.addEventListener('click',function(ev){
      var t=ev.target&&ev.target.closest?ev.target:null,b;
      if(!t)return;
      b=t.closest('[data-sastage]');if(b){bimSaSetDefine('stage',b.getAttribute('data-sastage'));return;}
      b=t.closest('[data-satog]');if(b){bimSaToggle(b.getAttribute('data-satog'));return;}
      b=t.closest('[data-saact]');if(!b||b.disabled)return;
      try{bimSaAct(b.getAttribute('data-saact'));}catch(eS){console.warn('[BIM] Site analysis',eS);a3dToast('That did not work - see the console');}
    });
    w.addEventListener('change',function(ev){
      var e=ev.target,k;
      if(!e||!e.getAttribute)return;
      if((k=e.getAttribute('data-saf'))){bimSaSetDefine(k,k==='pins'?e.checked:e.value);return;}
      if((k=e.getAttribute('data-sachk'))){bimSaCheck(k,e.checked);return;}
      if((k=e.getAttribute('data-saff'))){var i=k.lastIndexOf(':');bimSaSet(k.slice(0,i),k.slice(i+1),e.value);return;}
      if((k=e.getAttribute('data-saphoto'))){bimSaPhotoFile(k,e.files&&e.files[0]);return;}
    });
  }
  function bimSaToggle(id,on){
    if(!bimSaCat(id))return false;
    var v=on===undefined?!A3D_SA.open[id]:!!on;
    if(v)A3D_SA.open[id]=true;else delete A3D_SA.open[id];
    try{localStorage.setItem('acad3dSaOpen',JSON.stringify(A3D_SA.open));}catch(eS){}
    var c=document.querySelector('.a3d-sa-wrap [data-sacat="'+id+'"]'),b;
    if(c){c.classList.toggle('open',v);b=c.querySelector('[data-satog]');if(b)b.setAttribute('aria-expanded',String(v));}
    return v;
  }
  function bimSaAct(a){
    var k=String(a||''),i=k.indexOf(':'),v=i<0?'':k.slice(i+1),c=i<0?k:k.slice(0,i);
    if(c==='fill')return bimSaFill();
    if(c==='add')return bimSaAdd(v);
    if(c==='edit'){A3D_SA.edit=v;bimSaRefresh(true);return true;}
    if(c==='done'){A3D_SA.edit=null;bimSaRefresh(true);return true;}
    if(c==='del')return bimSaDel(v);
    if(c==='pin')return bimSaStartPin(v);
    if(c==='unpin')return bimSaPlace(v,null);
    if(c==='unphoto')return bimSaUnphoto(v);
    if(c==='cmd'&&/^(propertyshape|propertyline|context)$/.test(v))return window.__a3dRunCmd(v);
    return false;
  }
  /* the panel again: not while something in it has the focus, or what is typed would be lost */
  function bimSaRefresh(force){
    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='site'?sh.querySelector('.a3d-sa-wrap'):null;
    if(!w)return false;
    if(!force&&document.activeElement&&w.contains(document.activeElement)&&/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName))return false;
    var sc=w.querySelector('.a3d-sa'),top=sc?sc.scrollTop:0;
    try{w.innerHTML=bimSaHtml();var sc2=w.querySelector('.a3d-sa');if(sc2)sc2.scrollTop=top;}catch(eR){console.warn('[BIM] Site analysis panel',eR);}
    return true;
  }
  /* the pins: a numbered circle in the finding's colour */
  function drawSaPins(ctx,V,W,H){
    var s=A3D.site&&A3D.site.analysis,out=[],i,f,p;
    A3D.lastSaPins=out;
    if(!s||!s.pins||!Array.isArray(s.findings)||A3D.section)return;
    var y=0;
    ctx.save();
    ctx.font='600 10px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
    for(i=0;i<s.findings.length;i++){
      f=s.findings[i];
      if(!f.at)continue;
      p=toScreen([f.at[0],y,f.at[1]],V,W,H);
      if(!p||!isFinite(p[0])||!isFinite(p[1]))continue;
      var lab=bimSaNumber(f),r=Math.max(9,ctx.measureText(lab).width/2+5);
      ctx.beginPath();ctx.moveTo(p[0],p[1]);ctx.lineTo(p[0]-4,p[1]-r-2);ctx.lineTo(p[0]+4,p[1]-r-2);ctx.closePath();
      ctx.fillStyle=BIM_SA_COL[f.cls]||BIM_SA_COL.neutral;ctx.fill();
      ctx.beginPath();ctx.arc(p[0],p[1]-r-6,r,0,Math.PI*2);ctx.fill();
      ctx.lineWidth=1.5;ctx.strokeStyle='rgba(255,255,255,.9)';ctx.stroke();
      ctx.fillStyle='#fff';ctx.fillText(lab,p[0],p[1]-r-6);
      out.push({id:f.id,n:lab,x:p[0],y:p[1],cls:f.cls});
    }
    ctx.restore();
  }""")

# ---- hooks ----
rep("""  window.__acad3dV157='railkind,""", """  window.__acad3dV158='stages,categories,findings,sources,confidence,classes,checklists,fillfrommodel,pins,photos,sitetab';
  window.__a3dSa=function(){return JSON.parse(JSON.stringify(bimSa()));};
  window.__a3dSaStandard=function(){return {stages:BIM_SA_STAGES.map(function(x){return x[0];}),cats:BIM_SA_CATS.map(function(c){return {id:c.id,n:c.n,desk:c.desk.length,visit:c.visit.length};})};};
  window.__a3dSaAuto=function(){return bimSaAuto();};
  window.__a3dSaSlope=function(tin){return bimSaSlope(tin);};
  window.__a3dSaFill=function(){return bimSaFill();};
  window.__a3dSaAdd=function(cat,f){return bimSaAdd(cat,f);};
  window.__a3dSaSet=function(id,k,v){return bimSaSet(id,k,v);};
  window.__a3dSaDel=function(id){return bimSaDel(id);};
  window.__a3dSaDefine=function(k,v){return bimSaSetDefine(k,v);};
  window.__a3dSaCheck=function(k,on){return bimSaCheck(k,on);};
  window.__a3dSaPlace=function(id,pt){return bimSaPlace(id,pt);};
  window.__a3dSaStartPin=function(id){return bimSaStartPin(id);};
  window.__a3dSaPhotoUrl=function(id,url){return bimSaPhotoFromUrl(id,url);};
  window.__a3dSaNumber=function(id){var f=bimSaFind(id);return f?bimSaNumber(f):null;};
  window.__a3dSaPins=function(){return (A3D.lastSaPins||[]).slice();};
  window.__a3dSaEdit=function(id){A3D_SA.edit=id||null;bimSaRefresh(true);return true;};
  window.__acad3dV157='railkind,""")
rep("""  var BIM_APP_VERSION={v:'V157',date:'2026-10-04'};   /* __acad3dV157 */""",
    """  var BIM_APP_VERSION={v:'V158',date:'2026-10-04'};   /* __acad3dV158 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
