"""falsify_phase162.py -- break the V162 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- one Analyze ----
    'two_tab_bodies': [("abox.className='a3d-tabbody a3d-analyze-wrap a3d-sa-wrap';", "abox.className='a3d-tabbody a3d-analyze-wrap';")],
    'model_out_of_order': [("var BIM_ANZ_MODEL=['lens','areas','lod','stats','structure'];", "var BIM_ANZ_MODEL=['structure','lens','areas','lod','stats'];")],
    'rain_in_landform': [("grading:'landform',rain:'water',sun:'climate'", "grading:'landform',rain:'landform',sun:'climate'")],
    'sun_lost': [("rain:'water',sun:'climate',sunhours:'climate'", "rain:'water',sunhours:'climate'")],
    'climate_data_gone': [("climate:function(){return bimClbSaHtml();},", "")],
    'no_shared_links': [("var BIM_SA_SEE={risk:['climate','Air quality and earthquakes come with the climate data'],people:['access','The census and the daily needs within a walk come with the access data']};", "var BIM_SA_SEE={};")],
    'rows_open_with_category': [(".a3d-anzcard.open>.a3d-anzbody{display:block}", ".a3d-anzcard.open .a3d-anzbody{display:block}")],
    'never_whole_category': [("whole=!q||bimAnzWordsHit(q,name+' '+bimAnzTexts(K[i],'.a3d-saq,.a3d-clsec,.a3d-salink,.a3d-safind,.a3d-sachk'));", "whole=!q;")],
    'always_whole_category': [("whole=!q||bimAnzWordsHit(q,name+' '+bimAnzTexts(K[i],'.a3d-saq,.a3d-clsec,.a3d-salink,.a3d-safind,.a3d-sachk'));", "whole=true;")],
    'words_run_together': [("while((n=w.nextNode()))s.push(n.nodeValue);\n    return s.join(' ');", "while((n=w.nextNode()))s.push(n.nodeValue);\n    return s.join('');")],
    'search_not_opened': [("K[i].classList.toggle('qhit',!!q&&on);", "K[i].classList.toggle('qhit',false);")],
    'model_unfiltered': [("for(j=0;j<R.length;j++){hit=!q||bimAnzWordsHit(q,bimAnzRowText(R[j],name));show(R[j],hit);if(hit)k++;}", "for(j=0;j<R.length;j++){hit=true;show(R[j],hit);if(hit)k++;}")],
    'typing_overwritten': [("{A3D_ANZ.pend=true;return false;}", "{A3D_ANZ.pend=false;}")],
    'held_forever': [("abox.addEventListener('focusout',function(){if(A3D_ANZ.pend)setTimeout(function(){if(A3D_ANZ.pend)bimAnalyzeRefresh();},0);});", "")],
    'search_scrolls_away': [(".a3d-anz>.a3d-anzsearch{position:sticky;top:0;z-index:2;box-shadow:0 0 0 6px #2c2c2c}", ".a3d-anz>.a3d-anzsearch{box-shadow:0 0 0 6px #2c2c2c}")],
    'goto_not_opened': [("    bimSaToggle(id,true);\n    c=w?w.querySelector", "    c=w?w.querySelector")],
    'zoning_not_in_legal': [("zoning:function(){A3D_ZN.edit=true;bimSaGoto('legal');bimSaRefresh(true);}", "zoning:function(){A3D_ZN.edit=true;bimAnzView();bimSaRefresh(true);}")],
    # ---- a board is a page ----
    'board_first': [("    P.boards.push({id:id,kind:kind});\n    P.order.push(id);", "    P.boards.push({id:id,kind:kind});\n    P.order.unshift(id);")],
    'board_add_not_undoable': [("    if(bimBoardById(id))return id;\n    pushUndo();\n    P=bimPresData();", "    if(bimBoardById(id))return id;\n    P=bimPresData();")],
    'show_not_presentation': [("    bimShellSetTab('presentation');\n    if(!bimPresOpenBoard(id))return false;", "    if(!bimPresOpenBoard(id))return false;")],
    'analyze_opens_board_itself': [("    if(c==='accboard')return bimBoardShow('access');\n", "    if(c==='accboard')return bimClbOpen('access');\n")],
    'command_opens_board_itself': [("    climate:function(){bimBoardShow('climate');},", "    climate:function(){bimClbOpen('climate');},")],
    'no_board_button': [("'<button type=\"button\" class=\"a3d-prpbtn\" data-prpact=\"board\"", "''+'<button type=\"button\" hidden class=\"a3d-prpbtn\" data-prpact=\"board\"")],
    'no_board_tag': [("<span class=\"a3d-prptag\">Board</span>", "")],
    'board_menu_short': [("it.push('-',['Remove from the set','remove',true]);", "")],
    # ---- in the main view ----
    'board_over_everything': [(".a3d-vp>.a3d-clb{position:absolute;inset:0;z-index:700}", ".a3d-vp>.a3d-clb{z-index:700}")],
    'board_in_body': [("var host=document.querySelector('.a3d-vp')||document.body,b=bimClbEl(),w;", "var host=document.body,b=bimClbEl(),w;")],
    'dock_over_board': [("body.a3d-clb-open #a3d-dock,body.a3d-clb-open .a3d-tpal{display:none!important}", "body.a3d-clb-open .a3d-tpal{display:none!important}")],
    'width_by_window': [("function bimClbW(b){var p=b&&b.parentNode;return Math.round(p&&p!==document.body?(p.clientWidth||window.innerWidth):window.innerWidth);}", "function bimClbW(b){return Math.round(window.innerWidth);}")],
    'no_refit': [("if(!b.__clbRO&&typeof ResizeObserver!=='undefined'){", "if(false){")],
    'esc_eaten': [("    if(bimClbKey(ev))return;   /* __acad3dV162: a board's page owns the keys, as a sheet's does */\n", "")],
    'esc_from_any_field': [("    if(a&&a!==document.body&&!(b&&b.contains(a))&&(/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)||a.isContentEditable))return false;\n    if(ev.key==='Escape')", "    if(ev.key==='Escape')")],
    'view_keeps_board': [("    if(A3D_CLB.open)bimClbClose();   /* __acad3dV162: a board's page gives the main view back */\n", "")],
    'narrow_by_window': [("    A3D_CLB.narrow=w<760;", "    A3D_CLB.narrow=window.innerWidth<760;")],
    'phone_drawer_stays': [("    bimClbOpen(b.kind);\n    if(bimShellOverlay())bimShellDrawer(false);", "    bimClbOpen(b.kind);")],
    # ---- its thumbnail ----
    'thumb_not_print_look': [("function bimBoardPrintHtml(kind){return '<div class=\"a3d-clb prt w-l\">'+bimBoardHtmlFor(kind,false)+'</div>';}", "function bimBoardPrintHtml(kind){return '<div class=\"a3d-clb w-l\">'+bimBoardHtmlFor(kind,false)+'</div>';}")],
    'thumb_unscaled': [("fr.style.transform='scale('+k.toFixed(5)+')';", "")],
    'thumb_never_again': [("      key='brd|'+A3D_REV;", "      key='brd|0';")],
    # ---- the order ----
    'drag_sheets_only': [("      try{bimPresMoveNear(id,it.getAttribute('data-prpitem'),ev.clientY>r.top+r.height/2);}", "      try{bimSheetMoveNear(id,it.getAttribute('data-prpitem'),ev.clientY>r.top+r.height/2);}")],
    'tabs_not_reordered': [("    A3D.sheets.length=0;ord.forEach(function(s){A3D.sheets.push(s);});", "")],
    'sheet_menu_skips_boards': [("return where==='pages'?bimPresStep(id,a==='earlier'?-1:1):bimSheetMove(id,bimSheetIndex(id)+(a==='earlier'?-1:1));", "return bimSheetMove(id,bimSheetIndex(id)+(a==='earlier'?-1:1));")],
    'remove_keeps_board': [("    P.boards=P.boards.filter(function(x){return x.id!==id;});", "")],
    # ---- Present ----
    'present_draws_board_as_sheet': [("    if(e.t==='board'){bimSlideshowBoard(e);bimSlideshowBar();bimSlideshowAhead(A3D_SLIDESHOW.idx+1);return;}   /* __acad3dV162 */", "    if(e.t==='board'){bimSlideshowBar();return;}")],
    'wheel_always_pages': [("      if(bd&&ev.deltaY&&(ev.deltaY>0?bd.scrollTop+bd.clientHeight<bd.scrollHeight-1:bd.scrollTop>0))return;", "")],
    'end_not_on_board': [("    if(e&&e.t==='board'){bimClbOpen(e.b.kind);return true;}   /* __acad3dV162: back on the board last shown */", "")],
    'two_boards_while_presenting': [("    if(A3D_CLB.open)bimClbClose();   /* one board on the screen: Present's */", "")],
    'hint_over_board': [(".a3d-slideshow .a3d-ssboard .a3d-clb-page{padding-top:46px;padding-bottom:84px}", "")],
    # ---- print ----
    'printset_without_boards': [("        try{body+='<div class=\"a3dbrd\" data-page=\"'+bimEsc(e.id)+'\" style=\"page:a3dbrd\">'+bimBoardPrintHtml(e.b.kind)+'</div>';}", "        try{}")],
    'printset_unstyled': [("    if(brd)css+=bimClbCss()+'.a3dbrd{", "    if(brd)css+='.a3dbrd{")],
    'board_print_in_page': [("      else if(a==='print')bimClbPrint(A3D_CLB.kind);", "      else if(a==='print'){try{window.print();}catch(eP){}}")],
    'ctrl_p_blank': [("  window.addEventListener('beforeprint',function(){", "  window.addEventListener('beforeprintx',function(){")],
    # ---- kept with the project ----
    'set_not_in_file': [("resultLayers:A3D.resultLayers||[],pres:A3D.pres||null}});", "resultLayers:A3D.resultLayers||[]}});")],
    'set_not_stored': [("resultLayers:A3D.resultLayers||[],pres:A3D.pres||null};   /* __acad3dV146, __acad3dV148; __acad3dV162 */", "resultLayers:A3D.resultLayers||[]};")],
    'set_not_loaded': [("      A3D.pres=bimPresValid(st&&st.pres);   /* __acad3dV162: its boards in the set, and the set's order */\n", "")],
    'set_not_undone': [("    A3D.pres=bimPresValid(st.pres);   /* __acad3dV162: the set as it was */\n", "")],
    'bad_record_kept': [("if(b&&typeof b==='object'&&bimBoardName(b.kind)&&!seen[b.kind]){seen[b.kind]=1;", "if(b&&typeof b==='object'){")],
    'kinds_made_late': [("function bimBoards(){return [['climate','Climate and risk'],['zoning','Zoning and yield'],['access','Access and people']];}",
                         "var BIM_BOARDS_LATE=[['climate','Climate and risk'],['zoning','Zoning and yield'],['access','Access and people']];function bimBoards(){return BIM_BOARDS_LATE||[];}")],
    # ---- the open-all hook reaches the rows in their categories ----
    'open_all_rows_only': [("if(on!==false&&c.group!=='model')bimSaToggle(c.group,true);", "")],
    'header_squashed': [("#a3d-shell .a3d-projhead{flex-shrink:0}", "#a3d-shell[data-tab=\"analyze\"] .a3d-projhead{flex-shrink:0}")],
    'version_old': [("  var BIM_APP_VERSION={v:'V162',date:'2026-10-10'};", "  var BIM_APP_VERSION={v:'V161',date:'2026-10-10'};")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV162' in txt
out.write_text(txt, encoding='utf-8')
