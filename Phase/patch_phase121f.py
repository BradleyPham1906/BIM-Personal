"""patch_phase121f.py -- V121: the Layer Properties Manager, LAYER and LA.

The owner: "i should be able to manipulate a table like how autocad do like linetype, color,
hide/show, layer, sub layer, transparency". The Layers panel is a tree, and a 296 px panel holds
three switches per row; the table is AutoCAD's Layer Properties Manager, the column set its help
describes -- Status, Name, On, Freeze, Lock, Plot, Color, Linetype, Lineweight, Transparency -- with
the object count and Description beside them, the layers in tree order and sub-layers indented.

LAYER, LA and LAYERS open it from the command line and the palette (the command table has listed
LAYER since V86, as 'Layers panel', and nothing ran it: the engine had no 'layers' command), on a
sheet as well as in the model, as AutoCAD's does; the Layers panel's header opens it too.

Every cell goes through V121b's rules, and after every edit the table is drawn again from the
layers, so a refused change -- a frozen current layer, a name already taken, a transparency of 95 --
cannot go on showing what was refused. New layer, New sub-layer, Delete and Set current act on the
row picked; the search narrows the rows to the layers whose names match, with their parents."""
NAME = 'patch_phase121f.py'
BASE = 'fb2f189d392dd38acf1981c7025b9317337df9884a2b7f8953dca5d72e8e0a5e'
import re
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
# ---- 1. the manager
rep("    panel.addEventListener('dragend',function(){A3D_LY.drag=null;});\n  }\n",
    r"""    panel.addEventListener('dragend',function(){A3D_LY.drag=null;});
  }
  /* ================= __acad3dV121: the Layer Properties Manager (LAYER, LA) =================
     AutoCAD's table: Status, Name, On, Freeze, Lock, Plot, Color, Linetype, Lineweight,
     Transparency -- with the object count and Description -- in tree order, sub-layers indented.
     Every cell goes through V121b's rules, and after every edit the table is drawn again from the
     layers, so a refused change cannot go on showing what was refused. The picked row (A3D_LPM.sel)
     is what New sub-layer, Delete and Set current act on; neither it nor the search is saved. */
  var A3D_LPM={sel:null,filter:''};
  var BIM_LPM_IC={
    plot:ric('<path d="M7 9V4h10v5"/><rect x="4" y="9" width="16" height="7" rx="1.5"/><path d="M7 14h10v6H7z"/>'),
    noplot:ric('<path d="M7 9V4h10v5"/><rect x="4" y="9" width="16" height="7" rx="1.5"/><path d="M7 14h10v6H7z"/><path d="M3 3l18 18"/>'),
    close:ric('<path d="M6 6l12 12M18 6 6 18"/>')
  };
  function bimLpmOpen(){return !!(el.dlg&&el.dlg.parentNode&&el.dlg.classList.contains('a3d-lpm'));}
  function bimLpmLwText(v){return (v===null||v===undefined||!isFinite(v))?'Default':(+v).toFixed(2)+' mm';}
  /* a switch shows the state that is not the default -- off, frozen, locked, not plotted -- lit */
  function bimLpmTgl(field,lit,titleLit,titleNot,icLit,icNot){
    var tt=bimEsc(lit?titleLit:titleNot);
    return '<button type="button" class="a3d-lyi'+(lit?' on':'')+'" data-lpmtgl="'+field+'" title="'+tt+'" aria-label="'+tt+
      '" aria-pressed="'+(lit?'true':'false')+'">'+(lit?icLit:icNot)+'</button>';
  }
  function bimLpmBtn(a,label,ic){
    return '<button type="button" class="a3d-lpmbtn" data-lpmact="'+a+'" title="'+bimEsc(label)+'">'+ic+'<span>'+bimEsc(label)+'</span></button>';
  }
  function bimLpmTableHtml(){
    var con=bimLayerContents(),f=String(A3D_LPM.filter||'').toLowerCase(),cur=A3D.activeLayer,tree=bimLayerTree();
    var sel=bimLayerById(A3D_LPM.sel)?A3D_LPM.sel:cur,keep={},rows='',shown=0;
    /* a match brings its parents with it, so a sub-layer is never listed without its place */
    if(f)tree.forEach(function(t){
      if(String(t.ly.name).toLowerCase().indexOf(f)>=0)bimLayerChain(t.ly).forEach(function(a){keep[a.id]=1;});
    });
    tree.forEach(function(t){
      var l=t.ly;
      if(f&&!keep[l.id])return;
      shown++;
      var id=bimEsc(l.id),nm=bimEsc(l.name),isCur=(l.id===cur),s=bimLayerEff(l),k;
      var lt=(bimLinetypeDef(l.linetype)||BIM_LINETYPES[0]).name;
      var lw=(l.lineweight===undefined||l.lineweight===null||!isFinite(l.lineweight))?null:+l.lineweight;
      var tr=isFinite(l.transparency)?+l.transparency:0;
      var col=/^#[0-9a-fA-F]{6}$/.test(l.color||'')?l.color.toLowerCase():'#7f9db8';
      var lto='',lwo='<option value=""'+(lw===null?' selected':'')+'>Default</option>';
      for(k=0;k<BIM_LINETYPES.length;k++)
        lto+='<option value="'+BIM_LINETYPES[k].name+'" title="'+bimEsc(BIM_LINETYPES[k].desc)+'"'+(BIM_LINETYPES[k].name===lt?' selected':'')+'>'+BIM_LINETYPES[k].name+'</option>';
      for(k=0;k<BIM_LINEWEIGHTS.length;k++)
        lwo+='<option value="'+BIM_LINEWEIGHTS[k]+'"'+(BIM_LINEWEIGHTS[k]===lw?' selected':'')+'>'+bimLpmLwText(BIM_LINEWEIGHTS[k])+'</option>';
      rows+='<tr class="a3d-lpmrow'+(l.id===sel?' sel':'')+(isCur?' cur':'')+((!s.on||s.frozen)?' dim':'')+'" data-lpmid="'+id+'">'+
        '<td><button type="button" class="a3d-lystat'+(isCur?' on':'')+'" data-lpmcur="'+id+'" title="'+(isCur?nm+' is the current layer':'Make '+nm+' current')+
          '" aria-label="'+(isCur?nm+' is the current layer':'Make '+nm+' current')+'" aria-pressed="'+(isCur?'true':'false')+'">'+(isCur?BIM_LY_IC.cur:BIM_LY_IC.notcur)+'</button></td>'+
        '<td class="a3d-lpmname"><input type="text" data-lpmf="name" value="'+nm+'" style="margin-left:'+(t.depth*16)+'px" aria-label="Name of '+nm+'"></td>'+
        '<td>'+bimLpmTgl('visible',l.visible===false,'Turn '+nm+' on','Turn '+nm+' off',BIM_LY_IC.off,BIM_LY_IC.on)+'</td>'+
        '<td>'+bimLpmTgl('frozen',!!l.frozen,'Thaw '+nm,'Freeze '+nm,BIM_LY_IC.frozen,BIM_LY_IC.thawed)+'</td>'+
        '<td>'+bimLpmTgl('locked',!!l.locked,'Unlock '+nm,'Lock '+nm,BIM_LY_IC.locked,BIM_LY_IC.unlocked)+'</td>'+
        '<td>'+bimLpmTgl('plot',l.plot===false,'Plot '+nm,'Do not plot '+nm,BIM_LPM_IC.noplot,BIM_LPM_IC.plot)+'</td>'+
        '<td><input type="color" class="a3d-lysw" data-lpmf="color" value="'+col+'" aria-label="Color of '+nm+'"><span class="a3d-lpmhex">'+col+'</span></td>'+
        '<td><select data-lpmf="linetype" aria-label="Linetype of '+nm+'">'+lto+'</select></td>'+
        '<td><select data-lpmf="lineweight" aria-label="Lineweight of '+nm+'">'+lwo+'</select></td>'+
        '<td><input type="number" min="0" max="90" step="1" data-lpmf="transparency" value="'+tr+'" aria-label="Transparency of '+nm+'"></td>'+
        '<td class="a3d-lpmcnt">'+(con[l.id]||[]).length+'</td>'+
        '<td class="a3d-lpmdesc"><input type="text" data-lpmf="description" value="'+bimEsc(typeof l.description==='string'?l.description:'')+'" aria-label="Description of '+nm+'"></td>'+
        '</tr>';
    });
    return '<table class="a3d-lpmt"><thead><tr><th title="The current layer">Status</th><th>Name</th><th>On</th><th>Freeze</th><th>Lock</th><th>Plot</th>'+
      '<th>Color</th><th>Linetype</th><th>Lineweight</th><th>Transparency</th><th>Objects</th><th>Description</th></tr></thead><tbody>'+rows+
      '</tbody></table>'+(shown?'':'<div class="a3d-lyempty">No layer matches</div>');
  }
  function bimLayerManagerRefresh(){
    if(!bimLpmOpen())return;
    var body=el.dlg.querySelector('.a3d-lpmbody'),ft=el.dlg.querySelector('.a3d-lpmft'),cur=bimLayerById(A3D.activeLayer);
    bimRenderInto(body,bimLpmTableHtml());
    if(ft)ft.textContent=A3D.layers.length+' layer'+(A3D.layers.length===1?'':'s')+'. Current layer: '+(cur?cur.name:'none')+'.';
  }
  function bimLpmFocusName(id){
    var r=el.dlg?el.dlg.querySelector('[data-lpmid="'+String(id).replace(/"/g,'')+'"] [data-lpmf="name"]'):null;
    if(r){try{r.focus();r.select();}catch(eF){console.warn('[BIM] The layer name field could not take the focus',eF);}}
  }
  function bimLpmAct(a){
    var sel=bimLayerById(A3D_LPM.sel)||bimLayerById(A3D.activeLayer),n;
    if(a==='close'){closeDlg();return;}
    if(a==='new'){
      n=bimLayerNew({from:sel?sel.id:null});
      if(n){A3D_LPM.sel=n.id;bimLayerManagerRefresh();bimLpmFocusName(n.id);}
    }else if(a==='sub'){
      if(!sel)return;
      n=bimLayerNew({parent:sel.id});
      if(n){A3D_LY.open[sel.id]=true;A3D_LPM.sel=n.id;bimLayerManagerRefresh();bimLpmFocusName(n.id);}
    }else if(a==='del'){
      if(sel&&bimLayerDelete(sel.id))A3D_LPM.sel=A3D.activeLayer;
      bimLayerManagerRefresh();
    }else if(a==='cur'){
      if(sel)bimLayerMakeCurrent(sel.id);
      bimLayerManagerRefresh();
    }
  }
  function bimWireLayerManager(d){
    function rowOf(t){var r=(t&&t.closest)?t.closest('[data-lpmid]'):null;return r?bimLayerById(r.getAttribute('data-lpmid')):null;}
    d.addEventListener('click',function(ev){
      var t=ev.target,b,l,f;
      try{
        if((b=t.closest('[data-lpmact]'))){bimLpmAct(b.getAttribute('data-lpmact'));return;}
        if((b=t.closest('[data-lpmcur]'))){if(bimLayerMakeCurrent(b.getAttribute('data-lpmcur')))A3D_LPM.sel=A3D.activeLayer;bimLayerManagerRefresh();return;}
        if((b=t.closest('[data-lpmtgl]'))){
          l=rowOf(b);
          if(!l)return;
          f=b.getAttribute('data-lpmtgl');
          bimLayerSet(l.id,f,(f==='visible'||f==='plot')?(l[f]===false):!l[f]);
          bimLayerManagerRefresh();
          return;
        }
        if(t.closest('input,select'))return;
        l=rowOf(t);
        if(l){A3D_LPM.sel=l.id;bimLayerManagerRefresh();}
      }catch(eC){
        console.warn('[BIM] A Layer Properties Manager action failed',eC);
        a3dToast('That layer change could not be made');
      }
    });
    d.addEventListener('change',function(ev){
      var t=ev.target,f=(t&&t.getAttribute)?t.getAttribute('data-lpmf'):null,l=rowOf(t);
      if(!f||!l)return;
      try{bimLayerSet(l.id,f,t.value);}
      catch(eF){console.warn('[BIM] A layer field could not be set',eF);a3dToast('That layer change could not be made');}
      bimLayerManagerRefresh();
    });
    d.addEventListener('input',function(ev){
      var t=ev.target;
      if(t&&t.hasAttribute&&t.hasAttribute('data-lpmsearch')){A3D_LPM.filter=t.value;bimLayerManagerRefresh();}
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
  }
  function bimLayerManagerOpen(){
    try{
      closeDlg();
      var d=document.createElement('div');
      d.className='a3d-dlg a3d-lpm';
      d.setAttribute('role','dialog');
      d.setAttribute('aria-label','Layer Properties Manager');
      d.innerHTML='<div class="a3d-dlghd a3d-lpmhd"><span>Layer Properties Manager</span>'+
        '<button type="button" class="a3d-lpmx" data-lpmact="close" title="Close" aria-label="Close">'+BIM_LPM_IC.close+'</button></div>'+
        '<div class="a3d-lpmtb">'+
          bimLpmBtn('new','New layer',BIM_LY_IC.add)+
          bimLpmBtn('sub','New sub-layer',BIM_LY_IC.sub)+
          bimLpmBtn('del','Delete',BIM_LY_IC.del)+
          bimLpmBtn('cur','Set current',BIM_LY_IC.make)+
          '<input type="text" class="a3d-lysearch" data-lpmsearch="1" placeholder="Search for layer" aria-label="Search for layer" value="'+bimEsc(A3D_LPM.filter||'')+'">'+
        '</div><div class="a3d-lpmbody"></div><div class="a3d-lpmft"></div>';
      el.root.appendChild(d);
      el.dlg=d;
      bimWireLayerManager(d);
      bimLayerManagerRefresh();
      return true;
    }catch(eM){
      console.warn('[BIM] The Layer Properties Manager could not open',eM);
      a3dToast('The Layer Properties Manager could not open');
      return false;
    }
  }
""")

