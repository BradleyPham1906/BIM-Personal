# Opening SketchUp files (V163)

The owner asked for openskp's code ("they opensource sketchup like app ... just copy and paste their
whole code and make it work in our app") and chose **Open .skp files**: the reader goes in, and a
SketchUp file opens as this app's objects -- faces and solids, materials and textures, tags as
layers, components as blocks.

## What a .skp file is

- **Two containers.** Every file starts with the same header: the words "SketchUp Model" and the
  version that saved it, `{17.0.1}` for SketchUp 2017. Up to SketchUp 2020 what follows is SketchUp's
  own object archive (MFC-style records that refer back to earlier ones by slot). From 2021 it is a
  ZIP of separate parts. The version in the header says which, so the import names the SketchUp that
  saved the file rather than guessing from the bytes.
- **Units.** Geometry is stored in inches whatever unit the model is shown in; the 2021 container also
  names its display unit (`Millimeter`). Z is up and +Y is north.
- **Tags** (called layers before SketchUp 2020; `Layer0` is shown as Untagged) belong to instances
  and to single faces, each with a colour and on/off. **Materials** are a colour, an opacity and, for
  a textured one, the image and its size; SketchUp keeps the image's average colour with it, which is
  what its Shaded style draws.
- **Groups and components** are both a definition placed by an instance. A component's definition
  is shared by every copy and listed in the Components panel; a group's definition is hidden and
  named `Group#N`. A component left unnamed is `Component#N`, and Make Unique turns `Chair` into
  `Chair#1`. SketchUp names these in the language it runs in: a Portuguese file has `Agrupar#2` and
  `Componente#1`.

## openskp

- github.com/iamahsanmehmood/openskp, MIT, Copyright (c) 2024-2026 Ahsan Mehmood. Taken at commit
  359d183. A TypeScript package (with Python, C++ and other ports) that reads both containers and
  writes the archive one.
- **What is taken:** the reader only -- `parseSkp` (the model's tables: definitions, tags,
  materials, scenes, units), `buildInstancedScene` (the placed scene: each definition's triangles
  once, each instance's transform, in metres with Y up), `buildScene` and `SkpParseError` -- with the
  two packages it needs, fflate (MIT, the ZIP) and earcut (ISC, triangles). Its writers, exporters
  (GLB, IFC, DXF, Fragments) and viewer are left out. Its "design" -- the web viewer -- is not taken:
  this app has its own views.
- **How it goes in.** `tools/openskp/build_reader.mjs` bundles the reader with esbuild and compiles
  it to ES5 syntax with TypeScript, wrapped in one function so its helpers are not page globals, with
  the three licences in its opening comment; `Phase/patch_phase163a.py` inlines the result by its
  hash as a script block of its own. The code is not edited by hand. It uses ES2015 built-ins (Map,
  Set, typed arrays, TextDecoder), which every browser this app supports has.
- **What it does not keep.** Whether an instance is a group or a component (both are read by one
  record reader, and the class is dropped); an instance's hidden flag; a face's own tag (faces are
  grouped by material, under their instance's tag). A projected texture's coordinates are its
  author's approximation. Some old files fail ("back-ref to unwalked slot" on a SketchUp 3 sample);
  the import then says so, with the reader's own reason.
- **Back faces.** A face whose two sides are painted differently -- most faces, since SketchUp's back
  is its own default colour -- comes out twice: its front, and its back wound the other way in the
  colour an unpainted face falls back to.

## How others bring SketchUp in

- **Rhino** (docs.mcneel.com, SketchUp import/export): faces come in as meshes or as trimmed planar
  surfaces; tags become layers ("Use group layers" puts a group's contents on the group's layer);
  "Add objects to groups" keeps SketchUp's groups, otherwise everything comes in loose.
- **Revit** (help.sketchup.com, SketchUp to Revit): the file is linked (Insert > Link CAD) at the
  project's internal origin and can be reloaded as it changes; its tags become the layers Visibility
  Graphics turns on and off. Bringing it in as IFC instead makes its parts Revit families.

## What this app does with it

| SketchUp | here |
|---|---|
| a face set, per placement and material | a locked solid, in world position (as OBJ and IFC come in), welded at 0.01 mm; a mirroring placement is turned the right way out |
| a face painted on both sides alike | one face; a face painted differently on its back is one face too: the back openskp adds in the fallback colour is dropped, or, when both sides are painted, the later one |
| a tag | a sub-layer of the file's layer, `<file> - <tag>`, in the tag's colour, off when SketchUp had it off (the 2021 container keeps that per tag, the archive per layer record) |
| Untagged | the file's layer itself |
| a material | the solid's colour, named in Properties (brackets of SketchUp's own materials dropped); an unpainted face is SketchUp's white |
| a texture | the colour SketchUp keeps with it (its average), the image's file named in Properties. This app draws colours, not images, on solids |
| a see-through material | a sub-layer of its tag, `<tag layer> - 65% see-through`, at the material's opacity in 5% steps (this app keeps transparency on layers, 0 to 90%) |
| a named component | an Assets block in the SketchUp category: its own triangles and everything inside it, in its own frame, the insertion point as the base point. Opening the same file again replaces it |
| a group, an unnamed component | in the model only. A name `<word>#N` is SketchUp's own unless `<word>` is itself a definition in the file |
| units, axes | inches, Z up, +Y north become metres, Y up, north at -Z: the reader's frame is this app's, so nothing is turned |

- **One undo step**, and the current layer stays current (the CityJSON import's rule). The blocks are
  in the library, which is kept apart from any project (V21), so an undo leaves them.
- **Limits.** 250,000 triangles a file (the rest is reported as not read); a block of up to 6,000
  triangles, and 1.5 million characters of blocks a file, so the library stays within browser storage.
- **Where it opens.** Import CAD takes `.skp`; the SKPIN command (IMPORTSKP, SKETCHUP) opens one; the
  Assets library's Import takes a file's components as blocks, placing nothing.
- **Tests.** `tools/openskp/make_fixtures.mjs` writes `tests/skp/site_kit.skp` with openskp's own
  writer from geometry defined in the script, and the values the import must produce from that same
  geometry -- so the repo holds no SketchUp file of unknown origin. The writer makes only the archive
  container; the 2021 container was checked by hand on openskp's own sample files, which are not
  copied here (their origin is not stated).

## Checked by hand on openskp's samples

| file | saved by | result |
|---|---|---|
| SU_File.skp | SketchUp 2025 (ZIP) | 1 object, 104 triangles |
| Untitled.skp | SketchUp 2025 (ZIP) | 43 objects on 11 tags, all groups, no blocks; 18,636 triangles, about a second |
| gondola_v20.skp | SketchUp 2020, Portuguese | 161 objects, 53,269 triangles; one block, its `Agrupar#N` groups and `Componente#1` not |
| capilla_quiroz_v17.skp | SketchUp 2017 | 16 objects, textures by their colour, two glass materials on see-through layers, 2 blocks |
| chair_and_table.skp (web viewer sample) | SketchUp 2017 | 24 objects, 9 nested components as blocks |
| legacy_v3_synthetic.skp | SketchUp 3 | refused, with the reader's reason |
| blank_v17.skp | SketchUp 2017 | "No faces ... to bring in" |
