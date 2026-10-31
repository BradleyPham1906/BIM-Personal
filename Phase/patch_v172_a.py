#!/usr/bin/env python3
"""V172, patch a: the site analysis tools, wired in. reference/research-site-analysis-tools.md (5, 7).

The tools' own files are new, in src/js/engine/site-tools/ (the grid, what they read, the tools, Buffer, Distance,
Slope classes, Exclusions, Suitability, Locate, Buildable area, Constraints and opportunities, the panel) and
src/js/engine/testing/hooks-tools.js. This patch joins them to the app: the page lists them; the layout table has
their rows; the standards registry has the two records they read (Pennsylvania's site capacity calculation, as
Chalfont's section 440-17 has it, and the app's working set for constraints and opportunities) and a unit for a
ratio; the analysis workspace has the Tools group on its left, the tool on its right, its buttons and its fields;
the search reads the tools' rows; a tool's output is a result layer (V148): kept, drawn, out of date when the lot
changes, run again by Update, its swatch, key and words in Layers; the commands; the version.

Run from the repository root: python3 Phase/patch_v172_a.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('88f3938bdfb5af67d2645b822dd4e5f27f23fedab28160e19179879ee4557a43')   # V171d

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEW = ['site-tools/grid.js', 'site-tools/sources.js', 'site-tools/tools.js', 'site-tools/basic.js', 'site-tools/suitability.js',
       'site-tools/capacity.js', 'site-tools/panel.js']
for f in NEW + ['testing/hooks-tools.js']:
    p = ROOT / 'src' / 'js' / 'engine' / f
    if not p.exists():
        sys.exit('src/js/engine/%s is missing' % f)
    t = p.read_text(encoding='utf-8')
    try:
        t.encode('ascii')
    except UnicodeEncodeError as e:
        sys.exit('src/js/engine/%s: non-ASCII at %d' % (f, e.start))

# ---- the page: the files, in the order their code runs ----
rep('index.html', '<!-- @include js/engine/site-analysis/analysis-workspace.js -->\n',
    '<!-- @include js/engine/site-analysis/analysis-workspace.js -->\n' + ''.join('<!-- @include js/engine/%s -->\n' % f for f in NEW))
rep('index.html', '<!-- @include js/engine/testing/hooks-sun.js -->\n',
    '<!-- @include js/engine/testing/hooks-sun.js -->\n<!-- @include js/engine/testing/hooks-tools.js -->\n')

# ---- the layout table: each file's row, at its first line ----
LAY = ROOT / 'tools' / 'app_layout.py'
lay = LAY.read_text(encoding='utf-8')
a = "    ('site-analysis/analysis-workspace.js', '  /* ================= __acad3dV171b: the analysis workspace ================='),\n"
b = "    ('testing/hooks-sun.js', '  /* __acad3dV171d: the sun path, one clock, for the suite */'),\n"
if lay.count(a) != 1 or lay.count(b) != 1:
    sys.exit('tools/app_layout.py: the anchors are not there once each')
rows = ''
for f in NEW:
    first = (ROOT / 'src' / 'js' / 'engine' / f).read_text(encoding='utf-8').split('\n', 1)[0]
    rows += '    (%r, %r),\n' % (f, first)
hk = (ROOT / 'src' / 'js' / 'engine' / 'testing' / 'hooks-tools.js').read_text(encoding='utf-8').split('\n', 1)[0]
lay = lay.replace(a, a + rows).replace(b, b + '    (%r, %r),\n' % ('testing/hooks-tools.js', hk))

# ---- the standards registry: the two records, and a ratio's unit ----
RG = 'js/engine/standards/registry.js'
rep(RG, "    {id:'terrain.slope_bands',title:'Slope bands on terrain',",
    r"""    /* __acad3dV172: Buildable area, Pennsylvania's site capacity calculation, the owner's choice (2026-10-27) */
    {id:'land.site_capacity',title:'Site capacity: the open space ratios of resource protection land',pub:'Chalfont Borough, Pennsylvania',kind:'code',area:'Flood and ground',use:'Buildable area (the site analysis tools)',anywhere:true,
      eds:[{id:'land.site_capacity.chalfont',name:'Chalfont Borough Zoning, section 440-17, site capacity calculations',pub:'',st:'current',where:'Chalfont, Pennsylvania',adopt:[{at:'us-pa:chalfont'}],
        src:{t:'Chalfont Borough Code, Chapter 440 Zoning, section 440-17 Site capacity calculations, B, the resources and their open space ratios; read in Zoneomics\' copy of the code, not the borough\'s own',w:'section 440-17 B',u:'https://www.zoneomics.com/code/chalfont-PA/chapter_5',lv:'S',read:'2026-10-27'},
        v:[{n:'floodplain',v:1,u:'ratio',say:'floodplains'},{n:'slope_lo',v:15,u:'%',say:'the lower class of steep slopes from',lt:'slope_hi'},{n:'slope_hi',v:25,u:'%',say:'the upper class of steep slopes from',gt:'slope_lo'},
          {n:'slope_a',v:0.7,u:'ratio',say:'steep slopes of the lower class'},{n:'slope_b',v:0.85,u:'ratio',say:'steep slopes of the upper class'},
          {n:'forest',v:0.5,u:'ratio',say:'forested areas with no other resource'},{n:'forest_with',v:0.8,u:'ratio',say:'forested areas with another resource'},
          {n:'pond',v:1,u:'ratio',say:'ponds'},{n:'waters',v:1,u:'ratio',say:'waters of the Commonwealth'},{n:'wetland',v:1,u:'ratio',say:'wetlands'}]}]},
    {id:'terrain.slope_bands',title:'Slope bands on terrain',""")
rep(RG, "    {id:'app.land',title:'Land use, form and green around the site',",
    r"""    /* __acad3dV172: Constraints and opportunities, the app's working set */
    {id:'app.synthesis',title:'Constraints and opportunities: the distances and hours',pub:'This app',kind:'assumption',area:'Land and green',use:'Constraints and opportunities (the site analysis tools)',anywhere:true,
      eds:[{id:'app.synthesis.1',name:'The app\'s working set (V172)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: a working set for the summary plan, not a standard; set each to the place\'s own rule where it has one',w:'research-site-analysis-tools.md, sections 3 and 5',lv:'A'},
        v:[{n:'near_art',v:30,u:'m',say:'near an arterial road, within'},{n:'front',v:10,u:'m',say:'street frontage, within'},
          {n:'sunny',v:6,u:'h',say:'sunny, from'},{n:'shade',v:2,u:'h',say:'overshadowed, under'},{n:'green',v:15,u:'m',say:'near trees and woods, within'}]}]},
    {id:'app.land',title:'Land use, form and green around the site',""")
rep(RG, r"""'du/acre':[' an acre',' an acre'],deg:['\u00b0','\u00b0']};""",
    r"""'du/acre':[' an acre',' an acre'],deg:['\u00b0','\u00b0'],ratio:['',''],h:[' h',' h']};   /* __acad3dV172: a ratio, hours */""")

# ---- the analysis workspace: the Tools group, the tool's panel, its buttons and fields ----
AW = 'js/engine/site-analysis/analysis-workspace.js'
rep(AW, "    if(k==='cat'?!bimSaCat(id):!(k==='card'&&bimAwCard(id)))return false;",
    "    if(k==='cat'?!bimSaCat(id):k==='tool'?!(bimTlTool(id)||id==='history'):!(k==='card'&&bimAwCard(id)))return false;   /* __acad3dV172: a tool, or History */")
rep(AW, """    var r=document.querySelector('.a3d-analyze-wrap '+(k==='cat'?'[data-sacat="'+id+'"]':'[data-anzcard="'+id+'"]')),lp=document.getElementById('a3d-leftpanel'),a,b;""",
    """    var r=document.querySelector('.a3d-analyze-wrap '+(k==='cat'?'[data-sacat="'+id+'"]':k==='tool'?'[data-tlrow="'+id+'"]':'[data-anzcard="'+id+'"]')),lp=document.getElementById('a3d-leftpanel'),a,b;""")
rep(AW, "    M=BIM_ANZ_MODEL.map(function(id){return C.filter(function(c){return c.id===id;})[0];}).filter(function(c){return !!c;});",
    "    h+=bimTlListHtml(pk);   /* __acad3dV172: the tools */\n    M=BIM_ANZ_MODEL.map(function(id){return C.filter(function(c){return c.id===id;})[0];}).filter(function(c){return !!c;});")
rep(AW, "    if(pk&&pk.k==='card'&&(c=bimAwCard(pk.id)))return bimAwCardHtml(c);",
    "    if(pk&&pk.k==='card'&&(c=bimAwCard(pk.id)))return bimAwCardHtml(c);\n    if(pk&&pk.k==='tool'&&(bimTlTool(pk.id)||pk.id==='history'))return bimTlPanelHtml(pk.id);   /* __acad3dV172 */")
rep(AW, "      else if(c==='cat'||c==='card')r=bimAwPick(c,a);",
    "      else if(c==='cat'||c==='card')r=bimAwPick(c,a);\n      else if(c==='tool')r=bimAwPick('tool',a);   /* __acad3dV172: a tool, and its buttons */\n      else if(c==='tl'){r=bimTlAct(a);bimAwRefresh();}")
rep(AW, "        else if((k=e.getAttribute('data-sunsl')))bimSunSlide(k,e.value,true);   /* __acad3dV171d: a slider let go; the redraw keeps it in the hand */",
    "        else if((k=e.getAttribute('data-sunsl')))bimSunSlide(k,e.value,true);   /* __acad3dV171d: a slider let go; the redraw keeps it in the hand */\n"
    "        else if((k=e.getAttribute('data-tlf'))){bimTlSetField(k,e.type==='checkbox'?e.checked:e.value);if(bimAwOwns())bimAwRender(true);}   /* __acad3dV172: a tool's field, checked again */")

# ---- the search: the tools' rows by their words ----
AZ = 'js/engine/analysis/analyze-tab.js'
rep(AZ, "    if(q)bimAnzCards().forEach(function(x){C[x.id]=x;});",
    "    if(q){bimAnzCards().forEach(function(x){C[x.id]=x;});bimTlCards().forEach(function(x){C[x.id]=x;});}   /* __acad3dV172: the tools' rows */")
rep(AZ, "      c=bimSaCat(K[i].getAttribute('data-sacat'));nm=c?c.n:'Model';",
    "      c=bimSaCat(K[i].getAttribute('data-sacat'));nm=c?c.n:(K[i].getAttribute('data-anzgrp')==='tools'?'Tools':'Model');")

# ---- result layers: a tool's output ----
RL = 'js/engine/analysis/results-layers.js'
rep(RL, "  function bimResStale(R){return !!(R&&R.kind!=='terrain'&&R.kind!=='walk'&&R.key&&R.key!==bimResKey(R.kind));}",
    "  function bimResStale(R){if(R&&R.kind==='tool')return bimTlStale(R);   /* __acad3dV172: a tool's output, when the lot has changed */\n"
    "    return !!(R&&R.kind!=='terrain'&&R.kind!=='walk'&&R.key&&R.key!==bimResKey(R.kind));}")
rep(RL, "    if(R.kind==='walk'){a3dToast(R.name+' follows the access data: it is up to date');return true;}   /* __acad3dV161 */",
    "    if(R.kind==='walk'){a3dToast(R.name+' follows the access data: it is up to date');return true;}   /* __acad3dV161 */\n"
    "    if(R.kind==='tool')return bimTlLayerRerun(R);   /* __acad3dV172: its run again, with the same parameters */")
rep(RL, "      if(R.kind==='walk')return R.src==='access';   /* __acad3dV161 */",
    "      if(R.kind==='walk')return R.src==='access';   /* __acad3dV161 */\n      if(R.kind==='tool')return bimTlDataOk(R.data);   /* __acad3dV172 */")
rep(RL, "    var op=bimResOpacity(R),d=R.data,o,tin,tb;\n",
    "    var op=bimResOpacity(R),d=R.data,o,tin,tb;\n"
    "    if(R.kind==='tool'){var im=bimTlDataOk(d)?bimTlImage(R):null;if(!im)return false;bimSimDrawGrid(ctx,V,W,H,d,im,d.y||0,op);return true;}   /* __acad3dV172 */\n")

# ---- Layers: a tool layer's swatch, key and words ----
LY = 'js/engine/layers/analysis-data-rows.js'
rep(LY, "  function bimResSwatch(R){\n",
    "  function bimResSwatch(R){\n"
    "    if(R.kind==='tool'){var K=(R.data&&R.data.keys)||[];return K.length>1?'linear-gradient(90deg,'+K.map(function(k){return k.col;}).join(',')+')':(K.length?K[0].col:'#888');}   /* __acad3dV172 */\n")
rep(LY, "    if(R.kind!=='terrain'||bimResGone(R))return '';\n    o=objById(R.src);",
    "    if(R.kind==='tool')return d&&d.keys&&d.keys.length?'<div class=\"a3d-lyleg\">'+d.keys.map(function(k){return '<span><i style=\"background:'+bimEsc(k.col)+'\"></i>'+bimEsc(k.name)+'</span>';}).join('')+'</div>':'';   /* __acad3dV172 */\n"
    "    if(R.kind!=='terrain'||bimResGone(R))return '';\n    o=objById(R.src);")
rep(LY, "    if(R.kind!=='terrain'&&R.kind!=='walk'&&bimResStale(R))s+=' The model has changed since: Update runs it again'+(R.kind==='sunhours'?' for '+(d&&d.date):'')+'.';",
    "    else if(R.kind==='tool'){var th=bimTlRunById(R.run),tt=bimTlTool(R.tool);s=(tt?tt.name:'A tool')+'\\'s output'+(th?', from the run of '+th.at+(th.sum?': '+th.sum:''):'')+'. Update runs it again with the same parameters.';   /* __acad3dV172 */\n"
    "      if(bimTlStale(R))s+=' The lot has changed since: Update runs it on the lot as it is now.';}\n"
    "    if(R.kind!=='terrain'&&R.kind!=='walk'&&R.kind!=='tool'&&bimResStale(R))s+=' The model has changed since: Update runs it again'+(R.kind==='sunhours'?' for '+(d&&d.date):'')+'.';")

# ---- the commands ----
SH = 'js/shell/shell.js'
rep(SH, "    ['TRAFFICOFF',['TRAFFICSTOP'],'trafficoff','Stop simulating traffic and people'],\n",
    "    ['TRAFFICOFF',['TRAFFICSTOP'],'trafficoff','Stop simulating traffic and people'],\n"
    "    /* __acad3dV172: the site analysis tools, in the analysis workspace */\n"
    "    ['SITETOOLS',['GEOPROCESSING','TOOLHISTORY','GPHISTORY'],'sitetools','The site analysis tools and their History: buffer, distance, slope classes, exclusions, suitability, locate, constraints and opportunities, buildable area'],\n"
    "    ['BUFFER',['SABUFFER','BUFFERZONE'],'tlbuffer','Buffer: the area within a distance of the streets, the lot line, the trees, the flood zones or another layer'],\n"
    "    ['DISTANCEFROM',['EUCLIDEANDISTANCE','SADISTANCE'],'tldistance','Distance: the straight-line distance from every cell to the nearest of a layer\\'s features'],\n"
    "    ['SLOPECLASSES',['SLOPECLASS','SASLOPE'],'tlslope','Slope classes: the ground\\'s slope in the standards registry\\'s classes for development'],\n"
    "    ['EXCLUSIONS',['RESTRICTED','SAEXCLUDE'],'tlexclude','Exclusions: where building is restricted -- outside the lot, the setbacks, flood zones, wetlands, steep slopes, buildings, a buffer'],\n"
    "    ['SUITABILITY',['WEIGHTEDOVERLAY','SUITABILITYMODEL','SASUIT'],'tlsuit','Suitability: the criteria turned to a common scale, weighted and added, the restricted cells left out, as Esri\\'s Suitability Modeler'],\n"
    "    ['LOCATE',['LOCATEREGIONS','BESTSITE'],'tllocate','Locate: the best connected region of a given area in a suitability map'],\n"
    "    ['CONSTRAINTSMAP',['OPPORTUNITIES','CONSTRAINTSOPPORTUNITIES','SASYNTH'],'tlsynth','Constraints and opportunities: what limits the site and what it offers, on one plan'],\n"
    "    ['BUILDABLE',['SITECAPACITY','NETBUILDABLE','BUILDABLEAREA'],'tlcapacity','Buildable area: Pennsylvania\\'s site capacity calculation -- the net buildable site area, and where to build within the setbacks'],\n")
CM = 'js/engine/commands/command-map.js'
rep(CM, "    trafficoff:function(){bimTrCommand(false);},\n",
    "    trafficoff:function(){bimTrCommand(false);},\n"
    "    sitetools:function(){bimTlCommand('history');},tlbuffer:function(){bimTlCommand('buffer');},tldistance:function(){bimTlCommand('distance');},   /* __acad3dV172 */\n"
    "    tlslope:function(){bimTlCommand('slopecls');},tlexclude:function(){bimTlCommand('exclude');},tlsuit:function(){bimTlCommand('suit');},\n"
    "    tllocate:function(){bimTlCommand('locate');},tlsynth:function(){bimTlCommand('synth');},tlcapacity:function(){bimTlCommand('capacity');},\n")
CC = 'js/engine/commands/command-catalogue.js'
rep(CC, "  var BIM_CMD_TERMS={SITEWORKSPACE:",
    "  var BIM_CMD_TERMS={SITETOOLS:'geoprocessing pane history arcgis analysis tools runs',BUFFER:'around within distance zone setback dissolve',   /* __acad3dV172 */\n"
    "    DISTANCEFROM:'euclidean straight line nearest proximity',SLOPECLASSES:'reclassify steep gentle gradient',EXCLUSIONS:'restricted constraints mask nodata',\n"
    "    SUITABILITY:'weighted overlay criteria transform weight multicriteria siting',LOCATE:'regions best site footprint where to build',\n"
    "    CONSTRAINTSMAP:'constraints opportunities synthesis site analysis plan',BUILDABLE:'site capacity net buildable resource protection density impervious acres',\n"
    "    SITEWORKSPACE:")

# ---- the version ----
GV = 'js/engine/ui/guide-versions.js'
rep(GV, "  var BIM_APP_VERSION={v:'V171',date:'2026-10-25'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170; __acad3dV171 */",
    "  var BIM_APP_VERSION={v:'V172',date:'2026-10-31'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170; __acad3dV171; __acad3dV172 */")

# ---- the look: the tool's form, its messages, its status, its runs ----
rep('css/site-analysis/workspace.css', "body.light-theme .a3d-awp .a3d-sun-mode .a3d-anzbtn.on{border-color:#d63b41;color:#9f1d22;background:rgba(214,59,65,.08)}\n",
    "body.light-theme .a3d-awp .a3d-sun-mode .a3d-anzbtn.on{border-color:#d63b41;color:#9f1d22;background:rgba(214,59,65,.08)}\n"
    "/* __acad3dV172: the site analysis tools, in the geoprocessing pane's shape */\n"
    ".a3d-tl-form{display:flex;flex-direction:column;gap:8px}\n"
    ".a3d-tl-f{display:flex;flex-direction:column;gap:3px;font-size:12px;min-width:0}\n"
    ".a3d-tl-l{color:#c9d1d9}\n"
    ".a3d-tl-req{font-style:normal;color:#ff6b6b;margin-left:3px}\n"
    ".a3d-tl-in{display:flex;align-items:center;gap:6px}\n"
    ".a3d-tl input[type=text],.a3d-tl select{box-sizing:border-box;width:100%;min-width:0;background:#1f2327;border:1px solid #3a4048;border-radius:6px;color:#e6eaef;padding:3px 7px;min-height:28px;font:inherit;font-size:12px}\n"
    ".a3d-tl input[aria-invalid=true],.a3d-tl select[aria-invalid=true]{border-color:#e5484d}\n"
    ".a3d-tl-u{flex:0 0 auto;color:#8a96a3;font-size:11.5px}\n"
    ".a3d-tl-help{font-size:11px;color:#8a96a3}\n"
    ".a3d-tl-b{flex-direction:row;align-items:center;gap:8px;flex-wrap:wrap}\n"
    ".a3d-tl-b input[type=checkbox]{width:16px;height:16px;margin:0}\n"
    ".a3d-tl-msg{display:block;font-size:11.5px;line-height:1.35}\n"
    ".a3d-tl-msg.err{color:#ff8b8b}.a3d-tl-msg.warn{color:#f0b35a}\n"
    ".a3d-tl-crits{display:flex;flex-direction:column;gap:6px}\n"
    ".a3d-tl-crit{border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:6px 8px}\n"
    ".a3d-tl-crit .a3d-tl-cn{font-weight:550}\n"
    ".a3d-tl-cf{display:grid;grid-template-columns:1fr 1fr;gap:6px 8px;margin-top:6px}\n"
    ".a3d-tl-cf label{display:flex;flex-direction:column;gap:2px;font-size:11px;color:#8a96a3;min-width:0}\n"
    ".a3d-tl-cf label.w{grid-column:1/-1}\n"
    ".a3d-tl-st{border-radius:8px;padding:6px 9px;font-weight:600;font-size:12.5px;background:rgba(46,160,67,.14);color:#7ee2a0}\n"
    ".a3d-tl-st span{font-weight:400;color:#aeb7c1;margin-left:4px}\n"
    ".a3d-tl-st.warn{background:rgba(210,153,34,.16);color:#f0b35a}.a3d-tl-st.fail{background:rgba(229,72,77,.16);color:#ff8b8b}\n"
    ".a3d-tl-msgs{margin:6px 0 4px;padding-left:18px;font-size:11.5px;color:#aeb7c1}\n"
    ".a3d-tl-m.warn{color:#f0b35a}.a3d-tl-m.err{color:#ff8b8b}\n"
    ".a3d-tl-stats{margin:6px 0}\n"
    ".a3d-tl-lay{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:6px 0;font-size:12px}\n"
    ".a3d-tl-hist{display:flex;flex-direction:column;gap:4px}\n"
    ".a3d-tl-h{display:flex;flex-direction:column;gap:4px;border-left:3px solid #2ea043;padding:3px 0 3px 8px}\n"
    ".a3d-tl-h.warn{border-left-color:#d29922}.a3d-tl-h.fail{border-left-color:#e5484d}\n"
    ".a3d-tl-hn{display:flex;flex-direction:column}.a3d-tl-hn span{font-size:11.5px;color:#8a96a3}\n"
    ".a3d-tl-ha{display:flex;gap:6px;flex-wrap:wrap}\n"
    "@media(pointer:coarse){.a3d-tl input[type=text],.a3d-tl select{min-height:36px;font-size:16px}.a3d-tl-b input[type=checkbox]{width:22px;height:22px}}\n"
    "body.light-theme .a3d-tl-l{color:#2a2e33}\n"
    "body.light-theme .a3d-tl input[type=text],body.light-theme .a3d-tl select{background:#fff;border-color:#c9ced4;color:#1f2328}\n"
    "body.light-theme .a3d-tl-crit{border-color:rgba(0,0,0,.12)}\n"
    "body.light-theme .a3d-tl-msg.err,body.light-theme .a3d-tl-m.err{color:#b42318}body.light-theme .a3d-tl-msg.warn,body.light-theme .a3d-tl-m.warn{color:#9a5b00}\n"
    "body.light-theme .a3d-tl-st{background:rgba(46,160,67,.12);color:#1a7f37}body.light-theme .a3d-tl-st span{color:#57606a}\n"
    "body.light-theme .a3d-tl-st.warn{background:rgba(210,153,34,.14);color:#9a5b00}body.light-theme .a3d-tl-st.fail{background:rgba(229,72,77,.12);color:#b42318}\n"
    "body.light-theme .a3d-tl-msgs,body.light-theme .a3d-tl-hn span,body.light-theme .a3d-tl-help,body.light-theme .a3d-tl-u{color:#57606a}\n")

LAY.write_text(lay, encoding='utf-8')
done()
