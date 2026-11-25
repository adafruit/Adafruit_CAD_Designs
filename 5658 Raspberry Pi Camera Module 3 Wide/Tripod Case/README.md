# Raspberry Pi Camera Module 3 Wide Tripod Case

A two part snap-together case for the [Raspberry Pi Camera Module 3 Wide](https://www.adafruit.com/product/5658) with a printed 1/4"-20 tripod socket. Remixed from the Ruiz Brothers' [3D Printed Pi Camera Case and Tripod](https://learn.adafruit.com/3d-printed-pi-camera-case-and-tripod) (CC BY). Also fits the [Wide NoIR](https://www.adafruit.com/product/5660).

![Turntable render](<5658 Raspberry Pi Camera Module 3 Wide Tripod Case.gif>)

![Exploded line drawing: lens opening, pins, snap, ribbon path and tripod thread](<5658 Raspberry Pi Camera Module 3 Wide Tripod Case Anatomy.gif>)

- The case can't block the 120 degree view. The front face sits 0.6 mm behind the lens glass, and a 125 degree cone from the glass rim is cut from the front anyway, so moving the face forward chamfers the opening instead of darkening the corners.
- No screws. Pins on the front posts go through the board's mount holes into the back, and a lip on the back snaps inside the front walls. The ribbon runs down a 20.5 mm channel in the foot and out its front face, so the tripod plate never presses on it. A curve where the channel turns guides the ribbon round, so it pushes through from either end.
- The tripod thread is printed in the foot, so no nut or adapter is needed. Set `thread_d` 9.525 and `thread_tpi` 16 for a 3/8"-16 socket.
- Fit is checked against the official Raspberry Pi Camera Module 3 Wide STEP model. `build_case.py` runs that check when the STEP is in `ref/rpi-cm3-step/`.

## Files

| File | What |
|---|---|
| `Front.3mf`, `Back.3mf` | Ready to slice, as oriented. Front prints face down, back prints on the foot so the thread is vertical. No supports |
| `Front.step`, `Back.step` | For any CAD tool |
| `.FCStd` | FreeCAD model, every setting in the `Params` sheet. Includes a stand-in of the camera |
| `build_case.py` | Rebuilds the model headless with `freecadcmd build_case.py` and runs the fit and field of view checks |

## Hardware

None. Just the camera and its ribbon cable. (The board's mount holes are 2.2 mm, too small for M2.5.)
