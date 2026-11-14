/* V177 e04: the app's Pyodide and the pinned IfcOpenShell in a classic Web Worker, as the app's Python worker runs */
var WHEELS = ['six-1.17.0-py2.py3-none-any.whl', 'python_dateutil-2.9.0.post0-py2.py3-none-any.whl', 'typing_extensions-4.15.0-py3-none-any.whl',
  'shapely-2.0.7-cp313-cp313-pyemscripten_2025_0_wasm32.whl', 'isodate-0.7.2-py3-none-any.whl', 'lark-1.3.1-py3-none-any.whl',
  'ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl'];
self.onmessage = function () {
  var out = {}, t = Date.now(), py;
  function step(label, code) { var t = Date.now(); py.runPython(code); out[label] = Date.now() - t; }
  importScripts('/runtime/pyodide/0.29.5/pyodide.js');
  self.loadPyodide({ indexURL: '/runtime/pyodide/0.29.5/' }).then(function (p) {
    py = p; out.boot = Date.now() - t; t = Date.now();
    return py.loadPackage('numpy');
  }).then(function () {
    return Promise.all(WHEELS.map(function (f) { return fetch('/wheels/' + f).then(function (r) { return r.arrayBuffer(); }); }));
  }).then(function (bufs) {
    out.fetch = Date.now() - t; t = Date.now();
    bufs.forEach(function (b) { py.unpackArchive(b, 'wheel'); });
    out.unpack = Date.now() - t;
    step('numpy', 'import numpy');
    step('shapely', 'import shapely');
    step('wrapper', 'import ifcopenshell._ifcopenshell_wrapper');
    step('api_util', 'import ifcopenshell.api, ifcopenshell.api.project, ifcopenshell.api.root, ifcopenshell.api.unit, ifcopenshell.api.context, ifcopenshell.api.aggregate, ifcopenshell.api.geometry, ifcopenshell.api.spatial, ifcopenshell.util.element, ifcopenshell.util.placement, ifcopenshell.util.unit');
    step('create_file', 'f = ifcopenshell.api.project.create_file(version="IFC4")');
    step('wall', 'ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="P")\nc = ifcopenshell.api.context.add_context(f, context_type="Model")\nr = ifcopenshell.api.geometry.add_wall_representation(f, context=c, length=4, height=3, thickness=0.2)');
    step('write', 'f.write("/tmp/o.ifc")');
    step('open', 'g = ifcopenshell.open("/tmp/o.ifc")');
    self.postMessage(out);
  }).then(null, function (x) { out.error = String(x && x.message || x).slice(-300); self.postMessage(out); });
};
