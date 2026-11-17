"""V010 tapered triangulated arm profiles; original V008 joint/cable datums retained."""
import cadquery as cq
from . import parts as old
from .primitives import block, cyl_x, cyl_z, cyl_y
from .config import CONFIG as C

def _skeletal_link(front,back,bottom,thickness=7.5):
    outline=[(-7,front),(7,front),(9,front-8),(9,back+8),
             (7,back),(-7,back),(-9,back+8),(-9,front-8)]
    link=cq.Workplane('XY').polyline(outline).close().extrude(thickness).val().translate((0,0,bottom))
    for opening in ([(-5,front-9),(-5,back+9),(2.2,back+9)],
                    [(5,front-9),(5,back+9),(-2.2,front-9)]):
        tool=cq.Workplane('XY').polyline(opening).close().extrude(thickness+2).val().translate((0,0,bottom-1))
        link=link.cut(tool)
    return link

def clip(arm,*,yc,zc,open_side,x):
    """Short open U-retainer fused into the moving link; bore along local Y."""
    w=C.clip_width_mm
    r=C.clip_outer_radius_mm
    shell=cyl_y(r,w,x,yc-w/2,zc).cut(cyl_y(C.clip_bore_mm/2,w+2,x,yc-w/2-1,zc))
    mouth=(block(x+0.7,yc-w/2-1,zc-C.clip_throat_mm/2,r+3,w+2,C.clip_throat_mm)
           if open_side>0 else
           block(x-r-3,yc-w/2-1,zc-C.clip_throat_mm/2,r+2.3,w+2,C.clip_throat_mm))
    shell=shell.cut(mouth)
    foot=block(x+1.3,yc-w/2,zc-r+0.15,(-6.8)-(x+1.3),w,1.5)
    return arm.fuse(shell.fuse(foot)).clean()

def first_arm():
    a=_skeletal_link(-17,-52,7.5)
    for y in (-17,-52):
        a=a.fuse(cyl_z(7,7.5,0,y,7.5))
        a=a.cut(cyl_z(2.15,10,0,y,6.5))
    a=a.cut(old.hex_pocket(7.2,3.3,(0,-52,7.45)))
    for y,side in zip(C.first_clip_y_mm,(-1,1)):
        a=clip(a,yc=y,zc=C.first_cable_z_mm,open_side=side,x=C.first_cable_x_mm)
    return a.clean()

def second_arm():
    a=_skeletal_link(-52,-87,15)
    a=a.fuse(cyl_z(7,7.5,0,-52,15))
    a=a.cut(cyl_z(2.15,10,0,-52,14))
    a=a.fuse(block(-6,-90,-12,12,8,31))
    a=a.fuse(cyl_x(7.5,12,-6,-87,-12))
    a=a.cut(cyl_x(2.15,14,-7,-87,-12))
    for y,side in zip(C.second_clip_y_mm,(-1,1)):
        a=clip(a,yc=y,zc=C.second_cable_z_mm,open_side=side,x=C.second_cable_x_mm)
    return a.clean()
