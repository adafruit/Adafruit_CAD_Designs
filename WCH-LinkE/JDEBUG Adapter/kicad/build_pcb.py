# SPDX-FileCopyrightText: 2026 Mikey Sklar
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Builds wch-linke-adapter.kicad_pcb from scratch (idempotent).
# Single-sided milled adapter: WCH-LinkE probe (male 2.54 mm pins) plugs into
# a female SMD socket J1; a 2x5 1.27 mm male SMD header J2 takes a ribbon to
# the Metro CH32V4x7 JDEBUG (ARM Cortex 10-pin). Three signals: SWDIO, GND, RST.
#
# Milled-board rules (milled-pcb-design skill): F.Cu only, no pour, no vias,
# 45 deg miters on every bend, signal width 0.74 (J2 pad short side).
#
# Run with KiCad's bundled python (set KICAD_FPLIB off macOS):
#   /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 build_pcb.py

import json
import math
import os

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "wch-linke-adapter"
PCB = os.path.join(HERE, NAME + ".kicad_pcb")
PRO = os.path.join(HERE, NAME + ".kicad_pro")
FPLIB = os.environ.get("KICAD_FPLIB", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
MODEL_J1 = os.path.join(HERE, "PinSocket_2x05_P2.54mm_H3.5_SMD.step")

# WCH-LinkE pinout, verified from WCH's manual photo (R0-1v3). J1 pad number
# -> probe signal. This dict is the ONLY place to change if the probe differs.
PROBE = {1: "SWCLK", 3: "SWDIO", 5: "GND", 7: "3V3", 9: "5V",
         2: "RX", 4: "TX", 6: "TDO", 8: "TDI", 10: "RST"}

# ---- board dimensions first ---------------------------------------------------
X0, Y0 = 0.0, 0.0
W, H, R = 40.0, 30.0, 2.0
HOLE_D = 2.7
HOLES = [(4.0, 4.0), (4.0, 26.0), (36.0, 4.0), (36.0, 26.0)]

# ---- design rules -------------------------------------------------------------
CLEARANCE = 0.4
MIN_TRACK = 0.4
EDGE_CLEAR = 0.5
SIG_W = 0.74   # = PinHeader_2x05_P1.27mm SMD pad short side
GND_W = 1.0    # GND trunk / stitch

# ---- placement ----------------------------------------------------------------
J1_POS, J1_ROT = (10.0, 15.0), 0.0
J2_POS, J2_ROT = (30.0, 15.0), 0.0

board = pcbnew.CreateEmptyBoard()
mm = pcbnew.FromMM


def V(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


# ---- design settings ----------------------------------------------------------
ds = board.GetDesignSettings()
ds.m_MinClearance = mm(CLEARANCE)
ds.m_TrackMinWidth = mm(MIN_TRACK)
ds.m_CopperEdgeClearance = mm(EDGE_CLEAR)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetClearance(mm(CLEARANCE))
nc.SetTrackWidth(mm(SIG_W))
board.SetCopperLayerCount(2)   # B.Cu stays empty

# ---- nets ---------------------------------------------------------------------
NETS = {}


def net(name):
    if name not in NETS:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        NETS[name] = n
    return NETS[name]


for n in ("SWDIO", "GND", "RST"):
    net(n)


# ---- footprints ---------------------------------------------------------------
def load_fp(lib, name, ref, value, pos, rot):
    fp = pcbnew.FootprintLoad(os.path.join(FPLIB, lib + ".pretty"), name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(V(*pos))
    fp.SetOrientationDegrees(rot)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)
    return fp


j1 = load_fp("Connector_PinSocket_2.54mm", "PinSocket_2x05_P2.54mm_Vertical_SMD",
             "J1", "WCH-LinkE", J1_POS, J1_ROT)
j2 = load_fp("Connector_PinHeader_1.27mm", "PinHeader_2x05_P1.27mm_Vertical_SMD",
             "J2", "JDEBUG", J2_POS, J2_ROT)

# 3D model: J1 uses the local STEP when it exists (re-checked every run),
# otherwise the library default stays. J2 keeps the library default.
LIB_MODEL_J1 = "${KICAD10_3DMODEL_DIR}/Connector_PinSocket_2.54mm.3dshapes/PinSocket_2x05_P2.54mm_Vertical_SMD.step"
print("J1 3D model:", "local STEP" if os.path.isfile(MODEL_J1) else "library default (no local STEP yet)")


def pad_pos(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == str(num):
            q = p.GetPosition()
            return (pcbnew.ToMM(q.x), pcbnew.ToMM(q.y))
    raise KeyError(num)


# Pads are looked up, then checked against the spec frame.
P1 = {k: pad_pos(j1, k) for k in range(1, 11)}
P2 = {k: pad_pos(j2, k) for k in range(1, 11)}
assert abs(P1[1][0] - 12.52) < 0.01 and abs(P1[1][1] - 9.92) < 0.01, P1[1]
assert abs(P1[2][0] - 7.48) < 0.01, P1[2]
assert abs(P2[1][0] - 28.05) < 0.01 and abs(P2[2][0] - 31.95) < 0.01, P2

# Nets: J1 pad 3 SWDIO, pad 5 GND, pad 10 RST (per PROBE). J2: 2 SWDIO,
# 3/5/9 GND, 10 RST.
J1NET = {3: "SWDIO", 5: "GND", 10: "RST"}
J2NET = {2: "SWDIO", 3: "GND", 5: "GND", 9: "GND", 10: "RST"}
for fp, table in ((j1, J1NET), (j2, J2NET)):
    for p in fp.Pads():
        num = p.GetNumber()
        if num.isdigit() and int(num) in table:
            p.SetNet(net(table[int(num)]))

# Sanity: the PROBE names used for the GND/SWDIO/RST nets match the table.
assert PROBE[3] == "SWDIO" and PROBE[5] == "GND" and PROBE[10] == "RST"


# ---- tracks -------------------------------------------------------------------
def add_track(a, b, netname, w):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(V(*a))
    t.SetEnd(V(*b))
    t.SetWidth(mm(w))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net(netname))
    board.Add(t)


def add_path(points, netname, w):
    for a, b in zip(points, points[1:]):
        add_track(a, b, netname, w)


# SWDIO: from J1 pad 3, east, 45 up, east along the top, 45 down-right,
# south at x 34.6 (outside the J2 hood outline), 45 down-left into J2 pad 2.
add_path([
    (13.0, 12.46),
    (21.0, 12.46),
    (23.86, 9.60),
    (33.6, 9.60),
    (34.6, 10.60),
    (34.6, 11.46),
    (33.6, 12.46),
    (33.0, 12.46),
], "SWDIO", SIG_W)

# RST: straight down out of J1 pad 10 (parts side), 45 down-right, east under
# the socket at y 22.6, 45 up-right, north at x 34.6, 45 up-left into J2 pad 10.
add_path([
    (7.48, 20.08),
    (7.48, 21.60),
    (8.48, 22.60),
    (33.6, 22.60),
    (34.6, 21.60),
    (34.6, 18.54),
    (33.6, 17.54),
    (33.0, 17.54),
], "RST", SIG_W)

# GND (v2): all forks sit 3+ mm west of J2 so nothing branches beside a pad.
# Trunk 1.0 from J1 pad 5 east along y 15.0.
add_path([(13.0, 15.00), (19.0, 15.00), (23.4, 15.00)], "GND", GND_W)
# Pads 3 + 5 share one GND copper block (polygon, flat ends, 45 deg taper off
# the trunk). Its top/bottom edges sit 0.535 from pads 1 and 7, the same as
# J2's own inter-pad gap, and its east edge is flush with the pad ends (x 29.25)
# so it fills the 3-5 gap: no same-net sliver for the mill to isolate.
blk = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_POLY)
blk.SetPolyPoints([V(22.8, 14.5), V(23.935, 13.365), V(29.25, 13.365),
                   V(29.25, 15.365), V(22.8, 15.365)])
blk.SetFilled(True)
blk.SetWidth(0)
blk.SetLayer(pcbnew.F_Cu)
blk.SetNet(net("GND"))
board.Add(blk)
# Pad 9 is fed from below so no copper runs past NC pad 7: 45 off the trunk
# at x 19, east at y 19.0, 45 up-right, north into pad 9's bottom edge.
add_path([(19.0, 15.00), (23.0, 19.00), (26.5, 19.00), (27.5, 18.00),
          (27.5, 17.54)], "GND", SIG_W)


# ---- outline: 4 lines + 4 arcs, mounting holes ---------------------------------
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


x1, y1, x2, y2 = X0, Y0, X0 + W, Y0 + H
edge_line((x1 + R, y1), (x2 - R, y1))
edge_line((x2, y1 + R), (x2, y2 - R))
edge_line((x2 - R, y2), (x1 + R, y2))
edge_line((x1, y2 - R), (x1, y1 + R))
edge_arc((x2 - R, y1 + R), (x2 - R, y1), (x2, y1 + R))
edge_arc((x2 - R, y2 - R), (x2, y2 - R), (x2 - R, y2))
edge_arc((x1 + R, y2 - R), (x1 + R, y2), (x1, y2 - R))
edge_arc((x1 + R, y1 + R), (x1, y1 + R), (x1 + R, y1))
for hx, hy in HOLES:
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_CIRCLE)
    s.SetCenter(V(hx, hy))
    s.SetEnd(V(hx + HOLE_D / 2, hy))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.05))
    board.Add(s)


