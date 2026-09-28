"""patch_phase120j.py -- V120: comments that describe the whiteboard, and the file's whitespace.

Comments are a quarter of this file, and most of them are the reason the code is the way it is --
they stay. What goes or changes is what the cleanup made false or what was never more than a
tombstone:

  - comments that describe deleted code as live: the palette's "retired whiteboard module", the
    project tabs' "whiteboard's drawings", a Start-page history, the material cards' "board" and
    its wire.material.hatchColor, the shell's "canvas-era sidebar module", the Escape chain's
    "retired-Canvas blocks", the Delete key's window.__ws3Del, the tool registry's "ribbon",
    __a3dWantsKey's "Canvas-era shortcut gate", __a3dShellGeom's "#viewport (the Canvas board)",
    and a dozen more;
  - epitaphs: the click-to-select dock that went in V117, the 2D-chrome hider, the whiteboard dock's
    properties pop-out;
  - runs of blank lines (up to 36 in a row, where deleted blocks used to be) become one, and
    trailing whitespace goes.

The script checks what it claims: every script's sequence of non-comment tokens, every
stylesheet's text with comments and whitespace removed, and the markup outside them are the same
before and after. Only comments and whitespace changed."""
NAME = 'patch_phase120j.py'
BASE = '057bace32cd693546911f9e7186ecb3d82857217a86564ffb90a27737eb19909'
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


def recomment(old, new):
    """Replace one comment (it must occur exactly once). An empty replacement removes the comment
    and, when it stood alone on its lines, the lines too."""
    global t
    c = t.count(old)
    if c != 1:
        sys.exit('ABORT: comment found %d times: %r' % (c, old[:80]))
    s = t.index(old)
    e = s + len(old)
    if new == '':
        a = s
        while a > 0 and t[a - 1] in ' \t':
            a -= 1
        b = e
        while b < len(t) and t[b] in ' \t':
            b += 1
        if (a == 0 or t[a - 1] == '\n') and b < len(t) and t[b] == '\n':
            s, e = a, b + 1
    t = t[:s] + esc(new) + t[e:]


# ---- the top bar, the palette, the project tabs
recomment("// AutoCAD-style ribbon: clean QAT + tabs + panels. Reuses existing tool actions.\n", "")
recomment("""/* __acad3dV113: and WHEN it opens, which used to live in the retired whiteboard module.
       Ctrl+K opens it, Escape and a pointer outside it close it, and window.openPalette /
       window.closePalette stay published because the ribbon's command button calls them. */""",
"""/* __acad3dV113: Ctrl+K opens the palette; Escape, or a pointer outside it, closes it.
       window.openPalette and window.closePalette are what the suites drive. */""")
recomment("""(window.__a3dDocs); this section only draws it and passes clicks on.

     V114 had cut this down to one tab, because the whiteboard's "drawings" it inherited were never
     separate models. They are separate now. The Start page was also never seen: it sat at z-index
     9300 under the drawing area's 9500, so the Start tab lit up over a model that did not move --
     and V114's suite passed, because it read the 'show' class instead of what was on top. */""",
"""(window.__a3dDocs); this section only draws it and passes clicks on. */""")
recomment("""  /* __acad3dV117: the click-to-select and properties dock section is gone. It hit-tested
     whiteboard wires on every pointerdown in the document, looking for a viewport that V113c
     deleted; drew a right-hand Properties / Layers / Blocks dock for wires that the stylesheet hid
     in this app; inserted blocks into the whiteboard's state; and published a state hook that threw,
     reading the drawing list V114 deleted. The BIM engine's own Project Browser and Properties are
     the only ones. The blocks and dock state it stored ('acadBlocksV1', 'acadDockV1') are left where
     they are, unread -- deleting a user's stored data is not this patch's call. */
""", "")

# ---- the engine
recomment("// ---- __acad3dV18: canvas-mode entry hardening. Drafting/annotation is fundamentally a",
          "// ---- __acad3dV18: drafting-mode entry hardening. Drafting/annotation is fundamentally a")
