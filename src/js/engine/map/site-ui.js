
  /* ===== __acad3dV202u: the Site and Map interface (docs/work-orders/v202/SPEC.md, part B) =====
     What the Site bar, the Data layers dialog, the place card and the compass show, as pure functions;
     the DOM that draws them is WO-15 to WO-19. */

  /* WO-12: the Data layers dialog's cards, one per kind in kinds' order:
     {kind, title, say, source, on, count}. st is bimCtxSettings()'s shape, counts the last fetch's
     {kind:n} (or null); labels the kinds' titles. A kind not in labels is left out. */
  function bimCtxCards(kinds, labels, st, counts) {
    if (!kinds || !labels) return [];
    var result = [];
    for (var i = 0; i < kinds.length; i++) {
      var kind = kinds[i];
      // Skip kinds not in labels
      if (!labels[kind]) continue;
      var on = !!(st && st.kinds && st.kinds[kind] === true);
      var count = counts ? (counts[kind] !== undefined ? counts[kind] : null) : null;
      var title = labels[kind];
      var source = labels ? (kind === 'terrain' ? 'AWS Terrain Tiles (Terrarium)' : 'OpenStreetMap') : '';
      var say = title + ' ' + source;
      result.push({ kind: kind, title: title, say: say, source: source, on: on, count: count });
    }
    // Add kinds from st.kinds that are not in the kinds array but are in labels
    if (st && st.kinds) {
      for (var key in st.kinds) {
        if (st.kinds.hasOwnProperty(key) && kinds.indexOf(key) === -1 && labels[key]) {
          var _on = st.kinds[key] === true;
          var _count = counts ? (counts[key] !== undefined ? counts[key] : null) : null;
          result.push({ kind: key, title: labels[key], say: labels[key], source: '', on: _on, count: _count });
        }
      }
    }
    return result;
  }
  /* WO-13: a context object's place card: {title, kind, rows:[[label,value],...], credit, osmUrl}.
     ctx is the object's o.context, name its o.name. null when ctx is missing. */
  function bimPlaceFacts(ctx,name){
    if(!ctx)return null;
    var kind=ctx.kind||'';
    var title=(ctx.tags&&ctx.tags.name)?ctx.tags.name:(name||'Unnamed');
    var credit=ctx.credit||null;
    var rows=[];
    if(ctx.height!==undefined){
      var h=ctx.height,hf=ctx.heightFrom,hv;
      if(!hf)hv=h+' m';
      else if(hf==='city')hv='6 m (measured)';
      else if(hf==='levels')hv='6 m (storeys x 3 m)';
      else if(hf==='assumed')hv='6 m (assumed)';
      else if(hf==='height')hv=h+' m (OpenStreetMap height)';
      else hv=h+' m';
      rows.push(['Height',hv]);
    }
    var lv=ctx.levels;
    if(lv===undefined&&ctx.tags&&ctx.tags['building:levels'])lv=ctx.tags['building:levels'];
    if(lv!==undefined)rows.push(['Levels',lv]);
    if(ctx.tags&&ctx.tags['addr:housenumber']&&ctx.tags['addr:street'])rows.push(['Address',ctx.tags['addr:housenumber']+' '+ctx.tags['addr:street']]);
    if(ctx.tags){
      var u='';
      if(ctx.tags.highway)u=ctx.tags.highway;
      else if(!ctx.tags.building||ctx.kind==='roads')u='';
      else if(ctx.tags.building&&ctx.tags.building.toLowerCase()==='yes')u=null;
      else u=ctx.tags.building?ctx.tags.building.replace(/_/g,' '):ctx.tags.use||'';
      if(u)rows.push(['Use',u]);
    }
    if(ctx.tags&&ctx.tags.start_date)rows.push(['Built',ctx.tags.start_date]);
    if(ctx.tags&&ctx.tags.operator)rows.push(['Operator',ctx.tags.operator]);
    if(ctx.fetched)rows.push(['Fetched',ctx.fetched]);
    if(ctx.width!==undefined)rows.push(['Width',ctx.width+' m']);
    if(ctx.deck!==undefined)rows.push(['Deck',ctx.deck+' m over the ground']);
    var osmUrl=null;
    if(ctx.osm&&ctx.id)osmUrl='https://www.openstreetmap.org/'+ctx.osm+'/'+ctx.id;
    var kl;
    if(kind==='buildings')kl='Building';
    else if(kind==='roads'||ctx.bridge)kl='Bridge';
    else if(kind==='rail')kl='Tunnel';
    else if(kind==='trees')kl='Tree';
    else kl='Unnamed';
    return {title:title,kind:kl,rows:rows,credit:credit,osmUrl:osmUrl};
  }
  /* WO-14: the compass: the needle's angle in degrees, 0 to under 360, for the camera's yaw (radians,
     0 looking down -z, positive turning left) and the project's true north (degrees, clockwise);
     and its letter, N, NE, E, SE, S, SW, W or NW, for the way the camera faces. NaN in, null out. */
  function bimCompass(yaw,trueNorth){
    return null;
  }
export { bimCompass, bimCtxCards, bimPlaceFacts };
