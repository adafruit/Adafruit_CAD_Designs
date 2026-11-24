# SPDX-FileCopyrightText: 2026 Mikey Sklar for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
Tripod case for the Raspberry Pi Camera Module 3 Wide, remixed from the Ruiz Brothers'
3D Printed Pi Camera Case and Tripod (learn.adafruit.com/3d-printed-pi-camera-case-and-tripod).

Run headless:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd build_case.py

Writes into build/ next to this file:
    cm3_case.FCStd     parametric model, every dimension in the Params sheet
    front.step         front shell, world frame
    back.step          back shell with the tripod foot, world frame
    front.3mf          front shell, print orientation (front face on the bed)
    back.3mf           back shell, print orientation (foot on the bed, thread vertical)
    camera.step        hand-built stand-in of the camera, world frame (for renders)

World frame, as used on a tripod:
    X  across the board, 0..pcb_w from the left edge seen from the front
    Y  up. The ribbon connector edge is at the bottom (Y = 0), image upright
    Z  out of the lens. The PCB back face is Z = 0

Board facts come from the Camera Module 3 Wide mechanical drawing RP-008155-DS-1. The
drawing shows the board with the connector edge at the top; this frame turns it 180 degrees
so the image is upright, and the "from the top" values below are measured from the edge
opposite the connector, as the drawing gives them.

The 120 degree field of view can't touch the case: the front face sits lens_proud behind
the front glass, and a cone of fov_diag + fov_margin from the glass rim is cut from the front
shell anyway, so a negative lens_proud chamfers the opening instead of vignetting. check()
fails if any case material is inside that cone.