# ---- 2. every view of the layers includes the manager
rep("  function refreshLayers(){\n    bimLayersPanelRefresh();\n  }\n",
    "  function refreshLayers(){\n    bimLayersPanelRefresh();\n    bimLayerManagerRefresh();   /* __acad3dV121 */\n  }\n")

# ---- 3. the Layers panel's header opens it
rep("    del:ric('<path d=\"M4.5 7h15M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13\"/>'),\n",
    "    del:ric('<path d=\"M4.5 7h15M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13\"/>'),\n"
    "    lpm:ric('<rect x=\"3.5\" y=\"5\" width=\"17\" height=\"14\" rx=\"1.5\"/><path d=\"M3.5 9.5h17M9 9.5V19M14.5 9.5V19\"/>'),   /* __acad3dV121 */\n")
rep("      bimLyBtn('del','Delete the selected layer',BIM_LY_IC.del)+\n",
    "      bimLyBtn('del','Delete the selected layer',BIM_LY_IC.del)+\n"
    "      bimLyBtn('lpm','Layer Properties Manager (LAYER)',BIM_LY_IC.lpm)+\n")
rep("    }else if(a==='del'){\n      if(sel&&bimLayerDelete(sel.id)){A3D_LY.sel=A3D.activeLayer;refreshLayers();}\n    }\n",
    "    }else if(a==='del'){\n      if(sel&&bimLayerDelete(sel.id)){A3D_LY.sel=A3D.activeLayer;refreshLayers();}\n"
    "    }else if(a==='lpm'){\n      bimLayerManagerOpen();\n    }\n")

