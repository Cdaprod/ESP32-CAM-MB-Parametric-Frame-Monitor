#!/usr/bin/env python3
"""Full geometric demonstrator: recovered photo-derived 4040 + V5 key + ESP32-CAM-MB V001 + screws.
All lengths in mm. Model is a *prototype* reference, not a certified manufacturer 4040 profile.

Global: extrusion cross section XY [-20,20]^2; rail long axis Z; mounting on right
face X=20, near slot Y=+10. V001 mount's back face Y(old)=0 maps to global X=20.
No imported CAD meshes used for STEP: the solid rail is rebuilt from the EXACT
recovered parametric OpenSCAD 2D void topology (and hole locations).
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
from pathlib import Path
import json, math, shutil
import cadquery as cq
from .primitives import Spec, rail_base, board_reference, v5_key, block, cyl_z, cyl_x, cyl_y

ROOT=Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class AssemblySpec:
    rail_length:float=180.0
    rail_size:float=40.0
    slot_pitch:float=20.0
    active_slot_y:float=10.0
    key_length:float=45.0
    key_pilot_d:float=4.2
    key_clearance:float=0.18
    m5_nominal_d:float=5.0
    m5_length:float=8.0
    m5_head_d:float=8.5
    m5_head_height:float=5.0
    m4_nominal_d:float=4.0
    m4_length:float=25.0
    m4_head_d:float=7.0
    m4_head_height:float=4.0
    m4_washer_od:float=8.0
    m4_washer_id:float=4.4
    m4_nut_af:float=7.0
    m4_nut_height:float=4.0
    yaw_deg:float=-22.0
    pitch_deg:float=12.0

A=AssemblySpec()
V=replace(Spec(),mount_width=18.0, mount_slot_x=0.0, key_length=A.key_length)

def cylinder(radius,h,pos,axis=(0,0,1)):
    return cq.Solid.makeCylinder(radius,h,cq.Vector(*pos),cq.Vector(*axis))
def egeom(shape,name,printed=False):
    assert shape.isValid(), f'invalid BREP {name}'
    assert len(shape.Solids())==1, f'not one connected body: {name}, {len(shape.Solids())}'
    cq.exporters.export(shape,str(ROOT/'step'/f'{name}.step'))
    if printed:
        cq.exporters.export(shape,str(ROOT/'stl'/f'{name}.stl'),tolerance=0.08,angularTolerance=0.12)

def slot_poly(overcut=2):
    # Same profile as 4040_recovered_v001/source/tslot_4040_interface.scad
    return [(-overcut,-V.slot_mouth/2),(V.slot_lip_depth,-V.slot_mouth/2),
            (V.slot_lip_depth,-V.slot_head_height/2),(V.slot_head_flat_end,-V.slot_head_height/2),
            (V.slot_depth,-V.slot_inner_flat/2),(V.slot_depth,V.slot_inner_flat/2),
            (V.slot_head_flat_end,V.slot_head_height/2),(V.slot_lip_depth,V.slot_head_height/2),
            (V.slot_lip_depth,V.slot_mouth/2),(-overcut,V.slot_mouth/2)]

def slot_transform(face,center,xy):
    u,v=xy
    if face=='right':return (20-u,center-v)
    if face=='left':return (-20+u,center+v)
    if face=='top':return (center+v,20-u)
    if face=='bottom':return (center-v,-20+u)
    raise ValueError(face)

def profile_rail(length=A.rail_length):
    # Rebuild exact 2D section of recovered SCAD using analytic BREP booleans.
    zz=-length/2
    a=cq.Workplane('XY').rect(40,40).extrude(length).translate((0,0,zz)).val()
    for face in ('right','left','top','bottom'):
        for center in (-10,10):
            pts=[slot_transform(face,center,pt) for pt in slot_poly()]
            cutter=(cq.Workplane('XY').polyline(pts).close().extrude(length+2)
                    .translate((0,0,zz-1)).val())
            a=a.cut(cutter)
    for x in (-10,10):
        for y in (-10,10):
            a=a.cut(cylinder(2.25,length+2,(x,y,zz-1)))
    coords=[(-3,18),(3,18),(3,15),(6,12),(6,8),(8,6),(12,6),(15,3),
            (18,3),(18,-3),(15,-3),(12,-6),(8,-6),(6,-8),(6,-12),
            (3,-15),(3,-18),(-3,-18),(-3,-15),(-6,-12),(-6,-8),(-8,-6),
            (-12,-6),(-15,-3),(-18,-3),(-18,3),(-15,3),(-12,6),
            (-8,6),(-6,8),(-6,12),(-3,15)]
    void=cq.Workplane('XY').polyline(coords).close().extrude(length+2).translate((0,0,zz-1)).val()
    a=a.cut(void).clean()
    return a

def install(shape):
    """V001 -> active 4040 right face X=20, slot Y=+10, same Z-axis."""
    return shape.rotate((0,0,0),(0,0,1),90).translate((20,A.active_slot_y,0))

def v002_swivel_arm(s):
    """V001 yaw link with pitch axis LOWERED 9.5mm, to clear ESP32-CAM-MB envelope."""
    z0=6.5
    yp=-17.0; ye=yp-s.arm_reach
    beam=block(-s.arm_width/2,ye,z0,s.arm_width,s.arm_reach,s.arm_thickness)
    a=cyl_z(s.arm_width/2,s.arm_thickness,0,yp,z0)
    lug=cyl_x(8,12,-6,ye,0.0)
    shape=beam.fuse(a).fuse(lug)
    shape=shape.cut(cyl_z(s.pivot_hole_d/2,s.arm_thickness+2,0,yp,z0-1))
    shape=shape.cut(cyl_x(s.pivot_hole_d/2,14,-7,ye,0.0))
    return shape.clean()

def v002_camera_cradle(s):
    """V001 nominal open cradle with relocated below-PCB pivot to resolve a REAL V001 clash."""
    internal_w=s.pcb_width+2*s.cradle_side_clearance
    w=internal_w+2*s.cradle_side_wall
    bottom=4.0; rear_y=-95.5; front_y=rear_y+s.cradle_rear_thickness
    shape=block(-w/2,rear_y,bottom,w,s.cradle_rear_thickness,s.pcb_length+8)
    for sign in (-1,1):
        x0=(-w/2) if sign<0 else w/2-s.cradle_side_wall
        shape=shape.fuse(block(x0,front_y,bottom+2,s.cradle_side_wall,s.cradle_depth,s.pcb_length-5))
        lipw=1.1
        xl=(-internal_w/2) if sign<0 else (internal_w/2-lipw)
        shape=shape.fuse(block(xl,front_y+s.cradle_depth-2.2,bottom+4,lipw,2.2,s.pcb_length-9))
    for xx in (-internal_w/2,internal_w/2-7):
        shape=shape.fuse(block(xx,front_y,bottom,7,s.cradle_depth,2.2))
    ear_x=7.3; ear_y=-17.0-s.arm_reach; ear_z=0.0
    tab=cyl_x(8,4.2,ear_x,ear_y,ear_z)
    # No material enters z>=8mm in the PCB travel envelope. Web overlaps tray bottom.
    web=block(ear_x,rear_y+1,-4.0,4.2,ear_y-(rear_y+1)+1,11.5)
    shape=shape.fuse(tab).fuse(web)
    shape=shape.cut(cyl_x(s.pivot_hole_d/2,6,ear_x-1,ear_y,ear_z))
    for x in (-10,-3,4):shape=shape.cut(cyl_y(1.5,s.cradle_rear_thickness+2,x,rear_y-1,bottom+5))
    return shape.clean()

def board_envelope_v002(s):
    """Reference ESP32-CAM plus MB stack ONLY, intentionally not a detailed PCB model."""
    half=s.pcb_width/2
    pcb=block(-half,-92,8,s.pcb_width,1.6,s.pcb_length)
    mb=block(-half,-91,8,s.pcb_width,s.cam_mb_stack_depth-3,s.pcb_length)
    # Align lens base to envelope front, rather than leave a 1mm disconnected gap.
    lens=cyl_y(3.0,5.0,0,-78,29)
    return pcb.fuse(mb).fuse(lens).clean()

def original_key_with_m5_pilots():
    key=v5_key(V,A.key_length)
    for zz in (-V.mount_hole_pitch/2,V.mount_hole_pitch/2):
        # 4.2mm nominal tap pilot along inward U, in the key--NOT clearance holes.
        hole=cylinder(A.key_pilot_d/2,V.slot_depth+2,(-0.5,0,zz),(1,0,0))
        key=key.cut(hole)
    key=key.clean()
    # local U inward maps to global X inward; local V to global Y reversed.
    return key.rotate((0,0,0),(0,0,1),180).translate((20,A.active_slot_y,0))

def socket_cap_screw(d,length,head_d,head_h,hex_af,position=(0,0,0),axis='z'):
    """Nominal M5/M4 geometry with a recessed hex socket and unthreaded shaft.
    The screw length is measured *under* its head. Orientation +Z at bearing seat.
    """
    s=cylinder(d/2,length,(0,0,0)).fuse(cylinder(head_d/2,head_h,(0,0,-head_h)))
    hex_r=hex_af/math.sqrt(3)
    socket=(cq.Workplane('XY').polygon(6,2*hex_r).extrude(head_h*0.60+0.2)
            .translate((0,0,-head_h-.1)).val())
    s=s.cut(socket).clean()
    if axis=='-x':s=s.rotate((0,0,0),(0,1,0),-90)
    elif axis=='+x':s=s.rotate((0,0,0),(0,1,0),90)
    elif axis!='z': raise ValueError(axis)
    return s.translate(position)

def washer_at(z,thickness=1):
    return cylinder(A.m4_washer_od/2,thickness,(0,0,z)).cut(cylinder(A.m4_washer_id/2,thickness+0.2,(0,0,z-0.1)))

def hex_nut(z):
    # M4 metal hex nut envelope, modeled without nylon insert and internal threads.
    w=cq.Workplane('XY').polygon(6,2*A.m4_nut_af/math.sqrt(3)).extrude(A.m4_nut_height)
    return w.val().translate((0,0,z)).cut(cylinder(2.1,A.m4_nut_height+.2,(0,0,z-.1))).clean()

def at_old_xy_z(shape,x,y,z=0):return shape.translate((x,y,z))
def pose_arm(s):return s.rotate((0,-17,0),(0,-17,1),A.yaw_deg)
def pose_camera(s):
    return s.rotate((0,-77,0),(1,-77,0),A.pitch_deg).rotate((0,-17,0),(0,-17,1),A.yaw_deg)

def assemble_components():
    """(component-id, installed CQ solid, (RGB), class). All placements physically coincident."""
    comps=[]
    def add(n,s,color,kind='hardware'):comps.append((n,s,color,kind))
    rail=profile_rail()
    add('4040_reference_extrusion',rail,(0.62,0.67,0.73),'reference')
    key=original_key_with_m5_pilots()
    add('V5_profile_matched_key_M5_pilots',key,(0.97,0.48,0.09),'printed')
    base=rail_base(V)
    add('V001_mount_base_4040_slot_10',install(base),(0.15,0.24,0.30),'printed')
    arm=pose_arm(v002_swivel_arm(V))
    add('V001_60mm_yaw_arm',install(arm),(0.95,0.42,0.16),'printed')
    cradle=pose_camera(v002_camera_cradle(V))
    add('V001_camera_tilt_cradle',install(cradle),(0.15,0.57,0.69),'printed')
    pcb=pose_camera(board_envelope_v002(V))
    add('ESP32_CAM_MB_nominal_envelope',install(pcb),(0.08,0.44,0.25),'reference')
    # Front face X=20; base plate thickness=6, seat 3 deep into face of plate.
    # Underhead 23 -> tip 15: M5x8, leaving about 4.8 mm engagement inside
    # printed key, less than 6.8 mm deep slot. Metal extrusion cannot be struck.
    for i,z in enumerate((-V.mount_hole_pitch/2,V.mount_hole_pitch/2),1):
        screw=socket_cap_screw(A.m5_nominal_d,A.m5_length,A.m5_head_d,A.m5_head_height,4.0,
                               (20+V.mount_thickness-V.mount_cbore_depth,A.active_slot_y,z),'-x')
        add(f'M5x8_socket_screw_{i}',screw,(0.72,0.73,0.76))
    # M4x25 vertical yaw bolt, washers in physical gaps, M4 nylon-lock style hex envelope.
    yaw_c=(0,-17)
    s=socket_cap_screw(A.m4_nominal_d,A.m4_length,A.m4_head_d,A.m4_head_height,3.0,
                       (yaw_c[0],yaw_c[1],-7),'z')
    add('M4x25_yaw_socket_bolt',install(s),(0.74,0.75,0.77))
    for idx,zz,th in [('bottom',-7,1),('pivot',6,0.5),('top',12.5,1)]:
        add(f'M4_yaw_washer_{idx}',install(washer_at(zz,th).translate((0,-17,0))),(0.73,0.75,0.78))
    add('M4_yaw_hex_locknut',install(hex_nut(13.5).translate((0,-17,0))),(0.81,0.82,0.84))
    # pitch shaft along +X through 12mm lug + 4.2mm ear.
    pcenter=(0,-77,0)
    pbolt=socket_cap_screw(A.m4_nominal_d,A.m4_length,A.m4_head_d,A.m4_head_height,3.0,
                           (-7,-77,0),'+x')
    add('M4x25_pitch_socket_bolt',install(pose_arm(pbolt)),(0.74,0.75,0.77))
    for idx,xx,th in [('lug_inner',-7,1),('ear_gap',6,1.3),('outer',11.5,1)]:
        w=washer_at(0,th).rotate((0,0,0),(0,1,0),90).translate((xx,-77,0))
        add(f'M4_pitch_washer_{idx}',install(pose_arm(w)),(0.73,0.75,0.78))
    nut=hex_nut(0).rotate((0,0,0),(0,1,0),90).translate((12.5,-77,0))
    add('M4_pitch_hex_locknut',install(pose_arm(nut)),(0.81,0.82,0.84))
    return comps

def build_all():
    comps=assemble_components()
    print('Building geometry...')
    assembly=cq.Assembly(name='4040_ESP32_CAM_MB_PARAMETRIC_FRAME_MONITOR_DEMO_V002')
    for name,shape,color,kind in comps:
        assert shape.isValid(),('invalid',name)
        assembly.add(shape,name=name,color=cq.Color(*color))
        if kind=='printed' or name=='4040_reference_extrusion':
            egeom(shape,name,printed=kind=='printed')
    assembly.save(str(ROOT/'step'/'COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY.step'),exportType='STEP')
    json.dump({'units':'mm','assembly':asdict(A),'V001_spec':asdict(V),
               'components':[{'name':n,'kind':k,'volume_mm3':round(s.Volume(),2)} for n,s,c,k in comps],
               'fasteners':['2 x M5x8 socket-head cap screws (modelled nominally, no helical threads)',
                            '2 x M4x25 socket-head cap screws','6 x M4 washer envelopes','2 x M4 locknut envelopes']},
              open(ROOT/'docs'/'assembly_manifest.json','w'),indent=2)
    print('Saved',len(comps),'components; assembly STEP')
    return comps

if __name__=='__main__':build_all()
