"""falsify_phase108.py -- break the V108 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'incircle_inverted': [("if(dd<cc.r2*(1-1e-12))bad.push(tris[t]);else keep.push(tris[t]);", "if(dd>cc.r2*(1-1e-12))bad.push(tris[t]);else keep.push(tris[t]);")],
    'cavity_keeps_inner_edges': [("        if(cnt[a<b?a+'_'+b:b+'_'+a]!==1)continue;\n", "")],
    'contour_interpolated_wrong': [("if((ha>=0)!==(hb>=0)){u=ha/(ha-hb);", "if((ha>=0)!==(hb>=0)){u=hb/(hb-ha);")],
    'no_index_contours': [("out.push({level:lev,index:k%5===0,segs:segs});", "out.push({level:lev,index:false,segs:segs});")],
    'prism_not_split': [("      cp=bimClipHalfPlane(piece,-gx,-gz,g0);", "      cp=piece;")],
    'gradient_sign': [("      gz=((B[0]-A[0])*dC-(C[0]-A[0])*dB)/det;", "      gz=((C[0]-A[0])*dB-(B[0]-A[0])*dC)/det;")],
    'pad_not_clipped': [("      piece=bimClipToTri(pad,tr,tin.P);", "      piece=pad.slice();")],
    'outside_not_reported': [("note:r.outside>0.005?(r.outside.toFixed(2)+' m\\u00b2 off the surface, not measured'):''", "note:''")],
    'usft_as_ft': [("var BIM_SURVEY_UNITS={m:1,ft:0.3048,usft:1200/3937};", "var BIM_SURVEY_UNITS={m:1,ft:0.3048,usft:0.3048};")],
    'true_north_ignored': [("tn=(tnDeg||0)*Math.PI/180,ct=Math.cos(tn)", "tn=0,ct=Math.cos(tn)")],
    'north_sign': [("return [dE*ct+dN*st,dE*st-dN*ct,(r.z-base.z)*u,", "return [dE*ct+dN*st,dE*st+dN*ct,(r.z-base.z)*u,")],
    'header_not_reported': [("if(ok&&isFinite(rec.n)&&isFinite(rec.e)&&isFinite(rec.z))out.push(rec);else bad.push(i+1);", "if(ok&&isFinite(rec.n)&&isFinite(rec.e)&&isFinite(rec.z))out.push(rec);")],
    'base_not_kept': [("      A3D.site.surveyBase={n:base.n,e:base.e,z:base.z,units:units};\n", "")],
    'pad_not_undoable': [("    pushUndo();\n    if(v==='')delete o.gradeElev;else o.gradeElev=n;", "    if(v==='')delete o.gradeElev;else o.gradeElev=n;")],
    'pad_field_not_wired': [("      if(f==='gradeelev'){bimSetGradeElev(o,inp.value);return;}      /* __acad3dV108 */\n", "")],
    'interval_ignored': [("    if(isFinite(v)&&v>0)return v;\n    r=bimTerrainRange(tin);", "    r=bimTerrainRange(tin);")],
    'not_in_bounds': [("      }else if(o.t==='terrain'&&o.survey&&o.survey.length){   /* __acad3dV108", "      }else if(false){   /* __acad3dV108")],
    'drawn_in_3d': [("    A3D.lastTerrainDrawn=null;\n    if(!A3D.flat||A3D.section)return;", "    A3D.lastTerrainDrawn=null;\n    if(A3D.section)return;")],
    'command_does_nothing': [("    survey:function(){openSurveyDlg();},", "    survey:function(){},")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV108' in txt
out.write_text(txt, encoding='utf-8')
