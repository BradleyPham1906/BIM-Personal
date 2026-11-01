#!/usr/bin/env python3
"""V172b, patch b: Ladybug's four figures on the Climate and risk board. reference/research-ladybug-weather-comfort.md.

js/engine/ladybug/figures.js (new) draws the kept results in the board's style. Once Ladybug has run, its figures
follow the board's own (UTCI in the four conditions, the psychrometric chart with the comfort and strategy zones, the
wind rose, the design days), numbered on; the board's notes name Ladybug, its version and the weather it read.
Before a run, and offline, the board is exactly as it was.

Run from the repository root: python3 Phase/patch_v172b_b.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done, ROOT   # noqa: E402

begin('3aec44f4e8daaff992d67d0804962817706df94c10b77446a071c5b826a9b9d6')   # patch a

rep('index.html', '<!-- @include js/engine/ladybug/analyses.js -->\n',
    '<!-- @include js/engine/ladybug/analyses.js -->\n<!-- @include js/engine/ladybug/figures.js -->\n')
rep('js/engine/site-analysis/climate-board.js', "    h+=cards.join('')+'</section>';\n",
    "    /* __acad3dV172b: Ladybug's figures, once it has run, after the board's own */\n"
    "    var lbAny=false;\n"
    "    BIM_LB_FIGS.forEach(function(F){var c=null;try{c=F[1](null,fig+1);}catch(eLb){console.warn('[BIM] Ladybug figure '+F[0],eLb);}if(c){fig++;lbAny=true;cards.push(c.replace('<figure class=\"a3d-clb-card','<figure data-figid=\"'+F[0]+'\" class=\"a3d-clb-card'));}});\n"
    "    h+=cards.join('')+'</section>';\n")
rep('js/engine/site-analysis/climate-board.js',
    "      '<li>Earthquakes: the <a href=\"https://earthquake.usgs.gov/\" target=\"_blank\" rel=\"noopener\">USGS</a> catalogue",
    "      (lbAny?'<li>Comfort, design days and the Ladybug wind rose: <a href=\"https://www.ladybug.tools/\" target=\"_blank\" rel=\"noopener\">Ladybug Tools</a>\\' own code (AGPL-3.0), unchanged, run in the browser by Pyodide, on '+bimClbE(bimLbSrcWords(bimLbSrcKept()))+'.</li>':'')+\n"
    "      '<li>Earthquakes: the <a href=\"https://earthquake.usgs.gov/\" target=\"_blank\" rel=\"noopener\">USGS</a> catalogue")

rep('js/engine/site-analysis/climate-board.js', "Get climate and risk</button></div></div></div>';\n",
    "Get climate and risk</button></div></div>'+bimLbOnlyFigs()+'</div>';   /* __acad3dV172b: Ladybug's figures, an EPW's, with no Open-Meteo climate */\n")

LAY = ROOT / 'tools' / 'app_layout.py'
s = LAY.read_text(encoding='utf-8')
a = "    ('ladybug/analyses.js', '  /* ================= __acad3dV172b: the analyses, run and kept ================='),\n"
assert s.count(a) == 1
s = s.replace(a, a + "    ('ladybug/figures.js', '  /* ================= __acad3dV172b: the Ladybug analyses as board figures ================='),\n")
LAY.write_text(s, encoding='utf-8')
done()
