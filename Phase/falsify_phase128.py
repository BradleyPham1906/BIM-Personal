"""falsify_phase128.py -- break the V128 build one way at a time, keeping the marker.

Each variant takes back one thing V128 does, and the V128 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 128a: the catalogue and the search
    'no_ribbon_merge': [("      var same=(cad&&byCad[cad])||(byName[nm]?[byName[nm]]:null);", "      var same=null;")],
    'ribbon_left_out': [("    var all=a3drAllCommands();\n    for(i=0;i<all.length;i++){\n      var a=all[i].act,where=", "    var all=[];\n    for(i=0;i<all.length;i++){\n      var a=all[i].act,where=")],
    'keys_not_read': [("        keys:keys[c.name]||null,terms:BIM_CMD_TERMS[c.name]||''};", "        keys:null,terms:BIM_CMD_TERMS[c.name]||''};")],
    'no_synonyms': [("        keys:keys[c.name]||null,terms:BIM_CMD_TERMS[c.name]||''};", "        keys:keys[c.name]||null,terms:''};")],
    'alias_not_exact': [("    for(i=0;i<it.aliases.length;i++)if(it.aliases[i].toLowerCase()===t)return {tier:1};\n", "")],
    'any_word_matches': [("        if(r.tier<0){ok=false;break;}", "        if(r.tier<0){continue;}")],
    'no_abbreviation': [("    if(t.length>=2&&nm.charAt(0)===t.charAt(0)){var sq=bimSubseq(nm,t);if(sq)return {tier:6,hl:sq};}", "")],
    'no_key_chords': [("      if(kn===tn)return {tier:1.5};", "")],
    'cmd_not_ctrl': [("  function bimKeyNorm(s){return String(s||'').toLowerCase().replace(/\\s+/g,'').replace(/cmd|ctrl|control|meta|\\u2318/g,'mod');}",
                      "  function bimKeyNorm(s){return String(s||'').toLowerCase().replace(/\\s+/g,'');}")],
    'typo_always_offered': [("    if(direct.length)res=direct;\n", "")],
    'no_typo': [("      if(bimEditWithin1(t,nm))return {tier:8,typo:true};\n", "")],
    'no_frequency': [("    res.sort(function(a,b){return (a.s-b.s)||(b.n-a.n)||(a.i-b.i);});", "    res.sort(function(a,b){return (a.s-b.s)||(a.i-b.i);});")],
    'frequency_over_match': [("    res.sort(function(a,b){return (a.s-b.s)||(b.n-a.n)||(a.i-b.i);});", "    res.sort(function(a,b){return (b.n-a.n)||(a.s-b.s)||(a.i-b.i);});")],
    'recent_by_count': [("    ids.sort(function(a,b){return use[b].t-use[a].t;});", "    ids.sort(function(a,b){return use[b].n-use[a].n;});")],
    'usage_not_saved': [("    try{localStorage.setItem(BIM_CMD_USE_KEY,JSON.stringify(u));}", "    try{}")],
    'ribbon_run_not_repeatable': [("      if(ran)bimRecordCmd(function(){bimRunAct(it.act);},it.act);   /* Enter repeats it, as it repeats a typed command */\n", "")],
    'no_off_reason': [("    if(bimSheetOnScreen())return (it.cad?BIM_SHEET_CMDS[it.cad]:BIM_SHEET_ACTS[it.act])?'':'works on the model, not a sheet';", "")],
    # ---- 128b: the palette and type-anywhere
    'no_highlight': [("      if(!c.hl||!c.hl.length)return escH(n);", "      return escH(n);")],
    'no_recent_section': [("var rec=(!q&&window.__a3dCommandRecent)?window.__a3dCommandRecent(5):[]", "var rec=[]")],
    'recent_listed_twice': [("        var rest=res.filter(function(c){return !seen[c.id];});", "        var rest=res;")],
    'no_tab_cycle': [("      else if(e.key==='Tab'){if(n){active=(active+(e.shiftKey?n-1:1))%n;highlight();}e.preventDefault();}   /* AutoCAD: Tab cycles */\n", "")],
    'no_shortcut_mode': [("      if(q.charAt(0)==='?'){", "      if(false){")],
    'shortcut_row_does_not_run': [("        if(c.cmd&&window.__a3dCommandRun){if(!window.__a3dCommandRun('cmd:'+c.cmd)", "        if(false){if(!window.__a3dCommandRun('cmd:'+c.cmd)")],
    'no_type_anywhere': [("        e.preventDefault();openPal(e.key);\n", "")],
    'type_anywhere_drops_letter': [("        e.preventDefault();openPal(e.key);\n", "        e.preventDefault();openPal();\n")],
    'no_aria_active': [("      if(cur){input.setAttribute('aria-activedescendant',cur.id);", "      if(cur){")],
    'where_not_shown': [("      else if(c.where&&c.where.length)meta+=", "      else if(false)meta+=")],
    'alias_not_shown': [("      if(c.aliases&&c.aliases.length)meta+='<span class=\"a3d-cmdkey\" title=\"Also typed as '", "      if(false)meta+='<span class=\"a3d-cmdkey\" title=\"Also typed as '")],
    'keys_not_shown': [("      meta+=kbdHtml(c.keys);\n      return '<div class=\"a3d-cmdrow'+(c.off?", "      return '<div class=\"a3d-cmdrow'+(c.off?")],
    # ---- 128c: one search, tooltips, the sheet
    'magnifier_opens_nothing': [("        if(window.openPalette)window.openPalette();\n        return;\n      }", "        return;\n      }")],
    'no_tooltip_hint': [("      if((cad&&it.cad===cad)||it.act===act||it.ribbon===act)return '  \\u00b7  type '", "      if(false)return '  \\u00b7  type '")],
    'sheet_not_searchable': [("    var words=norm(q).split(/\\s+/).filter(function(w){return !!w;}),kids=p.querySelectorAll('.a3d-rukeys > *'),i,grp=null,any=false,shown=0;",
                              "    return 0;var words=norm(q).split(/\\s+/).filter(function(w){return !!w;}),kids=p.querySelectorAll('.a3d-rukeys > *'),i,grp=null,any=false,shown=0;")],
    'hidden_rows_still_drawn': [(".a3d-rukeys [hidden]{display:none!important}", "")],
    'sheet_escape_closes_at_once': [("        if(ev.target.value){ev.target.value='';bimFilterShortcuts(p,'');}\n        else{", "        {")],
    'sheet_not_focused': [("    if(rkf){try{rkf.focus({preventScroll:true});}catch(eFo){}}", "")],
    # ---- 128d: the type-anywhere test
    'type_anywhere_during_tool': [("      if(A3D.sk||A3D.face||A3D.facePick||A3D.conPick||A3D.zoomWindow||A3D_TYPING.active||drag||bimTypingDrag())return false;",
                                   "      if(A3D.face||A3D.facePick||A3D.conPick||A3D.zoomWindow||A3D_TYPING.active||drag||bimTypingDrag())return false;")],
    'type_anywhere_over_dialog': [("      if(bimStartShowing()||bimSheetOnScreen()||A3D_SLIDESHOW.on||el.dlg)return false;", "      if(bimStartShowing()||bimSheetOnScreen()||A3D_SLIDESHOW.on)return false;")],
    'type_anywhere_any_key': [("!/^[A-Za-z?]$/.test(ev.key||'')", "!/^.$/.test(ev.key||'')")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV128' in txt
out.write_text(txt, encoding='utf-8')
