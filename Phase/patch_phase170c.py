#!/usr/bin/env python3
"""V170c: Save image takes the view as it is that moment, the model included -- the 3D canvas (WebGPU or WebGL,
which keep no picture once a frame is shown) copied in the task it is drawn in, the overlay over it; the hooks,
the marker and the version.

Run from the repository root: python3 Phase/patch_phase170c.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '5dad54056677c7adb0dcbd86ef4ff275126ddbc79ee52cd17d9fe8467d12cf04'   # V170b

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


rep("""  /* ---- Save image ----
     The viewport canvas itself, downloaded. Local-first: no server, no upload. */
  function bimSaveViewportPng(){
    if(!el.cv){a3dToast('No viewport to capture');return false;}
    try{
      var url=el.cv.toDataURL('image/png');
""", """  /* ---- Save image ----
     The viewport canvas itself, downloaded. Local-first: no server, no upload.
     __acad3dV170: the view as it is this moment, the model included. The model is on a canvas of its own under the
     overlay (WebGPU or WebGL), which keeps no picture once its frame is shown, so the view is drawn and that canvas
     copied in the same task, the overlay laid over it; a motion playing or paused is taken as it stands. */
  function bimViewportCanvas(){
    var cv=el.cv,out=document.createElement('canvas'),c,src=null,eng,id;
    out.width=cv.width;out.height=cv.height;c=out.getContext('2d');
    paint();
    eng=A3D_GPU.engine;id=eng==='webgpu'?'a3d-gpucanvas':(eng==='webgl'?'a3d-glcanvas':'');
    if(id&&!A3D.presentMode&&!bimPresentGraphics()){src=document.getElementById(id);if(src&&(src.style.visibility==='hidden'||!(src.width>0)||!(src.height>0)))src=null;}
    if(src)c.drawImage(src,0,0,out.width,out.height);
    c.drawImage(cv,0,0);
    return {cv:out,engine:src?eng:'2d'};
  }
  function bimSaveViewportPng(){
    if(!el.cv){a3dToast('No viewport to capture');return false;}
    try{
      var url=bimViewportCanvas().cv.toDataURL('image/png');
""")

rep("  window.__acad3dV169='assets,people,wheelchair,cycles,stands,bay,trees,leaf,gsl,shadows,turning,contexttrees,registry,vehicles,turningpaths,refit';\n",
    "  window.__acad3dV169='assets,people,wheelchair,cycles,stands,bay,trees,leaf,gsl,shadows,turning,contexttrees,registry,vehicles,turningpaths,refit';\n"
    "  window.__acad3dV170='clock,play,pause,stop,march,drawon,rings,reveal,sun,shadowday,motionstyle,reducedmotion,hidden,saveimage3d,command';\n"
    "  /* __acad3dV170: the analyses in motion */\n"
    "  window.__a3dAnim=function(){var F=bimAnimFrame();return JSON.parse(JSON.stringify({on:A3D_ANIM.on,paused:A3D_ANIM.paused,t:A3D_ANIM.t,playAt:A3D_ANIM.playAt,sunTime:A3D_ANIM.sunTime,can:A3D_ANIM.can,frames:A3D_ANIM.frames,live:bimAnimLive(),\n"
    "    raf:!!A3D_ANIM.raf,fr:{order:F.order,idx:F.idx,rings:F.rings,Rmax:F.Rmax,any:F.any,sun:F.sun,sunAt:F.sunAt||null,shadowDone:F.shadowDone}}));};\n"
    "  window.__a3dAnimPlay=function(on){return bimAnimPlay(on);};\n"
    "  window.__a3dAnimStop=function(){return bimAnimStop();};\n"
    "  /* the clock set by hand, paused there: the frame at t seconds, the last Play at playAt */\n"
    "  window.__a3dAnimAt=function(t,playAt){bimAnimHalt();A3D_ANIM.on=false;A3D_ANIM.paused=true;A3D_ANIM.t=+t||0;A3D_ANIM.playAt=+playAt||0;A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();paint();return window.__a3dAnim();};\n"
    "  window.__a3dAnimOf=function(id){var o=objById(id);if(!bimIsDiag(o))return null;var R=bimAnimRingOf(o);\n"
    "    return {motion:bimAnimMotion(o),kinds:bimAnimKinds(o),auto:bimAnimAuto(o),out:bimAnimOut(o),ring:R,k:bimAnimLive()&&bimAnimMotion(o)==='ring'?bimAnimRingK(o):null,draw:bimAnimLive()&&bimAnimMotion(o)==='draw'?bimAnimDrawOf(o):null,reveal:bimAnimReveal(o.dg.a)};};\n"
    "  window.__a3dAnimSettings=function(){return JSON.parse(JSON.stringify({anim:BIM_ANIM,names:BIM_ANIM_NAMES,auto:BIM_ANIM_AUTO}));};\n"
    "  window.__a3dAnimTint=function(h){return bimAnimTint(h);};\n"
    "  window.__a3dAnimSunTime=function(t){var k=A3D_ANIM.t;A3D_ANIM.t=+t||0;var r=bimAnimSunTime();A3D_ANIM.t=k;return r;};\n"
    "  window.__a3dViewportImage=function(){var r=bimViewportCanvas();return {url:r.cv.toDataURL('image/png'),engine:r.engine,w:r.cv.width,h:r.cv.height};};\n")
rep("  var BIM_APP_VERSION={v:'V169',date:'2026-10-19'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168 */",
    "  var BIM_APP_VERSION={v:'V170',date:'2026-10-24'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170 */")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
