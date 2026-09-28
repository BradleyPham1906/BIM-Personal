"""patch_phase120m.py -- V120: what the rename left reading like the old shell.

enter3d still called the left shell's elements flShell and flPanel, "fl" for the Figma-layers
sidebar they were named after, and its comments called the panel the "file dock" and told how the
whiteboard's dock used to be collapsed on entry. The V80 whitelist kept a note about the
whiteboard's "A?" button, whose class no longer appears anywhere; the lesson it carried -- claim a
control only after driving it -- is a standing rule of the project, not a property of this list.
The top bar's height variable was still --acad-ribbon-h, the height of a ribbon V120c removed; it
is --a3d-top-h. The V67 note on the status bar still described the 2D workspace's #acad-status and
window.CAD/cadRun as the thing it answered, and the V68 note on the inspector named a design tool the
file no longer mentions anywhere else.

Names and comments only: the proof from V120j is repeated, every script token but the two renamed
variables and the one reworded warning is unchanged."""
NAME = 'patch_phase120m.py'
BASE = 'd6e771ccb884299e9c043b9aba4bad302a476a82af407e79e75f87cf55520165'
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
# ---- the lexer for the proof below (checked against acorn on this build)
_PUNCT_BEFORE_REGEX = set('(,=:[!&|?{};+-*%<>~^')
_KW_BEFORE_REGEX = {'return', 'typeof', 'case', 'do', 'else', 'in', 'instanceof', 'new', 'delete',
                    'void', 'throw', 'yield', 'await'}
_WORDCH = re.compile(r'[A-Za-z0-9_$]')


def decode(body):
    """The value of a string literal's body (between the quotes)."""
    out, i, n = [], 0, len(body)
    while i < n:
        c = body[i]
        if c != '\\':
            out.append(c); i += 1; continue
        i += 1
        if i >= n:
            break
        c = body[i]
        simple = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v', '0': '\0'}
        if c in simple and not (c == '0' and i + 1 < n and body[i + 1].isdigit()):
            out.append(simple[c]); i += 1
        elif c == 'u':
            if i + 1 < n and body[i + 1] == '{':
                j = body.index('}', i)
                out.append(chr(int(body[i + 2:j], 16))); i = j + 1
            else:
                out.append(chr(int(body[i + 1:i + 5], 16))); i += 5
        elif c == 'x':
            out.append(chr(int(body[i + 1:i + 3], 16))); i += 3
        elif c == '\r':
            i += 2 if body[i:i + 2] == '\r\n' else 1
        elif c in '\n  ':
            i += 1
        else:
            out.append(c); i += 1
    s = ''.join(out)
    # a surrogate pair written as two \\u escapes is one character, as it is to the browser
    return s.encode('utf-16', 'surrogatepass').decode('utf-16') if re.search('[\ud800-\udfff]', s) else s


