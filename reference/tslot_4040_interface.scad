// /cad/tslot/tslot_4040_interface.scad
// V3: right-hand outside-facing 4040 dual-slot reference + retained sliding key.
// Geometry is PARAMETRIC and PHOTO-DERIVED; NOT manufacturer-certified.
// File is self-contained. No BOSL2 or external library dependencies.
//
// Coordinate system: extrusion section XY, rail travel Z.
// RIGHT face lies at X=+20. Right-upper slot is centered at Y=+10.
// Local slot coordinate U is INWARD from that face (global X = 20-U).
// Local V is perpendicular to U, across the slot (global Y = 10-V).
// There are TWO 20-mm-pitch slots per face of the 40x40 body.
$fn = 96;

view = "assembly"; // assembly, section, exploded, key, rail, interference, void, key_section, rail_section

profile_size = 40;
slot_pitch = 20;
rail_length = 34;
key_length = 18;

// All dimensions in millimeters. PHOTO-DERIVED, not officially verified.
slot_mouth = 6.20;      // exterior throat, V opening
slot_head_height = 10.50;// widest region behind retaining lip
slot_inner_flat = 5.00; // rear vertical flat at deepest slot wall
slot_depth = 6.80;      // inward reach from exterior face
lip_depth = 1.50;       // U-depth of narrow mouth before step into undercut
head_flat_end = 3.50;   // U coordinate at start of rear chamfer

// Independent interface parameters:
slide_clearance = 0.18; // offset PER SURFACE on the male head
stem_protrusion = 4;    // outboard mounting tongue extends beyond face
stem_extra_overlap = 0.60;

// Reference-fixture-only dimensions (NOT verified production extrusion values):
core_hole_diameter = 4.5;
// Central void topology approximated from the photo (not verified to print).

assert(profile_size == 40 && slot_pitch==20,
       "This layout is specifically a 40x40 dual-20-mm-pitch section");
assert(slot_mouth > 0 && slot_head_height > slot_mouth);
assert(slot_inner_flat > 0 && slot_inner_flat < slot_head_height);
assert(slot_depth > head_flat_end && head_flat_end > lip_depth && lip_depth > 0);
assert(slide_clearance >= 0 && slide_clearance < min(lip_depth/2,slot_mouth/4));
assert(key_length < rail_length);

// The void has a REAL mechanical undercut: narrow opening from U=0 to
// U=lip_depth, wider chamber immediately behind lips, then CHAMFERED BACK WALL.
// Extend void 2 mm outside the metal so it cuts a continuous side opening.
function slot_void_vertices(overcut=2) = [
    [-overcut, -slot_mouth/2],
    [lip_depth, -slot_mouth/2],
    [lip_depth, -slot_head_height/2],
    [head_flat_end, -slot_head_height/2],
    [slot_depth, -slot_inner_flat/2],
    [slot_depth,  slot_inner_flat/2],
    [head_flat_end,  slot_head_height/2],
    [lip_depth,  slot_head_height/2],
    [lip_depth,  slot_mouth/2],
    [-overcut, slot_mouth/2]
];

module slot_void_local_2d(overcut=2) {
    polygon(slot_void_vertices(overcut));
}

module cavity_inside_local_2d() {
    intersection() {
        slot_void_local_2d(overcut=0);
        translate([0, -slot_head_height])
            square([slot_depth, 2*slot_head_height]);
    }
}

// Orientation intentionally explicit. Each slot opens OUTWARD on a side face.
module at_slot(face="right", position=10) {
    if(face == "right")
        translate([ profile_size/2, position]) rotate(180) children();
    else if(face == "left")
        translate([-profile_size/2, position]) children();
    else if(face == "top")
        translate([position, profile_size/2]) rotate(-90) children();
    else if(face == "bottom")
        translate([position, -profile_size/2]) rotate(90) children();
    else assert(false, "Invalid face");
}

// Full 40x40 reference section: 8 T-slots + 4 bores + central space.
// Only the SLOT CAVITY is parameterized from the photographed measurements;
// core holes / central diamond are deliberately reference-fixture approximations.
// Photo-inspired CENTRAL void. The thin closed exterior walls, broad cross,
// and four bores mimic the supplied photograph, but are NOT tolerance data.
module core_cross_void_2d() {
    polygon([
      [-3,18],[3,18],[3,15],[6,12],[6,8],
      [8,6],[12,6],[15,3],[18,3],
      [18,-3],[15,-3],[12,-6],[8,-6],[6,-8],[6,-12],
      [3,-15],[3,-18],[-3,-18],[-3,-15],[-6,-12],
      [-6,-8],[-8,-6],[-12,-6],[-15,-3],[-18,-3],
      [-18,3],[-15,3],[-12,6],[-8,6],[-6,8],[-6,12],[-3,15]
    ]);
}

module extrusion_4040_section_2d() {
    difference() {
        square([profile_size, profile_size], center=true);
        for (face=["right", "left", "top", "bottom"])
            for (position=[-slot_pitch/2,slot_pitch/2])
                at_slot(face,position) slot_void_local_2d();
        for(x=[-10,10]) for(y=[-10,10])
            translate([x,y]) circle(d=core_hole_diameter);
        core_cross_void_2d();
    }
}

// Male key head follows the *same* female cavity, with radial 2D clearance.
// The external stem remains narrower than the mouth and can join a bracket.
module sliding_key_local_2d() {
    union() {
        offset(delta=-slide_clearance) cavity_inside_local_2d();
        translate([-stem_protrusion, -(slot_mouth-2*slide_clearance)/2])
            square([stem_protrusion+lip_depth+stem_extra_overlap,
                    slot_mouth-2*slide_clearance]);
    }
}

module reference_rail_3d() {
    linear_extrude(height=rail_length, center=true, convexity=10)
        extrusion_4040_section_2d();
}
module fitted_key_3d() {
    linear_extrude(height=key_length, center=true, convexity=10)
        at_slot("right",10) sliding_key_local_2d();
}

// A tool-free 2D section is best for examining lip capture and the clearance.
// Use F5 preview for gray metal + orange key, and F6 to validate meshes.
if (view == "assembly") {
    color([0.66,0.72,0.78,0.25]) reference_rail_3d();
    color([1.00,0.45,0.03]) fitted_key_3d();
} else if (view == "section") {
    color([0.62,0.68,0.75]) extrusion_4040_section_2d();
    color([1.00,0.45,0.03]) at_slot("right",10) sliding_key_local_2d();
} else if (view == "exploded") {
    color([0.66,0.72,0.78,0.45]) reference_rail_3d();
    color([1.00,0.45,0.03]) translate([10,0,0]) fitted_key_3d();
} else if (view == "key") {
    color([1,0.45,0.03]) fitted_key_3d();
} else if (view == "rail") {
    reference_rail_3d();
} else if (view == "interference") {
    intersection() {
        reference_rail_3d();
        fitted_key_3d();
    }
} else if (view == "void") {
    at_slot("right",10) slot_void_local_2d(overcut=0);
} else if (view == "key_section") {
    at_slot("right",10) sliding_key_local_2d();
} else if (view == "rail_section") {
    extrusion_4040_section_2d();
} else assert(false, "Unknown view");
