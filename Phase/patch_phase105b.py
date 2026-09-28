#!/usr/bin/env python3
"""patch_phase105b.py -- V105 occupant load in Properties: Occupancy offers the IBC functions
(still free text), Load Factor shows the default it overrides, and an Occupant Load row reads
the same two functions the schedule does. A Tab between room fields keeps the focus: the V101
change handler rebuilt the panel at once and dropped it."""
NAME = 'patch_phase105b.py'
BASE = '9150f3bd8fb1d7f45785c65da3bd7ed2ebad1514c60dde96a1a0950c96568686'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)
rep(r"""    return Math.ceil(o.area/f.m2-1e-9);
  }
""", r"""    return Math.ceil(o.area/f.m2-1e-9);
  }
  /* __acad3dV105: the Properties side of occupant load. All of it reads the two functions the
     schedule reads, so the panel and the schedule cannot disagree. */
  function bimRoomLoadFactorHint(o){
    var row=bimOccLoadRow(o&&o.occupancy);
    return row?(row.m2.toFixed(2)+' IBC default ('+row.ft2+' sq ft '+row.basis+')'):'none: pick an IBC Occupancy or type a factor';
  }
  function bimRoomOccupantsText(o){
    var f=bimRoomLoadFactor(o),n=bimRoomOccupants(o);
    if(!f)return 'no load factor';
    return (n===null?'-':String(n))+' at '+f.m2.toFixed(2)+' m²/person'+(f.basis?' '+f.basis:'')+' ('+f.src+')';
  }
  function bimOccDatalist(){
    var h='<datalist id="bimOccList">',i;
    for(i=0;i<BIM_OCC_LOADS.length;i++)h+='<option value="'+bimEsc(BIM_OCC_LOADS[i][0])+'">'+BIM_OCC_LOADS[i][1]+' sq ft '+BIM_OCC_LOADS[i][2]+'</option>';
    return h+'</datalist>';
  }
""")
rep(r"""        var rrow=bimPropRow(rf.label,'<input type="text" data-roomf="'+rf.k+'" value="'+bimEsc(bimRoomField(o,rf.k))+'">');
""", r"""        /* __acad3dV105: Occupancy offers the IBC functions and stays free text -- a name not in the
           table is the owner's own; Load Factor shows the default it would override. */
        var rext=rf.k==='occupancy'?' list="bimOccList"':(rf.k==='loadFactor'?' placeholder="'+bimEsc(bimRoomLoadFactorHint(o))+'"':'');
        var rrow=bimPropRow(rf.label,'<input type="text" data-roomf="'+rf.k+'"'+rext+' value="'+bimEsc(bimRoomField(o,rf.k))+'">'+(rf.k==='occupancy'?bimOccDatalist():''));
""")
rep(r"""        if(rf.grp==='fin')finRows+=rrow;else idd+=rrow;
      }
    }
""", r"""        if(rf.grp==='fin')finRows+=rrow;else idd+=rrow;
      }
      idd+=bimPropRow('Occupant Load','<span data-roomload="'+bimEsc(o.id)+'">'+bimEsc(bimRoomOccupantsText(o))+'</span>');   /* __acad3dV105 */
    }
""")
rep(r"""        a3dToast('That room field could not be changed - see the console');
      }
      refreshProps();
    });
""", r"""        a3dToast('That room field could not be changed - see the console');
      }
      /* __acad3dV105: rebuild once the focus has settled, then put the cursor where the user sent
         it -- the field a Tab or Enter was aimed at. The edit rebuilds the panel before the
         browser moves the focus, so a Tab from Occupancy to Load Factor -- the way these two are
         filled in -- used to leave the cursor nowhere. */
      setTimeout(function(){
        var ae=document.activeElement,k=A3D.roomFieldNext||((ae&&ae.getAttribute)?ae.getAttribute('data-roomf'):null),n;
        A3D.roomFieldNext=null;
        refreshProps();
        if(k&&el.propsbody){n=el.propsbody.querySelector('[data-roomf="'+k+'"]');if(n)n.focus();}
      },0);
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){   /* __acad3dV105: where Tab / Enter was aimed */
      if(ev.key!=='Tab'&&ev.key!=='Enter')return;
      var ri=ev.target&&ev.target.closest?ev.target.closest('[data-roomf]'):null;
      if(!ri)return;
      var all=Array.prototype.slice.call(el.propsbody.querySelectorAll('[data-roomf]')),i=all.indexOf(ri);
      var nx=ev.key==='Enter'?ri:all[i+(ev.shiftKey?-1:1)];
      A3D.roomFieldNext=nx?nx.getAttribute('data-roomf'):null;
      setTimeout(function(){A3D.roomFieldNext=null;},60);   /* no edit, no change event: forget it */
    });
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
