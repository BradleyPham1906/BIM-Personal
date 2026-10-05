"""patch_phase159b.py -- V159: Site analysis inside Analyze; the Climate and risk board.

1. The owner: "why this site analysis separate from 'analyze' on the left panel? they should be
   together". The Site tab leaves the rail. Analyze opens with a switch, Analyses | Site analysis;
   the view is remembered in this browser. SITEANALYSIS opens Analyze on Site analysis.
2. The board (reference/research-climate-risk-presentation.md), opened from Site analysis or with
   CLIMATE, in reading order:
   - a header: the site, its coordinates, its Koppen zone, the period, the sources;
   - an indicator strip: each a number, what it means, and a state (icon and word) where a
     reference exists;
   - ten figures, each with a numbered caption, a title that states the finding, the chart, its
     source and a table;
   - notes on method.
   The charts follow one set of rules: one y-axis, hairline grids, thin marks, one hue for
   magnitude, a diverging pair with a grey midpoint for temperature around comfort, validated
   categorical colours, a legend for two or more series, text in ink, hover on every mark, and a
   table for every chart. It follows the app's theme, and prints on A3 landscape on white."""
NAME = 'patch_phase159b.py'
BASE = 'ae7d187beb9512ebc74a1ff4dbef6f89fea0303970cd62c472f2ff72ae1d3013'
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


# ================= 1. Site analysis inside Analyze =================
rep("""      '<button type="button" class="a3d-railbtn" data-tab="site" data-short="Site" title="Site analysis" aria-label="Site analysis">'+   /* __acad3dV158 */
      bimRailIcon('site')+'</button>'+
""", "")
rep("""    {sel:'.a3d-railbtn[data-tab="site"]',why:'Site analysis tab: the standard process, the ten categories and every finding'},   /* __acad3dV158 */
""", """    {sel:'[data-anzview]',why:'Analyze: the switch between the analyses and the site analysis'},   /* __acad3dV159 */
    {sel:'[data-sastage]',why:'Site analysis: the stage the project is at'},
    {sel:'[data-satog]',why:'Site analysis: a category opens and closes'},
    {sel:'[data-saact]',why:'Site analysis: fill, add, edit, pin, photograph, delete; climate and risk'},
    {sel:'[data-saf]',why:'Site analysis: the project type, the questions, the pins switch'},
    {sel:'[data-saff]',why:'Site analysis: a field of a finding'},
    {sel:'[data-sachk]',why:'Site analysis: a checklist item'},
    {sel:'[data-saphoto]',why:'Site analysis: the photograph of a finding'},
""")
rep("""#a3d-shell[data-tab="site"] .a3d-projhead{flex-shrink:0}
#a3d-shell[data-tab="site"] .a3d-sa-wrap{flex:1 1 auto;min-height:0;display:flex;flex-direction:column}""",
    """#a3d-shell[data-tab="analyze"] .a3d-sa-wrap{flex:1 1 auto;min-height:0;display:flex;flex-direction:column}   /* __acad3dV159: in Analyze */
.a3d-anzview{display:flex;gap:2px;padding:2px;margin:0 0 10px;border-radius:8px;background:rgba(255,255,255,.06)}
.a3d-anzviewbtn{flex:1 1 0;border:0;border-radius:6px;background:transparent;color:#aab4bf;font:inherit;font-size:12px;font-weight:500;min-height:28px;cursor:pointer;padding:0 8px;white-space:nowrap}
.a3d-anzviewbtn:hover{color:#fff}
.a3d-anzviewbtn[aria-selected="true"]{background:#2f3540;color:#fff;box-shadow:0 1px 2px rgba(0,0,0,.35)}
.a3d-anzviewbtn:focus-visible{outline:2px solid #4ea1ff;outline-offset:-2px}
@media(pointer:coarse){.a3d-anzviewbtn{min-height:38px;font-size:13px}}
body.light-theme .a3d-anzview{background:rgba(0,0,0,.06)}
body.light-theme .a3d-anzviewbtn{color:#555}
body.light-theme .a3d-anzviewbtn[aria-selected="true"]{background:#fff;color:#111;box-shadow:0 1px 2px rgba(0,0,0,.15)}""")
rep("""  var A3D_ANZ={lod:null,open:bimAnzOpenLoad(),q:''};   /* __acad3dV148: the rows open, and the search */""",
    """  var A3D_ANZ={lod:null,open:bimAnzOpenLoad(),q:'',view:(function(){try{return localStorage.getItem('acad3dAnzView')==='site'?'site':'analyses';}catch(eV){return 'analyses';}})()};   /* __acad3dV148: the rows open, and the search; __acad3dV159: the view */
  /* __acad3dV159: Analyses | Site analysis, the switch at the top of the Analyze tab */
  function bimAnzViewHtml(){
    var v=A3D_ANZ.view;
    return '<div class="a3d-anzview" role="tablist" aria-label="Analyze">'+
      '<button type="button" role="tab" class="a3d-anzviewbtn" data-anzview="analyses" aria-selected="'+(v!=='site')+'">Analyses</button>'+
      '<button type="button" role="tab" class="a3d-anzviewbtn" data-anzview="site" aria-selected="'+(v==='site')+'">Site analysis</button></div>';
  }
  function bimAnzView(v){
    v=v==='site'?'site':'analyses';
    A3D_ANZ.view=v;
    try{localStorage.setItem('acad3dAnzView',v);}catch(eS){}
    var p=document.getElementById('a3d-leftpanel'),w;
    if(p){w=p.querySelector('.a3d-analyze-wrap');if(w)w.parentNode.removeChild(w);w=p.querySelector('.a3d-sa-wrap');if(w)w.parentNode.removeChild(w);}
    bimShellSetTab('analyze');
    var b=p&&p.querySelector('[data-anzview="'+v+'"]');
    return !!b;
  }""")
rep("""    return '<div class="a3d-anz"><div class="a3d-anzhead"><span class="a3d-anzttl0">Analyze</span>""",
    """    return '<div class="a3d-anz">'+bimAnzViewHtml()+'<div class="a3d-anzhead"><span class="a3d-anzttl0">Analyses</span>""")
rep("""    var h='<div class="a3d-anz a3d-sa"><div class="a3d-anzhead"><span class="a3d-anzttl0">Site analysis</span>""",
    """    var h='<div class="a3d-anz a3d-sa">'+bimAnzViewHtml()+'<div class="a3d-anzhead"><span class="a3d-anzttl0">Site analysis</span>""")
rep("""    if(shell.dataset.tab==='analyze'&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141 */""",
    """    var saView=shell.dataset.tab==='analyze'&&A3D_ANZ.view==='site';   /* __acad3dV159: one of Analyze's two views */
    if(shell.dataset.tab==='analyze'&&!saView&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141 */""")
rep("""      abox.addEventListener('click',function(ev){
        var tg=ev.target&&ev.target.closest?ev.target.closest('[data-anztog]'):null;   /* __acad3dV148: a row opens and closes */""",
    """      abox.addEventListener('click',function(ev){
        var vw=ev.target&&ev.target.closest?ev.target.closest('[data-anzview]'):null;   /* __acad3dV159 */
        if(vw){bimAnzView(vw.getAttribute('data-anzview'));return;}
        var tg=ev.target&&ev.target.closest?ev.target.closest('[data-anztog]'):null;   /* __acad3dV148: a row opens and closes */""")
rep("""    if(shell.dataset.tab!=='analyze'){
      var astale=panel.querySelector('.a3d-analyze-wrap');""",
    """    if(shell.dataset.tab!=='analyze'||saView){
      var astale=panel.querySelector('.a3d-analyze-wrap');""")
rep("""    if(shell.dataset.tab==='site'&&!panel.querySelector('.a3d-sa-wrap')){   /* __acad3dV158 */""",
    """    if(saView&&!panel.querySelector('.a3d-sa-wrap')){   /* __acad3dV158; __acad3dV159: inside Analyze */""")
rep("""    if(shell.dataset.tab!=='site'){
      var sstale=panel.querySelector('.a3d-sa-wrap');""",
    """    if(!saView){
      var sstale=panel.querySelector('.a3d-sa-wrap');""")
rep("""    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='site'?sh.querySelector('.a3d-sa-wrap'):null;""",
    """    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='analyze'?sh.querySelector('.a3d-sa-wrap'):null;   /* __acad3dV159 */""")
rep("""      b=t.closest('[data-sastage]');if(b){bimSaSetDefine('stage',b.getAttribute('data-sastage'));return;}""",
    """      b=t.closest('[data-anzview]');if(b){bimAnzView(b.getAttribute('data-anzview'));return;}   /* __acad3dV159 */
      b=t.closest('[data-sastage]');if(b){bimSaSetDefine('stage',b.getAttribute('data-sastage'));return;}""")
rep("""    siteanalysis:function(){bimShellSetTab('site');},            /* __acad3dV158 */
    safill:function(){bimShellSetTab('site');bimSaFill();},""",
    """    siteanalysis:function(){bimAnzView('site');},                /* __acad3dV158; __acad3dV159: in Analyze */
    safill:function(){bimAnzView('site');bimSaFill();},
    climate:function(){bimClbOpen();},                           /* __acad3dV159 */""")
rep("""    ['SITEANALYSIS',['SA','SITEAN','SITEPROCESS'],'siteanalysis','The Site analysis tab: the standard process, ten categories, findings with their sources, on the plan'],   /* __acad3dV158 */""",
    """    ['SITEANALYSIS',['SA','SITEAN','SITEPROCESS'],'siteanalysis','Site analysis, in the Analyze tab: the standard process, ten categories, findings with their sources, on the plan'],   /* __acad3dV158; __acad3dV159 */
    ['CLIMATE',['CLIMATEBOARD','CLIMATEANALYSIS','WINDROSE','PSYCHROMETRIC','DEGREEDAYS','SEISMIC','AIRQUALITY'],'climate','The Climate and risk board: temperature, rain, hourly heat map, wind rose, sun path, degree days, solar, psychrometric comfort, air quality, earthquakes'],""")

# ---- the Site analysis view: a Climate and risk section ----
rep("""      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="fill" title="Location, context, property, terrain, sun, access: what the model knows, with its sources">Fill from the model</button>'+""",
    """      bimClbSaHtml()+   /* __acad3dV159 */
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="fill" title="Location, context, property, terrain, sun, access: what the model knows, with its sources">Fill from the model</button>'+""")
rep("""    if(c==='fill')return bimSaFill();""",
    """    if(c==='fill')return bimSaFill();
    if(c==='climget')return bimClimFetch();   /* __acad3dV159 */
    if(c==='climboard')return bimClbOpen();""")

