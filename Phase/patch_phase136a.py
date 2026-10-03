"""patch_phase136a.py -- V136: the colour-by-property lens, the engine.

- A3D.site.lens = {by, prop}: '' (off), usage, level, type, layer, material, height, or prop (a
  named property: an OSM tag, an imported attribute, a context field). Kept on the site, so it is
  saved, undone and loaded with it.
- A value per object; categories take the scheme colours in name order (usage takes the usage's own
  colour), numbers take a six-step ramp between their lowest and highest. No value: grey.
- Computed once per paint and applied where every solid takes its colour: the GL face pass and the
  2D face loop (over Presentation's fill).
- A data layer can be coloured by one of its attributes, the same way, and has an opacity.
- One legend panel: the lens, then each data layer coloured by an attribute; below V105's room
  legend; not on paper."""
NAME = 'patch_phase136a.py'
BASE = '874b82bc0527d3d73d96fd854f5fff679e17253c5ec1ea41408e621c0cffe6df'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


ENGINE = r"""  /* ================= __acad3dV136: the colour-by-property lens ================= */
  var BIM_LENS_BY=['usage','level','type','layer','material','height','prop'];
  var BIM_LENS_LABEL={usage:'Usage',level:'Level',type:'Type',layer:'Layer',material:'Material',height:'Height',prop:'Property'};
  var BIM_LENS_RAMP=['#ffffb2','#fed976','#feb24c','#fd8d3c','#f03b20','#bd0026'];
  var BIM_LENS_NONE='#6b7480';
  var BIM_LENS_MAX_ROWS=14;
  var A3D_LENS={cur:null};
  function bimLensSettings(){
    var l=A3D.site&&A3D.site.lens;
    return {by:l&&BIM_LENS_BY.indexOf(l.by)>=0?l.by:'',prop:l&&typeof l.prop==='string'?l.prop:''};
  }
  /* the named properties an object carries: its OSM tags, its imported attributes, its context record */
  function bimLensProps(o){
    var out={},k,s;
    function take(src){for(k in src)if(src.hasOwnProperty(k)&&!out.hasOwnProperty(k)){s=src[k];if(s!==null&&(typeof s==='string'||typeof s==='number'||typeof s==='boolean'))out[k]=s;}}
    if(o.context&&o.context.tags)take(o.context.tags);
    if(o.geo&&o.geo.props)take(o.geo.props);
    if(o.context)take(o.context);
    return out;
  }
  function bimLensHeight(o){
    if(o.context&&typeof o.context.height==='number'&&isFinite(o.context.height))return o.context.height;
    var m=meshOf(o),i,a=Infinity,b=-Infinity;
    if(!m||!m.v||!m.v.length)return null;
    for(i=0;i<m.v.length;i++){if(m.v[i][1]<a)a=m.v[i][1];if(m.v[i][1]>b)b=m.v[i][1];}
    return isFinite(b-a)?Math.round((b-a)*100)/100:null;
  }
  /* one object's value under the lens: {v, name, col?} or null */
  function bimLensValue(o,st){
    var v,u,ly,k;
    if(st.by==='usage'){u=o.usage?bimUsageById(o.usage):null;return u?{v:'u:'+u.id,name:u.name,col:u.color}:null;}
    if(st.by==='level'){
      if(!o.level)return null;
      for(k=0;k<A3D.levels.length;k++)if(A3D.levels[k].id===o.level)return {v:'l:'+k,name:A3D.levels[k].name,order:k};
      return null;
    }
    if(st.by==='type'){k=(o.bim&&o.bim.type)||o.t;return k?{v:'t:'+k,name:(TYPES[k]&&TYPES[k].n)||(String(k).charAt(0).toUpperCase()+String(k).slice(1))}:null;}
    if(st.by==='layer'){ly=bimLayerById(o.layer);return ly?{v:'y:'+ly.id,name:ly.name}:null;}
    if(st.by==='material')return o.materialName?{v:'m:'+o.materialName,name:o.materialName}:null;
    if(st.by==='height'){v=bimLensHeight(o);return v===null?null:{num:v};}
    if(st.by==='prop'&&st.prop){
      v=bimLensProps(o)[st.prop];
      if(v===undefined||v==='')return null;
      if(typeof v==='number'||(/^-?\d+(\.\d+)?$/.test(String(v))&&isFinite(parseFloat(v))))return {num:parseFloat(v),raw:String(v)};
      return {v:'p:'+String(v).toLowerCase(),name:String(v)};
    }
    return null;
  }
  /* the scale: categories in name order (level in level order), or six steps between the lowest and highest number */
  function bimLensScale(vals){
    var cats={},list=[],nums=[],i,x,lo=Infinity,hi=-Infinity;
    for(i=0;i<vals.length;i++){
      x=vals[i];if(!x)continue;
      if(x.num!==undefined){nums.push(x.num);if(x.num<lo)lo=x.num;if(x.num>hi)hi=x.num;continue;}
      if(!cats[x.v]){cats[x.v]={name:x.name,col:x.col||'',order:x.order,n:0};list.push(x.v);}
      cats[x.v].n++;
    }
    if(nums.length&&!list.length){
      var bins=[],step=(hi-lo)/BIM_LENS_RAMP.length;
      for(i=0;i<BIM_LENS_RAMP.length;i++)bins.push({lo:lo+step*i,hi:i===BIM_LENS_RAMP.length-1?hi:lo+step*(i+1),col:BIM_LENS_RAMP[i],n:0});
      return {kind:'num',lo:lo,hi:hi,bins:bins};
    }
    list.sort(function(a,b){
      var A=cats[a],B=cats[b];
      if(A.order!==undefined&&B.order!==undefined)return A.order-B.order;
      var p=A.name.toLowerCase(),q=B.name.toLowerCase();return p<q?-1:(p>q?1:0);
    });
    for(i=0;i<list.length;i++)if(!cats[list[i]].col)cats[list[i]].col=BIM_SCHEME_COLS[i%BIM_SCHEME_COLS.length];
    return {kind:'cat',cats:cats,list:list};
  }
  function bimLensPick(sc,x){
    var i;
    if(!x)return null;
    if(sc.kind==='num'){
      if(x.num===undefined)return null;
      if(sc.hi<=sc.lo)return sc.bins[sc.bins.length-1];
      i=Math.min(sc.bins.length-1,Math.max(0,Math.floor((x.num-sc.lo)/(sc.hi-sc.lo)*sc.bins.length)));
      return sc.bins[i];
    }
    return x.v!==undefined?sc.cats[x.v]||null:null;
  }
  /* once per paint: the lens's colour for every object, and the legend */
  function bimLensCurrent(){
    if(A3D_LENS.cur)return A3D_LENS.cur;
    var st=bimLensSettings(),cur={by:st.by,prop:st.prop,col:{},none:0,scale:null},vals=[],ids=[],i,o,x,e;
    if(st.by&&!(st.by==='prop'&&!st.prop)){
      for(i=0;i<A3D.objs.length;i++){
        o=A3D.objs[i];
        if(!meshOf(o))continue;
        x=bimLensValue(o,st);vals.push(x);ids.push(o.id);
      }
      cur.scale=bimLensScale(vals);
      for(i=0;i<ids.length;i++){
        e=bimLensPick(cur.scale,vals[i]);
        if(e){cur.col[ids[i]]=e.col;e.n=(e.n||0)+(cur.scale.kind==='num'?1:0);}
        else{cur.col[ids[i]]=BIM_LENS_NONE;cur.none++;}
      }
    }
    A3D_LENS.cur=cur;
    return cur;
  }
  function bimLensCol(o){
    var c=bimLensCurrent();
    return c.by?(c.col[o.id]||null):null;
  }
  function bimLensTitle(st){
    if(!st.by)return '';
    return 'Coloured by '+(st.by==='prop'?st.prop:BIM_LENS_LABEL[st.by].toLowerCase())+(st.by==='height'?' (m)':'');
  }
  function bimLensFmt(v){return Math.abs(v)>=100?String(Math.round(v)):String(Math.round(v*10)/10);}
  /* the legend's rows for a scale: a colour and a name for each, the count, and "no value" */
  function bimLensRows(sc,none){
    var r=[],i,c;
    if(!sc)return r;
    if(sc.kind==='num'){
      for(i=0;i<sc.bins.length;i++)if(sc.bins[i].n)r.push({col:sc.bins[i].col,name:bimLensFmt(sc.bins[i].lo)+' to '+bimLensFmt(sc.bins[i].hi),n:sc.bins[i].n});
    }else for(i=0;i<sc.list.length;i++){c=sc.cats[sc.list[i]];r.push({col:c.col,name:c.name,n:c.n});}
    if(none)r.push({col:BIM_LENS_NONE,name:'no value',n:none});
    return r;
  }
  /* a data layer coloured by one of its attributes: the scale over its features, kept with its model */
  function bimDataLensScale(L){
    if(!L.by)return null;
    var F=bimDataFeats(L.id),vals=[],i,v,none=0;
    for(i=0;i<F.length;i++){
      v=F[i].p?F[i].p[L.by]:undefined;
      if(v===undefined||v===null||v===''){vals.push(null);none++;continue;}
      if(typeof v==='number'||(/^-?\d+(\.\d+)?$/.test(String(v))&&isFinite(parseFloat(v))))vals.push({num:parseFloat(v)});
      else vals.push({v:'p:'+String(v).toLowerCase(),name:String(v)});
    }
    var sc=bimLensScale(vals),k;
    if(sc.kind==='num')for(i=0;i<vals.length;i++){k=bimLensPick(sc,vals[i]);if(k)k.n++;}
    return {scale:sc,vals:vals,none:none};
  }
  function bimDataFeatCol(L,ds,fi){
    if(!ds)return L.color;
    var e=bimLensPick(ds.scale,ds.vals[fi]);
    return e?e.col:BIM_LENS_NONE;
  }
  function bimDataAttrKeys(id){
    var F=bimDataFeats(id),seen={},out=[],i,k;
    for(i=0;i<F.length&&i<500;i++)for(k in F[i].p)if(F[i].p.hasOwnProperty(k)&&!seen[k]){seen[k]=1;out.push(k);}
    return out.sort(function(a,b){a=a.toLowerCase();b=b.toLowerCase();return a<b?-1:(a>b?1:0);});
  }
  /* the properties the model's objects carry, most common first, for the lens's Property */
  function bimLensPropKeys(){
    var cnt={},out=[],i,k,p;
    for(i=0;i<A3D.objs.length;i++){p=bimLensProps(A3D.objs[i]);for(k in p)if(p.hasOwnProperty(k))cnt[k]=(cnt[k]||0)+1;}
    for(k in cnt)if(cnt.hasOwnProperty(k))out.push(k);
    out.sort(function(a,b){return cnt[b]-cnt[a]||(a<b?-1:(a>b?1:0));});
    return out.slice(0,80);
  }
  /* the lens is an undo step of its own */
  function bimLensSet(by,prop){
    by=BIM_LENS_BY.indexOf(by)>=0?by:'';
    prop=String(prop==null?'':prop).slice(0,80);
    var st=bimLensSettings();
    if(by!=='prop')prop=by===st.by?st.prop:'';
    if(by===st.by&&prop===st.prop)return st;
    pushUndo();
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    A3D.site.lens={by:by,prop:prop};
    A3D_LENS.cur=null;
    refreshProps();paint();saveSoon();
    var c=bimLensCurrent(),rows=by?bimLensRows(c.scale,c.none):[];
    a3dToast(!by?'Colour by: off':(by==='prop'&&!prop)?'Colour by property: pick the property':
      (bimLensTitle(bimLensSettings())+': '+(rows.length?rows.length+' entr'+(rows.length===1?'y':'ies'):'nothing has one')));
    return bimLensSettings();
  }
  /* the legend panel: the lens, then each shown data layer coloured by an attribute */
  function drawLensLegend(ctx,V,W,H){
    A3D.lastLensLegend=null;
    if(A3D.sheetCapture||A3D_PLOT.on)return;
    var blocks=[],c=bimLensCurrent(),st=bimLensSettings(),L=bimDataList(),i,ds,rows;
    if(c.by&&c.scale){rows=bimLensRows(c.scale,c.none);if(rows.length)blocks.push({title:bimLensTitle(st),rows:rows});}
    for(i=0;i<L.length;i++){
      if(!L[i].visible||!L[i].by)continue;
      ds=bimDataLensScale(L[i]);
      rows=ds?bimLensRows(ds.scale,ds.none):[];
      if(rows.length)blocks.push({title:L[i].name+': '+L[i].by,rows:rows});
    }
    if(!blocks.length)return;
    ctx.save();
    try{
      var sr=bimSafeViewRect(),rowH=16,pad=8,sw=11,w=0,h=pad,x,y,b,j,tw,ry,more,shown=[];
      ctx.font='11px sans-serif';ctx.textBaseline='middle';ctx.textAlign='left';
      for(i=0;i<blocks.length;i++){
        b=blocks[i];more=b.rows.length>BIM_LENS_MAX_ROWS?b.rows.length-BIM_LENS_MAX_ROWS+1:0;
        b.show=more?b.rows.slice(0,BIM_LENS_MAX_ROWS-1):b.rows;b.more=more;
        tw=ctx.measureText(b.title).width;if(tw>w)w=tw;
        for(j=0;j<b.show.length;j++){tw=sw+6+ctx.measureText(b.show[j].name+'  '+b.show[j].n).width;if(tw>w)w=tw;}
        h+=rowH*(1+b.show.length+(more?1:0))+(i?6:0);
      }
      w=Math.ceil(w+pad*2+10);h+=pad;
      x=sr.x+12;y=sr.y+12;
      if(A3D.lastRoomLegend&&A3D.lastRoomLegend.box)y=A3D.lastRoomLegend.box[1]+A3D.lastRoomLegend.box[3]+8;
      ctx.globalAlpha=1;
      ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(x,y,w,h);
      ctx.strokeStyle='rgba(255,255,255,0.18)';ctx.lineWidth=1;ctx.strokeRect(x+0.5,y+0.5,w-1,h-1);
      ry=y+pad;
      for(i=0;i<blocks.length;i++){
        b=blocks[i];if(i)ry+=6;
        ctx.fillStyle='#e8edf2';ctx.fillText(b.title,x+pad,ry+rowH/2);ry+=rowH;
        for(j=0;j<b.show.length;j++){
          ctx.fillStyle=b.show[j].col;ctx.fillRect(x+pad,ry+(rowH-sw)/2,sw,sw);
          ctx.fillStyle='#e8edf2';ctx.fillText(b.show[j].name,x+pad+sw+6,ry+rowH/2);
          ctx.fillStyle='#9aa7b4';ctx.textAlign='right';ctx.fillText(String(b.show[j].n),x+w-pad,ry+rowH/2);ctx.textAlign='left';
          ry+=rowH;
        }
        if(b.more){ctx.fillStyle='#9aa7b4';ctx.fillText('and '+b.more+' more',x+pad+sw+6,ry+rowH/2);ry+=rowH;}
        shown.push({title:b.title,rows:b.show,more:b.more});
      }
      A3D.lastLensLegend={blocks:shown,box:[x,y,w,h]};
    }catch(e){
      console.warn('[BIM] lens legend',e);
      if(!A3D.lensLegendWarned){A3D.lensLegendWarned=true;a3dToast('The colour legend could not be drawn');}
    }
    ctx.restore();
  }
"""

