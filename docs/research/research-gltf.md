# V195: glTF and GLB, in and out

Research and build, 2026-11-12. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer only.

## 1. The question

The owner (2026-11-12) asked for the five steps after V194; this is the first: bring models in (furniture, trees,
cars, people from model libraries) and send the model out (Blender, SketchUp, game engines, headsets). PIPELINE
already held it as "later: glTF and GLB in as Assets models" and Track E1 ("glTF and GLB export, meshes named by
element ID and layer, metres, +Y up").

## 2. Hypotheses

- H1: three.js's own GLTFLoader and GLTFExporter can be added to V194's pinned runtime without a second copy of
  three. **Held**: one bundle, one `three`; a GLB built by hand is read in Node (unit test).
- H2: no axis or unit conversion is needed. **Held** (S): glTF 2.0 is metres, +Y up, right-handed; this engine is
  metres, +Y up, with +Z south (north is -Z), also right-handed. The specification's section 3.4 was not reread
  for this note; the unit test reads a node's translation in metres and finds it unchanged.
- H3: a triangulated import drawn with every triangle's edges looks like a wireframe. **Held** by reading
  `render/gpu-batches.js` and `render/webgl.js`: every face's border is an outline. Answered by a mesh's own list
  of edges (`mesh.fe`): borders, and folds over 20 degrees.

## 3. The owner's decisions (2026-11-12)

- Compressed files: supported. Draco (KHR_draco_mesh_compression) through three.js's DRACOLoader and Draco's own
  glTF decoder (Apache-2.0, `runtime/three/0.186.1/draco/`, fetched only for such a file); meshopt
  (EXT_meshopt_compression) through three.js's MeshoptDecoder (MIT), in the bundle. KTX2 textures
  (KHR_texture_basisu) are not read: such a file is refused with that said.
- Where an import goes: the model (locked solids on a layer named after the file, see-through materials on a
  sub-layer, as V163's SketchUp import) and Assets (the whole file as one block, up to 20,000 triangles).

## 4. Found while building

- three.js's DRACOLoader works out default decoder addresses from `import.meta.url` when it loads. In a classic
  script that throws, so the bundle defines a fixed base that is never fetched (the app always sets the path). P:
  `examples/jsm/loaders/DRACOLoader.js` lines 17 to 23, three 0.186.1.
- GLTFExporter needs the browser's FileReader, so export cannot be tested in Node; the bundle grows from
  743,351 to 859,434 bytes.
- The unit tests' browser stand-in cannot draw the Layers panel (`refreshLayers` exhausts memory on its stubs), so
  the placing step is checked in the browser, the reading step in Node.

## 5. As built

- `io/gltf.js`: `bimGltfWeld`, `bimGltfFeatureEdges`, `bimGltfGather`, `bimGltfParts`, `bimImportGLTF`;
  `bimGltfScene`, `bimGltfExport`. `GLTFIN`, `GLTFOUT`, and `.glb`/`.gltf` in the Import picker.
- Out: one mesh per element shown, named by its name, its id and type in `extras`, under a node per layer, in its
  colour and its layer's transparency; faces as fans, as the shaded view draws them.
- Limits: 300,000 triangles read (the rest counted and said), a warning over 100,000.

## 6. Not yet

Textures drawn (a part takes its material's colour), KTX2, a `.gltf` with separate `.bin` or image files (open it
as one `.glb`), the Assets library's own Import button for glTF, placing a block from a glTF at a pick point (it
comes in where the file puts it). The app's own browser check has not been run.

## 7. Sources

P: three.js 0.186.1 from npm: `GLTFLoader.js`, `GLTFExporter.js`, `DRACOLoader.js`, `libs/meshopt_decoder.module.js`,
`libs/draco/README.md`, read and run here. P: this repository at 8253eb8. S: the glTF 2.0 specification's
coordinate system and units, from memory of it, checked only by the unit test.
