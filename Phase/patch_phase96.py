"""patch_phase96.py -- __acad3dV96: pattern ANGLE, end to end.

Phase 53 built a pattern library with nine tiles and wired it into three sinks. It has no angle.
Angle is baked into the tile names instead -- 'diagonal' and 'diagonal-reverse' are separate
patterns -- so a hatch cannot be set to 30 degrees, and AutoCAD's HATCH expects exactly that.
Shipping a HATCH command with an angle field it could not honour is the decorative control
Product Principle 1 forbids, so the angle goes in first, before any hatch object exists.

Three things here, and the second and third are consequences of the first:

1. patternAngle joins the graphics dict, is clamped and persisted like the rest, and is applied
   by every sink through ONE function, bimPatternRotation.

   The sign matters and is the part that would be silently wrong. Both sinks draw with y
   increasing DOWNWARD -- the SVG writers emit -y, the canvas is screen space -- so a model
   angle measured counter-clockwise from +x has to be applied as its negative in both. One
   function answers that for both, rather than each sink getting the sign right or wrong on its
   own.

2. The two graphics sanitizers were the SAME eight field checks written out twice, differing
   only in what an absent key means. Adding a ninth key to two copies is how the two copies
   start disagreeing, so the field validation is extracted into bimApplyGraphicsFields and both
   sanitizers call it. They keep their opposite absence semantics, which is the only thing that
   was ever actually different between them.

3. bimMaterialPattern read a material card's hatch {angle, gap, cross} and used the angle ONLY
   to choose between four fixed tile names, then threw it away. A 30-degree material hatch
   rendered at 45. With patternAngle in the dict the card's own angle is carried through, so the
   same material now hatches at the same angle in both engines -- which is what the comment
   under it already claimed was the point.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '366102f030ad3f5ef845a8d37029ce6db409af29a754b83222d99b5c9b09ff89'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  var BIM_GRAPHICS_KEYS=['lineWeight','lineColor','fill','pattern','opacity','shadow','patternColor','patternScale'];""",
     """  var BIM_GRAPHICS_KEYS=['lineWeight','lineColor','fill','pattern','opacity','shadow','patternColor','patternScale','patternAngle'];"""),

    ("""    return {lineWeight:0.25,lineColor:'#000000',fill:'none',pattern:'none',opacity:1,shadow:false,
            patternColor:'#555555',patternScale:1};""",
     """    /* __acad3dV96: patternAngle defaults to 0, so a project saved before this phase resolves
       the appearance it always did. */
    return {lineWeight:0.25,lineColor:'#000000',fill:'none',pattern:'none',opacity:1,shadow:false,
            patternColor:'#555555',patternScale:1,patternAngle:0};"""),

    # --- one field validator, called by both sanitizers
    ("""  function bimValidGraphicsColor(v){""",
     """  /* __acad3dV96: the field checks, once. bimSanitizeGraphics and bimSanitizeGraphicsOverride
     had identical copies of this list and differed only in what an ABSENT key means -- defaults
     for a full set, inherit-from-type for an override. That difference lives in the callers; the
     validation lives here, so a new key is added in one place and the two cannot drift. */
  function bimApplyGraphicsFields(src,dst){
    if(!src||typeof src!=='object'||!dst)return dst;
    if(typeof src.lineWeight==='number'&&isFinite(src.lineWeight)&&src.lineWeight>0)dst.lineWeight=src.lineWeight;
    if(bimValidGraphicsColor(src.lineColor)&&src.lineColor!=='none')dst.lineColor=src.lineColor;
    if(bimValidGraphicsColor(src.fill))dst.fill=src.fill;
    if(typeof src.pattern==='string'&&BIM_HATCH_PATTERNS.indexOf(src.pattern)>=0)dst.pattern=src.pattern;
    if(typeof src.opacity==='number'&&isFinite(src.opacity))dst.opacity=Math.max(0,Math.min(1,src.opacity));
    if(typeof src.shadow==='boolean')dst.shadow=src.shadow;
    /* __acad3dV63: patternColor reuses the same colour validator as lineColor and, like it,
       rejects 'none' (a hatch with no colour is just 'pattern:none', which the pattern field
       already expresses). patternScale is clamped to a range that stays drawable at both ends:
       below ~0.1 the tile collapses to sub-pixel noise, above 8 it is a single line per face. */
    if(bimValidGraphicsColor(src.patternColor)&&src.patternColor!=='none')dst.patternColor=src.patternColor;
    if(typeof src.patternScale==='number'&&isFinite(src.patternScale)&&src.patternScale>0)
      dst.patternScale=Math.max(0.1,Math.min(8,src.patternScale));
    /* __acad3dV96: normalised into [0,180). A hatch line at 200 degrees is the same field of
       lines as one at 20, so storing it any other way gives two values that draw identically
       and compare unequal. */
    if(typeof src.patternAngle==='number'&&isFinite(src.patternAngle))
      dst.patternAngle=((src.patternAngle%180)+180)%180;
    return dst;
  }
  /* __acad3dV96: what rotation a sink applies for a MODEL angle. Both sinks draw with y
     increasing downward -- the SVG writers emit -y and the canvas is screen space -- so a model
     angle measured counter-clockwise from +x is applied as its negative in both. One answer for
     both, because a sign that is right in one sink and wrong in the other is invisible until
     someone exports a drawing and compares it with the screen. */
  function bimPatternRotation(angleDeg,yDown){
    var a=(typeof angleDeg==='number'&&isFinite(angleDeg))?(((angleDeg%180)+180)%180):0;
    return yDown?-a:a;
  }
  function bimValidGraphicsColor(v){"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

# --- both sanitizer bodies collapse to a call
OLD_BODY = """      if(typeof src.lineWeight==='number'&&isFinite(src.lineWeight)&&src.lineWeight>0)out[m].lineWeight=src.lineWeight;
      if(bimValidGraphicsColor(src.lineColor)&&src.lineColor!=='none')out[m].lineColor=src.lineColor;
      if(bimValidGraphicsColor(src.fill))out[m].fill=src.fill;
      if(typeof src.pattern==='string'&&BIM_HATCH_PATTERNS.indexOf(src.pattern)>=0)out[m].pattern=src.pattern;
      if(typeof src.opacity==='number'&&isFinite(src.opacity))out[m].opacity=Math.max(0,Math.min(1,src.opacity));
      if(typeof src.shadow==='boolean')out[m].shadow=src.shadow;
      /* __acad3dV63: patternColor reuses the same colour validator as lineColor and, like it,
         rejects 'none' (a hatch with no colour is just 'pattern:none', which the pattern field
         already expresses). patternScale is clamped to a range that stays drawable at both ends:
         below ~0.1 the tile collapses to sub-pixel noise, above 8 it is a single line per face. */
      if(bimValidGraphicsColor(src.patternColor)&&src.patternColor!=='none')out[m].patternColor=src.patternColor;
      if(typeof src.patternScale==='number'&&isFinite(src.patternScale)&&src.patternScale>0)
        out[m].patternScale=Math.max(0.1,Math.min(8,src.patternScale));"""
NEW_BODY = """      bimApplyGraphicsFields(src,out[m]);   /* __acad3dV96 */"""
assert txt.count(OLD_BODY) == 2, 'sanitizer body count %d' % txt.count(OLD_BODY)
txt = txt.replace(OLD_BODY, NEW_BODY)

MORE = [
    # --- the material's own angle stops being discarded
    ("""    return {pattern:name,patternColor:card.color||'#555555',
      fill:bimTintColor(card.color||'#555555',0.62),
      patternScale:Math.max(0.1,Math.min(8,(h.gap||8)/8))};""",
     """    /* __acad3dV96: the card's ANGLE is carried through rather than thrown away after being
       used to pick a tile name. Before this a 30-degree material hatch chose the 'diagonal'
       tile and then drew at 45, so the two engines disagreed about the same material -- which
       is the one thing the note above says must not happen. The four fixed names keep their
       own built-in direction, so the residual angle is what is left after that choice. */
    var baseAng=(name==='vertical')?90:((name==='diagonal')?45:((name==='diagonal-reverse')?135:0));
    return {pattern:name,patternColor:card.color||'#555555',
      fill:bimTintColor(card.color||'#555555',0.62),
      patternAngle:((a-baseAng)%180+180)%180,
      patternScale:Math.max(0.1,Math.min(8,(h.gap||8)/8))};"""),

    # --- canvas sink applies the rotation
    ("""    var tile=bimPatternTile(rg.pattern,col,sz.w,sz.h,sz.sc);
    if(!tile)return null;
    try{return ctx.createPattern(tile,'repeat');}
    catch(eP){console.warn('[BIM] Pattern fill unavailable: ',eP);return null;}""",
     """    var tile=bimPatternTile(rg.pattern,col,sz.w,sz.h,sz.sc);
    if(!tile)return null;
    try{
      var pat=ctx.createPattern(tile,'repeat');
      /* __acad3dV96: the angle, through the one rotation function both sinks use. Guarded
         because setTransform and DOMMatrix are not universal; without them the pattern draws
         unrotated rather than not at all. */
      var ang=bimPatternRotation(rg.patternAngle,true);
      if(pat&&ang&&typeof pat.setTransform==='function'&&typeof DOMMatrix!=='undefined'){
        try{pat.setTransform(new DOMMatrix().rotate(ang));}
        catch(eR){console.warn('[BIM] Pattern rotation unavailable: ',eR);}
      }
      return pat;
    }
    catch(eP){console.warn('[BIM] Pattern fill unavailable: ',eP);return null;}"""),

    # --- SVG sink applies the rotation
    ("""  function bimPatternSvgDef(id,name,color,unitsPerMm,scale,flipY){""",
     """  function bimPatternSvgDef(id,name,color,unitsPerMm,scale,flipY,angleDeg){"""),

    ("""    return '<pattern id="'+id+'" patternUnits="userSpaceOnUse" width="'+tw.toFixed(6)+
           '" height="'+th.toFixed(6)+'">'+body+'</pattern>';""",
     """    /* __acad3dV96: same rotation function the canvas sink uses, so a drawing on screen and
       the SVG exported from it cannot disagree about which way a hatch runs. */
    var rot=bimPatternRotation(angleDeg,!!flipY);
    var xf=rot?(' patternTransform="rotate('+rot.toFixed(4)+')"'):'';
    return '<pattern id="'+id+'" patternUnits="userSpaceOnUse" width="'+tw.toFixed(6)+
           '" height="'+th.toFixed(6)+'"'+xf+'>'+body+'</pattern>';"""),

    # --- the registry interns per angle too, or every angle shares one definition
    ("""        var sc=(rg.patternScale>0)?rg.patternScale:1;
        var key=rg.pattern+'|'+col+'|'+sc;
        if(!map[key]){
          var id=prefix+(++n);
          var d=bimPatternSvgDef(id,rg.pattern,col,unitsPerMm,sc,flipY);""",
     """        var sc=(rg.patternScale>0)?rg.patternScale:1;
        /* __acad3dV96: the angle is part of the identity. Without it the first hatch to use a
           pattern would define it and every later one at a different angle would reference that
           same definition -- the angle would be stored, shown in the panel, and ignored. */
        var ang=(typeof rg.patternAngle==='number'&&isFinite(rg.patternAngle))?rg.patternAngle:0;
        var key=rg.pattern+'|'+col+'|'+sc+'|'+ang;
        if(!map[key]){
          var id=prefix+(++n);
          var d=bimPatternSvgDef(id,rg.pattern,col,unitsPerMm,sc,flipY,ang);"""),
]

for old, new in MORE:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