CSS = r"""
/* ================= __acad3dV159: the Climate and risk board =================
   Tokens per the data-viz reference palette (validated: categorical first three all-pairs, the
   wind ramp ordinal in both modes). Dark by default with the app; light with body.light-theme;
   white in print. */
.a3d-clsec{margin:4px 0 10px;padding:9px 10px;border-radius:8px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}
.a3d-clsec .a3d-sasechd{margin-bottom:4px}
.a3d-clsum{font-size:12px;color:#c9d1d9;line-height:1.45;margin:0 0 6px}
body.light-theme .a3d-clsec{background:rgba(0,0,0,.03);border-color:rgba(0,0,0,.08)}
body.light-theme .a3d-clsum{color:#333}
.a3d-clb{--surf:#1a1a19;--page:#0d0d0d;--ink:#ffffff;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--base:#383835;--ring:rgba(255,255,255,.10);
  --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--band:rgba(255,255,255,.08);
  --w1:#1c5cab;--w2:#2a78d6;--w3:#5598e7;--w4:#86b6ef;--w5:#cde2fb;--hn:#77766f;
  --good:#0ca30c;--warning:#fab219;--serious:#ec835a;--critical:#d03b3b;
  position:fixed;inset:0;z-index:20000;background:var(--page);color:var(--ink);overflow:auto;-webkit-overflow-scrolling:touch;
  font:13px/1.45 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:dark}
body.light-theme .a3d-clb{--surf:#fcfcfb;--page:#f1f0ec;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--base:#c3c2b7;--ring:rgba(11,11,11,.10);
  --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--band:rgba(11,11,11,.07);
  --w1:#86b6ef;--w2:#5598e7;--w3:#2a78d6;--w4:#1c5cab;--w5:#104281;--hn:#e7e5df;color-scheme:light}
.a3d-clb-bar{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:8px;padding:8px max(16px,env(safe-area-inset-right)) 8px max(16px,env(safe-area-inset-left));
  background:var(--page);border-bottom:1px solid var(--ring)}
.a3d-clb-bart{flex:1 1 auto;min-width:0;font-weight:600;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.a3d-clb-btn{flex:0 0 auto;border:1px solid var(--ring);background:var(--surf);color:var(--ink);border-radius:7px;font:inherit;font-size:12.5px;min-height:30px;padding:0 11px;cursor:pointer}
.a3d-clb-btn:hover{border-color:var(--muted)}
.a3d-clb-btn[aria-pressed="true"]{background:var(--ink);color:var(--surf)}
.a3d-clb-btn.pri{background:var(--s1);border-color:var(--s1);color:#fff}
.a3d-clb-btn:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.a3d-clb-page{max-width:1440px;margin:0 auto;padding:22px max(16px,env(safe-area-inset-right)) 40px max(16px,env(safe-area-inset-left));box-sizing:border-box}
.a3d-clb-kicker{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
.a3d-clb-h1{font-size:26px;line-height:1.2;font-weight:650;margin:4px 0 6px;letter-spacing:-.01em}
.a3d-clb-sub{color:var(--ink2);margin:0 0 18px;font-size:13px}
.a3d-clb-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:0 0 16px}
@media(min-width:1240px){.a3d-clb-kpis{grid-template-columns:repeat(var(--n,9),minmax(0,1fr))}}
.a3d-clb-kpi{background:var(--surf);border:1px solid var(--ring);border-radius:10px;padding:11px 12px 12px;min-width:0}
.a3d-clb-kl{font-size:11.5px;color:var(--ink2);margin:0 0 4px}
.a3d-clb-kv{font-size:24px;font-weight:650;line-height:1.15;letter-spacing:-.01em;overflow-wrap:anywhere}
.a3d-clb-ku{font-size:12px;font-weight:500;color:var(--ink2);margin-left:3px}
.a3d-clb-km{font-size:11.5px;color:var(--ink2);margin-top:4px;line-height:1.35}
.a3d-clb-st{display:inline-flex;align-items:center;gap:5px;margin-top:7px;font-size:11.5px;font-weight:600;color:var(--ink)}
.a3d-clb-st svg{width:14px;height:14px;flex:none}
.a3d-clb-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:12px}
.a3d-clb-card{grid-column:span 12;background:var(--surf);border:1px solid var(--ring);border-radius:12px;padding:14px 16px 12px;margin:0;min-width:0;break-inside:avoid}
.a3d-clb-card.s4{grid-column:span 4}.a3d-clb-card.s5{grid-column:span 5}.a3d-clb-card.s6{grid-column:span 6}.a3d-clb-card.s7{grid-column:span 7}
.a3d-clb-fno{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
.a3d-clb-h2{font-size:15.5px;line-height:1.3;font-weight:620;margin:3px 0 3px}
.a3d-clb-dek{color:var(--ink2);font-size:12.5px;margin:0 0 8px}
.a3d-clb-chart svg{display:block;width:100%;height:auto;overflow:visible}
.a3d-clb-row{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start}
.a3d-clb-row>*{flex:1 1 0;min-width:0}
.a3d-clb-legend{display:flex;flex-wrap:wrap;gap:4px 14px;margin:6px 0 2px;font-size:11.5px;color:var(--ink2)}
.a3d-clb-legend span{display:inline-flex;align-items:center;gap:6px}
.a3d-clb-legend i{display:inline-block;width:12px;height:12px;border-radius:3px;flex:none}
.a3d-clb-legend i.ln{height:2px;width:14px;border-radius:1px}
.a3d-clb-legend i.dsh{height:0;width:14px;border-top:1.5px dashed var(--ink2);border-radius:0}
.a3d-clb-src{font-size:11px;color:var(--muted);margin:8px 0 0}
.a3d-clb-empty{padding:22px 4px;color:var(--ink2)}
.a3d-clb-table{display:none;width:100%;border-collapse:collapse;margin:10px 0 2px;font-size:11.5px;font-variant-numeric:tabular-nums}
.a3d-clb.tables .a3d-clb-table{display:table}
.a3d-clb-table th,.a3d-clb-table td{padding:3px 6px;border-bottom:1px solid var(--grid);text-align:right;white-space:nowrap}
.a3d-clb-table th:first-child,.a3d-clb-table td:first-child{text-align:left}
.a3d-clb-table th{color:var(--ink2);font-weight:600}
.a3d-clb-tw{overflow-x:auto}
.a3d-clb-eqt{width:100%;border-collapse:collapse;font-size:11.5px;font-variant-numeric:tabular-nums}
.a3d-clb-eqt th,.a3d-clb-eqt td{padding:4px 6px;border-bottom:1px solid var(--grid);text-align:right;white-space:nowrap}
.a3d-clb-eqt th:first-child,.a3d-clb-eqt td:first-child,.a3d-clb-eqt td.pl{text-align:left}
.a3d-clb-eqt td.pl{white-space:normal;color:var(--ink2)}
.a3d-clb-eqt th{color:var(--ink2);font-weight:600}
.a3d-clb-notes{margin:16px 0 0;background:var(--surf);border:1px solid var(--ring);border-radius:12px;padding:14px 16px;font-size:12px;color:var(--ink2)}
.a3d-clb-notes h3{font-size:13px;color:var(--ink);margin:0 0 6px;font-weight:620}
.a3d-clb-notes ul{margin:0 0 8px;padding-left:18px}
.a3d-clb-notes li{margin:2px 0}
.a3d-clb-notes a{color:var(--s1)}
.a3d-clb-tip{position:fixed;z-index:20001;pointer-events:none;max-width:260px;background:var(--surf);color:var(--ink);border:1px solid var(--ring);border-radius:8px;
  box-shadow:0 6px 22px rgba(0,0,0,.28);padding:7px 9px;font-size:12px;line-height:1.4}
.a3d-clb-tip b{font-weight:650}
.a3d-clb-tip .tl{color:var(--ink2)}
.a3d-clb svg text{font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.a3d-clb .tk{fill:var(--muted);font-size:11px}
.a3d-clb .tl2{fill:var(--ink2);font-size:11px}
.a3d-clb .lb{fill:var(--ink);font-size:11.5px;font-weight:600;paint-order:stroke;stroke:var(--surf);stroke-width:3px;stroke-linejoin:round}
.a3d-clb .tl2,.a3d-clb .tk{paint-order:stroke;stroke:var(--surf);stroke-width:2.5px;stroke-linejoin:round}
.a3d-clb .gd{stroke:var(--grid);stroke-width:1;fill:none}
.a3d-clb .bs{stroke:var(--base);stroke-width:1;fill:none}
.a3d-clb .hit{fill:transparent;cursor:crosshair}
.a3d-clb .hit:hover,.a3d-clb .hit:focus{fill:var(--band);outline:none}
.a3d-clb .mk:hover,.a3d-clb .mk:focus{opacity:.8;outline:none}
@media(max-width:1100px){.a3d-clb-card.s4,.a3d-clb-card.s5,.a3d-clb-card.s6,.a3d-clb-card.s7{grid-column:span 6}.a3d-clb-card.wide{grid-column:span 12}}
@media(max-width:760px){.a3d-clb-card.s4,.a3d-clb-card.s5,.a3d-clb-card.s6,.a3d-clb-card.s7{grid-column:span 12}.a3d-clb-h1{font-size:21px}
  .a3d-clb-heat{overflow-x:auto;-webkit-overflow-scrolling:touch}.a3d-clb-heat svg{min-width:880px}
  .a3d-clb-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.a3d-clb-kv{font-size:20px}.a3d-clb-btn{min-height:38px}.a3d-clb-bar .a3d-clb-hide-s{display:none}}
@media print{
  body.a3d-clb-open>*:not(.a3d-clb){display:none!important}
  body.a3d-clb-open .a3d-clb{position:static;overflow:visible;background:#fff;
    --surf:#fff;--page:#fff;--ink:#0b0b0b;--ink2:#52514e;--muted:#6f6d68;--grid:#e1e0d9;--base:#c3c2b7;--ring:rgba(11,11,11,.14);
    --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--band:rgba(11,11,11,.07);
    --w1:#86b6ef;--w2:#5598e7;--w3:#2a78d6;--w4:#1c5cab;--w5:#104281;--hn:#e7e5df;color-scheme:light}
  .a3d-clb-bar,.a3d-clb-tip{display:none!important}
  .a3d-clb-page{max-width:none;padding:0}
  .a3d-clb-card,.a3d-clb-kpi,.a3d-clb-notes{break-inside:avoid;page-break-inside:avoid}
  @page{size:A3 landscape;margin:10mm}
}"""
rep(""".a3d-anzview{display:flex;""", CSS.lstrip('\n') + "\n.a3d-anzview{display:flex;")

