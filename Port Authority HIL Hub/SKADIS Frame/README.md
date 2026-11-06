# Port Authority HIL Hub SKADIS Frame

A skeleton frame that hangs the [Port Authority HIL hub](https://github.com/mikeysklar/hil-hub-port-authority) (Rev C) on an IKEA SKADIS pegboard. Two rails run through the mount hole rows, with a boss and heat set insert at each hole that holds the board 4 mm off the rails, clear of the through-hole leads. The top rail rests on two stock SKADIS hooks 120 mm apart, in notches on its underside. USB-C, the DC jack and the terminal block are on top, and the USB-A ports point down.

![Swing render](<Port Authority HIL Hub SKADIS Frame.gif>)

## Files

| File | What |
|---|---|
| `.3mf` | Ready to slice, back face down |
| `.step` | For any CAD tool |
| `.FCStd` | FreeCAD model, every dimension in the `Params` sheet. Includes a stand-in of the hub |
| `build_case.py` | Rebuilds the model headless with `freecadcmd build_case.py` |

## Hardware

| Part | Qty |
|---|---|
| M2.5 heat set insert, for a 3.3 mm pocket 3.3 mm deep | 4 |
| M2.5 screw | 4 |
| Stock IKEA SKADIS hook | 2 |
