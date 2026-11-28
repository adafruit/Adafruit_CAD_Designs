# SPDX-FileCopyrightText: 2026 Mikey Sklar
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Builds qtpy-dap-breakout.kicad_pcb from scratch (idempotent).
# Single-sided milled carrier: an Adafruit QT Py CH32V203 (PID 5996) plugs
# into the inner rows of two 2x7 2.54 mm SMD female sockets (cut from Adafruit
# 2187, the short 2x20 Pi HAT socket); the outer rows repeat every QT Py pin
# for jumper wires, like the Proto Doubler PiCowbell (5906). A 2x5 1.27 mm SMT
# box header (PID 752,
# ARM Cortex 10-pin) takes a 1675 IDC cable to the target (ARM SWD, or the
# Metro CH32V4x7 JDEBUG where pin 2 carries WCH SWIO).
#
# Pins follow Liz's Adafruit_DAP ch32_host examples:
#   A3 -> pin 2 SWDIO/SWIO, A2 -> pin 4 SWCLK, A0 -> pin 10 nRESET,
#   GND -> 3/5/9. Pin 1 VTref is NC, like the Pi Debug Probe: the target
#   powers itself (the Metro ties VTref to its own 3.3 V rail). Pins 6/7/8 NC.
#   UART is not broken out.
#
# Milled-board rules (milled-pcb-design skill): F.Cu only, GND pour, no vias,
# 45 deg miters on every bend, signal width 0.76 (box header pad short side).
# Each socket's two pads per pin are tied by a straight trace under the body.
# Copper may run under the QT Py: it sits ~8.5 mm up on the sockets (stock
# KiCad socket model height; the cut-down 2187 is shorter, unverified).
#
# Run with KiCad's bundled python:
#   /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 build_pcb.py

import json
import math
import os

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "qtpy-dap-breakout"
PCB = os.path.join(HERE, NAME + ".kicad_pcb")
PRO = os.path.join(HERE, NAME + ".kicad_pro")
FPLIB = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
LOCAL_PRETTY = os.path.join(HERE, "..", "models", "QTPyDAP.pretty")
BOX_FP = "BoxHeader_2x05_P1.27mm_SMD_752"
MODEL_BOX = os.path.join(HERE, "..", "models", BOX_FP + ".step")
MODEL_QTPY = os.path.join(HERE, "..", "models", "QTPy_CH32V203_5996.stpZ")

# ---- board dimensions first ---------------------------------------------------
W, H, R = 40.0, 42.0, 2.0
HOLE_D = 2.7
HOLES = [(4.0, 4.0), (W - 4.0, 4.0), (4.0, H - 4.0), (W - 4.0, H - 4.0)]

# ---- design rules -------------------------------------------------------------
CLEARANCE = 0.4
MIN_TRACK = 0.4
EDGE_CLEAR = 0.5
SIG_W = 0.76   # = 752 box header SMD pad short side (Adafruit Eagle 2X05_1.27MM_BOX_POSTS)
GND_W = 1.0

# ---- placement ----------------------------------------------------------------
QX, QY = W / 2, 16.5          # QT Py centre (pin 4 row)
ROW = 15.24                   # QT Py row spacing (0.6")
XL, XR = QX - ROW / 2, QX + ROW / 2   # inner socket rows (QT Py pins)
SROW = 2.54                   # socket row pitch: outer rows at XL - SROW, XR + SROW
HX, HY = QX - 1.4, 36.5        # box header centre: ~5.9 mm clear of the QT Py edge for the IDC plug and pin labels
QTPY_Z = 8.5                  # QT Py underside above the carrier (socket height)

board = pcbnew.CreateEmptyBoard()
mm = pcbnew.FromMM


