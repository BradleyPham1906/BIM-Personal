"""falsify_phase118.py -- break the V118 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

GATE = "    if(el.dlg&&ev.key!=='Escape'&&!/^F\\d+$/.test(ev.key))return;\n"

VARIANTS = {
    # ---- Properties renders through the helper, and the helper keeps the markup's values
    'props_replaced': [("    if(gP){bimRenderInto(el.propsbody,bimGridPropsHtml(gP));return;}   /* __acad3dV118 */\n",
                        "    if(gP){el.propsbody.innerHTML=bimGridPropsHtml(gP);return;}\n"),
                       ("      bimRenderInto(el.propsbody,bimModelPropsHtml());   /* __acad3dV118 */\n",
                        "      el.propsbody.innerHTML=bimModelPropsHtml();\n"),
                       ("    bimRenderInto(el.propsbody,h);   /* __acad3dV118: the panel keeps the focus through its own rebuild */\n",
                        "    el.propsbody.innerHTML=h;\n")],
    'no_value_sync': [("      else if(a.type!=='file'&&a.value!==b.value)a.value=b.value;\n", "")],
    'no_select_sync': [("      for(i=0;i<a.options.length&&i<b.options.length;i++)\n"
                        "        if(a.options[i].selected!==b.options[i].selected)a.options[i].selected=b.options[i].selected;\n", "")],

    # ---- the helper's own contract
    'no_refocus': [("    try{s.focus({preventScroll:true});}catch(eF){}\n", "")],
    'no_caret': [("    if(keep.s!==null&&s.value===keep.v){try{s.setSelectionRange(keep.s,keep.e,keep.d||'none');}catch(eR){}}\n", "")],
    'moves_past_unkeyed': [("      while(cur&&cur!==m&&bimMorphKey(cur)===null){c=cur.nextSibling;live.removeChild(cur);cur=c;}\n", "")],
    'moves_past_stale': [("      while(cur&&(k=bimMorphKey(cur))!==null&&!need[k]){m=cur.nextSibling;live.removeChild(cur);cur=m;}\n", "")],

    # ---- the class: the dock
    'dock_replaced': [("    bimRenderInto(host,h+'</div>'+pops);   /* __acad3dV118: the Discipline dropdown keeps the focus */\n",
                       "    host.innerHTML=h+'</div>'+pops;\n")],

    # ---- after any field's change the panel shows the model: one refresh, registered last
    'final_refresh_gone': [("    if(el.propsbody)el.propsbody.addEventListener('change',function(){\n"
                            "      try{refreshProps();}\n", "    if(false)el.propsbody.addEventListener('change',function(){\n"
                            "      try{refreshProps();}\n")],

    # ---- an open dialog owns the keyboard
    'dialog_gate_gone': [(GATE, "")],
    'dialog_gate_eats_fkeys': [(GATE, "    if(el.dlg&&ev.key!=='Escape')return;\n")],
    'dialog_gate_eats_escape': [(GATE, "    if(el.dlg)return;\n")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV118' in txt
out.write_text(txt, encoding='utf-8')
