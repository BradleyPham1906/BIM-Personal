# Model generation languages: what exists, and what the app should speak

Research, 2026-11-15. Second round on algorithmic design; the first is `../research-algorithmic-design.md`
and `grammars-and-layout.md` (CGA shape and split grammars are there and are only cited here).

Levels: **P** the source itself was read today (licence file, README, package metadata, language reference,
paper or its abstract: said which); **S** a dependable secondary source; **U** a search summary, or a fact
recalled from before this session and not re-read today. U facts are pointers and must not reach the code.
Code was read as text only; nothing was built, installed or run. Examples are written for this note.

## 1. Summary of findings

Written by the coordinator from the entries below: the researcher was stopped by the account's usage limit
after family 2.7, before the summary, the comparison table, the search log and the reference list. Each
entry names what was read and its level in place; there is no separate reference list for this note.

1. Model generation languages fall into five families: CSG scripts (OpenSCAD, JSCAD), code on a B-rep kernel
   (CadQuery, build123d, Replicad, KCL, FeatureScript), grammars and constraint generators (CGA, L-systems,
   Wave Function Collapse), dataflow graphs (Grasshopper, Dynamo and DesignScript, Geometry Nodes, Houdini,
   Marionette), and BIM-oriented generation (GDL, families, Hypar Elements, IfcOpenShell's API, Topologic).
2. Only the last family knows what a wall is, and none of it can be adopted here as it stands: GDL and
   families are proprietary and run only in their hosts; Hypar Elements is C# run as services; IfcOpenShell's
   API is Python (LGPL), which this app already carries in its Python worker for IFC export. P for licences.
3. The geometry-only languages that run in a browser under an allowed licence (JSCAD, MIT) are ordinary
   JavaScript programs: running one means running code, which the engine does not do. OpenSCAD is GPL.
   The B-rep ones need OpenCascade (round one: 22.9 MB). P.
4. There is no open, implemented standard for exchanging a parametric or procedural model. IFC records the
   result, not the rule. P for IFC and USD; S for STEP.
5. Systems that turn text into models moved in two years from special token sequences to readable code or
   structured text; the ones that make buildings give the model a small vocabulary of element-level calls
   (26 in Text2BIM), not a geometry language and not raw IFC. P (papers and abstracts), medium: a young field.
6. A new format has no training data and must be taught in the prompt; the papers that chose CadQuery did so
   because models already know Python. P.

## 2. The families

Each entry: maker; licence (language / implementation); what a program looks like; what it generates; how it
executes; browser; building elements; weaknesses.

### 2.1 Constructive solid geometry scripts

**OpenSCAD.** The OpenSCAD project. The implementation is GPL-2.0 with a linking exception for CGAL (COPYING
read, P); the language has no separate specification or licence, it is what the program accepts (U). Its own
README calls it a "3D-compiler": a script describes the object, the program renders it; two techniques, CSG
and extrusion of 2D outlines (P). A program is a tree of nested calls, for example:

    wall_t = 0.2;
    difference() {
      cube([6, wall_t, 2.7]);
      translate([2, -0.1, 0]) cube([0.9, wall_t + 0.2, 2.1]);
    }

(a wall slab with a door-sized hole). It generates a triangle mesh (STL, OFF, 3MF); no B-rep, no element
types, no properties (P for the formats named in the README). Execution: a declarative tree; variables are
bound once per scope, modules are not functions and return no value, and a script cannot ask the size of what
it has made (U, recalled from the user manual; this is the criticism made most often).
Browser: yes. `openscad-wasm` builds the whole program headless to WebAssembly, an ES module driven like a
command line (write a file into a virtual file system, call main with arguments, read the result) (its README,
P). npm: `openscad-wasm` 0.0.4, GPL-2.0, 13.9 MB unpacked; `openscad-wasm-prebuilt` 1.2.0, GPL-2.0-or-later,
11.1 MB unpacked (registry, P). The OpenSCAD playground wraps it as an installable offline web app (P).
**Under the app's rule:** GPL means it may never be joined into `canvas_v10.html`. It could ship only as a
separate, unchanged program under `runtime/`, run inside a worker, reached by messages, optional, as the rule
already allows for IfcOpenShell's wheel. About 11 MB for a mesh-only result with no building elements.
Building elements: none.

**JSCAD (OpenJSCAD).** The JSCAD organisation; MIT (LICENSE read, P). A program is ordinary JavaScript: a
`main` function returns solids built with library calls (primitives, booleans, extrusions, transforms); a
second function may declare the parameters shown to the user (U for the parameter function's name, recalled).
In words: make a cuboid, make a smaller cuboid, subtract, return. Mesh output (polygons, BSP booleans: the
method the app already has, round one 4.5, P there). Execution: an imperative script building an immutable
value tree. Browser: native. `@jscad/modeling` 2.13.0, MIT, 1.59 MB unpacked in 1,100 files, no dependencies
(registry, P). Building elements: none. Weaknesses: BSP booleans are slow and not robust on large or
near-coplanar input (round one, P there); its programs are JavaScript, so running a user's or an LLM's program
is running arbitrary code in the page.

**ImplicitCAD.** Haskell-Things; AGPL-3.0 (LICENSE read, P). Two surfaces: "ExtOpenSCAD", a modified OpenSCAD
dialect, and a Haskell library (README, P). Its addition over OpenSCAD is that every boolean takes a rounding
radius, because shapes are implicit functions (P). Output: STL, SVG, G-code. The README calls it a work in
progress for beta testers (P). No browser build was found (U). Building elements: none.

**libfive and Studio.** Matt Keeter. The library is MPL-2.0; the Studio GUI is GPL-2.0-or-later (README, P).
Shapes are functional representations (signed distance functions); programs are Guile Scheme or Python calling
a standard library of shapes, transforms and CSG; the mesher gives watertight, manifold, feature-preserving
triangles (P). Studio adds "direct modeling": dragging the surface changes variables in the script (P), the
one idea here worth borrowing (a hand edit written back into the program's parameters). No browser build is
listed in the README (P); no npm package (registry, P). Building elements: none. Weakness: a distance field
has no faces, edges or dimensions to refer to, so nothing can be dimensioned, hosted or scheduled (inference).

**Curv.** Doug Moen; Apache-2.0 (LICENSE read, P); the repository says it has moved from GitHub to Codeberg
(README, P). A pure functional, dynamically typed language for F-Rep shapes with colour; its standard library
is written in Curv itself (P). Rendered on the GPU; meshes for printing. No browser build (U). None.

**What the family shows.** A CSG script is a tree of solids and transforms: it is readable, diffs well, and
LLMs write it (family 6). It knows nothing of walls, storeys, hosts or properties, and its results are meshes.

### 2.2 Code-CAD on B-rep kernels

**CadQuery.** The CadQuery organisation; Apache-2.0 (README, P). Python on OpenCascade through its own
bindings (OCP), shipped as binary wheels for Linux, macOS and Windows, Python 3.9 to 3.12 (P). A program is a
chain of method calls on a workplane: start on the XY plane, draw a box, select the top face with a selector
string, put a hole in it, fillet the vertical edges. Output: a B-rep solid; STEP and DXF as well as meshes
(P). Execution: an imperative script; faces and edges are found by selectors evaluated when the script runs,
not by stored ids. Browser: no official build (U). Building elements: none. Weakness: selectors by direction
and position break when the shape changes (the topological naming problem, round one 4.2).

**build123d.** Roger Maitland ("gumyr"); Apache-2.0 (README, P). Python on OpenCascade. Two modes it names
itself: algebra mode (stateless, objects combined with operators such as `+` and `*` for placement) and
builder mode (`with BuildPart() as p:` blocks that track pending faces and edges like a feature history) (P).
B-rep; STEP. No browser build (U). Building elements: none.

**Replicad.** Steve Genoud; the library is MIT, its kernel build `replicad-opencascadejs` is LGPL-2.1-only
(registry, P). "The library to build browser based 3D models with code" (README, P). A program is a JavaScript
file with a parameter object and a `main` function that draws a 2D profile and revolves, extrudes or lofts it
(its vase example read, P). B-rep. Browser: yes; `replicad` 1.2.1 is 6.8 MB unpacked, the kernel package
48.8 MB unpacked in 11 files (registry, P; round one measured the wasm at 22.9 MB). LGPL as its own file fits
the rule; the size does not fit a one-file build. Building elements: none.

**CascadeStudio.** Johnathon Selstad ("zalo"); MIT; OpenCascade 8.0 compiled to WebAssembly; a browser IDE
with a standard library of functions (box, sphere, sketch, booleans, sweeps, lofts, fillets) and the whole
kernel reachable below it; installable for offline use (README, P). JavaScript/TypeScript programs. B-rep.
Same size class as Replicad. Building elements: none.

**Zoo KCL (KittyCAD language).** Zoo (KittyCAD, Inc.). The language tooling is open: the repository is MIT
(LICENSE read, P) and `@kittycad/kcl-wasm-lib` 0.1.196 is MIT, 17.5 MB unpacked (registry, P). A program is
plain assignments and pipelines: a settings line for units, named numbers computed from each other, then a
sketch piped (`|>`) through line, close and extrude steps, with tags naming edges for later fillets (one of
their samples read, and the reference's topic list: pipelines, units, sketch blocks and constraints, edge
references, modules; P). **The geometry is not computed in the browser:** the project's README says the 3D
view "is just a video stream from our hosted geometry engine" and that modelling commands go to it over
WebSockets (P); the crate has an `engine` feature and depends on the vendor's API client (Cargo.toml, P). So
the language is open, the parser runs client-side, and a model still needs the vendor's server and an account.
It cannot run offline from `file://`. B-rep solids, mechanical parts; no building elements.

**Onshape FeatureScript.** Onshape (PTC); proprietary, runs only inside Onshape's cloud. What matters is the
model, in its own words: a feature type is a function; a feature in the tree is a call of that function; the
feature's parameters are the call's arguments; a part studio is a function with one call per feature whose
result is the geometry; the language is deterministic by design; the standard features' source is published
(FsDoc introduction, P). Geometry is referenced by queries evaluated at regeneration rather than by stored
ids, and every feature call carries an id from which the ids of what it makes are derived (U, recalled, not
re-read today). This is the same shape as the app's queued V213 generators with a stable key (round one).

**FreeCAD Python.** The FreeCAD project; LGPL-2.1 (LICENSE read, P). Python that creates document objects
(a sketch, a pad, a pocket) whose properties are then re-evaluated by the document's dependency graph; its
BIM workbench adds walls, structures and windows as parametric objects (U for the workbench detail). B-rep
through OpenCascade. No browser build (U). FreeCAD 1.0's history-based naming and its own statement that
the matching is a heuristic are in round one 4.2 (P there).

**bitbybit** (noted in passing): a browser platform that wraps OCCT, Manifold and JSCAD behind one
TypeScript/visual API; `@bitbybit-dev/occt` 1.6.2 is "MIT AND Apache-2.0 AND LGPL-2.1-only WITH
OCCT-exception", 102 MB unpacked (registry, P).

**What the family shows.** Every language here is a general programming language plus a geometry library:
expressive, written well by LLMs (family 6), and none has a notion of a building element. In the browser the
kernel is 20 MB or more, or it is a server.

### 2.3 Shape and rule grammars, and constraint-based generation

**CGA shape and split grammars.** Round one (`grammars-and-layout.md` F1 to F8; `../research-algorithmic-design.md`
4.3): a shape is a symbol, a scope and attributes; rules replace whole labelled boxes; the split arithmetic is
tiny. Not repeated. **New here:** CityEngine's current release notes list a **Visual CGA Editor** (a node
browser, "Visual CGA Design" files that components import) alongside the textual language, and a Python 3 API
around it; CGA itself gained edge selectors for holes and setback operations usable inside `inline` and
`modify`; no new file format is listed, and rule packages (`.rpk`) remain the closed, compiled carrier that
the Rhino and Houdini plug-ins and PyPRT consume (release notes read, P; the plug-in facts are U, a search
summary). So Esri itself now offers nodes over the same rule language: the two are front ends of one model.

**CGA++** (Schwarz and Mueller 2015). Round one F8 (P there): shapes as first-class values, coordination
across branches, operations on several shapes, trial derivations. A research language; no open implementation
was found in round one. Nothing new.

**L-systems** (Lindenmayer 1968; Prusinkiewicz and Lindenmayer, The Algorithmic Beauty of Plants, 1990, hosted
free by its author's group: the publication list was read, the book was not re-read, so its content is U).
A program is an axiom and productions over a string, for example axiom `F`, rule `F -> F[+F]F[-F]`, read
afterwards by a turtle that draws (`F` forward, `+`/`-` turn, `[`/`]` push and pop). Rule rewriting, all
symbols in parallel each step; variants are stochastic, context-sensitive and parametric (README of the npm
library, P). Implementation: `lindenmayer` 1.5.4, MIT, 81 KB unpacked, a classic-script browser build, with
productions as strings or as JavaScript functions (registry and README, P). Generates a string; geometry is
whatever the turtle makes. Suits growth (plants, branching street networks: Parish and Mueller 2001, U); for
buildings the split grammar replaced it because a building is subdivided, not grown (Wonka 2003, round one P).
Building elements: none.

**Shape grammar interpreters** (Stiny and Gips 1972). Round one F9: a general interpreter must find every
transformed copy of a rule's left side, including emergent shapes; cost at least quadratic to cubic, worse
with parameters (S there). Existing interpreters are research software (U). Nothing new; not a candidate.

**Wave Function Collapse and model synthesis.** Model synthesis: Paul Merrell, 2007 (i3D), 2008 (ACM TOG,
continuous), 2010 (IEEE TVCG), PhD 2009; his page says WFC (Maxim Gumin, 2016) reimplements the algorithm, the
two being nearly identical, model synthesis aimed at 3D models and WFC at 2D textures (his page and README,
P). WFC: MIT (LICENSE read, P). The "program" is not a script: it is an example, or a tile set with allowed
adjacencies, plus a grid. The solver repeatedly picks the cell with the fewest remaining options, fixes it
at random by the observed weights, and propagates what neighbours may still be (README, P). Constraint
solving, stochastic, and it can reach a contradiction and have to restart (README, P). Client-side:
`wavefunctioncollapse` 2.1.0, MIT, 34 KB unpacked (registry, P). Generates a labelled grid; tiles could be
building modules, but adjacency is the only constraint it knows: no areas, no storeys, no code rules, no
global structure (inference from the algorithm's definition). A different kind of thing from a rule language:
it is written by example and cannot be read as intent.

**What the family shows.** A grammar is rules as data: readable, diffable, small to implement (round one's 50
lines), and limited by design. Esri putting a node editor over CGA rather than replacing it is evidence that
rules-as-data is the durable layer and the editor is a view.

### 2.4 Visual dataflow languages as languages

**Grasshopper `.gh` / `.ghx`.** Robert McNeel and Associates; proprietary host. `.ghx` is XML, `.gh` the
binary form of the same nested dictionary written by `GH_IO.dll`; the vendor's wiki says the files can be
read by third parties or by hand, that the library is documented, and that "no schema is available" (wiki
page dated 2008, P). The developer has said each component writes itself to the archive, so there is no
definition of what a file contains beyond the top-level frame (forum, U via search). So the container is
readable; the meaning of each component (several hundred built in, thousands in plug-ins, each identified by
a GUID) is not specified anywhere but in the program. Execution: dataflow with data trees, expire and
re-solve downstream (round one 4.1, P there). Generates Rhino geometry (NURBS, meshes); elements only through
plug-ins. **Importable: the wiring, yes; the behaviour, no.**

**Dynamo `.dyn` and DesignScript.** Autodesk; Dynamo's core is Apache-2.0 (LICENSE read, P). `.dyn` is JSON
since 2.0: nodes with ids, inputs, outputs, connectors, a separate view block, and element bindings (round
one 4.2, a `.dyn` read, P there). Under the nodes is a textual language whose specification is public in the
repository (LanguageSpec.md read, P): the default block is **associative** (a variable at global scope may be
assigned once; statements form a dependency graph); an `[Imperative]` block runs statements in order, allows
mutation, `if`, `for` and `while` (valid only there), cannot be nested in another imperative block, and must
capture outer variables explicitly; **replication** calls a function once per list element without a loop:
zip (shortest by default, longest on request) or cartesian, chosen by replication guides such as `x<1>`,
`y<2>`, or triggered when an argument's rank is higher than the parameter's (P). A program in words:
`xs = 0..10..2;` then `pts = Point.ByCoordinates(xs<1>, xs<2>);` gives a grid of points with no loop.
Generates host geometry, or Revit elements through Revit nodes. Engine is .NET; no browser build (U).
**Importable: the JSON and the language are documented; the node library is the host's.**

**Blender Geometry Nodes.** Blender Foundation; GPL-2.0-or-later (U, recalled). Node trees are data-blocks
inside the binary `.blend` file; fields (functions evaluated per element) flow beside geometry (round one read
the manual's fields page, P there; the manual's introduction could not be read today: the page returned only
navigation). There is no text form of its own, but third-party Python front ends generate the trees: one reads
`@tree` functions and builds the node tree, its README saying that large trees become unmanageable as nodes
(README read, P). Meshes, curves, instances, volumes; no building elements (Bonsai is separate). `.blend` is
a memory dump with an embedded struct table, not an interchange format (U).

**Houdini VEX and HDAs.** SideFX; proprietary. VEX is "loosely based on C" with ideas from C++ and the
RenderMan shading language, a small fast language for shaders and custom nodes, close to compiled speed
(reference index read, P); it runs over points or primitives inside nodes (U for the per-element model,
recalled). An HDA (digital asset) packages a node network with a promoted parameter interface as a file;
it is the unit of reuse and the nearest thing here to a "generator with typed parameters" (U, recalled).
Closed format; needs Houdini or its engine. Not importable.

**Vectorworks Marionette.** Vectorworks (Nemetschek); proprietary. Each node is a Python script that declares
its ports and the code run when the network executes; the network is traversed and one composite Python script
is built from the nodes' code (developer wiki, U via search; the vendor's help and wiki refused scripted
requests: 403). Text2BIM (family 6) took its tool list partly from Marionette's BIM nodes (P, the paper).
Generates Vectorworks objects, including BIM ones. Not importable outside the product.

**Sverchok.** Open-source add-on for Blender; GPL-3 (README and a source header read, P). Node trees for
parametric geometry, with its own JSON import and export of trees (the importer's source header read, P).
Meshes and curves; IFC only through Bonsai's own nodes (U). GPL and bound to Blender's Python: not usable.

**Is any of these open and documented enough to import?** The containers, yes (`.ghx` XML, `.dyn` JSON,
Sverchok JSON). The semantics, no: a graph is a list of calls into a host's node library, and that library is
the language. Importing a file means re-implementing every node it uses, with that host's list-matching
rules (data trees, replication, fields). Only DesignScript has a published specification. Inference: import
is realistic only for a small fixed subset (numbers, ranges, arithmetic, a few geometry calls), which is not
what real definitions contain. Confidence medium: no count of nodes used in typical files was made.

### 2.5 BIM-oriented generation

**Archicad GDL.** Graphisoft (Nemetschek); a proprietary language interpreted only by Archicad; its reference
guide is public. A library part is a parameter table plus scripts: a master script run before each of the
others, a 2D script (plan symbol), a 3D script (model), a properties script (quantities and listing), a
parameter script (allowed values), and an interface script (the custom settings dialog) (vendor help and GDL
centre, U via search; the GDL centre's own pages returned 404 at the addresses tried). The language is
BASIC-like with a transformation stack, for example `ADDZ sill`, `BLOCK w, t, h`, `DEL 1` (U, recalled, not
re-read). It generates one BIM object (door, window, stair, furniture) with 2D, 3D, properties and UI from
one definition. No browser implementation. The lesson is the **shape of a library part**: one definition that
yields the plan symbol, the solid, the schedule values and the form, with parameter ranges declared as data.
Weakness: one object per script, no model-wide generation, and a 1980s syntax that tools and LLMs know little
of (inference).

**Revit family parameters and formulas.** Autodesk; proprietary. A family is geometry constrained to
reference planes and labelled dimensions; parameters are typed (length, angle, yes/no, material), belong to
type or instance, and may be formulas over other parameters with arithmetic, trigonometry and a conditional
(U, recalled; Autodesk's help page is script-rendered and returned nothing). It is constraint solving over
dimensions plus spreadsheet-like formulas, not a script; there is no loop, so arrays are driven by a count
parameter. The app's V204 feature records and expressions are this layer (round one).

**Hypar Elements.** Hypar; MIT (LICENSE read, P). A C# library of building element classes (the `Wall` class
read: a profile extruded to a height, with a list of openings, material, transform, id and name, P), with its
own kernel, free of host applications, serialising to JSON, IFC and glTF, and with JSON schemas from which
element types are code-generated (README and `Model.json` schema read, P: a model is a transform plus a
dictionary of elements keyed by id). A generator ("function") is C# code that takes typed inputs and returns
a model. .NET; a browser playground is listed in the repository (P) but its size was not read. **The nearest
prior art to what the app needs:** typed elements as plain JSON, generators as functions with a declared
input schema. Weakness: the generator itself is still C#; only its inputs and outputs are data.

**IfcOpenShell's Python API** (`ifcopenshell.api`). IfcOpenShell project; LGPL-3.0-or-later by its metadata,
but the WebAssembly wheel contains CGAL's GPL code (this repository's `research-ifcopenshell-app.md`, P
there), so under the app's rule it is a separate program in the Python worker. A program is a sequence of
high-level calls; its geometry guide uses, in order of frequency, `context.add_context`, `root.create_entity`,
`geometry.edit_object_placement`, `geometry.assign_representation`, `unit.assign_unit`, `type.assign_type`,
`material.add_layer`, `geometry.add_wall_representation`, `project.create_file` (the guide's source read and
counted, P). In words: create a file, a project and units, a context, then create an `IfcWall`, give it a
wall representation of a length, height and thickness, place it, assign its type and container. Imperative
script; generates real IFC elements with types, property sets and relations. Runs client-side in Pyodide
(the repository already loads it, V176). The only language in this survey that both produces standard BIM
elements and is already runnable in the app. Weakness: verbose, IFC-shaped rather than design-shaped, Python
in a worker with a multi-megabyte runtime, nothing keyed for re-runs.

**Bonsai (BlenderBIM).** Same project; GPL-3.0-or-later (README table, P). An authoring interface over that
API inside Blender, not a language. Not usable; shows the API is enough to author whole models.

**Topologic / topologicpy.** Wassim Jabi (Cardiff) and collaborators. topologicpy's README states LGPL (P);
the core is C++ on OpenCascade 7.8 (core README, P). A building is described as non-manifold topology: a
cell complex of cells sharing faces, with apertures, plus graphs derived from it (adjacency, access) and
dictionaries of attributes (P). It describes spaces and their relations rather than walls; elements come from
converting faces. No browser build found (U); the OpenCascade dependency puts it in the 20 MB class.
The idea to borrow: rooms and their shared faces as the primary model, walls derived.

**COMPAS.** ETH Zurich (Block Research Group) and the COMPAS Association; MIT; a core "written in pure
Python" with extensions wrapping CGAL, libigl and others (README and LICENSE read, P). A framework of data
structures (mesh, network, assembly) with JSON serialisation, not a building language. Pure-Python core means
it could load in the app's Pyodide worker (inference, not tested).

**Speckle objects.** Speckle Systems; the SDK is Apache-2.0 and its README says the object model now lives
in the SDK, the separate Objects package being a deprecated shell (README, P). A transport and object model
(a base object with dynamic properties, hashed and serialised as JSON), with client-side JavaScript loaders:
`@speckle/objectloader` 2.31.14, Apache-2.0, 74 KB (registry, P). It carries results, not rules.

**Khepri and Rosetta** (ADA group, Lisbon). Round one (`execution-and-identity.md`, P there): portable
programs in Julia or Racket calling element operations (slab, wall, door with host) on several back ends;
everything is deleted and re-made on each run. Khepri's Julia package today says it is restricted to the
AutoCAD back end (README, P). No browser build.

**IFC itself is not a generation language.** It records the result: types, occurrences, placements, property
sets, relations. It has parametric pieces (profile definitions given by dimensions, extrusions and sweeps,
material layer sets), but no variables, expressions, conditions or repetition, and no record of how an
element came to be (round one 4.8, P there; the IFC documentation page for parameterised profiles refused
scripted requests today, so that detail is U). IFC 5's alpha examples are JSON with a composition model in
the USD manner (layers over layers), and its repository says they are preliminary and not for production
(README, P): still data, not rules.

**CityGML / CityJSON.** CityJSON has an Extensions mechanism (a JSON-schema file adding object types and
attributes, names starting with `+`) and states that only linear and planar primitives are allowed (spec
source read, P). No procedural or parametric extension appears in the specification (P for the absence in
the text searched). Procedural generators that write CityGML exist as tools (U), not as part of the format.

**bSDD and IDS.** buildingSMART. IDS is an XML file of specifications, each with an applicability part
(which elements) and a requirements part (what they must have), built from facets: entity, attribute,
classification, property, material, part-of (user manual read, P). bSDD is a dictionary service of classes
and properties. Both state what a model must contain; neither makes anything. They matter as the **check**
after generation: Text2BIM runs a rule-based checker over the IFC export and feeds the faults back (P).

**What the family shows.** BIM-aware generation exists in three forms: per-object scripts (GDL), element
libraries called from a general language (Hypar, IfcOpenShell, Khepri), and constraint-plus-formula families
(Revit). None is a small declarative language for a whole building; each leans on a host language.

### 2.6 Natural language and learned generation as an input layer

What matters here is the **intermediate language** each system makes the model write, and why.

| System | Year | Emits | Why, in its own words | Level |
|---|---|---|---|---|
| DeepCAD | 2021 | a sequence of sketch and extrude commands as vectors | CAD operations are like a language; 178,238 models | P (abstract) |
| Text2CAD | 2024 | the same command sequences, from text | first text-to-parametric-CAD; about 170K models, 660K prompts | P (abstract) |
| CAD-MLLM, CAD-GPT, CadVLM | 2024 | command sequences or sketch primitives | CAD-GPT: multimodal models "still struggle with inferring accurate 3D spatial location and orientation" | P (abstracts) |
| CADCodeVerify | 2024 | CadQuery (Python) | chosen over OpenSCAD because Python is common in training data and CadQuery is more concise | P (paper) |
| CAD-Recode | 2024 | CadQuery-style Python | pre-trained LLMs have seen Python; the output can be read and edited by an ordinary LLM | P (abstract) |
| Text-to-CadQuery | 2025 | CadQuery | command sequences "pretrained models cannot directly handle"; code needs no new model; best top-1 exact match 69.3% | P (abstract) |
| CAD-Coder (two papers) | 2025 | CadQuery | one reports 100% valid syntax after fine-tuning on 163K pairs; the other adds a geometric reward | P (abstracts) |
| CADmium | 2025 | a JSON form of the CAD sequence | fine-tuned code models on 170K annotated models | P (abstract) |
| "Don't mesh with me" | 2024 | CSG as Python scripts | meshes lack precision for engineering | P (abstract) |
| Zoo Text-to-CAD | 2023 on | KCL, run on the vendor's engine; returns code and B-rep | every result is an editable feature tree | U (search summary of vendor pages; their API page was 404 at the address tried) |
| 3D-GPT | 2023 | parameter values for an existing procedural generator | the model fills parameters; the generator makes the geometry | P (abstract) |
| LayoutGPT | 2023 | a style-sheet-like text (CSS) of boxes | LLMs plan layouts well in a familiar declarative syntax; 20 to 40% over text-to-image baselines | P (abstract) |
| Holodeck | 2023 | spatial relation constraints between objects, then a solver | "to address the challenge of positioning objects correctly": the model states relations, an optimiser finds coordinates | P (abstract) |
| Tell2Design | 2023 | floor plans directly (sequence to sequence) | 80K plans with language instructions; designs must meet constraints image models miss | P (abstract) |
| Text2BIM | 2024, v2 2025 | Python calling 26 high-level tool functions over a BIM tool's API | imperative code expresses geometry and semantics in "the minimal and most flexible text format"; it can mix tool calls with logic, which JSON function calling cannot; the plan stage uses structured text with coordinates, which worked better than SVG/XML or images | P (paper) |
| MCP4IFC | 2025 | tool calls for common elements, and generated IfcOpenShell Python beyond them | predefined element functions first, code as the escape hatch | P (abstract) |

**Evidence for an LLM-writable text format.**
- The field moved from special token sequences to code or structured text in two years; every 2025 system in
  the table emits a language a person can read (P, the table).
- Compile rates without fine-tuning (CADPrompt, 200 objects, CadQuery): GPT-4 92 to 96%, Gemini 85%, CodeLlama
  64.5 to 67% (P, the paper's Table 2).
- Text2BIM: 25 prompts, three runs each, three general models, no fine-tuning; rule-check pass rates mostly
  above 0.95 after up to three review passes; reviewers resolved about 70% of detected issues (P).
- The successful building systems give the model **a small vocabulary of element-level calls** (26 in
  Text2BIM; a predefined set in MCP4IFC), not a geometry language and not raw IFC (P).
- Holodeck and LayoutGPT show the split that works for layout: the model states relations or boxes in a
  declarative form, deterministic code places things (P, abstracts).

**Evidence against, or limits.**
- Compiling is not being right: in CADCodeVerify 48% of errors were structural and 18% logical; the verifying
  model answered its own questions correctly 64.6 to 68.2% of the time; refinement past two rounds did not
  help (P).
- Text2BIM's own limits: no stairs, columns or beams; illogical door and window placement; no grounding in
  codes or structure; text-only agents "struggle with 3D spatial reasoning"; local fixes cause new clashes;
  experts saw "a significant gap from real-world designs"; long prompts drop requirements (P).
- **A new format has no training data.** Two papers chose CadQuery precisely because models already know
  Python (P). An app-specific rule format starts from zero and must be taught in the prompt (schema plus
  examples) every time. What offsets this: JSON is itself well known to models, constrained output can force
  validity against a schema, and CADmium trained on a JSON form successfully (P for CADmium; the rest is
  inference).
- Text2BIM argues code beats JSON function calling because code can loop and compute (P). A pure data format
  must therefore have repetition and expressions built in (as a split grammar's repeat and the app's V204
  expressions do), or the model will have to enumerate (inference).
- An offline one-file app has no model: the LLM is outside, and the format is what crosses the boundary by
  copy and paste or file. That favours text a person can check before it runs (inference).
- Visual against textual for people: round one (`execution-and-identity.md` F8, P there): the ADA group moved
  from "text is better" to a hybrid, nodes for exploration and text for scale.

### 2.7 Interchange for parametric definitions

- **STEP.** ISO 10303 has had resources for procedural and constrained models for years (Parts 55, 108, 111),
  demonstrated by a NIST-affiliated prototype; AP242's current edition lists a parametric and constrained
  geometry model. No evidence was found of a commercial CAD system exchanging construction history this way
  (all U: search summaries; the ISO texts are paywalled). In practice STEP carries the resulting B-rep.
- **IFC.** Parametric profiles, swept solids, material layer sets and types: parameters of a shape, not a
  procedure (2.5). IFC 5 alpha is a layered JSON composition (P).
- **OpenUSD.** `UsdProc` holds one schema, a generative procedural prim that carries its inputs as
  properties for a downstream system; USD does not define how it is evaluated (API page, P). Variant sets
  switch between authored alternatives; they are choices, not parameters (U, recalled).
- **glTF.** None; a delivered asset format (this repository's `research-gltf.md`).
- **Vendor carriers.** Esri's `.rpk` (compiled CGA plus assets), Houdini's HDA, Grasshopper's `.ghx`,
  Dynamo's `.dyn`: each portable only to its own engine.

**There is no open, implemented standard for a parametric or procedural model.** Each tool's definition is
its own. Whatever the app chooses is the app's format; the realistic interchange is the result (IFC, glTF),
plus the definition kept as text in the project file. Confidence medium-high: absence is hard to prove.

## 3. The comparison

By the coordinator, from the entries in part 2. Criteria fixed in the brief before the survey.

| Language | Makes BIM elements | A non-programmer can write it | An LLM can write it (evidence) | Client-side under an allowed licence | Diffs as text | A useful subset in a few hundred lines of ES5 |
|---|---|---|---|---|---|---|
| OpenSCAD | No | With effort | Yes, but papers preferred CadQuery | No: GPL | Yes | The language no; a CSG tree as data yes |
| JSCAD | No | No: JavaScript | Likely (JavaScript); not measured | Yes, MIT, but it is code to run | Yes | No: it is a program |
| CadQuery, build123d | No | No: Python | Yes: 85 to 96% compile for general models (CADPrompt) | No: needs OpenCascade | Yes | No |
| KCL (Zoo) | No | Through direct manipulation | Vendor's own text-to-CAD (U) | No: geometry on their servers | Yes | No |
| CGA and split grammars | Shapes with names, not typed elements | Rules as data: yes, with a form | Not measured | Ours: 50 lines of core (e02) | Yes | Yes |
| L-systems, Wave Function Collapse | No | No | Not measured | Small and implementable | Rules yes | Yes, but they do not fit building elements well |
| Grasshopper `.ghx`, Dynamo `.dyn` | Through host nodes only | Yes, visually | Not measured | No engine in the browser; the files are readable | Poorly: ids and layout | The container yes; the node libraries no |
| DesignScript | Through Revit nodes | Partly | Not measured | No | Yes | Its ideas (one assignment per name, replication) yes |
| GDL | One object per script | No | Little known to models (inference) | No: Archicad only | Yes | Its shape (one definition gives plan, solid, schedule, form) yes |
| Hypar Elements | Yes | No: C# | Not measured | No: services | Yes | Its element classes as a vocabulary yes |
| IfcOpenShell API | Yes | No: Python | Yes: MCP4IFC uses it as the escape hatch | Already in the app's Python worker (LGPL, separate file) | Yes | No, and no need: it is already carried |
| A small app format: rules and element calls as JSON | Yes, by construction | Through a form; readable as text | Plausible: JSON is well known, a schema can force validity; untested here | Ours | Yes | Yes |

## 4. What this means for the app

The coordinator's reasoning from the survey: inference, not a source's statement.

- **Adopt as is:** none. The only BIM-aware language already inside the app's reach is IfcOpenShell's Python
  API in the existing worker, and it is an escape hatch for later, not the everyday language: it is slow to
  start, it is code, and it writes IFC, not the app's own elements.
- **Import from:** nothing worth a phase. `.dyn` and `.ghx` can be read, but a graph is only as useful as its
  node library, and those belong to Revit and Rhino.
- **The app's own format should borrow:**
  - from CGA: a scope, split, repeat, and rules as named data;
  - from GDL: one definition that yields the plan symbol, the solid, the schedule values and the form, with
    the allowed range of each parameter declared;
  - from DesignScript: one assignment per name (so order does not matter and the dependency graph is the
    program) and replication (a call applied to each item of a list without a loop);
  - from Text2BIM and MCP4IFC: a small vocabulary of element-level calls (wall, slab, opening, column, roof,
    room), not geometry;
  - from Holodeck and LayoutGPT: state relations and boxes; let deterministic code place things;
  - from Dynamo's file: permanent ids on nodes, and the layout stored apart from the logic.
- **Why text matters even with a form and a canvas:** an offline one-file app has no model inside it. A rule
  set that is plain, schema-checked text can be written by a model outside the app, pasted in, read by the
  owner, and refused if it does not validate. That is the cheapest route to "describe it and get a building".

## 5. Not done in this note

The search log and the reference list were not written (the researcher was stopped). Deliberate
counter-evidence is inside 2.6 only. No independent second reading was made of this round: nothing in it is a
number or rule the code will use; it informs decisions 11 to 13 in the main note.