def V(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


ds = board.GetDesignSettings()
ds.m_MinClearance = mm(CLEARANCE)
ds.m_TrackMinWidth = mm(MIN_TRACK)
ds.m_CopperEdgeClearance = mm(EDGE_CLEAR)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetClearance(mm(CLEARANCE))
nc.SetTrackWidth(mm(SIG_W))
board.SetCopperLayerCount(2)   # B.Cu stays empty

NETS = {}


def net(name):
    if name not in NETS:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        NETS[name] = n
    return NETS[name]


def load_fp(libdir, name, ref, value, pos, rot):
    fp = pcbnew.FootprintLoad(libdir, name)
    assert fp is not None, (libdir, name)
    fp.SetFPID(pcbnew.LIB_ID(os.path.basename(libdir).replace(".pretty", ""), name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(V(*pos))
    fp.SetOrientationDegrees(rot)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)
    return fp


SOCK_LIB = os.path.join(FPLIB, "Connector_PinSocket_2.54mm.pretty")
# 2x7 SMD sockets, legs out to both sides (odd pads east, even pads west at
# rot 0). Pin pair k (pads 2k-1, 2k) is QT Py pin k from the USB end. The
# QT Py takes the inner contact row; the outer row is the extra wiring row.
SOCK = "PinSocket_2x07_P2.54mm_Vertical_SMD"
jl = load_fp(SOCK_LIB, SOCK, "J1", "QT Py left (2187 cut 2x7)", (XL - SROW / 2, QY), 0)
jr = load_fp(SOCK_LIB, SOCK, "J2", "QT Py right (2187 cut 2x7)", (XR + SROW / 2, QY), 0)
if os.path.isfile(os.path.join(LOCAL_PRETTY, BOX_FP + ".kicad_mod")):
    jh = load_fp(LOCAL_PRETTY, BOX_FP, "J3", "SWD 2x5 (752)", (HX, HY), 90)
    print("J3 footprint: local", BOX_FP)
    if os.path.isfile(MODEL_BOX) and not list(jh.Models()):
        m3 = pcbnew.FP_3DMODEL()
        m3.m_Filename = "${KIPRJMOD}/../models/" + BOX_FP + ".step"
        jh.Add3DModel(m3)
else:
    jh = load_fp(os.path.join(FPLIB, "Connector_PinHeader_1.27mm.pretty"),
                 "PinHeader_2x05_P1.27mm_Vertical_SMD", "J3", "SWD 2x5 (752)",
                 (HX, HY), 90)
    print("J3 footprint: stock PinHeader placeholder (752 footprint not ready)")


def pad_pos(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == str(num):
            q = p.GetPosition()
            return (round(pcbnew.ToMM(q.x), 4), round(pcbnew.ToMM(q.y), 4))
    raise KeyError(num)


def pad_size(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == str(num):
            b = p.GetBoundingBox()
            return (pcbnew.ToMM(b.GetWidth()), pcbnew.ToMM(b.GetHeight()))
    raise KeyError(num)


# Per QT Py pin k: (east pad, west pad) of each socket.
LE = {k: pad_pos(jl, 2 * k - 1) for k in range(1, 8)}
LW = {k: pad_pos(jl, 2 * k) for k in range(1, 8)}
RE = {k: pad_pos(jr, 2 * k - 1) for k in range(1, 8)}
RW = {k: pad_pos(jr, 2 * k) for k in range(1, 8)}
SPW = pad_size(jl, 1)[0]                     # socket pad length (x)
J = {k: pad_pos(jh, k) for k in range(1, 11)}
# QT Py pin order, top (USB end) to bottom.
QL = {1: "A0", 2: "A1", 3: "A2", 4: "A3", 5: "SDA", 6: "SCL", 7: "TX"}
QR = {1: "5V", 2: "GND", 3: "3V3", 4: "MO", 5: "MI", 6: "SCK", 7: "RX"}

# Frame checks: odd socket pads east, pin 1 at the USB end (north); header
# even row north, odd row south, pad 1/2 at the west end.
assert LE[1][0] > LW[1][0] and LE[1][1] < LE[7][1], (LE, LW)
assert RE[1][0] > RW[1][0], (RE, RW)
assert J[2][1] < HY < J[1][1], J
assert J[1][0] < J[3][0] < J[9][0] and J[2][0] < J[10][0], J
assert abs(J[1][0] - J[2][0]) < 0.01, J
TOP = J[2][1] - pad_size(jh, 2)[1] / 2      # north row pad top edge
BOT = J[1][1] + pad_size(jh, 1)[1] / 2      # south row pad bottom edge

# Every pin pair gets a net (named for the QT Py pin unless it is used), so
# the tie traces and the extra row are real connections.
LNET = {1: "RST", 2: "A1", 3: "SWCLK", 4: "SWDIO", 5: "SDA", 6: "SCL", 7: "TX"}
RNET = {1: "5V", 2: "GND", 3: "3V3", 4: "MO", 5: "MI", 6: "SCK", 7: "RX"}
NETMAP = [
    (jl, {n: LNET[(n + 1) // 2] for n in range(1, 15)}),
    (jr, {n: RNET[(n + 1) // 2] for n in range(1, 15)}),
    (jh, {2: "SWDIO", 3: "GND", 4: "SWCLK", 5: "GND", 9: "GND",
          10: "RST"}),
]
for fp, table in NETMAP:
    for p in fp.Pads():
        num = p.GetNumber()
        if num.isdigit() and int(num) in table:
            p.SetNet(net(table[int(num)]))


def add_track(a, b, netname, w):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(V(*a))
    t.SetEnd(V(*b))
    t.SetWidth(mm(w))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net(netname))
    board.Add(t)


def add_path(points, netname, w=SIG_W):
    for a, b in zip(points, points[1:]):
        add_track(a, b, netname, w)


def poly(points, netname):
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_POLY)
    s.SetPolyPoints([V(*p) for p in points])
    s.SetFilled(True)
    s.SetWidth(0)
    s.SetLayer(pcbnew.F_Cu)
    s.SetNet(net(netname))
    board.Add(s)


# Tie each socket's two pads per pin straight across under the socket body.
for k in range(1, 8):
    add_path([LW[k], LE[k]], LNET[k])
    add_path([RW[k], RE[k]], RNET[k])

# Lanes (x). Under-QT Py lanes nest: the lower QT Py pin takes the lane
# nearer the socket. The three signal lanes are evenly spaced at LANE_P so the
# GND pour runs between them (gap 2.54 - 0.76 = 1.78 mm; pour 0.78 mm wide
# after 0.5 mm clearance each side). SWDIO drops straight into pad 2 and RST
# into pad 10; SWCLK runs over NC pad 6 and jogs 45 deg one pitch west into pad 4.
LE_EDGE = LE[1][0] + SPW / 2                 # east end of the left east pads
RE_EDGE = RE[1][0] + SPW / 2                 # east end of the right east pads
LANE_P = 2.54
A3_X = J[2][0]                 # SWDIO, pad 2
A2_X = A3_X + LANE_P           # SWCLK, over NC pad 6
A0_X = A3_X + 2 * LANE_P       # RST, pad 10
assert abs(A2_X - J[6][0]) < 0.01 and abs(A0_X - J[10][0]) < 0.01, J
V3_X = RE_EDGE + 0.4 + SIG_W / 2 + 0.1   # right pin-name column
assert A3_X - SIG_W / 2 - LE_EDGE >= 0.45, (A3_X, LE_EDGE)


def east_exit(pad, lane_x, y_end, netname):
    """East off a left-socket east pad, 45 down, south on lane_x to y_end."""
    x, y = pad
    return [(x, y), (lane_x - 0.7, y), (lane_x, y + 0.7), (lane_x, y_end)]


add_path(east_exit(LE[4], A3_X, TOP + 0.3, "SWDIO"), "SWDIO")
add_path(east_exit(LE[1], A0_X, TOP + 0.3, "RST"), "RST")
x4 = J[4][0]
dx = A2_X - x4
yj = TOP - 0.5 - dx            # jog ends 0.5 above the pad row (room for pin labels above)
add_path(east_exit(LE[3], A2_X, yj, "SWCLK") + [(x4, yj + dx), (x4, TOP + 0.3)], "SWCLK")

# GND: no trace. Every GND pad (right socket pin 2, header 3/5/9) joins the
# F.Cu GND pour with a solid connection.

# Header pin 1 (VTref) is left unconnected: no 3V3 to the target.


# ---- outline, holes -----------------------------------------------------------
def edge_line(a, b):
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(V(*a))
    s.SetEnd(V(*b))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.05))
    board.Add(s)


def edge_arc(center, a, b):
    ax, ay = a[0] - center[0], a[1] - center[1]
    bx, by_ = b[0] - center[0], b[1] - center[1]
    mx, my = ax + bx, ay + by_
    k = R / math.hypot(mx, my)
    mid = (center[0] + mx * k, center[1] + my * k)
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(V(*a), V(*mid), V(*b))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.05))
    board.Add(s)


edge_line((R, 0), (W - R, 0))
edge_line((W, R), (W, H - R))
edge_line((W - R, H), (R, H))
edge_line((0, H - R), (0, R))
edge_arc((W - R, R), (W - R, 0), (W, R))
edge_arc((W - R, H - R), (W, H - R), (W - R, H))
edge_arc((R, H - R), (R, H), (0, H - R))
edge_arc((R, R), (0, R), (R, 0))
for hx, hy in HOLES:
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_CIRCLE)
    s.SetCenter(V(hx, hy))
    s.SetEnd(V(hx + HOLE_D / 2, hy))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.05))
    board.Add(s)


# ---- silkscreen ---------------------------------------------------------------
def silk(text, x, y, size=0.8, just=0, bold=False, angle=0):
    t = pcbnew.PCB_TEXT(board)
    if angle:
        t.SetTextAngleDegrees(angle)
    t.SetText(text)
    t.SetPosition(V(x, y))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(V(size, size))
    t.SetTextThickness(mm(size * (0.25 if bold else 0.2)))
    if just < 0:
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
    elif just > 0:
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)