# the engine sits before the GL face pass
rep("""  /* __acad3dV121: one solid's faces, at an alpha -- the body of the face pass, shared by the opaque
     pass and the transparent one */
  function bimGlDrawFaces(G,o,rec,alpha){
    var gl=G.gl,col=bimHexToRgb(o.col||(TYPES[o.t]||{}).c||'#7f9db8');""",
    ENGINE + """  /* __acad3dV121: one solid's faces, at an alpha -- the body of the face pass, shared by the opaque
     pass and the transparent one */
  function bimGlDrawFaces(G,o,rec,alpha){
    var gl=G.gl,col=bimHexToRgb(bimLensCol(o)||o.col||(TYPES[o.t]||{}).c||'#7f9db8');   /* __acad3dV136: the lens first */""")
# computed afresh each paint
rep("""  function paint(){
    var cv=el.cv;if(!cv||!el.ctx)return;""", """  function paint(){
    var cv=el.cv;if(!cv||!el.ctx)return;
    A3D_LENS.cur=null;   /* __acad3dV136: the lens is worked out once per paint */""")
# the 2D face loop: the lens, over Presentation's fill
rep("""      var col=ob.col||(TYPES[ob.t]||{}).c||'#7f9db8';
      var wv=[];""", """      var lcol=bimLensCol(ob),col=lcol||ob.col||(TYPES[ob.t]||{}).c||'#7f9db8';   /* __acad3dV136 */
      var wv=[];""")
