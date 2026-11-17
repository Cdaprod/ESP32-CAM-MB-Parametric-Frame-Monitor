// Parametric T-slot clamping / jacking rail; photo-derived cavity, NOT certified.
// Coordinate: local U inward from rail face; V across slot; Z along extrusion.
// Render with OpenSCAD; change view and fastening_mode below.
$fn=64;
view="assembly"; // assembly, key, section, interference, plate, holes
fastening_mode="clamp"; // clamp or jack (different hardware and hole requirements)
key_length=76.2;
rail_length=90;
hole_pitch=25.4;
end_margin=10;
fastener_d=5; // M5 nominal, for visual screw
pilot_d=4.2; // approximate M5 tapping drill, calibrate for material/process
clearance_hole_d=5.5;
slide_clearance=0.18;
slot_mouth=6.2;
slot_head_height=10.5;
slot_inner_flat=5;
slot_depth=6.8;
lip_depth=1.5;
head_flat_end=3.5;
tongue_recess=0.20; // positive inward from extrusion face
stem_protrusion=-tongue_recess; // compatibility with previous parameter naming
stem_overlap=0.6;
plate_thickness=3;
plate_width=15;
plate_length=key_length;
show_screws=true;
// Nominal geometric prototype; validate lip dimensions and printed fit before use.

assert(key_length>2*end_margin);
assert(slot_head_height>slot_mouth && slot_depth>head_flat_end && head_flat_end>lip_depth);
assert(fastening_mode=="clamp" || fastening_mode=="jack");
function hole_z_positions() = let(n=floor((key_length-2*end_margin)/hole_pitch)+1) [for(i=[0:n-1]) (i-(n-1)/2)*hole_pitch];
function cavity_vertices(overcut=2) = [
 [-overcut,-slot_mouth/2],[lip_depth,-slot_mouth/2],
 [lip_depth,-slot_head_height/2],[head_flat_end,-slot_head_height/2],
 [slot_depth,-slot_inner_flat/2],[slot_depth,slot_inner_flat/2],
 [head_flat_end,slot_head_height/2],[lip_depth,slot_head_height/2],
 [lip_depth,slot_mouth/2],[-overcut,slot_mouth/2]
];
module cavity_2d(overcut=2) polygon(cavity_vertices(overcut));
module head_2d() offset(delta=-slide_clearance) intersection(){
 cavity_2d(0); translate([0,-20]) square([slot_depth,40]);
}
module key_section_2d() union(){
 head_2d();
 translate([tongue_recess,-(slot_mouth-2*slide_clearance)/2])
 square([lip_depth+stem_overlap-tongue_recess,slot_mouth-2*slide_clearance]);
}
module key_blank() linear_extrude(height=key_length,center=true) key_section_2d();
// Transverse X-axis holes, drilled from the outer side into the head.
// For 'clamp' use tapped key holes; for 'jack' use tapped-through holes.
module transverse_holes(d=pilot_d) for(z=hole_z_positions())
 translate([-0.5,0,z]) rotate([0,90,0]) cylinder(d=d,h=slot_depth+1);
module key() difference(){key_blank(); transverse_holes();}
// Reference female fixture: wall and lips only, open at U<0.
// This is NOT a manufacturer-verified full 4040 profile.
module fixture_section_2d(){
 difference(){translate([-0.001,-9]) square([slot_depth+3.5,18]); cavity_2d(2);}
}
module fixture() linear_extrude(height=rail_length,center=true) fixture_section_2d();
// Plate on exterior face (local U<0). The plate has clearance bores.
module plate(){difference(){
 translate([-plate_thickness,-plate_width/2,-plate_length/2])
 cube([plate_thickness,plate_width,plate_length]);
 for(z=hole_z_positions())
 translate([-plate_thickness-0.5,0,z]) rotate([0,90,0]) cylinder(d=clearance_hole_d,h=plate_thickness+1);
}}
// Screw visuals only. Real screws need specified length, threads and tip.
module screw_at(z){
 color([0.25,0.29,0.34]){
 // M5 shaft entering from outside. Jack mode extends toward cavity rear wall.
 u0=fastening_mode=="clamp" ? -plate_thickness-1 : -0.5;
 shaft_len=fastening_mode=="clamp" ? plate_thickness+4.5 : slot_depth+0.2;
 translate([u0,0,z]) rotate([0,90,0]) cylinder(d=fastener_d,h=shaft_len);
 // Head outside (clamp), small socket-head visual (jack)
 translate([u0-1.2,0,z]) rotate([0,90,0]) cylinder(d=fastening_mode=="clamp"?8:5.8,h=1.2);
 }}
module screws() for(z=hole_z_positions()) screw_at(z);
if(view=="assembly"){
 color([0.65,0.70,0.76,0.38]) fixture();
 color([1,0.49,0.06]) key();
 if(fastening_mode=="clamp") color([0.84,0.20,0.17]) plate();
 if(show_screws) screws();
}else if(view=="key") color([1,0.49,0.06]) key();
else if(view=="section"){
 color([0.67,0.72,0.77]) fixture_section_2d();
 color([1,0.49,0.06]) key_section_2d();
}
else if(view=="interference") intersection(){fixture();key();}
else if(view=="plate") plate();
else if(view=="holes") key();
else assert(false,"Unknown view");