recomment("""the prompt that advertises it cannot drift apart -- and the Canvas-era shortcut gate can
     ask this table rather than keeping a list of its own. */""",
"""the prompt that advertises it cannot drift apart. */""")
recomment("""/* A card's hatch is {angle, gap, cross} in the board's own terms; this app's pattern engine
     takes a NAMED pattern from BIM_HATCH_PATTERNS.""",
"""/* A card's hatch is {angle, gap, cross}; this app's pattern engine
     takes a NAMED pattern from BIM_HATCH_PATTERNS.""")
recomment("""/* Mixes a colour toward white. Used for ONE thing: turning a material's own swatch colour into
     a poche tint light enough for its hatch to read on top of. Deriving the tint is the only way
     to avoid inventing a second colour per card that the board would know nothing about. */""",
"""/* Mixes a colour toward white. Used for ONE thing: turning a material's own swatch colour into
     a poche tint light enough for its hatch to read on top of. Deriving the tint avoids a second
     colour per card that the library would have to keep in step. */""")
recomment("""/* patternColor is the card's colour UNCHANGED, which is what the 2D board already uses as its
       hatch stroke (wire.material.hatchColor = card.color). Keeping it identical is the point:
       the same material hatches the same colour in both engines. Only the fill underneath is
       derived, because the board draws no fill at all and a hatch with nothing behind it is
       invisible in a plan -- the wall poche is gated on fill!=='none'. */""",
"""/* patternColor is the card's colour UNCHANGED, so a material hatches in its own colour. Only
       the fill underneath is derived: a hatch with nothing behind it is invisible in a plan --
       the wall poche is gated on fill!=='none'. */""")
recomment("""     V80 removed the retired whiteboard's card/sticky library because it dragged onto a board that
     no longer exists. Removing something that did not work was right; leaving nothing in its place
     was not -- those assets are the annotation a drawing needs.
""", """     Notes, callouts and markers are the annotation a drawing needs.
""")
recomment("""     Inserted into the rendered rail rather than written into the whiteboard's template -- that
     template is a single-line string literal shared with a competing second sidebar
     implementation, and V80 already established this pass-over-the-shell pattern for exactly that
     reason. The same MutationObserver keeps the stack present across a re-render. */""",
"""     Inserted by the shell's render pass, which the panel's MutationObserver re-runs, so the stack
     is present across a re-render. */""")
recomment("""  // Operates on A3D.objs directly -- distinct from the pre-existing 2D CAD shell's own Trim/
  // Fillet/Offset/Mirror/Rotate, which run on its separate 2D "wire" object model and have no
  // reach into walls/rooms/etc. See the architectural note in Known Limitations. ----""",
"""  // Operates on A3D.objs directly. ----""")
recomment("""  // ---- __acad3dV32: Offset and Align for BIM objects. Until now Home's Offset/Align operated on
  // the 2D shell's separate wire model and had no reach into A3D.objs -- they appeared in the 3D
  // Modify tab only as disabled stubs. These are real implementations against BIM geometry.""",
"""  // ---- __acad3dV32: Offset and Align for BIM objects, against BIM geometry.""")
recomment("    // The file card described a whiteboard document. It now describes the project.\n",
          "    // The panel's header names the project and its site.\n")
recomment("""/* __acad3dV113b: the BIM shell owns its left rail and panel.

     Until now #a3d-shell was built by a canvas-era sidebar module and the BIM navigator
     was appended into its panel. Two workarounds in this file exist only because of that. V66:
     "the sidebar shell swallows clicks on .a3d-railbtn before they reach the button, so toggle
     the dock on capture-phase pointerdown instead". V80: four dead whiteboard blocks had to be
     cleaned out of the panel on a MutationObserver, because the module that drew them was
     retired as a workspace and never went back through the panel its code draws. Owning the
     shell means nothing dead is ever built, so there is nothing to clean.

     bimCleanShell stays and is called from here. It is no longer a cleanup -- it is the render
     pass for the file card, the V83 rail stack and the Assets tab, and it was already written to
     be idempotent, so calling it on a shell that is already correct costs one pass and changes
     nothing. */""",
"""/* __acad3dV113b: the BIM shell builds its own left rail and panel. bimCleanShell is their render
     pass -- the panel's header, the V83 rail stack and the Assets tab -- and it is idempotent, so
     running it on a shell that is already correct changes nothing. */""")
