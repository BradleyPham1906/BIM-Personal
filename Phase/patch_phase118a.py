"""patch_phase118a.py -- V118: Properties keeps the focus through its own rebuild.

Properties re-rendered by assigning innerHTML, which replaces every element in the panel. Replacing
the element that has the focus drops the focus to the page, and on the page the next key is the
model's: with the wall's Type dropdown focused, ArrowDown stepped the type (117f), the change
re-rendered the panel, and a second ArrowDown moved the wall a metre. A Tab in Model Properties
landed nowhere, and a click from one room field into another was lost. V105 patched the Tab for
room fields alone. This adds the one way to re-render a panel the user may be working in -- the new
markup is built off the document and the live panel brought into line with it, so an element that
is still there keeps its identity, its focus and its caret -- and Properties renders through it."""
NAME = 'patch_phase118a.py'
BASE = 'a3525cef68f0b81342ef17c3299eeade3386b1b0c16a5545c7e64fb807608dea'
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
rep("  function refreshProps(){\n",
    r'''  /* __acad3dV118: the one way to re-render a panel the user may be working in.

     Assigning innerHTML replaces every element in a panel, the focused one included, and the focus
     falls to the page -- where the next key belongs to the model. With the wall's Type dropdown
     focused, ArrowDown stepped the type, the change re-rendered Properties, and the second ArrowDown
     moved the wall a metre. A Tab in Model Properties landed nowhere; a click from one field into
     another was lost, the element clicked being gone before the mouse came up.

     Here the new markup is parsed off the document and the live panel is brought into line with it,
     element by element. An element that is still there keeps its identity -- its focus, its caret,
     an open dropdown -- and only what differs is touched. Elements are matched by what they are: an
     id or their data-* attributes, or, for a container with neither, those of the first element
     inside it that has them; anything else by position. The result is the markup, attribute for
     attribute, and every field shows the value the markup gives it, as innerHTML did. If the focused
     element had to be moved or rebuilt, the focus and the caret are put back on it by the same key. */
  function bimOwnKey(n){
    if(!n||n.nodeType!==1)return null;
    if(n.id)return n.nodeName+'#'+n.id;
    var a=n.attributes,i,k=[];
    for(i=0;i<a.length;i++)if(a[i].name.indexOf('data-')===0)k.push(a[i].name+'='+a[i].value);
    return k.length?(n.nodeName+'['+k.sort().join('|')+']'):null;
  }
  function bimMorphKey(n){
    var k=bimOwnKey(n),c;
    if(k!==null||!n||n.nodeType!==1)return k;
    for(c=n.firstElementChild;c;c=c.nextElementSibling){
      k=bimMorphKey(c);
      if(k!==null)return n.nodeName+'>'+k;
    }
    return null;
  }
  function bimMorphKids(live,next){
    var pool={},need={},c,k,cur,nn,nx,m;
    for(c=live.firstChild;c;c=c.nextSibling){
      k=bimMorphKey(c);
      if(k!==null)(pool[k]=pool[k]||[]).push(c);
    }
    for(c=next.firstChild;c;c=c.nextSibling){k=bimMorphKey(c);if(k!==null)need[k]=(need[k]||0)+1;}
    cur=live.firstChild;
    for(nn=next.firstChild;nn;nn=nx){
      nx=nn.nextSibling;
      /* a keyed element that nothing still to come wants is gone: remove it here, rather than move
         everything after it past it -- a moved element loses the focus */
      while(cur&&(k=bimMorphKey(cur))!==null&&!need[k]){m=cur.nextSibling;live.removeChild(cur);cur=m;}
      k=bimMorphKey(nn);m=null;
      if(k!==null){need[k]--;if(pool[k]&&pool[k].length)m=pool[k].shift();}
      else if(cur&&bimMorphKey(cur)===null&&cur.nodeType===nn.nodeType&&cur.nodeName===nn.nodeName)m=cur;
      if(!m){live.insertBefore(nn,cur);continue;}   /* new: it leaves the parsed markup for the panel */
      /* unkeyed nodes between here and the match go, rather than the match being moved past them */
      while(cur&&cur!==m&&bimMorphKey(cur)===null){c=cur.nextSibling;live.removeChild(cur);cur=c;}
      if(m===cur)cur=cur.nextSibling;
      else live.insertBefore(m,cur);                 /* a true reorder: kept, and moved into its place */
      bimMorphNode(m,nn);
    }
    while(cur){nx=cur.nextSibling;live.removeChild(cur);cur=nx;}
  }
  function bimMorphNode(a,b){
    if(a.nodeType!==1){if(a.nodeValue!==b.nodeValue)a.nodeValue=b.nodeValue;return;}
    var i,n,aa=a.attributes,ba=b.attributes;
    for(i=aa.length-1;i>=0;i--){n=aa[i].name;if(!b.hasAttribute(n))a.removeAttribute(n);}
    for(i=0;i<ba.length;i++){n=ba[i].name;if(a.getAttribute(n)!==ba[i].value)a.setAttribute(n,ba[i].value);}
    bimMorphKids(a,b);
    /* the markup's value, as innerHTML gave it -- a rejected edit shows the model's value again */
    if(a.nodeName==='INPUT'){
      if(a.type==='checkbox'||a.type==='radio'){if(a.checked!==b.checked)a.checked=b.checked;}
      else if(a.type!=='file'&&a.value!==b.value)a.value=b.value;
    }else if(a.nodeName==='TEXTAREA'){
      if(a.value!==b.value)a.value=b.value;
    }else if(a.nodeName==='SELECT'){
      for(i=0;i<a.options.length&&i<b.options.length;i++)
        if(a.options[i].selected!==b.options[i].selected)a.options[i].selected=b.options[i].selected;
    }
  }
  function bimFindByKey(host,k){
    if(k===null)return null;
    var all=host.getElementsByTagName('*'),i;
    for(i=0;i<all.length;i++)if(bimOwnKey(all[i])===k)return all[i];
    return null;
  }
  function bimRenderInto(host,html){
    if(!host)return;
    var a=document.activeElement,keep=null,t,s;
    if(a&&a!==document.body&&host.contains(a)){
      keep={el:a,key:bimOwnKey(a),v:a.value,s:null,e:null,d:null};
      try{if(typeof a.selectionStart==='number'){keep.s=a.selectionStart;keep.e=a.selectionEnd;keep.d=a.selectionDirection;}}
      catch(eS){}
    }
    try{
      t=document.createElement('template');
      t.innerHTML=html;
      bimMorphKids(host,t.content);
    }catch(eM){
      console.warn('[BIM] A panel update fell back to a full redraw.',eM);
      a3dToast('A panel was redrawn in full; the focus may have moved');
      host.innerHTML=html;
    }
    if(!keep)return;
    s=keep.el;
    if(!host.contains(s))s=bimFindByKey(host,keep.key);
    if(!s||document.activeElement===s)return;
    try{s.focus({preventScroll:true});}catch(eF){}
    if(keep.s!==null&&s.value===keep.v){try{s.setSelectionRange(keep.s,keep.e,keep.d||'none');}catch(eR){}}
  }
  window.__a3dRenderInto=bimRenderInto;   /* the helper's own contract is tested directly, reorders included */
  function refreshProps(){
''')
rep("    if(gP){el.propsbody.innerHTML=bimGridPropsHtml(gP);return;}\n",
    "    if(gP){bimRenderInto(el.propsbody,bimGridPropsHtml(gP));return;}   /* __acad3dV118 */\n")
rep("      el.propsbody.innerHTML=bimModelPropsHtml();\n",
    "      bimRenderInto(el.propsbody,bimModelPropsHtml());   /* __acad3dV118 */\n")
rep("    el.propsbody.innerHTML=h;\n  }\n",
    "    bimRenderInto(el.propsbody,h);   /* __acad3dV118: the panel keeps the focus through its own rebuild */\n  }\n")
if 'propsbody.innerHTML' in t:
    sys.exit('ABORT: Properties is still rendered by replacing its elements')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
