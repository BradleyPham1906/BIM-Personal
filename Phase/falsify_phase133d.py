"""falsify_phase133d.py -- break V133d and V133e one way at a time, keeping the markers.

Each variant takes back one thing they do, and the 133d suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 133d: the map on a real screen
    # RE-ANCHORED IN V133f: the street map is Esri's
    'carto_street': [("url:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}'", "url:'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'")],
    'no_retina_tiles': [(".split('{r}').join(bimMapDpr()>1.5?'@2x':'');", ".split('{r}').join('');")],
    'density_ignored': [("    var dz=tpl.indexOf('{r}')>=0?1:bimMapDpr(),", "    var dz=1,")],
    'density_counted_twice': [("    var dz=tpl.indexOf('{r}')>=0?1:bimMapDpr(),", "    var dz=bimMapDpr(),")],
    'cap_fixed': [("maxT=Math.round(BIM_MAP_MAXT*bimMapDpr());", "maxT=BIM_MAP_MAXT;")],
    'no_mipmaps': [("if(tw&&th&&!(tw&(tw-1))&&!(th&(th-1))){", "if(false){")],
    'refusal_generic': [("(hs===403?'refused it (HTTP 403)", "(hs===-1?'refused it (HTTP 403)")],
    'busy_generic': [("(hs===429?'is busy (HTTP 429)", "(hs===-1?'is busy (HTTP 429)")],
    # ---- 133e: zoom
    'zoom_capped': [("var BIM_ZOOM_MIN=0.5,BIM_ZOOM_MAX=200000;", "var BIM_ZOOM_MIN=6,BIM_ZOOM_MAX=150;")],
    'zoom_about_centre': [("      if(p1){c.tx+=p0[0]-p1[0];c.tz+=p0[2]-p1[2];}\n", "")],
    'far_fixed': [("    var near=camDist>1000?camDist/2000:0.5,far=Math.max(4000,camDist*8);", "    var near=0.5,far=4000;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV133e' in txt
out.write_text(txt, encoding='utf-8')