recomment("""/* __acad3dV85: the RAIL is watched too. It is a SIBLING of the panel, not a child, so a
       rail re-render never fired this observer -- which meant the cleanup pass that removes the
       dead "A?" button never ran on the one element it exists to remove. Measured: inject a
       .fl-help button into the rail and it was still there 900ms later. The panel was watched
       because that is where the retired Canvas blocks lived; the rail was simply never in
       scope. */""",
"""/* __acad3dV85: the RAIL is watched too. It is a SIBLING of the panel, not a child, so a
       rail re-render never fired this observer and the rail stack was not put back. */""")
recomment("""     Before this, "Drafting & Annotation" and "3D" were MODES chosen from a menu, and the label
     at the top of the ribbon reported the mode. It therefore read "Drafting & Annotation" while
     the camera sat in an isometric 3D view, which is what the user reported. Revit has no such
     concept: the Project Browser lists views, you open one, and the ribbon follows.
""", """     Revit's model: the Project Browser lists views, and you open one. There are no modes.
""")
recomment("""/* The name of a view, as the HUD and Properties' View row show it (__acad3dV119: the ribbon label
     that showed it went with the view dropdown). `sv` is the saved-view record, passed in rather
     than looked up again so a view deleted mid-activation cannot produce a blank label. */""",
"""/* The name of a view, as the HUD and Properties' View row show it. `sv` is the saved-view record,
     passed in rather than looked up again so a view deleted mid-activation cannot produce a blank
     label. */""")
recomment("""     reads -- so the two cannot disagree. The canvas-era strip this replaces kept its own list of
     "layouts" in localStorage and drew whiteboard wires on them; it was never shown in this app. */""",
"""     reads -- so the two cannot disagree. */""")
recomment("""         Escape already walks outwards -- dialog, constraint pick, sketch, section, plan,
         and finally out of the workspace entirely. A rail menu and an armed zoom window are
         the innermost things now, so they back out first. Measured before this: one Escape
         with a zoom window armed exited the whole BIM shell, and the V80 audit caught it by
         the retired-Canvas blocks reappearing the moment a3d-mode came off the body.
""", """         Escape walks outwards -- dialog, constraint pick, sketch, section, selection. A rail
         menu and an armed zoom window are the innermost things, so they back out first.
""")
recomment("""/* __acad3dV85: the chain STOPS here. It used to end:

             if(A3D.flat){toggleFlat();...}   // in a plan, Escape swung the camera into 3D
             exit3d();                        // in 3D, Escape closed the whole workspace

         Measured: one Escape in the 3D view with nothing open left the BIM workspace entirely --
         body lost 'a3d-mode' and the engine stopped. Both steps made sense while this was a MODE
         you were in and Escape meant "get me out of it". V84 retired that model: views are the
         navigation, and there is nothing sensible left to back out TO. Escape is also the most
         reflexive key in any drawing application, and that reflex should never close the
         workspace.

         Clearing the selection is the honest last step rather than an empty one -- it is what
         Escape does in Revit and in AutoCAD. Past that, Escape does nothing and says nothing. */""",
"""/* __acad3dV85: the chain STOPS here. Views are the navigation, so there is nothing to back
         out TO, and the most reflexive key in a drawing application should never close the
         workspace. Clearing the selection is the last step -- what Escape does in Revit and in
         AutoCAD. Past that, Escape does nothing and says nothing. */""")
