#!/usr/bin/env python3
"""V006: independent fourth wrist pivot and outboard USB routing.
Retains V005 left-face 4040 assembly and V004 base, elbow and pitch joints.
Geometric reference only: no physical cable bending, strain or torque qualification.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from functools import lru_cache
import cadquery as cq
from . import parts as b4

from .primitives import block, cyl_x, cyl_z
from .finish import finish_wrist,finish_shell

ROOT=Path(__file__).resolve().parents[2]

def left_side(shape):
    return shape.rotate((0,0,0),(1,0,0),90)


@dataclass(frozen=True)
class Spec:
    base_yaw_deg:float=30.0
    elbow_deg:float=-30.0
    pitch_deg:float=12.0
    wrist_yaw_deg:float=0.0
    wrist_x_mm:float=7.5
    wrist_y_mm:float=-136.0
    cable_d_mm:float=3.2
    min_knob_gap_mm:float=2.0
    min_rigid_gap_mm:float=1.5

S=Spec()

@lru_cache(maxsize=1)
def adapter():
    """New M4 pitch ear coupled to 49mm wrist link and bottom Z-journal."""
    ya=S.wrist_y_mm
    a=cyl_x(9.5,6.3,7.4,-87,-12)
    a=a.fuse(block(7.35,ya,-14,6.35,-87-ya,8))
    # A broad wrist-end spine tapers back to the pitch mating plane.
    web=(cq.Workplane('XY').polyline([(3,-136),(13.7,-136),
         (13.7,-87),(7.35,-87),(7.35,-99),(3,-108)])
         .close().extrude(8).val().translate((0,0,-14)))
    a=a.fuse(web)
    # Continuous underside rib reaches BOTH journals, rather than ending
    # short of the small pitch-ear/beam junction.
    rib=(cq.Workplane('YZ').polyline([(-136,-9),(-87,-9),
         (-87,-18),(-94,-20),(-124,-16),(-136,-10)])
         .close().extrude(6.35).val().translate((7.35,0,0)))
    a=a.fuse(rib)
    a=a.fuse(cyl_z(7,6,S.wrist_x_mm,ya,-10))
    a=a.cut(cyl_x(2.15,8,7,-87,-12))
    a=a.cut(b4.hex_pocket(7.2,3.75,(10.25,-87,-12),'x'))
    a=a.cut(cyl_z(2.15,7,S.wrist_x_mm,ya,-10.5))
    # Open the nut insertion passage through the deeper rib; the nut seat
    # and metal nut datum remain at their original height.
    a=a.cut(b4.hex_pocket(7.2,8.2,(S.wrist_x_mm,ya,-15)))
    return finish_wrist(a.clean())

@lru_cache(maxsize=1)
def shell():
    """Full-sidewall V004 shell with new wrist leaf instead of original pitch ear."""
    s=block(-18,-116,2,36,24,51)
    s=s.cut(block(-15,-113,6,30,22,43))
    s=s.cut(block(-5.5,-111,1,11,14,7))
    for x in (-16.25,16.25):
        for z in (4.5,50.5):
            s=s.cut(b4.cyl(1.07,7,(x,-91,z),(0,-1,0)))
    # Full-width leaf, with a deep rear-wall root instead of the previous
    # 5 mm tab attached to the floor by only 0.8 mm of overlap.
    s=s.fuse(block(.5,S.wrist_y_mm,-3.5,14,-113-S.wrist_y_mm,5.8))
    # Begin the rising buttress outside the rotating handwheel's R11.5
    # envelope. Its 12 x 14 mm rear-wall attachment avoids the USB opening.
    root=(cq.Workplane('YZ').polyline([(-123,1.8),(-116,16),
          (-113,16),(-113,2),(-116,1.8)])
          .close().extrude(12).val().translate((1.5,0,0)))
    s=s.fuse(root)
    s=s.fuse(cyl_z(7,5.8,S.wrist_x_mm,S.wrist_y_mm,-3.5))
    s=s.cut(cyl_z(2.15,7,S.wrist_x_mm,S.wrist_y_mm,-4))
    # Nominal 3mm sidewalls: 0.8mm triangular outer reliefs leave >=2.2mm.
    for x in (-18,17.2):
        for y0,z0 in ((-107,16),(-107,36)):
            pocket=(cq.Workplane('YZ')
                 .polyline([(y0,z0),(y0+10,z0),(y0+5,z0+9)])
                 .close().extrude(.8).val().translate((x,0,0)))
            s=s.cut(pocket)
    s=s.clean()
    # R1.5 concave root blend spreads the transition into the rear wall.
    edges=[e for e in s.Edges() if abs(e.Center().y+116)<.001
           and abs(e.Center().z-16)<.001 and abs(e.Length()-12)<.001]
    if len(edges)!=1: raise ValueError('Shell root edge selection changed')
    s=s.fillet(1.5,edges)
    return finish_shell(s.clean())

def pose_cam(s,wrist=0.0):
    return b4.pose_cam(s.rotate((S.wrist_x_mm,S.wrist_y_mm,0),
                               (S.wrist_x_mm,S.wrist_y_mm,1),wrist))

def install(s,pose=None):
    return left_side(b4.horizontal(b4.b.install((pose or (lambda v:v))(s))))

def _point(p,pose):
    return install(cq.Vertex.makeVertex(*p),pose).Center()

def cable_points(wrist=0.0):
    """3.2mm nominal flexible polyline; links track their own moving pose."""
    cam=lambda s:pose_cam(s,wrist)
    link=b4.pose_cam
    coords=[
      ((0,-104,1),cam), ((0,-104,-1.5),cam),
      ((0,-120,-1.5),cam),((-27,-120,-1.5),cam),
      ((-27,-120,-28),cam),((-27,-136,-28),cam),
      ((-27,-140,-28),link),((-27,-116,-28),link),
      ((-27,-91,-27),link),((-27,-89,-27),b4.pose_two),
      ((-27,-72,27),b4.pose_two),((-27,-56,27),b4.pose_two),
      ((-27,-48,27),b4.pose_one),((-27,-35,19),b4.pose_one),
      ((-27,-23,19),b4.pose_one),((-27,-12,17),lambda s:s),
      ((-27,-4,16),lambda s:s)]
    return [_point(p,pose) for p,pose in coords]

def cable(wrist=0.0):
    pts=cable_points(wrist)
    radius=S.cable_d_mm/2
    segments=[]
    for a,b in zip(pts[:-1],pts[1:]):
        dv=b-a
        if dv.Length>1e-5:
            segments.append(cq.Solid.makeCylinder(radius,dv.Length,a,dv.normalized()))
    return cq.Compound.makeCompound(segments)

def components(base=None,elbow=None,pitch=None,wrist=None):
    base=S.base_yaw_deg if base is None else base
    elbow=S.elbow_deg if elbow is None else elbow
    pitch=S.pitch_deg if pitch is None else pitch
    wrist=S.wrist_yaw_deg if wrist is None else wrist
    old=(b4.P.yaw_deg,b4.P.elbow_deg,b4.P.camera_pitch_deg)
    for k,v in [('yaw_deg',base),('elbow_deg',elbow),('camera_pitch_deg',pitch)]:
        object.__setattr__(b4.P,k,v)
    try:
        upstream=[(n,s if n=='4040_horizontal_reference' else left_side(s),c,t)
                  for n,s,c,t in b4.components()]
        omitted={'V004_full_sidewall_camera_shell','V004_removable_camera_bezel',
                 'ESP32_CAM_MB_provisional_envelope','USB_bottom_exit_arm_routing_reference'}
        parts=[p for p in upstream if p[0] not in omitted
               and not p[0].startswith('M2p5_bezel_screw_')]
        def add(n,s,color,kind='printed',pose=None):
            parts.append((n,install(s,pose),color,kind))
        add('V006_wrist_adapter',adapter(),(.70,.31,.19),pose=b4.pose_cam)
        wp=lambda s:pose_cam(s,wrist)
        add('V006_camera_shell',shell(),(.10,.49,.62),pose=wp)
        add('V006_camera_bezel',b4.camera_bezel(),(.94,.72,.25),pose=wp)
        add('ESP32_CAM_MB_provisional_envelope',b4.board_envelope(),(.02,.58,.33),'reference',pose=wp)
        add('M4_thumbwheel_wrist',b4.thumbwheel().translate((S.wrist_x_mm,S.wrist_y_mm,4.5)),
            (.95,.69,.19),pose=b4.pose_cam)
        add('M4_bolt_wrist',b4.m4_bolt(19).translate((S.wrist_x_mm,S.wrist_y_mm,8)),
            (.75,.75,.77),'hardware',pose=b4.pose_cam)
        add('M4_captive_hex_nut_wrist',b4.m4_nut().translate((S.wrist_x_mm,S.wrist_y_mm,-10)),
            (.73,.74,.76),'hardware',pose=b4.pose_cam)
        for i,(x,z) in enumerate(((x,z) for x in (-16.25,16.25) for z in (4.5,50.5)),1):
            bolt=b4.cyl(1.25,7,(x,-89,z),(0,-1,0)).fuse(b4.cyl(2.25,1.7,(x,-89,z),(0,1,0)))
            add('M2p5_bezel_screw_%d'%i,bolt,(.76,.76,.79),'hardware',pose=wp)
        parts.append(('V006_USB_outboard_cable_reference',cable(wrist),(.12,.15,.19),'reference_cable'))
        return parts
    finally:
        for k,v in zip(('yaw_deg','elbow_deg','camera_pitch_deg'),old):
            object.__setattr__(b4.P,k,v)

def build():
    for sub in ('step','stl','docs','previews'):(ROOT/sub).mkdir(parents=True,exist_ok=True)
    for name,shape in [('V006_wrist_adapter',adapter()),('V006_camera_shell',shell())]:
        assert shape.isValid() and len(shape.Solids())==1,name
        cq.exporters.export(shape,str(ROOT/'step'/f'{name}.step'))
        cq.exporters.export(shape,str(ROOT/'stl'/f'{name}.stl'),tolerance=.08,angularTolerance=.12)
    parts=components()
    assembly=cq.Assembly(name='ESP32_CAM_MB_LEFT_SIDE_WRIST_CABLE_V006')
    for n,sh,color,kind in parts:
        assert sh.isValid(),n
        assembly.add(sh,name=n,color=cq.Color(*color))
    assembly.save(str(ROOT/'step'/'COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V006.step'),exportType='STEP')
    (ROOT/'docs'/'manifest_v006.json').write_text(json.dumps({
       'revision':'V006','spec':asdict(S),'component_count':len(parts),
       'components':[{'name':n,'kind':kind} for n,s,col,kind in parts],
       'qualification':'CAD-only; real printer fit, cable bend and torque unverified'},indent=2))
    print('V006 built',len(parts),'assembly entries')
    return parts

if __name__=='__main__':build()
