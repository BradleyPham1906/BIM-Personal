

  /* ================= __acad3dV218: Streaming: OGC 3D Tiles, the pure part =================
     docs/research/research-notion-streaming-3d-tiles.md and docs/work-orders/v218/SPEC.md. 3D Tiles selection: screen-space
     error, the distance to a bounding sphere, refinement by REPLACE and ADD. Each function is a work order, added below as
     it is built; none uses another file's names. */

/* WO-01 bimTilesSse(ge, dist, h, fov): screen-space error in pixels */
function bimTilesSse(ge, dist, h, fov) {
  if (dist <= 0) {
    return Infinity;
  }
  return ge * h / (2 * dist * Math.tan(fov / 2));
}

/* WO-02 bimTilesDist(sphere, eye): distance from eye to sphere surface, 0 inside */
function bimTilesDist(sphere, eye) {
  var dx = eye[0] - sphere[0];
  var dy = eye[1] - sphere[1];
  var dz = eye[2] - sphere[2];
  var d = Math.sqrt(dx * dx + dy * dy + dz * dz);
  if (d <= sphere[3]) {
    return 0;
  }
  return d - sphere[3];
}

/* WO-03 bimTilesSelect(tile, eye, h, fov, maxSse, parentRefine): which tile uris to draw */
function bimTilesSelect(tile, eye, h, fov, maxSse, parentRefine) {
  var refine = tile.refine !== undefined ? tile.refine : (parentRefine !== undefined ? parentRefine : 'REPLACE');
  var dist = bimTilesDist(tile.boundingVolume.sphere, eye);
  var sse = bimTilesSse(tile.geometricError, dist, h, fov);
  var result = [];

  if (sse <= maxSse || !tile.children || tile.children.length === 0) {
    if (tile.content && tile.content.uri) {
      result.push(tile.content.uri);
    }
    return result;
  }

  if (refine === 'ADD') {
    if (tile.content && tile.content.uri) {
      result.push(tile.content.uri);
    }
  }

  if (tile.children) {
    for (var i = 0; i < tile.children.length; i++) {
      var child = bimTilesSelect(tile.children[i], eye, h, fov, maxSse, refine);
      for (var j = 0; j < child.length; j++) {
        result.push(child[j]);
      }
    }
  }

  return result;
}
