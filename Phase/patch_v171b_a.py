#!/usr/bin/env python3
"""V171b: the analysis workspace (reference/research-analysis-workspace.md). The site analysis becomes a place one goes
into and leaves, as archiMap's and Forma's are: a bar over the view with the analysis in focus and a cross; the analyses
on the left in their groups, one in focus and others ticked under it; the one analysis on the right, where Properties is
while nothing is selected. The view goes quiet in the app's own mode, light or dark: its ground, the map greyed and
faded, the context in the mode's greys, the words and the key in its colours, so only the data keeps its colour.

Three new files: site-analysis/analysis-workspace.js, its stylesheet site-analysis/workspace.css, and the suite's
hooks testing/hooks-workspace.js. Here, the files they reach into: Analyze shows the list while the workspace is open,
its rows gain Open; Properties shows the one analysis; Analyze site ends in the workspace with nothing in focus, inside
its one undo step; TRAFFIC puts Traffic and people in focus, inside its; the colour lens gives the context its tones;
the view's background, the map's shaders, the grid, the words and the key take the mode's; SITEWORKSPACE opens it.

The workspace's files are written from the scratch copies named below. Run from the repository root:
    python3 Phase/patch_v171b_a.py <aw.js> <aw.css>
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, write, done   # noqa: E402

AW_JS = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
AW_CSS = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')

begin('c77eb5aa6d0bca806ff31b4a7b8bb68b8f1dd5b4846ecbd35968e186a3ba92ab')   # V171, as merged

# ---- the new files, and where they go in the order ----
write('js/engine/site-analysis/analysis-workspace.js', AW_JS)
write('css/site-analysis/workspace.css', AW_CSS)
write('js/engine/testing/hooks-workspace.js',
      "  /* __acad3dV171b: the analysis workspace, for the suite */\n"
      "  window.__acad3dV171b='workspace,enter,leave,focus,ticks,layers,undo,kept,afterrun,traffic,bar,list,panel,overview,chart,key,"
      "look,lightdark,ground,ctxtones,mapgrey,words,legendplace,dockhidden,toasttop,phone,chips,details,command,open,rowfit';\n"
      "  window.__a3dAw=function(){var S=bimAwState(),L=bimAwLook();\n"
      "    return {on:!!A3D_AW.on,focus:S.focus,add:S.add.slice(),now:bimAwFocusNow(),look:L?(L.light?'light':'dark'):null,bg:bimAwBgHex(),\n"
      "      shown:BIM_DG_AN.filter(function(A){return bimAwShown(A.id);}).map(function(A){return A.id;}),\n"
      "      run:BIM_DG_AN.filter(function(A){return !!bimDgState().runs[A.id];}).map(function(A){return A.id;})};};\n"
      "  window.__a3dAwEnter=function(f){return f===undefined?bimAwEnter():bimAwEnter(f);};\n"
      "  window.__a3dAwLeave=function(){return bimAwLeave();};\n"
      "  window.__a3dAwFocus=function(a){return bimAwFocus(a);};\n"
      "  window.__a3dAwTick=function(a){return bimAwTick(a);};\n"
      "  window.__a3dAwCtxCol=function(id){var o=objById(id);return o?bimAwCtxCol(o):null;};\n"
      "  window.__a3dAwInk=function(c){return bimAwInk(c);};\n"
      "  window.__a3dAwGroups=function(){return BIM_AW_GROUPS.map(function(G){return {id:G.id,name:G.name,an:G.an.slice()};});};\n"
      "  /* the older suites' view of a run: out of the workspace, each analysis shown as a run showed it before V171b */\n"
      "  window.__a3dAwClassic=function(){\n"
      "    if(A3D_AW.on)bimAwLeave();\n"
      "    var D=bimDgState(),n=0;\n"
      "    BIM_DG_AN.forEach(function(A){var ly=bimLayerById(D.layers[A.id]);if(ly&&D.runs[A.id]&&(ly.visible!==false)!==!A.hidden){ly.visible=!A.hidden;n++;}});\n"
      "    var S=bimAwState();S.focus=null;S.add=[];\n"
      "    if(n)bimLayerChanged();\n"
      "    return n;\n"
      "  };\n")
rep('index.html', "<!-- @include css/shell/top-bar-start.css -->\n",
    "<!-- @include css/shell/top-bar-start.css -->\n<!-- @include css/site-analysis/workspace.css -->\n")
rep('index.html', "<!-- @include js/engine/simulation/traffic-ui.js -->\n",
    "<!-- @include js/engine/simulation/traffic-ui.js -->\n<!-- @include js/engine/site-analysis/analysis-workspace.js -->\n")
rep('index.html', "<!-- @include js/engine/testing/hooks-traffic.js -->\n",
    "<!-- @include js/engine/testing/hooks-traffic.js -->\n<!-- @include js/engine/testing/hooks-workspace.js -->\n")

# ---- Analyze: the list while the workspace is open; Open on each row and on the site ----
rep('js/engine/analysis/analyze-tab.js',
    "  function bimAnalyzeHtml(){\n    var C=bimAnzCards();\n",
    "  function bimAnalyzeHtml(){\n    if(A3D_AW.on)return bimAwListHtml();   /* __acad3dV171b: the workspace's analyses */\n    var C=bimAnzCards();\n")
rep('js/engine/analysis/analyze-tab.js',
    "      var rows=w.querySelector('.a3d-anzrows'),cnt=w.querySelector('.a3d-anzcount'),C;\n",
    "      if(A3D_AW.on){bimRenderInto(w,bimAwListHtml());return true;}   /* __acad3dV171b */\n"
    "      var rows=w.querySelector('.a3d-anzrows'),cnt=w.querySelector('.a3d-anzcount'),C;\n")
rep('js/engine/analysis/analyze-tab.js',
    "  function bimAnzAct(a){\n    var k=String(a||''),g;\n",
    "  function bimAnzAct(a){\n    var k=String(a||''),g;\n    if(k.indexOf('aw:')===0)return bimAwAct(k.slice(3));   /* __acad3dV171b: the workspace */\n")
rep('js/engine/site-analysis/analyze-site.js',
    "        acts:[{act:'dg:show:'+A.id,label:on?'Hide':'Show',pri:!on&&L.length>0,off:L.length?'':'Nothing drawn yet'},\n",
    "        acts:[{act:'dg:show:'+A.id,label:on?'Hide':'Show',pri:!on&&L.length>0,off:L.length?'':'Nothing drawn yet'},\n"
    "          {act:'aw:open:'+A.id,label:'Open',tip:'In the site analysis: drawn alone, with its key and its panel',off:R?'':'Not run yet'},   /* __acad3dV171b */\n")
rep('js/engine/site-analysis/analyze-site.js',
    "      (D.last?'<button type=\"button\" class=\"a3d-anzbtn\" data-saact=\"dglegend\"",
    "      (D.last?'<button type=\"button\" class=\"a3d-anzbtn\" data-anzact=\"aw:open:\" title=\"The analyses one at a time, each with its key and its panel\">Open the site analysis</button>':'')+   /* __acad3dV171b */\n"
    "      (D.last?'<button type=\"button\" class=\"a3d-anzbtn\" data-saact=\"dglegend\"")
rep('js/engine/site-analysis/analyze-site.js',
    "        var res=finish(true);\n",
    "        bimAwAfterRun();   /* __acad3dV171b: the site and its context, and the list, in the run's one step */\n        var res=finish(true);\n")

# ---- Properties: the one analysis while nothing is selected ----
rep('js/engine/site-analysis/panel.js',
    "    bimAnalyzeRefresh();   /* __acad3dV141; __acad3dV162: the site analysis with it */\n",
    "    bimAnalyzeRefresh();   /* __acad3dV141; __acad3dV162: the site analysis with it */\n    bimAwTitleSync();   /* __acad3dV171b */\n")
rep('js/engine/site-analysis/panel.js',
    "      bimRenderInto(el.propsbody,bimModelPropsHtml());   /* __acad3dV118 */\n",
    "      if(A3D_AW.on){bimRenderInto(el.propsbody,bimAwPanelHtml());return;}   /* __acad3dV171b: the one analysis */\n"
    "      bimRenderInto(el.propsbody,bimModelPropsHtml());   /* __acad3dV118 */\n")

# ---- the view in the mode's quiet tones ----
rep('js/engine/map/colour-lens.js',
    "    return c.by?(c.col[o.id]||null):null;\n",
    "    return c.by?(c.col[o.id]||null):bimAwCtxCol(o);   /* __acad3dV171b: in the workspace the context's quiet tones */\n")
rep('js/engine/map/terrain-3d.js',
    "    gl.clearColor(0.114,0.125,0.141,1);\n",
    "    var awB=bimAwBg();gl.clearColor(awB[0],awB[1],awB[2],1);   /* __acad3dV171b: the workspace's ground */\n")
rep('js/engine/map/terrain-3d.js',
    "    else{ctx.fillStyle='#1d2024';ctx.fillRect(0,0,W,H);}\n",
    "    else{ctx.fillStyle=bimAwBgHex();ctx.fillRect(0,0,W,H);}   /* __acad3dV171b */\n")
rep('js/engine/map/terrain-3d.js',
    "      ctx.strokeStyle='#282c31';ctx.lineWidth=1;ctx.beginPath();\n",
    "      ctx.strokeStyle=bimAwLook()?bimAwLook().grid:'#282c31';ctx.lineWidth=1;ctx.beginPath();   /* __acad3dV171b */\n")
rep('js/engine/render/webgpu.js',
    "clearValue:{r:0.114,g:0.125,b:0.141,a:1}",
    "clearValue:bimAwClear()")
rep('js/engine/render/webgpu.js',
    "'@fragment fn fsMap(i:MO)->@location(0) vec4f{let c=textureSample(tx,smp,i.uv).rgb;return vec4f(mix(vec3f(0.114,0.125,0.141),c,m.color.a),1.0);}\\n'+",
    "'@fragment fn fsMap(i:MO)->@location(0) vec4f{let c=textureSample(tx,smp,i.uv).rgb;let g=mix(c,vec3f(dot(c,vec3f(0.299,0.587,0.114))),m.tile.w);return vec4f(mix(m.color.rgb,g,m.color.a),1.0);}\\n'+   /* __acad3dV171b: color.rgb the ground, tile.w grey */")
rep('js/engine/render/webgpu.js',
    "        out.mapPrm=put([0,0,0],plan.opacity,[0,0,1,1],[0,0,1,0]);\n",
    "        out.mapPrm=put(bimAwBg(),plan.opacity,[0,0,1,1],[0,0,1,bimAwLook()?bimAwLook().grey:0]);   /* __acad3dV171b */\n")
rep('js/engine/map/map-tiles.js',
    "'precision mediump float;uniform sampler2D uTex;uniform float uAlpha;varying vec2 vUV;'+",
    "'precision mediump float;uniform sampler2D uTex;uniform float uAlpha;uniform vec3 uBg;uniform float uGrey;varying vec2 vUV;'+")
rep('js/engine/map/map-tiles.js',
    "'void main(){vec3 c=texture2D(uTex,vUV).rgb;gl_FragColor=vec4(mix(vec3(0.114,0.125,0.141),c,uAlpha),1.0);}');",
    "'void main(){vec3 c=texture2D(uTex,vUV).rgb;c=mix(c,vec3(dot(c,vec3(0.299,0.587,0.114))),uGrey);gl_FragColor=vec4(mix(uBg,c,uAlpha),1.0);}');   /* __acad3dV171b: the ground, and grey */")
rep('js/engine/map/map-tiles.js',
    "tex:gl.getUniformLocation(p,'uTex'),alpha:gl.getUniformLocation(p,'uAlpha')};",
    "tex:gl.getUniformLocation(p,'uTex'),alpha:gl.getUniformLocation(p,'uAlpha'),bg:gl.getUniformLocation(p,'uBg'),grey:gl.getUniformLocation(p,'uGrey')};")
rep('js/engine/map/map-tiles.js',
    "      gl.uniform1f(P.alpha,plan.opacity);\n",
    "      gl.uniform1f(P.alpha,plan.opacity);\n"
    "      var awM=bimAwBg(),awL=bimAwLook();gl.uniform3f(P.bg,awM[0],awM[1],awM[2]);gl.uniform1f(P.grey,awL?awL.grey:0);   /* __acad3dV171b */\n")
rep('js/engine/map/map-tiles.js',
    "      ctx.globalAlpha=plan.opacity;\n",
    "      ctx.globalAlpha=plan.opacity;\n      if(bimAwLook())ctx.filter='grayscale(1)';   /* __acad3dV171b */\n")
rep('js/engine/map/map-tiles.js',
    "r.opacity=st.opacity;",
    "r.opacity=st.opacity*(bimAwLook()?bimAwLook().fade:1);")   # __acad3dV171b: faded in the workspace

# ---- the words and the key in the mode's colours; the key at the bottom left ----
rep('js/engine/site-analysis/model-layers.js',
    "    ctx.lineWidth=3;ctx.strokeStyle=cap?'rgba(255,255,255,0.9)':'rgba(15,18,22,0.85)';ctx.lineJoin='round';\n",
    "    var awL=bimAwLook();   /* __acad3dV171b: the workspace's halo and ink */\n"
    "    ctx.lineWidth=3;ctx.strokeStyle=cap?'rgba(255,255,255,0.9)':(awL?awL.halo:'rgba(15,18,22,0.85)');ctx.lineJoin='round';\n")
rep('js/engine/site-analysis/model-layers.js',
    "    ctx.fillStyle=cap?'#1d2329':(col||'#e8edf2');\n",
    "    ctx.fillStyle=cap?'#1d2329':(awL?bimAwInk(col):(col||'#e8edf2'));\n")
rep('js/engine/site-analysis/model-analyses.js',
    "    if(sr.w<620)return null;   /* a phone's view: each analysis's row in Analyze carries its key */\n",
    "    if(sr.w<(bimAwLook()?280:620))return null;   /* a phone's view: each analysis's row in Analyze carries its key; __acad3dV171b: in the workspace, the one in focus's on the view */\n")
rep('js/engine/site-analysis/model-analyses.js',
    "      LY.X=sr.x+sr.w-LY.w-12;LY.Y=Y;LY.all=blocks.length;\n",
    "      LY.X=sr.x+sr.w-LY.w-12;LY.Y=Y;LY.all=blocks.length;\n"
    "      if(bimAwLook()){LY.X=sr.x+12;LY.Y=Math.max(sr.y+12,sr.y+sr.h-LY.h-12);}   /* __acad3dV171b: the workspace's, at the bottom left */\n")
rep('js/engine/site-analysis/model-analyses.js',
    "      ctx.globalAlpha=1;ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(X,Y,w,h);\n"
    "      ctx.strokeStyle='rgba(255,255,255,0.18)';",
    "      var awK=bimAwLook();awK=awK?awK.key:null;   /* __acad3dV171b: in the mode's colours */\n"
    "      ctx.globalAlpha=1;ctx.fillStyle=awK?awK.bg:'rgba(22,26,32,0.9)';ctx.fillRect(X,Y,w,h);\n"
    "      ctx.strokeStyle=awK?awK.line:'rgba(255,255,255,0.18)';")
rep('js/engine/site-analysis/model-analyses.js',
    "        if(op.k==='t'){ctx.font='bold 11px sans-serif';ctx.fillStyle='#e8edf2';ctx.fillText(op.t,ox,oy);continue;}\n"
    "        if(op.k==='s'){ctx.font='10px sans-serif';ctx.fillStyle='#9aa7b4';ctx.fillText(op.t,ox,oy);continue;}\n",
    "        if(op.k==='t'){ctx.font='bold 11px sans-serif';ctx.fillStyle=awK?awK.ink:'#e8edf2';ctx.fillText(op.t,ox,oy);continue;}\n"
    "        if(op.k==='s'){ctx.font='10px sans-serif';ctx.fillStyle=awK?awK.sub:'#9aa7b4';ctx.fillText(op.t,ox,oy);continue;}\n")
rep('js/engine/site-analysis/model-analyses.js',
    "        ctx.font='11px sans-serif';ctx.fillStyle='#e8edf2';ctx.fillText(op.t,ox+sw+4,oy);\n",
    "        ctx.font='11px sans-serif';ctx.fillStyle=awK?awK.ink:'#e8edf2';ctx.fillText(op.t,ox+sw+4,oy);\n")

# ---- the commands ----
rep('js/engine/commands/command-map.js',
    "    siteanalysis:function(){bimAnzView();},                      /* __acad3dV158; __acad3dV162: Analyze is one list */\n",
    "    siteanalysis:function(){bimAnzView();},                      /* __acad3dV158; __acad3dV162: Analyze is one list */\n"
    "    siteworkspace:function(){bimAwEnter();},                     /* __acad3dV171b: the analysis workspace */\n")
rep('js/engine/commands/command-map.js',
    "    traffic:function(){bimAnzView();bimSaGoto('access');bimTrCommand(true);},   /* __acad3dV171 */\n",
    "    traffic:function(){if(bimTrCommand(true))bimAwTraffic();else{bimAnzView();bimSaGoto('access');}},   /* __acad3dV171; __acad3dV171b: in focus in the workspace */\n")
rep('js/shell/shell.js',
    "    ['TRAFFIC',[",
    "    ['SITEWORKSPACE',['ANALYSISWORKSPACE','SAWORKSPACE','SITEWS'],'siteworkspace','The site analysis as a workspace: the analyses on the left, one in focus and others ticked under it; its panel on the right with what it shows, its settings, its chart, its key and its source; the view quiet in the app\\'s light or dark mode'],   /* __acad3dV171b */\n"
    "    ['TRAFFIC',[")
rep('js/engine/commands/command-catalogue.js',
    "  var BIM_CMD_TERMS={TRAFFIC:",
    "  var BIM_CMD_TERMS={SITEWORKSPACE:'analyses focus legend key workspace archimap forma diagram',TRAFFIC:")
done()
