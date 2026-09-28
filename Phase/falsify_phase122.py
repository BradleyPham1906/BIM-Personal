"""falsify_phase122.py -- break the V122 build one way at a time, keeping the marker.

Each variant takes back one thing V122 does, or breaks one thing it built, and the V122 suite must
fail on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 122a: the same page at any size, and nothing that is not on it
    'page_scale_ignored': [("    var s=(isFinite(scale)&&scale>0)?scale:1;\n", "    var s=1;\n")],
    'viewport_scale_ignored': [("    var bs=(isFinite(scale)&&scale>0)?scale:1;\n", "    var bs=1;\n")],
    'selection_on_paper': [("      A3D.selSet=[];A3D.selGrid=null;\n", "")],
    'grid_selection_on_paper': [("      A3D.selSet=[];A3D.selGrid=null;\n", "      A3D.selSet=[];\n")],
    'rubber_band_on_paper': [("    if(!capMode)drawSkLivePreview(ctx,V,W,H);", "    drawSkLivePreview(ctx,V,W,H);")],
    'schedule_fmt_called': [("        var txt=bimFmtScheduleValue(val,col.fmt);\n",
                             "        var txt=col.fmt?col.fmt(val,rows[i]):String(val==null?'':val);\n")],
    'png_export_at_6': [("      var cv=bimRenderSheet(sheet,SHEET_PREVIEW_PXMM,true,null,SHEET_EXPORT_PXMM/SHEET_PREVIEW_PXMM);\n      var dataURL=cv.toDataURL('image/png');\n      var a=document.createElement('a');\n",
                         "      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM,true);\n      var dataURL=cv.toDataURL('image/png');\n      var a=document.createElement('a');\n")],
    'layout_pixel_floor': [("    if(pm)return Math.max(1/cvScale(el.cv),", "    if(pm)return Math.max(1,")],
    # ---- 122b: the appearance a sheet prints in
    'sheet_technical_only': [("  function bimPresentGraphics(){return A3D_PLOT.on?!!A3D_PLOT.pres:!!A3D.presentMode;}",
                              "  function bimPresentGraphics(){return A3D.sheetCapture?false:(A3D_PLOT.on?!!A3D_PLOT.pres:!!A3D.presentMode);}")],
    'sheet_outline_fixed': [("      var baseStroke=capMode?(rg?rg.lineColor:'rgba(0,0,0,0.55)'):", "      var baseStroke=capMode?'rgba(0,0,0,0.55)':")],
    # ---- 122c: the Pages display
    'pages_reversed': [("      if(col.children[i]!==e.box)col.insertBefore(e.box,col.children[i]||null);\n",
                        "      col.insertBefore(e.box,col.firstChild);\n")],
    'scroll_not_followed': [("      if(id&&id!==A3D.activeSheetId)bimPagesSetCurrent(id);\n", "")],
    'next_button_dead': [("        if(t.closest('#a3d-pgnext')){bimPagesGo(bimPagesIndex()+1);return;}\n",
                          "        if(t.closest('#a3d-pgnext'))return;\n")],
    'page_number_ignored': [("        if(ev.key==='Enter'){ev.preventDefault();bimPagesTypedNumber();el.pgnum.blur();}\n",
                             "        if(ev.key==='Enter'){ev.preventDefault();el.pgnum.blur();}\n"),
                            ("      el.pgnum.addEventListener('change',function(){bimPagesTypedNumber();});\n", "")],
    'page_keys_hand_list': [("      var pact=bimPageKeyAct(ev.key);\n",
                             "      var pact={PageDown:'next',PageUp:'prev',Home:'first',End:'last',ArrowDown:'down',ArrowUp:'up'}[ev.key];\n")],
    'zoom_percent_wrong': [("  var BIM_PX_PER_MM_100=96/25.4;", "  var BIM_PX_PER_MM_100=3;")],
    'fit_page_is_width': [("    if(z==='page')k=Math.min(k,Math.max(40,wrap.clientHeight-2*BIM_PAGE_GAP)/mh);\n", "")],
    'model_change_not_redrawn': [("    A3D_REV++;   /* __acad3dV122 */\n    bimPagesStale();\n", "    A3D_REV++;   /* __acad3dV122 */\n")],
    'dblclick_no_layout': [("      bimPagesSetCurrent(b.getAttribute('data-page'));\n      bimPagesSetDisplay('layout');\n",
                            "      bimPagesSetCurrent(b.getAttribute('data-page'));\n")],
    'delete_leaves_pages': [("        var inPages=wasOn&&A3D_PAGES.display==='pages'&&A3D.sheets.length>0;\n",
                             "        var inPages=false;\n")],
    'pages_bar_not_marked': [("    for(j=0;j<b.length;j++)b[j].classList.toggle('on',b[j].getAttribute('data-shdisp')===A3D_PAGES.display);\n", "")],
    # ---- 122d: Present
    'present_keys_hand_list': [("    for(i=0;i<A3D_SHOW_KEYS.length;i++)if(A3D_SHOW_KEYS[i].keys.indexOf(ev.key)>=0){act=A3D_SHOW_KEYS[i].act;break;}\n",
                                "    act={ArrowRight:'next',ArrowLeft:'prev',Home:'first',End:'last',Escape:'end',' ':'next'}[ev.key]||null;\n")],
    'keys_reach_model': [("    if(A3D_SLIDESHOW.on){bimSlideshowKey(ev);return;}   /* __acad3dV122: nothing typed reaches the model */\n",
                          "    if(A3D_SLIDESHOW.on&&!ev.ctrlKey&&!ev.metaKey&&/^(Arrow|Page|Home|End|Escape| |Enter|Backspace|[nNpP]$)/.test(ev.key)){bimSlideshowKey(ev);return;}\n")],
    'no_full_screen': [("    var rq=ov.requestFullscreen||ov.webkitRequestFullscreen,p;\n", "    var rq=null,p;\n")],
    'fs_exit_not_ending': [("    if(A3D_SLIDESHOW.fs&&!fsEl){A3D_SLIDESHOW.fs=false;bimSlideshowEnd();return;}\n",
                            "    if(A3D_SLIDESHOW.fs&&!fsEl){A3D_SLIDESHOW.fs=false;return;}\n")],
    'end_not_back_to_page': [("      if(A3D_PAGES.display==='pages'){if(s.id!==A3D.activeSheetId)bimPagesSetCurrent(s.id);bimPagesScrollTo(s.id);}\n      else if(s.id!==A3D.activeSheetId)bimActivateView('sheet',s.id);\n",
                              "")],
    'wheel_every_notch': [("      if(now-A3D_SLIDESHOW.wheelAt<BIM_SHOW_WHEEL_MS||!ev.deltaY)return;\n", "      if(!ev.deltaY)return;\n")],
    'click_does_nothing': [("        else if(!(ev.target.closest&&ev.target.closest('.a3d-ssbar')))bimSlideshowAct('next');\n", "")],
    'never_idle': [("    A3D_SLIDESHOW.idleT=setTimeout(function(){A3D_SLIDESHOW.idleT=null;if(A3D_SLIDESHOW.on)ov.classList.add('idle');},BIM_SHOW_IDLE_MS);\n", "")],
    'refusal_silent': [("    A3D_SLIDESHOW.msg='Full screen was not allowed here, so the pages fill the window. ';\n", "")],
    'no_page_ahead': [("    bimSlideshowAhead(A3D_SLIDESHOW.idx+1);\n", "")],
    'bar_back_always_on': [("    ov.querySelector('[data-ssact=\"prev\"]').disabled=(i<=0);\n", "")],
    'present_not_fitted': [("    var k=Math.max(0.05,Math.min((vw-2*m)/s.w,(vh-2*m)/s.h));\n    var W=Math.max(1,Math.round(s.w*k)),H=Math.max(1,Math.round(s.h*k)),sc=bimPageScaleFor(s,W);\n",
                            "    var k=Math.max(0.05,(vw-2*m)/s.w);\n    var W=Math.max(1,Math.round(s.w*k)),H=Math.max(1,Math.round(s.h*k)),sc=bimPageScaleFor(s,W);\n")],
    # ---- 122e: the printed set
    'print_one_paper_size': [("      body+='<div class=\"a3dpg\" data-page=\"'+bimEsc(s.id)+'\" style=\"page:'+nm+';",
                              "      body+='<div class=\"a3dpg\" data-page=\"'+bimEsc(s.id)+'\" style=\"page:'+Object.keys(sizes)[0]+';")],
    'print_out_of_order': [("      body+='<div class=\"a3dpg\"", "      body='<div class=\"a3dpg\""),
                           ("mm\">'+svg+'</div>';\n", "mm\">'+svg+'</div>'+body;\n")],
    # ---- 122f: the Presentation panel
    'panel_not_on_rail': [("      '<button type=\"button\" class=\"a3d-railbtn\" data-tab=\"presentation\" title=\"Presentation\" aria-label=\"Presentation\">'+   /* __acad3dV122 */\n      bimRailIcon('presentation')+'</button>'+\n", "")],
    'thumbnail_blank': [("      A3D_PRP.thumbs[s.id]={key:key,cv:c};\n      bimThumbBlit(cv,c);\n", "      A3D_PRP.thumbs[s.id]={key:key,cv:document.createElement('canvas')};\n")],
    'thumbnails_stale': [("      try{if(bimPagesOn())bimPagesQueue();bimPresThumbsQueue();}", "      try{if(bimPagesOn())bimPagesQueue();}")],
    'click_opens_layout': [("    bimPagesSetDisplay('pages');\n    return bimActivateView('sheet',id);\n", "    return bimActivateView('sheet',id);\n")],
    'rename_two_paths': [("      if(keep)bimSheetRename(id,inp.value);   /* __acad3dV122: the one path, the page's too */\n",
                          "      var v=String(inp.value).trim();\n      if(keep&&v&&v!==sh.name&&bimSheetById(id)){pushUndo();sh.name=v;refreshBrowser();bimSheetViewRefresh();saveSoon();}\n")],
    'move_not_undoable': [("    pushUndo();\n    A3D.sheets.splice(to,0,A3D.sheets.splice(i,1)[0]);\n", "    A3D.sheets.splice(to,0,A3D.sheets.splice(i,1)[0]);\n")],
    'drop_ignores_half': [("    if(after)to++;\n    if(from<to)to--;\n", "    if(from<to)to--;\n")],
    'tab_menu_hand_list': [("    bimSheetMenu(ev,id,'tabs');   /* __acad3dV122: the items the page's menu reads too */\n",
                            "    bimLtMenuOpen(ev.clientX,ev.clientY,[['New sheet','new'],['Rename','rename'],['Delete','del',true],'-',['Sheet setup\\u2026','setup'],['Plot\\u2026','plot']],function(a){bimSheetMenuDo(a,id,'tabs');});\n")],
    'first_page_moves_up': [("    if(i>0)it.push([pg?'Move up':'Move left','earlier']);\n", "    it.push([pg?'Move up':'Move left','earlier']);\n")],
    'panel_marks_nothing': [("      h+='<div class=\"a3d-prpitem'+(s.id===cur?' cur':'')+'\"", "      h+='<div class=\"a3d-prpitem'+'\"")],
    'empty_buttons_live': [("      '<button type=\"button\" class=\"a3d-prpbtn pri\" data-prpact=\"present\"'+(n?'':' disabled')+", "      '<button type=\"button\" class=\"a3d-prpbtn pri\" data-prpact=\"present\"'+")],
    'shortcuts_hand_list': [("    return A3D_KEYS.concat([{grp:'Pages',rows:rows(A3D_PAGEVIEW_KEYS)},{grp:'Presenting',rows:rows(A3D_SHOW_KEYS)}]);\n",
                             "    return A3D_KEYS.concat([{grp:'Pages',rows:rows(A3D_PAGEVIEW_KEYS)},{grp:'Presenting',rows:rows(A3D_SHOW_KEYS.slice(0,4))}]);\n")],
    'move_not_saved': [("    A3D.sheets.splice(to,0,A3D.sheets.splice(i,1)[0]);\n    refreshBrowser();bimSheetViewRefresh();saveSoon();\n",
                        "    A3D.sheets.splice(to,0,A3D.sheets.splice(i,1)[0]);\n    refreshBrowser();bimSheetViewRefresh();\n")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV122' in txt
out.write_text(txt, encoding='utf-8')