The tripod socket is a printed female thread (1/4"-20 by default, 3/8"-16 is
thread_d = 9.525 and thread_tpi = 16). No nut or adapter screw. No screws at all: pins on the
front posts go through the board's 2.2 mm holes into sockets in the back bosses, and a lip on
the back plate snaps inside the front walls (a bead on each side into a groove).
"""

import os
import struct
import zipfile

import FreeCAD as App
import MeshPart
import Part
import Sketcher

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    HERE = os.getcwd()
OUT = os.path.join(HERE, "build")
os.makedirs(OUT, exist_ok=True)

# name, value or formula, note. Formulas start with "=".
PARAMS = [
    ("# camera: official STEP (RP-008154) where it differs from drawing RP-008155-DS-1", None, ""),
    ("pcb_w", 25.0, "board width (X)"),
    ("pcb_h", 23.862, "board height (Y)"),
    ("pcb_t", 0.757, "board thickness, from the STEP (the drawing's 1.12 is not the board)"),
    ("pcb_r", 2.0, "board corner radius, from the STEP"),
    ("hole_d", 2.2, "mount hole diameter"),
    ("hole_x0", 2.0, "hole centre from the left and right edges"),
    ("hole_top", 2.0, "upper hole row, from the edge opposite the connector"),
    ("hole_dy", 12.5, "hole row pitch"),
    ("lens_x", 12.5, "lens axis from the left edge"),
    ("lens_top", 14.4, "lens axis from the edge opposite the connector"),
    ("holder_w", 8.5, "lens module square block, from the STEP"),
    ("holder_h", 4.511, "top of the square block above the PCB front face, from the STEP"),
    ("barrel_d", 7.2, "lens barrel, largest round diameter in the STEP"),
    ("glass_d", 6.8, "barrel front rim, where the field of view cone starts (conservative)"),
    ("lens_z", 8.818, "lens front from the PCB back face, from the STEP"),
    ("conn_w", 22.92, "ribbon connector width, on the back, at the bottom edge, from the STEP"),
    ("conn_h", 6.91, "ribbon connector height (Y), from the STEP"),
    ("conn_t", 2.59, "ribbon connector depth behind the PCB, from the STEP"),
    ("flex_w", 8.9, "sensor flex on the front, above the lens holder"),
    ("flex_h", 7.3, "sensor flex height from the top edge"),
    ("flex_t", 0.8, "sensor flex thickness (not dimensioned)"),
    ("fov_diag", 120.0, "diagonal field of view, degrees"),
    ("# case", None, ""),
    ("gap", 0.3, "board edge to inner wall"),
    ("wall", 1.6, "side wall thickness"),
    ("corner_r", "=pcb_r + gap + wall", "outer corner radius, concentric with the board corners so the wall stays even"),
    ("edge_r", 1.5, "round on the front and back face edges, like the Ruiz case. Keep it under corner_r - 0.3 and out of 0.5..1.4 with 1.6 mm walls (the check reports the wall left)"),
    ("front_t", 1.6, "front plate thickness"),
    ("lens_proud", 0.6, "front glass ahead of the front face. Negative puts the case in front"),
    ("barrel_clear", 0.4, "radial clearance around the barrel"),
    ("lens_chamfer", 1.0, "45 degree chamfer around the lens opening, at the front face"),
    ("fov_margin", 5.0, "degrees added to each side of the FOV cone"),
    ("fov_len", 40.0, "length of the FOV cone used to cut and check"),
    ("back_gap", 3.2, "space behind the PCB, clears the connector"),
    ("back_t", 1.6, "back plate thickness"),
    ("post_d", 4.0, "front post and back boss diameter"),
    ("pin_d", 1.9, "pin on each front post, through the 2.2 mm board hole"),
    ("socket_d", 2.3, "socket in each back boss for the pin"),
    ("socket_depth", 2.0, "socket depth below the PCB back face"),
    ("pin_tip_gap", 0.3, "pin tip short of the socket floor"),
    ("back_edge_r", 1.2, "round on the back plate's back edge, under back_t"),
    ("lip_t", 1.0, "snap lip thickness, on the back plate inside the front walls"),
    ("lip_gap", 0.15, "lip outer face to the front wall's inner face"),
    ("lip_clear", 0.2, "lip top below the PCB back face"),
    ("bead_r", 0.35, "snap bead radius on the lip's left and right outer faces"),
    ("bead_int", 0.2, "snap interference: how far the bead reaches past the wall's inner face"),
    ("bead_z", 2.0, "snap bead height above the back plate"),
    ("bead_len", 10.0, "bead and groove length, centred on the side, where the walls flex most"),
    ("groove_clear", 0.05, "groove radius over the bead"),
    ("cable_w", 20.5, "ribbon slot width, bottom wall of the front shell and the foot (16 mm ribbon + 2.25 mm each side)"),
    ("# tripod foot, on the back shell", None, ""),
    ("foot_h", 10.0, "foot height below the case (Y). The foot is the case width, the ribbon runs down a channel in its front"),
    ("foot_rise", 6.0, "foot runs up the back face this far, for strength"),
    ("foot_ext", 9.0, "foot depth behind the back plate (Z)"),
    ("thread_d", 6.35, "major diameter. 1/4-20: 6.35, 3/8-16: 9.525"),
    ("thread_tpi", 20.0, "threads per inch. 1/4-20: 20, 3/8-16: 16"),
    ("thread_len", 7.0, "thread depth from the foot's bottom face"),
    ("thread_clear", 0.2, "radial clearance for a printed thread"),
    ("# derived, do not edit", None, ""),
    ("in_x0", "=-gap", ""),
    ("in_x1", "=pcb_w + gap", ""),
    ("in_y0", "=-gap", ""),
    ("in_y1", "=pcb_h + gap", ""),
    ("out_x0", "=in_x0 - wall", ""),
    ("out_x1", "=in_x1 + wall", ""),
    ("out_y0", "=in_y0 - wall", ""),
    ("out_y1", "=in_y1 + wall", ""),
    ("lens_y", "=pcb_h - lens_top", "lens axis Y"),
    ("hole_x1", "=pcb_w - hole_x0", "right hole column X"),
    ("hole_y1", "=pcb_h - hole_top", "upper hole row Y"),
    ("hole_y0", "=hole_y1 - hole_dy", "lower hole row Y"),
    ("z_front", "=lens_z - lens_proud", "front face Z"),
    ("z_plate", "=z_front - front_t", "front plate inside face Z"),
    ("z_floor", "=-back_gap", "back plate inside face Z, and the parting line"),
    ("lip_x0", "=in_x0 + lip_gap", "lip outer face, left"),
    ("lip_x1", "=in_x1 - lip_gap", "lip outer face, right"),
    ("lip_y1", "=in_y1 - lip_gap", "lip outer face, top"),
    ("bead_x0", "=in_x0 - bead_int + bead_r", "left bead and groove axis X"),
    ("bead_x1", "=in_x1 + bead_int - bead_r", "right bead and groove axis X"),
    ("bead_y0", "=pcb_h / 2 - bead_len / 2", "bead start Y"),
    ("z_back", "=-(back_gap + back_t)", "back face Z"),
    ("fov_half", "=fov_diag / 2 + fov_margin", "half angle of the cut and checked cone"),
    ("pitch", "=25.4 / thread_tpi", "thread pitch"),
    ("thread_r_min", "=(thread_d - 1.0825 * pitch) / 2 + thread_clear", "bore radius"),
    ("thread_r_max", "=thread_d / 2 + thread_clear", "groove root radius"),
    ("foot_y0", "=out_y0 - foot_h", "foot bottom face Y"),
    ("foot_z0", "=z_back - foot_ext", "foot back face Z"),
    ("thread_z", "=(foot_z0 + z_floor) / 2", "thread axis Z, centred in the foot"),
]

EPS = 0.05
P = "Params."
# Print orientation: front face down for the front, foot down for the back.
PRINT_ROT = {"front": (App.Vector(0, 1, 0), 180), "back": (App.Vector(1, 0, 0), 90)}


def build_sheet(doc):
    sheet = doc.addObject("Spreadsheet::Sheet", "Params")
    sheet.set("A1", "parameter")
    sheet.set("B1", "value")
    sheet.set("C1", "note")
    row = 2
    for name, value, note in PARAMS:
        sheet.set("A%d" % row, name)
        if value is not None:
            sheet.set("B%d" % row, str(value))
            sheet.setAlias("B%d" % row, name)
            sheet.set("C%d" % row, note)
        row += 1
    sheet.setColumnWidth("A", 130)
    sheet.setColumnWidth("C", 420)
    doc.recompute()
    return sheet


def e(expr):
    """Prefix bare parameter names in a formula with the sheet name."""
    out, word = [], ""
    for ch in expr + " ":
        if ch.isalnum() or ch == "_":
            word += ch
            continue
        if word:
            names = {n for n, v, _ in PARAMS if v is not None}
            out.append(P + word if word in names else word)
            word = ""
        out.append(ch)
    return "".join(out).strip()


def bind(o, prop, expr):
    o.setExpression(prop, e(expr))


def box(doc, name, x0, x1, y0, y1, z0, z1):
    o = doc.addObject("Part::Box", name)
    bind(o, "Length", "(%s) - (%s)" % (x1, x0))
    bind(o, "Width", "(%s) - (%s)" % (y1, y0))
    bind(o, "Height", "(%s) - (%s)" % (z1, z0))
    bind(o, "Placement.Base.x", x0)
    bind(o, "Placement.Base.y", y0)
    bind(o, "Placement.Base.z", z0)
    return o


def cyl_z(doc, name, x, y, z0, z1, d):
    o = doc.addObject("Part::Cylinder", name)
    bind(o, "Radius", "(%s) / 2" % d)
    bind(o, "Height", "(%s) - (%s)" % (z1, z0))
    bind(o, "Placement.Base.x", x)
    bind(o, "Placement.Base.y", y)
    bind(o, "Placement.Base.z", z0)
    return o


def rrect(doc, name, x0, x1, y0, y1, z0, z1, r):
    """Rounded rectangle prism from primitives (no fillets, so no toponaming)."""
    r = "(%s)" % r  # r may be a sum: "x1 - pcb_r + gap" is not "x1 - (pcb_r + gap)"
    parts = [
        box(doc, name + "_a", "%s + %s" % (x0, r), "%s - %s" % (x1, r), y0, y1, z0, z1),
        box(doc, name + "_b", x0, x1, "%s + %s" % (y0, r), "%s - %s" % (y1, r), z0, z1),
    ]
    for i, (cx, cy) in enumerate((("%s + %s" % (x0, r), "%s + %s" % (y0, r)),
                                  ("%s - %s" % (x1, r), "%s + %s" % (y0, r)),
                                  ("%s + %s" % (x0, r), "%s - %s" % (y1, r)),
                                  ("%s - %s" % (x1, r), "%s - %s" % (y1, r)))):
        parts.append(cyl_z(doc, "%s_c%d" % (name, i), cx, cy, z0, z1, "2 * (%s)" % r))
    return fuse(doc, name, parts)


def rrect_round(doc, name, x0, x1, y0, y1, z0, z1, r, er, face):
    """rrect() with the perimeter of one face rounded by er, like the Ruiz case.

    A core rrect inset by er (corner radius r - er) is grown by er with a 3D offset (arc
    joins), which rounds every edge, then a box trims it flat on the other face. No edge is
    referenced, so it survives parameter changes. face is "top" (round the z1 face) or
    "bottom" (round the z0 face). Needs er < r.
    """
    r, er = "(%s)" % r, "(%s)" % er
    if face == "top":
        cz0, cz1 = "%s - %s - 1" % (z0, er), "%s - %s" % (z1, er)
        tz0, tz1 = z0, "%s + 1" % z1
    else:
        cz0, cz1 = "%s + %s" % (z0, er), "%s + %s + 1" % (z1, er)
        tz0, tz1 = "%s - 1" % z0, z1
    core = rrect(doc, name + "_core", "%s + %s" % (x0, er), "%s - %s" % (x1, er),
                 "%s + %s" % (y0, er), "%s - %s" % (y1, er), cz0, cz1, "%s - %s" % (r, er))
    grown = doc.addObject("Part::Offset", name + "_grown")
    grown.Source = core
    grown.Join = 0  # arc
    grown.Mode = 0  # skin
    bind(grown, "Value", er)
    trim = box(doc, name + "_trim", "%s - 1" % x0, "%s + 1" % x1, "%s - 1" % y0, "%s + 1" % y1,
               tz0, tz1)
    o = doc.addObject("Part::Common", name)
    o.Base = grown
    o.Tool = trim
    o.Refine = True
    core.Visibility = grown.Visibility = trim.Visibility = False
    return o


def fuse(doc, name, shapes, refine=True):
    o = doc.addObject("Part::MultiFuse", name)
    o.Shapes = shapes
    o.Refine = refine
    for s in shapes:
        s.Visibility = False
    return o


def cut(doc, name, base, tools):
    tool = tools[0] if len(tools) == 1 else fuse(doc, name + "_tools", tools)
    o = doc.addObject("Part::Cut", name)
    o.Base = base
    o.Tool = tool
    o.Refine = True
    base.Visibility = False
    tool.Visibility = False
    return o


HOLES = (("bl", "hole_x0", "hole_y0"), ("br", "hole_x1", "hole_y0"),
         ("tl", "hole_x0", "hole_y1"), ("tr", "hole_x1", "hole_y1"))


def posts(doc, tag, z0, z1, x0="in_x0 - %g" % EPS, x1="in_x1 + %g" % EPS,
          y1="in_y1 + %g" % EPS):
    """A post at each hole, tied by a web to the wall (or lip) at x0 / x1, and the top
    posts also up to y1, so no sliver gap is left beside them."""
    out = []
    for h, hx, hy in HOLES:
        out.append(cyl_z(doc, "%sPost_%s" % (tag, h), hx, hy, z0, z1, "post_d"))
        wx0, wx1 = (x0, hx) if hx == "hole_x0" else (hx, x1)
        out.append(box(doc, "%sWeb_%s" % (tag, h), wx0, wx1,
                       "%s - post_d / 2" % hy, "%s + post_d / 2" % hy, z0, z1))
        if hy == "hole_y1":  # the top posts sit in the board's corner arcs: tie them up too
            out.append(box(doc, "%sWebUp_%s" % (tag, h), "%s - post_d / 2" % hx,
                           "%s + post_d / 2" % hx, hy, y1, z0, z1))
    return out


def fov_cone(doc, name):
    o = doc.addObject("Part::Cone", name)
    bind(o, "Radius1", "glass_d / 2")
    bind(o, "Radius2", "glass_d / 2 + fov_len * tan(fov_half)")
    bind(o, "Height", "fov_len")
    bind(o, "Placement.Base.x", "lens_x")
    bind(o, "Placement.Base.y", "lens_y")
    bind(o, "Placement.Base.z", "lens_z")
    return o


def build_front(doc):
    # Walls run back to the back plate; the back's lip snaps inside them.
    shell = rrect_round(doc, "FrontOuter", "out_x0", "out_x1", "out_y0", "out_y1",
                        "z_floor", "z_front", "corner_r", "edge_r", "top")
    cavity = rrect(doc, "FrontCavity", "in_x0", "in_x1", "in_y0", "in_y1",
                   "z_floor - 1", "z_plate", "pcb_r + gap")
    pins = [cyl_z(doc, "FrontPin_" + h, hx, hy,
                  "pin_tip_gap - socket_depth", "pcb_t + %g" % EPS, "pin_d")
            for h, hx, hy in HOLES]
    body = fuse(doc, "FrontBody", [cut(doc, "FrontShell", shell, [cavity])]
                + posts(doc, "Front", "pcb_t", "z_plate + %g" % EPS) + pins)
    tools = []
    for side, x in (("l", "bead_x0"), ("r", "bead_x1")):
        tools.append(y_cyl(doc, "SnapGroove_" + side, x, "bead_r + groove_clear",
                           "bead_y0 - groove_clear", "bead_y0 + bead_len + groove_clear",
                           "z_floor + bead_z"))
    tools.append(box(doc, "FrontCableSlot", "lens_x - cable_w / 2", "lens_x + cable_w / 2",
                     "out_y0 - 1", "in_y0 + 1", "z_floor - 1", "0"))
    tools.append(cyl_z(doc, "BarrelHole", "lens_x", "lens_y", "z_plate - 1",
                       "z_front + 1", "barrel_d + 2 * barrel_clear"))
    chamfer = doc.addObject("Part::Cone", "LensChamfer")
    bind(chamfer, "Radius1", "barrel_d / 2 + barrel_clear")
    bind(chamfer, "Radius2", "barrel_d / 2 + barrel_clear + lens_chamfer + %g" % EPS)
    bind(chamfer, "Height", "lens_chamfer + %g" % EPS)
    bind(chamfer, "Placement.Base.x", "lens_x")
    bind(chamfer, "Placement.Base.y", "lens_y")
    bind(chamfer, "Placement.Base.z", "z_front - lens_chamfer")
    tools.append(chamfer)
    tools.append(fov_cone(doc, "FovCut"))
    return cut(doc, "Front", body, tools)


def thread_cutter(doc):
    """Bore plus a helical 60 degree groove, axis +Y from the foot's bottom face."""
    base = ("foot_y0 - pitch", "lens_x", "thread_z")
    helix = doc.addObject("Part::Helix", "ThreadHelix")
    bind(helix, "Pitch", "pitch")
    bind(helix, "Height", "thread_len + pitch")
    bind(helix, "Radius", "thread_r_min")
    helix.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), -90)
    bind(helix, "Placement.Base.x", base[1])
    bind(helix, "Placement.Base.y", base[0])
    bind(helix, "Placement.Base.z", base[2])

    # Groove profile in the XY plane through the axis: x radial, y axial.
    sk = doc.addObject("Sketcher::SketchObject", "ThreadProfile")
    bind(sk, "Placement.Base.x", base[1])
    bind(sk, "Placement.Base.y", base[0])
    bind(sk, "Placement.Base.z", base[2])
    pts = [App.Vector(2.4, -0.5, 0), App.Vector(3.3, -0.05, 0),
           App.Vector(3.3, 0.05, 0), App.Vector(2.4, 0.5, 0)]
    for i in range(4):
        sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4]))
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
    # Inner edge 0.1 inside the bore, flanks at 30 degrees, flat of pitch / 8 at the root.
    r_in = "thread_r_min - 0.1"
    half_in = "(pitch * 0.375 + 0.1 * tan(30))"
    exprs = [(0, 1, "%s" % r_in, "-" + half_in), (1, 1, "thread_r_max", "-pitch / 16"),
             (2, 1, "thread_r_max", "pitch / 16"), (3, 1, "%s" % r_in, half_in)]
    for geo, pos, ex, ey in exprs:
        cx = sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, geo, pos, 1.0))
        cy = sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, geo, pos, 1.0))
        sk.setExpression("Constraints[%d]" % cx, e(ex))
        sk.setExpression("Constraints[%d]" % cy, e(ey))

    sweep = doc.addObject("Part::Sweep", "ThreadGroove")
    sweep.Sections = [sk]
    sweep.Spine = (helix, ["Edge1"])
    sweep.Solid = True
    sweep.Frenet = True
    helix.Visibility = sk.Visibility = False

    bore = doc.addObject("Part::Cylinder", "ThreadBore")
    bind(bore, "Radius", "thread_r_min")
    bind(bore, "Height", "thread_len + 1")
    bore.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), -90)
    bind(bore, "Placement.Base.x", "lens_x")
    bind(bore, "Placement.Base.y", "foot_y0 - 1")
    bind(bore, "Placement.Base.z", "thread_z")

    lead = doc.addObject("Part::Cone", "ThreadLead")
    bind(lead, "Radius1", "thread_r_max + 0.6")
    bind(lead, "Radius2", "thread_r_min")
    bind(lead, "Height", "thread_r_max + 0.6 - thread_r_min")
    lead.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), -90)
    bind(lead, "Placement.Base.x", "lens_x")
    bind(lead, "Placement.Base.y", "foot_y0 - 0.01")
    bind(lead, "Placement.Base.z", "thread_z")
    return [bore, sweep, lead]