rep("""        polys.push({o:ob,pts:pts,z:zs/fc.length,n:faceNormal(wpts),col:col,lock:!bimLayerPickable(ob),la:bimLayerAlpha(ob)});   /* __acad3dV121 */""",
    """        polys.push({o:ob,pts:pts,z:zs/fc.length,n:faceNormal(wpts),col:col,lens:!!lcol,lock:!bimLayerPickable(ob),la:bimLayerAlpha(ob)});   /* __acad3dV121, __acad3dV136 */""")
rep("""      var baseFill=(rg&&rg.fill!=='none')?rg.fill:pl.col;""", """      var baseFill=pl.lens?pl.col:((rg&&rg.fill!=='none')?rg.fill:pl.col);   /* __acad3dV136: the lens over Presentation's fill */""")
# the legend, after the room legend
rep("""    drawRoomSchemeLegend(ctx,V,W,H);   /* __acad3dV105: the colour fill's legend, from what drawRooms just drew */""",
    """    drawRoomSchemeLegend(ctx,V,W,H);   /* __acad3dV105: the colour fill's legend, from what drawRooms just drew */
    drawLensLegend(ctx,V,W,H);         /* __acad3dV136: the lens's and the data layers' legend, below it */""")
# data layers: coloured by an attribute, at an opacity
rep("""      ctx.save();
      ctx.strokeStyle=L[i].color;ctx.fillStyle=L[i].color;
      for(j=0;j<c.feats.length;j++){
        f=c.feats[j];
        sel=!!(A3D_DATA.sel&&A3D_DATA.sel.layer===L[i].id&&A3D_DATA.sel.fi===f.fi);
        ctx.lineWidth=sel?2.6:1.2;
        if(f.rings.length){
          ctx.beginPath();
          f.rings.forEach(function(r){path(r.pts,true);});
          ctx.globalAlpha=sel?0.34:0.16;ctx.fill('evenodd');ctx.globalAlpha=1;ctx.stroke();
        }""", """      ctx.save();
      ctx.strokeStyle=L[i].color;ctx.fillStyle=L[i].color;
      var ds=bimDataLensScale(L[i]),op=bimDataOpacity(L[i]),fa=ds?0.5:0.16,fc;   /* __acad3dV136: by an attribute, at an opacity */
      ctx.globalAlpha=op;
      for(j=0;j<c.feats.length;j++){
        f=c.feats[j];
        if(ds){fc=bimDataFeatCol(L[i],ds,f.fi);ctx.strokeStyle=fc;ctx.fillStyle=fc;}
        sel=!!(A3D_DATA.sel&&A3D_DATA.sel.layer===L[i].id&&A3D_DATA.sel.fi===f.fi);
        ctx.lineWidth=sel?2.6:1.2;
        if(f.rings.length){
          ctx.beginPath();
          f.rings.forEach(function(r){path(r.pts,true);});
          ctx.globalAlpha=(sel?Math.min(1,fa*2.1):fa)*op;ctx.fill('evenodd');ctx.globalAlpha=op;ctx.stroke();
        }""")
