#!/usr/bin/env python3
"""V170b: Play, Pause and Stop in the status bar, beside the view's own buttons (nothing floats over the drawing,
V109); the clock's loop; the PLAY command; and Motion, an element's style in Properties.

Run from the repository root: python3 Phase/patch_phase170b.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '86ea7667a575fea367ed372c73f3123df545c28869a83358bcca87a725e2732d'   # V170a

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


# ---- the clock ----
CLOCK = r'''  /* Play from still starts the clock at nothing, the layers coming in one after another; Play after Pause goes on
     from the moment kept */
  function bimAnimCan(){A3D_ANIM.fr=null;return bimAnimFrame().any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk());}
  function bimAnimPlay(on){
    if(on===undefined||on===null)on=!A3D_ANIM.on;
    on=!!on;
    if(on===A3D_ANIM.on)return true;
    if(on&&!bimAnimCan()){a3dToast('Nothing to play: show a site analysis layer, or the sun study in plan');return false;}
    A3D_ANIM.on=on;
    if(on){
      if(!A3D_ANIM.paused){A3D_ANIM.t=0;A3D_ANIM.playAt=0;}
      A3D_ANIM.paused=false;A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();
      bimAnimWire();A3D_ANIM.last=0;A3D_ANIM.painted=0;bimAnimRun();
    }else{A3D_ANIM.paused=true;bimAnimHalt();}
    paint();
    return true;
  }
  function bimAnimStop(){
    var was=A3D_ANIM.on||A3D_ANIM.paused;
    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;
    bimAnimHalt();
    if(was)paint();
    return was;
  }
  function bimAnimRun(){if(!A3D_ANIM.raf&&A3D_ANIM.on&&!document.hidden)A3D_ANIM.raf=requestAnimationFrame(bimAnimTick);}
  function bimAnimHalt(){if(A3D_ANIM.raf){cancelAnimationFrame(A3D_ANIM.raf);A3D_ANIM.raf=0;}A3D_ANIM.last=0;}
  function bimAnimTick(ts){
    A3D_ANIM.raf=0;
    if(!A3D_ANIM.on||!A3D.on)return;
    if(A3D_ANIM.last)A3D_ANIM.t+=Math.min(0.1,Math.max(0,(ts-A3D_ANIM.last)/1000));   /* a slow frame moves it a tenth of a second at most, never a jump */
    A3D_ANIM.last=ts;
    if(!A3D_ANIM.painted||ts-A3D_ANIM.painted>=1000/BIM_ANIM.fps-2){
      A3D_ANIM.painted=ts;A3D_ANIM.sunTime=bimAnimSunTime();
      try{paint();A3D_ANIM.frames++;}
      catch(eA){console.warn('[BIM] A frame of the motion could not be drawn',eA);bimAnimPlay(false);a3dToast('The motion was paused: a frame could not be drawn - see the console');return;}
      if(!A3D_ANIM.on)return;
    }
    bimAnimRun();
  }
  /* the page hidden: the clock waits; the device asking for reduced motion while it plays: paused */
  function bimAnimWire(){
    if(A3D_ANIM.wired)return;
    A3D_ANIM.wired=true;
    document.addEventListener('visibilitychange',function(){if(document.hidden)bimAnimHalt();else bimAnimRun();});
    try{
      var mq=window.matchMedia?window.matchMedia('(prefers-reduced-motion: reduce)'):null,f;
      if(mq){
        f=function(){if(mq.matches&&A3D_ANIM.on){bimAnimPlay(false);a3dToast('Paused: the device asks for reduced motion');}};
        if(mq.addEventListener)mq.addEventListener('change',f);else if(mq.addListener)mq.addListener(f);
      }
    }catch(eM){console.warn('[BIM] The reduced-motion setting could not be followed',eM);}
  }
  /* Play and Pause shown whenever something can move, Stop while it is not still; nothing left to move, still */
  function bimAnimSync(){
    var F=bimAnimFrame(),can=F.any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk()),moving=A3D_ANIM.on||A3D_ANIM.paused,g,b,x,key;
    A3D_ANIM.can=can;
    if(!can&&moving){A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;bimAnimHalt();moving=false;}
    g=document.getElementById('a3d-animgrp');b=document.getElementById('a3d-animplay');x=document.getElementById('a3d-animstop');
    if(!g||!b)return;
    key=(can?1:0)+':'+(A3D_ANIM.on?1:0)+':'+(moving?1:0);
    if(key!==A3D_ANIM.key){
      A3D_ANIM.key=key;
      g.hidden=!can;
      b.innerHTML=(A3D_ANIM.on?PILL_PAUSE:PILL_PLAY)+'<span>'+(A3D_ANIM.on?'PAUSE':'PLAY')+'</span>';
      b.setAttribute('aria-pressed',A3D_ANIM.on?'true':'false');
      b.classList.toggle('on',!!A3D_ANIM.on);
      if(x)x.hidden=!moving;
    }
    var tt=A3D_ANIM.on?'Pause, keeping this moment'+(A3D_ANIM.sunTime?' (the sun at '+A3D_ANIM.sunTime+')':''):
      (A3D_ANIM.paused?'Play on from this moment':'Play the site analysis in motion: marching dashes, winds drawn on, rings growing, the layers in turn, the sun through the day');
    if(b.title!==tt)b.title=tt;
  }
'''
rep("  /* what is under the pointer: a line, a dot, a label or a symbol of a diagram, drawn over the\n",
    CLOCK + "  /* what is under the pointer: a line, a dot, a label or a symbol of a diagram, drawn over the\n")
rep("    A3D.frames++;\n  }\n",
    "    if(!capMode)bimAnimSync();   /* __acad3dV170: Play and Pause, shown when something can move */\n    A3D.frames++;\n  }\n")

# ---- the buttons ----
rep("  var PILL_GRID=", "  var PILL_PLAY='<svg width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"currentColor\"><path d=\"M7 4.5v15l12.5-7.5z\"/></svg>';   /* __acad3dV170 */\n"
    "  var PILL_PAUSE='<svg width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"currentColor\"><rect x=\"6\" y=\"4.5\" width=\"4.2\" height=\"15\" rx=\"0.8\"/><rect x=\"13.8\" y=\"4.5\" width=\"4.2\" height=\"15\" rx=\"0.8\"/></svg>';\n"
    "  var PILL_STOP='<svg width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"currentColor\"><rect x=\"5.5\" y=\"5.5\" width=\"13\" height=\"13\" rx=\"1.2\"/></svg>';\n"
    "  var PILL_GRID=")
rep("""        '<button class="a3d-stbtn a3d-stview" id="a3d-present" data-a3dnav="present" title="Toggle Presentation appearance (graphic overrides from Phase 51)">Tech</button>'+
      '</span>'+
