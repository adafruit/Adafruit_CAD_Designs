# QT Py CH32V203 SWD DAP Breakout

![QT Py CH32V203 on the breakout, ribbon to a Metro CH32V407](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout%20programming%20a%20Metro%20CH32V407.jpg)

A 40 x 42 mm carrier that turns an Adafruit QT Py CH32V203 into a debug probe. The silk title is "WCH + ARM Programmer". It works two ways:

| Mode | Targets |
|---|---|
| WCH SWIO programmer | Metro CH32V407 and CH32V467 |
| ARM SWD CMSIS-DAP probe | ARM Cortex targets on the 10-pin header |

No pull-up resistor is needed on SWIO. The SWIO firmware is in [Adafruit_DAP PR #60](https://github.com/adafruit/Adafruit_DAP/pull/60).

The QT Py plugs into the inner rows of two 2x7 SMD sockets. The outer rows repeat every QT Py pin, so you can plug jumper wires in for the spare IO, like the Proto Doubler PiCowbell. A 2x5 1.27 mm box header takes a 1675 cable to the target. It is a single-sided board made to be cut at home on a laser or a mill: no vias, a GND pour, 45 degree bends only.

![Turntable render](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout.gif)

![Breakout cabled to a Metro CH32V407 with a 1675 cable](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout%20with%20Metro.jpg)

![Breakout on its own](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout.jpg)

![Top view](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout%20top.jpg)

![Anatomy](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout%20anatomy.gif)

![Test rig with a logic analyzer on SWIO, Metro CH32V407](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout%20test%20rig%20with%20logic%20analyzer.jpg)

![Laser-cut stencil next to a milled breakout v2](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout%20stencil%20and%20milled%20board.jpg)

## Files

| File | What |
|---|---|
| [5996 QT Py CH32V203 SWD DAP Breakout.stpZ](5996%20QT%20Py%20CH32V203%20SWD%20DAP%20Breakout.stpZ) | Board with QT Py, sockets and box header, gzipped STEP |
| [kicad/qtpy-dap-breakout.kicad_pcb](kicad/qtpy-dap-breakout.kicad_pcb) | KiCad 10 board |
| [kicad/qtpy-dap-breakout.kicad_pro](kicad/qtpy-dap-breakout.kicad_pro) | KiCad 10 project |
| [kicad/build_pcb.py](kicad/build_pcb.py) | Regenerates the board from scratch |
| [kicad/fp-lib-table](kicad/fp-lib-table) | Points KiCad at `models/QTPyDAP.pretty` |
| [models/QTPyDAP.pretty](models/QTPyDAP.pretty) | 752 box header footprint |
| [models/BoxHeader_2x05_P1.27mm_SMD_752.step](models/BoxHeader_2x05_P1.27mm_SMD_752.step) | 752 box header STEP |
| [models/QTPy_CH32V203_5996.stpZ](models/QTPy_CH32V203_5996.stpZ) | QT Py CH32V203 model, gzipped STEP |
| [models/gen_box_header_752.py](models/gen_box_header_752.py) | Generates the box header model |
| [milling/qtpy-dap-breakout-F_Cu.gbr](milling/qtpy-dap-breakout-F_Cu.gbr) | F.Cu Gerber |
| [milling/qtpy-dap-breakout-Edge_Cuts.gbr](milling/qtpy-dap-breakout-Edge_Cuts.gbr) | Edge.Cuts Gerber |
| [milling/qtpy-dap-breakout.drl](milling/qtpy-dap-breakout.drl) | Drill file |
| [milling/qtpy-dap-breakout-job.gbrjob](milling/qtpy-dap-breakout-job.gbrjob) | Gerber job file |
| [milling/F_Cu-reference.pdf](milling/F_Cu-reference.pdf) | 1:1 etch PDF |
| [milling/F_Cu-mirrored-1to1.pdf](milling/F_Cu-mirrored-1to1.pdf) | 1:1 etch PDF, mirrored |

A SKADIS mount for this board, with its STEP, 3MF and FreeCAD files, is in [SKADIS Mount](../SWD%20DAP%20Breakout%20SKADIS%20Mount).

## Parts

| Ref | Part | Qty |
|---|---|---|
| U1 | Adafruit QT Py CH32V203 (PID 5996) | 1 |
| J1, J2 | 2x7 2.54 mm SMD female socket, cut from an Adafruit 2187 2x20 short SMT socket, one per QT Py side | 2 |
| J3 | Adafruit 752 2x5 1.27 mm SMT box header, 10-pin ARM Cortex | 1 |
| J4, J5 | 1x7 2.54 mm male header strip, solders to the QT Py | 2 |
| | Adafruit 1675 SWD cable, 2x5 1.27 mm, 150 mm | 1 |
| | M2 x 4 screw, into the SKADIS mount's heat set inserts | 4 |
| | Single-sided copper-clad blank, 40 x 42 mm | 1 |

## Pinout

| Header J3 | Signal | QT Py | Metro CH32V407/467 (JDEBUG) |
|---|---|---|---|
| 1 | VTref | not connected | 1, the Metro's own 3.3 V |
| 2 | SWDIO / SWIO | A3 | 2 (PA13) |
| 3, 5, 9 | GND | GND | 3, 5, 9 |
| 4 | SWCLK | A2 | 4 (PA14, unused in SWIO mode) |
| 6, 7, 8 | not connected | | |
| 10 | nRESET | A0 | 10 |

- Only 3.3 V targets. There is no level shifting.
- The breakout does not power the target, like the Raspberry Pi Debug Probe. The target needs its own supply. Pin 1 is left open so the Metro's 3.3 V never meets the QT Py's.
- The UART is not wired to the box header. TX and RX, like every other QT Py pin, are on the outer socket rows.
- Each QT Py pin has a second socket on the outer row, labeled on the silk. The two contacts of each pin are tied by a trace under the socket.

## Firmware

Liz Clark's Adafruit_DAP examples run as-is with this wiring.

| Example | Result |
|---|---|
| `ch32_host/cmsis_dap_probe` | Runs as-is. Its UART bridge is on the QT Py TX and RX pins, reachable on the outer socket rows |
| `ch32_host/dragdrop_programmer` | Runs as-is |
| `stm32/stm32f4_test` | Runs as-is |

Most other examples do not fit this board:

| Group | Examples | Why |
|---|---|---|
| Needs pin changes | `samd21/flash_MKR_bootloaders`, `samd51/samx5_flash_from_header`, `nrf/nrf52_test` | Pins are hardcoded. The samx5 image may not fit in flash |
| Needs SD card, SPI flash or WiFi | `samd21/flash_from_SD`, `samd21/flash_from_SPI_flash`, `samd21/SWD_standalone_core`, `stm32/stm32_flash_from_SD`, `nrf/flash_feather52`, `nrf/flash_feather52840`, `nrf/flash_nrf51_from_SPI_flash`, `ESPHost/*` | The breakout has none of these |
| Image too large | `samd21/flash_from_header` | 239 KB image, more than 7 times the 32 KB flash |

Tested through the breakout:

| Target | Firmware | Result |
|---|---|---|
| Metro CH32V407 | [Adafruit_DAP PR #60](https://github.com/adafruit/Adafruit_DAP/pull/60) | Programmed and verified in 66.5 s |
| Metro CH32V467 | [Adafruit_DAP PR #60](https://github.com/adafruit/Adafruit_DAP/pull/60) | Programmed and verified TinyUF2 in 67.0 s, chip ID 10/10 |
| Metro M0 Express (SAMD21G18A) | `ch32_host/cmsis_dap_probe` | Read over SWD with OpenOCD at 400 kHz |

## Milling

Cut on F.Cu only. Signal traces are 0.76 mm with 45 degree miters. GND is a pour with 0.5 mm clearance and solid pad connections, with no GND traces. The tightest gap is 0.51 mm between the box header pads. A fiber laser such as the xTool F1 Ultra handles it; a mill needs a 0.4 mm end mill or a fine V-bit.

The Metro and QT Py in the renders are approximate models, not official CAD.

In the Data 70 font, D reads like O ("SWD", "GND") and 1 reads like I in the date.

## Credits

Probe firmware by Liz Clark (Adafruit_DAP, ch32_host examples). The QT Py model is built from Liz's [QT Py CH32V203 Eagle board](https://github.com/adafruit/Adafruit-QT-Py-CH32V203-PCB).
