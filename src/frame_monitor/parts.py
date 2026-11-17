#!/usr/bin/env python3
"""V004 fixed horizontal 4040 extrusion monitor. mm; prototype envelope, not production fit.

Changes over V003:
- 4040 along global X; two metal M5 sliding nuts clamp base, short printed key only aligns it
- key 0.65 mm below extrusion face; plate bears against extrusion face
- three M4 thumb knobs with captive hex pockets, no external wrench for re-aiming
- full perimeter camera shell + removable windowed four-screw faceplate
- microUSB exits bottom into cable service loop and zip-tie saddles along the arm

V001..V003 sources, artifacts and preview assets are retained, not regenerated.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import json, math
import cadquery as cq
from . import rail as b
from .primitives import Spec, block, cyl_x, cyl_y, cyl_z, v5_key

ROOT=Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class V004Spec:
    face_key_recess:float=0.65
    radial_slide_clearance:float=0.18
    key_length:float=11.0
    nut_length:float=9.0
    mount_hole_pitch:float=30.0
    arm_segment_length:float=35.0
    arm_width:float=14.0
    first_pivot_y:float=-17.0
    elbow_pivot_y:float=-52.0
    camera_pivot_y:float=-87.0
    camera_pivot_z:float=-12.0
    shell_width:float=36.0
    shell_back_y:float=-116.0
    shell_front_y:float=-92.0
    shell_bottom_z:float=2.0
    shell_top_z:float=53.0
    board_width:float=27.0
    board_height:float=40.0
    board_stack_depth:float=17.0
    yaw_deg:float=18.0
    elbow_deg:float=-15.0
    camera_pitch_deg:float=12.0

P=V004Spec()
S=replace(b.V,mount_hole_pitch=P.mount_hole_pitch,mount_width=18.0,mount_height=51.0,slide_fit=P.radial_slide_clearance,tongue_recess=P.face_key_recess,key_length=P.key_length)

def cyl(r,l,position,axis=(0,0,1)):
    return cq.Solid.makeCylinder(r,l,cq.Vector(*position),cq.Vector(*axis))

def hex_pocket(af,depth,position,axis='z'):
    # polygon diameter is circumscribed circle diameter: across flats = af
    r=af/math.sqrt(3)
    s=cq.Workplane('XY').polygon(6,2*r).extrude(depth).val()
    if axis=='x':s=s.rotate((0,0,0),(0,1,0),90)
    return s.translate(position)

def base_plate():
    v=b.rail_base(S)
    # M4 captive nut in base under the first pivot, bottom accessible during assembly
    v=v.cut(hex_pocket(7.2,3.2,(0,P.first_pivot_y,-6)))
    return v.clean()

def alignment_key():
    # No screws in alignment key; it can never bottom against the plate at X=20
    return v5_key(S,P.key_length).rotate((0,0,0),(0,0,1),180).translate((20,10,0)).cut(block(20-P.face_key_recess,-5,-10,3,30,20)).clean()

def steel_tnut(z):
    # Nominal metal nut mimics recovered V5 slot-compatible undercut section.
    # 0.65 mm under face; M5 hole along global X; threads intentionally schematic.
    n=v5_key(S,P.nut_length).rotate((0,0,0),(0,0,1),180).translate((20,10,z))
    n=n.cut(block(20-P.face_key_recess,-5,z-6,3,30,12))
    n=n.cut(cyl(2.5,9,(12.5,10,z),(1,0,0)))
    return n.clean()

def arm_one():
    # lower 35mm link with parallel Z elbow pivot
    a=block(-7,-52,7.5,14,35,6)
    for y in (-17,-52):
        a=a.fuse(cyl_z(7.0,6,0,y,7.5))
        a=a.cut(cyl_z(2.15,9,0,y,6))
    a=a.cut(hex_pocket(7.2,3.3,(0,-52,7.45)))
    # integrally bonded strain-relief saddle; hollow channel for a ~3mm cable
    a=a.fuse(block(-5,-37,13.2,10,6,5))
    a=a.cut(cyl_y(1.9,8,0,-38,16.4))
    return a.clean()

def arm_two():
    a=block(-7,-87,15.0,14,35,6)
    a=a.fuse(cyl_z(7.0,6,0,-52,15.0))
    a=a.cut(cyl_z(2.15,8,0,-52,14.0))
    # support descends to pitch joint, but stays in front of the camera shell
    a=a.fuse(block(-6,-90,-12,12,8,31))
    a=a.fuse(cyl_x(7.5,12,-6,-87,-12))
    a=a.cut(cyl_x(2.15,14,-7,-87,-12))
    # cable saddle on upper arm surface
    a=a.fuse(block(-5,-70,20.7,10,6,5))
    a=a.cut(cyl_y(1.9,8,0,-71,23.9))
    return a.clean()

def camera_shell():
    # Closed left and right walls, continuous back, bottom/top perimeter.
    s=block(-18,-116,2,36,24,51)
    # rear wall 3mm, wall thickness 3mm, bottom 4mm, top 4mm
    s=s.cut(block(-15,-113,6,30,22,43))
    # Bottom-mounted USB port: centered slot; 2 structural side feet remain
    s=s.cut(block(-5.5,-111,1,11,14,7))
    # 4 blind M2.5 pilot bores from front edge towards rear
    for x in (-16.25,16.25):
        for z in (4.5,50.5):
            s=s.cut(cyl(1.07,7,(x,-91,z),(0,-1,0)))
    # off-axis pitch lug and rib below the board floor, avoiding the camera envelope
    s=s.fuse(cyl_x(7.5,4.3,7.4,-87,-12))
    s=s.fuse(block(7.0,-99,-16.0,11.8,6.5,22.5))
    s=s.cut(cyl_x(2.15,6,7.0,-87,-12))
    # captive M4 hex nut on pitch joint outer face
    s=s.cut(hex_pocket(7.2,3.5,(8.25,-87,-12),'x'))
    return s.clean()

def camera_bezel():
    # 4 M2.5 removable fasteners allow camera removal without destroying enclosure.
    s=block(-18,-92,2,36,3,51)
    s=s.cut(cyl_y(6.4,5,0,-93,29))  # optical aperture
    s=s.cut(block(-11,-93,43.2,22,5,6.0))  # antenna window
    for x in (-16.25,16.25):
        for z in (4.5,50.5):
            s=s.cut(cyl(1.4,5,(x,-93,z),(0,1,0)))
    return s.clean()

def board_envelope():
    # Two physically separate visual references, nominal only: main board and lens.
    body=block(-13.5,-112,8,27,17,40)
    # lens extends toward bezel, through optical aperture
    lens=cyl_y(3.0,2,0,-95,29)
    return body.fuse(lens).clean()

def thumbwheel():
    # printed 12-sided wrench-free hand wheel w/ hex-head recess and through M4 shaft
    knob=cq.Workplane('XY').polygon(12,23).extrude(7).val()
    knob=knob.cut(cyl_z(2.15,9,0,0,-1))
    knob=knob.cut(hex_pocket(7.2,3.2,(0,0,4)))
    return knob.clean()

def m4_bolt(length):
    # nominal smooth shank with M4 7mm hex head, shoulder at Z=0, shaft toward -Z
    sh=cyl(2,length,(0,0,-length))
    head=hex_pocket(7,3,(0,0,0))
    return sh.fuse(head).clean()

def m4_nut():
    return hex_pocket(7.0,3.2,(0,0,0)).cut(cyl(2,3.5,(0,0,-0.15))).clean()

def washer():
    return cyl_z(4.5,1,0,0,0).cut(cyl_z(2.25,1.3,0,0,-.1)).clean()

def m5_socket(z):
    # 2x M5 bolts with shaft from x=23 toward x=15, through base into metal T-nut
    return b.socket_cap_screw(5,8,8.5,5,4,(23,10,z),'-x')

def pose_one(s):return s.rotate((0,-17,0),(0,-17,1),P.yaw_deg)
def pose_two(s):
    return pose_one(s.rotate((0,-52,0),(0,-52,1),P.elbow_deg))
def pose_cam(s):
    return pose_two(s.rotate((0,-87,-12),(1,-87,-12),P.camera_pitch_deg))

def horizontal(s):
    # First convert local bracket (-Y) -> global X outward on the right rail face,
    # then rotate *everything* so 4040 rail is HORIZONTAL (global X).
    return s.rotate((0,0,0),(0,1,0),90)

def add_hardware(parts):
    def add(name,shape,rgb,kind='hardware'):parts.append((name,horizontal(shape),rgb,kind))
    for i,z in enumerate((-15,15),1):
        add(f'M5x8_fastener_{i}',m5_socket(z),(.70,.71,.73))
    # Three proper metal bolts with printable, manually adjustable thumb wheels.
    # Nested shell bolt holes are simplified nominal M4 clearance models.
    for name,xyz,orientation,length in [
        ('base_roll',(0,-17,17.5),'z',25),
        ('elbow_swing',(0,-52,25.0),'z',19),
        ('camera_tilt',(-11.1,-87,-12),'x',23)]:
        wheel=thumbwheel()
        shaft=m4_bolt(length)
        if orientation=='x':
            # Rotate -Z shaft into +X; knob extends towards negative X
            wheel=wheel.rotate((0,0,0),(0,1,0),-90)
            shaft=shaft.rotate((0,0,0),(0,1,0),-90)
            # Wheel must not intersect arm lug; center at -14, bolt head at -7.1
            wpos=(-7.1,xyz[1],xyz[2]);bpos=xyz
        else:
            wpos=(xyz[0],xyz[1],xyz[2]-4.0);bpos=xyz
        trans=lambda sh,pos:sh.translate(pos)
        pose=pose_one if name=='elbow_swing' else (pose_two if name=='camera_tilt' else (lambda sh:sh))
        add(f'M4_thumbwheel_{name}',b.install(pose(trans(wheel,wpos))),(0.98,.69,.16),'printed')
        add(f'M4_bolt_{name}',b.install(pose(trans(shaft,bpos))),(0.75,.75,.78))
    # Captive M4 hex nuts in each receiving part, tool-free tightening.
    for name,position,pose,orient in [
        ('base_roll',(0,-17,-6),lambda s:s,'z'),
        ('elbow_swing',(0,-52,7.45),pose_one,'z'),
        ('camera_tilt',(8.25,-87,-12),pose_cam,'x')]:
        nut=m4_nut()
        if orient=='x':nut=nut.rotate((0,0,0),(0,1,0),90)
        add(f'M4_captive_hex_nut_{name}',b.install(pose(nut.translate(position))),(.78,.8,.81))
    # four M2.5 fastener references along front/rear camera axis
    for i,(x,z) in enumerate(((x,z) for x in (-16.25,16.25) for z in (4.5,50.5)),1):
        s=cyl(1.25,7,(x,-89,z),(0,-1,0)).fuse(cyl(2.25,1.7,(x,-89,z),(0,1,0)))
        add(f'M2p5_bezel_screw_{i}',b.install(pose_cam(s)),(.76,.76,.79))



def routed_power_cable():
    """Illustrative 3.2mm USB power cable: starts at BOTTOM, follows both arms.

    Point chains are posed with each moving link and joined by flexible service
    loops across the two joints. Not a connector model or minimum-bend test.
    """
    def point(p,pose):
        bead=cyl(0.12,0.2,p)
        center=b.install(pose(bead)).Center()
        return horizontal(cyl(.12,.2,center.toTuple())).Center()
    chain=[
       ((0,-104,2),pose_cam),((0,-104,-23),pose_cam),
       ((0,-91,-26),pose_cam),((0,-83,-23),pose_cam),
       ((11,-78,-20),pose_two),((11,-78,23.5),pose_two),
       ((0,-72,23.9),pose_two),((0,-67,23.9),pose_two),
       ((0,-54,23.9),pose_two),((11,-48,22),pose_one),
       ((11,-45,16.4),pose_one),((0,-37,16.4),pose_one),
       ((0,-34,16.4),pose_one),((11,-22,16.4),pose_one),
       ((11,-9,13),pose_one)]
    pts=[point(p,pose) for p,pose in chain]
    def link(a,bb):
        d=bb-a
        return cyl(1.6,d.Length,a.toTuple(),d.normalized().toTuple())
    geom=cq.Compound.makeCompound([link(a,bb) for a,bb in zip(pts[:-1],pts[1:])]+[cq.Solid.makeSphere(1.6,p) for p in pts])
    return geom

def components():
    parts=[]
    def add(name,shape,rgb,kind='printed'):parts.append((name,horizontal(shape),rgb,kind))
    add('4040_horizontal_reference',b.profile_rail(180),(.62,.66,.72),'reference')
    add('V004_recessed_alignment_key',alignment_key(),(.94,.44,.12))
    for side,z in [('left',-15),('right',15)]:
        add(f'M5_metal_tnut_{side}',steel_tnut(z),(.77,.77,.80),'hardware')
    add('V004_mount_plate',b.install(base_plate()),(.15,.23,.31))
    add('V004_first_arm',b.install(pose_one(arm_one())),(.92,.36,.16))
    add('V004_second_arm',b.install(pose_two(arm_two())),(.90,.52,.17))
    add('V004_full_sidewall_camera_shell',b.install(pose_cam(camera_shell())),(.08,.46,.59))
    add('V004_removable_camera_bezel',b.install(pose_cam(camera_bezel())),(.92,.7,.23))
    add('ESP32_CAM_MB_provisional_envelope',b.install(pose_cam(board_envelope())),(.04,.55,.27),'reference')
    add_hardware(parts)
    # Routing is a reference compound (individual cable segments), not a print part.
    parts.append(('USB_bottom_exit_arm_routing_reference',routed_power_cable(),(.12,.12,.17),'reference_cable'))
    return parts

def build():
    for sub in ('step','stl','docs','previews'):(ROOT/sub).mkdir(exist_ok=True,parents=True)
    names=['V004_recessed_alignment_key','V004_mount_plate','V004_first_arm','V004_second_arm',
           'V004_full_sidewall_camera_shell','V004_removable_camera_bezel','V004_M4_thumbwheel']
    # STL and individual STEP in PRINT ORIENTATION (unposed, local geometry)
    local=dict(zip(names,[alignment_key(),base_plate(),arm_one(),arm_two(),camera_shell(),camera_bezel(),thumbwheel()]))
    out=[]
    for name,shape in local.items():
        assert shape.isValid() and len(shape.Solids())==1,(name,'BREP invalid',len(shape.Solids()))
        cq.exporters.export(shape,str(ROOT/'step'/f'{name}.step'))
        cq.exporters.export(shape,str(ROOT/'stl'/f'{name}.stl'),tolerance=.08,angularTolerance=.12)
        out.append({'name':name,'volume_mm3':round(shape.Volume(),2),'valid':True})
    parts=components()
    assembly=cq.Assembly(name='ESP32_CAM_MB_HORIZONTAL_4040_V004')
    for n,shape,col,kind in parts:
        assert shape.isValid() and (len(shape.Solids())==1 or kind=='reference_cable'),(n,'invalid assembled solid')
        assembly.add(shape,name=n,color=cq.Color(*col))
    path=ROOT/'step'/'COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V004.step'
    assembly.save(str(path),exportType='STEP')
    manifest={'revision':'V004','units':'mm','scope':'prototype geometry, physical fit unverified',
              'parameters':asdict(P),'printable_parts':out,
              'components':[{'name':n,'type':k} for n,_,_,k in parts],
              'warnings':['Nominal PCB envelope; actual ESP32-CAM-MB connectors must be measured',
                          'Recovered 4040 is photo-derived, not a manufacturer-certified section',
                          'M5 T-nuts and M4 hardware depicted without real helical threads',
                          'Plate-on-face clamp and key recess must be checked on physical extrusion',
                          'Full tool-less tightening torque, servo vibration and machine travel are not tested']}
    (ROOT/'docs'/'manifest_v004.json').write_text(json.dumps(manifest,indent=2))
    print('V004 assembled components',len(parts),'STEP',path.stat().st_size,'bytes')
    return local,parts

if __name__=='__main__':build()