def lex(code):
    """Yield (kind, start, end) with kind in comment, string, template, regex, word, num, punct."""
    i, n = 0, len(code)
    prev = None          # (kind, text) of the previous significant token
    while i < n:
        c = code[i]
        if c in ' \t\r\n ﻿  ':
            i += 1; continue
        if code.startswith('//', i):
            j = code.find('\n', i)
            j = n if j < 0 else j
            yield ('comment', i, j); i = j; continue
        if code.startswith('/*', i):
            j = code.find('*/', i + 2)
            j = n if j < 0 else j + 2
            yield ('comment', i, j); i = j; continue
        if c in '"\'':
            j = i + 1
            while j < n and code[j] != c:
                j += 2 if code[j] == '\\' else 1
            yield ('string', i, j + 1); prev = ('string', ''); i = j + 1; continue
        if c == '`':
            j = i + 1
            depth = 0
            while j < n:
                if code[j] == '\\':
                    j += 2; continue
                if code[j] == '`' and depth == 0:
                    break
                if code.startswith('${', j):
                    depth += 1; j += 2; continue
                if code[j] == '}' and depth:
                    depth -= 1
                j += 1
            yield ('template', i, j + 1); prev = ('template', ''); i = j + 1; continue
        if c == '/':
            is_regex = prev is None or (prev[0] == 'punct' and prev[1][-1] in _PUNCT_BEFORE_REGEX) or \
                (prev[0] == 'word' and prev[1] in _KW_BEFORE_REGEX)
            if is_regex:
                j, cls = i + 1, False
                while j < n:
                    ch = code[j]
                    if ch == '\\':
                        j += 2; continue
                    if ch == '[':
                        cls = True
                    elif ch == ']':
                        cls = False
                    elif ch == '/' and not cls:
                        break
                    elif ch == '\n':
                        raise ValueError('unterminated regex at %d' % i)
                    j += 1
                j += 1
                while j < n and _WORDCH.match(code[j]):
                    j += 1
                yield ('regex', i, j); prev = ('regex', ''); i = j; continue
        if _WORDCH.match(c):
            j = i
            while j < n and (_WORDCH.match(code[j]) or (code[j] == '.' and c.isdigit())):
                j += 1
            kind = 'num' if c.isdigit() else 'word'
            yield (kind, i, j); prev = (kind, code[i:j]); i = j; continue
        if c == '.' and i + 1 < n and code[i + 1].isdigit():
            j = i + 1
            while j < n and _WORDCH.match(code[j]):
                j += 1
            yield ('num', i, j); prev = ('num', code[i:j]); i = j; continue
        # punctuation: the longest operators first matter only for '/' handling via prev
        m = re.match(r'>>>=|===|!==|\*\*=|<<=|>>=|>>>|\.\.\.|=>|==|!=|<=|>=|&&|\|\||\?\?|\+\+|--|[-+*/%&|^]=|<<|>>|\*\*|.', code[i:i + 4], re.S)
        tok = m.group(0)
        yield ('punct', i, i + len(tok))
        # ')' and ']' end an expression; '++'/'--' are ambiguous and treated as ending one
        prev = ('punct', tok) if tok not in (')', ']', '}', '++', '--') else ('end', tok)
        i += len(tok)



ORIG = t
rep("""    /* __acad3dV65: ONE left column, not two.

       Previously this collapsed the file dock to its icon rail on entry, because the dock's panel
       and this shell's own Properties/Project Browser tree (.a3d-tree) competed for the same
       left-hand space. That was a truce, not a fix: re-opening File or Assets from the rail put a
       242px panel back on screen beside a 268px tree -- 510px of chrome before any drawing -- and
       the two read as two separate navigators, which is exactly what the app was being criticised
       for.

       The tree is now NESTED INSIDE the dock panel instead, so the rail's own content and the BIM
       navigator stack as sections in a single scrolling column. That is the shape every comparable
       tool uses (a narrow rail selecting a panel; stacked, collapsible sections within it).
""", """    /* __acad3dV65: ONE left column, not two. The Project Browser tree is NESTED INSIDE the left
       panel, so the rail's sections and the BIM navigator stack in a single column -- the shape
       every comparable tool uses (a narrow rail selecting a panel; stacked sections within it).
""")
rep("""      var flShell=document.getElementById('a3d-shell');
      var flPanel=document.getElementById('a3d-leftpanel');
      var tree=el.root&&el.root.querySelector('.a3d-tree');
      if(flPanel&&tree&&tree.parentNode!==flPanel){
        flPanel.appendChild(tree);
        document.body.classList.add('a3d-tree-docked');
      }
      if(flShell&&flShell.classList.contains('collapsed')){
        // The dock is now the host for the BIM navigator, so it must be open on entry --
        // the opposite of the old behaviour, and the reason that block is gone.
        flShell.classList.remove('collapsed');
      }
      bimShellDockW();
    }catch(eDock){console.warn('[BIM] Could not nest the Project Browser into the file dock; falling back to the separate panel.',eDock);}""",
"""      var shellEl=document.getElementById('a3d-shell');
      var panelEl=document.getElementById('a3d-leftpanel');
      var tree=el.root&&el.root.querySelector('.a3d-tree');
      if(panelEl&&tree&&tree.parentNode!==panelEl){
        panelEl.appendChild(tree);
        document.body.classList.add('a3d-tree-docked');
      }
      if(shellEl&&shellEl.classList.contains('collapsed')){
        // the panel hosts the BIM navigator, so it opens on entry
        shellEl.classList.remove('collapsed');
      }
      bimShellDockW();
    }catch(eDock){console.warn('[BIM] Could not nest the Project Browser into the left panel; it stays in the shell\\'s own pane.',eDock);}""")
