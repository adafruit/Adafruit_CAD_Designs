// SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
//
// SPDX-License-Identifier: MIT

// L-shaped stand legs for the Raspberry Pi Touch Display 2 (5")
// -------------------------------------------------------------
// Two legs, each screwed (M2.5) into ONE of the two bottom corner mounting
// bosses on the back of the display in landscape. Each leg is an "L": an
// upright that lies flat against the back of the panel with a pocket that fits
// over the boss and the screw hole on its centre line, and a foot that runs
// back along the desk.
//
// On the 5" display the corner bosses at the two ends are rotated 90 degrees
// from each other. In landscape, one bottom boss is TALL (long axis vertical)
// and the other is WIDE (long axis horizontal), so the two legs get different
// pockets:
//     tall_leg  -> fits the boss nearest the DSI ribbon connector
//     wide_leg  -> fits the boss at the other end
//
// Dimensions are from the Touch Display 2 product brief (Aug 2025), page 3.
// Values marked (est.) were scaled off the drawing, or taken from
// geerlingguy's printables #1062445 stand (made for the 7" panel). Print
// part="fit_test" first to check the pocket fit.
//
// World coordinates:  X = along the display's long edge, Y = towards the back,
//                     Z = up, desk at Z = 0. The display's bottom front edge is at Y = 0.
// Display-local:      u = distance up the panel from its bottom edge,
//                     v = distance back from the front of the glass.

/* [What to render] */
part = "print_pair"; // [assembly, tall_leg, wide_leg, print_pair, fit_test]

/* [Stand] */
tilt      = 27;   // lean-back angle from vertical (degrees)
lift      = 0;    // height of the display's bottom edge above the desk (0 = resting on the desk)
foot_len  = 70;   // foot reaches this far behind the front of the screen
foot_t    = 5;    // foot thickness
upright_t = 8;    // upright thickness (max ~8 so it stays under a Pi on 8.5 mm standoffs)
u_top     = 31;   // top of the upright, measured up the panel. Keep it below ~33 so
                  // it stays clear of the DSI ribbon and the raised centre strip.
fillet_r  = 7;    // inside fillet of the L
round_r   = 1.5;  // outside edge rounding (side profile)
w_tall    = 20;   // width of the tall-boss leg (wider would hit the Pi standoff)
w_wide    = 23;   // width of the wide-boss leg

/* [Display (datasheet)] */
hole_u    = 91.46 - 9.25 - 10.98 - 51; // = 20.23: hole height above bottom edge
hole_x    = 143.4/2 - 19.85;           // = 51.85: hole offset from display centre
plate_v   = 15.9 - 8.5;                // = 7.4: back plate, measured back from the glass
rest_v    = 1.0;  // (est.) when lift = 0, where the bottom edge touches the desk

/* [Boss pocket] */
boss_h        = 3.0;  // boss height above the plate
pocket_d      = 3.0;  // pocket depth (= boss height -> face sits on the plate)
pocket_len    = 17.6; // (est.) long side at the mouth
pocket_len_b  = 16.4; // (est.) long side at the bottom (the boss ends are sloped)
pocket_wid    = 8.6;  // (est.) short side
pocket_ch     = 0.6;  // lead-in chamfer at the mouth
floor_t       = 2.0;  // material under the screw head (same as the reference stand)
screw_d       = 2.9;  // M2.5 clearance
head_d        = 5.6;  // counterbore for the screw head

/* [Raised-strip relief (wide-boss leg)] */
relief_u  = 27.8; // (est.) above this the plate has a raised strip near the wide boss
relief_d  = 2.5;

$fn = 48;

// ---------------------------------------------------------------- helpers
function P(u, v) = [ u*sin(tilt) + (v - rest_v)*cos(tilt),
                     lift + u*cos(tilt) - (v - rest_v)*sin(tilt) ];

// place display-local geometry (built as X=x, Y=v, Z=u) into the world
module display_frame() {
    translate([0, 0, lift]) rotate([-tilt, 0, 0]) translate([0, -rest_v, 0]) children();
}