def build_back(doc):
    plate = rrect_round(doc, "BackOuter", "out_x0", "out_x1", "out_y0", "out_y1",
                        "z_back", "z_floor", "corner_r", "back_edge_r", "bottom")
    # U-shaped snap lip inside the front walls. Open at the bottom, where the ribbon
    # connector sits right at the board edge.
    lip_out = rrect(doc, "LipOuter", "lip_x0", "lip_x1", "in_y0 + lip_gap", "lip_y1",
                    "z_floor - %g" % EPS, "-lip_clear", "pcb_r + gap - lip_gap")
    lip_in = rrect(doc, "LipInner", "lip_x0 + lip_t", "lip_x1 - lip_t",
                   "in_y0 + lip_gap + lip_t", "lip_y1 - lip_t", "z_floor - 1", "1",
                   "pcb_r + gap - lip_gap - lip_t")
    # Open past the lip's bottom corner arcs, which would curl into the ends of the connector.
    lip_open = box(doc, "LipOpen", "in_x0 - 1", "in_x1 + 1", "in_y0 - 1",
                   "in_y0 + pcb_r + gap + 0.2", "z_floor", "1")
    lip = cut(doc, "Lip", lip_out, [lip_in, lip_open])
    beads = [y_cyl(doc, "SnapBead_" + side, x, "bead_r", "bead_y0", "bead_y0 + bead_len",
                   "z_floor + bead_z")
             for side, x in (("l", "bead_x0"), ("r", "bead_x1"))]
    # Full case width and forward to the parting line, so nothing overhangs when the back
    # prints foot-down. The rise runs up the back face for strength.
    # Two boxes: under the plate it bites 0.6 mm into it (a face flush with the plate's
    # rounded edge is tangent and breaks the fusion); under the front walls it stops at
    # their bottom face.
    foot = box(doc, "Foot", "out_x0", "out_x1", "foot_y0", "out_y0 + 0.6", "foot_z0", "z_floor")
    foot_front = box(doc, "FootFront", "out_x0", "out_x1", "foot_y0", "out_y0",
                     "z_floor - 0.5", "z_front")
    rise = box(doc, "FootRise", "out_x0", "out_x1", "out_y0 - %g" % EPS, "out_y0 + foot_rise",
               "foot_z0", "z_back + %g" % EPS)
    body = fuse(doc, "BackBody", [plate, lip, foot, foot_front, rise]
                + posts(doc, "Back", "z_floor - %g" % EPS, "0",
                        "lip_x0 + lip_t / 2", "lip_x1 - lip_t / 2", "lip_y1 - lip_t / 2"))
    tools = [cyl_z(doc, "BackSocket_" + h, hx, hy, "-socket_depth", "1", "socket_d")
             for h, hx, hy in HOLES]
    # Guard: above the plate, nothing on the back may reach past the lip's outer outline
    # into the front walls (the post webs' box corners would, at the board's corner arcs).
    envelope = rrect(doc, "LipEnvelope", "lip_x0", "lip_x1", "in_y0 + lip_gap", "lip_y1",
                     "z_floor", "2", "pcb_r + gap - lip_gap")
    outside = box(doc, "WallZone", "out_x0 - 1", "out_x1 + 1", "out_y0", "out_y1 + 1",
                  "z_floor", "1")
    tools.append(cut(doc, "OutsideLip", outside, [envelope]))
    tools.append(box(doc, "CableSlot", "lens_x - cable_w / 2", "lens_x + cable_w / 2",
                     "foot_y0 - 1", "out_y0 + %g" % EPS, "z_floor", "0"))
    tools += thread_cutter(doc)
    # The beads go on after the guard cut: they reach past the lip into the grooves on purpose.
    return fuse(doc, "Back", [cut(doc, "BackCut", body, tools)] + beads)