# ---- silkscreen ---------------------------------------------------------------
def silk(text, x, y, size=0.8, just=0, bold=False):
    # just: -1 right, 0 centre, +1 left
    t = pcbnew.PCB_TEXT(board)
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


def dot(x, y, r):
    d = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_CIRCLE)
    d.SetCenter(V(x, y))
    d.SetEnd(V(x + r, y))
    d.SetFilled(True)
    d.SetLayer(pcbnew.F_SilkS)
    d.SetWidth(mm(0.1))
    board.Add(d)


def box(x0, y0, x1, y1, w=0.15):
    for a_, b_ in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                   ((x1, y1), (x0, y1))):
        silk_line(a_, b_, w)


def silk_line(a_, b_, w=0.15):
    l = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
    l.SetStart(V(*a_))
    l.SetEnd(V(*b_))
    l.SetLayer(pcbnew.F_SilkS)
    l.SetWidth(mm(w))
    board.Add(l)


PIN_SZ = 1.1     # per-pin labels
TITLE_SZ = 1.8   # part descriptions

# J1 labels, each centred on its pad y, ~1 mm clear of the pad ends (odd pads
# end at x 14.02, even at 5.98). SWDIO and GND have tracks running east at
# their pad y, so those two sit just above their track.
silk("SWCLK", 15.0, 9.55, PIN_SZ, just=1)
silk("SWDIO", 15.0, 11.30, PIN_SZ, just=1)   # above SWDIO track (top 12.09)
silk("GND", 15.0, 13.66, PIN_SZ, just=1)     # between SWDIO (12.83) and GND (14.50)
silk("3V3", 15.0, P1[7][1], PIN_SZ, just=1)
silk("5V", 15.0, P1[9][1], PIN_SZ, just=1)
for num in (2, 4, 6, 8, 10):
    silk(PROBE[num], 5.0, P1[num][1], PIN_SZ, just=-1, bold=True)
