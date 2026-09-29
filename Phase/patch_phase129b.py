"""patch_phase129b.py -- V129: the tool dock says what its tools are.

The dock was two rows of bare icons: no tool had a name on screen, no group said what it was, the
caret that opens a group's other tools was a bare triangle, and the search was a magnifier with
nothing beside it. Revit's panels and Fusion's toolbar name every group; Figma's and Google Docs'
tooltips give a tool's name and its keys; the rule of thumb from the tooltip research: if a user
cannot finish a task without the tooltip, the text belongs on the button.

- Every group has its name under it (Architecture, Drafting, Modify ...).
- Every tool has its name under its icon. Appearance (the rail) switches that off for icons only:
  "Tool names on the dock" / "Icons only", kept per browser.
- A tooltip for every tool, after a short pause on hover and at once on keyboard focus: its name,
  its keys if it has any, what to type for it ("Type WALL or WA"), what it does, and where it sits.
  It replaces the browser's plain title, which said less and came late.
- The caret is "More", with the dots of a menu; its tooltip names the group.
- The magnifier is a search box you can read: "Search tools and commands", with Ctrl K."""
NAME = 'patch_phase129b.py'
BASE = '27f698196a74db1ce31d4519a6878c8ef575519bebbe12f1be1f871c2f234def'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---- the dock, drawn with names
rep("""    var h='<div class="a3d-dockbody">',pops='',r,g,tab,prim,i,grps,gi,ai,act,cat=bimCmdCatalog();   /* __acad3dV128 */""",
    """    var h='<div class="a3d-dockbody">',pops='',r,g,tab,prim,i,grps,gi,ai,act,cat=bimCmdCatalog();   /* __acad3dV128 */
    var names=bimDockLabelsOn();   /* __acad3dV129: tool names under the icons, unless Icons only */
    host.classList.toggle('a3d-docklabels',names);""")
rep("""      '<button class="a3d-dbtn" id="a3d-dsearch" title="Search every command and tool (Ctrl+K, or start typing on the drawing)">'+
      A3DR_SEARCH_ICON+'</button>'+""", """      '<button type="button" class="a3d-dsearchpill" id="a3d-dsearch" aria-label="Search tools and commands" data-a3dtip="__search">'+
      A3DR_SEARCH_ICON+'<span>Search tools and commands</span><kbd>'+bimEsc(A3D_MODKEY)+' K</kbd></button>'+   /* __acad3dV129: a search you can read */""")
rep("""        h+='<div class="a3d-dockgrp" data-dockgrp="'+tab.id+'">';
        for(i=0;i<prim.length;i++)
          h+='<button class="a3d-dbtn" data-a3dr="'+prim[i]+'" title="'+
            bimEsc(a3drLabel(prim[i])+'  \\u00b7  '+tab.name+bimActHint(prim[i],cat))+'">'+a3drIcon(prim[i])+'</button>';
        h+='<button class="a3d-dcar" data-dockmore="'+tab.id+'" title="'+
          bimEsc(tab.name+' \\u2014 all tools')+'">\\u25b4</button>';
        h+='</div>';""", """        h+='<div class="a3d-dockgrp" data-dockgrp="'+tab.id+'"><div class="a3d-dgtools">';
        for(i=0;i<prim.length;i++)   /* __acad3dV129: a name under the icon, a tooltip instead of a title */
          h+='<button type="button" class="a3d-dbtn" data-a3dr="'+prim[i]+'" data-a3dtip="'+prim[i]+'" aria-label="'+
            bimEsc(a3drLabel(prim[i])+bimActHint(prim[i],cat))+'">'+a3drIcon(prim[i])+
            (names?'<span class="a3d-dblbl">'+bimEsc(a3drLabel(prim[i]))+'</span>':'')+'</button>';
        h+='<button type="button" class="a3d-dcar" data-dockmore="'+tab.id+'" data-a3dtip="__more:'+bimEsc(tab.name)+'" aria-label="'+
          bimEsc('All '+tab.name+' tools')+'">'+(names?A3DR_MORE_ICON+'<span class="a3d-dblbl">More</span>':'\\u25b4')+'</button>';
        h+='</div><span class="a3d-dglbl">'+bimEsc(tab.name)+'</span></div>';""")
rep("""            pops+='<div class="a3d-dockitem'+(a3drIsUnimpl(act)?' a3dr-dis':'')+'" data-a3dr="'+act+'"'+
              (a3drIsUnimpl(act)?' title="Not implemented yet"':(bimActHint(act,cat)?' title="'+bimEsc(a3drLabel(act)+bimActHint(act,cat))+'"':''))+'>'+a3drIcon(act)+""",
    """            pops+='<div class="a3d-dockitem'+(a3drIsUnimpl(act)?' a3dr-dis':'')+'" data-a3dr="'+act+'" data-a3dtip="'+act+'">'+a3drIcon(act)+""")

