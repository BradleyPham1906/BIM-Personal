"""patch_phase96e.py -- __acad3dV96: a hatch draws in Technical mode.

Found by the suite. Every pattern this library has drawn since Phase 53 is a presentation-mode
appearance override, so all four sinks gate on `pres` -- and the hatch branches added in 96b
inherited that gate without my noticing, because the CANVAS path does not go through it and the
canvas was what I looked at. The object existed, the pattern was stored, the screen showed it,
and the SVG export of a Technical drawing contained no hatch at all.

That is the exact shape of the V86 fault: the thing that renders and the thing that exports
disagreeing, with only one of them in front of you.

The fix is one predicate rather than four edited conditions. A graphics dict now carries
`explicit`, which bimHatchGraphics sets and nothing else does, and the gate asks
bimPatternAlways(pres,rg) in all four places. Mode-driven appearance keeps the behaviour it has
always had; drawn geometry is not mode-driven.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'f2e791dc90d02d567436a8c54a1c9fd1a4637a01bf56a4e4f825b1be965bf806'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # the one predicate, beside the rotation function both sinks already share
    ("""  function bimPatternRotation(angleDeg,yDown){""",
     """  /* __acad3dV96: does this appearance draw whatever the mode is?

     Everything the pattern library drew before this phase was a presentation-mode override, so
     every sink gated on presentation mode. A hatch is drawn geometry and is not mode-driven, so
     it carries `explicit` and the four gates ask here instead of each deciding for itself. */
  function bimPatternAlways(pres,rg){
    return !!(rg&&(pres||rg.explicit));
  }
  function bimPatternRotation(angleDeg,yDown){"""),

    ("""  function bimHatchGraphics(o){
    var g=bimDefaultGraphics();
    if(!o)return g;""",
     """  function bimHatchGraphics(o){
    var g=bimDefaultGraphics();
    g.explicit=true;   /* __acad3dV96: drawn geometry, not a presentation-mode appearance */
    if(!o)return g;"""),

    # --- bimBuildSVG
    ("""    function styleAttrs(rg,fillOn){
      if(!pres||!rg)return {fill:'none',extra:''};
      var fillVal=(fillOn&&rg.fill!=='none')?rg.fill:'none';
      var sw=Math.max(strokeW*0.1,svgLwUnit*rg.lineWeight);""",
     """    function styleAttrs(rg,fillOn){
      if(!bimPatternAlways(pres,rg))return {fill:'none',extra:''};   /* __acad3dV96 */
      var fillVal=(fillOn&&rg.fill!=='none')?rg.fill:'none';
      var sw=Math.max(strokeW*0.1,svgLwUnit*rg.lineWeight);"""),

    ("""    function patternOverlay(cmd,d,extraAttrs){
      if(!pres||!cmd.rg)return null;""",
     """    function patternOverlay(cmd,d,extraAttrs){
      if(!bimPatternAlways(pres,cmd.rg))return null;   /* __acad3dV96 */"""),

    # --- bimBuildPlanViewportSVG
    ("""    function styleAttrs(rg,fillOn){
      if(!pres||!rg)return {fill:'none',extra:''};
      var fillVal=(fillOn&&rg.fill!=='none')?rg.fill:'none';
      var extra=' stroke="'+rg.lineColor+'" stroke-width="'+Math.max(0.02,rg.lineWeight).toFixed(3)+'"'""",
     """    function styleAttrs(rg,fillOn){
      if(!bimPatternAlways(pres,rg))return {fill:'none',extra:''};   /* __acad3dV96 */
      var fillVal=(fillOn&&rg.fill!=='none')?rg.fill:'none';
      var extra=' stroke="'+rg.lineColor+'" stroke-width="'+Math.max(0.02,rg.lineWeight).toFixed(3)+'"'"""),

    ("""    function patternOverlay(rg,objId,d,extraAttrs){
      if(!pres||!rg)return;""",
     """    function patternOverlay(rg,objId,d,extraAttrs){
      if(!bimPatternAlways(pres,rg))return;   /* __acad3dV96 */"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
