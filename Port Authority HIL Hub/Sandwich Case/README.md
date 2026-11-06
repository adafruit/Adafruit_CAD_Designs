# Port Authority HIL Hub Sandwich Case

Two printed plates that sandwich the [Port Authority HIL hub](https://github.com/mikeysklar/hil-hub-port-authority) (Rev C). Each plate has its own bosses at the four mount holes, so M2.5 screws go straight through plate, boss, PCB, boss and plate with no spacers. The top plate rests on both STEMMA QT ports, and everything taller pokes through cutouts. PORT AUTHORITY is engraved on the outer face of both plates.

![Turntable render](<Port Authority HIL Hub Sandwich Case.gif>)

## Files

| File | What |
|---|---|
| `Top Plate.3mf`, `Bottom Plate.3mf` | Ready to slice, outer face down |
| `Top Plate.step`, `Bottom Plate.step` | For any CAD tool |
| `.FCStd` | FreeCAD model, every setting in the `Params` sheet. Includes a stand-in of the hub |
| `build_case.py` | Rebuilds the model headless with `freecadcmd build_case.py`. The engraving uses the Data70 font from `~/Library/Fonts` |

## Hardware

| Part | Qty |
|---|---|
| M2.5 screw, long enough for the 11.5 mm plate, boss, PCB, boss, plate stack plus a nut | 4 |
| M2.5 nut | 4 |
