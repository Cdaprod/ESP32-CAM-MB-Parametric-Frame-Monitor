#!/usr/bin/env python3
"""V003 captive, inversion-resistant ESP32-CAM-MB cradle and full 4040 demo.

Retains the original V002 Python construction as src/build_assembly.py, untouched.
Dimensions are mm. The camera PCB and programmer are nominal *envelopes* rather
than a verified physical model. 4040 shape is photo-derived. M2.5 heat-set
insert envelopes are illustrative and must match the actual selected product.

Local camera coordinates (before V002's pitch/yaw pose and install transform):
  camera x = +/- 13.5 ; local y = -92 .. -78 ; local z = 8 .. 48
  left/right cradle old outer x = +/- 16.45, bottom stops z = 4 .. 6.2
  board FRONT is local +Y, EXIT on gravity inversion is local +Z.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, math
import cadquery as cq

import build_assembly as upstream
from build_assembly import V, A, ROOT, cylinder, pose_camera, install
from v001_mount import block, cyl_z

@dataclass(frozen=True)
class CaptureSpec:
    # Base cradle stays V002 but is upgraded with outer towers and wider front lips.
    front_lip_overlap_width: float = 2.20  # V002=1.10: stronger forward retention
    tower_x_inner: float = 14.05  # 0.55 side clearance to nominal 27-mm PCB
    tower_x_outer: float = 22.55
    tower_y_back: float = -92.50
    tower_y_front: float = -80.50
    tower_z_bottom: float = 38.20
    tower_z_top: float = 49.25
    cap_z_base: float = 49.25
    cap_thickness: float = 3.00
    cap_y_rear: float = -91.0
    cap_y_front: float = -80.50
    cap_bridge_y_front: float = -88.60
    cap_bridge_half_x: float = 11.20
    cap_wing_inner_x: float = 10.80
    insert_x: float = 18.30
    insert_y: float = -86.50
    insert_pocket_d: float = 3.45
    insert_outer_d: float = 3.70
    insert_inner_d: float = 2.55
    insert_length: float = 4.00
    insert_top_z: float = 49.20
    cap_clearance_d: float = 2.90
    screw_d: float = 2.50
    screw_length: float = 8.00
    screw_head_d: float = 4.50
    screw_head_height: float = 2.50
    nominal_board_top_z: float = 48.0
    nominal_camera_top_clearance: float = 1.25

C = CaptureSpec()


def captured_cradle(s=V,c=C):
    """Integrally connected V002 cradle with side towers and enhanced lips."""
    body=upstream.v002_camera_cradle(s)
    side_internal_half=s.pcb_width/2+s.cradle_side_clearance
    front_y=-95.5+s.cradle_rear_thickness+s.cradle_depth-2.2
    for side in (-1,1):
        x0=c.tower_x_inner if side==1 else -c.tower_x_outer
        body=body.fuse(block(x0,c.tower_y_back,c.tower_z_bottom,
              c.tower_x_outer-c.tower_x_inner,
              c.tower_y_front-c.tower_y_back,
              c.tower_z_top-c.tower_z_bottom))
        # Extend old V002 lip by 1.1 mm towards midline, same y and z extent.
        # Cut-free approach avoids changing the proven rear web and pitch tab.
        old_lip=1.10
        extra=c.front_lip_overlap_width-old_lip
        if side==-1:
            xx=-side_internal_half+old_lip
        else:
            xx=side_internal_half-c.front_lip_overlap_width
        body=body.fuse(block(xx,front_y,8.0,extra,2.2,s.pcb_length-9))
    # TWO vertical insert seats; actual inserts are selected/manufactured hardware.
    # Undersized pilot depicts nominal heat-set embedding into surrounding polymer.
    # Actual insert bore requires selecting real hardware and verifying its datasheet.
    for side in (-1,1):
        x=side*c.insert_x
        body=body.cut(cylinder(c.insert_pocket_d/2,4.35,
                               (x,c.insert_y,c.tower_z_top-4.30)))
        # blind tip relief below insert: avoids driving M2.5 into solid plastic
        body=body.cut(cylinder(1.5,1.45,(x,c.insert_y,43.80)))
    return body.clean()


def bolted_retainer(c=C):
    """Detachable U-shaped bridge: top stop at z=49.25 over 48-mm board.

    Side fingers overlap board corners across x=[11,13.5] and
    x=[-13.5,-11]. The center rear 2.4-mm strip joins both wings while
    leaving the front antenna area open. 3 mm thick and 2 x M2.5 clearance.
    """
    z=c.cap_z_base;th=c.cap_thickness
    width=c.tower_x_outer-c.cap_wing_inner_x
    l=block(-c.tower_x_outer,c.cap_y_rear,z,width,c.cap_y_front-c.cap_y_rear,th)
    r=block(c.cap_wing_inner_x,c.cap_y_rear,z,width,c.cap_y_front-c.cap_y_rear,th)
    b=block(-c.cap_bridge_half_x,c.cap_y_rear,z,2*c.cap_bridge_half_x,
            c.cap_bridge_y_front-c.cap_y_rear,th)
    body=l.fuse(r).fuse(b)
    for sign in (-1,1):
        x=sign*c.insert_x
        body=body.cut(cylinder(c.cap_clearance_d/2,th+0.4,(x,c.insert_y,z-0.2)))
    return body.clean()


def insert_envelope(c=C):
    """Metal insert BREP, centered at origin, bottom z=0; no real knurl modeled."""
    outer=cylinder(c.insert_outer_d/2,c.insert_length,(0,0,0))
    hole=cylinder(c.insert_inner_d/2,c.insert_length+.3,(0,0,-.15))
    return outer.cut(hole).clean()


def cap_screw(c=C):
    """M2.5 socket-head screw underhead at z=0, shaft downward (-Z)."""
    local=upstream.socket_cap_screw(c.screw_d,c.screw_length,
              c.screw_head_d,c.screw_head_height,2.0)
    return local.rotate((0,0,0),(1,0,0),180)


def new_parts_local():
    return captured_cradle(),bolted_retainer()


def assemble_components_v003():
    comps=[]
    for n,shape,col,kind in upstream.assemble_components():
        if n=='V001_camera_tilt_cradle':
            cr=captured_cradle()
            comps.append(('V003_anti_inversion_cradle',install(pose_camera(cr)),
                          (0.06,0.48,0.64),'printed'))
        else:
            comps.append((n,shape,col,kind))
    cap=bolted_retainer()
    comps.append(('V003_bolted_top_retainer',install(pose_camera(cap)),
                  (0.95,0.70,0.18),'printed'))
    insert=insert_envelope()
    screw=cap_screw()
    for side,name in ((-1,'left'),(1,'right')):
        x=side*C.insert_x
        ins=insert.translate((x,C.insert_y,C.insert_top_z-C.insert_length))
        sc=screw.translate((x,C.insert_y,C.cap_z_base+C.cap_thickness))
        comps.append((f'M2p5_brass_insert_{name}',install(pose_camera(ins)),
                      (0.82,0.63,0.27),'hardware'))
        comps.append((f'M2p5x8_socket_screw_{name}',install(pose_camera(sc)),
                      (0.70,0.73,0.78),'hardware'))
    return comps


def build_v003():
    (ROOT/'step').mkdir(exist_ok=True);(ROOT/'stl').mkdir(exist_ok=True)
    (ROOT/'docs').mkdir(exist_ok=True)
    comps=assemble_components_v003()
    assembly=cq.Assembly(name='4040_ESP32_CAM_MB_CAPTIVE_CRADLE_DEMO_V003')
    for n,shape,color,kind in comps:
        assert shape.isValid(),(n,'invalid BREP')
        assert len(shape.Solids())==1,(n,'not a single solid')
        assembly.add(shape,name=n,color=cq.Color(*color))
    # The original V002 BOM's four printed parts remain but the V002 cradle is
    # replaced by a NEW SOLID. Preserve original V002 unchanged within reference.
    cradle,cap=new_parts_local()
    for name,solid in [('V003_anti_inversion_cradle',cradle),
                       ('V003_bolted_top_retainer',cap)]:
        cq.exporters.export(solid,str(ROOT/'step'/f'{name}.step'))
        cq.exporters.export(solid,str(ROOT/'stl'/f'{name}.stl'),
                            tolerance=.08,angularTolerance=.12)
    stepout=ROOT/'step'/'COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V003.step'
    assembly.save(str(stepout),exportType='STEP')
    manifest={'units':'mm','rev':'V003','base':'V002; original ZIP preserved in reference/',
              'capture_spec':asdict(C),'original_v002_assembly':asdict(A),
              'parts':[{'name':n,'kind':kind,'volume_mm3':round(s.Volume(),4)} for n,s,col,kind in comps]}
    (ROOT/'docs'/'assembly_manifest_v003.json').write_text(json.dumps(manifest,indent=2))
    print('V003',len(comps),'solids; STEP',stepout,'size',stepout.stat().st_size)
    return comps

if __name__=='__main__':build_v003()
