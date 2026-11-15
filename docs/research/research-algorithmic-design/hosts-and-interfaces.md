# Hosts and interfaces: how visual-programming engines attach to their modeller

Research, 2026-11-15, for the owner's question: "Should we have a Grasshopper engine pop up on a tab in the web
app that links to the model, like how Grasshopper runs in Rhino?" Second round; the first is
`../research-algorithmic-design.md` (cited as RAD, by part). Levels: P the source itself was read here; S a
dependable secondary source; U a search summary only (a pointer, not to be used in code). Pages were read
through a fetch tool that returns the page as text digested by a small model: where a P fact rests on such a
digest and not on raw text, it is marked P(d). Raw text was read for the Graphisoft guide (PDF) and for
files on raw.githubusercontent.com. No code was built or run.

Parts 2 to 7 are filled topic by topic; part 1 is written last.

## 1. Summary of findings

Written by the coordinator from the findings below: the researcher was stopped by the account's usage limit
after part 7 and before this part. Levels and confidence are those of the findings cited.

1. Grasshopper's classic link to Rhino is three separate things: a parameter that holds a Rhino object's id
   (in), a preview drawn in the viewport that is not in the document (out, temporary), and a bake that copies
   the result into the document and keeps no link (out, permanent). P, high (2.1).
2. Every vendor who took a graph to a BIM host replaced preview-then-bake with tracked elements that are
   created in the model from the start and updated in place: Rhino.Inside.Revit, the Grasshopper-Archicad
   connection, Rhino 8's Content Cache, Dynamo's binding. P, high (2.1, 2.2).
3. Outside Grasshopper and Dynamo, the common pattern is not a model-wide canvas at all: the rule lives
   inside one object and its inputs are fields in the ordinary properties panel (Blender, Marionette objects,
   Param-O, Houdini assets, Live Components). P, medium to high (2.3).
4. Nothing found is a client-side, permissively licensed graph engine that produces BIM elements and could be
   vendored. That Open Engine has no generative part. P, high (2.4).
5. No vendor ships a node canvas on a phone or tablet; what they ship there is the form (the player). The
   evidence is the absence of examples, not a usability study. Medium (2.6).
6. A survey of 1,982 shared Grasshopper scripts found 97.5% had no modules; unstructured ones were misread by
   every interviewee. S, medium (2.5).

## 2. Findings by topic

### 2.1 Grasshopper in Rhino, and what changed for BIM

**The classic link (Rhino 4 to 7).**

- Grasshopper is a Rhino plug-in with its own window. Rhino's command help: the `Grasshopper` command opens
  the Grasshopper window, a graphical algorithm editor integrated with Rhino's modelling tools; its options
  load the plug-in, show, hide or toggle the window, and enable or disable the solver [R1, P(d)].
  Confidence high.
- **Referenced geometry.** A geometry value in Grasshopper can be a reference: the API's `IGH_GeometricGoo`
  has `ReferenceID` (the Guid of the referenced object), `IsReferencedGeometry`, `IsGeometryLoaded`,
  `LoadGeometry` (loads a referenced, unloaded geometry from the document) and `ClearCaches` (for referenced
  geometry, erases the local copy). The API says not all types support referencing [R2, P(d)]. So the link
  from model to graph is one Guid per value, held by a parameter; the graph keeps a cached copy and reloads
  it. Confidence high.
- That a change to the referenced Rhino object re-solves the graph, that deleting it leaves a missing
  reference, and that a re-drawn look-alike is a different object (a new Guid) come from course material and
  forum posts found by search only [U]; RAD 4.1 has the expiry mechanism itself at P. Confidence medium.
- **Internalised data** copies the referenced value into the parameter and drops the Guid, so the `.gh` file
  carries the geometry and no longer follows the Rhino object [U for the wording; the mechanism follows from
  R2]. Confidence medium.
- **Preview.** Objects that want to draw in Rhino's viewports implement `IGH_PreviewObject`:
  `DrawViewportWires`, `DrawViewportMeshes`, `ClippingBox`, `Hidden`, `IsPreviewCapable` [R3, P(d)]. Preview
  is drawing during viewport redraw, not objects in the document: it cannot be selected, snapped to as
  ordinary objects, saved in the `.3dm`, or put on a layer. Confidence high for the mechanism.
- **Bake.** `IGH_BakeAwareObject.BakeGeometry(RhinoDoc, [ObjectAttributes], List<Guid>)` writes the object's
  geometry into the Rhino document and returns the new object ids [R4, P(d)]. Nothing on the interface keeps
  those ids: a classic bake is a one-way copy, and baking twice makes two sets of objects. Graphisoft's guide
  describes it the same way from outside: geometry embedded with Rhino's Bake, unlike theirs, does not stay
  associated with its generating code [R7, P]. Confidence high.

**What changed for BIM hosts.**

