"""patch_phase158b.py -- V158: Analysis and Data are layers in the tree, as Context is.

The owner: "analysis and datalayer ... should be part of layer management. just like how context
layer is". V148 put them below the layers as two sections, headed in small bold type behind a rule.
Now each heads its group as a layer row does: the caret, a swatch, its name and count, and an eye
that shows or hides everything in it, one undo step; its layers sit under it, their eyes in the
layers' eye column."""
NAME = 'patch_phase158b.py'
BASE = '3125c05cf369884c4cfdca5155e881891d6c233998dd80b8889001e9697a968c'
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


rep(""".a3d-lysec{margin:2px 0 0;border-top:1px solid rgba(255,255,255,.07);padding-top:4px}
.a3d-lysechd{display:flex;align-items:center;gap:3px;height:28px;padding:0 4px 0 4px}
.a3d-lysecttl{flex:1 1 auto;font-size:11px;font-weight:600;color:#aeb8c2}""",
    """.a3d-lysec{margin:0;padding:0}   /* __acad3dV158: a layer group in the tree, as Context is */
.a3d-lysechd{display:flex;align-items:center;gap:3px;height:26px;padding:0 2px 0 4px;border-radius:6px;user-select:none}
.a3d-lysechd:hover{background:rgba(255,255,255,.06)}
.a3d-lysecttl{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.a3d-lysec.dim .a3d-lysecttl{color:#6e7781}
.a3d-lygsw{width:14px;height:14px;flex:0 0 14px;border-radius:3px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.25)}
.a3d-lyspc{visibility:hidden;pointer-events:none}
.a3d-lylist+.a3d-lysec{margin-top:-20px}   /* right under the layers, over most of the list's drop room */
.a3d-lyres .a3d-lyspc,.a3d-lyres .a3d-lyspc+.a3d-lyspc{margin-left:-3px}   /* its wider gap: the eye in the layers' eye column */""")
rep("""body.light-theme .a3d-lysec{border-color:rgba(0,0,0,.08)}
body.light-theme .a3d-lysecttl{color:#555}""",
    """body.light-theme .a3d-lysechd:hover{background:rgba(0,0,0,.05)}""")

SP = "'<span class=\"a3d-lyi a3d-lyspc\" aria-hidden=\"true\"></span><span class=\"a3d-lyi a3d-lyspc\" aria-hidden=\"true\"></span>'"
rep("""      bimLyTgl('lyreson',key,hid,hid?'Show '+R.name:'Hide '+R.name,BIM_LY_IC.off,BIM_LY_IC.on)+'</div>';
    if(sel)h+='<div class="a3d-lyresd" data-lyresd="'+bimEsc(key)+'">'+bimLyOpacityHtml(key,R.name,bimResOpacity(R))+bimResLegendHtml(R)+""",
    """      bimLyTgl('lyreson',key,hid,hid?'Show '+R.name:'Hide '+R.name,BIM_LY_IC.off,BIM_LY_IC.on)+""" + SP + """+'</div>';   /* __acad3dV158: in the eye column */
    if(sel)h+='<div class="a3d-lyresd" data-lyresd="'+bimEsc(key)+'">'+bimLyOpacityHtml(key,R.name,bimResOpacity(R))+bimResLegendHtml(R)+""")
rep("""      bimLyTgl('lyreson',key,hid,hid?'Show '+L.name:'Hide '+L.name,BIM_LY_IC.off,BIM_LY_IC.on)+'</div>';
    if(sel)h+='<div class="a3d-lyresd" data-lyresd="'+bimEsc(key)+'">'+bimLyOpacityHtml(key,L.name,bimDataOpacity(L))+""",
    """      bimLyTgl('lyreson',key,hid,hid?'Show '+L.name:'Hide '+L.name,BIM_LY_IC.off,BIM_LY_IC.on)+""" + SP + """+'</div>';
    if(sel)h+='<div class="a3d-lyresd" data-lyresd="'+bimEsc(key)+'">'+bimLyOpacityHtml(key,L.name,bimDataOpacity(L))+""")