# Probe faces and pin-1 end
silk("PARTS", 7.0, 7.7, 1.0)
silk("QR", 13.0, 7.7, 1.0)
dot(10.0, 7.7, 0.45)
silk("WCH-LinkE", 13.0, 4.2, TITLE_SZ, bold=True)

# J2: hooded 2x5 1.27 mm shroud outline with the key slot on the pin-1 (odd)
# side. Drawn as an orientation aid, not to a datasheet.
HX0, HX1, HY0, HY1 = 26.3, 33.7, 10.8, 19.2
box(HX0, HY0, HX1, HY1)                       # top, right, bottom
silk_line((HX0, HY0), (HX0, 14.0))            # left side, split by the key slot
silk_line((HX0, 16.0), (HX0, HY1))
silk_line((HX0, 14.0), (HX0 - 0.6, 14.0))     # slot drawn as an outward step
silk_line((HX0 - 0.6, 14.0), (HX0 - 0.6, 16.0))
silk_line((HX0 - 0.6, 16.0), (HX0, 16.0))
dot(25.3, 11.4, 0.45)                         # pin-1 marker beside J2 pad 1
silk("JDEBUG", 29.0, 4.2, TITLE_SZ, bold=True)
silk("SWDIO", 29.0, 8.2, PIN_SZ, just=0)      # above the SWDIO top run
silk("RST", 29.0, 21.2, PIN_SZ, just=0)       # above the RST bottom run
silk("GND", 23.6, 17.2, PIN_SZ, just=0)       # between the pad-9 feed and the 3+5 feed

silk("wch-linke-adapter v2", 20.0, 25.0, 1.2)
silk("20261124", 20.0, 27.3, 1.2)

pcbnew.SaveBoard(PCB, board)

# Font: Data 70 on all text (pcbnew API cannot set faces), as in the template.
s = open(PCB).read()
s = s.replace("(font\n\t\t\t\t(size", '(font\n\t\t\t\t(face "Data 70")\n\t\t\t\t(size')
if os.path.isfile(MODEL_J1):
    assert LIB_MODEL_J1 in s, "library J1 model path not found in board"
    s = s.replace(LIB_MODEL_J1, "${KIPRJMOD}/PinSocket_2x05_P2.54mm_H3.5_SMD.step")
open(PCB, "w").write(s)

# Rules live in the .kicad_pro. Create a minimal one if absent, then patch.
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


# ---- corner check: every bend must be a 45 deg turn ----------------------------
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
            nodes.setdefault((n, key(end)), []).append((i, other, end))
    bad, junc = [], []
    for (n, k), items in nodes.items():
        if len(items) < 2:
            continue
        vecs = []
        for i, other, end in items:
            vx, vy = other[0] - end[0], other[1] - end[1]
            vecs.append((vx, vy))
        angs = []
        for i in range(len(vecs)):
            for j in range(i + 1, len(vecs)):
                ux, uy = vecs[i]
                vx, vy = vecs[j]
                cosv = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy))
                angs.append(math.degrees(math.acos(max(-1.0, min(1.0, cosv)))))
        if len(items) == 2:
            interior = angs[0]
            if min(abs(interior - 135), abs(interior - 180)) > 0.5:
                bad.append((n, k, round(interior, 1)))
        else:
            junc.append((n, k, len(items), [round(a, 1) for a in angs]))
    print("segments:", len(segs))
    print("widths:", sorted({round(w, 2) for _, _, _, w in segs}))
    print("bends not 45 deg (should be empty):", bad)
    print("junctions (3+ way, spec-mandated tees/forks):")
    for j in junc:
        print("   ", j)


check_corners(PCB)

print("J1", {k: P1[k] for k in P1})
print("J2", {k: P2[k] for k in P2})
