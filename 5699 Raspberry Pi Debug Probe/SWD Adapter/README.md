# Raspberry Pi Debug Probe SWD Adapter

Connects the 3-pin JST-SH "D" port of the [Raspberry Pi Debug Probe](https://www.adafruit.com/product/5699) to a standard 2x5 1.27 mm SWD header, like the one on many Metro and Feather boards. No active parts, just three signals and a ground pour on a 26.6 x 11 mm single-sided board. Tested with a Metro M0 Express over OpenOCD.

![Turntable render](<5699 Raspberry Pi Debug Probe SWD Adapter.gif>)

## Files

| File | What |
|---|---|
| `.step` | Board with connectors, for any CAD tool |
| `.3mf` | Board mesh, for test fits |
| `pico-debug-swd-adapter.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | KiCad source |

## Parts

| Ref | Part | Qty |
|---|---|---|
| J1 | JST `BM03B-SRSS-TB`, 3-pin 1.00 mm vertical SMT | 1 |
| J2 | CNC Tech `3220-10-0300-00`, 2x5 1.27 mm shrouded SWD header, SMT | 1 |
| | M2.5 screw | 2 |
| | 2x5 1.27 mm ribbon cable | 1 |

The STEP and renders show J2 as a plain 2x5 1.27 mm pin header, since KiCad has no model of the shrouded part.

## Pinout

| Debug Probe "D" (J1) | SWD 2x5 (J2) |
|---|---|
| 1, SC | 4, SWCLK |
| 2, GND | 3 and 5, GND |
| 3, SD | 2, SWDIO |

Use the "D" port on the probe, not "U". The probe does not power the target.

Source: [mikeysklar/pi-debug-swd-adapter](https://github.com/mikeysklar/pi-debug-swd-adapter)
