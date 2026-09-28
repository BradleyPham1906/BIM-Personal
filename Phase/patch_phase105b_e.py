"""patch_phase105be.py"""
NAME = 'patch_phase105be'
BASE = '4c75166ad7441432c9b3f1c73d49de9fd16f7c93a96aa95d1127ab56f5f4c7e7'
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
# --- patch e: AREAPLAN, the overlay it draws, and the API the suite drives it through.

after_line("    ['TRIBAREA',['TRIBUTARY','TRIB'],'tribarea',",
"    ['AREAPLAN',['AREA','GROSSAREA','AP'],'areaplan','Show or hide the gross area inside the exterior walls on this level'],   /* __acad3dV105b */\n")

after_line("    tribarea:function(){bimToggleTrib();},",
"    areaplan:function(){bimToggleAreaPlan();},        /* __acad3dV105b */\n")

after_line("    drawTribAreas(ctx,V,W,H);",
"    drawAreaPlan(ctx,V,W,H);           /* __acad3dV105b */\n")

rep("""  function bimToggleTrib(){""","""  /* __acad3dV105b: the area plan overlay. It reads bimLevelAreas, which is what the schedule and
     the toast read, so the ring on screen and the number in the schedule cannot disagree. */
  function bimToggleAreaPlan(){
    A3D.showArea=!A3D.showArea;
    paint();
    if(!A3D.showArea){a3dToast('Area plan hidden');return false;}
    var a=bimLevelAreas(A3D.activeLevel);
    if(a.gross===null)a3dToast('Area plan on '+a.level+': nothing to measure'+(a.note?' -- '+a.note:''));
    else a3dToast('Area plan on '+a.level+': gross '+a.gross.toFixed(2)+' m\\u00b2, net '+a.net.toFixed(2)+
                  ' m\\u00b2'+(a.efficiency===null?'':' ('+a.efficiency.toFixed(0)+'% efficient)')+
                  (a.occupants===null?'':', '+a.occupants+' occupant'+(a.occupants===1?'':'s')));
    return true;
  }
  function drawAreaPlan(ctx,V,W,H){
    A3D.lastAreaDrawn=null;
    if(!A3D.showArea||A3D.section||A3D.sheetCapture)return;
    var lv=bimLevelById(A3D.activeLevel);
    if(!lv)return;
    var a,y=lv.elev||0,i,j,sp,ok,cx,cz,cp,txt,p,s;
    ctx.save();
    try{
      a=bimLevelAreas(A3D.activeLevel);
      ctx.font='11px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
      for(i=0;i<a.rings.length;i++){
        sp=[];ok=true;cx=0;cz=0;
        for(j=0;j<a.rings[i].pts.length;j++){
          p=a.rings[i].pts[j];
          cx+=p[0];cz+=p[1];
          s=toScreen([p[0],y,p[1]],V,W,H);
          if(!s||!isFinite(s[0])||!isFinite(s[1])){ok=false;break;}
          sp.push(s);
        }
        if(!ok||sp.length<3)continue;
        cx/=a.rings[i].pts.length;cz/=a.rings[i].pts.length;
        ctx.beginPath();ctx.moveTo(sp[0][0],sp[0][1]);
        for(j=1;j<sp.length;j++)ctx.lineTo(sp[j][0],sp[j][1]);
        ctx.closePath();
        ctx.fillStyle='rgba(90,209,160,0.10)';ctx.fill();
        ctx.setLineDash([9,5]);ctx.lineWidth=1.6;ctx.strokeStyle='#5ad1a0';ctx.stroke();
        cp=toScreen([cx,y,cz],V,W,H);
        if(cp&&isFinite(cp[0])&&isFinite(cp[1])){
          txt=a.rings[i].area.toFixed(2)+' m\\u00b2 gross';
          ctx.setLineDash([]);ctx.lineWidth=3;ctx.strokeStyle='rgba(0,0,0,0.75)';ctx.strokeText(txt,cp[0],cp[1]);
          ctx.fillStyle='#d7fff0';ctx.fillText(txt,cp[0],cp[1]);
        }
      }
      A3D.lastAreaDrawn={levelId:a.levelId,rings:a.rings.length,gross:a.gross,net:a.net,
                         efficiency:a.efficiency,occupants:a.occupants,note:a.note};
    }catch(eAD){
      if(!A3D.areaWarned){A3D.areaWarned=true;a3dToast('The area plan could not be drawn');}
      console.warn('[BIM] Area plan draw failed: ',eAD);
    }
    ctx.restore();
  }
  function bimToggleTrib(){""",1)

after_line("  window.__a3dSunPath=function(){return A3D.lastSunPath||null;};",
"""  /* __acad3dV105b: area plans, through the same functions the schedule and the overlay read. */
  window.__a3dLevelAreas=function(levelId){return bimLevelAreas(levelId||A3D.activeLevel);};
  window.__a3dGrossRings=function(levelId){
    var r=bimLevelGrossRings(levelId||A3D.activeLevel);
    return {error:r.error||null,rings:(r.rings||[]).map(function(x){return {pts:x.pts,area:x.area,srcIds:x.srcIds};})};
  };
  window.__a3dAreaDrawn=function(){return A3D.lastAreaDrawn||null;};
  window.__a3dWallFaceRings=function(id){var o=objById(id);return o?bimWallFaceRings(o):null;};
  window.__acad3dV105b='wallbasepts,wallfacerings,grossrings,levelareas,arealevel,areaplan';
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
