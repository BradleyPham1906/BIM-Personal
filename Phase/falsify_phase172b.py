"""falsify_phase172b.py -- break the V172b build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase172b_ladybug_boards_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the records ----
    'marker_lost': [("window.__acad3dV172b='runtime,manifest,", "window.__acad3dV172b='manifest,")],   # the V172b marker
    'utci_band_off': [("v:[-40,-27,-13,0,9,26,32,38,46],say:'the bounds", "v:[-40,-27,-13,0,9,27,32,38,46],say:'the bounds")],   # UTCI's scale and range in the registry
    'ppd_off': [("{n:'ppd',v:10,u:'%'", "{n:'ppd',v:12,u:'%'")],   # ASHRAE 55-2023's PPD 10% and still air 0.1 m/s
    'clo_off': [("{n:'clo',t:1,u:'clo',v:[0.5,1.0]", "{n:'clo',t:1,u:'clo',v:[0.6,1.0]")],   # the comfort assumptions (0.5 and 1.0 clo at 1.1 met)
    'dd_percent_off': [("{n:'heating',t:1,u:'%',v:[99.6,99]", "{n:'heating',t:1,u:'%',v:[99.6,98]")],   # ... and the design conditions' percentiles
    'psych_ppd_literal': [("ppd:bimStd('ashrae.55','ppd'),still:bimStd('ashrae.55','still')", "ppd:10,still:bimStd('ashrae.55','still')")],   # PPD 20% set for the project widens the zone
    'utci_still_literal': [("still:u('va_lo')};", "still:0.5};")],   # run again, still air is the project's 0.6 m/s
    # ---- 2. the runtime ----
    'wheel_hash_unchecked': [("if(hex(h)!==w.h)throw new Error(w.f+' does not match its SHA-256');", "")],   # a wheel that is not what the app pins is refused
    'pages_base_wrong': [("var BIM_LB_PAGES='https://bradleypham1906.github.io/BIM-Personal/runtime/'", "var BIM_LB_PAGES='https://bradleypham1906.github.io/BIM-Personal/runtimes/'")],   # from file:// it asks the Pages site
    # ---- 3. a weather file ----
    'same_source_undo': [("    if(kept&&kept.key===s.key)return kept;", "")],   # the same file again changes nothing
    # ---- 4. UTCI ----
    'shade_sun_mrt': [('"        mrt = sun_mrt if sun else None",', '"        mrt = sun_mrt",')],   # shade_wind: every hour's category by the official polynomial
    'still_is_wind': [('"        u = UTCI(db, rh, mrt, ws if wind else still_ws)",', '"        u = UTCI(db, rh, mrt, ws)",')],   # shade_still: every hour's category ... (and native)
    'outside_no_calm': [("v < lva[0] or v > lva[1] or pa > lpa:", "v > lva[1] or pa > lpa:")],   # ... hours outside its range
    'eleven_categories': [("cats = [int(v) for v in u.original_utci_category.values]", "cats = [int(v) for v in u.utci_category.values]")],   # four conditions (Ladybug's own eleven-point scale)
    'utci_range_dropped': [("    if(b.length!==9)return [];", "    return [];")],   # the figure's ranges from the registry's scale
    # ---- 5. the psychrometric chart ----
    'unmerged': [("strategy_par:[c('day_above'),c('night_below'),c('fan'),c('balance'),c('solar_cap'),c('time_const')],", "strategy_par:[c('day_above'),c('night_below'),c('fan'),c('balance'),c('solar_cap'),c('time_const')],merge:false,")],   # the merged comfort zone, then Ladybug's five strategies
    'night_flush_dewpoint': [('"            pg, epw.dry_bulb_temperature, night_below, tim_c, 0.01) if pg else None)",', '"            pg, epw.dew_point_temperature, night_below, tim_c, 0.01) if pg else None)",')],   # each zone's share and shape as native CPython's
    'solar_north': [("window = 180 if epw.location.latitude >= 0 else 0", "window = 0 if epw.location.latitude >= 0 else 180")],   # each zone's share ... (passive solar)
    'strategy_range_unchecked': [("        if v is None or not isinstance(v, (int, float)) or v != v or v < lo or v > hi:", "        if v is None:")],   # a fan speed of 40 m/s goes back to Ladybug's 1.0, said
    # ---- 6. wind ----
    'bin_edge_out': [("if v >= bins[j]:", "if v > bins[j]:")],   # 16 sectors ... in the app's speed bands
    'wind_bins_literal': [("if(kind==='wind')return {directions:16,bins:bimClimWindBins()};", "if(kind==='wind')return {directions:16,bins:[0.5,2,4,6,9]};")],   # ... and as native CPython's (the registry's bands)
    # ---- 7. design days ----
    'cooling_tail_wrong': [("('cooling', 'Ann Clg .4% Condns DB=>MWB')", "('cooling', 'Ann Clg 1% Condns DB=>MWB')")],   # the DDY's five design days
    # ---- 8. Open-Meteo ----
    'om_instant_late': [("db, f1 = col('temperature_2m')", "db, f1 = col('temperature_2m', 1.0, 1)")],   # UTCI from those hours, hour by hour
    'om_zone_sign': [("return off===0?'GMT':'Etc/GMT'+(off<0?'+':'-')+Math.abs(off);", "return off===0?'GMT':'Etc/GMT'+(off<0?'-':'+')+Math.abs(off);")],   # the last full year ... Etc/GMT+5
    'om_end_short': [("end_date:(year+1)+'-01-01'", "end_date:year+'-12-31'")],   # its 8760 hours, the gaps filled and counted
    'om_error_words': [("      function(e){throw new Error('archive-api.open-meteo.com could not be reached ('+(e&&e.message||e)+'): the hours need the network');}).then(function(js){",
                        "      function(e){throw e;}).then(function(js){")],   # Open-Meteo down: said
    # ---- 9. kept and out of date ----
    'std_stamp_lost': [("std:bimStdStamp(BIM_LB_STD[kind]||[]),", "")],   # each result keeps ... the standards it used
    'utci_std_lost': [("var BIM_LB_STD={utci:['utci','app.comfort']", "var BIM_LB_STD={utci:['app.comfort']")],   # a standard changed marks only the result that used it
    # ---- 10. Analyze ----
    'rows_unlisted': [("    bimLbCards().forEach(function(c){C.push(c);});   /* __acad3dV172b: Ladybug's rows, in Climate */\n", "")],   # Climate's rows: Ladybug's five
    'rows_wrong_group': [("BIM_ANZ_GROUP_OF.lbutci='climate';", "BIM_ANZ_GROUP_OF.lbutci='risk';")],   # Climate's rows ... after the sun's
    'addto_new_empty': [("return !!bimBrdNewUi(BIM_LB_NAMES[k],[F]);", "return !!bimBrdNewUi(BIM_LB_NAMES[k],[]);")],   # Add to a board, A new board: ... with the figure
    # ---- 11. the boards' figures ----
    'card_not_kept': [("    if(id)bimFigCapCard(id,C,title,dek,body,src);\n", "")],   # the climate board's indicators and figures, each named
    'card_id_wrong': [("['s5','@clim.wind']", "['s5','@clim.winds']")],   # the climate board's ... each named
    'zn_kpis_lost': [("    bimFigCapKpis('zn.kpis',kp);   /* __acad3dV172b */\n", "")],   # the zoning board's
    'edit_btn_outside_set': [("    if(!B||A3D_CLB.other)return h;", "    if(A3D_CLB.other)return h;")],   # a board without a list is drawn exactly as the kept build draws it
    # ---- 12. Edit ----
    'figid_attr_lost': [("+'\" data-fig=\"'+no+'\"'+(id?' data-figid=\"'+id+'\"':'')+'><figcaption>", "+'\" data-fig=\"'+no+'\"'+'><figcaption>")],   # Edit: the figures arranged as laid out, 13
    'edit_btn_lost': [("data-brd=\"edit\" aria-pressed=\"false\"", "data-brd=\"edyt\" aria-pressed=\"false\"")],   # the board's bar: Edit
    'edit_keeps_at_once': [("    A3D_CLB.edit=!!on;\n    bimBrdDlgClose();", "    A3D_CLB.edit=!!on;\n    if(on){var B0=bimBrdRec();if(B0&&!B0.figs)B0.figs=bimBrdWorking(B0);}\n    bimBrdDlgClose();")],   # Edit: ... nothing kept, no undo step yet
    'zoom_off': [("z=w>0?Math.min(1,w/BIM_BRD_W0):1;", "z=1;")],   # laid out 1408 px across and zoomed to the main view: ... px across of its ...
    'width_off': [("var BIM_BRD_W0=1408,", "var BIM_BRD_W0=1400,")],   # at a wide view, unzoomed, each figure where the board's grid put it
    'grid_ignored': [("if(A3D_SNAP.grid){if(!sx&&lx)nx=Math.round(nx);if(!sy&&ly)ny=Math.round(ny);}", "")],   # Grid: a drag puts the figure on whole steps
    'snap_resize_off': [("if(lx){best=near([r],xs);if(best){r+=best[0];ex=true;R.guides.push(['x',best[1],true]);}}", "")],   # Snap: a corner dragged within 12 px ... caught
    'ortho_ignored': [("if(A3D_SNAP.ortho){if(Math.abs(dx)>=Math.abs(dy))dy=0;else dx=0;lx=dx!==0;ly=dy!==0;}", "")],   # Ortho: a slanting drag goes straight across
    'drag_uncommitted': [("    F.x=R.x;F.y=R.y;F.w=R.w;F.h=R.h;\n    bimBrdCommit(B,D.L,null,D.k);", "    F.x=R.x;F.y=R.y;F.w=R.w;F.h=R.h;")],   # the first change keeps the list: one undo step
    'key_step': [("st=A3D_SNAP.grid?1:0.1;", "st=A3D_SNAP.grid?1:0.2;")],   # the keys: down a tenth of a step
    'shift_moves': [("bimBrdNudge(k,dx*st,dy*st,ev.shiftKey);", "bimBrdNudge(k,dx*st,dy*st,false);")],   # the keys: ... Shift, a tenth narrower
    'menu_no_fit': [("it=[[F.f==='text'?'The heading…':'Options…','opts'],['Fit the height to its content','fit'],['Duplicate','dup']];", "it=[[F.f==='text'?'The heading…':'Options…','opts'],['Duplicate','dup']];")],   # a figure's menu
    'show_class_lost': [("var cls='a3d-clb-fig'+(o.show==='table'?' o-table':o.show==='both'?' o-both':'')", "var cls='a3d-clb-fig'")],   # Options: ... its numbers as a table
    'title_ignored': [("return bimClbCard(P.cls.concat(['@'+F.f]),no,o.t||P.title,P.dek,P.body,P.src);", "return bimClbCard(P.cls.concat(['@'+F.f]),no,P.title,P.dek,P.body,P.src);")],   # Options: its title
    'utci_cond_ignored': [("cond=(opt&&BIM_LB_COND[opt.cond])?opt.cond:'sun_wind'", "cond='sun_wind'")],   # Add: UTCI in the shade and still air
    'add_at_top': [("F={k:bimBrdNewK(L),f:f,x:0,y:bimBrdBottom(L),", "F={k:bimBrdNewK(L),f:f,x:0,y:0,")],   # Add: ... below the others
    'add_no_height': [("    F.h=bimBrdNatH(F,F.w);\n    if(A3D_SNAP.grid)F.h=Math.max(1,Math.ceil(F.h-1e-6));\n    L.push(F);", "    if(A3D_SNAP.grid)F.h=Math.max(1,Math.ceil(F.h-1e-6));\n    L.push(F);")],   # Add: ... at its own width and height
    'fit_dead': [("    F.h=bimBrdNatH(F,F.w);\n    if(A3D_SNAP.grid)F.h=Math.max(1,Math.ceil(F.y+F.h-1e-6)-F.y);", "    if(A3D_SNAP.grid)F.h=Math.max(1,Math.ceil(F.y+F.h-1e-6)-F.y);")],   # Fit: back to its content's height
    'dup_dead': [("    L.push(N);\n    return bimBrdCommit(B,L,'Duplicated, below the others',N.k);", "    return bimBrdCommit(B,L,'Duplicated, below the others',N.k);")],   # Duplicate: a second of it
    'remove_not_off': [("off=(B.off||[]).slice();if(off.indexOf(F.f)<0)off.push(F.f);", "off=(B.off||[]).slice();")],   # Remove: off the board, and kept off
    'add_keeps_off': [("    if(B.off&&B.off.indexOf(f)>=0)off=B.off.filter(function(x){return x!==f;});\n", "")],   # added again: no longer off
    'catalogue_all_enabled': [("data-brdaddf=\"'+E.f+'\"'+(ok?'':' disabled')+'>'", "data-brdaddf=\"'+E.f+'\"'+''+'>'")],   # Add a figure: ... not offered
    'dialog_not_board': [("    d.className='a3d-clb a3d-clb-dlg';", "    d.className='a3d-clb-dlg';")],   # the previews in the board's own style
    'esc_closes_board': [("if(!bimBrdEsc())bimClbClose();return true;", "bimClbClose();return true;")],   # Escape closes the dialog; Edit stays
    'reset_dead': [("    delete B.figs;delete B.off;", "    delete B.off;")],   # Reset: the board's own figures in their own places
    'undo_not_redrawn': [("    bimBrdRestored();   /* __acad3dV172b: the open board, as the record now is */\n", "")],   # undo: the board without a list again, drawn so
    # ---- 13. bands and reading order ----
    'rows_no_tolerance': [("if(ry===null||g.y-ry>=0.25)", "if(ry===null||g.y-ry>=0)")],   # a column beside a tall figure: row by row
    'bands_by_top': [("if(cur&&f.y<cur.b-1e-6){cur.f.push(f);", "if(cur&&f.y<cur.t+1e-6){cur.f.push(f);")],   # the board's bands and reading order
    'valid_x_unclamped': [("r.w=bimBrdNum(f.w,1,12,6);r.x=bimBrdNum(f.x,0,12-r.w,0);", "r.w=bimBrdNum(f.w,1,12,6);r.x=bimBrdNum(f.x,0,12,0);")],   # a list read back: sizes held to the board
    # ---- 14. boards of one's own ----
    'notes_lost': [("if(a>=0&&b>a)notes+='<h4>'", "if(0)notes+='<h4>'")],   # its notes: those of the boards its figures come from
    'dup_board_no_kpis': [("        if(!E.kpis||E.kind!==B.kind||!bimFigSrc(ctx,E.f,null))return;", "        return;")],   # the climate board duplicated: ... its indicators on top
    'new_board_menu_lost': [(".concat(['-',['New board','new']])", "")],   # + Board: the three boards, then New board
    'delete_label': [("[c?'Delete the board':'Remove from the set','remove',true]", "['Remove from the set','remove',true]")],   # its menu: ... Delete the board
    'rename_dead': [("    B.name=name;\n    saveSoon();bimBrdRedraw();bimPresPanelRefresh();", "    saveSoon();bimBrdRedraw();bimPresPanelRefresh();")],   # its name
    # ---- 15. Present, Print set, the thumbnail ----
    'present_edit_chrome': [("function bimBrdEditing(){return A3D_CLB.edit&&!A3D_CLB.other;}", "function bimBrdEditing(){return A3D_CLB.edit;}")],   # while Edit is on, the board's page for print and for its thumbnail: ... nothing of Edit
    'band_break_lost': [(".a3d-clb-band{position:relative;break-inside:avoid;page-break-inside:avoid}", ".a3d-clb-band{position:relative}")],   # their rules go with them: on the printed page no band is split
    'thumb_zoom_lost': [(".a3d-clb.prt .a3d-clb-arr{zoom:.86364}", "")],   # the thumbnail: the arranged board zoomed to its page
    # ---- 16. a phone ----
    'phone_flow_lost': [(".a3d-clb.w-s .a3d-clb-fig{position:relative;left:auto!important;top:auto!important;width:auto!important;height:auto!important}", "")],   # on a phone ... one column
    'phone_menu_small': [("@media(pointer:coarse){.a3d-clb-fctl button{width:42px;height:42px}", "@media(pointer:coarse){.a3d-clb-fctl button{width:30px;height:30px}")],   # each figure's menu a finger's size
    'phone_swap_dead': [("    a.x=b.x;a.y=b.y;a.w=b.w;a.h=b.h;b.x=t.x;b.y=t.y;b.w=t.w;b.h=t.h;", "")],   # Later in reading order: the first and the second change places
    # ---- 17. kept ----
    'custom_dropped_on_load': [("        else if(b&&typeof b==='object'&&b.kind==='custom'&&typeof b.id==='string'&&/^board-c\\d{1,6}$/.test(b.id)&&!seen[b.id])", "        else if(0)")],   # the set over a reload: ... a board of one's own
    'figs_dropped_on_load': [("    if(F)r.figs=F;\n", "")],   # the set over a reload: ... their lists
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV172b' in txt
out.write_text(txt, encoding='utf-8')
