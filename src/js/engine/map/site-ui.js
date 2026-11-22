
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
    return null;
  }
  /* WO-14: the compass: the needle's angle in degrees, 0 to under 360, for the camera's yaw (radians,
     0 looking down -z, positive turning left) and the project's true north (degrees, clockwise);
     and its letter, N, NE, E, SE, S, SW, W or NW, for the way the camera faces. NaN in, null out. */
  function bimCompass(yaw,trueNorth){
    return null;
  }
export { bimCompass, bimCtxCards, bimPlaceFacts };
