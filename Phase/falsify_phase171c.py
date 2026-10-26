"""falsify_phase171c.py -- break the V171c build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase171c_one_analyze_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the records ----
    'marker_lost': [("window.__acad3dV171c='oneanalyze,tab,", "window.__acad3dV171c='tab,")],   # the V171c marker
    'hub_hook_kept': [("  window.__a3dAwPick=function(k,id){return bimAwPick(k,id);};", "  window.__a3dAwPick=function(k,id){return bimAwPick(k,id);};window.__a3dAnzOpenAll=function(){return [];};")],   # the old hub's hooks are gone
    # ---- 2. the tab ----
    'tab_no_open': [("    bimAwTab(t,was);   /* __acad3dV171c", "    0&&bimAwTab(t,was);   /* __acad3dV171c")],   # Analyze's tab opens it, from Assets
    'tab_no_leave': [("    }else if(A3D_AW.on)bimAwLeave();\n", "    }else if(0)bimAwLeave();\n")],   # another tab leaves it
    'prev_lost': [("      if(was&&was!=='analyze')A3D_AW.prev=was;\n", "")],   # Analyze's tab opens it, from Assets (prev)
    'leave_drawer_open': [("      if(shut){sh.classList.add('collapsed');bimShellDockW();}\n", "")],   # the cross goes back ... the panel left as it was
    'bar_kicker': [("<span class=\"a3d-awbar-k\">Analyze</span>", "<span class=\"a3d-awbar-k\">Site analysis</span>")],   # the bar says Analyze
    # ---- 3. the list before a run ----
    'no_boundary_buttons': [(" or <button type=\"button\" class=\"a3d-awl-lk\" data-saact=\"cmd:propertyline\">from bearings</button>", "")],   # no boundary yet: from a shape, or from bearings
    'cards_left_out': [("      var T=C.filter(function(x){return x.group===c.id;}),k=bimAwCatCounts(c.id),p=", "      var T=C.filter(function(x){return x.group===c.id&&x.id.indexOf('dg')===0;}),k=bimAwCatCounts(c.id),p=")],   # the others too
    'rows_not_waiting': [("(run?'':' disabled')+' aria-pressed=\"'+(a===f)+'\">'+bimEsc(A.name)", "' aria-pressed=\"'+(a===f)+'\">'+bimEsc(A.name)")],   # not run yet: each says so, and waits
    # ---- 4. Analyze site ----
    'progress_lost': [("bimEsc(R.busy?dn+' of '+R.steps.length+' done'+(now.length?': '+now.join(', ')+' ...':''):", "bimEsc(R.busy?'Analyzing':")],   # the list says how far it is
    'steps_not_live': [("    bimSaRefresh(true);   /* __acad3dV171c: the list's line and the overview's steps */", "    bimAnalyzeRefresh(true);")],   # the overview's steps follow it as they come
    'data_not_on_right': [("  function bimSaRefresh(force){var r=bimAnalyzeRefresh(force);if(A3D_AW.on)refreshProps();return r;}", "  function bimSaRefresh(force){return bimAnalyzeRefresh(force);}")],   # the overview's steps follow it as they come
    'list_counts_wrong': [("'\">'+(k.n||'')+'</span></button>'", "'\">'+(k.r||'')+'</span></button>'")],   # and in the list, beside each category
    'overview_counts_wrong': [("return k.n?bimSaN(k.n,'finding')+(k.r?', '+bimSaN(k.r,'red flag'):''):'No findings yet';", "return k.n?bimSaN(k.n,'finding'):'No findings yet';"),
                              ("'<span class=\"a3d-awl-fn\" title=\"'+bimEsc(bimAwCatSub(k))+'\">'", "'<span class=\"a3d-awl-fn\">'")],   # each with its findings counted -- with a red flag, the count says it (Legal's)
    'flags_lost': [("    if(RF.length)h+=bimAwSec('Red flags')", "    if(0)h+=bimAwSec('Red flags')")],   # a red flag: listed first in the overview
    'flag_badge_lost': [("(k.r?'<span class=\"a3d-awl-rf\"", "(0?'<span class=\"a3d-awl-rf\"")],   # and counted on its category's line in red
    'flag_no_link': [("class=\"a3d-awp-flag\" data-awact=\"cat:'+bimEsc(f.cat)+'\"", "class=\"a3d-awp-flag\" data-awact=\"cat:x'+bimEsc(f.cat)+'\"")],   # a red flag pressed: its category
    # ---- 5. a category ----
    'pick_undo': [("    bimAwBlur();\n    A3D_AW.pick={k:k,id:id};", "    pushUndo();bimAwBlur();\n    A3D_AW.pick={k:k,id:id};")],   # nothing drawn, no undo step
    'pick_draws': [("    bimAwBlur();\n    A3D_AW.pick={k:k,id:id};", "    bimAwBlur();bimAwState().focus=null;bimAwApply(false);\n    A3D_AW.pick={k:k,id:id};")],   # and its link goes there; the focus as it was
    'cat_findings_lost': [("(F.length?F.map(bimSaFindingHtml).join(''):'<p class=\"a3d-awp-note\">None yet:", "(0?F.map(bimSaFindingHtml).join(''):'<p class=\"a3d-awp-note\">None yet:")],   # what was found: each finding
    'cat_analyses_lost': [("    if(T.length)h+=bimAwSec('Analyses')", "    if(0)h+=bimAwSec('Analyses')")],   # the analyses that answer it
    'cat_data_lost': [("    if(dat)h+=dat();\n", "")],   # its data: the climate and risk
    'cat_see_lost': [("    if(see){for(j=0;j<BIM_SA_CATS.length;j++)", "    if(0){for(j=0;j<BIM_SA_CATS.length;j++)")],   # Risk says where its data is
    'cat_question_lost': [("'<p class=\"a3d-awp-about\">'+bimEsc(c.q)+'</p>'", "'<p class=\"a3d-awp-about\">'+bimEsc(c.n)+'</p>'")],   # its question
    'cat_pick_unmarked': [("'<button type=\"button\" class=\"a3d-awl-cat'+(p?' pick':'')+'\"", "'<button type=\"button\" class=\"a3d-awl-cat\"")],   # its line picked
    'field_wiped': [("    },true);   /* in the capture:", "    });   /* in the capture:")],   # a field changed: the zoning takes it / a floor load typed
    'hold_lost': [("    if(!force&&a&&b.contains(a)&&a.closest", "    if(0&&a&&b.contains(a)&&a.closest")],   # a refresh while a field is typed in waits
    'focusout_lost': [("    el.propsbody.addEventListener('focusout',function(){if(A3D_AW.pend)", "    0&&el.propsbody.addEventListener('focusout',function(){if(A3D_AW.pend)")],   # a field left unchanged: the refresh held happens as it is left
    'zn_refusal_shown_late': [("{bimZnSet(k,e.value);if(bimAwOwns())bimAwRender(true);}", "{bimZnSet(k,e.value);}")],   # refused: the field, still in use, shows the zoning's own again
    'blur_lost': [("  function bimAwBlur(){var a=document.activeElement;if(a&&a!==document.body", "  function bimAwBlur(){var a=document.activeElement;if(0&&a&&a!==document.body")],   # (a pick after a field: the panel changes) what it found
    # ---- 6. an analysis ----
    'finds_short': [("wind:['climate.wind','climate.comfort']", "wind:['climate.wind']")],   # what it found: the findings the winds draw
    'itfound_lost': [("h+=bimAwSec('What it found')+(FF.length?", "h+=bimAwSec('What it found')+(0?")],   # what it found
    'answers_lost': [("bimAwBtn('dg:reset:'+f,'Reset',false,R?'':'Not run yet')+'</div>'+bimAwInHtml('dg'+f);", "bimAwBtn('dg:reset:'+f,'Reset',false,R?'':'Not run yet')+'</div>';")],   # the category it answers, named
    'nofinding_vague': [("under '+(g?g.n:'its category')+'.'", "under its category.'")],   # one that writes no finding says where its category's are
    'stale_unsaid': [("    if(SC&&(SC.run.length||SC.data.length))h+=", "    if(0&&SC)h+=")],   # a standard changed since it ran: its panel says so
    'stale_row_unsaid': [("    if(SC.run.length||SC.data.length)return {cls:' stale',st:'Out of date'};", "    if(SC.run.length||SC.data.length)return {cls:' stale',st:''};")],   # its line says so
    # ---- 7. one of the model's ----
    'card_extra_lost': [("'<p class=\"a3d-awp-about\">'+bimEsc(c.status)+'</p>'+(c.extra||'')+", "'<p class=\"a3d-awp-about\">'+bimEsc(c.status)+'</p>'+")],   # its settings: the floor loads
    'card_layer_lost': [("    if(ly)acts.push(ly);\n    return '<div class=\"a3d-awp a3d-sa\" data-awpanel=\"card:'", "    return '<div class=\"a3d-awp a3d-sa\" data-awpanel=\"card:'")],   # Sun hours: Add as layer
    'card_answers_lost': [("acts.map(bimAnzBtn).join('')+'</div>':'')+bimAwInHtml(c.id)+'</div>';", "acts.map(bimAnzBtn).join('')+'</div>':'')+'</div>';")],   # and the category it answers
    'card_state_lost': [("      (c.state?'<span class=\"a3d-anzstate a3d-anzstate-'+c.state+'\">'+bimAnzStateText(c.state)+'</span>':'')+'</div>';", "      '</div>';")],   # Run: its line says On
    'load_refusal_late': [("{updateLevel(A3D.activeLevel,k,e.value);if(bimAwOwns())bimAwRender(true);}", "{updateLevel(A3D.activeLevel,k,e.value);}")],   # a negative one refused: the field shows the level's 4 again
    # ---- 8. Properties from a button ----
    'props_flag_lost': [("    if(A3D_AW.on)A3D_AW.props=true;   /* __acad3dV171c", "    0&&(A3D_AW.props=true);   /* __acad3dV171c")],   # Settings: the model's Properties at Location
    'back_lost': [("      else if(c==='back'){bimAwBlur();A3D_AW.props=false;", "      else if(c==='back'){bimAwBlur();")],   # back: the analysis as it was
    'title_in_props': [("t.textContent=bimAwOwns()&&!A3D_AW.props?'Analysis':'Properties';", "t.textContent=bimAwOwns()?'Analysis':'Properties';")],   # Settings: ... (Properties' title)
    'props_kept_on_leave': [("    A3D_AW.on=false;A3D_AW.props=false;\n", "    A3D_AW.on=false;\n")],   # out of it: the model's Properties are Properties' own again
    # ---- 9. a pick over a selection ----
    'pick_under_selection': [("    return A3D_AW.on&&(none||A3D_AW.over===bimAwSelKey());", "    return A3D_AW.on&&none;")],   # a row picked: its panel, the mass still selected
    'over_kept': [("    if(none)A3D_AW.over=null;\n", "")],   # the first selected again, later: its properties
    # ---- 10. the search ----
    'search_no_findings': [("bimSaOf(c.id).map(function(f){return f.title+' '+f.value+' '+bimSaPair(BIM_SA_CLS,f.cls)+' '+f.source;}).join(' ')", "''")],   # a word of a finding: its category
    'search_no_class': [("return f.title+' '+f.value+' '+bimSaPair(BIM_SA_CLS,f.cls)+' '+f.source;", "return f.title+' '+f.value+' '+f.source;")],   # a finding's class
    'search_no_buttons': [("(x.acts||[]).map(function(b){return b.label;}).join(' ')+' '+grp;", "grp;")],   # a row's button: Slope arrows finds Grading
    'search_no_settings': [("String(x.extra||'').replace(/<[^>]*>/g,' ')+' '+", "")],   # a row's settings: the floor loads
    'search_no_about': [("(a?(BIM_AW_ABOUT[a]||''):'')+' '+String(x.extra", "String(x.extra")],   # what an analysis shows: the divides
    'search_overview_kept': [("    if(ov)show(ov,!q);\n", "")],   # Overview and Model step aside
    'goto_search_kept': [("    if(!bimSaCat(id))return false;\n    A3D_ANZ.q='';\n    bimAwPick('cat',id);", "    if(!bimSaCat(id))return false;\n    bimAwPick('cat',id);")],   # a link to a category the search hid: the search cleared
    # ---- 11. the look ----
    'pick_colour_dark': [(".a3d-awl-row.pick,.a3d-awl-cat.pick,.a3d-awl-row.pick:hover,.a3d-awl-cat.pick:hover{background:#e8edf2;", ".a3d-awl-row.pick,.a3d-awl-cat.pick,.a3d-awl-row.pick:hover,.a3d-awl-cat.pick:hover{background:#2f6fd6;")],   # a pick in the mode's colours
    'pick_colour_light': [("body.light-theme .a3d-awl-cat.pick:hover{background:#1f2328;color:#fff}", "body.light-theme .a3d-awl-cat.pick:hover{background:#e8edf2;color:#fff}")],   # a pick in the mode's colours, light
    'cars_by_map': [("  function bimTrLight(){var L=bimAwLook();return L?L.light:bimMvLight();}", "  function bimTrLight(){return bimMvLight();}")],   # on the dark, the dark
    'drawn_by_mode': [("  function bimMvLight(){var s=bimMapSettings().style;", "  function bimMvLight(){var L=bimAwLook();if(L)return L.light;var s=bimMapSettings().style;")],   # what a run draws keeps the map's colours
    # ---- 12. out and in, a phone ----
    'pick_lost_on_leave': [("    A3D_AW.on=false;A3D_AW.props=false;\n", "    A3D_AW.on=false;A3D_AW.props=false;A3D_AW.pick=null;\n")],   # back in: the pick as it was left
    'phone_no_sheet': [("    bimAwFold(true);   /* a drawer layout: the panel, to read */", "    bimAwFold(false);")],   # a category: the category open as a sheet
    'phone_focus_drawer': [("    bimAwFold(false);   /* a drawer layout: the view, with the key on it */", "")],   # an analysis: the drawer shut and the sheet too
    'phone_run_drawer': [("    bimAwOpen();\n    bimAwFold(false);\n    bimAwBar();\n", "    bimAwOpen();\n    bimAwBar();\n")],   # the run done: the drawer shut
    'phone_rows_small': [("@media(pointer:coarse){.a3d-awl-cat,.a3d-awl-row{min-height:44px}", "@media(pointer:coarse){.a3d-awl-cat,.a3d-awl-row{min-height:30px}")],   # lines a finger's height
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV171c' in txt
out.write_text(txt, encoding='utf-8')
