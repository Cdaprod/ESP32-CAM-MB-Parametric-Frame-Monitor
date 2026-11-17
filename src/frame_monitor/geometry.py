"""New arm geometry; guide bore centers derive from the cable route config."""
from . import parts as old
from .primitives import block, cyl_x, cyl_z, cyl_y
from .config import CONFIG


def cable_guide(arm, *, y:float, z:float, core_top:float):
    x=CONFIG.cable_outboard_x_mm
    radius=CONFIG.guide_bore_diameter_mm/2
    length=CONFIG.guide_axial_length_mm
    # Supported outboard captured guide; 1.9 mm nominal radial guide wall.
    ring=block(x-3.8,y-length/2,z-3.8,7.6,length,7.6)
    web=block(x+3.15,y-length/2,core_top-2.0,
              -6.5-(x+3.15),length,z-1.0-(core_top-2.0))
    joined=arm.fuse(web).fuse(ring)
    guide_hole=cyl_y(radius,length+2,x,y-length/2-1,z)
    return joined.cut(guide_hole).clean()


def first_arm():
    a=block(-7,-52,7.5,14,35,6)
    for y in (-17,-52):
        a=a.fuse(cyl_z(7,6,0,y,7.5))
        a=a.cut(cyl_z(2.15,9,0,y,6))
    a=a.cut(old.hex_pocket(7.2,3.3,(0,-52,7.45)))
    return cable_guide(a,y=CONFIG.guide_first_y_mm,
                       z=CONFIG.guide_first_z_mm,core_top=13.5)


def second_arm():
    a=block(-7,-87,15,14,35,6)
    a=a.fuse(cyl_z(7,6,0,-52,15))
    a=a.cut(cyl_z(2.15,8,0,-52,14))
    a=a.fuse(block(-6,-90,-12,12,8,31))
    a=a.fuse(cyl_x(7.5,12,-6,-87,-12))
    a=a.cut(cyl_x(2.15,14,-7,-87,-12))
    return cable_guide(a,y=CONFIG.guide_second_y_mm,
                       z=CONFIG.guide_second_z_mm,core_top=21)
