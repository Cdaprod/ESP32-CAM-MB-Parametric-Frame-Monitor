"""V010 structural arm links with cable seats integrated into their sidewalls.

The cable seats and routing groove are subtracted from a locally reinforced
arm-body edge, with no detached rings, standoffs, or vertical support struts.
Nominal CAD prototype: physical clip fatigue and cable flexibility unverified.
"""
from functools import lru_cache
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

@lru_cache(maxsize=1)
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
    a=a.cut(cyl_y(C.clip_bore_mm/2,28,C.first_cable_x_mm,-49,C.first_cable_z_mm))
    return finish_arm(a.clean())

@lru_cache(maxsize=1)
def second_arm():
    a=_skeletal_link(-52,-87,15)
    a=a.fuse(cyl_z(7,7.5,0,-52,15))
    a=a.cut(cyl_z(2.15,10,0,-52,14))
    # Relieve the rear upper corner for the housing's -20 degree wrist
    # sweep. Keep the lower boss heel, and transfer load to the front gusset.
    upright=(cq.Workplane('YZ').polyline([(-90,-12),(-82,-12),
             (-82,19),(-87.5,19),(-87.5,-1),(-90,-4.5)])
             .close().extrude(12).val().translate((-6,0,0)))
    a=a.fuse(upright)
    # Carry pitch load into 19 mm of the link with a full-width triangular
    # heel; the old upright met the arm through a short rectangular toe.
    heel=(cq.Workplane('YZ').polyline([(-87.5,-12),(-79,-12),
          (-69,16.5),(-87.5,19)])
          .close().extrude(12).val().translate((-6,0,0)))
    a=a.fuse(heel)
    a=a.fuse(cyl_x(7.5,12,-6,-87,-12))
    a=a.cut(cyl_x(2.15,14,-7,-87,-12))
    # Smooth conservative silhouette of the sampled camera/bezel sweep.
    # A single convex clearance prism avoids a staircase of stress notches
    # from successively subtracting individual pose boxes.
    from shapely.geometry import MultiPoint
    points=[]
    slab=block(-10,-100,-8,20,30,31.5)
    for pitch in (0,12,25):
        for yaw in (-20,-10,0,10,20):
            keepout=block(-18.7,-116.7,1.3,37.4,28.4,52.4)
            keepout=keepout.rotate((7.5,-136,0),(7.5,-136,1),yaw)
            keepout=keepout.rotate((0,-87,-12),(1,-87,-12),pitch)
            for v in keepout.intersect(slab).Vertices():
                c=v.Center()
                points.append((c.y,c.z))
    outline=list(MultiPoint(points).convex_hull.exterior.coords)[:-1]
    clearance=(cq.Workplane('YZ').polyline(outline).close()
               .extrude(40).val().translate((-20,0,0)))
    a=a.cut(clearance)
    for y,side in zip(C.second_clip_y_mm,(-1,1)):
        a=clip(a,yc=y,zc=C.second_cable_z_mm,open_side=side)
    a=a.cut(cyl_y(C.clip_bore_mm/2,35,C.second_cable_x_mm,-88,C.second_cable_z_mm))
    return finish_arm(a.clean())


def structural_checks():
    """Solid-section witnesses along the load path; not a strength rating."""
    from . import wrist
    shell,adapter,arm,mount=wrist.shell(),wrist.adapter(),second_arm(),old.reinforced_base_plate()
    witnesses=[
        ('enclosure rear-wall buttress',shell,block(1.5,-117,2,12,1,11.5)),
        ('enclosure full-width leaf',shell,block(.5,-126,-3.5,14,1,5.8)),
        ('wrist broad spine',adapter,block(3.5,-123,-13.8,9.7,1,7)),
        ('wrist pitch heel',adapter,block(7.35,-97,-17,6.35,1,3)),
        ('pitch upright heel',arm,block(-6,-79,8,12,3,6)),
        ('mount left rib',mount,block(-8.5,-8,-9,3,2,3)),
        ('mount right rib',mount,block(5.5,-8,-9,3,2,3)),
    ]
    for label,solid,witness in witnesses:
        missing=witness.Volume()-solid.intersect(witness).Volume()
        assert abs(missing)<1e-4,(label,'missing load-path material',missing)
    seat=block(7.5,-90.4,-12.2,2.6,.4,.4)
    assert abs(adapter.intersect(seat).Volume()-seat.Volume())<1e-5,'Thin pitch nut bearing floor'
    assert shell.intersect(old.board_envelope()).Volume()<1e-4,'Board cavity obstructed'
    usb=block(-5.5,-111,1,11,14,5)
    assert shell.intersect(usb).Volume()<1e-4,'USB aperture obstructed'
    for solid,probe in [(shell,cyl_z(2,8,7.5,-136,-4)),
                         (adapter,cyl_z(2,15,7.5,-136,-16)),
                         (adapter,cyl_x(2,8,7,-87,-12)),
                         (arm,cyl_x(2,14,-7,-87,-12)),
                         (first_arm(),cyl_z(2,10,0,-17,6.5)),
                         (mount,cyl_z(2,14,0,-17,-7))]:
        assert solid.intersect(probe).Volume()<1e-4,'Pivot bore obstructed'
    gaps=[abs(a-b)-(C.clip_width_mm+.9) for a,b in
          (C.first_clip_y_mm,C.second_clip_y_mm)]
    assert min(gaps)>=2*C.cable_diameter_mm,('Cable insertion gap too short',gaps)
    return {'section_witnesses':len(witnesses),
            'enclosure_leaf_width_mm':14,'enclosure_leaf_thickness_mm':5.8,
            'enclosure_leaf_section_mm2':81.2,'previous_leaf_section_mm2':31.5,
            'rear_root_blend_radius_mm':1.5,'pitch_ear_outer_radius_mm':9.5,'pitch_nut_seat_floor_mm':2.85,
            'clear_clip_pad_gaps_mm':gaps,'board_and_usb_clear':True,
            'pivot_bores_clear':True,'physical_load_rating':'UNTESTED'}
