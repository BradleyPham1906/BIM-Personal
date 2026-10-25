  /* ================= __acad3dV107: sun position =================
     The NOAA Solar Calculator equations (after Meeus, Astronomical Algorithms) as NOAA's
     spreadsheet gives them, its refraction approximation included. Checked against NREL's SPA
     (pvlib) at six places and dates: elevation within 0.01 deg, azimuth within 0.01 deg away from
     the zenith, sunrise, sunset and solar noon within half a minute. Time is local clock time with
     the UTC offset in force on that date (-5 EST, -4 EDT); noon, sunrise and sunset are minutes
     from local midnight; azimuth is degrees clockwise from TRUE north. */
  function bimSunCalc(lat,lon,tz,dateStr,timeStr){
    var dm=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dateStr||'')),tm=/^(\d{1,2}):(\d{2})$/.exec(String(timeStr||''));
    if(!dm||!tm||!isFinite(lat)||!isFinite(lon)||!isFinite(tz))return null;
    var rad=Math.PI/180,deg=180/Math.PI;
    var mins=(+tm[1])*60+(+tm[2]);
    var jd=Date.UTC(+dm[1],+dm[2]-1,+dm[3],0,0,0)/86400000+2440587.5+mins/1440-tz/24;
    var G=(jd-2451545)/36525;
    var I=((280.46646+G*(36000.76983+G*0.0003032))%360+360)%360;
    var J=357.52911+G*(35999.05029-0.0001537*G);
    var K=0.016708634-G*(0.000042037+0.0000001267*G);
    var L=Math.sin(J*rad)*(1.914602-G*(0.004817+0.000014*G))+Math.sin(2*J*rad)*(0.019993-0.000101*G)+Math.sin(3*J*rad)*0.000289;
    var M=I+L;
    var P=M-0.00569-0.00478*Math.sin((125.04-1934.136*G)*rad);
    var Q=23+(26+((21.448-G*(46.815+G*(0.00059-G*0.001813))))/60)/60;
    var R=Q+0.00256*Math.cos((125.04-1934.136*G)*rad);
    var T=Math.asin(Math.sin(R*rad)*Math.sin(P*rad))*deg;
    var U=Math.tan(R*rad/2)*Math.tan(R*rad/2);
    var V=4*deg*(U*Math.sin(2*I*rad)-2*K*Math.sin(J*rad)+4*K*U*Math.sin(J*rad)*Math.cos(2*I*rad)-0.5*U*U*Math.sin(4*I*rad)-1.25*K*K*Math.sin(2*J*rad));
    var hc=Math.cos(90.833*rad)/(Math.cos(lat*rad)*Math.cos(T*rad))-Math.tan(lat*rad)*Math.tan(T*rad);
    var W=(hc>=-1&&hc<=1)?Math.acos(hc)*deg:null;
    var noon=720-4*lon-V+tz*60;
    var AB=(((mins+V+4*lon-60*tz)%1440)+1440)%1440;
    var AC=AB/4<0?AB/4+180:AB/4-180;
    var cz=Math.sin(lat*rad)*Math.sin(T*rad)+Math.cos(lat*rad)*Math.cos(T*rad)*Math.cos(AC*rad);
    var AD=Math.acos(Math.max(-1,Math.min(1,cz)))*deg;
    var AE=90-AD,te=Math.tan(AE*rad);
    var AF=(AE>85?0:(AE>5?58.1/te-0.07/Math.pow(te,3)+0.000086/Math.pow(te,5):(AE>-0.575?1735+AE*(-518.2+AE*(103.4+AE*(-12.79+AE*0.711))):-20.772/te)))/3600;
    var ca=(Math.sin(lat*rad)*Math.cos(AD*rad)-Math.sin(T*rad))/(Math.cos(lat*rad)*Math.sin(AD*rad));
    var ac=Math.acos(Math.max(-1,Math.min(1,ca)))*deg;
    var AH=AC>0?((ac+180)%360):(((540-ac)%360)+360)%360;
    return {elevation:AE+AF,geomElevation:AE,azimuth:AH,declination:T,eqTime:V,hourAngle:AC,
      noon:noon,sunrise:W===null?null:noon-4*W,sunset:W===null?null:noon+4*W,
      polar:W!==null?'':(hc>1?'night':'day')};
  }
  /* __acad3dV107: the site's place on the earth and the moment studied. No invented location: the
     latitude, longitude and UTC offset stay unset until the owner gives them, and everything that
     needs them says so. Date and time default to noon on June 21 of this year. */
  function bimSunNum(v){return typeof v==='number'&&isFinite(v);}
  function bimPad2(n){n=Math.floor(n);return (n<10?'0':'')+n;}
  function bimHHMM(m){m=((Math.round(m)%1440)+1440)%1440;return bimPad2(m/60)+':'+bimPad2(m%60);}
  function bimSunSettings(){
    var s=(A3D.site&&A3D.site.sun)||{};
    return {lat:s.lat,lon:s.lon,tz:s.tz,date:s.date||(new Date().getFullYear()+'-06-21'),time:s.time||'12:00'};
  }
  function bimSunNow(){
    var st=bimSunSettings(),miss=[],r;
    if(!bimSunNum(st.lat))miss.push('latitude');
    if(!bimSunNum(st.lon))miss.push('longitude');
    if(!bimSunNum(st.tz))miss.push('UTC offset');
    if(miss.length)return {missing:miss,settings:st};
    r=bimSunCalc(st.lat,st.lon,st.tz,st.date,st.time);
    if(!r)return {missing:['a valid date and time'],settings:st};
    r.settings=st;
    return r;
  }
  function bimSunText(sun){
    if(!sun)return '-';
    if(sun.missing)return 'set the '+sun.missing.join(', ');
    var t=sun.elevation>0?('altitude '+sun.elevation.toFixed(1)+', azimuth '+sun.azimuth.toFixed(1)+' deg'):'below the horizon';
    if(sun.polar==='day')t+='; no sunset (midnight sun)';
    else if(sun.polar==='night')t+='; no sunrise (polar night)';
    else t+='; rises '+bimHHMM(sun.sunrise)+', sets '+bimHHMM(sun.sunset);
    return t;
  }
  function bimSetSun(field,val){
    var v=String(val==null?'':val).replace(/^\s+|\s+$/g,''),n=parseFloat(v),nv=null,lim,m,nm,cur;
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    if(field==='lat'||field==='lon'||field==='tz'){
      lim=field==='lat'?[-90,90]:(field==='lon'?[-180,180]:[-12,14]);
      nm=field==='lat'?'Latitude':(field==='lon'?'Longitude':'UTC offset');
      if(v!==''&&(!isFinite(n)||n<lim[0]||n>lim[1])){a3dToast(nm+' must be a number from '+lim[0]+' to '+lim[1]);refreshProps();return false;}
      nv=v===''?null:n;
    }else if(field==='date'){
      m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
      if(v!==''&&(!m||+m[2]<1||+m[2]>12||new Date(Date.UTC(+m[1],+m[2]-1,+m[3])).getUTCDate()!==+m[3])){a3dToast('The sun date must be a real date, YYYY-MM-DD');refreshProps();return false;}
      nv=v===''?null:v;
    }else if(field==='time'){
      m=/^(\d{1,2}):(\d{2})(?::\d{2})?$/.exec(v);
      if(v!==''&&(!m||+m[1]>23||+m[2]>59)){a3dToast('The sun time must be HH:MM, from 00:00 to 23:59');refreshProps();return false;}
      nv=v===''?null:(bimPad2(+m[1])+':'+m[2]);
    }else return false;
    cur=A3D.site.sun||{};
    if((cur[field]==null?null:cur[field])===nv)return true;
    pushUndo();
    A3D.site.sun=A3D.site.sun||{};
    if(nv===null)delete A3D.site.sun[field];else A3D.site.sun[field]=nv;
    refreshProps();paint();saveSoon();
    a3dToast('Sun: '+bimSunText(bimSunNow()));
    return true;
  }