rep("""       not folded into the dock-nesting one above: if the file dock is missing the navigator
       falls back to the shell's own left pane,""", """       not folded into the nesting one above: if the left panel is missing the navigator
       falls back to the shell's own left pane,""")
rep("""    /* __acad3dV85: '.fl-help' -- the "A?" button -- used to be claimed here as 'keyboard
       help'. It was claimed on the strength of its appearance and never driven; it had no
       handler at all. A whitelist entry taken on faith is worse than no whitelist, because it
       turns an unexamined control into a documented one. The button is gone and so is its
       claim. Claim a control only after driving it. */
""", "")


rep("""         button -- correct while the tree is a child of the shell, but since V65 it is a section
         inside the file dock, which is itself the drawer. Without this the dock rendered as an
         empty 296px column on a 700px screen: header, then nothing. */""", """         button -- correct while the tree is a child of the shell, but since V65 it is a section
         inside the left panel, which is itself the drawer. Without this the panel rendered as an
         empty 296px column on a 700px screen: header, then nothing. */""")


rep("""       LEFT column, which is Figma's arrangement, not Rayon's: it put "what exists" and "what""",
    """       LEFT column, which is not Rayon's arrangement: it put "what exists" and "what""")
rep("""/* __acad3dV67: the BIM status bar. Phase 64 documented the last remaining shell
       difference: the 2D workspace has #acad-status pinned to the bottom of the window and
       the BIM workspace had nothing there, because #acad-status's four toggles drive
       window.CAD/cadRun (the 2D engine) and would be dead controls in BIM. This is the
       honest fix -- the same 26px strip, the same colours, type and toggle language, in the
       same screen position, carrying BIM's OWN state. It is the third flex child of #acad3d
       (toolbar / body / status) so it spans the work area exactly, which is what the
       --a3d-left-w contract already defines as "the same position" in this shell. */""",
"""/* __acad3dV67: the BIM status bar -- a 26px strip carrying the workspace's own state. It is the
       third flex child of #acad3d (toolbar / body / status), so it spans the work area exactly. */""")
# the top bar's height is named for the bar, not for the ribbon it outlived
if len(re.findall(r'--acad-ribbon-h(?![\w-])', t)) != 6 or '--a3d-top-h' in t:
    sys.exit('ABORT: --acad-ribbon-h is not where it was measured')
t = re.sub(r'--acad-ribbon-h(?![\w-])', '--a3d-top-h', t)
rep("""/* ---- the top bar: the quick-access buttons and the project tabs. --a3d-top-h is its
   height, which every surface below it is positioned against: 28 + 24 px, and 22 + 22 in
   the compact tier. ---- */""", """/* ---- the top bar: the quick-access buttons and the project tabs. --a3d-top-h is its height,
   which every surface below it is positioned against: 28 + 24 px, and 22 + 22 in the compact
   tier. ---- */""")


def sig(text):
    toks = []
    opener = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
    low = text.lower()
    i = 0
    while True:
        m = opener.search(text, i)
        if not m:
            return toks
        if m.group(0) == '<!--':
            i = text.index('-->', m.end()) + 3
            continue
        tag = m.group(1).lower()
        e = low.index('</%s>' % tag, m.end())
        if tag == 'script':
            body = text[m.end():e]
            toks.append([{'flShell': 'shellEl', 'flPanel': 'panelEl'}.get(body[a:b], body[a:b]) for k, a, b in lex(body) if k != 'comment'])
        i = e + len(tag) + 3


s0, s1 = sig(ORIG), sig(t)
# the one intended token change: the warning's text
w0 = "'[BIM] Could not nest the Project Browser into the file dock; falling back to the separate panel.'"
w1 = "'[BIM] Could not nest the Project Browser into the left panel; it stays in the shell\\'s own pane.'"
s0 = [[w1 if x == w0 else x for x in blk] for blk in s0]
if s0 != s1:
    sys.exit('ABORT: a script token changed beyond the two renamed variables and the warning')
if re.search(r'\bfl(Shell|Panel)\b|file dock', t):
    sys.exit('ABORT: an old name is left')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
