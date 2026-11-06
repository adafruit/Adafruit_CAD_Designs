# Raspberry Pi Touch Display 2 (5") Legs

Designed by [FoamyGuy](https://github.com/FoamyGuy) (Tim Cocks). Two printed L-shaped legs that stand the [Raspberry Pi Touch Display 2, 5"](https://www.adafruit.com/product/6408) up in landscape on a desk. Each leg screws into one of the two bottom corner bosses on the back of the display, and its foot runs back along the desk.

![Turntable render](<6408 Raspberry Pi Touch Display 2 - 5in.gif>)

The two legs are different. On the 5" display the bottom corner bosses are turned 90 degrees from each other, so one leg has a pocket for the tall boss (nearest the DSI ribbon connector) and the other for the wide boss.

## Files

| File | What |
|---|---|
| `pi_touch_display_leg.scad` | OpenSCAD source. Set `part` to `print_pair`, `tall_leg`, `wide_leg`, `fit_test` or `assembly`, and `tilt` for the lean-back angle |
| `display_leg_1_27deg.stl` | Wide-boss leg, display leans back 27 degrees |
| `display_leg_2_27deg.stl` | Tall-boss leg (DSI connector end), 27 degrees |
| `display_leg_1_10deg.stl` | Leg 1, display leans back 10 degrees |
| `display_leg_2_10deg.stl` | Leg 2, 10 degrees |
| `.gif`, `.jpg` | Renders of the 27 degree legs on the display stand-in from the `.scad` |

Print one leg 1 and one leg 2 at the same angle. Some pocket sizes are estimated from the product brief drawing, so print `part = "fit_test"` first to check the fit over a boss.

## Hardware

| Part | Qty |
|---|---|
| M2.5 screw, into the corner boss | 2 |