- **Rhino.Inside.Revit** [R5, P(d), raw file from the project's repository; also RAD 4.2]. Components are
  typed by action (query, analyse, modify, create). "Add" components create real Revit elements and each
  output remembers which elements it added, to avoid duplicates. Tracking mode per component: Disabled (can
  create duplicates), Enabled: Replace (new elements each run, replacing the last), Enabled: Update (default;
  changes the existing element where Revit's API allows, else behaves as Replace). The tracking survives
  closing and reopening the file. Each Add output has Highlight, Unpin, Delete and Release; Release stops
  tracking, and the guide warns that this may create duplicates on the next run. Modifying components run in
  Revit transactions. Stated costs: previews need geometry conversion and many of them slow the Revit view;
  many small transactions are slower than one. There is no "bake" step in this model: creating is tracked
  from the start. Confidence high.
- **Grasshopper-Archicad Live Connection** [R7, P, Archicad 29 guide, raw PDF text]. Two programs, two
  palettes: a connection palette in Grasshopper (start connection, connect a document, element preview
  simple or detailed) and a Grasshopper palette in Archicad (Sync Changes to GH, Lock/Unlock GH Elements,
  Select in GH: selects the components that made the selected elements). Generated elements are real Archicad
  elements, not previews, kept associated to their generating code by an id-based method; they are created
  **locked**, and the guide itself compares the locked state to Rhino's preview. Unlock to edit by hand;
  lock again and they revert to what the graph defines, except for parameters the graph does not control,
  which keep the hand-set value. A parameter the graph controls is overwritten on every run. Copies made by
  copy-paste lose the connection. Elements stay in the project when the `.gh` file is absent; reconnecting
  the matching pair of files resumes the link. Input the other way: "AC parameter" components reference
  Archicad points, 2D curves, slabs, roofs and so on, stay associative, and update when "Send Changes" is
  pressed. Each element component has a Boolean Synchronize input, so parts of a graph can be live and
  others not. One graph talks to Archicad at a time; Teamwork is not supported; an open Archicad dialog
  suspends the connection. Confidence high.
- **Rhino 8 Content Cache** [R6, P(d)]. McNeel's own guide calls it smart baking: the component keeps track
  of the objects it baked. Push bakes, or updates what was already baked: it finds the object by its id and
  replaces it, keeping the id, so there are no duplicates and a material assigned by hand in Rhino survives
  the update. A cache has a name (a named collection of objects); Pull reads a cache back into the graph by
  that name. Push can be manual (a button) or automatic (an input set to true; the guide warns it overwrites
  what the component baked before). Without a layer name the objects go to a locked Grasshopper layer. A
  forum guide adds that the old Bake still exists on the component and still duplicates [U]. Known faults
  reported on McNeel's forum: crashes pushing block instances (8.6) and named-content pushes mis-deleted,
  fixed in 8.8 [U]. Confidence high for the mechanism.
- **Grasshopper Player** [R1, P(d); R8, P(d)]. The `GrasshopperPlayer` command loads and runs a `.gh`/`.ghx`
  definition without showing the Grasshopper window; a few added components take the inputs from Rhino's
  command line and send outputs back, so a definition is used as a command by people who do not know
  Grasshopper. A forum report says Rhino 8 opened the file in the editor unless a document property was
  changed [U]. Confidence high.

**Reading.** In fifteen years McNeel and both BIM vendors moved the same way: from "preview, then bake and
cut the link" to "write real objects, remember their ids, update in place, let the user release them". The
Archicad guide's locked/unlocked state and the Content Cache's keep-the-id rule are the same answer RAD 4.2
reached from Dynamo and the split-grammar papers. This is the note's inference from R5, R6 and R7.

### 2.2 Dynamo in Revit

- Dynamo's window beside Revit and its element binding (an element keyed by the node call that made it, the
  ids stored in the `.dyn`, updated or remade on a re-run) are in RAD 4.2 at P and are not repeated.
- **Where the binding is stored decides what goes wrong.** Dynamo for Civil 3D's primer page offers four
  storage settings: none (new objects every run); in the graph (suits one graph for one drawing: run in a
  second drawing, the binding is dropped, and a later run in the first drawing adds new objects beside the
  old); in the drawing (each drawing keeps its own record, so one graph can serve many); and in the drawing
  for Dynamo Player only. A Player run after a run in the main interface creates new objects on top of the
  existing ones; from then on the Player updates them [D2, P(d)]. Confidence high.
- Dynamo's own known-issues page records orphaned elements: if the number of elements a graph made is
  reduced after both files were saved and reopened, the extra Revit elements are not cleaned up on the
  re-run and "clutter" the model [D3, P, raw wiki text]. Confidence high (an old entry: version 0.8).
- **Dynamo Player.** The graph author marks nodes "Is Input"; the Player shows those inputs as a form and
  runs the graph, so a user adjusts a project without learning Dynamo. Supported inputs are listed (object
  selection, categories, levels, file and directory paths, string, Boolean, number, sliders, views and
  others); an unsupported input type is shown as such and ignored, and if it is required the graph will not
  run until it is edited in Dynamo [D1, P(d), the Civil 3D edition of the page; the Revit edition's address
  returned "page not found"]. Confidence high.
- **Generative Design** uses the same graphs as functions: inputs are nodes marked Is Input (sliders,
  Boolean, number, string, Revit selection), outputs are Watch nodes marked Is Output and must be numbers;
  the graph is exported with its dependencies into a study folder [D4, P(d)]. Its four search methods are
  in RAD 4.7. How a chosen result is written into the Revit model was not on the page read: open.

### 2.3 Other hosts

| Host | What the graph is attached to | Where its inputs appear | How results enter the model | Level |
|---|---|---|---|---|
| Archicad Param-O | A library part (an object); the editor has a node tree, a canvas and a model preview | In the placed object's settings (the Length node follows the working units) | The object is placed like any library part; the editor's preview is stated to differ from Archicad's (no textures, no edges, weaker transparency) | P(d) [H1]; that the output is a library part is from the page's wording and the product's place in the help's object chapter, S |
| Vectorworks Marionette | Three forms: a network of nodes drawn in the drawing itself; a wrapper node (the network collapsed into one node); an object node, "Marionette object" (a wrapper converted, optionally with one piece of control geometry) | A Marionette object's instance parameters are edited in the Object Info palette; parameters set by a style are shown but not editable there; "Edit Script" opens the network | The object node is the result; editing a style changes every instance using it | P(d) [H2] for the object and palette; the wrapper and conversion wording is from older help pages found by search, U |
| Blender Geometry Nodes | A modifier on an object; the modifier's node group defines what it does; geometry comes in from the modifier before and goes out to the next | In the modifier panel: the group's inputs, with values per modifier even when the group is shared; a field input can be switched between a value and an attribute | Non-destructive in the modifier stack; a bake panel stores baked data in the file or on disk; applying a modifier (general Blender behaviour, not on the page read) makes it plain mesh | P(d) [H3] |
| Houdini Digital Asset | A node network wrapped in one reusable node, stored in an asset library file | Parameters promoted from inner nodes to the asset node form its interface | Instances of the asset; a change to the asset definition updates all instances | P(d) [H4] |
| Houdini Engine | The same asset loaded in Maya, 3ds Max, Unity, Unreal | The asset's parameters are editable in the host, with viewport handles | The host needs a Houdini Engine licence to run the plug-in: the network is cooked by Houdini, not by the host | P(d) [H5]; the last clause is the note's reading of the licence text, S |
| SketchUp Live Components | A component whose logic is authored outside SketchUp, in Trimble Creator | A "Configure Live Component" parameter window in SketchUp desktop, web and iPad | Authoring or changing a configuration needs an internet connection; a placed one can be copied and used offline; "Detach Definition" makes it ordinary geometry | P(d) [H6] for platforms, Creator and the connection; detach and the parameter window U |
| SketchUp Dynamic Components | A component with attributes and spreadsheet-like formulas (no graph) | The Component Options dialog | The component itself | U (help pages found, not read) |
| Revit families | No graph: a family with typed and instance parameters and formulas, edited in the family editor | The Properties palette and type properties | Instances of the type | Not researched this round; general knowledge, U |

**Reading.** Every row but Houdini Engine is the same idea: the rule lives inside one object, and the place
where a user changes it is the ordinary properties panel. None of these tools gives a model-wide graph a
tab of its own; the graph editor opens only for the author of the object. Confidence medium to high.

### 2.4 Grasshopper-like engines on the web

| Tool | Licence | Runs fully client-side | How the logic links to the model | BIM elements or geometry | Level |
|---|---|---|---|---|---|
| ShapeDiver | Proprietary service | No: Grasshopper runs on their servers; the web viewer shows exposed parameters | The definition is uploaded; referenced Rhino geometry cannot follow (it has pages of forbidden components and output limits) | Geometry | U for the mechanism (the help centre's pages returned titles only); the page titles are P(d) [W1] |
| Rhino Compute and Hops | Compute's code is open on GitHub; it needs Rhino 8 for Windows | No: a Rhino server, local by default, not on macOS | A definition is called as a function; inputs are "Get" components, outputs "Context Bake" and "Context Print": the same components the Grasshopper Player uses; calls can be asynchronous and cached | Geometry | P [W2, raw README]; P(d) [W3] |
| Hypar | Elements library MIT; the platform is a service | No: functions run as services (the library was written to run in micro-services) | A function takes inputs and other functions' models and outputs elements; "overrides" are user edits tied to elements, kept across re-runs | Building elements (C# types, IFC and glTF export) | P [W4, raw README and licence]; overrides U (its docs page returned 404) |
| Speckle Automate | Service, Enterprise only | No: runs on Speckle's infrastructure | Triggered when a new model version is published; results are listed under the automation and not shown in the 3D viewer or model list | Works on model data | P(d) [W5] |
| That Open Engine | MIT (CLAUDE.md; the licence file was not at the address tried) | Yes | `engine_components` is a collection of BIM tools on three.js (viewing, dimensions, plans, DXF export); `engine_clay` is a library to create and edit IFC geometry and build modellers. Neither has a graph, a rule engine or a generator | BIM (IFC) | P [W6, W7, raw READMEs] |
| Nodi (v1) | Apache-2.0 | Yes; three.js and verb (NURBS); "tested on Chrome only" | A node editor and a viewer side by side; its own document, no host model | Geometry | P [W8, raw README]. The README marks v1 deprecated; v2 (v2.nodi3d.com) is said by a news site to be Rust and WebAssembly with its own kernel, licence not found: U |
| Bitbybit | NPM packages MIT. The OCCT kernel package is an MIT-licensed WebAssembly binary whose C++ layer is closed source and not built from the repository | The packages: yes (OCCT, JSCAD and Manifold as WebAssembly, drawn by three.js, Babylon.js or PlayCanvas) | The Rete, Blockly and Monaco editors are on the bitbybit.dev platform, not in the MIT repository's list; "script runners" (one script file) run scripts exported from those editors on any page; some algorithms are tiered platform-only or cloud-only | Geometry | P [W9, raw README and licence] |
| CascadeStudio | MIT | Yes; OCCT in WebAssembly; installable for offline use; states a responsive layout with mobile support | Code-first (JavaScript or OpenSCAD mode); sliders and checkboxes declared in the code appear as a small GUI; a history timeline scrubs the build steps | Geometry | P [W10, raw README] |
| Chili3D | AGPL-3.0 (its C++ module LGPL-3.0); commercial licence on request | Yes; OCCT in WebAssembly | Not a graph: a body is an ordered feature list replayed on rebuild, with tracked references to faces and edges and document variables; direct modelling beside it | Geometry | P [W11, raw README] |
| Zoo Design Studio (KCL) | App MIT; the geometry engine is a hosted service | No: the 3D view is a video stream from their engine over WebSockets | Every point-and-click action edits the KCL code; code and direct manipulation are the same model | Geometry (mechanical) | P [W12, raw README and licence] |
| Mobius Modeller | MIT | Browser application (the README is one line and a link) | Not read | Not read | P for the licence [W13]; the rest U |
| Sverchok | GPL-3.0, a Blender add-on | Not web | Nodes in Blender | Geometry; over 600 nodes | P [W14] |
| Luna Moth, Khepri | see RAD 4.1 | | Program re-run from scratch | | RAD |
| nodes.io, OpenSCAD playground, CadHub | not read | | | | open |

**What matters here.** (1) Nothing found is a client-side, permissively licensed, BIM-producing graph engine
that could be vendored: the BIM-aware ones (Hypar, Speckle, Rhino.Inside, Archicad) are services or desktop
plug-ins, and the client-side ones produce geometry only. (2) Bitbybit, the closest to "Grasshopper in the
browser", keeps its visual editors on its own platform and its OCCT kernel layer closed; the reusable part
is the geometry packages, and OCCT's size is already ruled out in RAD 4.5. (3) Chili3D is AGPL: under the
repository's library rule it could only be a separate program, not joined code. (4) That Open Engine, the
library the owner chose on 2026-11-13, brings no generative part: algorithmic design stays the app's own
work. Confidence high for (1), (3), (4); medium for (2), which rests on one README.

### 2.5 The four interface patterns, and what goes wrong in each

**(a) A separate window or tab with a canvas, linked by references, preview and bake** (Grasshopper, Dynamo;
with tracking instead of bake: Rhino.Inside.Revit, the Archicad connection, Content Cache).

- Two kinds of geometry on screen. Grasshopper's developer has explained on the forum that Grasshopper
  geometry does not exist as far as Rhino is concerned: it is drawn into the viewports and becomes a real
  object only when baked; forum threads show beginners unable to select or render the preview [U, search
  summary of McNeel forum threads]. The mechanism behind it is P (2.1: `IGH_PreviewObject`).
- Baking cuts the link and repeats make duplicates (P: 2.1; Graphisoft says so of Rhino's bake, R7). The
  vendors' own repairs are the evidence that this was a real problem: Geometry Cache, then Content Cache
  (R6); tracking modes in Rhino.Inside.Revit, whose Disabled mode and Release control both carry a
  duplicate warning in the guide (R5); Dynamo's binding (RAD 4.2).
- Tracking has its own failures: orphaned elements when the count shrinks between sessions (D3, P); a
  binding stored in the graph breaks when the graph is run on a second file, and a Player run after an
  editor run stacks new objects on the old (D2, P(d)); forum reports of duplicates and of the link lost
  between sessions in Rhino.Inside.Revit, and that its tracking is by the item's index in the component's
  output, not by Revit id [U]. An index key is the weakest key RAD 4.2 measured (Lipp 2019).
- Who wins when both sides edit. Archicad's rule (R7, P): what the graph controls is overwritten on every
  run; what it does not control keeps the hand-set value; copies lose the link.
- Unreadable graphs. Davis, Burry and Burry 2011 surveyed 1,982 scripts shared by 575 designers on the
  Grasshopper forum: 97.5% had no clusters (modules) and 56% no named parameters; in thinking-aloud
  interviews (four students) every participant guessed the function of an unstructured script wrongly,
  while modular ones could be described [C1, S: the author's own page for the paper, not the PDF]. A small
  interview sample; the survey is the stronger part. RAD (H5) has the Leitao group's evidence that text
  scales better, with its weaknesses.
- Screen space: a canvas and a viewport side by side. See 2.6.

**(b) The graph owned by an object, inputs in the properties panel** (Blender modifier, Marionette object,
Param-O, Houdini asset, Live Components; families and Dynamic Components without a graph).

- No preview-versus-document split and no bake step in normal use: the object is the result (2.3).
- What goes wrong, from the sources read: the editor's preview is not what the model shows (Param-O, H1);
  an edit to a shared definition or style changes every instance (Marionette styles, H2; Houdini, H5),
  which is the point of it and also a way to change things unseen; detaching or applying ends the
  procedural link (Live Components [U]; Blender's apply, general knowledge); the scope is one object, so
  relations between objects (a facade that follows a slab edge) need references across objects, which
  these tools handle weakly or not at all in the pages read. Community criticism of Param-O (basic, slow
  to develop, a character limit on pasted GDL) is U. Deliberate criticism of Geometry Nodes and Marionette
  was not searched in depth: open.

**(c) A player or form that hides the graph** (Dynamo Player, Grasshopper Player, ShapeDiver, Hypar,
Hops as its function form, Live Components' configure window).

- The vendors' reason is the same each time: people who do not know the graph tool can use what an author
  made (D1, R8, both P(d)).
- What goes wrong: only some input types are supported and an unsupported required one stops the run
  (D1); the Player and the editor keep separate bindings, so mixing them stacks objects (D2); a user who
  needs something the form does not offer must go to the author or the editor; the web services compute
  on a server (W1 to W5), which this app cannot do.

**(d) Code and model as two views of one thing** (KCL in Zoo, CascadeStudio, OpenSCAD; Chili3D's feature
list is the same idea with a list instead of text).

- Zoo's README states the principle: every point-and-click action is an edit to the code, so there is one
  model and no second representation to drift (W12, P). CascadeStudio and OpenSCAD are code-first with a
  small declared GUI (W10, P).
- What goes wrong: a text editor is the worst input on a phone; the model is only as editable by hand as
  the code generator is good; and (RAD part 5, option C) it needs a language and an interpreter. Criticism
  from users of these tools was not searched: open.

### 2.6 Small screens

- **Rhino on iPad.** The App Store listing read today describes iRhino 3D as the official Rhino viewer for
  iOS: view and present, AR, markup; no modelling tools and no Grasshopper are listed (version 9.2, 31
  October) [S1, P(d)]. A search summary quoted a forum remark that iRhino is "basically Rhino running on an
  iPad" and users asking for modelling [U]: the listing does not support that. No Grasshopper canvas on
  iOS was found anywhere. Confidence high that none ships; McNeel's intentions are open.
- **Blender on tablets.** The Blender developers' post of July 2025 lists the constraints (one full-screen
  window, relatively small screen, no keyboard or mouse by default, touch and pen) and starts with basic
  object manipulation and sculpting, then Grease Pencil; node editors are not mentioned [S2, P(d)]. So the
  best-resourced open project with a node system did not put its node editor first on a tablet.
- **SketchUp for iPad** offers Live Components only as a configure window: the form, not the graph
  [H6, P(d)].
- **Shapr3D and Onshape** on iPad use a history list or feature list with parameters, not a graph;
  Shapr3D added draggable parameter cards because its history was hard to reach on iPad; Onshape's team
  says selection with a finger was the first problem to solve [U, search summaries of the vendors' pages].
- **Browser node tools.** Nodi v1 says it was tested on Chrome only (W8, P); CascadeStudio states a
  responsive layout with mobile support (W10, P), and it is code plus sliders, not a graph. RAD 4.5 found
  no node-editor library both framework-free and good on touch.
- General remarks found by search only [U]: a phone is too small for a node editor (a TouchDesigner
  community post); dragging wires with a finger hides the target and mis-hits. No usability study of a
  node editor on a tablet or phone was found. Confidence medium: the absence of shipped examples is the
  evidence, not a measurement.

## 3. The four patterns compared

Fit columns are this note's judgement from the findings above, not a source's statement.

| Pattern | Who uses it | How it links to the model | What goes wrong | Fit for a one-file offline browser app | Fit for a phone |
|---|---|---|---|---|---|
| (a) Canvas in its own window or tab | Grasshopper, Dynamo; Rhino.Inside.Revit, Archicad connection, Content Cache as the tracked variants | In: a parameter holds an element id and re-solves when it changes. Out: preview drawn but not in the document, then bake (link cut), or tracked elements updated in place by a stored key | Preview and real objects confused; duplicates on re-bake or after Release; orphans when counts shrink; binding lost between files or sessions; graph overwrites hand edits it controls; large graphs unreadable (97.5% without modules) | Possible with our own ES5 editor (RAD decision 8); the engine is small, the editor is the cost; only the tracked variant is worth building, never preview-then-bake | Poor: canvas and viewport compete; no shipped example found; wires are hard by finger |
| (b) Graph or rule owned by an object | Blender Geometry Nodes, Marionette object, Param-O, Houdini asset, Live Components; Revit families and Dynamic Components without a graph | The object carries its rule; its inputs are fields in the properties panel; the object is the result | Scope is one object; shared definitions change all instances; apply or detach ends the link; editor preview differs from the model | Good: it is what V204's records and V213's generators already are (RAD option A); no editor needed to use one | Good: a form in the properties panel |
| (c) Player or form hiding the graph | Dynamo Player, Grasshopper Player, ShapeDiver, Hypar, Hops, Live Components configure | A saved graph or function with marked inputs; run produces or updates elements | Limited input types; separate bindings for player and editor; users cannot go beyond the form; web versions compute on servers | Good, as the front of (a) or (b): a form generated from marked inputs; must compute in the page | Good: the only pattern the vendors themselves ship on tablets |
| (d) Code and model as one | Zoo (KCL), CascadeStudio, OpenSCAD; Chili3D's feature list | Every direct edit writes code or a feature; the code is the model | Needs a language and interpreter; text is poor on touch; hand-editability depends on the code generator | Poor now (RAD option C); the feature-list form is closer to the app's history than to a language | Poor for text; fair for a feature list |

## 4. Counter-evidence

- **For the canvas (against this note's lean).** Grasshopper and Dynamo are the most used tools of this kind
  and their separate canvas is what users know; a relation between many objects (pattern (b)'s weak point)
  is exactly what a model-wide graph expresses. Forum posts argue a node-and-parameter workflow could suit
  a tablet better than direct selection [U]. The Davis survey shows graphs are written badly, not that
  they cannot be written well: his modular scripts were understood.
- **Against tracking as a cure.** Tracked elements still orphan (D3) and still duplicate when bindings are
  per file or per player (D2); Rhino.Inside.Revit's index-based tracking is reported fragile [U]. Tracking
  moves the problem to the key, as RAD 4.2 found.
- **Against "objects own their rules".** Blender's own next step was node tools and a tablet version that
  starts without nodes; Param-O is criticised by its users as limited [U]; Marionette offers all three
  forms (network in the drawing, wrapper, object) rather than choosing one, which suggests the object form
  alone was not enough for its authors.
- **Against the premise that iRhino only views.** A forum remark says iRhino is being rebuilt as Rhino on
  iPad [U]; the App Store listing read today still describes a viewer [S1].
- **Sources' interests.** R5 to R8, D1, D2, H1 to H6 are vendors' documentation: they describe mechanisms
  reliably and problems sparingly. The problems here come from known-issue pages, warnings inside the
  guides, one academic survey and forum summaries (U).

## 5. Still open

- Graphisoft's help-centre page for the connection redirected and its community article refused the
  request (403); the Archicad 29 PDF guide was read instead, in full text for the linking chapters.
- Vectorworks' 2025 help refused the request (403); the 2026 page for editing Marionette objects was read.
  How a network is stored in the drawing, and the wrapper conversion, are U.
- ShapeDiver's help pages returned titles without body text; its restrictions (forbidden components, output
  limits, computation time) are U. Hypar's overrides page returned 404: U. Speckle's first address 404,
  second read.
- Autodesk's Revit page for Dynamo Player returned "page not found"; the Civil 3D edition was read. How a
  Generative Design result is written into Revit was not read.
- Blender's manual pages are mostly navigation in the fetch tool; the modifier page's body was reached at
  an offset. "Apply" is general knowledge, not read. Bake node and node tools pages not read.
- Houdini: where an asset is cooked under Houdini Engine and the locked/unlocked asset state were not on
  the pages read.
- Nodi v2's licence and whether it works on phones; nodes.io; Mobius Modeller's editor; Luna Moth beyond
  RAD; CadHub; the OpenSCAD playground; BeeGraphy (a browser node modeller that appeared in one search and
  was not read): all open.
- That Open Engine's licence file was not at the address tried (the repository's instructions record MIT).
- The Davis paper's PDF was not read, only the author's page for it: S.
- Deliberate criticism of patterns (b) and (d) was searched thinly. No usability study of node canvases on
  touch devices was found.
- Whether a referenced Rhino object's change re-solves Grasshopper through a document event was not read in
  the API (RAD has expiry itself at P).

## 6. Search log

All on 2026-11-15. "Fetch" is the page-to-text tool; "curl" is raw text.

| Tool | Query or address | Result | Kept |
|---|---|---|---|
| Fetch | developer.rhino3d.com API: IGH_BakeAwareObject, IGH_PreviewObject, IGH_GeometricGoo, ReferenceID | Read | R2, R3, R4 |
| Fetch | docs.mcneel.com Rhino 8 help, grasshopperplayer.htm | Redirect page only | No |
| Fetch | docs.mcneel.com Rhino 8 help, grasshopper.htm | Read: Grasshopper and GrasshopperPlayer commands | R1 |
| Fetch | rhino3d.com/features/grasshopper/player | Read | R8 |
| Fetch, curl | raw.githubusercontent.com mcneel/rhino.inside-revit 1.x guides/rir-grasshopper.md | Read | R5 |
| Search | Rhino 8 Content Cache push bake update | Found the guide and forum threads | Guide read (R6); threads U |
| Fetch | rhino3d.com/docs/guides/grasshopper/baking | Read | R6 |
| Search | referenced geometry, Set one, Internalise data | Courses and forum posts | U |
| Fetch | helpcenter.graphisoft.com live connection guide | Redirect to community home | No |
| Fetch | community.graphisoft.com live connection article | 403 | No |
| Search | Grasshopper-Archicad Live Connection guide | Found help.graphisoft.com/AC/29/INT/GC.pdf | Yes |
| Fetch | that PDF (and the AC25 one) | Too large for the tool | No |
| curl, pdftotext | help.graphisoft.com/AC/29/INT/GC.pdf (22.8 MB, 2,305 text lines) | Read: palettes, parameters, Synchronize, Important Notes | R7 |
| Fetch | help.autodesk.com Revit 2025 Dynamo Player (guessed id); primer2.dynamobim.org (guessed path) | Page not found, twice | No |
| Search | Dynamo Player "Is Input" | Found help pages and the Generative Design primer | Yes |
| Fetch | help.autodesk.com Civil 3D 2024, dynamo_player_require_input | Read | D1 |
| Fetch | refineryprimer.dynamobim.org, redirected to generativedesign.org 03-02 | Read | D4 |
| Search | Dynamo element binding problems duplicates | Wiki, primer page, forum threads | D2, D3 read; threads U |
| Fetch | primer2.dynamobim.org dynamo-for-civil-3d/advanced-topics/object-binding | Read | D2 |
| curl | raw.githubusercontent.com/wiki/DynamoDS/Dynamo/Known-Issues.md | Read | D3 |
| Fetch | docs.blender.org manual: modifiers/generate/geometry_nodes (404); geometry_nodes/introduction (navigation only); modifiers/geometry_nodes at offset 190000 | Last one read | H3 |
| Fetch | app-help.vectorworks.net 2025 Marionette | 403 | No |
| Search | Marionette object node, wrapper, Object Info palette | Help pages of several years | U; one read |
| Fetch | app-help.vectorworks.net 2026 Editing_Marionette_objects | Read | H2 |
| Search | Param-O library part node editor limitations | Help pages and community threads | One read; threads U |
| Fetch | help.graphisoft.com AC29 PARAM-O Editor | Read | H1 |
| Fetch | sidefx.com docs assets/intro; unity/index; products/houdini-engine | First and third read; second is an index | H4, H5 |
| Search, Fetch | SketchUp Live Components; help.sketchup.com FAQ (help.sketchup.com/en/sketchup/live-components was 404) | FAQ read (first 100,000 characters) | H6 |
| curl | READMEs and licences: bitbybit-dev/bitbybit, zalo/CascadeStudio, xiangechen/chili3d, KittyCAD/modeling-app, design-automation/mobius-parametric-modeller, Nodi3d/nodi, mcneel/compute.rhino3d, ThatOpen/engine_components, ThatOpen/engine_clay, hypar-io/Elements, nortikin/sverchok | Read (That Open's LICENSE path 404; a guessed Speckle template 404; mattatz/nodi 404) | W2, W4, W6 to W14 |
| Fetch | developer.rhino3d.com guides/compute/hops-component | Read | W3 |
| Fetch | help.shapediver.com/doc (and two sub-pages) | 404, then titles only | W1, titles |
| Fetch | hypar-io.github.io/Elements; docs.hypar.io overrides | No function text; 404 | No |
| Search | Hypar overrides; Speckle Automate; Nodi v2 | Summaries | U |
| Fetch | docs.speckle.systems/developers/automate/overview (404); .../introduction.md | Second read | W5 |
| Search | Davis Burry "Understanding visual scripts" | Found the author's page | Yes |
| Fetch | danieldavis.com page for the paper | Read | C1 |
| Search, Fetch | Blender "Beyond Mouse & Keyboard"; code.blender.org/2025/07/beyond-mouse-keyboard | Read | S2 |
| Search, Fetch | iRhino iPad Grasshopper; apps.apple.com iRhino 3D listing | Listing read; forum remark U | S1 |
| Search | Shapr3D history; Onshape iPad | Summaries | U |
| Search (counter-evidence) | node editor on iPad, small-screen criticism | Forum posts, no study | U |
| Search (counter-evidence) | Grasshopper preview and bake confusion | Forum threads incl. the developer's explanation | U |

## 7. References

All read 2026-11-15. P(d): read through the fetch tool's digest; P: raw text read.

| Id | What | Address | What was read | Level |
|---|---|---|---|---|
| R1 | Rhino 8 help, Grasshopper commands | https://docs.mcneel.com/rhino/8/help/en-us/commands/grasshopper.htm | Grasshopper and GrasshopperPlayer command text | P(d) |
| R2 | Grasshopper API, IGH_GeometricGoo | https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_Kernel_Types_IGH_GeometricGoo.htm | Members and descriptions | P(d) |
| R3 | Grasshopper API, IGH_PreviewObject | https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_Kernel_IGH_PreviewObject.htm | Members and descriptions | P(d) |
| R4 | Grasshopper API, IGH_BakeAwareObject | https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_Kernel_IGH_BakeAwareObject.htm | Description and both BakeGeometry methods | P(d) |
| R5 | Rhino.Inside.Revit guide, Grasshopper in Revit | https://raw.githubusercontent.com/mcneel/rhino.inside-revit/1.x/docs/pages/_en/1.0/guides/rir-grasshopper.md | Whole page | P(d) |
| R6 | McNeel guide, Content Cache: smart baking | https://www.rhino3d.com/docs/guides/grasshopper/baking/ | Whole page | P(d) |
| R7 | Grasshopper-Archicad Live Connection User Guide (Archicad 29) | https://help.graphisoft.com/AC/29/INT/GC.pdf | Getting started, parameter components, Synchronize, Important Notes (pp. 5-17, 82-84) | P |
| R8 | McNeel, Grasshopper Player feature page | https://rhino3d.com/features/grasshopper/player | Whole page | P(d) |
| D1 | Autodesk help, requiring input for Dynamo graphs (Civil 3D 2024) | https://help.autodesk.com/cloudhelp/2024/ENU/Civil3D-Dynamo/files/Dynamo_Player/dynamo_player_require_input.html | Whole page | P(d) |
| D2 | Dynamo Primer, object binding (Civil 3D) | https://primer2.dynamobim.org/dynamo-for-civil-3d/advanced-topics/object-binding | Whole page | P(d) |
| D3 | Dynamo wiki, Known Issues | https://raw.githubusercontent.com/wiki/DynamoDS/Dynamo/Known-Issues.md | The orphaned-elements entry | P |
| D4 | Generative Design Primer, setting up a graph | https://www.generativedesign.org/03-hello-gd-for-revit/03-02_setting-up-a-graph-for-gd-for-revit | Whole page | P(d) |
| H1 | Archicad 29 help, PARAM-O Editor | https://help.graphisoft.com/AC/29/INT/_AC29_Help/065_PARAM-O/065_PARAM-O-5.htm | Whole page | P(d) |
| H2 | Vectorworks 2026 help, Editing Marionette objects | https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Editing_Marionette_objects.htm | Whole page | P(d) |
| H3 | Blender manual, Geometry Nodes modifier | https://docs.blender.org/manual/en/latest/modeling/modifiers/geometry_nodes.html | Body (from offset 190000) | P(d) |
| H4 | Houdini docs, introduction to digital assets | https://www.sidefx.com/docs/houdini/assets/intro.html | Whole page | P(d) |
| H5 | SideFX, Houdini Engine product page | https://www.sidefx.com/products/houdini-engine/ | Whole page | P(d) |
| H6 | SketchUp help, Live Components FAQ | https://help.sketchup.com/en/sketchup-live-components/frequently-asked-questions | First 100,000 characters | P(d) |
| W1 | ShapeDiver help centre | https://help.shapediver.com/doc/ | Section and page titles only | P(d) for titles |
| W2 | Rhino Compute README | https://raw.githubusercontent.com/mcneel/compute.rhino3d/8.x/README.md | Whole file | P |
| W3 | McNeel guide, the Hops component | https://developer.rhino3d.com/guides/compute/hops-component/ | Whole page | P(d) |
| W4 | Hypar Elements README and licence | https://raw.githubusercontent.com/hypar-io/Elements/master/README.md | First 45 lines; LICENSE.md head | P |
| W5 | Speckle Automate introduction | https://docs.speckle.systems/developers/automate/introduction.md | Whole page | P(d) |
| W6 | That Open engine_components README | https://raw.githubusercontent.com/ThatOpen/engine_components/main/README.md | First 60 lines | P |
| W7 | That Open engine_clay README | https://raw.githubusercontent.com/ThatOpen/engine_clay/main/README.md | First 25 lines | P |
| W8 | Nodi README | https://raw.githubusercontent.com/nodi3d/nodi/main/README.md | Whole file | P |
| W9 | Bitbybit README and licence | https://raw.githubusercontent.com/bitbybit-dev/bitbybit/master/README.md | Lines 1-30, 54, 60-110, 145-149; LICENSE head | P |
| W10 | CascadeStudio README | https://raw.githubusercontent.com/zalo/CascadeStudio/master/README.md | Lines 1-75 | P |
| W11 | Chili3D README | https://raw.githubusercontent.com/xiangechen/chili3d/main/README.md | Feature, architecture and licence lines | P |
| W12 | Zoo Design Studio README and licence | https://raw.githubusercontent.com/KittyCAD/modeling-app/main/README.md | First 40 lines; LICENSE head | P |
| W13 | Mobius Modeller README and licence | https://raw.githubusercontent.com/design-automation/mobius-parametric-modeller/master/README.md | Whole file (one line); LICENSE head | P |
| W14 | Sverchok README | https://raw.githubusercontent.com/nortikin/sverchok/master/README.md | First 45 lines | P |
| C1 | Davis, Burry, Burry 2011, "Understanding Visual Scripts", IJAC 9(4) 361-376 | https://www.danieldavis.com/understanding-visual-scripts-improving-collaboration-through-modular-programming/ | The author's page for the paper | S |
| S1 | App Store listing, iRhino 3D | https://apps.apple.com/gb/app/irhino-3d/id373666504 | Description and version history | P(d) |
| S2 | Blender developers' blog, Beyond Mouse & Keyboard, July 2025 | https://code.blender.org/2025/07/beyond-mouse-keyboard/ | Whole post | P(d) |
| RAD | The first round | `../research-algorithmic-design.md` parts 1, 4, 5, 11 | Read | - |
