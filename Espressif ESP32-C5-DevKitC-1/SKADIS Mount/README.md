# ESP32-C5-DevKitC-1 SKADIS Mount

Hangs the Espressif ESP32-C5-DevKitC-1 edge-on from an IKEA SKADIS pegboard. The board's own header pins press into holes in the arms, like a breadboard, with no screws. Pin positions are checked against the Espressif dimension drawing.

![Turntable render](<ESP32-C5-DevKitC-1 SKADIS Mount.gif>)

Mounted edge: The antenna end, so both USB-C ports point away from the panel. The first four pins of each header row go into the arms.

Needs the male pin headers soldered on, pointing down. The holes are 1.0 mm for a press fit on 0.64 mm square pins; if the fit is too tight or loose, change Up_Clear_D in the FCStd spreadsheet (try 0.95 to 1.1). Espressif does not publish a 3D model of this board, so the clash check used a stand-in built from the dimension drawing. The arms sit under the module's antenna end, which may detune it slightly.

## Files

| File | What |
|---|---|
| `.3mf` | Ready to slice, print flat as oriented |
| `.step` | For any CAD tool |
| `.FCStd` | FreeCAD source, dimensions in the `Spreadsheet` |
