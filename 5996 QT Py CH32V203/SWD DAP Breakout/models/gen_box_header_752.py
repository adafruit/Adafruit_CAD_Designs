# SPDX-FileCopyrightText: 2026 (generated)
# SPDX-License-Identifier: MIT
#
# Generates BoxHeader_2x05_P1.27mm_SMD_752.step for Adafruit product 752
# (2x5 1.27 mm SMT box header, shrouded), using CnC Tech 3220-XX-0300-00 dims.
#
# Run with FreeCAD's command-line tool (Part module, no GUI needed):
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c \
#     "exec(open('<this file>').read())"
#
# Coordinates (KiCad-style footprint frame, Z up):
#   origin = body centre in XY, Z = 0 at PCB top surface
#   pin 1 at (-0.635, -2.54); odd pins at x<0, even pins at x>0
#   pin rows at y = -2.54, -1.27, 0, 1.27, 2.54
#   body long axis = Y (12.7), width = X (5.0)
#   key slot in the long wall on the x<0 side, centred on Y
#
# Dimension sources (CnC Tech drawing 3220-XX-0300-00, rev D, 2023-04-10):
#   Dim.C 12.70 (+-0.50) outer length     Dim.B 11.10 cavity length (10-pin row)
#   Dim.A  5.08 pin span along length     top view 3.4 cavity width, 5.0 outer width
#   height 4.90 body height, side view 5.30 total from PCB to top
#   standoff 0.40 (5.30 - 4.90)           pin square SQ0.40
#   pitch 1.27 along length and across    feet: side view 5.50 foot-to-foot
#   key slot ~2.5 wide, ~3.1 deep from top (front view, measured from drawing)
# Assumed, not on the drawing: cavity floor (Z=1.3), pin top (Z=4.0), wall/cavity
# depth, foot inner edge (0.42). Those are marked ASSUMED below.

import os
import Part
from FreeCAD import Vector

OUT_DIR = "/Volumes/clear/Downloads/ada/ch32v4/qtpy-dap-breakout/models"
STEP_PATH = os.path.join(OUT_DIR, "BoxHeader_2x05_P1.27mm_SMD_752.step")

# --- body (datasheet) ---
BODY_L = 12.70   # Y, Dim.C
BODY_W = 5.00    # X, top view
BODY_H = 4.90    # side view
Z_STANDOFF = 0.40          # 5.30 - 4.90
Z_BODY_BOT = Z_STANDOFF
Z_BODY_TOP = Z_BODY_BOT + BODY_H   # 5.30

WALL = 0.80      # (5.0 - 3.4) / 2, top view cavity 3.4 wide
CAV_W = 3.40     # top view
CAV_L = 11.10    # Dim.B (10-pin row)

# --- ASSUMED ---
Z_CAV_FLOOR = 1.30   # ASSUMED
Z_PIN_TOP = 4.00     # ASSUMED, pin tip inside cavity

# --- key slot (front view, measured) ---
KEY_W = 2.50         # across Y
KEY_DEPTH = 3.10     # from top face down

# --- pins (datasheet) ---
PIN_SQ = 0.40
PITCH = 1.27
PIN_X = PITCH / 2.0  # 0.635, pin rows across the body
ROW_Y = [-2.0 * PITCH, -PITCH, 0.0, PITCH, 2.0 * PITCH]

# --- SMT feet (datasheet side view: 5.50 foot-to-foot) ---
FOOT_OUT = 2.75      # 5.50 / 2
FOOT_IN = 0.42       # ASSUMED inner edge of foot tab, from side view
FOOT_W = 0.65        # pad width along Y, layout 0.65 +-0.05
FOOT_T = Z_STANDOFF  # foot thickness 0.40, lies on PCB


def box(x0, y0, z0, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, Vector(x0, y0, z0))


def build():
    # body: outer block, minus cavity, minus key slot in the x<0 wall
    body = box(-BODY_W / 2, -BODY_L / 2, Z_BODY_BOT, BODY_W, BODY_L, BODY_H)
    cavity = box(-CAV_W / 2, -CAV_L / 2, Z_CAV_FLOOR, CAV_W, CAV_L, Z_BODY_TOP + 1.0 - Z_CAV_FLOOR)
    body = body.cut(cavity)
    key = box(-BODY_W / 2 - 0.1, -KEY_W / 2, Z_BODY_TOP - KEY_DEPTH,
              WALL + 0.2 + 0.0, KEY_W, KEY_DEPTH + 0.5)
    body = body.cut(key)

    parts = [body]

    for n in range(1, 11):
        row = (n - 1) // 2
        y = ROW_Y[row]
        odd = (n % 2 == 1)
        x = -PIN_X if odd else PIN_X
        # contact pin, from PCB level up into the cavity
        parts.append(box(x - PIN_SQ / 2, y - PIN_SQ / 2, 0.0,
                         PIN_SQ, PIN_SQ, Z_PIN_TOP))
        # SMT foot on the PCB, same side as the contact
        if odd:
            x0, x1 = -FOOT_OUT, -FOOT_IN
        else:
            x0, x1 = FOOT_IN, FOOT_OUT
        parts.append(box(min(x0, x1), y - FOOT_W / 2, 0.0,
                         abs(x1 - x0), FOOT_W, FOOT_T))

    return parts


def main():
    parts = build()
    shape = Part.makeCompound(parts)
    bb = shape.BoundBox
    print("bbox X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" %
          (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
    print("volume %.3f mm3, solids %d" % (shape.Volume, len(parts)))
    shape.exportStep(STEP_PATH)
    print("wrote", STEP_PATH)
    stl = "/private/tmp/claude-501/-Volumes-clear-Downloads-ada-ch32v4/67dbead9-cbdf-4225-ad37-ec16eec00eb9/scratchpad/box752.stl"
    shape.exportStl(stl)
    print("stl", stl)


main()
