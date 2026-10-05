"""falsify_phase158.py -- break the V158 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # RETIRED IN V159: the owner asked for Site analysis inside Analyze; there is no Site tab to remove. V159's
    # falsify file breaks the switch that replaced it.
    # 'no_site_tab': [("      '<button type=\"button\" class=\"a3d-railbtn\" data-tab=\"site\" data-short=\"Site\" title=\"Site analysis\" aria-label=\"Site analysis\">'+   /* __acad3dV158 */\n      bimRailIcon('site')+'</button>'+\n", "")],
    'nine_categories': [("    {id:'people',n:'People and place',", "    {id:'people',hide:1,n:'People and place',"), ("  function bimSaCat(id){var i;", "  BIM_SA_CATS=BIM_SA_CATS.slice(0,9);\n  function bimSaCat(id){var i;")],
    'refill_doubles': [("      f=null;s.findings.forEach(function(x){if(x.auto===A[i].auto)f=x;});", "      f=null;")],
    'refill_overwrites_class': [("        if(!f.touched){f.cls=", "        if(true){f.cls=")],
    'stale_kept': [("      del++;return false;", "      return true;")],
    'noted_dropped': [("      if(x.note||x.photo||x.at||x.touched){x.auto='';return true;}", "")],
    'no_source': [("source:osm,date:od});\n    }\n    var P=A3D.objs.filter(bimIsProperty);", "source:'',date:od});\n    }\n    var P=A3D.objs.filter(bimIsProperty);")],
    'no_stage_move': [("    if(s.stage<1)s.stage=1;\n", "")],
    'no_property': [("    var P=A3D.objs.filter(bimIsProperty);\n    if(P.length){", "    var P=[];\n    if(P.length){")],
    'slope_unweighted': [("      area+=A;sum+=g*A;if(g>mx)mx=g;if(g>0.15)steep+=A;", "      area+=1;sum+=g;if(g>mx)mx=g;if(g>0.15)steep+=1;")],
    'datum_ignored': [("        var off=dat!==null&&dat!==undefined?dat:0,", "        var off=0,")],
    'day_length_wrong': [("var m=Math.round(r.sunset-r.sunrise);", "var m=Math.round(r.sunset-r.noon);")],
    'airport_not_constraint': [("aircraft noise and height limits are likely',cls:'constraint',sev:2", "aircraft noise and height limits are likely',cls:'neutral',sev:1")],
    'uses_not_counted': [("      if(c.use)uses[c.use]=(uses[c.use]||0)+1;", "")],
    'bad_class_taken': [("    else if(k==='cls'){if(!bimSaPair(BIM_SA_CLS,v))return false;}", "    else if(k==='cls'){}")],
    'bad_sev_taken': [("v=parseInt(v,10);if(!(v>=1&&v<=3))return false;}\n    else if(k==='date')", "v=parseInt(v,10);}\n    else if(k==='date')")],
    'edit_not_undoable': [("    if(f[k]===v)return true;\n    pushUndo();\n    f[k]=v;", "    if(f[k]===v)return true;\n    f[k]=v;")],
    'numbered_globally': [("    for(i=0;i<F.length;i++){if(F[i].cat===f.cat)k++;if(F[i]===f)break;}", "    for(i=0;i<F.length;i++){k++;if(F[i]===f)break;}")],
    'check_any_key': [("    if(!c||!(+m[3]<(m[2]==='d'?c.desk:c.visit).length))return false;", "    if(!m)return false;")],
    'stage_unbounded': [("v=parseInt(v,10);if(!(v>=0&&v<BIM_SA_STAGES.length))return false;}", "v=parseInt(v,10);}")],
    'pin_not_placed': [("      bimSaPlace(saF,[gx,gz]);", "      bimSaPlace(saF,null);")],
    'pins_not_drawn': [("    if(!capMode)drawSaPins(ctx,V,W,H);   /* __acad3dV158: the site analysis findings */", "")],
    'pins_not_hidden': [("    if(!s||!s.pins||!Array.isArray(s.findings)||A3D.section)return;", "    if(!s||!Array.isArray(s.findings)||A3D.section)return;")],
    'photo_full_size': [("var k=Math.min(1,BIM_SA_PHOTO_PX/Math.max(im.width,im.height))", "var k=1")],
    'no_red_flags_block': [("    if(R.length)h+='<div class=\"a3d-saflags\">", "    if(false)h+='<div class=\"a3d-saflags\">")],
    'panel_field_ignored': [("      if((k=e.getAttribute('data-saff'))){var i=k.lastIndexOf(':');bimSaSet(k.slice(0,i),k.slice(i+1),e.value);return;}", "")],
    'phone_small_fields': [(".a3d-sa select,.a3d-sa input[type=text],.a3d-sa input[type=date],.a3d-sa textarea{min-height:36px;font-size:16px}", "")],
    # RE-ANCHORED FOR V159: SITEANALYSIS opens Analyze on Site analysis
    'no_command': [("    siteanalysis:function(){bimAnzView('site');},                /* __acad3dV158; __acad3dV159: in Analyze */\n", "")],
    # 158b: Analysis and Data as layer groups
    'group_eye_dead': [("    if((b=t.closest('[data-lysecon]'))){bimLySecVisible(b.getAttribute('data-lysecon'));return true;}   /* __acad3dV158 */\n", "")],
    'group_not_dim': [("return '<div class=\"a3d-lysec'+(off?' dim':'')+'\" data-lysec=", "return '<div class=\"a3d-lysec\" data-lysec=")],
    'group_eye_misaligned': [("(off?'Show ':'Hide ')+'everything in '+label,BIM_LY_IC.off,BIM_LY_IC.on)+'<span class=\"a3d-lyi a3d-lyspc\" aria-hidden=\"true\"></span><span class=\"a3d-lyi a3d-lyspc\" aria-hidden=\"true\"></span>'+'</div>'+", "(off?'Show ':'Hide ')+'everything in '+label,BIM_LY_IC.off,BIM_LY_IC.on)+'</div>'+")],
    'gap_back': [(".a3d-lylist+.a3d-lysec{margin-top:-20px}", "")],
    'group_eye_not_undoable': [("    v=!!v;\n    pushUndo();\n    for(i=0;i<L.length;i++){", "    v=!!v;\n    for(i=0;i<L.length;i++){")],
    'empty_group_silent': [("if(!L.length){a3dToast('Nothing in '+(key==='analysis'?'Analysis':'Data')+' yet');return null;}", "if(!L.length)return null;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV158' in txt
out.write_text(txt, encoding='utf-8')
