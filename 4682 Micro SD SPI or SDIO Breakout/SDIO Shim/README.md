# Micro SD SPI or SDIO Breakout SDIO Shim

A passive shim that plugs an [Adafruit Micro SD SPI or SDIO Card Breakout](https://www.adafruit.com/product/4682) straight onto a Feather, no breadboard needed. It routes 4-bit SDIO to A0 to A3 (DAT0 to DAT3), D24 (CLK) and D25 (CMD), so the SPI, UART and I2C buses stay free. The breakout already has the pull-ups and caps SDIO needs, so the shim has no parts besides its two connectors.

![Turntable render](<4682 Micro SD SPI or SDIO Breakout SDIO Shim.gif>)

## Files

| File | What |
|---|---|
| `.step` | Board with connectors, for any CAD tool |
| `.3mf` | Board mesh, for test fits |
| `sdio-shim.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | KiCad source |

## Parts

| Part | Qty |
|---|---|
| 1x08 right-angle SMD header, Feather side (H1) | 1 |
| 1x09 SMD socket, breakout side (H2) | 1 |

## CircuitPython

```python
import board, sdioio, storage
sd = sdioio.SDCard(
    clock=board.D24,
    command=board.D25,
    data=(board.A0, board.A1, board.A2, board.A3),
    frequency=37_500_000,
)
storage.mount(storage.VfsFat(sd), "/sd")
```

Card detect is not connected.

Source: [mikeysklar/sdio-shim](https://github.com/mikeysklar/sdio-shim)
