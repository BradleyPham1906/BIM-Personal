# Presentation boards, a cleaner Analyze, a cleaner right panel

The owner's notes (2026-10-04), with research into how the leading tools do each. In our own
words; nothing copied. PIPELINE.md carries the phases.

## 1. Presentation: boards that are designed like Figma and stay connected like Archicad

**What the owner asked for.** Presentation that works like Adobe, Canva or Figma: elements on
layers, transparency and the like, every one editable, with the data still connected.

**What the tools do.**

- **Figma: the layer model.**
  - Every element is a layer in one tree. Frames hold children; groups, locking and hiding work
    on any branch.
  - Each layer has an opacity and one of 16 blend modes (normal, darken, multiply, lighten,
    screen, overlay and the rest).
  - A mask shows its siblings only inside its shape.
  - Auto layout lets a frame space and resize its children as rows or columns.
  - Components and their variants make an element reusable: change the main one and every copy
    follows.
  - Sources: [blend modes](https://help.figma.com/hc/en-us/articles/360040667874-Apply-blend-modes-to-layers-fills-and-effects),
    [effects](https://help.figma.com/hc/en-us/articles/360041488473-Apply-effects-to-layers),
    [combining layers](https://help.figma.com/hc/en-us/articles/26610806345623-Layers-101-Combine-layers),
    [masks](https://blog.logrocket.com/ux-design/using-layer-masks-figma/).
- **Archicad: the model link.** A layout book holds layouts that inherit a master layout (sheet
  size, title block). Drawings placed on a layout stay linked to their source views and update
  when the model changes. Autotext places project data (project info, drawing name and number,
  layout counts) as live text.
  Sources: [Graphisoft help: layout and drawing IDs](https://help.graphisoft.com/AC/28/INT/_AC28_Help/070_Documentation/070_Documentation-93.htm),
  [master layout autotext](https://community.graphisoft.com/t5/Documentation/New-Autotext-Options-for-Master-Layout-and-Subset-Information/ta-p/339123).
- **SketchUp LayOut: editing a linked view.** A viewport keeps a dynamic link to the model;
  Auto-render redraws it when the model changes. A property changed on the page (scene, style,
  scale) becomes an override, marked and with a Reset button. An overridden viewport no longer
  follows the model until it is reset.
  Sources: [managing model references](https://help.sketchup.com/en/layout/managing-model-references),
  [rendering models](https://help.sketchup.com/en/layout/rendering-models).
- **Canva and Adobe Express.** Templates and brand kits (colours, fonts, logos) make a good-looking
  board fast. Alignment guides and smart spacing keep a page tidy.

**What it means here.** A **board** is a sheet you design on. Every element sits in one layer tree
with opacity, a blend mode, masks, lock and hide.

Elements are either drawn (shape, text, image) or **live**:
- a view of the model;
- a schedule;
- a legend;
- an analysis result (sun hours, cut and fill, solar);
- a number (GBA, cut volume, a site area);
- text bound to project data (autotext).

Each live element stays linked to its source and redraws when the model changes. Edit one on the
board and the edit becomes an override, marked, with Reset (LayOut's rule). Nothing goes stale
silently.

The canvas 2D API already has the blend modes (`globalCompositeOperation`: multiply, screen,
overlay, darken, lighten, colour-dodge, colour-burn, hard-light, soft-light, difference,
exclusion, hue, saturation, color, luminosity), `globalAlpha` for opacity, and `clip()` for masks.
SVG and PDF export map them to `mix-blend-mode`, `opacity` and `clipPath`.

## 2. Analyze: a tidy list, and results that become layers

**Today.** Twelve cards in one long column. Every card has its own row of buttons and some titles
wrap. The states (On, Off, Check, Out of date) look different in different places. Nothing groups
them and nothing searches them. A result cannot be kept: it is drawn over the plan, and the next
run replaces it.

**What the tools do.**

- **QGIS.** A processing run can write its outputs as layers, temporary or saved, into a named
  group in the Layers panel.
  Sources: [the Toolbox](https://docs.qgis.org/3.44/en/docs/user_manual/processing/toolbox.html),
  [configuring Processing](https://docs.qgis.org/testing/en/_sources/docs/user_manual/processing/configuration.rst.txt).
- **Figma's UI3.** The panel was rebuilt to keep the work centre stage:
  - what matters most goes first, and rarely used fields go away;
  - related fields are merged into one section;
  - the panels can be minimised.
  Sources: [behind the redesign](https://www.figma.com/blog/behind-our-redesign-ui3/),
  [our approach to UI3](https://www.figma.com/blog/our-approach-to-designing-ui3/).

**What it means here.**

**The list.** Analyses become a compact list, grouped: Model, Site and terrain, Structure,
Environment. Each row carries a name, one status chip in one style, and one primary action, with
the rest in a menu.

**A row opens a detail view:**
- settings;
- the last result, with its legend and numbers;
- when it ran and whether it is out of date;
- **Add as Layer**.

**Results as layers.** A run's result becomes a layer in Layer Management (an "Analysis" group),
named for what it shows and when ("Sun hours, 21 Dec"). It can be shown, hidden, faded and
locked. It stays linked to its run and says when the model has moved on.

The site's **Data Layers** (V134) join the same tree under a "Data" group, so the plan has one
list of what is drawn.

## 3. The right panel: minimal, consistent, easy

**Today:**
- a tab strip;
- uppercase group headers, each with its own arrow;
- rows of label and value in several input styles;
- groups that pile up (Identity Data, Statistics, History...);
- long lists inside groups.

**The direction (Figma UI3, and the app's own rule: Properties follow the selection):**

- **What matters first.** For an element: what it is (type, instance) at the top, then its
  geometry in one merged section, then its data.
- **One row grid.** The label column is the same width everywhere. All inputs share one style.
  Headers are in sentence case, with fewer borders and more air (spacing on a 4 and 8 grid, a
  three-step type scale).
- **Less on screen.** Rarely used fields go behind "More". Long lists (history, changes, bands)
  show the first few and "Show all".
- **Every group, the same pieces.** A header with its own + or menu, a body, and an empty state
  that says what to do.
- **Light and dark** from the same tokens. A resizable panel, and a Minimize UI toggle.
