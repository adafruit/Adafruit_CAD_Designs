# Port Authority HIL Hub Display Case

Shows live voltage and current per port on the [Port Authority HIL hub](https://github.com/mikeysklar/hil-hub-port-authority) (Rev C). A top plate carries a [QT Py ESP32-S3](https://www.adafruit.com/product/5426) and a [0.96" 128x64 STEMMA QT OLED](https://www.adafruit.com/product/326) over the hub, and a rail frame behind the board hangs on an IKEA SKADIS pegboard.

![Swing render](<Port Authority HIL Hub Display Case.gif>)

- The top plate sits on M2.5 x 5 standoffs at the four mount holes. Their male ends go through the PCB into heat set inserts in the frame bosses.
- The QT Py has no mount holes. It slides into a cradle printed into the top plate, USB-C out the left edge, with no screws.
- The OLED sits on printed spacers with a heat set insert in each. Its STEMMA QT cable goes in its left port. The right port is blocked by the DC jack plug.
- The left edge of the plate stays open so both of the hub's STEMMA QT ports can be plugged in.
- The bottom rail has two nicks 120 mm apart that seat on stock SKADIS hooks.

## Files

| File | What |
|---|---|
| `Top Plate.3mf`, `Frame.3mf` | Ready to slice, as oriented |
| `Top Plate.step`, `Frame.step` | For any CAD tool |
| `.FCStd` | FreeCAD model, every setting in the `Params` sheet. Includes stand-ins of the hub, QT Py and OLED |
| `build_case.py` | Rebuilds the model headless with `freecadcmd build_case.py` |

## Hardware

| Part | Qty |
|---|---|
| M2.5 heat set insert, for a 3.3 mm pocket 3.3 mm deep (frame bosses and OLED spacers) | 8 |
| M2.5 x 5 male-female hex standoff | 4 |
| Short M2.5 screw, top plate onto the standoffs | 4 |
| Short M2.5 screw, OLED onto its spacers | 4 |
| Stock IKEA SKADIS hook | 2 |
| QT Py ESP32-S3, 0.96" STEMMA QT OLED and a STEMMA QT cable | 1 each |