# ---- the tooltip
rep("""  var A3DR_SEARCH_ICON=ric(""", r"""  /* ================= __acad3dV129: the dock's tooltips and its names ================= */
  var A3DR_MORE_ICON=ric('<circle cx="6" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="18" cy="12" r="1.3"/>');
  function bimDockLabelsOn(){var p=bimLoadUIPanelPrefs();return p.dockLabels!==false;}
  function bimSetDockLabels(on){
    var p=bimLoadUIPanelPrefs();p.dockLabels=!!on;bimSaveUIPanelPrefs(p);
    bimBuildDock();
    a3dToast(on?'Tool names are shown on the dock':'The dock shows icons only; hover a tool for its name');
  }
  /* what a tooltip says: the tool's name, its keys, what to type for it, what it does, where it is */
  function bimDockTipData(spec){
    if(spec==='__search')return {name:'Search tools and commands',keys:[A3D_MODKEY,'K'],desc:'Or just start typing a command on the drawing',type:[],where:''};
    if(spec.indexOf('__more:')===0)return {name:'More',keys:null,desc:'All '+spec.slice(7)+' tools',type:[],where:''};
    var cat=bimCmdCatalog(),cad=BIM_ACT_CMD[spec],it=null,i;
    for(i=0;i<cat.length;i++)if((cad&&cat[i].cad===cad)||cat[i].act===spec||cat[i].ribbon===spec){it=cat[i];break;}
    if(a3drIsUnimpl(spec))return {name:a3drLabel(spec),keys:null,desc:'Not built yet',type:[],where:'',off:true};
    if(!it)return {name:a3drLabel(spec),keys:null,desc:'',type:[],where:''};
    return {name:a3drLabel(spec),keys:it.keys,desc:it.desc,type:[it.name].concat(it.aliases.slice(0,1)),where:it.where[0]||''};
  }
  function bimDockTipHtml(spec){
    var d=bimDockTipData(spec),h='<div class="a3d-tiphd"><strong>'+bimEsc(d.name)+'</strong>',k;
    if(d.keys){h+='<span class="a3d-tipkeys">';for(k=0;k<d.keys.length;k++)h+=(k?'<i>+</i>':'')+'<kbd>'+bimEsc(d.keys[k])+'</kbd>';h+='</span>';}
    h+='</div>';
    if(d.type.length)h+='<div class="a3d-tiptype">Type '+d.type.map(function(x){return '<b>'+bimEsc(x)+'</b>';}).join(' or ')+'</div>';
    if(d.desc)h+='<div class="a3d-tipdesc'+(d.off?' off':'')+'">'+bimEsc(d.desc)+'</div>';
    if(d.where)h+='<div class="a3d-tipwhere">'+bimEsc(d.where)+'</div>';
    return h;
  }
  var A3D_TIP={el:null,timer:null,at:null};
  function bimTipHide(){
    if(A3D_TIP.timer){clearTimeout(A3D_TIP.timer);A3D_TIP.timer=null;}
    if(A3D_TIP.el)A3D_TIP.el.classList.remove('show');
    if(A3D_TIP.at){A3D_TIP.at.removeAttribute('aria-describedby');A3D_TIP.at=null;}
  }
  function bimTipShow(target){
    var spec=target&&target.getAttribute('data-a3dtip');
    if(!spec||!document.body.contains(target))return;
    var el=A3D_TIP.el;
    if(!el){el=A3D_TIP.el=document.createElement('div');el.id='a3d-tip';el.setAttribute('role','tooltip');document.body.appendChild(el);}
    el.innerHTML=bimDockTipHtml(spec);
    el.classList.add('show');
    var r=target.getBoundingClientRect(),w=el.offsetWidth,hh=el.offsetHeight;
    var left=Math.max(8,Math.min(window.innerWidth-w-8,r.left+r.width/2-w/2)),top=r.top-hh-10;
    if(top<8)top=r.bottom+10;
    el.style.left=Math.round(left)+'px';el.style.top=Math.round(top)+'px';
    target.setAttribute('aria-describedby','a3d-tip');A3D_TIP.at=target;
  }
  /* after a short pause on hover (so a pointer passing over does not flash them), at once on focus */
  function bimBindDockTips(host){
    if(host.getAttribute('data-tips'))return;
    host.setAttribute('data-tips','1');
    host.addEventListener('mouseover',function(ev){
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-a3dtip]'):null;
      if(!tg||tg===A3D_TIP.at)return;
      bimTipHide();
      A3D_TIP.timer=setTimeout(function(){A3D_TIP.timer=null;bimTipShow(tg);},350);
    });
    host.addEventListener('mouseout',function(ev){
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-a3dtip]'):null;
      if(tg&&!(ev.relatedTarget&&tg.contains(ev.relatedTarget)))bimTipHide();
    });
    host.addEventListener('focusin',function(ev){
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-a3dtip]'):null;
      bimTipHide();if(tg&&tg.matches(':focus-visible'))bimTipShow(tg);
    });
    host.addEventListener('focusout',bimTipHide);
    host.addEventListener('pointerdown',bimTipHide,true);
    host.addEventListener('keydown',function(ev){if(ev.key==='Escape')bimTipHide();});
    window.addEventListener('scroll',bimTipHide,true);
  }
  var A3DR_SEARCH_ICON=ric(""")
