"""V009 tapered triangulated arm profiles; original V008 joint/cable datums retained."""
import cadquery as cq
from . import parts as old
from .primitives import block, cyl_x, cyl_z, cyl_y
from .config import CONFIG

def _skeletal_link(front,back,bottom,thickness=7.5):
    outline=[(-7,front),(7,front),(9,front-8),(9,back+8),
             (7,back),(-7,back),(-9,back+8),(-9,front-8)]
    link=cq.Workplane('XY').polyline(outline).close().extrude(thickness).val().translate((0,0,bottom))
    for opening in ([(-5,front-9),(-5,back+9),(2.2,back+9)],
                    [(5,front-9),(5,back+9),(-2.2,front-9)]):
        tool=cq.Workplane('XY').polyline(opening).close().extrude(thickness+2).val().translate((0,0,bottom-1))
        link=link.cut(tool)
    return link

def cable_guide(arm,*,y,z,core_top):
    x=CONFIG.cable_outboard_x_mm
    length=CONFIG.guide_axial_length_mm
    ring=block(x-3.8,y-length/2,z-3.8,7.6,length,7.6)
    web=block(x+3.15,y-length/2,core_top-2,
              -6.5-(x+3.15),length,z-1-(core_top-2))
    return arm.fuse(web).fuse(ring).cut(
        cyl_y(CONFIG.guide_bore_diameter_mm/2,length+2,x,y-length/2-1,z)).clean()

def first_arm():
    a=_skeletal_link(-17,-52,7.5)
    for y in (-17,-52):
        a=a.fuse(cyl_z(7,7.5,0,y,7.5))
        a=a.cut(cyl_z(2.15,10,0,y,6.5))
    a=a.cut(old.hex_pocket(7.2,3.3,(0,-52,7.45)))
    return cable_guide(a,y=CONFIG.guide_first_y_mm,
                       z=CONFIG.guide_first_z_mm,core_top=15)

def second_arm():
    a=_skeletal_link(-52,-87,15)
    a=a.fuse(cyl_z(7,7.5,0,-52,15))
    a=a.cut(cyl_z(2.15,10,0,-52,14))
    a=a.fuse(block(-6,-90,-12,12,8,31))
    a=a.fuse(cyl_x(7.5,12,-6,-87,-12))
    a=a.cut(cyl_x(2.15,14,-7,-87,-12))
    return cable_guide(a,y=CONFIG.guide_second_y_mm,
                       z=CONFIG.guide_second_z_mm,core_top=22.5)