recomment("""       It used to arrive here the long way round: the whiteboard shell's document listener called
       window.__ws3Del, which this engine wrapped. That ran after this handler had returned, outside
       every gate above, and two leaks were measured: with the Start page showing, Delete erased the
       selection of the project behind it; with a dialog open and the focus off its fields, Backspace
       erased the object the dialog sat over. Here it sits behind the gates -- the Start page, a
       sheet, a field, a gizmo value or a point being typed, and an open dialog (one gate since
       V118). Last before the nudge keys, where the old listener effectively ran. */""",
"""       It sits behind the gates -- the Start page, a sheet, a field, a gizmo value or a point being
       typed, and an open dialog (one gate since V118) -- so Delete cannot erase the selection of
       the project behind the Start page, or the object a dialog sits over. Last before the nudge
       keys. */""")
recomment("""  // Commands Revit has that this app does not implement yet. Listed so the ribbon shows the real
  // shape of the toolset, greyed out, rather than pretending the gap is not there.""",
"""  // Commands Revit has that this app does not implement yet. Listed so the tool dock shows the
  // real shape of the toolset, greyed out, rather than pretending the gap is not there.""")
recomment("""/* __acad3dV70: the floating tool dock, GENERATED from A3DR_TABS rather than hand-listed.
     That is the whole safety argument for retiring the ribbon in this workspace: a hand-built
     dock would quietly drop commands, and a command that exists but cannot be reached is the
     same failure as one that does not work. One group per ribbon TAB (nine groups over two
     rows, the reference tool's density); the group shows that tab's headline tools and its
     caret opens every action the tab has, still grouped under its panel headings.
     Buttons carry data-a3dr, so the existing document-level dispatcher wires them by
     construction -- this phase adds no new command routing at all. */""",
"""/* __acad3dV70: the floating tool dock, GENERATED from A3DR_TABS rather than hand-listed: a
     hand-built dock would quietly drop commands, and a command that exists but cannot be reached
     is the same failure as one that does not work. One group per registry TAB (nine groups over
     two rows, the reference tool's density); the group shows that tab's headline tools and its
     caret opens every action the tab has, grouped under its panel headings. Buttons carry
     data-a3dr, so the document-level dispatcher wires them by construction. */""")
recomment("""/* Every action a tab can reach, in ribbon order, grouped by panel and de-duplicated within
     the tab.""", """/* Every action a tab can reach, in registry order, grouped by panel and de-duplicated within
     the tab.""")
recomment("""  // the toolbar/ribbon itself be hidden (that's where the toggle control lives) -- same""",
          """  // the toolbar itself be hidden (that's where the toggle control lives) -- same""")
recomment("""  /* __acad3dV117: the 2D-chrome hider is gone. It hid the 2D workspace's status bar on entry and
     restored it on exit; nothing has built that bar since the whiteboard shell went, so it hid and
     restored nothing. */
""", "")
recomment("""/* __acad3dV117: this used to close the whiteboard dock's properties pop-out on entry, and to
       explain why two Properties panels must not show at once. That dock is deleted; the class
       below is what the rest of the stylesheet keys this workspace on. */""",
"""/* the class the rest of the stylesheet keys this workspace on */""")
recomment("""     Every entry here was driven before it was listed. A command with no BIM implementation is
     NOT in this table and therefore is not offered by the palette -- that is the point. The
     palette used to list 44 CAD commands and 9 canvas commands, every one of which dispatched
     into the retired Canvas whiteboard and did nothing. */""",
"""     Every entry here was driven before it was listed. A command with no BIM implementation is
     NOT in this table and therefore is not offered by the palette -- that is the point. */""")
recomment("""/* __acad3dV87. Three of these -- rotate, arrayRect, arrayPolar -- are not new work: the
       tools existed and ran from the ribbon, and the command line simply could not reach them
       because their registry rows still pointed at the retired whiteboard's acts. A working
       tool that no command can start is the same leftover as a control that no longer does
       anything, so they are wired here rather than left for a later phase to rediscover. */""",
"""/* __acad3dV87: rotate, arrayRect and arrayPolar, reachable from the command line. A working
       tool that no command can start is the same leftover as a control that no longer does
       anything. */""")
