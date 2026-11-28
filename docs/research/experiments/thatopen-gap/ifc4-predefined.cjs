// The IFC4 (ADD2 TC1) predefined type enumerations V306 uses, read from web-ifc's IFC4 schema namespace (the pinned
// tools/thatopen/node_modules/web-ifc). node docs/research/experiments/thatopen-gap/ifc4-predefined.cjs > ifc4-predefined.json
const W = require('../../../../tools/thatopen/node_modules/web-ifc/web-ifc-api-node.js'), N = W.IFC4;
const m = { IfcWall: 'IfcWallTypeEnum', IfcSlab: 'IfcSlabTypeEnum', IfcCovering: 'IfcCoveringTypeEnum', IfcColumn: 'IfcColumnTypeEnum',
  IfcBeam: 'IfcBeamTypeEnum', IfcFooting: 'IfcFootingTypeEnum', IfcRoof: 'IfcRoofTypeEnum', IfcStair: 'IfcStairTypeEnum',
  IfcDoor: 'IfcDoorTypeEnum', IfcWindow: 'IfcWindowTypeEnum', IfcSpace: 'IfcSpaceTypeEnum', IfcBuildingElementProxy: 'IfcBuildingElementProxyTypeEnum' };
const out = {};
for (const [c, e] of Object.entries(m)) out[c] = Object.keys(N[e]).filter((k) => /^[A-Z_]+$/.test(k));
console.log(JSON.stringify({ source: 'web-ifc ' + require('../../../../tools/thatopen/node_modules/web-ifc/package.json').version + ', IFC4 namespace', enums: out }, null, 1));
