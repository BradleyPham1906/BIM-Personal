"""patch_phase120e.py -- V120: the command palette without its whiteboard fall-backs.

The palette (Ctrl+K) and the project tabs were written when the palette also served the Canvas
whiteboard. What is left of that is code that can no longer run:
  - runCadAct's fall-through for a command asked for outside the BIM workspace, commented as the
    place "the fall-through into the retired whiteboard's dispatchers went with";
  - buildPalette's search for an OLD palette to replace -- the whiteboard's own, deleted in V113c;
  - pool()'s second branch, which listed every command, runnable or not, when the engine was not
    there to say which run;
  - runIdx's c.fn branch: every command in the registry carries its engine act, and none a function;
  - draw()'s key for a description starting 'Shortcut', which no command has had since the
    whiteboard's commands went.
And the section's catch stored an error in window.__wsErr and said nothing; it now warns, and
toasts once the engine can, as every failure in this file must."""
NAME = 'patch_phase120e.py'
BASE = 'a2929e354b3294807d2b7364b604339d51b635ea4e43b151750721fbb0b7cfc1'
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
rep("""  function runCadAct(act){
    /* __acad3dV86: in the BIM workspace these commands run against the BIM engine, and the
       fall-through below is NOT taken.

       That fall-through is why every palette command was dead: window.cadRun dispatches into
       WB[act], the retired Canvas whiteboard's table, which does not run in this workspace.
       Worse, this function returned true regardless of what cadRun did, so a command that did
       nothing still reported success and nothing ever surfaced the failure. */
    if(window.__a3dOn){
      try{ if(window.__a3dRunCmd)return !!window.__a3dRunCmd(act); }
      catch(e){ console.warn('[BIM] Palette command failed: '+act,e); }
      return false;
    }
    /* __acad3dV115: the fall-through into the retired whiteboard's dispatchers went with them */
    console.warn('[BIM] A command was asked for before the BIM workspace was on: '+act);
    return false;
  }
  /* __acad3dV113c: the nine whiteboard commands are gone with the whiteboard. V86 had already
     filtered them out of the BIM workspace's palette -- pool() keeps only commands the BIM engine
     supports -- which made them invisible rather than absent. */
  var REGISTRY=[];""",
"""  /* __acad3dV86: a command runs through the BIM engine and reports whether it ran, so a command
     that did nothing cannot report success (V120: the engine is the only thing it can run on). */
  function runCadAct(act){
    if(!window.__a3dOn||!window.__a3dRunCmd){
      console.warn('[BIM] A command was asked for before the BIM workspace was on: '+act);
      return false;
    }
    try{ return !!window.__a3dRunCmd(act); }
    catch(e){ console.warn('[BIM] Palette command failed: '+act,e); return false; }
  }
  var REGISTRY=[];""")
rep("""  // Replace the old palette node (same id/classes so existing open/close/Ctrl+K keep working)
  function buildPalette(){
    var old=document.getElementById('uploaded-command-palette');
    var pal=document.createElement('div'); pal.id='uploaded-command-palette';""",
"""  function buildPalette(){
    var pal=document.createElement('div'); pal.id='uploaded-command-palette';""")
rep("""    if(old) old.replaceWith(pal); else document.body.appendChild(pal);""",
"""    document.body.appendChild(pal);""")
rep("""    /* __acad3dV86: in the BIM workspace the palette offers only commands that RUN there.
       Everything it used to list dispatched into the retired Canvas whiteboard and did nothing;
       a shorter list of working commands beats a long list of dead ones. */
    function pool(){
      if(window.__a3dOn&&window.__a3dCmdSupported){
        return REGISTRY.filter(function(c){return c.cad&&window.__a3dCmdSupported(c.cad);});
      }
      return REGISTRY;
    }""",
"""    /* __acad3dV86: the palette offers only commands that RUN: a shorter list of working commands
       beats a long list of dead ones. Before the engine has loaded, nothing runs. */
    function pool(){
      if(!window.__a3dCmdSupported)return [];
      return REGISTRY.filter(function(c){return window.__a3dCmdSupported(c.cad);});
    }""")
rep("""        var key=c.aliases&&c.aliases.length?c.aliases[0]:(c.desc&&c.desc.indexOf('Shortcut')===0?c.desc.replace('Shortcut ',''):'');
        return '<div class="uc-row'+(i===0?' active':'')+'" data-idx="'+i+'"><span>'+c.name+(c.cad?' <span style="opacity:.45;font-weight:500">\\u2014 '+c.desc+'</span>':'')+'</span><span class="uc-key">'+key+'</span></div>';""",
"""        var key=c.aliases.length?c.aliases[0]:'';
        return '<div class="uc-row'+(i===0?' active':'')+'" data-idx="'+i+'"><span>'+c.name+' <span style="opacity:.45;font-weight:500">\\u2014 '+c.desc+'</span></span><span class="uc-key">'+key+'</span></div>';""")
rep("""      var ok=c.cad?runCadAct(c.cad):(c.fn?(c.fn(),true):false);""",
"""      var ok=runCadAct(c.cad);""")
rep("""  }catch(err){window.__wsErr=String(err&&err.stack||err);}""",
"""  }catch(err){
    window.__wsErr=String(err&&err.stack||err);
    console.warn('[BIM] The command palette and the project tabs could not be set up.',err);   /* __acad3dV120 */
    setTimeout(function(){if(window.__a3dToast)window.__a3dToast('The command palette could not be set up; reload the page');},1500);
  }""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
