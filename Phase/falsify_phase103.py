"""falsify_phase103.py -- break the V103 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'se_quadrant_wrong': [("    else if(ns==='S'&&ew==='E')az=180-a;", "    else if(ns==='S'&&ew==='E')az=180+a;")],
    'seconds_ignored': [("    var a=deg+mi/60+se/3600;", "    var a=deg+mi/60;")],
    'minutes_unchecked': [("    if(mi>=60||se>=60)return {error:'minutes and seconds must be under 60'};\n", "")],
    'over_90_accepted': [("    if(a>90)return {error:'a quadrant bearing is 90 degrees at most'};\n", "")],
    'traverse_ignores_true_north': [("      az=legs[i].az*Math.PI/180+tn;", "      az=legs[i].az*Math.PI/180;")],
    'north_is_plus_z': [("      x+=legs[i].d*Math.sin(az);z-=legs[i].d*Math.cos(az);", "      x+=legs[i].d*Math.sin(az);z+=legs[i].d*Math.cos(az);")],
    'misclosure_hidden': [("    var ex=x-start[0],ez=z-start[1],mis=Math.sqrt(ex*ex+ez*ez);", "    var ex=0,ez=0,mis=0;")],
    'setback_outward': [("    var n=ring.length,i,sgn=bimPolySignedArea(ring)>0?1:-1,lines=[],out=[];",
                         "    var n=ring.length,i,sgn=bimPolySignedArea(ring)>0?-1:1,lines=[],out=[];")],
    'setback_one_value': [("s=(sb&&isFinite(sb[i]))?+sb[i]:0;", "s=(sb&&isFinite(sb[0]))?+sb[0]:0;")],
    'no_violations': [("      if(bad)list.push({id:b.id,name:b.name});", "")],
    'parse_legs_no_line_numbers': [("      if(b.error){errs.push('line '+(i+1)+': '+b.error);continue;}", "      if(b.error){errs.push(b.error);continue;}")],
    'dialog_no_closure': [("      cl.textContent=r.p.errors.length?'':bimClosureText(bimTraverse(r.start,r.p.legs));", "      cl.textContent='';")],
    'dialog_accepts_bad': [("      if(r.p.errors.length){eb.textContent=r.p.errors.join('; ');return;}\n      closeDlg();", "      closeDlg();")],
    'not_pickable': [("||bimPickHatch(x,y)||bimPickProperty(x,y);", "||bimPickHatch(x,y);")],
    'arrow_ignores_true_north': [("    var tn=bimTrueNorthDeg()*Math.PI/180,c=A3D.cam;", "    var tn=0,c=A3D.cam;")],
    'no_true_north_field': [("    rows+=bimPropRow('True North (deg)','<input type=\"number\" step=\"any\" data-propmodel=\"truenorth\" value=\"'+bimTrueNorthDeg()+'\">');   /* __acad3dV103 */\n", "")],
    'dxf_no_bearings': [("               bimFormatBearing(o.legs[lk].az,'%%d')+' '+o.legs[lk].d.toFixed(2),0.25,lay);", "               '',0.25,lay);")],
    'fit_ignores_property': [("      }else if(bimIsProperty(o)||((o.t==='text'||o.t==='roomtag')&&o.pt)){", "      }else if(false){")],
    'no_site_panel': [("      {t:'Site',small:['bim:property','bim:propshape','bim:truenorth']}   /* __acad3dV103 */", "      {t:'Site',small:[]}")],
    'shape_legs_reversed_axis': [("      dE=b[0]-a[0];dN=-(b[1]-a[1]);d=Math.sqrt(dE*dE+dN*dN);", "      dE=b[0]-a[0];dN=(b[1]-a[1]);d=Math.sqrt(dE*dE+dN*dN);")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV103' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