rep("""    bimRenderInto(host,h+'</div>'+pops);   /* __acad3dV118: the Discipline dropdown keeps the focus */
    return true;""", """    bimRenderInto(host,h+'</div>'+pops);   /* __acad3dV118: the Discipline dropdown keeps the focus */
    bimTipHide();bimBindDockTips(host);   /* __acad3dV129 */
    return true;""")

# ---- Appearance: names or icons only
rep("""        '<button class="a3d-ruitem'+(light?' on':'')+'" data-a3druitem="appear:light">Light interface</button>';""",
    """        '<button class="a3d-ruitem'+(light?' on':'')+'" data-a3druitem="appear:light">Light interface</button>'+
        '<div class="a3d-rusep"></div>'+   /* __acad3dV129 */
        '<button class="a3d-ruitem'+(bimDockLabelsOn()?' on':'')+'" data-a3druitem="appear:docknames">Tool names on the dock</button>'+
        '<button class="a3d-ruitem'+(bimDockLabelsOn()?'':' on')+'" data-a3druitem="appear:dockicons">Icons only</button>';""")
rep("""    if(grp==='appear'){
      if(key==='technical'||key==='presentation'){""", """    if(grp==='appear'){
      if(key==='docknames'||key==='dockicons'){bimSetDockLabels(key==='docknames');}   /* __acad3dV129 */
      else if(key==='technical'||key==='presentation'){""")

# ---- the look
rep(""".a3d-dockgrp{display:flex;align-items:center;gap:1px;flex:0 0 auto}""",
    """.a3d-dockgrp{display:flex;flex-direction:column;align-items:center;gap:2px;flex:0 0 auto}
.a3d-dgtools{display:flex;align-items:center;gap:1px}
.a3d-dglbl{font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#7d8590;line-height:1;white-space:nowrap}
#a3d-dock.a3d-docklabels .a3d-dockgrp{gap:1px}
#a3d-dock.a3d-docklabels .a3d-dbtn{width:60px;height:38px;flex-direction:column;gap:2px}
#a3d-dock.a3d-docklabels .a3d-dbtn svg{width:16px;height:16px}
#a3d-dock.a3d-docklabels .a3d-dcar{width:40px;height:38px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#aab2bd}
#a3d-dock.a3d-docklabels .a3d-dcar svg{width:16px;height:16px}
.a3d-dblbl{font-size:10px;line-height:1.1;color:#aab2bd;max-width:58px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.a3d-dbtn:hover .a3d-dblbl,.a3d-dcar:hover .a3d-dblbl{color:#fff}
.a3d-dsearchpill{display:flex;align-items:center;gap:7px;flex:1 1 auto;min-width:210px;height:24px;padding:0 9px;background:#1c2024;border:1px solid #3a4048;border-radius:6px;color:#8b949e;font:inherit;font-size:11.5px;cursor:pointer;text-align:left}
.a3d-dsearchpill:hover{border-color:#4ea1ff;color:#dfe4ea}
.a3d-dsearchpill svg{width:14px;height:14px;flex:0 0 auto}
.a3d-dsearchpill span{flex:1 1 auto}
.a3d-dsearchpill kbd{font:600 10px/1 Inter,system-ui,sans-serif;padding:2px 5px;border:1px solid #4a525c;border-radius:4px;color:#c7ced6}
.a3d-dockhead .a3d-dockgrp{flex-direction:row;gap:6px;width:100%}
.a3d-dbtn:focus-visible,.a3d-dcar:focus-visible,.a3d-dsearchpill:focus-visible{outline:2px solid #4ea1ff;outline-offset:1px}
#a3d-tip{position:fixed;z-index:10050;display:none;max-width:260px;background:#0f1114;border:1px solid #3f4650;border-radius:8px;padding:8px 10px;box-shadow:0 8px 22px rgba(0,0,0,.5);font:12px/1.4 Inter,system-ui,sans-serif;color:#aab2bd;pointer-events:none}
#a3d-tip.show{display:block}
.a3d-tiphd{display:flex;align-items:center;justify-content:space-between;gap:12px}
.a3d-tiphd strong{font-size:13px;color:#fff;font-weight:600}
.a3d-tipkeys{display:flex;align-items:center;gap:3px}.a3d-tipkeys i{font-style:normal;color:#6e7781;font-size:10px}
.a3d-tipkeys kbd{font:600 10.5px/1 Inter,system-ui,sans-serif;padding:2px 5px;border:1px solid #56606b;border-radius:4px;color:#e6eaef}
.a3d-tiptype{margin-top:4px}.a3d-tiptype b{font-family:ui-monospace,Menlo,monospace;color:#8fb8ff;font-weight:600}
.a3d-tipdesc{margin-top:2px}.a3d-tipdesc.off{color:#e8a87c}
.a3d-tipwhere{margin-top:3px;font-size:11px;color:#7d8590}
body.light-theme #a3d-tip{background:#fff;border-color:#c9ced4;color:#40464d;box-shadow:0 8px 22px rgba(0,0,0,.15)}
body.light-theme #a3d-tip strong{color:#202124}body.light-theme .a3d-tiptype b{color:#1f5fbf}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
