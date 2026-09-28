"""patch_phase103.py -- __acad3dV103: property lines entered as a survey -- the math.

First phase of the site track. A civil engineer describes a parcel the way the deed does: a
point of beginning, then legs of BEARING and DISTANCE -- N 45 30 00 E 120.00 -- around to the
start. This patch is the arithmetic, kept in small pure functions so each can be checked:

  bimParseBearing / bimFormatBearing   quadrant bearings <-> azimuth, with seconds
  bimParseLegs                         "BEARING DISTANCE" per line, errors by line number
  bimTraverse                          legs -> points, misclosure, precision, perimeter, area
  bimLegsFromRing                      a drawn closed shape -> the legs that describe it
  bimSetbackRing                       each side offset inward by its own setback, mitred

Bearings are TRUE bearings. The site's True North angle (Revit's name for it: the angle from
project north to true north, clockwise) rotates every traverse, so a parcel entered from a deed
lands correctly on a plan drawn square to the building. Project north is up on the plan (-Z).
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '44b5fa28178de66f87bcfc4c3b4f30957864385e6ec0bba184cfbdd598ce4f6b'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

FN = r"""  /* ================= __acad3dV103: survey arithmetic ================= */
  function bimTrueNorthDeg(){
    var t=A3D.site&&A3D.site.trueNorth;
    return isFinite(t)?+t:0;
  }
  /* "N 45 30 00 E", "N45-30-00E", "N 45.5 E", with or without degree/minute/second marks.
     Returns the azimuth in degrees clockwise from north, or {error}. */
  function bimParseBearing(s){
    var str=String(s==null?'':s).replace(/[°'"dms]/gi,function(c){return /[NSEW]/i.test(c)?c:' ';}).replace(/-/g,' ');
    var m=/^\s*([NS])\s*(\d+(?:\.\d+)?)(?:\s+(\d+(?:\.\d+)?))?(?:\s+(\d+(?:\.\d+)?))?\s*([EW])\s*$/i.exec(str);
    if(!m)return {error:'not a bearing (expected like N 45 30 00 E)'};
    var deg=parseFloat(m[2]),mi=m[3]?parseFloat(m[3]):0,se=m[4]?parseFloat(m[4]):0;
    if(mi>=60||se>=60)return {error:'minutes and seconds must be under 60'};
    if((m[3]&&Math.floor(deg)!==deg)||(m[4]&&Math.floor(mi)!==mi))return {error:'only the last part of a bearing can have decimals'};
    var a=deg+mi/60+se/3600;
    if(a>90)return {error:'a quadrant bearing is 90 degrees at most'};
    var ns=m[1].toUpperCase(),ew=m[5].toUpperCase(),az;
    if(ns==='N'&&ew==='E')az=a;
    else if(ns==='S'&&ew==='E')az=180-a;
    else if(ns==='S'&&ew==='W')az=180+a;
    else az=360-a;
    az=((az%360)+360)%360;
    return {az:az};
  }
  /* Azimuth -> quadrant bearing, rounded to the second. deg is the degree mark to use: the
     canvas takes the real mark, an R12 DXF takes %%d. */
  function bimFormatBearing(az,deg){
    az=((az%360)+360)%360;
    var ns,ew,a;
    if(az<=90){ns='N';ew='E';a=az;}
    else if(az<=180){ns='S';ew='E';a=180-az;}
    else if(az<=270){ns='S';ew='W';a=az-180;}
    else{ns='N';ew='W';a=360-az;}
    var tot=Math.round(a*3600),d=Math.floor(tot/3600),mi=Math.floor((tot%3600)/60),se=tot%60;
    function p2(n){return (n<10?'0':'')+n;}
    return ns+' '+d+(deg===undefined?'°':deg)+p2(mi)+"'"+p2(se)+'" '+ew;
  }
  /* One leg per line: BEARING DISTANCE. Blank lines are skipped. Every bad line is reported. */
  function bimParseLegs(text){
    var lines=String(text||'').split(/\r?\n/),legs=[],errs=[],i,ln,m,b,d;
    for(i=0;i<lines.length;i++){
      ln=lines[i].replace(/^\s+|\s+$/g,'');
      if(!ln)continue;
      m=/^(.*?)\s+(-?\d+(?:\.\d+)?)\s*(?:m)?$/i.exec(ln);
      if(!m){errs.push('line '+(i+1)+': expected a bearing then a distance');continue;}
      b=bimParseBearing(m[1]);d=parseFloat(m[2]);
      if(b.error){errs.push('line '+(i+1)+': '+b.error);continue;}
      if(!(d>0)){errs.push('line '+(i+1)+': the distance must be positive');continue;}
      legs.push({b:bimFormatBearing(b.az,' '),az:b.az,d:d});
    }
    if(!errs.length&&legs.length<3)errs.push('a parcel needs at least 3 legs');
    return {legs:legs,errors:errs};
  }
  /* Legs -> WORLD plan points from start, rotated by True North. Project north is -Z. */
  function bimTraverse(start,legs,tnDeg){
    var tn=(isFinite(tnDeg)?tnDeg:bimTrueNorthDeg())*Math.PI/180;
    var pts=[[start[0],start[1]]],x=start[0],z=start[1],per=0,i,az;
    for(i=0;i<legs.length;i++){
      az=legs[i].az*Math.PI/180+tn;
      x+=legs[i].d*Math.sin(az);z-=legs[i].d*Math.cos(az);
      per+=legs[i].d;
      pts.push([x,z]);
    }
    var ex=x-start[0],ez=z-start[1],mis=Math.sqrt(ex*ex+ez*ez);
    var ring=pts.slice(0,pts.length-1);
    return {pts:pts,ring:ring,end:[x,z],misclosure:mis,perimeter:per,
            precision:mis>1e-9?per/mis:Infinity,area:ring.length>=3?bimPolyArea(ring):0};
  }
  /* A closed WORLD ring -> legs (true bearings), starting at its first point. */
  function bimLegsFromRing(ring,tnDeg){
    var tn=isFinite(tnDeg)?tnDeg:bimTrueNorthDeg(),legs=[],i,a,b,dE,dN,d,azP;
    for(i=0;i<ring.length;i++){
      a=ring[i];b=ring[(i+1)%ring.length];
      dE=b[0]-a[0];dN=-(b[1]-a[1]);d=Math.sqrt(dE*dE+dN*dN);
      if(d<1e-9)continue;
      azP=Math.atan2(dE,dN)*180/Math.PI;
      var az=(((azP-tn)%360)+360)%360;
      legs.push({b:bimFormatBearing(az,' '),az:az,d:d});
    }
    return legs;
  }
  /* Each side moved inward by its own setback; neighbours meet where the moved lines cross.
     {ring} or {error} when the setbacks leave no buildable area. */
  function bimSetbackRing(ring,sb){
    var n=ring.length,i,sgn=bimPolySignedArea(ring)>0?1:-1,lines=[],out=[];
    if(n<3)return {error:'the parcel has fewer than 3 corners'};
    for(i=0;i<n;i++){
      var a=ring[i],b=ring[(i+1)%n],dx=b[0]-a[0],dz=b[1]-a[1],L=Math.sqrt(dx*dx+dz*dz);
      if(L<1e-9)return {error:'the parcel has a zero-length side'};
      var nx=sgn>0?-dz/L:dz/L,nz=sgn>0?dx/L:-dx/L,s=(sb&&isFinite(sb[i]))?+sb[i]:0;
      lines.push({p:[a[0]+nx*s,a[1]+nz*s],d:[dx/L,dz/L]});
    }
    for(i=0;i<n;i++){
      var L1=lines[(i+n-1)%n],L2=lines[i];
      var den=L1.d[0]*L2.d[1]-L1.d[1]*L2.d[0];
      if(Math.abs(den)<1e-12){out.push([L2.p[0],L2.p[1]]);continue;}
      var t=((L2.p[0]-L1.p[0])*L2.d[1]-(L2.p[1]-L1.p[1])*L2.d[0])/den;
      out.push([L1.p[0]+L1.d[0]*t,L1.p[1]+L1.d[1]*t]);
    }
    var sa=bimPolySignedArea(out);
    if(!(Math.abs(sa)>1e-6)||(sa>0?1:-1)!==sgn)return {error:'the setbacks leave no buildable area'};
    return {ring:out};
  }
"""

EDITS = [
    ("""  function bimRemoveGrid(id){""", FN + """  function bimRemoveGrid(id){"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
