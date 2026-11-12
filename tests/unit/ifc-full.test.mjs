// V196, full IFC import (io/ifc-full.js): a small IFC4 file written here (a wall with a window's opening, on a storey,
// with a property set) read through the pinned cc-ifc engine and Manifold, as the browser has them, into the parts the
// model takes. Placing them in the model draws the Layers panel; that is checked in the browser.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { loadEngine } from './helpers/engine.mjs';

loadEngine();
const F = globalThis.__a3dIfc;
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const RT = path.join(ROOT, 'runtime', 'cc-ifc', F.limits.rev);

// the engine as one classic script, and Manifold given its wasm as bytes. Manifold's loader takes Node's own path
// when it sees Node; hidden for that call, it takes the browser's.
async function engine() {
  if (!globalThis.BIMIFC) vm.runInThisContext(fs.readFileSync(path.join(RT, 'bim-ifc.min.js'), 'utf8'));
  const B = globalThis.BIMIFC, P = Object.getOwnPropertyDescriptor(globalThis, 'process');
  Object.defineProperty(globalThis, 'process', { value: undefined, configurable: true });
  let p;
  try { p = B.Manifold({ wasmBinary: fs.readFileSync(path.join(RT, 'manifold.wasm')) }); }
  finally { Object.defineProperty(globalThis, 'process', P); }
  const M = await p; M.setup();
  return { B, M };
}

// millimetres; a wall 4 m long, 200 mm thick, 3 m high on a storey at 3.5 m, red, with a 1 m by 1.2 m opening
const IFC = `ISO-10303-21;
HEADER;FILE_DESCRIPTION(('ViewDefinition [ReferenceView]'),'2;1');FILE_NAME('t.ifc','2026-11-12T00:00:00',(''),(''),'','','');FILE_SCHEMA(('IFC4'));ENDSEC;
DATA;
#1=IFCPROJECT('0YvctVUKr0kugbFTf53O9L',$,'Test',$,$,$,$,(#20),#10);
#10=IFCUNITASSIGNMENT((#11));
#11=IFCSIUNIT(*,.LENGTHUNIT.,.MILLI.,.METRE.);
#12=IFCCARTESIANPOINT((0.,0.,0.));
#13=IFCAXIS2PLACEMENT3D(#12,$,$);
#20=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#13,$);
#30=IFCSITE('1YvctVUKr0kugbFTf53O9L',$,'Site',$,$,#31,$,$,.ELEMENT.,$,$,$,$,$);
#31=IFCLOCALPLACEMENT($,#13);
#32=IFCBUILDING('2YvctVUKr0kugbFTf53O9L',$,'Building',$,$,#33,$,$,.ELEMENT.,$,$,$);
#33=IFCLOCALPLACEMENT(#31,#13);
#34=IFCCARTESIANPOINT((0.,0.,3500.));
#35=IFCAXIS2PLACEMENT3D(#34,$,$);
#36=IFCBUILDINGSTOREY('3YvctVUKr0kugbFTf53O9L',$,'Level 1',$,$,#37,$,$,.ELEMENT.,3500.);
#37=IFCLOCALPLACEMENT(#33,#35);
#38=IFCRELAGGREGATES('4YvctVUKr0kugbFTf53O9L',$,$,$,#1,(#30));
#39=IFCRELAGGREGATES('5YvctVUKr0kugbFTf53O9L',$,$,$,#30,(#32));
#40=IFCRELAGGREGATES('6YvctVUKr0kugbFTf53O9L',$,$,$,#32,(#36));
#50=IFCWALL('7YvctVUKr0kugbFTf53O9L',$,'Wall A',$,$,#51,#60,$,.STANDARD.);
#51=IFCLOCALPLACEMENT(#37,#13);
#52=IFCCARTESIANPOINT((2000.,100.));
#53=IFCAXIS2PLACEMENT2D(#52,$);
#54=IFCRECTANGLEPROFILEDEF(.AREA.,$,#53,4000.,200.);
#55=IFCDIRECTION((0.,0.,1.));
#56=IFCEXTRUDEDAREASOLID(#54,#13,#55,3000.);
#57=IFCSHAPEREPRESENTATION(#20,'Body','SweptSolid',(#56));
#60=IFCPRODUCTDEFINITIONSHAPE($,$,(#57));
#61=IFCCOLOURRGB($,1.,0.,0.);
#62=IFCSURFACESTYLESHADING(#61,0.);
#63=IFCSURFACESTYLE($,.BOTH.,(#62));
#64=IFCSTYLEDITEM(#56,(#63),$);
#70=IFCRELCONTAINEDINSPATIALSTRUCTURE('8YvctVUKr0kugbFTf53O9L',$,$,$,(#50),#36);
#80=IFCOPENINGELEMENT('9YvctVUKr0kugbFTf53O9L',$,'Opening',$,$,#81,#87,$,.OPENING.);
#81=IFCLOCALPLACEMENT(#51,#13);
#82=IFCCARTESIANPOINT((2000.,100.));
#83=IFCAXIS2PLACEMENT2D(#82,$);
#84=IFCRECTANGLEPROFILEDEF(.AREA.,$,#83,1000.,600.);
#85=IFCCARTESIANPOINT((0.,0.,900.));
#86=IFCEXTRUDEDAREASOLID(#84,#88,#55,1200.);
#88=IFCAXIS2PLACEMENT3D(#85,$,$);
#89=IFCSHAPEREPRESENTATION(#20,'Body','SweptSolid',(#86));
#87=IFCPRODUCTDEFINITIONSHAPE($,$,(#89));
#90=IFCRELVOIDSELEMENT('AYvctVUKr0kugbFTf53O9L',$,$,$,#50,#80);
#100=IFCPROPERTYSINGLEVALUE('FireRating',$,IFCLABEL('EI 60'),$);
#101=IFCPROPERTYSINGLEVALUE('IsExternal',$,IFCBOOLEAN(.T.),$);
#102=IFCPROPERTYSET('BYvctVUKr0kugbFTf53O9L',$,'Pset_WallCommon',$,(#100,#101));
#103=IFCRELDEFINESBYPROPERTIES('CYvctVUKr0kugbFTf53O9L',$,$,$,(#50),#102);
ENDSEC;
END-ISO-10303-21;
`;

