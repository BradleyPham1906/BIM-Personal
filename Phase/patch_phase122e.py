"""patch_phase122e.py -- V122: the set, printed -- every page in one print job, for a PDF.

A presentation goes to the client afterwards, and what a client is sent is a PDF. The browser's
print dialog makes one (Save as PDF); what it was given was one sheet at a time. Print set sends every
page in the project's order as one document: each page the vector sheet (bimBuildSheetSVG, as Print
has drawn one sheet since V57), in the appearance chosen, on paper of its own size -- a named @page per
size, so an A3 page between two ANSI B pages prints on A3. A page whose vector drawing fails is printed
from its image instead and the presenter is told which, rather than the set stopping at it.

It is on the Pages display's bar (V122c) and on the Presentation panel (V122f)."""
NAME = 'patch_phase122e.py'
BASE = '167794ec0fd4c2f5ed368601d4c40ac629badda875efa293ead642239a1b2fab'
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

# ---- the button, on the Pages bar
rep("""          '<select id="a3d-pgzoom" class="a3d-pgonly a3d-pgzoom" aria-label="Zoom"></select>'+
""", """          '<select id="a3d-pgzoom" class="a3d-pgonly a3d-pgzoom" aria-label="Zoom"></select>'+
          '<button class="a3d-btn a3d-pgonly" id="a3d-pgprint" title="Print every page in one go -- Save as PDF in the print dialog makes the client\\'s PDF">Print set</button>'+   /* __acad3dV122 */
""")
rep("""    var sheetPresentBtn=root.querySelector('#a3d-sheetpresent');
""", """    var pgPrintBtn=root.querySelector('#a3d-pgprint');
    if(pgPrintBtn)pgPrintBtn.addEventListener('click',function(){bimPrintSet();});   /* __acad3dV122 */
    var sheetPresentBtn=root.querySelector('#a3d-sheetpresent');
""")

# ---- the set
rep("""  function bimPrintSheet(){
""", """  /* __acad3dV122: every page in the project's order, one print job -- the print dialog's Save as PDF
     makes the document a client is sent. Each page is the vector sheet on paper of its own size: a
     named @page per size (the first size is also the plain @page, for a browser without named
     pages). A page whose vector build fails goes in as its image, and the presenter is told. */
  function bimPrintSetHtml(){
    var n=A3D.sheets.length,mode=A3D.presentMode?'presentation':'technical',sizes={},css='',body='',bad=[],i,s,nm,svg,cv;
    for(i=0;i<n;i++){
      s=A3D.sheets[i];
      nm='a3dsz'+String(s.w.toFixed(1)+'x'+s.h.toFixed(1)).replace(/[^0-9x]/g,'_');
      if(!sizes[nm]){
        sizes[nm]=1;
        if(i===0)css+='@page{size:'+s.w+'mm '+s.h+'mm;margin:0}';
        css+='@page '+nm+'{size:'+s.w+'mm '+s.h+'mm;margin:0}';
      }
      try{svg=bimBuildSheetSVG(s,mode);}
      catch(eS){
        console.warn('[BIM] Page '+(i+1)+' could not be built as a vector drawing; it is printed from its image',eS);
        bad.push(i+1);
        try{
          cv=bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,document.createElement('canvas'),SHEET_EXPORT_PXMM/SHEET_PREVIEW_PXMM);
          svg='<img alt="" src="'+cv.toDataURL('image/png')+'">';
        }catch(eR){
          console.warn('[BIM] Page '+(i+1)+' could not be drawn at all',eR);
          svg='<div class="a3dpgerr">Page '+(i+1)+' ('+bimEsc(bimSheetLabel(s))+') could not be drawn</div>';
        }
      }
      body+='<div class="a3dpg" data-page="'+bimEsc(s.id)+'" style="page:'+nm+';width:'+s.w+'mm;height:'+s.h+'mm">'+svg+'</div>';
    }
    var html='<html><head><title>'+bimEsc(bimProjectLabel())+' - '+n+' page'+(n===1?'':'s')+'</title><style>'+css+
      'body{margin:0}.a3dpg{break-after:page;page-break-after:always;overflow:hidden}.a3dpg:last-child{break-after:auto;page-break-after:auto}'+
      '.a3dpg svg,.a3dpg img{width:100%;height:100%;display:block}.a3dpgerr{padding:20mm;font:14pt sans-serif;color:#c33}'+
      '</style></head><body>'+body+'<script>window.onload=function(){window.focus();window.print();};<\\/script></body></html>';
    return {html:html,bad:bad,n:n};
  }
  function bimPrintSet(){
    if(!A3D.sheets.length){a3dToast('There are no pages to print yet: every sheet is a page');return false;}
    var r;
    try{r=bimPrintSetHtml();}
    catch(eB){console.warn('[BIM] The set could not be put together for printing',eB);a3dToast('The set could not be printed -- see the console');return false;}
    var w=window.open('','_blank');
    if(!w){a3dToast('The print window was blocked -- allow pop-ups for this page and try again');return false;}
    try{w.document.write(r.html);w.document.close();}
    catch(eW){console.warn('[BIM] The print window could not be written',eW);a3dToast('The set could not be printed -- see the console');return false;}
    if(r.bad.length)a3dToast('Page'+(r.bad.length>1?'s ':' ')+r.bad.join(', ')+' printed from '+(r.bad.length>1?'their images':'its image')+': the vector drawing failed -- see the console');
    else a3dToast('Printing '+r.n+' page'+(r.n===1?'':'s')+' -- Save as PDF in the print dialog makes a PDF');
    return true;
  }
  function bimPrintSheet(){
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