""", """        '<button class="a3d-stbtn a3d-stview" id="a3d-present" data-a3dnav="present" title="Toggle Presentation appearance (graphic overrides from Phase 51)">Tech</button>'+
      '</span>'+
      '<span id="a3d-animgrp" hidden>'+   /* __acad3dV170: the site analysis in motion */
        '<button class="a3d-stbtn" id="a3d-animplay" data-a3danim="play" aria-pressed="false" title="Play the site analysis in motion">'+PILL_PLAY+'<span>PLAY</span></button>'+
        '<button class="a3d-stbtn" id="a3d-animstop" data-a3danim="stop" title="Stop: the still drawing" hidden>'+PILL_STOP+'<span>STOP</span></button>'+
      '</span>'+
""")
rep("#a3d-navgrp{display:flex;gap:4px;margin-left:6px;padding-left:8px;border-left:1px solid #3a4048}/* __acad3dV109 */\n",
    "#a3d-navgrp{display:flex;gap:4px;margin-left:6px;padding-left:8px;border-left:1px solid #3a4048}/* __acad3dV109 */\n"
    "#a3d-animgrp{display:flex;gap:4px;margin-left:6px;padding-left:8px;border-left:1px solid #3a4048}#a3d-animgrp[hidden],#a3d-animgrp [hidden]{display:none}#a3d-animgrp .a3d-stbtn *{pointer-events:none}/* __acad3dV170 */\n")
rep("#a3d-statusbar.a3d-onsheet .a3d-stlvl,#a3d-statusbar.a3d-onsheet #a3d-stcoords,#a3d-statusbar.a3d-onsheet #a3d-snapgrp,#a3d-statusbar.a3d-onsheet #a3d-navgrp{display:none}",
    "#a3d-statusbar.a3d-onsheet .a3d-stlvl,#a3d-statusbar.a3d-onsheet #a3d-stcoords,#a3d-statusbar.a3d-onsheet #a3d-snapgrp,#a3d-statusbar.a3d-onsheet #a3d-navgrp,#a3d-statusbar.a3d-onsheet #a3d-animgrp{display:none}")
rep("    /* __acad3dV116: the layout tabs and the space button */\n",
    "    var animGrp=root.querySelector('#a3d-animgrp');   /* __acad3dV170: Play, Pause and Stop */\n"
    "    if(animGrp)animGrp.addEventListener('click',function(ev){\n"
    "      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3danim]'):null;\n"
    "      if(!b)return;\n"
    "      if(b.getAttribute('data-a3danim')==='stop')bimAnimStop();else bimAnimPlay();\n"
    "    });\n"
    "    /* __acad3dV116: the layout tabs and the space button */\n")

# ---- the command ----
rep("    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],\n",
    "    ['PLAY',['ANIMATE','PAUSE','MOTION','PLAYANALYSIS'],'animplay','Play or pause the site analysis in motion: marching dashes along flows, walks and transit, winds drawn on, the distance rings growing, the layers in turn, the sun and the shadows through the day; Stop in the status bar gives the still drawing back'],   /* __acad3dV170 */\n"
    "    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],\n")
rep("    analyzesite:function(){bimAnzView();bimSiteAnalyze('');},   /* __acad3dV164 */\n",
    "    analyzesite:function(){bimAnzView();bimSiteAnalyze('');},   /* __acad3dV164 */\n"
    "    animplay:function(){bimAnimPlay();},   /* __acad3dV170 */\n")

# ---- Motion, a style of the element ----
rep("""    r+=bimPropRow('Opacity (%)','<input type="number" min="10" max="100" step="5" data-dgf="op\"""",
    """    var mk=bimAnimKinds(o),au=bimAnimAuto(o),am=au?(au[2]==='sun'||mk.indexOf(au[2])>=0?au[2]:null):null;   /* __acad3dV170 */
    if(mk.length||am){
      var mc=s.anim&&BIM_ANIM_NAMES[s.anim]?s.anim:'',mo='<option value=""'+(mc?'':' selected')+'>Default ('+bimEsc((am?BIM_ANIM_NAMES[am]:'Still').toLowerCase())+')</option>';
      ['none'].concat(mk).forEach(function(m){mo+='<option value="'+m+'"'+(mc===m?' selected':'')+'>'+bimEsc(BIM_ANIM_NAMES[m])+'</option>';});
      r+=bimPropRow('Motion','<select data-dgf="anim">'+mo+'</select>');
    }
    r+=bimPropRow('Opacity (%)','<input type="number" min="10" max="100" step="5" data-dgf="op\"""")
rep("    if(!(f==='stroke'||f==='fill'||f==='w'||f==='dash'||f==='op'||li>=0))return false;\n",
    "    if(f==='anim'&&!(v===''||v==='none'||bimAnimKinds(o).indexOf(String(v))>=0))return false;   /* __acad3dV170 */\n"
    "    if(f==='anim'&&String(v)===String(s.anim||''))return true;\n"
    "    if(!(f==='stroke'||f==='fill'||f==='w'||f==='dash'||f==='op'||f==='anim'||li>=0))return false;\n")
rep("    else if(f==='op')s.op=Math.round(n)/100;\n",
    "    else if(f==='op')s.op=Math.round(n)/100;\n"
    "    else if(f==='anim'){if(v==='')delete s.anim;else s.anim=String(v);}\n")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