def silk_line(a_, b_, w=0.15):
    l = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
    l.SetStart(V(*a_))
    l.SetEnd(V(*b_))
    l.SetLayer(pcbnew.F_SilkS)
    l.SetWidth(mm(w))
    board.Add(l)


def dot(x, y, r):
    d = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_CIRCLE)
    d.SetCenter(V(x, y))
    d.SetEnd(V(x + r, y))
    d.SetFilled(True)
    d.SetLayer(pcbnew.F_SilkS)
    d.SetWidth(mm(0.1))
    board.Add(d)


PIN_SZ = 1.3
TITLE_SZ = 1.6
# QT Py footprint (17.78 x 20.70, pin 1 2.73 below the USB edge), USB arrow.
qx0, qx1 = QX - 8.89, QX + 8.89
qy0 = LE[1][1] - 2.73
qy1 = qy0 + 20.70
# Only the USB-end edge: the sides would cross the socket pads and silk.
silk_line((qx0 + 4.0, qy0), (qx1 - 4.0, qy0), 0.12)
silk("USB", QX, qy0 - 1.3, 1.3, bold=True)
# Every QT Py pin named beside its outer (extra-row) pad: left names west of
# the west pads, right names east of the 3V3 lane.
LW_EDGE = LW[1][0] - SPW / 2
QLN = {1: "A0", 2: "A1", 3: "A2", 4: "A3", 5: "SDA", 6: "SCL", 7: "TX"}
QRN = {1: "5V", 2: "GND", 3: "3V3", 4: "MO", 5: "MI", 6: "SCK", 7: "RX"}
for k in range(1, 8):
    silk(QLN[k], LW_EDGE - 1.5, LW[k][1], PIN_SZ, just=-1, bold=True)
    silk(QRN[k], V3_X + 0.9, RE[k][1], PIN_SZ, just=1, bold=True)
