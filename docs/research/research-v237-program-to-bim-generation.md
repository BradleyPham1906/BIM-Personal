# V237 — Program-to-BIM generation

## Decision and verdict

**Question:** How should approved program and schematic records become BIM objects without losing requirement identity?  
**Verdict:** Generate stable typed spaces first, then optional bounding and contained elements. Keep the program requirement, spatial concept and BIM occurrence related but distinct. Export IFC-compatible data and use IDS-style information checks, while retaining app-specific generative rules in the project file.

## Evidence

IFC defines IfcSpace as a functional area or volume associated with a storey or site. It participates in the hierarchical spatial structure, can be a group, element or partial space, contains elements, has physical or virtual boundaries, and carries a number/name, descriptive name and functional type.[^https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSpace.htm]

buildingSMART IDS provides machine-interpretable requirements and automated IFC information checking for entities, classifications, properties, values and relations. IDS is intentionally limited to alphanumeric information and does not validate geometry.[^https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids]

The platform already imports IFC2x3, IFC4 and IFC4.3 using its pinned cc-ifc engine, maps storeys to levels and reads GlobalId and property sets. It does not yet write IFC or turn imported solids into editable walls.[^https://app.notion.com/p/a851a33d06eb4be9a73cc8c8bf149b3e]

The algorithmic-design research concluded that generated elements require semantic stable keys, in-place updates and separately stored manual overrides; IFC carries results, not the generating rules.[^https://app.notion.com/p/419cbfcc3a388166aaf4f10da9849507]

## Identity chain

Maintain separate stable records:

- Requirement ID → what was requested.
- Program-space ID → planned function and criteria.
- Schematic-space ID → placed concept instance.
- BIM-space ID / IFC GlobalId → geometric occurrence.
- Generated element key → walls, doors, slabs or other elements derived from that space.

Relationships record derivation and revision. Deleting or merging a schematic space must not erase the original requirement history.

## Generation stages

1. Create typed space occurrences by building/storey.
2. Produce virtual or physical boundaries from approved schematic outlines.
3. Generate selected enclosing elements with V228 stable keys.
4. Add names, numbers, functional type, quantities, classification and approved properties.
5. Map information requirements to an IDS-compatible validation profile where possible.
6. Export IFC and re-import it through the existing reader.
7. Compare identities, hierarchy, quantities, properties and geometry summaries.

## Acceptance criteria

- Stable space IDs survive non-destructive regeneration.
- Name/number, LongName, type, storey, quantities and property mappings are deterministic.
- IFC hierarchy is Project → Site → Building → Storey → Space.
- Export/re-import preserves GlobalIds and required alphanumeric information.
- Every generated BIM space links to its requirement and approved program revision.
- Failed mappings and unsupported custom requirements are reported.
- IDS-style checks identify missing or invalid properties with reproducible pass/fail results.
- Rules and graph definitions remain in the app's project file rather than being falsely represented as standard IFC semantics.

## Alternatives and limitations

Generating complete walls, doors and slabs immediately would couple V237 to every construction-detail rule; begin with spaces and boundaries. IDS cannot prove geometric adjacency, area fit, path compliance or constructability, so V238 needs separate geometric analyses. IFC interoperability varies by model view and receiving tool; round-trip testing must use a published fixture set rather than one successful sample.
