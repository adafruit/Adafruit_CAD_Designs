# ESP32-S31 Function CoreBoard-1 SKADIS Mount

Hangs the Espressif ESP32-S31-Function-CoreBoard-1 edge-on from an IKEA SKADIS pegboard. The board screws to two M2 heat set inserts in the mount. Hole positions are checked against the Espressif dimension drawing (DXF).

![Turntable render](<ESP32-S31 Function CoreBoard-1 SKADIS Mount.gif>)

Mounted edge: The 55 mm edge with no connectors. The module's antenna overhangs this edge, so the board stands 7 mm off the spine.

Espressif does not publish a 3D model of this board, so the clash check used a stand-in built from the dimension drawing. The module height (3.2 mm) is assumed.

## Files

| File | What |
|---|---|
| `.3mf` | Ready to slice, print flat as oriented |
| `.step` | For any CAD tool |
| `.FCStd` | FreeCAD source, dimensions in the `Spreadsheet` |

## Hardware

| Part | Qty |
|---|---|
| M2 heat set insert, for a 3.3 mm hole up to 3.3 mm deep | 2 |
| M2 x 4 screw | 2 |