silk("QT Py", QX, QY - 1.0, TITLE_SZ, bold=True)
silk("CH32V203", QX, QY + 1.2, 1.3, bold=True)

# U1: the QT Py itself, a pad-less footprint that only carries the 3D model,
# sitting on top of the sockets. The STEP origin is the QT Py's STEMMA-end
# corner with Y up; its A0 pin centre is at (1.27, 17.971) in that frame
# (models/QTPy_CH32V203_5996.md), which must land on the left socket's
# centreline at the pin-1 row.
QTPY_A0 = (1.27, 17.971)
u1 = pcbnew.FOOTPRINT(board)
u1.SetReference("U1")
u1.SetValue("QT Py CH32V203 (5996)")
u1.Reference().SetVisible(False)
u1.Value().SetVisible(False)
u1.SetPosition(V(XL - QTPY_A0[0], LE[1][1] + QTPY_A0[1]))
if os.path.isfile(MODEL_QTPY):
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/../models/QTPy_CH32V203_5996.stpZ"
    m.m_Offset = pcbnew.VECTOR3D(0, 0, QTPY_Z)
    u1.Add3DModel(m)
board.Add(u1)

# Box header hood outline (12.6 x 5.0 body, long axis east-west at rot 90) with
# the key slot on the pin-1 (odd, south) wall, and a pin-1 dot.
# The 752 footprint carries its own hood silk and pin-1 marker; add a large
# pin-1 dot west of the body for the 180-degree-rotation trap.
bx0, by0 = HX - 6.3, HY - 2.5
dot(bx0 - 0.9, J[1][1], 0.45)
silk("1", bx0 - 2.1, J[1][1], PIN_SZ, bold=True)
# SWD/SWIO, the date, DIO and RST positions were set by hand in the KiCad GUI
# on 11/26 (the fabbed boards); they are fixed numbers here to match.
silk("SWD", 6.0, 30.5, 1.5, bold=True)
silk("SWIO", 6.0, 32.5, 1.5, bold=True)
# Board name across the top, between the top mounting holes (replaces the USB arrow).
silk("WCH + ARM Programmer", W / 2, 2.7, 2.0, bold=True)
# Identifier, wrapped, in the open corner right of the 2x5 and below the QT Py.
silk("qtpy-dap", 32.4, HY - 6.6, 2.0, bold=True)
silk("breakout v2", 32.4, HY - 3.8, 2.0, bold=True)
# Date, above the SWD/SWIO marking.
silk("20261126", 6.0, 28.5, 1.5)
# Active header pins, read along each lane between the QT Py edge and the
# header: SWDIO pin 2, SWCLK pin 4 (lane over NC pad 6), RST pin 10.
PIN_LBL_Y = (qy1 + 0.25 + yj) / 2
for lx, txt in ((14.5, "DIO"), (A2_X, "CLK"), (23.0, "RST")):
    silk(txt, lx, PIN_LBL_Y, 1.5, bold=True, angle=90)