BOARD = r"""
  /* ================= __acad3dV159: the Climate and risk board =================
     reference/research-climate-risk-presentation.md. Each chart is an SVG string drawn from what
     A3D.site.climate and A3D.site.risk keep; its colours are CSS tokens, so it follows the theme. */
  var BIM_HEAT_EDGES=[-10,0,8,14,20,24,27,30,33,36];
  var BIM_HEAT_NAMES=['Below −10 °C: extreme cold','−10 to 0: freezing','0 to 8: cold','8 to 14: cool','14 to 20: mild','20 to 24: comfortable','24 to 27: warm','27 to 30: hot','30 to 33: very hot','33 to 36: extremely hot','Above 36: dangerous heat'];
  var BIM_HEAT_SHORT=['< −10','−10–0','0–8','8–14','14–20','20–24','24–27','27–30','30–33','33–36','> 36'];
  var BIM_HEAT_COL=['#104281','#1c5cab','#2a78d6','#6da7ec','#b7d3f6','var(--hn)','#f6c2bd','#ec8f86','#e34948','#b8302f','#7d1f1f'];
  var BIM_STATE={good:['Good','var(--good)','<path d="M3.5 8.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'],
    warning:['Watch','var(--warning)','<path d="M8 3.5v5.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="8" cy="12" r="1.2" fill="currentColor"/>'],
    serious:['Serious','var(--serious)','<path d="M8 3 14 13H2z" fill="currentColor"/>'],
    critical:['Critical','var(--critical)','<path d="M4.5 4.5l7 7M11.5 4.5l-7 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>']};
  var A3D_CLB={open:false,tables:false,narrow:false};
  window.addEventListener('resize',function(){if(A3D_CLB.open&&(window.innerWidth<760)!==A3D_CLB.narrow)bimClbOpen();});
  /* Esc shuts the board wherever the focus is, before the app's own keys see it */
  document.addEventListener('keydown',function(ev){if(A3D_CLB.open&&ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimClbClose();}},true);
  function bimClbE(s){return bimEsc(String(s==null?'':s));}
  function bimClbTip(t){return ' data-tip="'+bimClbE(t)+'" tabindex="0"';}
  /* clean ticks: about n of them over lo..hi, steps of 1, 2, 2.5 or 5 times a power of ten */
  function bimClbTicks(lo,hi,n){
    if(!(hi>lo)){hi=lo+1;}
    var raw=(hi-lo)/Math.max(1,n||5),p=Math.pow(10,Math.floor(Math.log(raw)/Math.LN10)),f=raw/p,st=(f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10)*p;
    var a=Math.floor(lo/st)*st,b=Math.ceil(hi/st)*st,T=[],v;
    for(v=a;v<=b+st*1e-6;v+=st)T.push(Math.round(v*1e6)/1e6);
    return T;
  }
  function bimClbNum(v,d){return bimClimFmt(v,d===undefined?1:d);}
  function bimClbBar(x,y0,w,y1,r){   /* a column from the baseline y0 to y1, its data end rounded */
    var up=y1<y0,h=Math.abs(y1-y0);r=Math.min(r,w/2,h);
    if(h<0.5)return '';
    if(up)return 'M'+x+' '+y0+'V'+(y1+r)+'Q'+x+' '+y1+' '+(x+r)+' '+y1+'H'+(x+w-r)+'Q'+(x+w)+' '+y1+' '+(x+w)+' '+(y1+r)+'V'+y0+'Z';
    return 'M'+x+' '+y0+'V'+(y1-r)+'Q'+x+' '+y1+' '+(x+r)+' '+y1+'H'+(x+w-r)+'Q'+(x+w)+' '+y1+' '+(x+w)+' '+(y1-r)+'V'+y0+'Z';
  }
  function bimClbF(v){return Math.round(v*10)/10;}
  function bimClbAxisY(T,y,L,R,fmt){
    return T.map(function(v){var yy=bimClbF(y(v));return '<line class="gd" x1="'+L+'" x2="'+R+'" y1="'+yy+'" y2="'+yy+'"/><text class="tk" x="'+(L-6)+'" y="'+(yy+3.5)+'" text-anchor="end">'+bimClbE(fmt?fmt(v):v)+'</text>';}).join('');
  }
  function bimClbMonthsX(x,yb){return BIM_CLIM_MONTHS.map(function(m,i){return '<text class="tk" x="'+bimClbF(x(i))+'" y="'+yb+'" text-anchor="middle">'+(A3D_CLB.narrow?m.charAt(0):m)+'</text>';}).join('');}
  function bimClbTable(head,rows){
    return '<div class="a3d-clb-tw"><table class="a3d-clb-table"><thead><tr>'+head.map(function(h){return '<th>'+bimClbE(h)+'</th>';}).join('')+'</tr></thead><tbody>'+
      rows.map(function(r){return '<tr>'+r.map(function(c){return '<td>'+bimClbE(c)+'</td>';}).join('')+'</tr>';}).join('')+'</tbody></table></div>';
  }
  function bimClbCard(cls,no,title,dek,body,src){
    return '<figure class="a3d-clb-card '+(Array.isArray(cls)?cls.join(' '):cls)+'" data-fig="'+no+'"><figcaption><div class="a3d-clb-fno">Fig. '+no+'</div><h2 class="a3d-clb-h2">'+bimClbE(title)+'</h2>'+
      (dek?'<p class="a3d-clb-dek">'+bimClbE(dek)+'</p>':'')+'</figcaption>'+body+(src?'<p class="a3d-clb-src">Source: '+bimClbE(src)+'</p>':'')+'</figure>';
  }
  function bimClbIdx(M,k,f){var b=0,i;for(i=1;i<M.length;i++)if(f==='min'?M[i][k]<M[b][k]:M[i][k]>M[b][k])b=i;return b;}
  /* Fig. 1: temperature, the band of real days, the mean high and low */
  function bimClbTempSvg(M){
    var W=A3D_CLB.narrow?360:640,H=A3D_CLB.narrow?220:236,L=A3D_CLB.narrow?34:40,R=W-(A3D_CLB.narrow?8:14),T0=14,B=H-22,bw=(R-L)/12;   /* drawn for the screen: a phone's narrower */
    var lo=Math.min.apply(null,M.map(function(m){return m.tn10;})),hi=Math.max.apply(null,M.map(function(m){return m.tx90;}));
    var Tk=bimClbTicks(lo-1,hi+1,5),y0=Tk[0],y1=Tk[Tk.length-1];
    function x(i){return L+(i+0.5)*bw;}function y(v){return B-(v-y0)/(y1-y0)*(B-T0);}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Monthly temperature">'+bimClbAxisY(Tk,y,L,R,function(v){return bimClbNum(v,0)+'°';});
    if(y0<0&&y1>0)s+='<line class="bs" x1="'+L+'" x2="'+R+'" y1="'+bimClbF(y(0))+'" y2="'+bimClbF(y(0))+'"/>';
    var band=M.map(function(m,i){return bimClbF(x(i))+','+bimClbF(y(m.tx90));}).concat(M.slice().reverse().map(function(m,j){return bimClbF(x(11-j))+','+bimClbF(y(m.tn10));}));
    s+='<polygon points="'+band.join(' ')+'" fill="var(--band)"/>';
    s+='<polyline points="'+M.map(function(m,i){return bimClbF(x(i))+','+bimClbF(y(m.tx));}).join(' ')+'" fill="none" stroke="var(--s2)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>';
    s+='<polyline points="'+M.map(function(m,i){return bimClbF(x(i))+','+bimClbF(y(m.tn));}).join(' ')+'" fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>';
    var ih=bimClbIdx(M,'tx','max'),il=bimClbIdx(M,'tn','min');
    s+='<circle cx="'+bimClbF(x(ih))+'" cy="'+bimClbF(y(M[ih].tx))+'" r="4" fill="var(--s2)" stroke="var(--surf)" stroke-width="2"/>'+
      '<text class="lb" x="'+bimClbF(x(ih))+'" y="'+bimClbF(y(M[ih].tx)-9)+'" text-anchor="middle">'+bimClbNum(M[ih].tx)+'°</text>';
    s+='<circle cx="'+bimClbF(x(il))+'" cy="'+bimClbF(y(M[il].tn))+'" r="4" fill="var(--s1)" stroke="var(--surf)" stroke-width="2"/>'+
      '<text class="lb" x="'+bimClbF(x(il))+'" y="'+bimClbF(y(M[il].tn)+17)+'" text-anchor="middle">'+bimClbNum(M[il].tn)+'°</text>';
    M.forEach(function(m,i){s+='<rect class="hit" x="'+bimClbF(L+i*bw)+'" y="'+T0+'" width="'+bimClbF(bw)+'" height="'+(B-T0)+'"'+
      bimClbTip(BIM_CLIM_MONTH_NAMES[i]+'|Mean high '+bimClbNum(m.tx)+' °C|Mean low '+bimClbNum(m.tn)+' °C|Mean '+bimClbNum(m.tm)+' °C|Hot days (90th) '+bimClbNum(m.tx90)+' °C|Cold nights (10th) '+bimClbNum(m.tn10)+' °C')+'/>';});
    return s+bimClbMonthsX(x,H-6)+'</svg>';
  }
  /* Fig. 2: rainfall by month, sharing Fig. 1's months */
  function bimClbRainSvg(M){
    var W=A3D_CLB.narrow?360:640,H=150,L=A3D_CLB.narrow?34:40,R=W-(A3D_CLB.narrow?8:14),T0=16,B=H-22,bw=(R-L)/12,mx=Math.max.apply(null,M.map(function(m){return m.p;}));
    var Tk=bimClbTicks(0,Math.max(10,mx),4),y1=Tk[Tk.length-1],cw=Math.min(24,bw*0.56);
    function y(v){return B-v/y1*(B-T0);}function x(i){return L+(i+0.5)*bw;}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Monthly rainfall">'+bimClbAxisY(Tk,y,L,R,function(v){return v;})+'<line class="bs" x1="'+L+'" x2="'+R+'" y1="'+B+'" y2="'+B+'"/>';
    var iw=bimClbIdx(M,'p','max');
    M.forEach(function(m,i){
      s+='<path class="mk" d="'+bimClbBar(bimClbF(x(i)-cw/2),B,bimClbF(cw),bimClbF(y(m.p)),4)+'" fill="var(--s1)"'+bimClbTip(BIM_CLIM_MONTH_NAMES[i]+'|'+Math.round(m.p)+' mm|'+bimClbNum(m.wet,0)+' wet days (1 mm or more)')+'/>';
    });
    s+='<text class="lb" x="'+bimClbF(x(iw))+'" y="'+bimClbF(y(M[iw].p)-6)+'" text-anchor="middle">'+Math.round(M[iw].p)+' mm</text>';
    return s+bimClbMonthsX(x,H-6)+'</svg>';
  }
  /* Fig. 3: a year of hours, the day across, the hour down, in named bands */
  function bimClbHeatClass(v){var k;for(k=0;k<BIM_HEAT_EDGES.length;k++)if(v<BIM_HEAT_EDGES[k])return k;return BIM_HEAT_EDGES.length;}
  function bimClbHeatSvg(Hh){
    var heat=Hh.heat,days=Math.floor(heat.length/24),W=1200,H=268,L=46,R=W-10,T0=8,B=H-24,cw=(R-L)/days,ch=(B-T0)/24,s,h,d,run,k0,k;
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Hourly temperature heat map" data-heat="1" data-l="'+L+'" data-t="'+T0+'" data-cw="'+cw+'" data-ch="'+ch+'" data-days="'+days+'">';
    for(h=0;h<24;h++){
      run=0;k0=null;
      for(d=0;d<=days;d++){
        var v=d<days?heat[d*24+h]:null;k=v===null||v===undefined?-1:bimClbHeatClass(v);
        if(d<days&&k===k0){run++;continue;}
        if(k0!==null&&k0>=0&&run>0)s+='<rect x="'+bimClbF(L+(d-run)*cw)+'" y="'+bimClbF(T0+h*ch)+'" width="'+bimClbF(run*cw+0.35)+'" height="'+bimClbF(ch+0.35)+'" fill="'+BIM_HEAT_COL[k0]+'"/>';
        k0=k;run=1;
      }
    }
    [0,6,12,18].forEach(function(hh){s+='<text class="tk" x="'+(L-6)+'" y="'+bimClbF(T0+hh*ch+ch/2+3.5)+'" text-anchor="end">'+(hh<10?'0':'')+hh+':00</text>';});
    var y=+String(Hh.start).slice(0,4),cum=0,DM=[31,(y%4===0&&(y%100!==0||y%400===0))?29:28,31,30,31,30,31,31,30,31,30,31];
    BIM_CLIM_MONTHS.forEach(function(m,i){
      s+='<line class="bs" x1="'+bimClbF(L+cum*cw)+'" x2="'+bimClbF(L+cum*cw)+'" y1="'+B+'" y2="'+(B+4)+'"/><text class="tk" x="'+bimClbF(L+(cum+DM[i]/2)*cw)+'" y="'+(H-6)+'" text-anchor="middle">'+m+'</text>';
      cum+=DM[i];
    });
    return s+'<rect class="hit" x="'+L+'" y="'+T0+'" width="'+(R-L)+'" height="'+(B-T0)+'" data-heathit="1"/></svg>';
  }
  /* Figs. 4: the wind rose, 16 sectors, stacked speed bands, frequency rings */
  function bimClbWedge(cx,cy,r1,r2,a1,a2){
    function p(r,a){var t=a*Math.PI/180;return bimClbF(cx+r*Math.sin(t))+' '+bimClbF(cy-r*Math.cos(t));}
    return 'M'+p(r1,a1)+'L'+p(r2,a1)+'A'+r2+' '+r2+' 0 0 1 '+p(r2,a2)+'L'+p(r1,a2)+(r1>0?'A'+r1+' '+r1+' 0 0 0 '+p(r1,a1):'')+'Z';
  }
  function bimClbRoseSvg(Wd,small,label){
    var S=small?190:400,cx=S/2,cy=S/2,R=small?72:150,r0=small?7:15,nb=Wd.pct[0].length,mx=0,k,j,s;
    for(k=0;k<16;k++){var tt=0;for(j=0;j<nb;j++)tt+=Wd.pct[k][j];if(tt>mx)mx=tt;}
    var rt=bimClbTicks(0,Math.max(mx,1),small?2:4),rm=rt[rt.length-1];
    function rr(v){return r0+v/rm*(R-r0);}
    s='<svg viewBox="0 0 '+S+' '+S+'" role="img" aria-label="'+bimClbE(label||'Wind rose')+'">';
    rt.forEach(function(v){if(v>0)s+='<circle class="gd" cx="'+cx+'" cy="'+cy+'" r="'+bimClbF(rr(v))+'"/>';});
    for(k=0;k<16;k++)s+='<line class="gd" x1="'+bimClbF(cx+r0*Math.sin(k*Math.PI/8))+'" y1="'+bimClbF(cy-r0*Math.cos(k*Math.PI/8))+'" x2="'+bimClbF(cx+R*Math.sin(k*Math.PI/8))+'" y2="'+bimClbF(cy-R*Math.cos(k*Math.PI/8))+'"/>';
    for(k=0;k<16;k++){
      var a=k*22.5,cum=0;
      for(j=0;j<nb;j++){
        var v=Wd.pct[k][j];if(!(v>0))continue;
        s+='<path class="mk" d="'+bimClbWedge(cx,cy,rr(cum),rr(cum+v),a-9.2,a+9.2)+'" fill="var(--w'+(j+1)+')" stroke="var(--surf)" stroke-width="1.5"'+
          bimClbTip('From the '+BIM_CLIM_DIRS[k]+'|'+bimClbWindBand(j)+'|'+bimClbNum(v)+'% of hours')+'/>';
        cum+=v;
      }
    }
    s+='<circle cx="'+cx+'" cy="'+cy+'" r="'+r0+'" fill="var(--surf)" stroke="var(--grid)"/>';
    if(!small){
      s+='<text class="tk" x="'+cx+'" y="'+(cy+3.5)+'" text-anchor="middle">'+bimClbNum(Wd.calm,0)+'%</text>';
      rt.forEach(function(v){if(v>0)s+='<text class="tk" x="'+bimClbF(cx+rr(v)*Math.sin(Math.PI*3/8)+3)+'" y="'+bimClbF(cy-rr(v)*Math.cos(Math.PI*3/8)-3)+'">'+v+'%</text>';});
      ['N','NE','E','SE','S','SW','W','NW'].forEach(function(n,i){var t=i*Math.PI/4;
        s+='<text class="'+(i%2?'tk':'lb')+'" x="'+bimClbF(cx+(R+16)*Math.sin(t))+'" y="'+bimClbF(cy-(R+16)*Math.cos(t)+4)+'" text-anchor="middle">'+n+'</text>';});
    }else s+='<text class="lb" x="'+cx+'" y="'+(cy-R-8)+'" text-anchor="middle">N</text>';
    return s+'</svg>';
  }
  function bimClbWindBand(j){var b=BIM_CLIM_WIND_BINS;return j<b.length-1?b[j]+'–'+b[j+1]+' m/s':'≥ '+b[j]+' m/s';}
  /* Fig. 5: the sun path, stereographic, the centre overhead and the rim the horizon */
  function bimClbSunSvg(lat,lon,tz){
    var S=380,cx=190,cy=190,R=150,y=new Date().getFullYear(),s,k;
    function rad(alt){return R*Math.tan((90-Math.max(0,alt))*Math.PI/360);}
    function pt(alt,az){var t=az*Math.PI/180,r=rad(alt);return [cx+r*Math.sin(t),cy-r*Math.cos(t)];}
    s='<svg viewBox="0 0 '+S+' '+S+'" role="img" aria-label="Sun path">';
    [15,30,45,60,75].forEach(function(a){s+='<circle class="gd" cx="'+cx+'" cy="'+cy+'" r="'+bimClbF(rad(a))+'"/>';});
    s+='<circle class="bs" cx="'+cx+'" cy="'+cy+'" r="'+R+'"/>';
    for(k=0;k<24;k++){var t=k*15*Math.PI/180,o=k%6===0?10:5;
      s+='<line class="bs" x1="'+bimClbF(cx+R*Math.sin(t))+'" y1="'+bimClbF(cy-R*Math.cos(t))+'" x2="'+bimClbF(cx+(R+o)*Math.sin(t))+'" y2="'+bimClbF(cy-(R+o)*Math.cos(t))+'"/>';}
    ['N','E','S','W'].forEach(function(n,i){var t=i*Math.PI/2;s+='<text class="lb" x="'+bimClbF(cx+(R+22)*Math.sin(t))+'" y="'+bimClbF(cy-(R+22)*Math.cos(t)+4)+'" text-anchor="middle">'+n+'</text>';});
    [30,60].forEach(function(a){var p=pt(a,0);s+='<text class="tk" x="'+bimClbF(p[0]+3)+'" y="'+bimClbF(p[1]-3)+'">'+a+'°</text>';});
    var D=[['06-21','var(--s2)','21 June'],['03-20','var(--s3)','Equinox'],['12-21','var(--s1)','21 December']],out=[];
    D.forEach(function(dd){
      var P=[],hp=[],mx=0,m,r;
      for(m=0;m<=1440;m+=6){r=bimSunCalc(lat,lon,tz,y+'-'+dd[0],bimHHMM(m));if(r&&r.elevation>0){P.push(pt(r.elevation,r.azimuth));if(r.elevation>mx)mx=r.elevation;}}
      for(m=0;m<1440;m+=60){r=bimSunCalc(lat,lon,tz,y+'-'+dd[0],bimHHMM(m));if(r&&r.elevation>0)hp.push({h:m/60,p:pt(r.elevation,r.azimuth),alt:r.elevation,az:r.azimuth});}
      if(P.length>1)s+='<polyline points="'+P.map(function(q){return bimClbF(q[0])+','+bimClbF(q[1]);}).join(' ')+'" fill="none" stroke="'+dd[1]+'" stroke-width="2" stroke-linecap="round"/>';
      hp.forEach(function(q){s+='<circle class="mk" cx="'+bimClbF(q.p[0])+'" cy="'+bimClbF(q.p[1])+'" r="4" fill="'+dd[1]+'" stroke="var(--surf)" stroke-width="2"'+
        bimClbTip(dd[2]+', '+(q.h<10?'0':'')+q.h+':00|Altitude '+bimClbNum(q.alt,0)+'°|Azimuth '+bimClbNum(q.az,0)+'°')+'/>';});
      if(dd[0]==='06-21')hp.forEach(function(q){if(q.h%3===0){var vx=q.p[0]-cx,vy=q.p[1]-cy,l=Math.sqrt(vx*vx+vy*vy)||1;
        s+='<text class="tl2" x="'+bimClbF(q.p[0]+vx/l*13)+'" y="'+bimClbF(q.p[1]+vy/l*13+4)+'" text-anchor="middle">'+q.h+'h</text>';}});
      var r0=bimSunCalc(lat,lon,tz,y+'-'+dd[0],'12:00'),len=r0&&r0.sunrise!==null&&r0.sunset!==null?Math.round(r0.sunset-r0.sunrise):(r0&&r0.polar==='day'?1440:0);
      out.push({label:dd[2],col:dd[1],alt:mx,len:len});
    });
    return {svg:s+'<circle cx="'+cx+'" cy="'+cy+'" r="2.5" fill="var(--ink2)"/></svg>',days:out};
  }
  /* Fig. 6: degree days, cooling up and heating down from one baseline */
  function bimClbDdSvg(M){
    var W=A3D_CLB.narrow?360:440,H=230,L=40,R=W-10,T0=12,B=H-22,bw=(R-L)/12,mx=0;
    M.forEach(function(m){mx=Math.max(mx,m.hdd||0,m.cdd||0);});
    var Tk=bimClbTicks(0,Math.max(mx,10),3),tm=Tk[Tk.length-1],mid=(T0+B)/2,cw=Math.min(24,bw*0.56);
    function x(i){return L+(i+0.5)*bw;}function yu(v){return mid-v/tm*(mid-T0);}function yd(v){return mid+v/tm*(B-mid);}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Degree days by month">';
    Tk.forEach(function(v){if(v>0){s+='<line class="gd" x1="'+L+'" x2="'+R+'" y1="'+bimClbF(yu(v))+'" y2="'+bimClbF(yu(v))+'"/><text class="tk" x="'+(L-6)+'" y="'+bimClbF(yu(v)+3.5)+'" text-anchor="end">'+v+'</text>'+
      '<line class="gd" x1="'+L+'" x2="'+R+'" y1="'+bimClbF(yd(v))+'" y2="'+bimClbF(yd(v))+'"/><text class="tk" x="'+(L-6)+'" y="'+bimClbF(yd(v)+3.5)+'" text-anchor="end">'+v+'</text>';}});
    s+='<line class="bs" x1="'+L+'" x2="'+R+'" y1="'+mid+'" y2="'+mid+'"/>';
    M.forEach(function(m,i){
      s+='<path class="mk" d="'+bimClbBar(bimClbF(x(i)-cw/2),mid,bimClbF(cw),bimClbF(yu(m.cdd||0)),4)+'" fill="var(--s2)"'+bimClbTip(BIM_CLIM_MONTH_NAMES[i]+'|Cooling '+Math.round(m.cdd||0)+' degree days')+'/>';
      s+='<path class="mk" d="'+bimClbBar(bimClbF(x(i)-cw/2),mid,bimClbF(cw),bimClbF(yd(m.hdd||0)),4)+'" fill="var(--s1)"'+bimClbTip(BIM_CLIM_MONTH_NAMES[i]+'|Heating '+Math.round(m.hdd||0)+' degree days')+'/>';
    });
    return s+BIM_CLIM_MONTHS.map(function(m,i){return '<text class="tk" x="'+bimClbF(x(i))+'" y="'+(H-6)+'" text-anchor="middle">'+m.charAt(0)+'</text>';}).join('')+'</svg>';
  }
  /* Fig. 7: solar energy on the horizontal, by month */
  function bimClbSolarSvg(M){
    var W=A3D_CLB.narrow?360:440,H=230,L=40,R=W-10,T0=16,B=H-22,bw=(R-L)/12,mx=Math.max.apply(null,M.map(function(m){return m.sw||0;}));
    var Tk=bimClbTicks(0,Math.max(1,mx),4),y1=Tk[Tk.length-1],cw=Math.min(24,bw*0.56);
    function x(i){return L+(i+0.5)*bw;}function y(v){return B-v/y1*(B-T0);}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Solar energy by month">'+bimClbAxisY(Tk,y,L,R)+'<line class="bs" x1="'+L+'" x2="'+R+'" y1="'+B+'" y2="'+B+'"/>';
    var im=bimClbIdx(M,'sw','max');
    M.forEach(function(m,i){s+='<path class="mk" d="'+bimClbBar(bimClbF(x(i)-cw/2),B,bimClbF(cw),bimClbF(y(m.sw||0)),4)+'" fill="var(--s4)"'+
      bimClbTip(BIM_CLIM_MONTH_NAMES[i]+'|'+bimClbNum(m.sw,2)+' kWh/m² a day')+'/>';});
    s+='<text class="lb" x="'+bimClbF(x(im))+'" y="'+bimClbF(y(M[im].sw)-6)+'" text-anchor="middle">'+bimClbNum(M[im].sw)+'</text>';
    return s+BIM_CLIM_MONTHS.map(function(m,i){return '<text class="tk" x="'+bimClbF(x(i))+'" y="'+(H-6)+'" text-anchor="middle">'+m.charAt(0)+'</text>';}).join('')+'</svg>';
  }
  /* Fig. 8: the psychrometric chart, the year's hours as density, the comfort zone */
  function bimClbPsySvg(Hh){
    var W=A3D_CLB.narrow?380:620,H=A3D_CLB.narrow?340:360,L=42,R=W-(A3D_CLB.narrow?30:46),T0=10,B=H-30,keys=Object.keys(Hh.psy),tlo=1e9,thi=-1e9,whi=0,k,s;
    keys.forEach(function(q){var a=q.split('|'),t=+a[0],w=+a[1];if(t<tlo)tlo=t;if(t+1>thi)thi=t+1;if(w+1>whi)whi=w+1;});
    tlo=Math.max(-20,Math.min(tlo,BIM_CLIM_COMFORT.t0-5));thi=Math.min(50,Math.max(thi,BIM_CLIM_COMFORT.t1+5));
    var Tx=bimClbTicks(tlo,thi,8),x0=Tx[0],x1=Tx[Tx.length-1],Ty=bimClbTicks(0,Math.max(whi,16),5),wy=Ty[Ty.length-1];
    function x(v){return L+(v-x0)/(x1-x0)*(R-L);}function y(v){return B-v/wy*(B-T0);}
    s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Psychrometric chart">'+bimClbAxisY(Ty,y,L,R);
    Tx.forEach(function(v){s+='<text class="tk" x="'+bimClbF(x(v))+'" y="'+(B+16)+'" text-anchor="middle">'+bimClbNum(v,0)+'</text>';});
    s+='<text class="tl2" x="'+((L+R)/2)+'" y="'+(H-1)+'" text-anchor="middle">Dry-bulb temperature (°C)</text>';
    s+='<text class="tl2" x="12" y="'+((T0+B)/2)+'" text-anchor="middle" transform="rotate(-90 12 '+((T0+B)/2)+')">Humidity ratio (g/kg)</text>';
    function bin(n){return n>=100?5:n>=40?4:n>=15?3:n>=5?2:1;}
    keys.forEach(function(q){var a=q.split('|'),t=+a[0],w=+a[1],n=Hh.psy[q];
      if(t<x0||t+1>x1||w+1>wy)return;
      s+='<rect class="mk" x="'+bimClbF(x(t)+0.5)+'" y="'+bimClbF(y(w+1)+0.5)+'" width="'+bimClbF(x(t+1)-x(t)-1)+'" height="'+bimClbF(y(w)-y(w+1)-1)+'" fill="var(--w'+bin(n)+')"'+
        bimClbTip(t+' to '+(t+1)+' °C, '+w+' to '+(w+1)+' g/kg|'+n+' hour'+(n===1?'':'s'))+'/>';});
    for(k=10;k<=100;k+=10){
      var P=[],tt,last=null;
      for(tt=x0;tt<=x1+1e-6;tt+=0.5){var wv=bimHumRatio(tt,k);if(wv>wy){break;}P.push(bimClbF(x(tt))+','+bimClbF(y(wv)));last=[tt,wv];}
      if(P.length>1)s+='<polyline points="'+P.join(' ')+'" fill="none" stroke="'+(k===100?'var(--ink2)':'var(--grid)')+'" stroke-width="'+(k===100?1.5:1)+'"/>';
      if(last&&k%20===0&&!(A3D_CLB.narrow&&k===80))s+='<text class="tk" x="'+bimClbF(x(last[0])+4)+'" y="'+bimClbF(y(last[1])+3)+'">'+k+'%</text>';
    }
    var C=BIM_CLIM_COMFORT,Z=[];
    for(tt=C.t0;tt<=C.t1+1e-6;tt+=0.5)Z.push([tt,bimHumRatio(tt,C.rh0)]);
    for(tt=C.t1;tt>=C.t0-1e-6;tt-=0.5)Z.push([tt,bimHumRatio(tt,C.rh1)]);
    s+='<polygon points="'+Z.map(function(p){return bimClbF(x(p[0]))+','+bimClbF(y(p[1]));}).join(' ')+'" fill="none" stroke="var(--ink)" stroke-width="1.75" stroke-linejoin="round"/>';
    s+='<text class="lb" x="'+bimClbF(x(C.t0))+'" y="'+bimClbF(y(bimHumRatio(C.t0,C.rh1))-8)+'">Comfort zone'+(Hh.comfort&&!A3D_CLB.narrow?' · '+bimClbNum(Hh.comfort.inside,0)+'% of hours':'')+'</text>';
    return s+'</svg>';
  }
  /* Fig. 9: PM2.5 a day, against the WHO 24-hour guideline */
  function bimClbAirSvg(Q){
    var W=A3D_CLB.narrow?360:1200,H=230,L=34,R=W-10,T0=14,B=H-24,n=Q.days.length,bw=(R-L)/n,mx=Q.max?Q.max.v:0;
    var Tk=bimClbTicks(0,Math.max(mx,BIM_CLIM_WHO24*1.3),4),y1=Tk[Tk.length-1],cw=Math.max(1.5,Math.min(24,bw*0.7));
    function y(v){return B-v/y1*(B-T0);}
    var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Daily PM2.5">'+bimClbAxisY(Tk,y,L,R)+'<line class="bs" x1="'+L+'" x2="'+R+'" y1="'+B+'" y2="'+B+'"/>';
    Q.days.forEach(function(d,i){var over=d.v>BIM_CLIM_WHO24;
      s+='<path class="mk" d="'+bimClbBar(bimClbF(L+i*bw+(bw-cw)/2),B,bimClbF(cw),bimClbF(y(d.v)),Math.min(4,cw/2))+'" fill="'+(over?'var(--serious)':'var(--s1)')+'"'+
        bimClbTip(d.d+'|PM2.5 '+bimClbNum(d.v)+' µg/m³|'+(over?'Above':'Within')+' the WHO 24-hour guideline')+'/>';});
    [[BIM_CLIM_WHO24,'WHO 24-hour guideline, '+BIM_CLIM_WHO24],[25,'WHO interim target 4, 25'],[37.5,'Interim target 3, 37.5'],[50,'Interim target 2, 50'],[75,'Interim target 1, 75']].forEach(function(g,i){
      if(g[0]>y1)return;
      s+='<line x1="'+L+'" x2="'+R+'" y1="'+bimClbF(y(g[0]))+'" y2="'+bimClbF(y(g[0]))+'" stroke="'+(i?'var(--muted)':'var(--ink2)')+'" stroke-width="1" stroke-dasharray="5 4"/>'+
        '<text class="'+(i?'tk':'tl2')+'" x="'+(R-2)+'" y="'+bimClbF(y(g[0])-4)+'" text-anchor="end">'+bimClbE(g[1])+' µg/m³</text>';});
    var lastM='';
    Q.days.forEach(function(d,i){var m=d.d.slice(5,7);if(m!==lastM&&d.d.slice(8,10)<='07'){lastM=m;s+='<text class="tk" x="'+bimClbF(L+i*bw)+'" y="'+(H-6)+'">'+BIM_CLIM_MONTHS[+m-1]+'</text>';}});
    return s+'</svg>';
  }
  /* Fig. 10: earthquakes by distance and direction, sized by magnitude */
  function bimClbQuakeSvg(E){
    var S=340,cx=170,cy=170,R=140,s;
    function pr(km){return km/E.radius*R;}
    s='<svg viewBox="0 0 '+S+' '+S+'" role="img" aria-label="Earthquakes within '+E.radius+' km">';
    [25,50,75,100].forEach(function(km){if(km<=E.radius){s+='<circle class="'+(km===E.radius?'bs':'gd')+'" cx="'+cx+'" cy="'+cy+'" r="'+bimClbF(pr(km))+'"/>'+
      '<text class="tk" x="'+(cx+3)+'" y="'+bimClbF(cy-pr(km)-3)+'">'+km+' km</text>';}});
    ['N','E','S','W'].forEach(function(n,i){var t=i*Math.PI/2;s+='<text class="lb" x="'+bimClbF(cx+(R+14)*Math.sin(t))+'" y="'+bimClbF(cy-(R+14)*Math.cos(t)+4)+'" text-anchor="middle">'+n+'</text>';});
    E.events.slice().reverse().forEach(function(e){
      var t=e.az*Math.PI/180,r=pr(e.km),rr=Math.max(3,3+(e.m-E.minmag)*5);
      s+='<circle class="mk" cx="'+bimClbF(cx+r*Math.sin(t))+'" cy="'+bimClbF(cy-r*Math.cos(t))+'" r="'+bimClbF(rr)+'" fill="var(--s2)" fill-opacity=".35" stroke="var(--s2)" stroke-width="1.25"'+
        bimClbTip('M'+e.m.toFixed(1)+', '+e.t+'|'+bimClbNum(e.km,0)+' km '+bimClimDir(e.az)+(e.depth!==null?', '+bimClbNum(e.depth,0)+' km deep':'')+'|'+e.place)+'/>';
    });
    E.events.slice(0,3).forEach(function(e){var t=e.az*Math.PI/180,r=pr(e.km),rr=3+(e.m-E.minmag)*5;
      s+='<text class="lb" x="'+bimClbF(cx+r*Math.sin(t)+rr+3)+'" y="'+bimClbF(cy-r*Math.cos(t)+4)+'">M'+e.m.toFixed(1)+' · '+e.t.slice(0,4)+'</text>';});
    s+='<path d="M'+(cx-6)+' '+cy+'h12M'+cx+' '+(cy-6)+'v12" stroke="var(--ink)" stroke-width="2"/>';
    return s+'</svg>';
  }
  function bimClbState(st){
    var S=BIM_STATE[st];if(!S)return '';
    return '<div class="a3d-clb-st"><svg viewBox="0 0 16 16" style="color:'+S[1]+'" aria-hidden="true">'+S[2]+'</svg>'+S[0]+'</div>';
  }
  function bimClbKpi(label,val,unit,mean,st){
    return '<div class="a3d-clb-kpi" data-kpi="'+bimClbE(label)+'"><div class="a3d-clb-kl">'+bimClbE(label)+'</div><div class="a3d-clb-kv">'+bimClbE(val)+(unit?'<span class="a3d-clb-ku">'+bimClbE(unit)+'</span>':'')+'</div>'+
      (mean?'<div class="a3d-clb-km">'+bimClbE(mean)+'</div>':'')+(st?bimClbState(st):'')+'</div>';
  }
  function bimClbLeg(items){return '<div class="a3d-clb-legend">'+items.map(function(it){return '<span><i class="'+(it[2]||'')+'" style="background:'+it[0]+'"></i>'+bimClbE(it[1])+'</span>';}).join('')+'</div>';}
  /* the whole board */
  function bimClbHtml(){
    var C=A3D.site&&A3D.site.climate,K=A3D.site&&A3D.site.risk,st=bimSunSettings(),N=C&&C.normals,Hh=C&&C.hourly,h,cards=[],kp=[],src,i;
    var site=(A3D.site&&A3D.site.name&&A3D.site.name!=='Site')?A3D.site.name:(bimProjectLabel()||'The site');
    var bar='<div class="a3d-clb-bar"><div class="a3d-clb-bart">Climate and risk</div>'+
      '<button type="button" class="a3d-clb-btn" data-clb="tables" aria-pressed="'+A3D_CLB.tables+'">Tables</button>'+
      '<button type="button" class="a3d-clb-btn a3d-clb-hide-s" data-clb="refresh">Refresh data</button>'+
      '<button type="button" class="a3d-clb-btn a3d-clb-hide-s" data-clb="print">Print</button>'+
      '<button type="button" class="a3d-clb-btn" data-clb="close" aria-label="Close the board">Close</button></div>';
    if(!C&&!K){
      return bar+'<div class="a3d-clb-page"><div class="a3d-clb-kicker">Site analysis · Climate · Environmental risk</div><h1 class="a3d-clb-h1">'+bimClbE(site)+': climate and risk</h1>'+
        '<div class="a3d-clb-empty">No climate or risk data yet. They come from ERA5 (via Open-Meteo), CAMS air quality and the USGS earthquake catalogue: free, no account.'+
        (bimSunNum(st.lat)&&bimSunNum(st.lon)?'':' Set the site latitude and longitude first (Properties, Site, Location).')+
        '<div style="margin-top:12px"><button type="button" class="a3d-clb-btn pri" data-clb="refresh">Get climate and risk</button></div></div></div>';
    }
    var lat=C?C.lat:K.lat,lon=C?C.lon:K.lon;
    var sub=Math.abs(lat).toFixed(4)+'° '+(lat<0?'S':'N')+', '+Math.abs(lon).toFixed(4)+'° '+(lon<0?'W':'E');
    if(C&&C.koppen)sub+=' · '+C.koppen.code+' '+C.koppen.name;
    if(C&&C.period)sub+=' · climate '+C.period[0]+'–'+C.period[1];
    sub+=' · data of '+((C&&C.fetched)||(K&&K.fetched));
    h=bar+'<div class="a3d-clb-page"><header><div class="a3d-clb-kicker">Site analysis · 5 Climate · 7 Environmental risk</div>'+
      '<h1 class="a3d-clb-h1">'+bimClbE(site)+': climate and risk</h1><p class="a3d-clb-sub">'+bimClbE(sub)+'</p></header>';
    /* the indicators */
    if(N){
      var M=N.months,a=N.annual,iw=bimClbIdx(M,'tx','max'),ic=bimClbIdx(M,'tn','min'),ip=bimClbIdx(M,'p','max');
      if(C.koppen)kp.push(bimClbKpi('Climate zone',C.koppen.code,'',C.koppen.name));
      kp.push(bimClbKpi('Mean temperature',bimClbNum(a.t),'°C',BIM_CLIM_MONTHS[iw]+' highs '+bimClbNum(M[iw].tx)+'°, '+BIM_CLIM_MONTHS[ic]+' lows '+bimClbNum(M[ic].tn)+'°'));
      kp.push(bimClbKpi('Rainfall',bimClimInt(a.p),'mm/yr',a.wet+' wet days; most in '+BIM_CLIM_MONTH_NAMES[ip]));
    }
    if(Hh&&Hh.wind&&Hh.wind.year.prev!==null)kp.push(bimClbKpi('Prevailing wind',BIM_CLIM_DIRS[Hh.wind.year.prev],'',bimClbNum(Hh.wind.year.mean)+' m/s mean; calm '+bimClbNum(Hh.wind.year.calm,0)+'%'));
    if(N){kp.push(bimClbKpi('Degree days',bimClimInt(N.annual.hdd)+' / '+bimClimInt(N.annual.cdd),'','Heating / cooling, base '+BIM_CLIM_BASE+' °C'));
      kp.push(bimClbKpi('Solar energy',bimClimInt(N.annual.sw),'kWh/m²·yr','On the horizontal'));}
    if(Hh&&Hh.comfort)kp.push(bimClbKpi('Outdoor comfort',bimClbNum(Hh.comfort.inside,0),'%','Of the year\'s hours, 20–27 °C and 20–80% RH'));
    if(K&&K.air)kp.push(bimClbKpi('PM2.5',bimClbNum(K.air.mean),'µg/m³',K.air.days.length+'-day mean; '+K.air.over+' days above WHO '+BIM_CLIM_WHO24,K.air.status));
    if(K&&K.quakes)kp.push(bimClbKpi('Earthquakes',String(K.quakes.count),'','M'+K.quakes.minmag+'+ within '+K.quakes.radius+' km since '+K.quakes.since.slice(0,4)+(K.quakes.max?'; largest M'+K.quakes.max.m.toFixed(1):''),K.quakes.status));
    h+='<section class="a3d-clb-kpis" aria-label="Indicators" style="--n:'+kp.length+'">'+kp.join('')+'</section><section class="a3d-clb-grid">';
    var fig=0;
    if(N){
      M=N.months;a=N.annual;src=C.src+', '+C.period[0]+'–'+C.period[1]+' (daily, '+N.years+' years)';
      iw=bimClbIdx(M,'tx','max');ic=bimClbIdx(M,'tn','min');ip=bimClbIdx(M,'p','max');
      var title=(C.koppen?C.koppen.name+': ':'')+BIM_CLIM_MONTH_NAMES[iw]+' highs average '+bimClbNum(M[iw].tx)+' °C, '+BIM_CLIM_MONTH_NAMES[ic]+' lows '+bimClbNum(M[ic].tn)+' °C';
      fig++;
      cards.push(bimClbCard(['s7','wide'],fig,title,'Monthly mean of the daily high and low; the band holds 80% of real days (10th to 90th percentile). Below: rainfall, '+bimClimInt(a.p)+' mm a year, most in '+BIM_CLIM_MONTH_NAMES[ip]+'.',
        '<div class="a3d-clb-chart">'+bimClbTempSvg(M)+'</div>'+bimClbLeg([['var(--s2)','Mean daily high','ln'],['var(--s1)','Mean daily low','ln'],['var(--band)','10th to 90th percentile of days']])+
        '<div class="a3d-clb-chart" style="margin-top:6px">'+bimClbRainSvg(M)+'</div>'+
        bimClbTable(['Month','High °C','Low °C','Mean °C','90th high','10th low','Rain mm','Wet days'],M.map(function(m,j){return [BIM_CLIM_MONTHS[j],bimClbNum(m.tx),bimClbNum(m.tn),bimClbNum(m.tm),bimClbNum(m.tx90),bimClbNum(m.tn10),Math.round(m.p),bimClbNum(m.wet,0)];})),src));
    }
    if(Hh&&Hh.wind&&Hh.wind.year.n){
      var Wy=Hh.wind.year,sw=lat>=0?['Winter (Dec–Feb)','Summer (Jun–Aug)']:['Winter (Jun–Aug)','Summer (Dec–Feb)'];
      fig++;
      cards.push(bimClbCard('s5',fig,'Prevailing wind from the '+BIM_CLIM_DIRS[Wy.prev]+', '+bimClbNum(Wy.mean)+' m/s on average',
        'Share of '+Hh.year+'\'s hours from each direction, by speed at 10 m. Calm (under '+BIM_CLIM_CALM+' m/s) '+bimClbNum(Wy.calm,0)+'%, shown at the centre.',
        '<div class="a3d-clb-chart">'+bimClbRoseSvg(Wy,false,'Wind rose, '+Hh.year)+'</div>'+
        bimClbLeg(Hh.wind.bins.map(function(b,j){return ['var(--w'+(j+1)+')',bimClbWindBand(j)];}))+
        '<div class="a3d-clb-row" style="margin-top:6px"><div><div class="a3d-clb-fno" style="text-align:center">'+sw[0]+'</div><div class="a3d-clb-chart">'+bimClbRoseSvg(Hh.wind.winter,true,sw[0])+'</div></div>'+
        '<div><div class="a3d-clb-fno" style="text-align:center">'+sw[1]+'</div><div class="a3d-clb-chart">'+bimClbRoseSvg(Hh.wind.summer,true,sw[1])+'</div></div></div>'+
        bimClbTable(['From'].concat(Hh.wind.bins.map(function(b,j){return bimClbWindBand(j);})).concat(['All %']),Wy.pct.map(function(r,k){var tt=0;r.forEach(function(v){tt+=v;});return [BIM_CLIM_DIRS[k]].concat(r.map(function(v){return bimClbNum(v);})).concat([bimClbNum(tt)]);})),
        C.src+', '+Hh.year+' hourly'));
    }
    if(Hh&&Hh.heat&&Hh.heat.length>=24*28){
      var nh=0,nc=0,hx=-1e9,hxi=0;
      Hh.heat.forEach(function(v,j){if(v===null)return;nh++;if(v>=20&&v<24)nc++;if(v>hx){hx=v;hxi=j;}});
      var hd=new Date(Date.parse(Hh.start+'T00:00:00Z')+Math.floor(hxi/24)*864e5);
      fig++;
      cards.push(bimClbCard(['s12','wide'],fig,'In '+Hh.year+' the air was 20–24 °C for '+bimClbNum(100*nc/Math.max(1,nh),0)+'% of hours; the hottest hour reached '+hx+' °C on '+hd.getUTCDate()+' '+BIM_CLIM_MONTHS[hd.getUTCMonth()],
        'Every hour of '+Hh.year+': the day across, the hour of the day down (local time), in named temperature bands.'+(A3D_CLB.narrow?' Swipe across for the year.':''),
        '<div class="a3d-clb-chart a3d-clb-heat">'+bimClbHeatSvg(Hh)+'</div>'+bimClbLeg(BIM_HEAT_SHORT.map(function(n,j){return [BIM_HEAT_COL[j],n+' °C'];}))+
        bimClbTable(['Band','Hours','Share'],BIM_HEAT_NAMES.map(function(n,j){var c=0;Hh.heat.forEach(function(v){if(v!==null&&bimClbHeatClass(v)===j)c++;});return [n,c,bimClbNum(100*c/Math.max(1,nh))+'%'];})),
        C.src+', '+Hh.year+' hourly'));
    }
    var sun=bimClbSunSvg(lat,lon,bimSunNum(st.tz)?st.tz:Math.round(lon/15));
    fig++;
    cards.push(bimClbCard('s4',fig,'The sun climbs to '+bimClbNum(sun.days[0].alt,0)+'° at midsummer and '+bimClbNum(sun.days[2].alt,0)+'° at midwinter',
      'Sun path, looking up: the centre overhead, the rim the horizon, rings every 15° of altitude; dots every hour'+(bimSunNum(st.tz)?' (UTC'+(st.tz>=0?'+':'')+st.tz+')':' (approximate local time)')+'.',
      '<div class="a3d-clb-chart">'+sun.svg+'</div>'+bimClbLeg(sun.days.map(function(d){return [d.col,d.label+': '+bimClbNum(d.alt,0)+'°, '+Math.floor(d.len/60)+' h '+bimPad2(d.len%60)+' of daylight','ln'];}))+
      bimClbTable(['Day','Highest altitude','Daylight'],sun.days.map(function(d){return [d.label,bimClbNum(d.alt,1)+'°',Math.floor(d.len/60)+' h '+bimPad2(d.len%60)];})),
      'Sun position, NOAA equations (in this app)'));
    if(N){
      fig++;
      cards.push(bimClbCard('s4',fig,(a.hdd>2*a.cdd?'Heating dominates':(a.cdd>2*a.hdd?'Cooling dominates':'Both heating and cooling matter'))+': '+bimClimInt(a.hdd)+' heating, '+bimClimInt(a.cdd)+' cooling degree days',
        'Degree days a month, base '+BIM_CLIM_BASE+' °C on the daily mean ((high + low) / 2): cooling up, heating down.',
        '<div class="a3d-clb-chart">'+bimClbDdSvg(M)+'</div>'+bimClbLeg([['var(--s2)','Cooling degree days'],['var(--s1)','Heating degree days']])+
        bimClbTable(['Month','Heating','Cooling'],M.map(function(m,j){return [BIM_CLIM_MONTHS[j],Math.round(m.hdd||0),Math.round(m.cdd||0)];})),src));
      fig++;
      var im=bimClbIdx(M,'sw','max'),imn=bimClbIdx(M,'sw','min');
      cards.push(bimClbCard('s4',fig,bimClimInt(a.sw)+' kWh/m² of sun a year on open ground',
        'Daily global horizontal irradiation by month, kWh/m²: '+bimClbNum(M[im].sw)+' in '+BIM_CLIM_MONTH_NAMES[im]+', '+bimClbNum(M[imn].sw)+' in '+BIM_CLIM_MONTH_NAMES[imn]+'.',
        '<div class="a3d-clb-chart">'+bimClbSolarSvg(M)+'</div>'+
        bimClbTable(['Month','kWh/m² a day'],M.map(function(m,j){return [BIM_CLIM_MONTHS[j],bimClbNum(m.sw,2)];})),src));
    }
    if(Hh&&Hh.comfort&&Hh.psy){
      fig++;
      cards.push(bimClbCard('s6',fig,bimClbNum(Hh.comfort.inside,0)+'% of hours are comfortable outdoors; '+bimClbNum(Hh.comfort.cold,0)+'% too cool, '+bimClbNum(Hh.comfort.hot,0)+'% too hot or humid',
        'Psychrometric chart of '+Hh.year+'\'s hours: dry-bulb temperature across, humidity ratio up, curves of relative humidity. Darker cells hold more hours.',
        '<div class="a3d-clb-chart">'+bimClbPsySvg(Hh)+'</div>'+bimClbLeg([['var(--w1)','1–4 hours'],['var(--w2)','5–14'],['var(--w3)','15–39'],['var(--w4)','40–99'],['var(--w5)','100 or more'],['transparent','Comfort zone: 20–27 °C, 20–80% RH']])+
        bimClbTable(['Hours','Share'],[['Comfortable',bimClbNum(Hh.comfort.inside)+'%'],['Too cool',bimClbNum(Hh.comfort.cold)+'%'],['Too hot or humid',bimClbNum(Hh.comfort.hot)+'%'],['Hours read',Hh.comfort.hours]]),
        C.src+', '+Hh.year+' hourly; humidity ratio at sea-level pressure'));
    }
    if(K&&K.quakes){
      var E=K.quakes,b=E.max;
      fig++;
      cards.push(bimClbCard('s6',fig,E.count?(E.count+' earthquake'+(E.count===1?'':'s')+' of M'+E.minmag+'+ within '+E.radius+' km since '+E.since.slice(0,4)+'; the largest M'+b.m.toFixed(1)+' in '+b.t.slice(0,4)+', '+bimClbNum(b.km,0)+' km '+bimClimDir(b.az)):
        'No earthquake of M'+E.minmag+' or more recorded within '+E.radius+' km since '+E.since.slice(0,4),
        'By distance and direction from the site; the circle grows with magnitude. History, not a hazard model: for design, use the national seismic hazard map and code.',
        '<div class="a3d-clb-row"><div style="flex:1 1 300px"><div class="a3d-clb-chart">'+bimClbQuakeSvg(E)+'</div></div>'+
        (E.count?'<div style="flex:1 1 260px"><table class="a3d-clb-eqt"><thead><tr><th>Date</th><th>M</th><th>km</th><th>From</th><th style="text-align:left">Where</th></tr></thead><tbody>'+
          E.events.slice(0,8).map(function(e){return '<tr><td>'+bimClbE(e.t)+'</td><td>'+e.m.toFixed(1)+'</td><td>'+Math.round(e.km)+'</td><td>'+bimClimDir(e.az)+'</td><td class="pl">'+bimClbE(e.place)+'</td></tr>';}).join('')+'</tbody></table></div>':'')+'</div>'+
        bimClbTable(['Date','Magnitude','km','Direction','Depth km','Where'],E.events.map(function(e){return [e.t,e.m.toFixed(1),bimClbNum(e.km,0),bimClimDir(e.az),e.depth===null?'':bimClbNum(e.depth,0),e.place];})),K.quakeSrc));
    }
    if(K&&K.air){
      var Q=K.air;
      fig++;
      cards.push(bimClbCard(['s12','wide'],fig,'PM2.5 averaged '+bimClbNum(Q.mean)+' µg/m³; '+Q.over+' of '+Q.days.length+' days exceeded the WHO guideline',
        'Daily mean fine particulate matter (PM2.5), '+Q.from+' to '+Q.to+', against the WHO 2021 24-hour guideline of '+BIM_CLIM_WHO24+' µg/m³ (annual: '+BIM_CLIM_WHO_YEAR+').',
        '<div class="a3d-clb-chart">'+bimClbAirSvg(Q)+'</div>'+bimClbLeg([['var(--s1)','Within the guideline'],['var(--serious)','Above the guideline'],['transparent','WHO guideline and interim targets','dsh']])+
        bimClbTable(['Day','PM2.5 µg/m³'],Q.days.map(function(d){return [d.d,bimClbNum(d.v)];})),K.airSrc+' (model analysis, about 10 to 40 km)'));
    }
    h+=cards.join('')+'</section>';
    h+='<footer class="a3d-clb-notes"><h3>Method and sources</h3><ul>'+
      '<li>Climate: ERA5 reanalysis (ECMWF Copernicus), about 25 km cells, '+(C&&C.period?C.period[0]+' to '+C.period[1]+' daily and '+(Hh?Hh.year:'')+' hourly':'')+', via <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a> (CC BY 4.0). A reanalysis is a model of the weather, not a station record: a city\'s heat island, a valley\'s frost or a coast\'s breeze can differ; confirm with a local station where it matters.</li>'+
      '<li>Degree days on the daily mean, (high + low) / 2, against '+BIM_CLIM_BASE+' °C. Climate zone: Köppen–Geiger by the rules of Beck et al. 2018, from the monthly means and totals.</li>'+
      '<li>Comfort zone: '+BIM_CLIM_COMFORT.t0+'–'+BIM_CLIM_COMFORT.t1+' °C dry-bulb at '+BIM_CLIM_COMFORT.rh0+'–'+BIM_CLIM_COMFORT.rh1+'% relative humidity, a simple outdoor zone in still air and shade; sun, wind and clothing move it.</li>'+
      '<li>Air quality: CAMS (Copernicus Atmosphere Monitoring Service) via Open-Meteo, against the <a href="https://www.who.int/publications/i/item/9789240034228" target="_blank" rel="noopener">WHO 2021 guidelines</a>.</li>'+
      '<li>Earthquakes: the <a href="https://earthquake.usgs.gov/" target="_blank" rel="noopener">USGS</a> catalogue, M'+BIM_CLIM_EQ_MIN+' and above within '+BIM_CLIM_EQ_KM+' km since '+BIM_CLIM_EQ_SINCE.slice(0,4)+'.</li>'+
      ((C&&C.errors&&C.errors.length)?'<li>Not available at the last fetch: '+bimClbE(C.errors.join('; '))+'.</li>':'')+
      '</ul></footer></div>';
    return h;
  }
  /* open, refresh, close; the tooltip; Esc */
  function bimClbOpen(){
    var b=document.querySelector('.a3d-clb');
    if(!b){
      b=document.createElement('div');b.className='a3d-clb'+(A3D_CLB.tables?' tables':'');
      b.setAttribute('role','dialog');b.setAttribute('aria-modal','true');b.setAttribute('aria-label','Climate and risk board');
      document.body.appendChild(b);bimClbWire(b);
    }
    A3D_CLB.narrow=window.innerWidth<760;
    b.innerHTML=bimClbHtml()+'<div class="a3d-clb-tip" role="tooltip" hidden></div>';
    A3D_CLB.open=true;document.body.classList.add('a3d-clb-open');
    var c=b.querySelector('[data-clb="close"]');if(c)try{c.focus();}catch(eF){}
    return true;
  }
  function bimClbClose(){var b=document.querySelector('.a3d-clb');if(b)b.parentNode.removeChild(b);A3D_CLB.open=false;document.body.classList.remove('a3d-clb-open');return true;}
  function bimClbRefresh(){if(A3D_CLB.open)bimClbOpen();}
  function bimClbTipShow(b,x,y,txt){
    var t=b.querySelector('.a3d-clb-tip');if(!t)return;
    var P=String(txt).split('|');
    while(t.firstChild)t.removeChild(t.firstChild);
    P.forEach(function(p,i){var d=document.createElement('div');if(i===0){var bb=document.createElement('b');bb.textContent=p;d.appendChild(bb);}else{d.className='tl';d.textContent=p;}t.appendChild(d);});
    t.hidden=false;
    var w=t.offsetWidth,h=t.offsetHeight,vw=window.innerWidth,vh=window.innerHeight;
    t.style.left=Math.max(6,Math.min(vw-w-6,x+14))+'px';t.style.top=Math.max(6,Math.min(vh-h-6,y+14))+'px';
  }
  function bimClbTipHide(b){var t=b.querySelector('.a3d-clb-tip');if(t)t.hidden=true;}
  function bimClbHeatTip(svg,ev){
    var pt=svg.createSVGPoint?svg.createSVGPoint():null,m=svg.getScreenCTM&&svg.getScreenCTM();
    if(!pt||!m)return null;
    pt.x=ev.clientX;pt.y=ev.clientY;var p=pt.matrixTransform(m.inverse());
    var L=+svg.getAttribute('data-l'),T0=+svg.getAttribute('data-t'),cw=+svg.getAttribute('data-cw'),ch=+svg.getAttribute('data-ch'),days=+svg.getAttribute('data-days');
    var d=Math.floor((p.x-L)/cw),h=Math.floor((p.y-T0)/ch),Hh=A3D.site&&A3D.site.climate&&A3D.site.climate.hourly;
    if(!Hh||d<0||d>=days||h<0||h>23)return null;
    var v=Hh.heat[d*24+h],dt=new Date(Date.parse(Hh.start+'T00:00:00Z')+d*864e5);
    if(v===null||v===undefined)return null;
    return dt.getUTCDate()+' '+BIM_CLIM_MONTH_NAMES[dt.getUTCMonth()]+', '+(h<10?'0':'')+h+':00|'+v+' °C|'+BIM_HEAT_NAMES[bimClbHeatClass(v)];
  }
  function bimClbWire(b){
    b.addEventListener('click',function(ev){
      var k=ev.target&&ev.target.closest?ev.target.closest('[data-clb]'):null;if(!k)return;
      var a=k.getAttribute('data-clb');
      if(a==='close')bimClbClose();
      else if(a==='print'){try{window.print();}catch(eP){}}
      else if(a==='refresh')bimClimFetch();
      else if(a==='tables'){A3D_CLB.tables=!A3D_CLB.tables;b.classList.toggle('tables',A3D_CLB.tables);k.setAttribute('aria-pressed',String(A3D_CLB.tables));}
    });
    b.addEventListener('pointermove',function(ev){
      var e=ev.target&&ev.target.closest?ev.target.closest('[data-tip],[data-heathit]'):null;
      if(!e){bimClbTipHide(b);return;}
      var txt=e.hasAttribute('data-heathit')?bimClbHeatTip(e.ownerSVGElement||e.closest('svg'),ev):e.getAttribute('data-tip');
      if(txt)bimClbTipShow(b,ev.clientX,ev.clientY,txt);else bimClbTipHide(b);
    });
    b.addEventListener('pointerleave',function(){bimClbTipHide(b);});
    b.addEventListener('focusin',function(ev){var e=ev.target;if(e&&e.getAttribute&&e.getAttribute('data-tip')){var r=e.getBoundingClientRect();bimClbTipShow(b,r.left+r.width/2,r.top,e.getAttribute('data-tip'));}});
    b.addEventListener('focusout',function(){bimClbTipHide(b);});

  }
  /* the Site analysis view's section: what is known, and the two ways in */
  function bimClbSaHtml(){
    var C=A3D.site&&A3D.site.climate,K=A3D.site&&A3D.site.risk,s='<div class="a3d-clsec"><div class="a3d-sasechd">Climate and risk</div>';
    if(C||K){
      var p=[];
      if(C&&C.koppen)p.push(C.koppen.code+' '+C.koppen.name);
      if(C&&C.normals)p.push(bimClbNum(C.normals.annual.t)+' °C mean, '+bimClimInt(C.normals.annual.p)+' mm a year');
      if(C&&C.hourly&&C.hourly.wind&&C.hourly.wind.year.prev!==null)p.push('wind from the '+BIM_CLIM_DIRS[C.hourly.wind.year.prev]);
      if(K&&K.air)p.push('PM2.5 '+bimClbNum(K.air.mean)+' µg/m³');
      if(K&&K.quakes)p.push(K.quakes.count+' earthquake'+(K.quakes.count===1?'':'s')+' nearby');
      s+='<p class="a3d-clsum">'+bimClbE(p.join(' · '))+'. Data of '+bimClbE((C&&C.fetched)||(K&&K.fetched))+'.</p>'+
        '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="climboard">Open the board</button><button type="button" class="a3d-anzbtn" data-saact="climget">Refresh</button></div>';
    }else s+='<p class="a3d-clsum">Ten years of climate, a year of hours, air quality and earthquakes, from free open sources: a board of ten figures, and findings in Climate and Environmental risk.</p>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="climget">Get climate and risk</button><button type="button" class="a3d-anzbtn" data-saact="climboard">Open the board</button></div>';
    return s+'</div>';
  }"""
rep("""  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""", BOARD + """
  /* ---- edits: each one undo step ---- */
  function bimSaAdd(cat,f){""")

rep("""  window.__a3dClimAuto=function(){return bimClimAuto();};""",
    """  window.__a3dClimAuto=function(){return bimClimAuto();};
  window.__a3dClbOpen=function(){return bimClbOpen();};
  window.__a3dClbClose=function(){return bimClbClose();};
  window.__a3dClbHtml=function(){return bimClbHtml();};
  window.__a3dAnzView=function(v){if(v)return bimAnzView(v);return A3D_ANZ.view;};""")

rep("""    CONTEXT:'neighbours neighbors surrounding""", """    CLIMATE:'climate weather temperature rain rainfall precipitation wind rose sun path degree days heating cooling solar radiation humidity psychrometric comfort koppen air quality pollution pm2.5 earthquake seismic risk board dashboard charts',   /* __acad3dV159 */
    CLIMATEGET:'climate weather data temperature rain wind air quality earthquake fetch download era5 open-meteo usgs',
    CONTEXT:'neighbours neighbors surrounding""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
