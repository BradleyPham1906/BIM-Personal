"""patch_phase85.py -- __acad3dV85: the "A?" button was a dead control. Replace it with a real one.

WHAT THE USER ASKED: "whats that a? thing then its useless"

WHAT IT WAS. Measured, by clicking it with a real pointer on the shipped build:

    A? button: {'text': 'A?', 'title': None, 'x': 15, 'y': 906, 'w': 24, 'h': 24,
                'attrs': ['class=fl-help']}
    before: {'dlgs': 0, 'toast': None}
    after : {'dlgs': 0, 'toast': None}

Nothing. No handler anywhere in the file, no title attribute, no panel. It came from the
whiteboard shell's template as a piece of Figma-style set dressing and was never wired. The user
is right: it is useless.

THE PART THAT IS MY FAULT. V80 added a whitelist so that any control in the left shell which is
not claimed fails the build -- and I claimed this one:

    {sel:'.fl-help', why:'keyboard help'}

on the strength of its appearance, without ever driving it. A whitelist entry taken on faith is
worse than no whitelist, because it converts an unexamined control into a documented one. The
audit has been reporting a clean shell over a dead button ever since. The lesson is the same one
V84 recorded for `.a3d-bdel` and did honour: claim a control only after driving it.

WHAT SHIPS INSTEAD. The app has a real and fairly deep set of keyboard shortcuts -- F3/F8/F9
snaps, the Escape chain, type-an-exact-length while drawing, C to close a path, arrow nudge -- and
no way to discover any of them. So the dead button is removed and a real Keyboard shortcuts sheet
joins the V83 rail utility stack as its sixth entry, which is also where the user asked for these
controls to live ("just like how rayon have in vertical stack").

The sheet renders from A3D_KEYS, one registry, and the Phase 85 suite DISPATCHES every row that
names a single key and asserts the documented effect actually happens. That is the V74 rule --
never hand-list what can be derived -- applied to the one case where it cannot be fully derived:
the key handlers are a switch chain, not a table, so the list is written once and then held to
account by the suite rather than trusted.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = 'aaeebb06f5af81c150d290e0ecd0565781918565beb689ae22cb4c8c961348db'

src = SRC.read_bytes()
have = hashlib.sha256(src).hexdigest()
if have != BASE:
    print('ABORT: baseline mismatch\n  expected %s\n  found    %s' % (BASE, have))
    sys.exit(1)
print('baseline ok: %s (%d bytes)' % (have[:16], len(src)))

text = src.decode('utf-8')
edits = 0


def sub(old, new, label, count=1):
    global text, edits
    n = text.count(old)
    if n != count:
        print('ABORT: %s: expected %d occurrence(s), found %d' % (label, count, n))
        sys.exit(1)
    text = text.replace(old, new, count)
    edits += 1
    print('  edit %d ok: %s' % (edits, label))


# ------------------------------------------------------------------ 1. the icon
OLD_ICONS = """    capture:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<path d="M4 8h3l1.5-2h7L17 8h3v11H4z"/><circle cx="12" cy="13" r="3.2"/></svg>'
  };"""
NEW_ICONS = """    capture:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<path d="M4 8h3l1.5-2h7L17 8h3v11H4z"/><circle cx="12" cy="13" r="3.2"/></svg>',
    /* __acad3dV85: a keyboard, because that is what this one opens. The button it replaces
       said "A?" and did nothing at all. */
    help:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'+
      '<rect x="2.5" y="6.5" width="19" height="11" rx="2"/>'+
      '<path d="M6 10h.01M9 10h.01M12 10h.01M15 10h.01M18 10h.01M8 13.5h8"/></svg>'
  };"""
sub(OLD_ICONS, NEW_ICONS, 'the shortcuts icon')

# ------------------------------------------------------------------ 2. the stack entry
OLD_UTILS = """    {id:'capture',label:'Save image', menu:false}
  ];"""
NEW_UTILS = """    {id:'capture',label:'Save image', menu:false},
    {id:'help',   label:'Keyboard shortcuts', menu:true}
  ];

  /* ---- __acad3dV85: the shortcut registry ----

     One list, rendered into the sheet AND driven by the Phase 85 suite: every row carrying a
     `k` is dispatched as a real key event and asserted to do what its label claims. The key
     handlers in this app are a switch chain rather than a table, so this list cannot be derived
     from them the way V74 derived the schedule categories. Holding it to account with the suite
     is the next best thing, and it is what stops the sheet drifting into fiction -- which is
     precisely what the button this replaces had become.

     `k` is the ev.key value; `mod` means Ctrl (Cmd on a Mac). A row with k:null documents
     something a single synthetic keypress cannot demonstrate, and says so here rather than
     pretending. */
  var A3D_MODKEY=(navigator.platform&&/Mac|iPhone|iPad/.test(navigator.platform))?'Cmd':'Ctrl';
  var A3D_KEYS=[
    {grp:'Views',rows:[
      {keys:['Shift','>'],k:'>',label:'Switch between the plan and 3D'},
      {keys:['Esc'],k:'Escape',label:'Back out one step: menu, zoom window, dialog, sketch, section, plan'}
    ]},
    {grp:'Drawing',rows:[
      {keys:['Enter'],k:null,label:'Finish the current wall, polyline or stair'},
      {keys:['C'],k:null,label:'Close the current wall or polyline path'},
      {keys:['0-9'],k:null,label:'Type an exact length while drawing, then Enter to commit it'},
      {keys:['Arrows'],k:null,label:'Nudge the selected object'}
    ]},
    {grp:'Snaps',rows:[
      {keys:['F3'],k:'F3',label:'Object snap on or off'},
      {keys:['F8'],k:'F8',label:'Ortho on or off'},
      {keys:['F9'],k:'F9',label:'Grid snap on or off'}
    ]},
    {grp:'Editing',rows:[
      {keys:[A3D_MODKEY,'Z'],k:'z',mod:true,label:'Undo'},
      {keys:[A3D_MODKEY,'Y'],k:'y',mod:true,label:'Redo'},
      {keys:[A3D_MODKEY,'D'],k:'d',mod:true,label:'Duplicate the selection'},
      {keys:['Delete'],k:null,label:'Delete the selection'}
    ]},
    {grp:'Project',rows:[
      {keys:[A3D_MODKEY,'S'],k:null,label:'Export the project file'},
      {keys:[A3D_MODKEY,'K'],k:null,label:'Command palette'}
    ]}
  ];
  function bimShortcutsHtml(){
    var h='<div class="a3d-ruhd">Keyboard shortcuts</div><div class="a3d-rukeys">',g,r,i,j,k;
    for(i=0;i<A3D_KEYS.length;i++){
      g=A3D_KEYS[i];
      h+='<div class="a3d-rkgrp">'+bimEsc(g.grp)+'</div>';
      for(j=0;j<g.rows.length;j++){
        r=g.rows[j];
        h+='<div class="a3d-rkrow"><span class="a3d-rkkeys">';
        for(k=0;k<r.keys.length;k++){
          if(k)h+='<span class="a3d-rkplus">+</span>';
          h+='<kbd>'+bimEsc(r.keys[k])+'</kbd>';
        }
        h+='</span><span class="a3d-rklab">'+bimEsc(r.label)+'</span></div>';
      }
    }
    return h+'</div>';
  }"""
sub(OLD_UTILS, NEW_UTILS, 'the shortcuts registry and sheet renderer')

# ------------------------------------------------------------------ 3. the menu branch
OLD_MENU = """    return '<div class="a3d-ruhd">'+bimEsc(id)+'</div>';
  }
  function bimPresentModeOn(){return !!A3D.presentMode;}"""
NEW_MENU = """    if(id==='help')return bimShortcutsHtml();
    return '<div class="a3d-ruhd">'+bimEsc(id)+'</div>';
  }
  function bimPresentModeOn(){return !!A3D.presentMode;}"""
sub(OLD_MENU, NEW_MENU, 'the help menu opens the shortcuts sheet')

# ------------------------------------------------------------------ 4. remove the dead button
OLD_ENSURE = """  function bimEnsureRailStack(){
    var rail=document.getElementById('figma-layers-rail');
    if(!rail||!A3D.on)return false;
    if(rail.querySelector('#a3d-railutil'))return false;
    var help=rail.querySelector('.fl-help');
    var box=document.createElement('div');
    box.innerHTML=bimRailStackHtml();
    var node=box.firstChild;
    if(help)rail.insertBefore(node,help);else rail.appendChild(node);
    return true;
  }"""
NEW_ENSURE = """  function bimEnsureRailStack(){
    var rail=document.getElementById('figma-layers-rail');
    if(!rail||!A3D.on)return false;
    /* __acad3dV85: the whiteboard shell's "A?" button is REMOVED here, not left sitting under
       the stack. It had no click handler anywhere in the file, no title, and opened nothing --
       driven with a real pointer it produced no dialog, no toast and no visible change. It was
       Figma-style set dressing in a template this app inherited. Its job, keyboard help, is now
       a real entry in the stack above. Removed on every pass rather than once, because the
       whiteboard shell re-renders its own rail and would put it back. */
    var dead=rail.querySelector('.fl-help'),did=false;
    if(dead&&dead.parentNode){dead.parentNode.removeChild(dead);did=true;}
    if(rail.querySelector('#a3d-railutil'))return did;
    var box=document.createElement('div');
    box.innerHTML=bimRailStackHtml();
    rail.appendChild(box.firstChild);
    return true;
  }"""
sub(OLD_ENSURE, NEW_ENSURE, 'the dead A? button is removed from the rail')

# ------------------------------------------------------------------ 5. drop the unearned claim
OLD_CLAIM = "    {sel:'.fl-help',why:'keyboard help'},\n"
NEW_CLAIM = """    /* __acad3dV85: '.fl-help' -- the "A?" button -- used to be claimed here as 'keyboard
       help'. It was claimed on the strength of its appearance and never driven; it had no
       handler at all. A whitelist entry taken on faith is worse than no whitelist, because it
       turns an unexamined control into a documented one. The button is gone and so is its
       claim. Claim a control only after driving it. */