# ---- GND fill -----------------------------------------------------------------
# One F.Cu GND pour. 0.5 mm to foreign copper (xTool F1 Ultra laser isolation;
# the 752 pads already need 0.51 mm). Solid pad connection
# (no thermal spokes, milled-pcb-design rule). The 1.0 mm GND trunk stays, so
# ground never depends on the pour alone. Islands and <0.5 mm slivers dropped.
ZONE_CLEAR = 0.5
ZONE_MIN = 0.5
ZONE_INSET = 1.0     # pour edge back from the board edge
HOLE_KEEP = 1.0      # extra keepout around the M2 holes


def poly_outline(pts):
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in pts:
        chain.Append(mm(x), mm(y))
    chain.SetClosed(True)
    return chain


gnd = pcbnew.ZONE(board)
gnd.SetLayer(pcbnew.F_Cu)
gnd.SetNetCode(board.GetNetInfo().GetNetItem("GND").GetNetCode())
c = ZONE_INSET + 1.0     # corner chamfer follows the R2 board corners
i = ZONE_INSET
gnd.Outline().AddOutline(poly_outline([
    (c, i), (W - c, i), (W - i, c), (W - i, H - c),
    (W - c, H - i), (c, H - i), (i, H - c), (i, c)]))
gnd.SetLocalClearance(mm(ZONE_CLEAR))
gnd.SetMinThickness(mm(ZONE_MIN))
gnd.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
gnd.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
gnd.SetZoneName("GND")
board.Add(gnd)

