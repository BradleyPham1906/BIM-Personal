"""falsify_phase170.py -- break the V170 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase170_animation_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. before Play ----
    'set_speed': [("march:{speed:28,dash:6,gap:14}", "march:{speed:30,dash:6,gap:14}")],   # the clock's settings are the design's
    'set_names': [("ring:'Growing ring',sun:'Through the day'", "ring:'Ring',sun:'Through the day'")],   # the motions' names
    'auto_walk_lost': [("['walk','w','march'],", "")],   # each element has the motion the design gives it
    'kinds_no_draw': [("    if(k!=='segs'&&k!=='lines'&&n>=2)L.push('draw');\n", "")],   # drawn on: the winds
    'opens_playing': [("var A3D_ANIM={on:false,paused:false,t:0,", "var A3D_ANIM={on:false,paused:true,t:0,")],   # the app opens still
    'nothing_play_silent': [("if(on&&!bimAnimCan()){a3dToast('Nothing to play: show a site analysis layer, or the sun study in plan');return false;}", "if(on&&!bimAnimCan()){return false;}")],   # Play with nothing to move says so
    'cmd_missing': [("['PLAY',['ANIMATE','PAUSE','MOTION','PLAYANALYSIS'],'animplay',", "['PLAYMOTION',['PLAYANALYSIS'],'animplay',")],   # searching 'animate' finds PLAY
    'grp_always_hidden': [("      g.hidden=!can;\n", "      g.hidden=true;\n")],   # a run drawn: PLAY in the status bar
    'sync_missing': [("    if(!capMode)bimAnimSync();   /* __acad3dV170: Play and Pause, shown when something can move */\n", "")],   # a run drawn: PLAY in the status bar
    # ---- 2. Play, Pause, Stop ----
    'fps_uncapped': [("if(!A3D_ANIM.painted||ts-A3D_ANIM.painted>=1000/BIM_ANIM.fps-2){", "if(true){")],   # fed a second of frames: 30 drawn
    'clock_unclamped': [("A3D_ANIM.t+=Math.min(0.1,Math.max(0,(ts-A3D_ANIM.last)/1000));", "A3D_ANIM.t+=Math.max(0,(ts-A3D_ANIM.last)/1000);")],   # a half-second gap moves it a tenth
    'clock_ahead': [("A3D_ANIM.t+=Math.min(0.1,Math.max(0,(ts-A3D_ANIM.last)/1000));", "A3D_ANIM.t+=Math.min(0.1,Math.max(0,(ts-A3D_ANIM.last)/1000))*1.5;")],   # the clock runs in real time
    'pause_keeps_running': [("    }else{A3D_ANIM.paused=true;bimAnimHalt();}\n", "    }else{A3D_ANIM.paused=true;}\n")],   # Pause: the frames stand still
    'pause_snaps_still': [("    }else{A3D_ANIM.paused=true;bimAnimHalt();}\n", "    }else{A3D_ANIM.paused=false;bimAnimHalt();}\n")],   # paused: the moment still drawn
    'resume_restarts': [("      if(!A3D_ANIM.paused){A3D_ANIM.t=0;A3D_ANIM.playAt=0;}\n", "      A3D_ANIM.t=0;A3D_ANIM.playAt=0;\n")],   # Play again goes on from the moment
    'resume_reveals_again': [("      A3D_ANIM.paused=false;A3D_ANIM.c=null;", "      A3D_ANIM.paused=false;A3D_ANIM.playAt=A3D_ANIM.t;A3D_ANIM.c=null;")],   # without bringing the layers in again
    'hidden_runs': [("document.addEventListener('visibilitychange',function(){if(document.hidden)bimAnimHalt();else bimAnimRun();});", "document.addEventListener('visibilitychange',function(){if(!document.hidden)bimAnimRun();});")],   # the page hidden: the clock waits
    'hidden_never_back': [("document.addEventListener('visibilitychange',function(){if(document.hidden)bimAnimHalt();else bimAnimRun();});", "document.addEventListener('visibilitychange',function(){if(document.hidden)bimAnimHalt();});")],   # shown again: it goes on
    'reduced_ignored': [("f=function(){if(mq.matches&&A3D_ANIM.on){", "f=function(){if(false&&mq.matches&&A3D_ANIM.on){")],   # reduced motion while it plays: paused
    'stop_keeps_t': [("    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;\n    bimAnimHalt();\n", "    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;\n    bimAnimHalt();\n")],   # Stop: the clock at nothing
    'stop_stays_paused': [("    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;\n    bimAnimHalt();\n", "    A3D_ANIM.on=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;\n    bimAnimHalt();\n")],   # Stop: still
    'stop_btn_stays': [("      if(x)x.hidden=!moving;\n", "      if(x)x.hidden=false;\n")],   # a run drawn: no Stop yet
    'aria_pressed': [("b.setAttribute('aria-pressed',A3D_ANIM.on?'true':'false');", "b.setAttribute('aria-pressed','false');")],   # Play pressed: pressed
    'aria_label': [("      b.setAttribute('aria-label',A3D_ANIM.on?'Pause':'Play');\n", "")],   # Play pressed: named Pause
    'project_touched': [("    }else{A3D_ANIM.paused=true;bimAnimHalt();}\n    paint();\n", "    }else{A3D_ANIM.paused=true;bimAnimHalt();}\n    pushUndo();paint();\n")],   # Play, Pause and Stop left the project as it was
    'sun_writes_time': [("A3D_ANIM.painted=ts;A3D_ANIM.sunTime=bimAnimSunTime();", "A3D_ANIM.painted=ts;A3D_ANIM.sunTime=bimAnimSunTime();if(A3D_ANIM.sunTime&&A3D.site&&A3D.site.sun)A3D.site.sun.time=A3D_ANIM.sunTime;")],   # the sun's date and time unchanged
    'nothing_left_plays': [("    if(!can&&moving){A3D_ANIM.on=false;", "    if(false){A3D_ANIM.on=false;")],   # every analysis hidden: still, the buttons gone
    'keys_dead': [("      if(b.getAttribute('data-a3danim')==='stop')bimAnimStop();else bimAnimPlay();\n", "      if(b.getAttribute('data-a3danim')==='stop')bimAnimStop();else if(ev.detail)bimAnimPlay();\n")],   # the keyboard: Enter plays
    # ---- 3. marching dashes ----
    'march_still': [("ctx.setLineDash([M.dash+2*w,M.gap+2*w]);ctx.lineDashOffset=off;", "ctx.setLineDash([M.dash+2*w,M.gap+2*w]);ctx.lineDashOffset=0;")],   # the drawing moves between 5.00 and 5.25 s
    'march_way_reversed': [("    if(bimAnimFar(o,W[0],c)>bimAnimFar(o,W[W.length-1],c))P.reverse();\n", "    if(bimAnimFar(o,W[0],c)<bimAnimFar(o,W[W.length-1],c))P.reverse();\n")],   # each march runs its way
    'march_segs_unturned': [("      for(i=0;i+1<W.length;i+=2)if(bimAnimFar(o,W[i],c)>bimAnimFar(o,W[i+1],c)){t=P[i];P[i]=P[i+1];P[i+1]=t;}\n", "")],   # each pair turned
    'march_lines_unturned': [("    if(bimAnimFar(o,Wl[0],c)>bimAnimFar(o,Wl[Wl.length-1],c))lp.reverse();\n", "")],   # each polyline turned
    'march_path_out': [("return !(o.dg.s&&o.dg.s.head)&&!(A&&A[3]==='path');", "return !(o.dg.s&&o.dg.s.head);")],   # as drawn: the routes
    'tint_mix': [("t=(0.2126*r+0.7152*g+0.0722*b)/255>0.72?[0,0.5]:[255,0.6];", "t=(0.2126*r+0.7152*g+0.0722*b)/255>0.72?[0,0.5]:[255,0.5];")],   # the moving dashes' colour
    'tint_no_pale': [("t=(0.2126*r+0.7152*g+0.0722*b)/255>0.72?[0,0.5]:[255,0.6];", "t=[255,0.6];")],   # darker on a pale line
    'still_ignored': [("    if(m==='none')return null;\n", "")],   # each set still: the same at both moments
    # ---- 4. winds drawn on ----
    'draw_linear': [("return {f:x*x*(3-2*x),a:1};", "return {f:x,a:1};")],   # how far each is drawn
    'draw_no_stagger': [("p=bimAnimMod(A3D_ANIM.t-i*B.stagger,per)", "p=bimAnimMod(A3D_ANIM.t,per)")],   # the second after the first
    'draw_no_fade': [("return {f:1,a:1-(p-B.grow-B.hold)/B.fade};", "return {f:1,a:1};")],   # how clear
    'draw_unclipped': [("ctx.save();clip=true;bimAnimClip(ctx,P,an.f,!!g.closed);", "ctx.save();clip=true;")],   # its tip not yet
    'draw_under_unclipped': [("a*=an.a;bimAnimClip(ctx,P,an.f,true);}", "a*=an.a;}")],   # its tip not yet
    'draw_axis': [("B=closed?P[Math.floor((n-1)/2)]:P[n-1];", "B=P[n-1];")],   # tail to tip
    'draw_words_early': [("lbOk=an.f>=1;", "lbOk=true;")],   # its words come when it is whole
    # ---- 5. rings and reveals ----
    'ring_speed': [("w=bimAnimMod(A3D_ANIM.t,F.Rmax/B.mps+B.hold)*B.mps;", "w=bimAnimMod(A3D_ANIM.t,F.Rmax/B.mps+B.hold)*B.mps*1.2;")],   # the ripple
    'ring_all_grow': [("    for(i=0;i<F.rings.length;i++)if(F.rings[i]>w+1e-6&&F.rings[i]<R.r-1e-6)return 0;\n", "")],   # the front carried by the smallest ring
    'ring_no_hold': [("w=bimAnimMod(A3D_ANIM.t,F.Rmax/B.mps+B.hold)*B.mps;", "w=bimAnimMod(A3D_ANIM.t,F.Rmax/B.mps)*B.mps;")],   # held at the outermost
    'ring_unscaled': [("P=rk<1?bimAnimScreen(o,V,W,H,rk):bimDgScreen(o,V,W,H);", "P=bimDgScreen(o,V,W,H);")],   # on the canvas: at 50 m first
    'ring_words_early': [("lbOk=rk>=1;", "lbOk=true;")],   # a ring's words wait
    'reveal_order': [("for(i=0;i<BIM_DG_AN.length;i++)if(seen[BIM_DG_AN[i].id])F.order[BIM_DG_AN[i].id]=j++;", "for(i=BIM_DG_AN.length-1;i>=0;i--)if(seen[BIM_DG_AN[i].id])F.order[BIM_DG_AN[i].id]=j++;")],   # in Analyze's order
    'reveal_hidden_counted': [("      if(!bimLayerShown(L[i]))continue;\n      a=L[i].dg.a;seen[a]=true;", "      a=L[i].dg.a;seen[a]=true;")],   # noise hidden takes no turn
    'reveal_slow': [("x=(A3D_ANIM.t-A3D_ANIM.playAt-j*R.step)/R.fade;", "x=(A3D_ANIM.t-A3D_ANIM.playAt-j*R.step)/(2*R.fade);")],   # each layer's share
    'reveal_over_off': [("    if(bimAnimLive())a*=bimAnimReveal(dg.a);\n", "")],   # on the canvas: not there at the first moment
    # ---- 6. the sun through the day ----
    'sun_no_hold': [("p=bimAnimMod(A3D_ANIM.t,B.secs+B.hold);", "p=bimAnimMod(A3D_ANIM.t,B.secs);")],   # held at sunset
    'sun_rise_floor': [("a=Math.ceil(r.sunrise);b=Math.floor(r.sunset);", "a=Math.floor(r.sunrise);b=Math.floor(r.sunset);")],   # from sunrise
    'sun_polar_day': [("if(r.polar==='day'){a=0;b=1439;}", "if(r.polar==='day'){a=0;b=1440;}")],   # the whole day
    'sun_override_saved': [("if(!saved&&A3D_ANIM.sunTime&&bimAnimLive())st.time=A3D_ANIM.sunTime;", "if(A3D_ANIM.sunTime&&bimAnimLive())st.time=A3D_ANIM.sunTime;")],   # Properties shows the study's own sun
    'sun_override_off': [("if(!saved&&A3D_ANIM.sunTime&&bimAnimLive())st.time=A3D_ANIM.sunTime;", "")],   # while it plays the sun is the clock's
    'sun_dome_lost': [("dome:run&&run.dome?run.dome:undefined,", "dome:undefined,")],   # the sun paths keep their dome
    'sun_dome_wrong': [("sp=toScreen(bimDgDome(S,D.R,sun),V,W,H);", "sp=toScreen(bimDgDome(S,D.R*1.1,sun),V,W,H);")],   # where its 14:00 lies
    'now_stays': [("if(!(a>0)||(mo==='sun'&&A3D_ANIM.sunTime&&bimAnimFrame().sun))return hit;", "if(!(a>0))return hit;")],   # the sun now gives way to it
    'shadow_all': [("if(mv){var F=bimAnimFrame();if(F.shadowDone)return;F.shadowDone=true;}", "if(mv){var F=bimAnimFrame();F.shadowDone=true;}")],   # one shadow
    'shadow_own_time': [("sun=L?(mv?bimDgSun(dt,A3D_ANIM.sunTime):bimDgSun(L.date,L.time)):null;", "sun=L?bimDgSun(L.date,L.time):null;")],   # away from the sun at 08:30 and 16:00
    'sunstudy_ignores': [("    var sun=bimSunNow();\n    if(sun.missing){A3D.lastShadows={missing:sun.missing};return;}", "    var sun=bimSunNow(true);\n    if(sun.missing){A3D.lastShadows={missing:sun.missing};return;}")],   # the sun study follows the same clock
    'sunstudy_cant': [("can=F.any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk())", "can=F.any")],   # with the sun study on, Play is there
    # ---- 7. Motion in Properties ----
    'props_no_motion': [("      r+=bimPropRow('Motion','<select data-dgf=\"anim\">'+mo+'</select>');\n", "")],   # the choices each shape can take
    'props_default_word': [("+'>Default ('+bimEsc((am?BIM_ANIM_NAMES[am]:'Still').toLowerCase())+')</option>'", "+'>Default</option>'")],   # Default (marching dashes)
    'props_extra': [("['none'].concat(mk).forEach(", "['none','march'].concat(mk).forEach(")],   # through the day, or still
    'set_refuse_any': [("    if(f==='anim'&&!(v===''||v==='none'||bimAnimKinds(o).indexOf(String(v))>=0))return false;   /* __acad3dV170 */\n", "")],   # a motion its shape cannot take, refused
    'set_same_step': [("    if(f==='anim'&&String(v)===String(s.anim||''))return true;\n", "")],   # the same again: no second step
    'set_default_keeps': [("else if(f==='anim'){if(v==='')delete s.anim;else s.anim=String(v);}", "else if(f==='anim'){s.anim=String(v);}")],   # Default takes the setting away
    # ---- 8. Save image ----
    'image_overlay_only': [("    if(src)c.drawImage(src,0,0,out.width,out.height);\n", "")],   # the image holds the model
    'image_no_paint': [("    paint();\n    eng=A3D_GPU.engine;", "    eng=A3D_GPU.engine;")],   # copied in the task it is drawn in
    'image_old_path': [("var url=bimViewportCanvas().cv.toDataURL('image/png');", "var url=el.cv.toDataURL('image/png');")],   # the file holds the model
    'image_size': [("out.width=cv.width;out.height=cv.height;", "out.width=cv.width-2;out.height=cv.height;")],   # at the view's size
    # ---- 9. still on paper ----
    'paper_moves': [("return (A3D_ANIM.on||A3D_ANIM.paused)&&!A3D.sheetCapture&&!A3D_PLOT.on;", "return (A3D_ANIM.on||A3D_ANIM.paused)&&!A3D_PLOT.on;")],   # a sheet drawn the same at any moment
    'paper_play_shown': [(",#a3d-statusbar.a3d-onsheet #a3d-animgrp{display:none}", "{display:none}")],   # on the sheet there is no Play
    # ---- 10. a phone, a tablet ----
    'phone_last': [("#a3d-animgrp{order:-1;margin-left:0;", "#a3d-animgrp{order:0;margin-left:0;")],   # Play first in the bar
    'phone_words': [("#a3d-animgrp .a3d-stbtn span{display:none}", "#a3d-animgrp .a3d-stbtn span{display:inline}")],   # an icon
    'phone_caption': [("#a3d-statusbar.a3d-hasanim .a3d-stlvl{font-size:0;gap:0}", "#a3d-statusbar.a3d-hasanim .a3d-stlvl{gap:0}")],   # the level's caption gives it its room
    'caption_stays_hidden': [("if(bar)bar.classList.toggle('a3d-hasanim',can);", "if(bar)bar.classList.add('a3d-hasanim');")],   # nothing to play: the caption back
    'tablet_rule': [("@media(max-width:1024px),(max-height:500px){#a3d-animgrp", "@media(max-width:720px),(max-height:500px){#a3d-animgrp")],   # a tablet: on the screen
    # ---- the marker and the version ----
    'marker_lost': [("sun,shadowday,motionstyle", "sun,motionstyle")],   # the V170 marker
    'version_old': [("var BIM_APP_VERSION={v:'V170',date:'2026-10-24'};", "var BIM_APP_VERSION={v:'V169',date:'2026-10-24'};")],   # V170 or later
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV170' in txt
out.write_text(txt, encoding='utf-8')
