#!/usr/bin/env python3
"""V167g: the Standards group as a person uses it -- what the suite found.

- What is typed in the place's fields and an override's value and reason is kept as it is typed:
  Properties is drawn again when a field changes (moving from the country to the region did it), and
  the fields came back empty. Each is kept in a draft until Save or Cancel, as the address is (V149c).
- On a phone or a tablet STANDARDS, and a pack being looked at, open the Properties sheet (V151's way).
- An edition from a pack, adopted for a place, is in force there, not the app's own assumption: a
  topic of the app's assumptions said 'the app's assumption' for any edition.
- The same pack a second time is said to be applied already, before its editions are found to be in
  the registry: the reason was the wrong one.

Run from the repository root: python3 Phase/patch_phase167g.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '36c535ae831bd79ade12d1f4506521e239c0df6d0b0296182f4b419c19be4ed4'   # after patch_phase167f.py

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


# ---- the drafts ----
rep("  var A3D_STD_UI={open:{},edit:null,place:false,pending:null};\n",
    "  var A3D_STD_UI={open:{},edit:null,place:false,pending:null,draft:{}};\n"
    "  /* __acad3dV167g: what is typed in the place's and an override's fields, until Save or Cancel */\n"
    "  var BIM_STD_DRAFT_KEYS={cc:1,r:1,d8:1,city:1,ovv:1,ovwhy:1};\n"
    "  function bimStdDraft(k,d){var D=A3D_STD_UI.draft;return D&&D.hasOwnProperty(k)?D[k]:d;}\n"
    "  function bimStdDraftClear(keys){keys.forEach(function(k){delete A3D_STD_UI.draft[k];});}\n")
rep("<input type=\"number\" step=\"any\" data-propstd=\"ovv\" value=\"'+bimEsc(String(o?o.v:x.v))+'\"",
    "<input type=\"number\" step=\"any\" data-propstd=\"ovv\" value=\"'+bimEsc(bimStdDraft('ovv',String(o?o.v:x.v)))+'\"")
rep("'<input type=\"text\" data-propstd=\"ovwhy\" value=\"'+bimEsc(o?o.why:'')+'\"",
    "'<input type=\"text\" data-propstd=\"ovwhy\" value=\"'+bimEsc(bimStdDraft('ovwhy',o?o.why:''))+'\"")
rep("'<input type=\"text\" data-propstd=\"cc\" value=\"'+bimEsc((q.cc||'').toUpperCase())+'\"",
    "'<input type=\"text\" data-propstd=\"cc\" value=\"'+bimEsc(bimStdDraft('cc',(q.cc||'').toUpperCase()))+'\"")
rep("'<input type=\"text\" data-propstd=\"r\" value=\"'+bimEsc((q.r||'').toUpperCase())+'\"",
    "'<input type=\"text\" data-propstd=\"r\" value=\"'+bimEsc(bimStdDraft('r',(q.r||'').toUpperCase()))+'\"")
rep("'<input type=\"text\" data-propstd=\"d8\" value=\"'+bimEsc((q.d8||q.d6||'').toUpperCase())+'\"",
    "'<input type=\"text\" data-propstd=\"d8\" value=\"'+bimEsc(bimStdDraft('d8',(q.d8||q.d6||'').toUpperCase()))+'\"")
rep("'<input type=\"text\" data-propstd=\"city\" value=\"'+bimEsc(q.city||'')+'\"",
    "'<input type=\"text\" data-propstd=\"city\" value=\"'+bimEsc(bimStdDraft('city',q.city||''))+'\"")
rep("    return true;   /* the place's and an override's fields are read by Save */\n",
    "    if(BIM_STD_DRAFT_KEYS[k])A3D_STD_UI.draft[k]=f.value;\n"
    "    return true;   /* the place's and an override's fields are read by Save */\n")
P = ['cc', 'r', 'd8', 'city']
rep("    if(c==='place'){U.place=true;refreshProps();return true;}\n"
    "    if(c==='placecancel'){U.place=false;refreshProps();return true;}\n"
    "    if(c==='placeclear'){U.place=false;bimStdSetPlace(null);return true;}\n",
    "    if(c==='place'){U.place=true;bimStdDraftClear(['cc','r','d8','city']);refreshProps();return true;}\n"
    "    if(c==='placecancel'){U.place=false;bimStdDraftClear(['cc','r','d8','city']);refreshProps();return true;}\n"
    "    if(c==='placeclear'){U.place=false;bimStdDraftClear(['cc','r','d8','city']);bimStdSetPlace(null);return true;}\n")
rep("      if(bimStdSetPlace({cc:cc,r:bimStdPropVal('r'),d8:d,city:bimStdPropVal('city'),ccn:'',rn:''},'hand'))U.place=false;\n",
    "      if(bimStdSetPlace({cc:cc,r:bimStdPropVal('r'),d8:d,city:bimStdPropVal('city'),ccn:'',rn:''},'hand')){U.place=false;bimStdDraftClear(['cc','r','d8','city']);}\n")
rep("    if(c==='open'){U.open[v]=!U.open[v];if(!U.open[v]&&U.edit&&U.edit.indexOf(v+'|')===0)U.edit=null;refreshProps();return true;}\n"
    "    if(c==='ov'){U.edit=v;refreshProps();",
    "    if(c==='open'){U.open[v]=!U.open[v];if(!U.open[v]&&U.edit&&U.edit.indexOf(v+'|')===0){U.edit=null;bimStdDraftClear(['ovv','ovwhy']);}refreshProps();return true;}\n"
    "    if(c==='ov'){U.edit=v;bimStdDraftClear(['ovv','ovwhy']);refreshProps();")
rep("    if(c==='ovcancel'){U.edit=null;refreshProps();return true;}\n"
    "    if(c==='ovsave'){j=v.indexOf('|');if(bimStdOverride(v.slice(0,j),v.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy')))U.edit=null;refreshProps();return true;}\n",
    "    if(c==='ovcancel'){U.edit=null;bimStdDraftClear(['ovv','ovwhy']);refreshProps();return true;}\n"
    "    if(c==='ovsave'){j=v.indexOf('|');if(bimStdOverride(v.slice(0,j),v.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy'))){U.edit=null;bimStdDraftClear(['ovv','ovwhy']);}refreshProps();return true;}\n")
rep("      try{var j=A3D_STD_UI.edit.indexOf('|');if(bimStdOverride(A3D_STD_UI.edit.slice(0,j),A3D_STD_UI.edit.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy')))A3D_STD_UI.edit=null;refreshProps();}",
    "      try{var j=A3D_STD_UI.edit.indexOf('|');if(bimStdOverride(A3D_STD_UI.edit.slice(0,j),A3D_STD_UI.edit.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy'))){A3D_STD_UI.edit=null;bimStdDraftClear(['ovv','ovwhy']);}refreshProps();}")
rep("    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){\n"
    "      try{bimStdPropClick(ev);}",
    "    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){   /* __acad3dV167g: the drafts, as typed */\n"
    "      var f=ev.target&&ev.target.closest?ev.target.closest('[data-propstd]'):null,k=f&&f.getAttribute('data-propstd');\n"
    "      if(k&&BIM_STD_DRAFT_KEYS[k])A3D_STD_UI.draft[k]=f.value;\n"
    "    });\n"
    "    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){\n"
    "      try{bimStdPropClick(ev);}")

# ---- the sheet on a phone or a tablet ----
rep("  function bimStdCommand(){\n"
    "    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];\n"
    "    bimPropReveal('Standards');\n",
    "  function bimStdSheet(){if(bimShellOverlay()){var rp=document.getElementById('a3d-right');if(rp)rp.classList.add('open');}}   /* __acad3dV167g: V151's way */\n"
    "  function bimStdCommand(){\n"
    "    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];\n"
    "    bimPropReveal('Standards');bimStdSheet();\n")
rep("    bimPropReveal('Standards');refreshProps();\n    var D=A3D_STD_UI.pending.diff;",
    "    bimPropReveal('Standards');bimStdSheet();refreshProps();\n    var D=A3D_STD_UI.pending.diff;")

# ---- a pack's edition of an assumption ----
rep("      if(best)r={ed:best.e,how:rec.kind==='assumption'?'assumption':(path[i].k==='*'?'international':'adopted'),at:path[i],a:best.a};",
    "      if(best)r={ed:best.e,how:rec.kind==='assumption'&&!best.e.pack?'assumption':(path[i].k==='*'?'international':'adopted'),at:path[i],a:best.a};   /* __acad3dV167g: a pack's edition is adopted */")

# ---- the same pack again ----
rep("  function bimStdPackDiff(text){\n"
    "    var R=bimStdPackParse(text);\n"
    "    if(R.err)return {ok:false,err:R.err};\n"
    "    var S=bimStdS(),ts=R.pack.topics.map(function(t){return t.id;}),was={},now={},i;\n"
    "    if((S.packs||[]).some(function(p){return p.sha===R.sha;}))return {ok:false,err:'This pack is already applied to the project',sha:R.sha};\n",
    "  function bimStdPackDiff(text){\n"
    "    var t0=String(text==null?'':text),S=bimStdS(),sh=t0.length<=BIM_STD_PACK_MAX?bimSha256(t0):'';\n"
    "    /* __acad3dV167g: the same file again is said as such, before its editions are found in the registry already */\n"
    "    if(sh&&(S.packs||[]).some(function(p){return p.sha===sh;}))return {ok:false,err:'This pack is already applied to the project',sha:sh};\n"
    "    var R=bimStdPackParse(text);\n"
    "    if(R.err)return {ok:false,err:R.err};\n"
    "    var ts=R.pack.topics.map(function(t){return t.id;}),was={},now={},i;\n")

# ---- the marker ----
rep("framestd,refill,touchsizes';", "framestd,refill,touchsizes,drafts,sheet,packadopted,packagain';")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