for hx, hy in HOLES:
    ko = pcbnew.ZONE(board)
    ko.SetIsRuleArea(True)
    ko.SetDoNotAllowZoneFills(True)
    ko.SetDoNotAllowTracks(False)
    ko.SetDoNotAllowVias(False)
    ko.SetDoNotAllowPads(False)
    ko.SetDoNotAllowFootprints(False)
    ko.SetLayer(pcbnew.F_Cu)
    rk = HOLE_D / 2 + HOLE_KEEP
    ko.Outline().AddOutline(poly_outline(
        [(hx + rk * math.cos(math.radians(a)), hy + rk * math.sin(math.radians(a)))
         for a in range(0, 360, 15)]))
    board.Add(ko)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())

pcbnew.SaveBoard(PCB, board)

# Post-process: font face and local 3D models.
s = open(PCB).read()
s = s.replace("(font\n\t\t\t\t(size", '(font\n\t\t\t\t(face "Data 70")\n\t\t\t\t(size')
if os.path.isfile(MODEL_BOX):
    pass  # models stay ${KIPRJMOD}-relative so the project is portable
open(PCB, "w").write(s)

if os.path.isfile(PRO):
    pro = json.load(open(PRO))
else:
    pro = {"meta": {"filename": os.path.basename(PRO), "version": 3},
           "board": {"design_settings": {"rules": {}}},
           "net_settings": {"classes": [{"name": "Default"}]},
           "boards": [], "sheets": [], "text_variables": {}}
pro["meta"]["filename"] = os.path.basename(PRO)
rules = pro["board"]["design_settings"]["rules"]
rules["min_clearance"] = CLEARANCE
rules["min_track_width"] = MIN_TRACK
rules["min_copper_edge_clearance"] = EDGE_CLEAR
for cls in pro["net_settings"]["classes"]:
    if cls["name"] == "Default":
        cls["clearance"] = CLEARANCE
        cls["track_width"] = SIG_W
json.dump(pro, open(PRO, "w"), indent=2)


def check_corners(path):
    b = pcbnew.LoadBoard(path)
    segs = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        s0 = (pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y))
        s1 = (pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y))
        segs.append((t.GetNetname(), s0, s1, pcbnew.ToMM(t.GetWidth())))
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    nodes = {}
    for i, (n, a, c, w) in enumerate(segs):
        for end, other in ((a, c), (c, a)):
            nodes.setdefault((n, key(end)), []).append((other, end))
    bad = []
    for (n, k), items in nodes.items():
        if len(items) != 2:
            continue
        (o1, e1), (o2, e2) = items
        ux, uy = o1[0] - e1[0], o1[1] - e1[1]
        vx, vy = o2[0] - e2[0], o2[1] - e2[1]
        cosv = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy))
        ang = math.degrees(math.acos(max(-1.0, min(1.0, cosv))))
        if min(abs(ang - 135), abs(ang - 180)) > 0.5:
            bad.append((n, k, round(ang, 1)))
    print("segments:", len(segs))
    print("widths:", sorted({round(w, 2) for _, _, _, w in segs}))
    print("bends not 45 deg (should be empty):", bad)


check_corners(PCB)
print("LE", LE)
print("RE", RE)
print("J3", J)
