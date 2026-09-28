"""patch_phase101h.py -- __acad3dV101: the tag writes m-squared the way the room label does.
Seen on the first screenshot: the tag said "30.00 m2" beside a label saying "42.00 m(sq)". The
exports keep plain "m2" (R12 DXF is ASCII); the canvas uses the same unit mark everywhere."""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '8b11d1b53c8174a2ec8b65254cd29d93509806dde1a5ddf53c775a80c858e4be'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = """    if(o.showArea!==false)lines.push({t:(r.area||0).toFixed(2)+' m2',font:'10px system-ui,sans-serif',col:'#9ec1ff'});"""
NEW = """    if(o.showArea!==false)lines.push({t:(r.area||0).toFixed(2)+' m\\u00b2',font:'10px system-ui,sans-serif',col:'#9ec1ff'});"""
assert txt.count(OLD) == 1
txt = txt.replace(OLD, NEW, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