"""
sub(OLD_CLAIM, NEW_CLAIM, 'the unearned .fl-help claim is removed')

# ------------------------------------------------------------------ 6. styling
OLD_CSS = "body.a3d-mode #figma-layers-rail .fl-help{margin-bottom:10px}'+"
NEW_CSS = ("'+"
           "'.a3d-rukeys{min-width:336px;max-height:64vh;overflow:auto;padding:0 2px 2px}"
           ".a3d-rkgrp{font-size:9.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;"
           "color:#8b949e;padding:9px 8px 4px}"
           ".a3d-rkrow{display:flex;align-items:baseline;gap:10px;padding:4px 8px;border-radius:5px}"
           ".a3d-rkrow:hover{background:#2a2f35}"
           ".a3d-rkkeys{flex:0 0 96px;display:flex;align-items:center;gap:3px;justify-content:flex-end}"
           ".a3d-rkkeys kbd{font:600 10px/1 Inter,system-ui,sans-serif;color:#c7ced6;background:#1c2024;"
           "border:1px solid #3a4048;border-bottom-width:2px;border-radius:4px;padding:3px 5px;white-space:nowrap}"
           ".a3d-rkplus{color:#6e7781;font-size:9px}"
           ".a3d-rklab{flex:1;color:#c3cad2;font-size:11.5px;line-height:1.35}"
           "body.light-theme .a3d-rkkeys kbd{color:#333;background:#f2f3f5;border-color:#c9ced4}"
           "body.light-theme .a3d-rklab{color:#333}'+")
sub(OLD_CSS, NEW_CSS, 'styling for the shortcuts sheet')

# ------------------------------------------------------------------ 7. hooks + marker
OLD_HOOK = "  window.__a3dSyncViewLabel=bimSyncViewLabel;"
NEW_HOOK = """  window.__a3dSyncViewLabel=bimSyncViewLabel;
  window.__a3dShortcuts=function(){return JSON.parse(JSON.stringify(A3D_KEYS));};
  window.__acad3dV85='shortcutsheet,deadhelpremoved,railstackhelp,unearnedclaimdropped';"""
sub(OLD_HOOK, NEW_HOOK, 'the shortcuts hook and the V85 marker')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
