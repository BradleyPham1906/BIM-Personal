"""falsify_phase146.py -- break the V146 build one way at a time, keeping the marker.

Each variant takes back one thing V146 does, and the V146 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the store
    'canon_unsorted': [("    var k=Object.keys(v).filter(function(x){return v[x]!==undefined&&typeof v[x]!=='function';}).sort();",
                        "    var k=Object.keys(v).filter(function(x){return v[x]!==undefined&&typeof v[x]!=='function';});")],
    'hash_one_seed': [("    for(q=0;q<2;q++){\n      h1=0xdeadbeef^seeds[q];", "    for(q=0;q<1;q++){\n      h1=0xdeadbeef^seeds[q];")],
    'imul_float': [("  function bimImul(a,b){var ah=(a>>>16)&0xffff,al=a&0xffff,bh=(b>>>16)&0xffff,bl=b&0xffff;return ((al*bl)+(((ah*bl+al*bh)<<16)>>>0))|0;}",
                    "  function bimImul(a,b){return (a*b)|0;}")],
    'parts_left_out': [("    BIM_HIST_PARTS.forEach(function(p){put('@'+p[0],st[p[0]]===undefined?null:st[p[0]]);});\n", "")],
    'blobs_not_kept': [("    W.tree.forEach(function(e){if(!H.blobs.hasOwnProperty(e[1]))H.blobs[e[1]]=W.blobs[e[1]];});", "")],
    # ---- the diff
    'removed_unseen': [("    if(ta)ta.forEach(function(e){if(e[0]!=='#meta'&&!mb.hasOwnProperty(e[0]))out.push({key:e[0],kind:'removed'});});\n", "")],
    'meta_shown': [("    tb.forEach(function(e){if(e[0]==='#meta')return;if(!ma.hasOwnProperty(e[0]))", "    tb.forEach(function(e){if(!ma.hasOwnProperty(e[0]))")],
    'moved_backwards': [("join(', '),from:va,to:vb});return;}", "join(', ').replace(/^/,'-'),from:va,to:vb});return;}")],
    'records_whole': [("  function bimHistIdArr(v){return Array.isArray(v)&&v.length>0&&", "  function bimHistIdArr(v){return false&&Array.isArray(v)&&v.length>0&&")],
    'fields_not_walked': [("        if(va&&vb&&typeof va==='object'&&typeof vb==='object'&&!Array.isArray(va)&&!Array.isArray(vb)&&depth<3){walk(va,vb,p,depth+1);return;}\n", "")],
    # ---- commits
    'empty_commit_allowed': [("    if(!d.length)return {error:head?'Nothing has changed since \"'+head.msg+'\"':'There is nothing to commit yet'};\n", "")],
    'no_parent': [("parent:head?head.id:null,msg:msg,", "parent:null,msg:msg,")],
    'message_dropped': [("msg=String(msg==null?'':msg).replace(/^\\s+|\\s+$/g,'').slice(0,200)||('Version '+(H.commits.length+1));",
                         "msg='Version '+(H.commits.length+1);")],
    # ---- restore
    'restore_not_undoable': [("    if(!st)return {error:'\"'+c.msg+'\" is damaged: some of its elements are missing'};\n    pushUndo();\n",
                              "    if(!st)return {error:'\"'+c.msg+'\" is damaged: some of its elements are missing'};\n")],
    'restore_rewrites': [("    return {id:c.id,msg:c.msg,objs:st.objs.length};", "    bimHist().commits.splice(bimHist().commits.indexOf(c)+1);bimHist().head=c.id;\n    return {id:c.id,msg:c.msg,objs:st.objs.length};")],
    'restore_skips_parts': [("      else st[k.slice(1)]=v;\n    }\n    return st;", "    }\n    return st;")],
    # ---- an element's history
    'element_history_kinds': [("var r={id:c.id,msg:c.msg,at:c.at,kind:h===undefined?'removed':ph===undefined?'added':'changed'};",
                               "var r={id:c.id,msg:c.msg,at:c.at,kind:h===undefined?'added':ph===undefined?'removed':'changed'};")],
    'no_object_group': [("    if(A3D.history&&A3D.history.commits&&A3D.history.commits.length)h+=bimPropGroup('History',bimHistObjHtml(o));   /* __acad3dV146 */\n", "")],
    # ---- saved with the project
    'not_saved': [("dataFeatures:A3D.dataFeatures||{},history:A3D.history||null};   /* __acad3dV146 */", "dataFeatures:A3D.dataFeatures||{}};")],
    'not_loaded': [("      A3D.history=bimHistValid(st&&st.history);   /* __acad3dV146: its history, or none */\n", "")],
    # ---- the group and the commands
    'no_group': [("    h+=bimPTab('project',bimPropGroup('History',bimHistHtml()));   /* __acad3dV146 */\n", "")],
    'enter_does_nothing': [("      ev.preventDefault();ev.stopPropagation();\n      bimHistDoCommit(ev.target.value);", "      return;")],
    'commit_ignores_message': [("    if(k==='commit'){var inp=document.querySelector('#a3d-propsbody [data-histmsg]');return bimHistDoCommit((inp&&inp.value)||A3D_HIST_MSG);}",
                                "    if(k==='commit'){return bimHistDoCommit('');}")],
    'message_lost_on_render': [("      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histmsg'))A3D_HIST_MSG=ev.target.value;", "")],
    'discard_dead': [("    if(k==='discard'){var hd=bimHistHead();return hd?bimHistDoRestore(hd.id):null;}", "    if(k==='discard'){return null;}")],
    'changes_never_open': [("    if(k.indexOf('show:')===0){var id=k.slice(5);A3D_HIST_OPEN[id]=!A3D_HIST_OPEN[id];refreshProps();return true;}", "    if(k.indexOf('show:')===0){return true;}")],
    'commit_command_no_focus': [("    return bimHistReveal(true);\n  }", "    return bimHistReveal(false);\n  }")],
    'no_commands': [("    commit:function(){bimHistCommitCommand();},        /* __acad3dV146 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV146' in txt
out.write_text(txt, encoding='utf-8')