def y_cyl(doc, name, x, r, y0, y1, z):
    """Cylinder along Y, for the snap bead and groove."""
    o = doc.addObject("Part::Cylinder", name)
    bind(o, "Radius", r)
    bind(o, "Height", "(%s) - (%s)" % (y1, y0))
    o.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), -90)
    bind(o, "Placement.Base.x", x)
    bind(o, "Placement.Base.y", y0)
    bind(o, "Placement.Base.z", z)
    return o


def camera_shapes():
    """Stand-in Camera Module 3 Wide in the world frame, from the drawing."""
    g = {n: float(v) for n, v, _ in PARAMS if isinstance(v, float)}
    w, h, t, r = g["pcb_w"], g["pcb_h"], g["pcb_t"], g["pcb_r"]
    lx, ly = g["lens_x"], h - g["lens_top"]
    pcb = Part.makeBox(w - 2 * r, h, t, App.Vector(r, 0, 0))
    pcb = pcb.fuse(Part.makeBox(w, h - 2 * r, t, App.Vector(0, r, 0)))
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):
        pcb = pcb.fuse(Part.makeCylinder(r, t, App.Vector(cx, cy, 0)))
    hy1 = h - g["hole_top"]
    for cx in (g["hole_x0"], w - g["hole_x0"]):
        for cy in (hy1, hy1 - g["hole_dy"]):
            pcb = pcb.cut(Part.makeCylinder(g["hole_d"] / 2, t + 1, App.Vector(cx, cy, -0.5)))
    pcb = pcb.removeSplitter()
    hw, hh = g["holder_w"], g["holder_h"]
    holder = Part.makeBox(hw, hw, hh, App.Vector(lx - hw / 2, ly - hw / 2, t))
    barrel = Part.makeCylinder(g["barrel_d"] / 2, g["lens_z"] - t - hh - 0.05,
                               App.Vector(lx, ly, t + hh))
    glass = Part.makeCylinder(g["glass_d"] / 2, 0.05, App.Vector(lx, ly, g["lens_z"] - 0.05))
    flex = Part.makeBox(g["flex_w"], g["flex_h"], g["flex_t"],
                        App.Vector(lx - g["flex_w"] / 2, h - g["flex_h"], t))
    conn = Part.makeBox(g["conn_w"], g["conn_h"], g["conn_t"],
                        App.Vector(w / 2 - g["conn_w"] / 2, 0, -g["conn_t"]))
    return {"CamPCB": pcb, "CamHolder": holder, "CamBarrel": barrel, "CamGlass": glass,
            "CamFlex": flex, "CamConnector": conn}


