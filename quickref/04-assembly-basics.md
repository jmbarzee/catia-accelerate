# Assembly basics (Assembly Design workbench)

Start > Mechanical Design > Assembly Design. Or click the workbench icon.

## Structure

- A **Product** references documents. It does not contain geometry. Deleting a part from a
  product deletes the instance, not the `.CATPart` file.
- Insert > **Existing Component**: select the parent product in the tree, then pick the file.
  Insert > New Part / New Product creates empty ones. Insert > Existing Component With
  Positioning lets you place it on the fly.
- Multiple instances of the same part share one reference. Edit one and all change.
- Make the parent product active (double-click) before inserting. Insert goes into the
  active product.

## Constraints

Toolbar on the right in Assembly Design:

| Constraint | Use |
|---|---|
| Coincidence | Axis to axis, plane to plane, point to point |
| Contact | Surface to surface |
| Offset | Plane to plane at a distance |
| Angle | Plane or axis angle, including parallel and perpendicular |
| Fix | Pins a part to the assembly origin. Fix one part first, always |
| Fix Together | Group parts rigidly |

Constraints appear under the `Constraints` node. They stay red until you **Update**
(Ctrl+U). Green check icons mean solved. Red exclamation means over-constrained or broken.
Right-click a constraint > Deactivate to debug one at a time.

Tools > Options > Mechanical Design > Assembly > Update: set **Automatic** only on small
assemblies. **Manual** on large ones, then Ctrl+U when ready.

## Moving parts

- **Manipulation** icon: drag along an axis or plane without constraints. Check "With respect
  to constraints" to respect existing ones.
- The **compass**: drag it onto a part, then drag the compass arms. Right-click the compass
  > Edit for numeric moves.
- **Snap**: snap one element to another, a quick way to roughly position before constraining.

## Links and context

- Edit > **Links** shows every file the product references and whether it is found, loaded,
  or missing. The first place to look when something shows as a broken node.
- **Contextual links** happen when a part's feature references geometry in another part
  (for example a hole positioned from a mating bracket). The part becomes bound to that
  assembly context. Avoid unless you mean it. Tools > Options > Infrastructure > Part
  Infrastructure > General > "Keep link with selected object" controls whether this happens.
- Define the context: right-click a part > `<name> object` > Define Contextual Links.

## Saving

File > **Save Management** lists every open document, its state (New, Modified, Open), and
lets you Save, Save As, or Propagate Directory. In a PLM-managed site (ENOVIA, Windchill,
Teamcenter, 3DEXPERIENCE), saving is done through the PLM tool, not File > Save.
Read `company/plm-workflow.md` before saving an assembly for the first time.

## Reporting

- Analyze > **Bill of Material**: parts list with counts. Export to text.
- Analyze > **Constraints**: lists all constraints and their status.
- Analyze > **Degrees of Freedom**: what can still move.
- Analyze > **Dependencies**: a graph of what references what.
- Analyze > **Compute Clash**: see [06-measure-and-inspect](06-measure-and-inspect.md).