# ---- 4. LAYER, LA and LAYERS run it, in the model and on a sheet
rep("    ['LAYER',['LA','LAYERS'],'layers','Layers panel'],",
    "    ['LAYER',['LA','LAYERS'],'layers','Layer Properties Manager'],")
rep("    zoomFit:function(){fitScene();},\n",
    "    zoomFit:function(){fitScene();},\n"
    "    layers:function(){bimLayerManagerOpen();},   /* __acad3dV121: LAYER, listed since V86 and never run */\n")
rep("    newSheet:1,modelTab:1,mspace:1,pspace:1,shortcuts:1};",
    "    newSheet:1,modelTab:1,mspace:1,pspace:1,shortcuts:1,layers:1};   /* __acad3dV121: LAYER works on a sheet, as AutoCAD's does */")

# ---- 5. its stylesheet
after_line(".a3d-lyempty{padding:8px;color:#6e7781}", r"""/* __acad3dV121: the Layer Properties Manager */
.a3d-dlg.a3d-lpm{width:min(1060px,95vw);max-height:78vh;display:flex;flex-direction:column;overflow:hidden}
.a3d-lpmhd{display:flex;align-items:center;justify-content:space-between}
.a3d-lpmx{width:24px;height:24px;border:0;border-radius:6px;background:transparent;color:#9aa3ad;display:grid;place-items:center;cursor:pointer;padding:0}
.a3d-lpmx:hover{background:rgba(255,255,255,.1);color:#fff}
.a3d-lpmx svg{width:14px;height:14px}
.a3d-lpmtb{display:flex;align-items:center;gap:6px;padding:7px 10px;border-bottom:1px solid #30353c}
.a3d-lpmtb .a3d-lysearch{margin:0 0 0 auto;width:210px}
.a3d-lpmbtn{display:inline-flex;align-items:center;gap:5px;height:26px;padding:0 9px 0 6px;border:1px solid #3a4048;border-radius:6px;background:#2a2f35;color:#dfe4ea;font:12px Inter,system-ui,sans-serif;cursor:pointer}
.a3d-lpmbtn:hover{background:#343a41}
.a3d-lpmbtn svg{width:14px;height:14px}
.a3d-lpmbody{overflow:auto;flex:1 1 auto;min-height:0}
.a3d-lpmt{border-collapse:collapse;width:100%;font:12px/1.3 Inter,system-ui,sans-serif;color:#c9d1d9}
.a3d-lpmt th{position:sticky;top:0;z-index:1;background:#23272c;color:#8b949e;font-size:10.5px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;text-align:left;padding:6px;border-bottom:1px solid #30353c;white-space:nowrap}
.a3d-lpmt td{padding:3px 6px;border-bottom:1px solid #2a2f35;white-space:nowrap;vertical-align:middle}
.a3d-lpmrow:hover td{background:rgba(255,255,255,.04)}
.a3d-lpmrow.sel td{background:rgba(78,161,255,.16)}
.a3d-lpmrow.dim .a3d-lpmname input{color:#6e7781}
.a3d-lpmrow.cur .a3d-lpmname input{font-weight:600;color:#fff}
.a3d-lpmt input,.a3d-lpmt select{background:transparent;border:1px solid transparent;border-radius:4px;color:#dfe4ea;padding:3px 5px;font:inherit}
.a3d-lpmt input:hover,.a3d-lpmt select:hover{border-color:#3a4048}
.a3d-lpmt input:focus,.a3d-lpmt select:focus{border-color:#4ea1ff;background:#1c2024;outline:0}
.a3d-lpmt select{background:#1c2024}
.a3d-lpmt .a3d-lysw{padding:0;border:1px solid rgba(255,255,255,.25);vertical-align:middle}
.a3d-lpmname input{width:170px}
.a3d-lpmt input[type=number]{width:58px}
.a3d-lpmdesc input{width:170px}
.a3d-lpmcnt{color:#8b949e;text-align:right}
.a3d-lpmhex{margin-left:6px;color:#8b949e;font-size:11px}
.a3d-lpmft{padding:6px 12px;border-top:1px solid #30353c;color:#8b949e;font-size:11px}
""")

# ---- the command is real now, and every function of the manager is reached
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
if not re.search(r"\n    layers:function\(\)\{bimLayerManagerOpen\(\);\}", code):
    sys.exit('ABORT: LAYER still runs nothing')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