recomment("""/* __acad3dV95: the BIM toolset, reachable from the command line for the first time.
       Each of these already worked from the ribbon and from nowhere else. */""",
"""/* __acad3dV95: the BIM toolset, reachable from the command line. */""")
recomment("""/* __acad3dV115: the document commands. The quick-access bar's Save, Open, Undo, Redo and Plot
       carried these acts since the shell was built, and every one of them went into the retired
       whiteboard's dispatcher and did nothing. */""",
"""/* __acad3dV115: the document commands, which the quick-access bar's Save, Open, Undo, Redo and
       Plot run. */""")
recomment("""/* __acad3dV94: asked by the Canvas-era shortcut gate before it swallows a plain letter.
     True only when the drawing will actually consume it, so a letter the drafting engine does
     not want is still swallowed exactly as it was. */""",
"""/* __acad3dV94: whether the drawing will consume a plain letter -- true only when it will. The
     V94 suite asks it. */""")
recomment("""/* __acad3dV64: shell unification step 1-2. The three workspaces stacked rather than switched --
     #viewport (the Canvas board) stayed mounted and live under an opaque #acad3d in every mode,
     and the two surfaces disagreed about where the work area starts. Both now follow one
     contract. Test surface reports the measured shell geometry so a suite can assert the
     invariant rather than re-deriving it. */""",
"""/* __acad3dV64: the shell's measured geometry -- one work surface, and where it starts -- so a
     suite can assert the invariant rather than re-deriving it. */""")
recomment("""/* __acad3dV70: the safety surface for retiring the ribbon. __a3dRibbonActions is every action
     the ribbon registry can reach; __a3dDockActions is every action the rendered dock can reach.""",
"""/* __acad3dV70: __a3dRibbonActions is every action the tool registry (A3DR_TABS) can reach;
     __a3dDockActions is every action the rendered dock can reach.""")
recomment("""/* __acad3dV69: shared-material test surface. __a3dMaterialCards deliberately returns what the
     BIM SIDE can see, not a copy of the board's array, so a test can prove the two engines are
     reading one list rather than two that happen to match today. */""",
"""/* __acad3dV69: material test surface. __a3dMaterialCards returns the library itself, not a copy,
     so a test can prove every reader shares one list. */""")

# ---- whitespace: trailing blanks, and runs of blank lines become one
t = re.sub(r'[ \t]+\n', '\n', t)
t = re.sub(r'\n{3,}', '\n\n', t)


# ---- the proof that only comments and whitespace moved
def sig(text):
    """(script tokens without comments, style text without comments or whitespace, markup without
    comments or whitespace)."""
    toks, css, markup = [], [], []
    opener = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
    low = text.lower()
    i = prev = 0
    while True:
        m = opener.search(text, i)
        if not m:
            break
        markup.append(text[prev:m.start()])
        if m.group(0) == '<!--':
            i = prev = text.index('-->', m.end()) + 3
            continue
        tag = m.group(1).lower()
        e = low.index('</%s>' % tag, m.end())
        body = text[m.end():e]
        if tag == 'script':
            toks.append([body[a:b] for k, a, b in lex(body) if k != 'comment'])
        else:
            css.append(re.sub(r'\s+', '', re.sub(r'/\*.*?\*/', '', body, flags=re.S)))
        markup.append(m.group(0))
        i = prev = e + len(tag) + 3
    markup.append(text[prev:])
    return toks, css, re.sub(r'\s+', '', ''.join(markup))


a0, b0, c0 = sig(ORIG)
a1, b1, c1 = sig(t)
if a0 != a1:
    sys.exit('ABORT: a script token changed')
if b0 != b1:
    sys.exit('ABORT: a stylesheet changed beyond comments and whitespace')
if c0 != c1:
    sys.exit('ABORT: the markup changed')
print('only comments and whitespace changed: %d script blocks, %d stylesheets' % (len(a1), len(b1)))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
