"""patch_phase103d.py -- __acad3dV103: Fit and Zoom to Selection see property lines.

Found by the suite: Fit framed the model and left the parcel off-screen. bimWorldBounds measures
objects with a mesh or a point list, and a property has neither -- its corners are derived. The
same gap covered text labels and room tags (a single insertion point). All three now contribute.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '45603756b54becb43541da8fc36ab4cfec7ec22edcfeb920377453a288dbea28'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = """          any=true;
        }
      }
    }
    return any?{mn:mn,mx:mx}:null;
  }"""
NEW = """          any=true;
        }
      }else if(bimIsProperty(o)||((o.t==='text'||o.t==='roomtag')&&o.pt)){
        /* __acad3dV103: derived corners (property) or one insertion point (text, tag) */
        var extra=bimIsProperty(o)?bimPropertyGeometry(o).ring.map(function(p){return [p[0],(o.y||0)+q[1],p[1]];})
                                  :[bimWorldPt(o,o.pt,o.y||0)];
        for(j=0;j<extra.length;j++){
          for(k=0;k<3;k++){
            if(extra[j][k]<mn[k])mn[k]=extra[j][k];
            if(extra[j][k]>mx[k])mx[k]=extra[j][k];
          }
          any=true;
        }
      }
    }
    return any?{mn:mn,mx:mx}:null;
  }"""
assert txt.count(OLD) == 1, txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