// extrude a 2D (Y,Z) side profile along X, centred, total width w
module profile_extrude(w) {
    multmatrix([[0,0,1,-w/2],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
        linear_extrude(w) children();
}

// --------------------------------------------------------------- the leg
module side_profile() {
    vb = plate_v + upright_t;
    // where the upright's front face meets the desk
    u_f = ((plate_v - rest_v)*sin(tilt) - lift) / cos(tilt);
    yf  = P(u_f, plate_v)[0];
    offset(r = round_r) offset(delta = -round_r)        // round the outside corners
    offset(r = -fillet_r) offset(delta = fillet_r)      // fillet the inside of the L
    intersection() {
        union() {
            polygon([P(-80, plate_v), P(u_top, plate_v), P(u_top, vb), P(-80, vb)]);
            translate([yf, 0]) square([foot_len - yf, foot_t]);
        }
        translate([-50, 0]) square([300, 200]);         // nothing below the desk
    }
}

// pocket shape in display-local coords, long axis along u (tall) or x (wide)
module pocket(tall) {
    module slab(l, w, v) {
        sz = tall ? [w, 0.01, l] : [l, 0.01, w];
        translate([0, v, hole_u]) cube(sz, center = true);
    }
    hull() { slab(pocket_len + 2*pocket_ch, pocket_wid + 2*pocket_ch, plate_v - 0.01);
             slab(pocket_len, pocket_wid, plate_v + pocket_ch); }
    hull() { slab(pocket_len, pocket_wid, plate_v + pocket_ch);
             slab(pocket_len_b, pocket_wid, plate_v + pocket_d); }
}

module screw_holes() {
    // clearance hole through the floor
    translate([0, plate_v - 1, hole_u]) rotate([-90, 0, 0]) cylinder(d = screw_d, h = 30);
    // counterbore for the head, from the back
    translate([0, plate_v + pocket_d + floor_t, hole_u]) rotate([-90, 0, 0])
        cylinder(d = head_d, h = 30);
}

module leg(tall) {
    w = tall ? w_tall : w_wide;
    difference() {
        profile_extrude(w) side_profile();
        display_frame() {
            pocket(tall);
            screw_holes();
            if (!tall)   // clear the raised centre strip above the wide boss
                translate([-w, plate_v - 1, relief_u]) cube([2*w, relief_d + 1, 50]);
        }
    }
}

// small coupon to check the pocket fits over a boss and the screw reaches
module fit_test() {
    t = pocket_d + floor_t;
    difference() {
        translate([-13, -7.5, 0]) cube([26, 15, t]);
        // pocket opening upwards, so it prints without bridges
        // local (x, v, u) -> coupon (x, u - hole_u, t - (v - plate_v))
        multmatrix([[1,0,0,0],[0,0,1,-hole_u],[0,-1,0,t + plate_v],[0,0,0,1]]) pocket(false);
        translate([0, 0, -1]) cylinder(d = screw_d, h = t + 2);
    }
}

// ----------------------------------------------- display stand-in (5")
// Landscape, seen from the front: left end = portrait-bottom end (tall bosses,
// DSI connector), right end = portrait-top end (wide bosses, raised strip).
module display_dummy() {
    W = 143.4; H = 91.46;
    function X(yp) = yp - W/2;     // portrait y -> landscape X
    function U(xp) = H - xp;       // portrait x -> landscape u
    display_frame() {
        color("black", 0.9) translate([-W/2, 0, 0]) cube([W, 0.7, H]);
        color("silver") translate([X(12.8), 0.7, U(82.21)]) cube([122.74, plate_v - 0.7, 72.96]);
        // corner bosses: portrait-bottom end tall in landscape, top end wide
        for (yp = [19.85, 123.55], xp = [20.23, 71.23]) {
            tall = yp < 50;
            color("dimgray") translate([X(yp), plate_v + boss_h/2, U(xp)])
                cube(tall ? [8.6, boss_h, 17.1] : [17.1, boss_h, 8.6], center = true);
        }
        // raised centre strip (est.)
        color("gray") translate([X(36), plate_v, U(62.9)]) cube([133 - 36, 2, 62.9 - 29.4]);
        // DSI connector and ribbon (est.)
        color("ivory") translate([X(29), plate_v, U(58)]) cube([13, 2.5, 24]);
        color("orange", 0.8) translate([X(5), plate_v + 2.5, U(57)]) cube([25, 0.3, 22]);
        // Pi standoffs (58 x 49 pattern, 8.5 tall)
        for (yp = [33.91, 91.91], xp = [21.23, 70.23])
            color("gold") translate([X(yp), plate_v, U(xp)]) rotate([-90, 0, 0])
                cylinder(d = 5, h = 8.5, $fn = 6);
    }
}

// ----------------------------------------------------------------- output
if (part == "assembly") {
    display_dummy();
    color("tomato") translate([-hole_x, 0, 0]) leg(true);
    color("tomato") translate([ hole_x, 0, 0]) leg(false);
    color("burlywood", 0.4) translate([-90, -20, -2]) cube([180, 110, 2]);   // desk
} else if (part == "tall_leg") {
    leg(true);
} else if (part == "wide_leg") {
    leg(false);
} else if (part == "print_pair") {
    // both legs lying on their sides, ready to slice
    translate([0, 0, w_tall/2])  rotate([0, -90, 0]) leg(true);
    translate([8, 0, w_wide/2])  rotate([0,  90, 0]) leg(false);
} else if (part == "fit_test") {
    fit_test();
}
