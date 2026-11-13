import * as esb from "esbuild"; import { threeGlobal } from "./three-global.mjs";
// "three" from the app's BIMTHREE; three/webgpu and three/tsl (used only by WebGPU-only code paths) made to throw if reached
const noGpu = { name: "no-webgpu", setup(b) {
  b.onResolve({ filter: /^three\/(webgpu|tsl)$/ }, a => ({ path: a.path, namespace: "ng" }));
  b.onLoad({ filter: /.*/, namespace: "ng" }, () => ({ contents: "throw new Error('WebGPU path left out of this build')", loader: "js" }));
}};
const r = await esb.build({ entryPoints: ["entry.mjs"], bundle: true, format: "iife", minify: true, target: "es2020", logLevel: "error", outfile: "out/toe-ext-three-nogpu.js", plugins: [threeGlobal, noGpu], metafile: true });
let t = 0; for (const [f, v] of Object.entries(r.metafile.outputs["out/toe-ext-three-nogpu.js"].inputs)) if (f.includes("node_modules/three/")) t += v.bytesInOutput;
console.log("three bytes left in bundle:", t);