# View state. FreeCAD 1.1 has no ViewObject headless, so GuiDocument.xml is written into
# the saved FCStd directly. Same layout as the Port Authority build_case.py files.

VIEW_PROP = """        <ViewProvider name="%s" expanded="0">
            <Properties Count="6" TransientCount="0">
                <Property name="LineColor" type="App::PropertyColor" status="1">
                    <PropertyColor value="%d"/>
                </Property>
                <Property name="LineWidth" type="App::PropertyFloatConstraint" status="1">
                    <Float value="%.4f"/>
                </Property>
                <Property name="PointColor" type="App::PropertyColor" status="1">
                    <PropertyColor value="%d"/>
                </Property>
                <Property name="ShapeAppearance" type="App::PropertyMaterialList" status="1">
                    <MaterialList file="%s" version="3"/>
                </Property>
                <Property name="Transparency" type="App::PropertyPercent" status="1">
                    <Integer value="%d"/>
                </Property>
                <Property name="Visibility" type="App::PropertyBool" status="1">
                    <Bool value="%s"/>
                </Property>
            </Properties>
        </ViewProvider>
"""


def _rgb(spec):
    hx = spec.lstrip("#")
    r, g, b = (int(hx[i:i + 2], 16) for i in (0, 2, 4))
    return (r << 24) | (g << 16) | (b << 8) | 0xFF


