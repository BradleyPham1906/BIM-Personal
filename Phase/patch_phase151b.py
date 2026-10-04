"""patch_phase151b.py -- V151: a branch deleted from the panel; the Properties tabs no longer see-through.

- The branch row: the other branches' list on its own line, then Merge In, Compare and Delete.
  Delete asks once ("Delete Option A?") and deletes on the second tap; the branch you are on is
  never in that list. Its versions stay in the project file.
- Found on the V151 screenshot: the Properties tab strip sticks to the top as the panel scrolls,
  but its background was a see-through tint, so a heading scrolled under it showed through
  ("History" over "Project"). It is now the tint over the panel's own colour.
- Found on the phone: HISTORY, BRANCH, MERGE and COMPAREBRANCHES set the History group open but
  left the Properties sheet shut, so on a phone or tablet nothing seemed to happen. They now open
  the sheet."""
NAME = 'patch_phase151b.py'
BASE = 'a6fd24a31cb22160c065b5bcc1482331f46950d55a6992e4817ff04864ff1e45'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


rep("#a3d-right .a3d-ptabs{margin:12px 0 2px;background:var(--pp-hover)}",
    "#a3d-right .a3d-ptabs{margin:12px 0 2px;background:linear-gradient(var(--pp-hover),var(--pp-hover)),var(--pp-bg);box-shadow:0 -4px 0 var(--pp-bg)}")
rep("  var A3D_MERGE=null,A3D_BR_CMP=false,A3D_BR_NEW='';",
    "  var A3D_MERGE=null,A3D_BR_CMP=false,A3D_BR_NEW='',A3D_BR_DEL='',A3D_BR_PICK='';")
rep("""    if(others.length)r+='<div class="a3d-histrow"><select data-brmergefrom="1" aria-label="The branch to merge in">'+others.map(function(b){return '<option value="'+bimEsc(b.name)+'">'+bimEsc(b.name)+'</option>';}).join('')+
      '</select><button type="button" data-histact="merge">Merge In</button><button type="button" data-histact="compare">'+(A3D_BR_CMP?'Hide Compare':'Compare')+'</button></div>';""",
    """    if(!others.some(function(b){return b.name===A3D_BR_DEL;}))A3D_BR_DEL='';
    if(others.length)r+='<div class="a3d-histrow"><select data-brmergefrom="1" aria-label="Another branch: to merge in, compare or delete">'+others.map(function(b){return '<option value="'+bimEsc(b.name)+'"'+(b.name===(A3D_BR_DEL||A3D_BR_PICK)?' selected':'')+'>'+bimEsc(b.name)+'</option>';}).join('')+
      '</select></div><div class="a3d-histrow"><button type="button" data-histact="merge">Merge In</button><button type="button" data-histact="compare">'+(A3D_BR_CMP?'Hide Compare':'Compare')+'</button>'+
      '<button type="button" data-histact="brdelete"'+(A3D_BR_DEL?' class="warn"':'')+'>'+(A3D_BR_DEL?'Delete '+bimEsc(A3D_BR_DEL)+'?':'Delete')+'</button></div>';""")
rep("""    if(k==='compare'){A3D_BR_CMP=!A3D_BR_CMP;refreshProps();return A3D_BR_CMP;}""",
    """    if(k==='compare'){A3D_BR_CMP=!A3D_BR_CMP;refreshProps();return A3D_BR_CMP;}
    if(k==='brdelete'){   /* __acad3dV151: asked once, deleted on the second tap */
      s=document.querySelector('#a3d-propsbody [data-brmergefrom]');n=s?s.value:'';
      if(!n)return null;
      if(A3D_BR_DEL!==n){A3D_BR_DEL=n;refreshProps();return {ask:n};}
      A3D_BR_DEL='';r=bimHistBranchDelete(n);
      if(r.error)a3dToast(r.error);else a3dToast('Branch "'+n+'" deleted: its versions stay in the project file');
      refreshProps();return r;
    }""")
rep("""      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histbranch'))bimHistSwitchUI(ev.target.value);""",
    """      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histbranch'))bimHistSwitchUI(ev.target.value);
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-brmergefrom')){A3D_BR_PICK=ev.target.value;if(A3D_BR_DEL){A3D_BR_DEL='';refreshProps();}}   /* kept through a redraw; another picked: ask again */""")
rep("#a3d-right .a3d-histmore button{min-height:22px;padding:0 8px;font-size:11px}",
    "#a3d-right .a3d-histmore button{min-height:22px;padding:0 8px;font-size:11px}\n#a3d-right #a3d-propsbody button.warn{border-color:#e5534b;color:#ff7b72}\n#a3d-propsbody [data-brmergefrom]{flex:1 1 auto;min-width:0}")
rep("""    bimPropReveal('History');
    refreshProps();paint();""",
    """    bimPropReveal('History');
    if(bimShellOverlay()){var rpH=document.getElementById('a3d-right');if(rpH)rpH.classList.add('open');}   /* __acad3dV151: on a phone or tablet the sheet opens */
    refreshProps();paint();""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
