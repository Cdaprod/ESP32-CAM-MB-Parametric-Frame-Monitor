"""V010 structural arm links with cable seats integrated into their sidewalls.

The cable seats and routing groove are subtracted from a locally reinforced
arm-body edge, with no detached rings, standoffs, or vertical support struts.
Nominal CAD prototype: physical clip fatigue and cable flexibility unverified.
"""
import cadquery as cq
from . import parts as old
from .primitives import block, cyl_x, cyl_z, cyl_y
from .config import CONFIG as C
from .finish import finish_arm

def _skeletal_link(front, back, bottom, thickness=7.5):
    outline=[(-7,front),(7,front),(9,front-8),(9,back+8),
             (7,back),(-7,back),(-9,back+8),(-9,front-8)]
    link=cq.Workplane("XY").polyline(outline).close().extrude(thickness).val().translate((0,0,bottom))
    # Two rounded lightening slots retain a continuous 5 mm center spine
    # and >=3 mm outer rails, without acute internal web notches.
    for x in (-4.0,4.0):
        tool=(cq.Workplane("XY").center(x,(front+back)/2)
              .slot2D(13,3,90).extrude(thickness+2).val()
              .translate((0,0,bottom-1)))
        link=link.cut(tool)
    return link.clean()

def clip(arm, *, yc, zc, open_side):
    """Fully supported, arm-local U-seat, flush to the link thickness.

    Alternate outward (-X) and top (+Z) insertion access; the continuous
    Ø3.8-mm sidewall channel is bored once after all clip pads are fused.
    """
    x=C.first_cable_x_mm
    w=C.clip_width_mm
    r=C.clip_outer_radius_mm
    # Entire pad remains inside the 7.5-mm arm thickness, not beneath it.
    pad=block(x-r-.15,yc-w/2-.45,zc-2.75,2*r+.8,w+.9,7.5)
    solid=arm.fuse(pad).clean()
    if open_side<0:
        mouth=block(x-r-1,yc-w/2-.6,zc-C.clip_throat_mm/2,
                    r+1.25,w+1.2,C.clip_throat_mm)
    else:
        mouth=block(x-C.clip_throat_mm/2,yc-w/2-.6,zc,
                    C.clip_throat_mm,w+1.2,r+1.25)
    solid=solid.cut(mouth).clean()
    if not solid.isValid() or len(solid.Solids())!=1:
        raise ValueError(f"Disconnected U-seat at y={yc}")
    return solid

def first_arm():
    a=_skeletal_link(-17,-52,7.5)
    for y in (-17,-52):
        a=a.fuse(cyl_z(7,7.5,0,y,7.5))
        a=a.cut(cyl_z(2.15,10,0,y,6.5))
    a=a.cut(old.hex_pocket(7.2,3.3,(0,-52,7.45)))
    for y,side in zip(C.first_clip_y_mm,(-1,1)):
        a=clip(a,yc=y,zc=C.first_cable_z_mm,open_side=side)
    # Continuous shallow cable passage follows the arm from end to end,
    # removing material from the link itself instead of attaching rings.
    a=a.cut(cyl_y(C.clip_bore_mm/2,24,C.first_cable_x_mm,-45,C.first_cable_z_mm))
    return finish_arm(a.clean())

def second_arm():
    a=_skeletal_link(-52,-87,15)
    a=a.fuse(cyl_z(7,7.5,0,-52,15))
    a=a.cut(cyl_z(2.15,10,0,-52,14))
    a=a.fuse(block(-6,-90,-12,12,8,31))
    a=a.fuse(cyl_x(7.5,12,-6,-87,-12))
    a=a.cut(cyl_x(2.15,14,-7,-87,-12))
    for y,side in zip(C.second_clip_y_mm,(-1,1)):
        a=clip(a,yc=y,zc=C.second_cable_z_mm,open_side=side)
    a=a.cut(cyl_y(C.clip_bore_mm/2,27,C.second_cable_x_mm,-84,C.second_cable_z_mm))
    return finish_arm(a.clean())
