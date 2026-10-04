"""falsify_phase151.py -- break the V151 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'branch_without_version': [("    if(!H.head)return {error:'Commit a version first: a branch starts at one'};\n", "")],
    'any_name': [("    if(!BIM_BR_NAME.test(name))return {error:", "    if(false)return {error:")],
    'name_twice': [("    if(H.branches.hasOwnProperty(name))return {error:'There is a branch \"'+name+'\" already'};\n", "")],
    'new_stays_put': [("    H.branches[name]=H.head;H.branch=name;", "    H.branches[name]=H.head;")],
    'commit_moves_main': [("H.commits.push(c);H.head=c.id;H.branches[H.branch]=c.id;", "H.commits.push(c);H.head=c.id;H.branches.main=c.id;")],
    'switch_loses_work': [("    if(bimHistDirty())return {error:'Commit or discard the changes first: switching would lose them'};\n", "")],
    'switch_keeps_model': [("    if(st){pushUndo();bimRestoreState(JSON.stringify(st));A3D.selSet=[];}\n    H.branch=name;", "    H.branch=name;")],
    'switch_no_undo': [("    if(st){pushUndo();bimRestoreState(JSON.stringify(st));A3D.selSet=[];}\n    H.branch=name;", "    if(st){bimRestoreState(JSON.stringify(st));A3D.selSet=[];}\n    H.branch=name;")],
    'delete_current': [("    if(name===H.branch)return {error:'Switch to another branch first'};\n", "")],
    'base_ignores_merges': [("if(c){q.push(c.parent||null);if(c.parent2)q.push(c.parent2);}", "if(c){q.push(c.parent||null);}")],
    'theirs_ignored': [("        else if(cb===co){if(ft.hasOwnProperty(f))m[f]=ft[f];}\n", "        else if(cb===co){if(fo.hasOwnProperty(f))m[f]=fo[f];}\n")],
    'element_level_only': [("      for(f in fo)if(fo.hasOwnProperty(f))F[f]=1;\n      for(f in ft)if(ft.hasOwnProperty(f))F[f]=1;\n",
                            "      conflicts.push({key:k,kind:'both',label:bimHistLabel(k,fo),ours:o,theirs:t,fields:[{f:'(the whole element)',base:fb,ours:fo,theirs:ft}]});tree.push([k,o]);return;\n")],
    'conflict_hidden': [("        else{cf.push({f:f,base:fb[f],ours:fo[f],theirs:ft[f]});if(fo.hasOwnProperty(f))m[f]=fo[f];}", "        else{if(fo.hasOwnProperty(f))m[f]=fo[f];}")],
    'delete_wins_quietly': [("        conflicts.push({key:k,kind:'deleted',label:bimHistLabel(k,val(o!==undefined?o:t)),gone:o===undefined?'ours':'theirs',ours:o,theirs:t,fields:[]});\n", "")],
    'new_on_other_lost': [("    theirs.tree.forEach(function(e){if(!seen[e[0]]){keys.push(e[0]);seen[e[0]]=1;}});\n", "")],
    'no_fast_forward': [("    if(base===oid)return bimHistFastForward(from,tid);\n", "")],
    'up_to_date_merges': [("    if(base===tid)return {upToDate:true,msg:'\"'+H.branch+'\" already has everything in \"'+from+'\"'};\n", "")],
    'merge_into_self': [("    if(from===H.branch)return {error:'A branch cannot be merged into itself'};\n", "")],
    'merge_over_work': [("    if(bimHistDirty())return {error:'Commit or discard the changes first'};\n", "")],
    'finish_undecided': [("    for(i=0;i<M.conflicts.length;i++)if(!M.conflicts[i].choice)return {error:", "    for(i=0;i<0;i++)if(!M.conflicts[i].choice)return {error:")],
    'take_ignored': [("        cf.fields.forEach(function(f){var x=cf.choice==='ours'?f.ours:f.theirs;", "        cf.fields.forEach(function(f){var x=f.ours;")],
    'delete_take_ignored': [("        v=cf.choice==='ours'?cf.ours:cf.theirs;", "        v=cf.ours;")],
    'no_second_parent': [("    if(parent2)c.parent2=parent2;   /* __acad3dV151: a merge */\n", "")],
    'abort_keeps_merge': [("  function bimHistMergeAbort(){var had=!!A3D_MERGE;A3D_MERGE=null;", "  function bimHistMergeAbort(){var had=!!A3D_MERGE;")],
    'compare_current_stale': [("      var st=b.current?JSON.parse(bimSnapshotState()):", "      var st=b.current&&!b.head?JSON.parse(bimSnapshotState()):")],
    'compare_no_diff_mark': [("(same?'':' class=\"diff\"')", "('')")],
    'log_all_branches': [("    var C=H.commits.filter(function(c){return line[c.id];}).reverse(),sz=bimHistSize();", "    var C=H.commits.slice().reverse(),sz=bimHistSize();")],
    'finish_not_greyed': [("data-histact=\"mfinish\"'+(left?' disabled':'')+'>", "data-histact=\"mfinish\">")],
    'enter_dead': [("      if(ev.key==='Enter'&&ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-brname')){ev.preventDefault();ev.stopPropagation();bimHistBranchAct('branch');return;}   /* __acad3dV151 */\n", "")],
    'picker_dead': [("      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histbranch'))bimHistSwitchUI(ev.target.value);", "")],
    'not_saved': [("    if(h.branches&&typeof h.branches==='object')for(k in h.branches)", "    if(false)for(k in h.branches)")],
    'branch_not_restored': [("    var cur=typeof h.branch==='string'&&br.hasOwnProperty(h.branch)?h.branch:'main';", "    var cur='main';")],
    'no_branch_command': [("    ['BRANCH',['NEWBRANCH','DESIGNOPTION','OPTION'],'branch',", "    ['BRANCHX',['NEWBRANCHX'],'branchx',")],
    'delete_no_ask': [("      if(A3D_BR_DEL!==n){A3D_BR_DEL=n;refreshProps();return {ask:n};}\n", "")],
    'pick_lost': [("A3D_BR_PICK=ev.target.value;", "")],
    'tabs_see_through': [("#a3d-right .a3d-ptabs{margin:12px 0 2px;background:linear-gradient(var(--pp-hover),var(--pp-hover)),var(--pp-bg);", "#a3d-right .a3d-ptabs{margin:12px 0 2px;background:var(--pp-hover);")],
    'sheet_stays_shut': [("    if(bimShellOverlay()){var rpH=document.getElementById('a3d-right');if(rpH)rpH.classList.add('open');}", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV151' in txt
out.write_text(txt, encoding='utf-8')