rep("""  /* a layer's features in model terms, kept until the site's place, true north or the features change */""",
    """  function bimDataOpacity(L){var v=L.opacity;return typeof v==='number'&&v>=0.1&&v<=1?v:1;}   /* __acad3dV136 */
  /* a layer's features in model terms, kept until the site's place, true north or the features change */""")
rep("""    else if(field==='color'){v=String(val||'');if(!/^#[0-9a-fA-F]{6}$/.test(v)){a3dToast('That is not a colour');refreshProps();return false;}v=v.toLowerCase();}
    else return false;
    if(L[field]===v)return true;""", """    else if(field==='color'){v=String(val||'');if(!/^#[0-9a-fA-F]{6}$/.test(v)){a3dToast('That is not a colour');refreshProps();return false;}v=v.toLowerCase();}
    else if(field==='by'){v=String(val==null?'':val).slice(0,80);if(v&&bimDataAttrKeys(id).indexOf(v)<0){a3dToast(L.name+' has no attribute '+v);refreshProps();return false;}}   /* __acad3dV136 */
    else if(field==='opacity'){v=parseFloat(val);if(!isFinite(v)){a3dToast('Opacity is a percentage, 10 to 100');refreshProps();return false;}v=Math.max(0.1,Math.min(1,v>1?v/100:v));v=Math.round(v*100)/100;}
    else return false;
    if(L[field]===v||(field==='by'&&!v&&!L.by))return true;""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
