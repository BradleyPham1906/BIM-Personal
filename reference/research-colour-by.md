# Research: colour by property (V136)

The owner's screenshots asked for this twice:
- **GeoLibre:** Manhattan's buildings coloured by the era they were built, with a legend and an
  opacity per layer.
- **Rhino and Grasshopper:** context buildings drawn as one red massing.

Giraffe calls it a lens, and Revit a colour scheme.

## What the others do

- **Giraffe's lenses.** A lens colours every feature by one property, such as usage, height or a
  custom field, with a legend, and the lens table lists each value's total. The lens is one choice
  for the whole project, and it changes the view, not the data.
- **Revit's colour schemes.**
  - A scheme colours rooms or areas by a parameter.
  - **By value:** one colour per value.
  - **By range:** the range is split into steps, each with its colour.
  - Its legend is an annotation that lists only the values in the view.
- **GeoLibre, and MapLibre's data-driven styles.**
  - **Categorical:** a `match` expression, one colour per value, "Other" grey.
  - **Numeric:** an `interpolate` or `step` expression over a ramp.
  - Each layer has an opacity, and the legend shows each styled layer.

## What V136 does

- **One lens for the model,** kept on the site (`A3D.site.lens`), so it is saved, undone and loaded
  with the project, like V105's room colour fill.
- **By usage, level, type, layer, material, height, or any property.**
  - A property is a name an object carries: an OSM tag on the context (V133), an attribute
    imported with GeoJSON (V132), or a context field (`height`, `heightFrom`).
- **Categories:**
  - usage keeps each usage's own colour (V131);
  - level follows level order;
  - the rest take the twelve scheme colours of V105, in name order. The same value is therefore
    one colour on every level and in every view.
- **Numbers:** six equal steps from the lowest to the highest, a light-to-dark yellow, orange and
  red ramp (ColorBrewer's YlOrRd). A number in a text field (`"7"`) counts as a number.
- **No value:** a neutral grey, and a "no value" row in the legend, so nothing is silently
  misread.
- **Where it applies:** the lens colour is used where every solid takes its colour, the GL face
  pass and the 2D face loop. In 2D it is drawn over Presentation's fill, because a lens asked for
  is the point of the view.
- **The legend** is one panel at the top left, below V105's room legend.
  - It lists the lens, then each data layer coloured by an attribute.
  - Each row has its colour and count. Only the steps that hold something are listed, and past
    fourteen rows it says how many more.
  - Like the room legend, it is not printed on sheets.
- **Data layers:** each layer has Colour by (one of its attributes) and an opacity (10 to 100%),
  both undo steps.
  - Coloured by an attribute, an area is filled more strongly (0.5 rather than 0.16), so a zoning
    map reads as one.

## Not in V136

- A lens table of totals per value (Giraffe's): the usage areas already have one in V131.
- Choosing the colours by hand, and ranges by hand: the scheme and the ramp are fixed for now.
- A legend placed on sheets as an annotation, as Revit does.

## Sources

- Giraffe: `research-giraffe.md` (lenses).
- Autodesk Revit help: "Color Schemes", "Color Fill Legends".
- MapLibre GL style spec: `match`, `step` and `interpolate` expressions.
- ColorBrewer 2.0 (Brewer, Harrower), sequential YlOrRd, 6 classes.
