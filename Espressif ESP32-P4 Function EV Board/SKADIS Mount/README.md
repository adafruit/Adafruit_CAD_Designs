# ESP32-P4 Function EV Board SKADIS Mount

Hangs the Espressif ESP32-P4-Function-EV-Board edge-on from an IKEA SKADIS pegboard. The board screws to two M2 heat set inserts in the mount. Hole positions are checked against the Espressif dimension drawing (DXF, v1.5.2). v1.6 is assumed to use the same holes.

![Turntable render](<ESP32-P4 Function EV Board SKADIS Mount.gif>)

Mounted edge: The 74 mm MIPI camera and display edge, with the USB-C ports facing up. The MIPI connectors sit against the spine, so they can't take cables while the board is mounted.

Espressif does not publish a 3D model of this board, so the clash check covers a blank PCB only. The connectors in the render are stand-ins placed from the dimension drawing. The STEP and 3MF are mirrored so the arms rest on the back of the board. The FCStd is not mirrored: mirror any STEP you export from it across the XY plane.

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
