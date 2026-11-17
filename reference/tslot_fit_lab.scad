// /cad/tslot/tslot_fit_lab.scad
// PARAMETRIC TEST COUPON — NOT A VERIFIED 4040 MANUFACTURER PROFILE.
// Axes: X = inward from extrusion outer face; Y = across slot; Z = rail length.
// Mouth at X=0, cavity extends toward positive X.
$fn=48;
view="assembly"; // "assembly", "interference", "key", "section"
length=16;
cavity_height=10.5;
slot_opening=6.2;
cavity_depth=6.8;
lip_depth=1.5;
chamfer_run=1.5;
clearance=0.15; // radial 2D offset for key
// The polygon below is an illustrative six-sided cavity approximation.
// Confirm exact cavity boundaries from a manufacturer STEP/DXF before use.
module cavity_2d() {
    polygon([
      [0,-slot_opening/2],
      [lip_depth,-slot_opening/2],
      [lip_depth+chamfer_run,-cavity_height/2],
      [cavity_depth,-cavity_height/2],
      [cavity_depth,cavity_height/2],
      [lip_depth+chamfer_run,cavity_height/2],
      [lip_depth,slot_opening/2],
      [0,slot_opening/2]
    ]);
}
// Open-mouth neck is intentionally narrower than head; shape slides from rail end.
module key_2d() {
    offset(delta=-clearance) cavity_2d();
}
module cavity_3d(){linear_extrude(height=length,center=true) cavity_2d();}
module key_3d(){linear_extrude(height=length,center=true) key_2d();}
// A reference solid around cavity, open at x=0 (not a full 4040 profile).
module reference_wall_3d(){
  linear_extrude(height=length,center=true)
  difference(){
    translate([cavity_depth/2,0]) square([cavity_depth+4,cavity_height+5],center=true);
    cavity_2d();
    // Open access from the left edge through the mouth
    translate([-2,0]) square([4.01,slot_opening],center=true);
  }
}
assert(cavity_depth>lip_depth+chamfer_run,"Cavity depth must exceed lip + chamfer run");
assert(cavity_height>slot_opening,"Cavity height must exceed mouth height");
assert(clearance>=0 && clearance<slot_opening/4,"Check clearance");
if(view=="assembly"){
 color("silver",0.38) reference_wall_3d();
 color("orange") key_3d();
} else if(view=="interference"){
 color("red") intersection(){reference_wall_3d();key_3d();}
} else if(view=="key"){
 color("orange") key_3d();
} else if(view=="section"){
 color("silver",0.45) projection(cut=false) reference_wall_3d();
 color("orange") key_2d();
}
