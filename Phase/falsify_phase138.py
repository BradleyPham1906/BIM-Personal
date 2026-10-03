"""falsify_phase138.py -- break the V138 build one way at a time, keeping the marker.

Each variant takes back one thing V138 does, and the V138 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 138a: read
    'skipped_unsaid': [("    item('read','Read',skipped.length?'warn':'pass',", "    item('read','Read','pass',")],
    'duplicates_unnamed': [("      if(seen[k]){dup++;dupNames.push(String(model[i][3]||('#'+(i+1))));continue;}", "      if(seen[k]){dup++;continue;}")],
    'duplicates_not_kept': [("    if(src&&typeof src==='object'&&dupNames.length)src.duplicates=dupNames.slice(0,200);   /* __acad3dV138 */\n", "")],
    # ---- 138a: the surface
    'fidelity_lenient': [("      item('fidelity','Through every point',(maxr<=BIM_SURVEY_TOL.fidelity&&!out)?'pass':'fail',", "      item('fidelity','Through every point','pass',")],
    # ---- 138a: bust shots
    'busts_ignored': [("      if(bi<0||best<=thr)break;", "      break;")],
    'busts_no_floor': [("      thr=Math.max(BIM_SURVEY_TOL.bustMin,BIM_SURVEY_TOL.bustK*mad);", "      thr=BIM_SURVEY_TOL.bustK*mad;")],
    'busts_not_set_aside': [("        if(flag[i]){devs.push(null);continue;}", "        if(false){devs.push(null);continue;}")],
    'busts_mean_not_plane': [("        if(cnt>=3){\n          var det=", "        if(false){\n          var det=")],
    'corners_one_ring': [("        if(J.length<3)for(k=0,k2=J.length;k<k2;k++)", "        if(false)for(k=0,k2=J.length;k<k2;k++)")],
    'busts_dont_fail': [("      item('busts','Bust shots',bs.length?'fail':'pass',", "      item('busts','Bust shots',bs.length?'warn':'pass',")],
    # ---- 138a: check shots
    'checks_in_surface': [("        if(code&&String(res.points[q].d||'').replace(/^\\s+/,'').toUpperCase().indexOf(code)===0)chk.push(res.points[q]);else pts.push(res.points[q]);",
                           "        pts.push(res.points[q]);")],
    'checks_not_kept': [("      if(o&&chk.length)o.checks=bimSurveyToModel(chk,units,base,bimTrueNorthDeg());", "")],
    'checks_no_offset': [("        h=bimTinHeightAt(tin,ch[i][0]+x[0],ch[i][1]+x[2]);", "        h=bimTinHeightAt(tin,ch[i][0],ch[i][1]+50);")],
    'rmse_as_mean': [("var nIn=res.length-oo,rmse=nIn?Math.sqrt(sq/nIn):null;", "var nIn=res.length-oo,rmse=nIn?Math.sqrt(sq)/nIn:null;")],
    'no_code_takes_all': [("var code=String(checkCode==null?BIM_SURVEY_CHECK_CODE:checkCode)", "var code=String(checkCode?checkCode:BIM_SURVEY_CHECK_CODE)")],
    # ---- 138a: control
    'control_no_units': [("      var want=(ctl[i].z-bz)*u,df=", "      var want=(ctl[i].z-bz),df=")],
    'control_no_base': [("      var want=(ctl[i].z-bz)*u,df=", "      var want=ctl[i].z*u,df=")],
    'control_missing_ok': [("ok=df!==null&&Math.abs(df)<=BIM_SURVEY_TOL.control;", "ok=df===null||Math.abs(df)<=BIM_SURVEY_TOL.control;")],
    'control_not_checkshots': [("      if(got===null)for(j=0;j<(o.checks||[]).length;j++)if(String(o.checks[j][3])===nm){got=o.checks[j][2]+bimObjOffset(o)[1];break;}\n", "")],
    'control_not_undoable': [("    pushUndo();\n    if(out.length)o.control=out;else delete o.control;", "    if(out.length)o.control=out;else delete o.control;")],
    'control_typo_accepted': [("    if(bad.length){a3dToast('A control point is name=elevation", "    if(false){a3dToast('A control point is name=elevation")],
    # ---- 138a: public terrain
    'feet_unsaid': [("          if(Math.abs(slope-1/0.3048)<0.45){note=", "          if(false){note=")],
    'offset_unsaid': [("        if(!note&&Math.abs(off)>BIM_SURVEY_TOL.offsetWarn){", "        if(false){")],
    'relief_threshold_high': [("        if(rel>=0.25){slope=sxy/sxx;", "        if(rel>=2){slope=sxy/sxx;")],
    # ---- 138a: verdict, cache, report
    'warn_is_pass': [("if(items[i].status==='warn')verdict='warn';}", "}")],
    'cache_never_cleared': [("    if(c&&c.key===key)return c.r;", "    if(c)return c.r;")],
    'report_no_tolerances': [("    h+='</table><p>Tolerances: surface '", "    h+='</table><p>'+'' +'' +'' +'Limits: surface '")],
    # ---- 138b
    'no_group': [("    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Survey Check',bimSurveyCheckHtml(o));   /* __acad3dV138 */\n", "")],
    'control_input_ignored': [("    if(f.getAttribute('data-propsurvey')==='control'&&o)bimSurveySetControl(o,f.value);", "")],
    'export_not_wired': [("    if(b.getAttribute('data-propsurveyact')==='export'&&o)bimSurveyReportExport(o);", "")],
    'file_not_read': [("      rd.onload=function(){d.querySelector('[data-a3dp=\"pts\"]').value=String(rd.result||'');", "      rd.onload=function(){")],
    'dialog_code_ignored': [("      bimImportSurvey(res,fmt,units,base,chk);   /* __acad3dV138: the check shots */", "      bimImportSurvey(res,fmt,units,base,'');")],
    'no_command': [("    surveycheck:function(){bimSurveyCheckCommand();},  /* __acad3dV138 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV138' in txt
out.write_text(txt, encoding='utf-8')