test('values and class names as Properties shows them', () => {
  assert.equal(F.val({ value: 0.123456789 }), '0.123457');
  assert.equal(F.val({ value: true }), 'Yes');
  assert.equal(F.val([{ value: 'a' }, { value: 'b' }]), 'a, b');
  assert.equal(F.cls('IfcWallStandardCase'), 'IfcWall');
  assert.equal(F.cls('IfcCurtainWall'), 'IfcCurtainWall');
  assert.equal(F.hex({ x: 1, y: 0, z: 0.5, w: 1 }), '#ff0080');
  const s = F.set({ Name: { value: 'Qto' }, Quantities: [{ Name: { value: 'Length' }, LengthValue: { value: 4 } }] });
  assert.deepEqual(s, { name: 'Qto', rows: [['Length', '4']] });
});

test('the runtime is looked for beside a page opened as a file, then on the site', () => {
  const a = F.sources('file:', 'https://x.example/runtime/');
  assert.deepEqual(a.map((s) => s.sri), [false, true]);
  assert.match(a[0].u, /^runtime\/cc-ifc\//);
  assert.equal(F.sources('https:', 'https://x.example/runtime/').length, 1);
});

test('an IFC file is read into elements in metres, +Y up, coloured, with the opening cut, its storey and its properties', async () => {
  const R = await engine();
  const D = await F.read(R, new TextEncoder().encode(IFC));
  assert.equal(D.booleans, true, 'Manifold loaded: openings are cut');
  assert.equal(D.parts.length, 1, 'the wall; the opening is not an element drawn');
  const w = D.parts[0];
  assert.equal(w.type, 'IfcWall');
  assert.equal(w.guid, '7YvctVUKr0kugbFTf53O9L');
  assert.equal(w.name, 'Wall A');
  assert.equal(w.col, '#ff0000');
  const ys = w.mesh.v.map((p) => p[1]), xs = w.mesh.v.map((p) => p[0]);
  assert.ok(Math.abs(Math.max(...ys) - Math.min(...ys) - 3) < 1e-6, 'three metres high, up the Y axis');
  assert.ok(Math.abs(Math.max(...xs) - Math.min(...xs) - 4) < 1e-6, 'four metres long');
  assert.ok(w.mesh.f.length > 12, 'more than a plain box: the hole is cut (' + w.mesh.f.length + ' triangles)');
  assert.ok(w.mesh.fe.length > 12, 'the hole has its own edges');
  assert.equal(D.storeys.length, 1);
  assert.equal(D.storeys[0].name, 'Level 1');
  assert.ok(Math.abs(Math.min(...ys) - D.storeys[0].elev) < 1e-6, 'the storey level is where the wall stands, in the same frame');
  assert.equal(D.holder[w.id], D.storeys[0].id, 'the wall is on Level 1');
  const ps = w.psets.find((s) => s.name === 'Pset_WallCommon');
  assert.ok(ps, 'its property set');
  assert.deepEqual(ps.rows, [['FireRating', 'EI 60'], ['IsExternal', 'Yes']]);
});
