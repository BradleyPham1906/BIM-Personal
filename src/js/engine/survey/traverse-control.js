

  /* ================= __acad3dV212: Survey control, traverses and closure, the pure part =================
     docs/research/research-later-survey-control.md and docs/work-orders/v212/SPEC.md. Traverses: DMS, latitudes and
     departures, closure for loops and links (never for open traverses), the compass rule, angular misclosure. Each function
     is a work order, added below as it is built; none uses another file's names. */
  /* Degrees-minutes-seconds ('D-M-S' or 'D M S', seconds decimal, leading minus) or a bare number
     -> degrees. Minutes/seconds of 60 or more, and anything else, is null. */
  function bimSvDms(s){
    if(typeof s==='number')return isFinite(s)?s:null;
    if(typeof s!=='string')return null;
    var str=s,sign=1,parts,d,mi,se;
    if(str.charAt(0)==='-'){sign=-1;str=str.slice(1);}
    parts=str.split(/[-\s]+/);
    if(parts.length<1||parts.length>3)return null;
    d=parseFloat(parts[0]);mi=0;se=0;
    if(parts.length>=2){mi=parseFloat(parts[1]);if(mi>=60)return null;}
    if(parts.length>=3){se=parseFloat(parts[2]);if(se>=60)return null;}
    if(!isFinite(d)||!isFinite(mi)||!isFinite(se))return null;
    return sign*(d+mi/60+se/3600);
  }
  /* Legs [[az deg from north clockwise, distance]] -> {lat, dep} per leg, sumN, sumE, perimeter. */
  function bimSvLatDep(legs){
    var lat=[],dep=[],sumN=0,sumE=0,perimeter=0,i,az,d;
    for(i=0;i<legs.length;i++){
      az=legs[i][0]*Math.PI/180;d=+legs[i][1];
      lat[i]=d*Math.cos(az);dep[i]=d*Math.sin(az);
      sumN+=lat[i];sumE+=dep[i];perimeter+=d;
    }
    return {lat:lat,dep:dep,sumN:sumN,sumE:sumE,perimeter:perimeter};
  }
  /* 'closed' or 'link': misclosure and precision; open is not assessable. A link needs both ends. */
  function bimSvClosure(legs,kind,start,end){
    var r=bimSvLatDep(legs),east,north,misclosure,perimeter,ratio;
    if(kind==='open')return {status:'not assessable',why:'an open traverse has no independent closure'};
    if(kind==='link'){if(start==null||end==null)return {status:'not assessable',why:'a link traverse needs its known end'};east=start[0]+r.sumE-end[0];north=start[1]+r.sumN-end[1];}
    else{east=r.sumE;north=r.sumN;}
    perimeter=r.perimeter;
    misclosure=Math.sqrt(east*east+north*north);
    ratio=misclosure>1e-9?perimeter/misclosure:Infinity;
    return {status:'computed',east:east,north:north,misclosure:misclosure,perimeter:perimeter,ratio:ratio};
  }
  /* Bowditch (compass) rule: start [E, N], then each point moved by lat/dep less its length share
     of the closure error; the adjusted last point equals the first for a closed loop. */
  function bimSvCompass(legs,start){
    var r=bimSvLatDep(legs),pts=[[start[0],start[1]]],e=start[0],n=start[1],i,d,ce,cn;
    for(i=0;i<legs.length;i++){
      d=legs[i][1];
      ce=r.sumE*d/r.perimeter;cn=r.sumN*d/r.perimeter;
      e+=r.dep[i]-ce;n+=r.lat[i]-cn;
      pts.push([e,n]);
    }
    return pts;
  }
  /* Sum of interior angles less (n - 2) * 180; null for fewer than 3 angles. */
  function bimSvAngular(angles){
    var n=angles.length,sum=0,i;
    if(n<3)return null;
    for(i=0;i<n;i++)sum+=+angles[i];
    return sum-(n-2)*180;
  }

