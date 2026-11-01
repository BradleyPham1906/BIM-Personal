  /* ================= __acad3dV172b: the weather Ladybug reads =================
     reference/research-ladybug-weather-comfort.md, 7 and 8. One source at a time, held in the worker:
     - an EPW, or the station's ZIP (EPW, DDY, STAT) from climate.onebuilding.org, opened from a file: that server
       sends no CORS header, so the browser cannot fetch it (named, not proxied); the ZIP's DDY gives ASHRAE's design
       days, which Ladybug 0.44.63 cannot read from a 2025 EPW header;
     - a year of Open-Meteo hours (ERA5, V159's source, CORS open), the last full year, asked for in the site's
       standard time as an EPW is (Etc/GMT zones are whole hours, their sign reversed); a site in a half-hour zone
       gets its hours in UTC, said so, since hourly data cannot follow it.
     What is kept with the project is where the hours came from (A3D.site.ladybug.src), not the hours: a year of ten
     variables would add half a megabyte, and a weather file is the owner's to open again. */
  var BIM_LB_OM='https://archive-api.open-meteo.com/v1/archive';
  var BIM_LB_OM_VARS=['temperature_2m','dew_point_2m','relative_humidity_2m','surface_pressure','wind_speed_10m',
    'wind_direction_10m','direct_normal_irradiance','diffuse_radiation','shortwave_radiation','cloud_cover'];
  function bimLbData(){
    A3D.site=A3D.site||{};
    if(!A3D.site.ladybug||typeof A3D.site.ladybug!=='object'||Array.isArray(A3D.site.ladybug))A3D.site.ladybug={};
    return A3D.site.ladybug;
  }
  /* the source the project names, if it is one */
  function bimLbSrcKept(){
    var L=A3D.site&&A3D.site.ladybug,s=L&&L.src;
    return s&&typeof s==='object'&&(s.kind==='file'||s.kind==='openmeteo')&&typeof s.key==='string'?s:null;
  }
  /* the Open-Meteo zone for a standard offset in hours; null for a half hour, which no Etc zone has */
  function bimLbOmZone(off){
    if(typeof off!=='number'||!isFinite(off)||off!==Math.round(off)||Math.abs(off)>14)return null;
    return off===0?'GMT':'Etc/GMT'+(off<0?'+':'-')+Math.abs(off);
  }
  /* the worker's source, and the project's record of it: one undo step */
  function bimLbSourceSet(S,extra){
    var k,s={},keep=['kind','name','city','state','country','station','source','lat','lon','tz','elev','hours','leap','ddy',
      'ddy_days','filled','year','design_head','design_read'];
    for(k=0;k<keep.length;k++)if(S&&S.hasOwnProperty(keep[k]))s[keep[k]]=S[keep[k]];
    if(extra)for(k in extra)if(extra.hasOwnProperty(k))s[k]=extra[k];
    s.at=bimSaToday();
    s.key=[s.kind,s.kind==='file'?s.name:'',s.station||'',s.lat,s.lon,s.year||'',s.hours].join('|');
    A3D_LB.src=s;
    var kept=bimLbSrcKept();
    if(kept&&kept.key===s.key)return kept;   /* the same weather opened again: the project already names it */
    pushUndo();
    bimLbData().src=s;
    saveSoon();
    if(typeof bimLbRefresh==='function')bimLbRefresh();
    return s;
  }
  /* a File (or its bytes): an EPW, or a ZIP with one */
  function bimLbOpenBytes(name,bytes){
    if(!bytes||!bytes.length)return Promise.reject(new Error('The file is empty'));
    return bimLbCall('open_file',{path:'/tmp/bim_src',name:String(name||'')},[{path:'/tmp/bim_src',data:bytes}]).then(function(S){
      return bimLbSourceSet(S,{name:String(name||S.name||'')});
    });
  }
  function bimLbOpenFile(file){
    return new Promise(function(res,rej){
      var fr=new FileReader();
      fr.onload=function(){res(new Uint8Array(fr.result));};
      fr.onerror=function(){rej(new Error('The file could not be read'));};
      fr.readAsArrayBuffer(file);
    }).then(function(bytes){return bimLbOpenBytes(file.name,bytes);});
  }
  /* the file chooser, from a button */
  function bimLbPickFile(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.epw,.zip';
    inp.onchange=function(){
      var f=inp.files&&inp.files[0];
      if(!f)return;
      a3dToast('Opening '+f.name+' for Ladybug ...');
      bimLbOpenFile(f).then(function(s){a3dToast('Weather: '+bimLbSrcWords(s));},
        function(e){a3dToast('The weather file could not be opened: '+(e&&e.message||e));});
    };
    inp.click();
  }
  /* the last full year from Open-Meteo, at the site's place and in its standard time */
  function bimLbOmUrl(lat,lon,year,zone){
    return BIM_LB_OM+'?'+bimClimQs({latitude:lat.toFixed(4),longitude:lon.toFixed(4),start_date:year+'-01-01',
      end_date:(year+1)+'-01-01',hourly:BIM_LB_OM_VARS.join(','),wind_speed_unit:'ms',timezone:zone});
  }
  function bimLbFetchYear(){
    var st=bimSunSettings();
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon))return Promise.reject(new Error('Set the site latitude and longitude first (Properties, Site, Location)'));
    if(typeof fetch!=='function')return Promise.reject(new Error('This browser cannot fetch the weather'));
    var year=bimClimYears()[1],off=bimSunNum(st.tz)?st.tz:Math.round(st.lon/15),zone=bimLbOmZone(off),tz=zone?off:0,url;
    url=bimLbOmUrl(st.lat,st.lon,year,zone||'GMT');
    return fetch(url).then(function(r){if(!r.ok)throw new Error('archive-api.open-meteo.com answered '+r.status);return r.json();},
      function(e){throw new Error('archive-api.open-meteo.com could not be reached ('+(e&&e.message||e)+'): the hours need the network');}).then(function(js){
      var h=js&&js.hourly,H,i;
      if(!h||!Array.isArray(h.time))throw new Error('Open-Meteo gave no hours');
      for(i=0;i<BIM_LB_OM_VARS.length;i++)if(!Array.isArray(h[BIM_LB_OM_VARS[i]]))throw new Error('Open-Meteo gave no '+BIM_LB_OM_VARS[i]);
      H={year:year,lat:st.lat,lon:st.lon,tz:tz,elev:bimSunNum(js.elevation)?js.elevation:0,
        name:(A3D.site&&A3D.site.name&&A3D.site.name!=='Site')?A3D.site.name:'Site',hourly:h};
      return bimLbCall('open_hours',{path:'/tmp/bim_hours.json'},[{path:'/tmp/bim_hours.json',data:JSON.stringify(H)}]);
    }).then(function(S){return bimLbSourceSet(S,{zone:zone||'UTC',half:!zone,url:url});});
  }
  /* the source in words */
  function bimLbSrcWords(s){
    if(!s)return 'none yet';
    if(s.kind==='openmeteo')return 'Open-Meteo ERA5, '+s.year+(s.half?', in UTC':'')+(s.filled?' ('+s.filled+' hours filled)':'');
    return (s.city||s.name)+(s.station?' ('+s.station+')':'')+', '+s.name+(s.ddy?', with its design days':'');
  }
