# Measure and inspect

## Measure toolbar (available in most workbenches)

| Tool | What it gives |
|---|---|
| **Measure Item** | Length, area, volume, center of gravity of one element |
| **Measure Between** | Distance and angle between two elements. Choose the mode: minimum distance, center to center, and so on |
| **Measure Inertia** | Mass, volume, CoG, inertia matrix. Needs a material applied for mass |

Check **Keep measure** in the dialog to leave the result in the tree as a Measure node.
Results can be exported to text. In Visualization Mode the values come from the tessellated
CGR and are approximate; the dialog says so. Switch that part to Design Mode for exact values.

Tools > Options > General > Parameters and Measure > Measure Tools sets precision and units.

## Clash

Start > Digital Mockup > DMU Space Analysis > **Clash** (also Analyze > Compute Clash in
Assembly Design). Type: Clearance, Contact, Clash. Between: one selection, two selections,
or all. Results list every interfering pair; click one to highlight it in 3D. Works on CGR.
Large assemblies: restrict to two selections rather than "all" the first time.

## Sectioning

DMU Space Analysis > **Sectioning**. Drag the plane, rotate it with the compass that
appears on it. Double-click the section node later to re-enter. The result can be exported
as a 2D view. Works on CGR.

## Compare

DMU Space Analysis > **Compare Products** (license-dependent) shows the difference between
two versions of a part. Check `company/environment.md` for which DMU licenses you have.

## Properties and mass summary for an assembly

Measure Inertia on the top product computes mass for everything loaded. With Visualization
Mode parts the result is based on CGR volumes and the material assigned at the product level,
so treat it as an estimate. For a correct BOM mass, see
`macros/examples/ExportTreeToCsv.CATScript`.

## Interference-free check of a single part against everything

Select the part, Clash, type Clash, "Selection against all". Fast enough even on big
products because it is a bounding-box prefilter first.

## Analyze menu (Assembly Design)

- **Bill of Material**: counts and part numbers, with a Define Formats dialog to pick columns.
- **Constraints**, **Degrees of Freedom**, **Dependencies**: see [04-assembly-basics](04-assembly-basics.md).
- **Updates**: what needs to be updated and why.