rep("""    function sec(key,label,n,body,empty){
      if(f&&!body)return '';
      var open=!!f||!shut[key];
      return '<div class="a3d-lysec" data-lysec="'+key+'"><div class="a3d-lysechd"><button type="button" class="a3d-lycar" data-lysectog="'+key+'" aria-expanded="'+open+'" title="'+
        (open?'Close ':'Open ')+label+'" aria-label="'+(open?'Close ':'Open ')+label+'">'+(open?BIM_LY_IC.open:BIM_LY_IC.closed)+'</button>'+
        '<span class="a3d-lysecttl">'+label+'</span><span class="a3d-lycnt">'+(n||'')+'</span></div>'+
        (open?(body||'<div class="a3d-lyempty a3d-lyhint">'+empty+'</div>'):'')+'</div>';
    }""",
    """    /* __acad3dV158: the group's row, a layer row's columns: caret, status, swatch, name, count, eye */
    function sec(key,label,n,body,empty){
      if(f&&!body)return '';
      var open=!!f||!shut[key],off=bimLySecHidden(key),sw=key==='analysis'?'linear-gradient(135deg,#f6c445,#e0603b 55%,#2f7fe0)':'#7f9db8';
      return '<div class="a3d-lysec'+(off?' dim':'')+'" data-lysec="'+key+'"><div class="a3d-lysechd"><button type="button" class="a3d-lycar" data-lysectog="'+key+'" aria-expanded="'+open+'" title="'+
        (open?'Close ':'Open ')+label+'" aria-label="'+(open?'Close ':'Open ')+label+'">'+(open?BIM_LY_IC.open:BIM_LY_IC.closed)+'</button>'+
        '<span class="a3d-lystat" aria-hidden="true"></span><span class="a3d-lygsw" style="background:'+sw+'"></span>'+
        '<span class="a3d-lynm a3d-lysecttl">'+label+'</span><span class="a3d-lycnt">'+(n||'')+'</span>'+
        bimLyTgl('lysecon',key,off,(off?'Show ':'Hide ')+'everything in '+label,BIM_LY_IC.off,BIM_LY_IC.on)+""" + SP + """+'</div>'+
        (open?(body||'<div class="a3d-lyempty a3d-lyhint">'+empty+'</div>'):'')+'</div>';
    }""")
rep("""  /* ---- a row's actions, either section ---- */""",
    """  /* __acad3dV158: a group is hidden when it holds layers and none of them shows */
  function bimLySecItems(key){return key==='analysis'?bimResLayers():key==='data'?bimDataList():null;}
  function bimLySecHidden(key){
    var L=bimLySecItems(key)||[],i;
    if(!L.length)return false;
    for(i=0;i<L.length;i++)if(key==='analysis'?L[i].visible!==false:!!L[i].visible)return false;
    return true;
  }
  /* the group's eye: everything in it shown, or hidden, in one undo step */
  function bimLySecVisible(key,v){
    var L=bimLySecItems(key),i;
    if(!L)return null;
    if(!L.length){a3dToast('Nothing in '+(key==='analysis'?'Analysis':'Data')+' yet');return null;}
    if(v===undefined)v=bimLySecHidden(key);
    v=!!v;
    pushUndo();
    for(i=0;i<L.length;i++){
      L[i].visible=v;
      if(key==='data'&&!v&&A3D_DATA.sel&&A3D_DATA.sel.layer===L[i].id)A3D_DATA.sel=null;
    }
    refreshLayers();refreshProps();paint();saveSoon();
    return v;
  }
  /* ---- a row's actions, either section ---- */""")
rep("""    if((b=t.closest('[data-lyreson]'))){bimLyResVisible(b.getAttribute('data-lyreson'));return true;}""",
    """    if((b=t.closest('[data-lysecon]'))){bimLySecVisible(b.getAttribute('data-lysecon'));return true;}   /* __acad3dV158 */
    if((b=t.closest('[data-lyreson]'))){bimLyResVisible(b.getAttribute('data-lyreson'));return true;}""")
rep("""  window.__a3dSaSlope=function(tin){return bimSaSlope(tin);};""",
    """  window.__a3dSaSlope=function(tin){return bimSaSlope(tin);};
  window.__a3dLySecVisible=function(key,v){return bimLySecVisible(key,v);};
  window.__a3dLySecHidden=function(key){return bimLySecHidden(key);};""")
rep("""  window.__acad3dV158='stages,""", """  window.__acad3dV158='layergroups,stages,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
