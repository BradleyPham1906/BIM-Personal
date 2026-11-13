import * as esb from "esbuild"; import { threeGlobal } from "./three-global.mjs";
const base = { entryPoints: ["entry.mjs"], bundle: true, format: "iife", minify: true, target: "es2020", logLevel: "error", metafile: true };
const a = await esb.build({ ...base, outfile: "out/toe-with-three.js" });
const b = await esb.build({ ...base, outfile: "out/toe-ext-three.js", plugins: [threeGlobal] });
const top = (m) => { const s = {}; for (const [f, v] of Object.entries(m.outputs[Object.keys(m.outputs)[0]].inputs)) { const k = f.replace(/^node_modules\//, "").split("/").slice(0, f.includes("@") ? 2 : 1).join("/"); s[k] = (s[k] || 0) + v.bytesInOutput; } return Object.entries(s).sort((x, y) => y[1] - x[1]).slice(0, 10); };
console.log("with three:", JSON.stringify(top(a.metafile)));
console.log("ext three :", JSON.stringify(top(b.metafile)));
