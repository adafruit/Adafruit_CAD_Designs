# WCH-LinkE JDEBUG Adapter

Plugs a WCH-LinkE debug probe straight into a 2x5 1.27 mm JDEBUG ribbon cable, so it can flash the Metro CH32V407 and CH32V467 over SWD. It carries three signals (SWDIO, GND and RST) on a 40 x 30 mm single-sided board, designed to be milled at home: no vias, no pour, 45 degree bends only.

![Turntable render](<WCH-LinkE JDEBUG Adapter.gif>)

![Adapter with the probe and a Metro CH32V407](<WCH-LinkE JDEBUG Adapter with Metro.jpg>)

![Adapter on its own](<WCH-LinkE JDEBUG Adapter.jpg>)

## Files

| File | What |
|---|---|
| `.step` | Board with connectors, for any CAD tool |
| `kicad/` | KiCad 10 project. `build_pcb.py` regenerates the board from scratch |
| `milling/` | F.Cu and Edge.Cuts Gerbers, drill file, and 1:1 etch PDFs (normal and mirrored) |

## Parts

| Ref | Part | Qty |
|---|---|---|
| J1 | 2x5 2.54 mm female SMD socket, 3.5 mm low profile (cut from a PH3.5 2x12 SMD strip) | 1 |
| J2 | 2x5 1.27 mm SMD pin header, plain or shrouded | 1 |
| | 2x5 1.27 mm IDC ribbon cable | 1 |
| | M2 x 4 screw, for the SKADIS mount | 2 |

## Pinout

| WCH-LinkE (J1) | JDEBUG (J2) |
|---|---|
| SWDIO | 2 |
| GND | 3, 5 and 9 |
| RST | 10 |

The probe's 3V3 and 5V are not connected, so the probe does not power the target. The WCH-LinkE pinout comes from the WCH-Link user manual (R0-1v3). Plug the probe in with its parts side toward the `PARTS` label.

## Milling

The tightest gap is 0.53 mm, between the J2 pads, so it needs a 0.4 mm end mill or a fine V-bit. Every other gap is at least 0.4 mm.

The probe and Metro in the renders are approximate models made for this render, not official CAD.

A SKADIS mount for this board is in [JDEBUG Adapter SKADIS Mount](<../JDEBUG Adapter SKADIS Mount>).