def _material_blob(diffuse, transparency):
    return (struct.pack("<I", 1) + struct.pack("<I", _rgb("#333333"))
            + struct.pack("<I", diffuse) + struct.pack("<I", 0x000000FF)
            + struct.pack("<I", 0x000000FF)
            + struct.pack("<ff", 0.2, transparency / 100.0)
            + struct.pack("<III", 0, 0, 0))


def write_view_state(doc_path, styles, hidden):
    entries, blobs = [], {}
    for i, name in enumerate(list(styles) + hidden):
        color, line, transp = styles.get(name, ("#808080", "#000000", 0))
        blob = "ShapeAppearance" if i == 0 else "ShapeAppearance%d" % i
        blobs[blob] = _material_blob(_rgb(color), transp)
        entries.append(VIEW_PROP % (name, _rgb(line), 2.0, _rgb(line), blob, transp,
                                    "false" if name in hidden else "true"))
    xml = ("<?xml version='1.0' encoding='utf-8'?>\n"
           '<Document SchemaVersion="1">\n'
           '    <ViewProviderData Count="%d">\n%s    </ViewProviderData>\n'
           "</Document>\n" % (len(entries), "".join(entries)))
    with zipfile.ZipFile(doc_path, "r") as z:
        keep = [(n, z.read(n)) for n in z.namelist()
                if n != "GuiDocument.xml" and n not in blobs]
    with zipfile.ZipFile(doc_path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in keep:
            z.writestr(n, data)
        z.writestr("GuiDocument.xml", xml)
        for n, data in blobs.items():
            z.writestr(n, data)


STEP_REF = os.path.join(HERE, "ref", "rpi-cm3-step", "Camera_module_3_wide_model_simple.stp")


def camera_step():
    """The official Camera Module 3 Wide STEP in the case frame, or None if it isn't in ref/.

    STEP frame: X 0..23.862 toward the connector edge, Y 0..25, lens toward -Z, PCB back at
    Z = 0.013. Case frame: X = 25 - Y, Y = 23.862 - X, Z = 0.013 - Z (a proper rotation).
    """
    if not os.path.exists(STEP_REF):
        return None
    shape = Part.read(STEP_REF)
    m = App.Matrix(0, -1, 0, 25.0, -1, 0, 0, 23.862, 0, 0, -1, 0.013, 0, 0, 0, 1)
    return _placed(shape, m)


def _placed(shape, m):
    s = shape.copy()
    s.transformShape(m, True)
    return s


def check(doc, front, back, cam):
    ok = True

    def report(label, good, detail=""):
        nonlocal ok
        ok = ok and good
        print("%-5s %-26s %s" % ("ok" if good else "FAIL", label, detail))

    v = lambda name: doc.getObject("Params").get(name)
    for o in (front, back):
        s = o.Shape
        report(o.Name + " valid", s.isValid())
        report(o.Name + " solids", len(s.Solids) == 1, "%d" % len(s.Solids))
        report(o.Name + " volume", s.Volume > 0, "%.1f mm3" % s.Volume)
        for name, c in cam.items():
            vol = s.common(c).Volume
            report("%s vs %s" % (o.Name, name), vol < 1e-3, "%.4f mm3" % vol)
    vol = front.Shape.common(back.Shape).Volume
    report("front vs back", vol < 1e-3, "%.4f mm3" % vol)

    # Strongest gate: clash against the official STEP, solid by solid.
    real = camera_step()
    if real is None:
        print("skip  camera STEP clash          %s not found" % STEP_REF)
    else:
        for o in (front, back):
            s, worst = o.Shape, (0.0, None)
            total = 0.0
            for so in real.Solids:
                if not s.BoundBox.intersect(so.BoundBox):
                    continue
                vol = s.common(so).Volume
                total += vol
                if vol > worst[0]:
                    worst = (vol, so.BoundBox.Center)
            where = "" if worst[1] is None else " worst at (%.1f, %.1f, %.1f)" % tuple(worst[1])
            report("%s vs camera STEP" % o.Name, total < 1e-3, "%.4f mm3%s" % (total, where))
        layers = [so.BoundBox for so in real.Solids
                  if so.BoundBox.XLength > 24 and so.BoundBox.YLength > 23]
        z0, z1 = min(b.ZMin for b in layers), max(b.ZMax for b in layers)
        report("STEP PCB matches pcb_t", abs(z1 - z0 - v("pcb_t")) < 0.02,
               "STEP layers %.3f mm, pcb_t %.3f" % (z1 - z0, v("pcb_t")))
        lens_front = real.BoundBox.ZMax
        report("STEP lens front matches lens_z", abs(lens_front - v("lens_z")) < 0.02,
               "STEP %.3f, lens_z %.3f" % (lens_front, v("lens_z")))

    # Field of view: a cone from the glass rim, half angle fov_diag / 2 + fov_margin.
    fov = doc.getObject("FovCut").Shape
    for o in (front, back):
        vol = o.Shape.common(fov).Volume
        report("FOV clear of " + o.Name, vol < 1e-4, "%.5f mm3 in the cone" % vol)
    margin = v("lens_z") - v("z_front")
    report("front face behind glass", True,
           "%.2f mm (negative means the chamfered cut is doing the work)" % margin)

    # Wall left where the face round passes the cavity's inner corner.
    er = v("edge_r")
    report("edge_r below corner_r", er < v("corner_r") - 0.3, "%.2f < %.2f" % (er, v("corner_r")))
    for label, t in (("front", v("front_t")),):
        d = ((v("wall") - er) ** 2 + (t - er) ** 2) ** 0.5
        inside = (v("wall") - er) < 0 or (t - er) < 0
        left = er - d if er >= min(v("wall"), t) or inside else abs(d - er)
        left = min(left, v("wall"), t)
        report("wall at %s face round" % label, left >= 1.2, "%.2f mm" % left)
    gap = v("z_plate") - (v("pcb_t") + v("holder_h"))
    report("plate clears lens holder", gap >= 0.3, "%.2f mm" % gap)
    d = front.Shape.distToShape(cam["CamPCB"])[0]
    report("front posts touch PCB", d < 1e-3, "gap %.4f" % d)
    d = back.Shape.distToShape(cam["CamPCB"])[0]
    report("back posts touch PCB", d < 1e-3, "gap %.4f" % d)
    wall = v("thread_z") - v("thread_r_max") - v("foot_z0")
    report("thread wall, back", wall >= 1.2, "%.2f mm" % wall)
    wall = v("z_floor") - v("thread_z") - v("thread_r_max")
    report("thread wall, front", wall >= 1.2, "%.2f mm" % wall)
    # Fit against a nominal male screw: major d, minor d - 1.2269 P (UNC external).
    bolt_major = v("thread_d") / 2
    bolt_minor = (v("thread_d") - 1.2269 * v("pitch")) / 2
    report("thread root clears bolt crest", v("thread_r_max") - bolt_major >= 0.1,
           "%.2f mm radial" % (v("thread_r_max") - bolt_major))
    report("thread bore clears bolt root", v("thread_r_min") - bolt_minor >= 0.1,
           "%.2f mm radial" % (v("thread_r_min") - bolt_minor))
    engage = (v("thread_r_max") - v("thread_r_min"))
    report("thread engagement depth", engage >= 0.35 * v("pitch"),
           "%.2f mm of %.2f mm pitch" % (engage, v("pitch")))
    groove = doc.getObject("ThreadGroove").Shape
    report("thread groove valid", groove.isValid() and len(groove.Solids) == 1,
           "%d solid" % len(groove.Solids))

    # Pins and snap.
    report("pin clears board hole", v("hole_d") - v("pin_d") >= 0.2,
           "%.2f mm on diameter" % (v("hole_d") - v("pin_d")))
    report("socket clears pin", v("socket_d") - v("pin_d") >= 0.3,
           "%.2f mm on diameter" % (v("socket_d") - v("pin_d")))
    report("snap interference", 0.1 <= v("bead_int") <= 0.3, "%.2f mm per side" % v("bead_int"))
    ymid = v("bead_y0") + v("bead_len") / 2
    zb = v("z_floor") + v("bead_z")
    tip_l = App.Vector(v("bead_x0") - v("bead_r") + 0.05, ymid, zb)
    tip_r = App.Vector(v("bead_x1") + v("bead_r") - 0.05, ymid, zb)
    present = all(back.Shape.isInside(p, 0.001, True) for p in (tip_l, tip_r))
    report("snap beads present", present, "bead tips inside the back shell")
    lip_h = v("back_gap") - v("lip_clear")
    report("bead on the lip", v("bead_z") + v("bead_r") <= lip_h, "top %.2f of %.2f mm lip"
           % (v("bead_z") + v("bead_r"), lip_h))
    # Overhangs in print orientation: downward faces steeper than 45 degrees, off the bed.
    for o, rot in ((front, PRINT_ROT["front"]), (back, PRINT_ROT["back"])):
        s = o.Shape.copy()
        s.rotate(App.Vector(0, 0, 0), *rot)
        z0 = s.optimalBoundingBox().ZMin  # BoundBox is loose around curved faces
        area, bridge, thread, worst = 0.0, 0.0, 0.0, None
        for f in s.Faces:
            if f.BoundBox.ZMax < z0 + 0.2:
                continue  # on the bed
            # The thread's upper flanks face down at 60 degrees; printed threads take that.
            c = f.CenterOfMass  # back print frame: thread axis at (lens_x, -thread_z)
            if o is back and ((c.x - v("lens_x")) ** 2 + (c.y + v("thread_z")) ** 2
                              < (v("thread_r_max") + 0.7) ** 2):
                thread += f.Area
                continue
            # A flat ceiling held at both ends by walls is a bridge, not an overhang:
            # the back shell's cavity ceiling under the top wall, spanning the side walls.
            # On the back that ceiling has arched ends (the cavity's rounded corners), so take the
            # whole band under the top wall; in the back print frame, print Z is case Y.
            ceiling = (o is back and f.BoundBox.ZMin >= v("in_y1") - v("pcb_r") - v("gap") - 0.1
                       and f.BoundBox.ZMax <= v("in_y1") + 0.01)
            if ceiling or (f.Surface.__class__.__name__ == "Plane" and f.normalAt(0, 0).z < -0.99
                           and f.BoundBox.XLength >= v("pcb_w")):
                bridge += f.Area
                continue
            for tri in MeshPart.meshFromShape(Shape=f, LinearDeflection=0.05).Facets:
                if tri.Normal.z < -0.707 and min(p[2] for p in tri.Points) > z0 + 0.2:
                    area += tri.Area
                    if worst is None or tri.Area > worst[0]:
                        worst = (tri.Area, tri.Points[0])
        where = "" if worst is None else " largest near (%.1f, %.1f, %.1f)" % tuple(worst[1])
        # What is left on the back is the post undersides (3.2 mm cantilevers off the back
        # plate) and the tops of horizontal M2 holes, all fine unsupported on FDM.
        report(o.Name + " overhang area", area < 150.0,
               "%.1f mm2 (not counted: %.1f bridge, %.1f thread)%s"
               % (area, bridge, thread, where))
    bb = front.Shape.optimalBoundingBox().united(back.Shape.optimalBoundingBox())
    print("      case bbox X %.2f..%.2f  Y %.2f..%.2f  Z %.2f..%.2f"
          % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
    return ok


def export(shape, base, rot=None):
    shape.exportStep(base + ".step")
    s = shape.copy()
    if rot:
        s.rotate(App.Vector(0, 0, 0), *rot)
    bb = s.optimalBoundingBox()
    s.translate(App.Vector(-bb.Center.x, -bb.Center.y, -bb.ZMin))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02,
                           AngularDeflection=0.2).write(base + ".3mf")


doc = App.newDocument("cm3_case")
build_sheet(doc)
front = build_front(doc)
back = build_back(doc)
cam = camera_shapes()
for name, shape in cam.items():
    doc.addObject("Part::Feature", name).Shape = shape
doc.recompute()

broken = [o.Name for o in doc.Objects if "Invalid" in o.State or "Error" in o.State]
if broken:
    doc.saveAs(os.path.join(OUT, "failed.FCStd"))
    raise SystemExit("recompute failed: " + ", ".join(broken) + " (saved build/failed.FCStd)")

ok = check(doc, front, back, cam)

doc_path = os.path.join(OUT, "cm3_case.FCStd")
doc.saveAs(doc_path)
hidden = [o.Name for o in doc.Objects
          if hasattr(o, "Visibility") and not o.Visibility
          and o.TypeId != "Spreadsheet::Sheet"]
write_view_state(doc_path, {
    "Front": ("#1A1A1F", "#D9FF00", 0),
    "Back": ("#1A1A1F", "#FF2D9B", 0),
    "CamPCB": ("#0E3A2C", "#00E5C7", 30),
    "CamHolder": ("#202020", "#404040", 30),
    "CamBarrel": ("#303030", "#404040", 30),
    "CamGlass": ("#4060A0", "#4060A0", 30),
    "CamFlex": ("#C08020", "#C08020", 30),
    "CamConnector": ("#E0E0E0", "#404040", 30),
}, hidden + ["FovCut"])

export(front.Shape, os.path.join(OUT, "front"), PRINT_ROT["front"])
export(back.Shape, os.path.join(OUT, "back"), PRINT_ROT["back"])
Part.makeCompound(list(cam.values())).exportStep(os.path.join(OUT, "camera.step"))

print("wrote", OUT)
print("CHECKS PASS" if ok else "CHECKS FAIL")
