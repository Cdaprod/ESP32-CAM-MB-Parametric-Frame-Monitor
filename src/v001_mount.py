#!/usr/bin/env python3
"""Parametric ESP32-CAM + MB fixed-frame corner monitor. Units: mm.

Designed for a Neptune 2 / Ender-style stationary aluminum extrusion.
NOTE: 4040 T-slot profile is an independent, photo-derived fit reference.
Actual printer's extrusion geometry must be checked before production use.

World axes: X = lateral, Y = toward/out of machine (outward is -Y), Z = up.
The camera's optical axis points toward +Y (into the bed), with yaw/pitch joints.

Run: python src/build_mount.py [--out DIR] [--yaw DEG] [--pitch DEG]
Requires: cadquery>=2.4, shapely>=2, trimesh, matplotlib, numpy.
"""
from __future__ import annotations
import argparse, json, math
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import cadquery as cq
from shapely.geometry import Polygon, box as polybox
from shapely.ops import unary_union

@dataclass(frozen=True)
class Spec:
    pcb_width: float = 27.0  # CAM board, documented, MB variant-dependent
    pcb_length: float = 40.0
    cam_mb_stack_depth: float = 16.0  # provisional, caliper verification required
    cradle_side_clearance: float = 0.55  # per side
    cradle_side_wall: float = 2.4
    cradle_rear_thickness: float = 3.0
    cradle_depth: float = 17.0
    mount_width: float = 38.0
    mount_height: float = 51.0
    mount_thickness: float = 6.0
    mount_hole_pitch: float = 25.4  # along extrusion, inherited from prior T-slot V5
    mount_slot_x: float = 0.0  # 0 for single-slot; +/-10 for recovered 4040 dual-slot face
    mount_hole_d: float = 5.5  # M5 clearance to metal T-nuts
    mount_cbore_d: float = 9.0
    mount_cbore_depth: float = 3.0
    arm_reach: float = 60.0
    arm_width: float = 14.0
    arm_thickness: float = 6.0
    pivot_hole_d: float = 4.3  # M4 screw with washers / nyloc nut
    slot_clearance: float = 0.18  # from recovered 4040 interface
    slot_mouth: float = 6.20
    slot_head_height: float = 10.50
    slot_inner_flat: float = 5.00
    slot_depth: float = 6.80
    slot_lip_depth: float = 1.50
    slot_head_flat_end: float = 3.50
    slot_stem_overlap: float = 0.60
    tongue_recess: float = 0.20  # V5: key remains INSIDE face datum
    key_length: float = 45.0
    slide_fit: float = 0.18
    fit_key_test_length: float = 18.0

S = Spec()

def cyl_z(radius, height, x, y, z0):
    return cq.Solid.makeCylinder(radius, height, cq.Vector(x,y,z0), cq.Vector(0,0,1))

def cyl_x(radius, length, x0, y, z):
    return cq.Solid.makeCylinder(radius,length,cq.Vector(x0,y,z),cq.Vector(1,0,0))

def cyl_y(radius, length, x, y0, z):
    return cq.Solid.makeCylinder(radius,length,cq.Vector(x,y0,z),cq.Vector(0,1,0))

def block(x,y,z, dx,dy,dz):
    return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))

def rail_base(s):
    # Flat, stationary frame plate. Two M5 screws into independent METAL T-nuts.
    plate = block(-s.mount_width/2,-s.mount_thickness,-s.mount_height/2,
                  s.mount_width,s.mount_thickness,s.mount_height)
    # Protruding bridge to the yaw pivot; overlap with outer plate face.
    bridge = block(-8.5,-17.5,-6.0,17.0,12.8,12.0)
    hub = cyl_z(9,12,0,-17,-6)
    shape = plate.fuse(bridge).fuse(hub)
    # M5 fasteners normal to extrusion face. Two along travel axis @25.4mm.
    for zz in (-s.mount_hole_pitch/2,+s.mount_hole_pitch/2):
        shape=shape.cut(cyl_y(s.mount_hole_d/2,s.mount_thickness+2,s.mount_slot_x,-s.mount_thickness-1,zz))
        # Outer-face counterbores go from -Y side inward.
        shape=shape.cut(cyl_y(s.mount_cbore_d/2,s.mount_cbore_depth,s.mount_slot_x,-s.mount_thickness-0.1,zz))
    shape=shape.cut(cyl_z(s.pivot_hole_d/2,14,0,-17,-7))
    return shape.clean()

def swivel_arm(s):
    z0=6.5; z1=z0+s.arm_thickness
    yp=-17.0; ye=yp-s.arm_reach
    beam=block(-s.arm_width/2,ye,z0,s.arm_width,s.arm_reach,s.arm_thickness)
    a=cyl_z(s.arm_width/2,s.arm_thickness,0,yp,z0)
    # Distal pitch lug's rotation axis is horizontal (X).
    lug=cyl_x(8,12,-6,ye,9.5)
    shape=beam.fuse(a).fuse(lug)
    shape=shape.cut(cyl_z(s.pivot_hole_d/2,s.arm_thickness+2,0,yp,z0-1))
    shape=shape.cut(cyl_x(s.pivot_hole_d/2,14,-7,ye,9.5))
    return shape.clean()

def camera_cradle(s):
    # Camera optics and antenna face +Y; camera board is slid in from top.
    # Side retainers deliberately stop below the upper antenna zone.
    internal_w=s.pcb_width+2*s.cradle_side_clearance
    w=internal_w+2*s.cradle_side_wall
    bottom=4.0
    rear_y=-95.5
    front_y=rear_y+s.cradle_rear_thickness
    wall_y=front_y
    wall_depth=s.cradle_depth
    shape=block(-w/2,rear_y,bottom,w,s.cradle_rear_thickness,s.pcb_length+8)
    # two rail walls, upper antenna kept uncovered
    for sign in (-1,1):
        x0=(-w/2) if sign<0 else w/2-s.cradle_side_wall
        shape=shape.fuse(block(x0,wall_y,bottom+2,s.cradle_side_wall,wall_depth,s.pcb_length-5))
        # 1.1mm inward retaining lip along front of side rails
        lipw=1.1
        xl=(-internal_w/2) if sign<0 else (internal_w/2-lipw)
        shape=shape.fuse(block(xl,wall_y+wall_depth-2.2,bottom+4,
                               lipw,2.2,s.pcb_length-9))
    # Two small bottom stops with central microUSB clearance
    for xx in (-internal_w/2, internal_w/2-7):
        shape=shape.fuse(block(xx,front_y,bottom,7,wall_depth,2.2))
    # x-side pitch tab with structural web back to tray's rear.
    # Face/movement path is symmetric in either chassis corner via base yaw.
    dist_y=-17.0-s.arm_reach
    ear_x=7.3  # 0.3 mm lateral clearance to 14 mm arm beam; lug ends at x=6
    ear_y=dist_y
    ear_z=9.5
    tab=cyl_x(8,4.2,ear_x,ear_y,ear_z)
    web=block(ear_x,rear_y+1,ear_z-5.0,4.2,ear_y-(rear_y+1)+1,10.0)
    shape=shape.fuse(tab).fuse(web)
    shape=shape.cut(cyl_x(s.pivot_hole_d/2,6,ear_x-1,ear_y,ear_z))
    # Three optional 3mm holes for zip-tie/cable strain relief near lower rear.
    for x in (-10,-3,4):
        shape=shape.cut(cyl_y(1.5,s.cradle_rear_thickness+2,x,rear_y-1,bottom+5))
    return shape.clean()

def v5_key(s, length=None):
    # The SAME cavity polyline and 2D offset semantics as recovered V5 OpenSCAD.
    # It is a FIT TEST/reference key, NOT the main structural attachment.
    length=s.key_length if length is None else length
    pts=[(0,-s.slot_mouth/2),
         (s.slot_lip_depth,-s.slot_mouth/2),
         (s.slot_lip_depth,-s.slot_head_height/2),
         (s.slot_head_flat_end,-s.slot_head_height/2),
         (s.slot_depth,-s.slot_inner_flat/2),
         (s.slot_depth,s.slot_inner_flat/2),
         (s.slot_head_flat_end,s.slot_head_height/2),
         (s.slot_lip_depth,s.slot_head_height/2),
         (s.slot_lip_depth,s.slot_mouth/2),
         (0,s.slot_mouth/2)]
    head=Polygon(pts).buffer(-s.slide_fit,join_style=2)
    # Protrusion -0.20mm means stem starts INBOARD at U=0.20.
    stem=polybox(s.tongue_recess,
                 -(s.slot_mouth-2*s.slide_fit)/2,
                 s.slot_lip_depth+s.slot_stem_overlap,
                 (s.slot_mouth-2*s.slide_fit)/2)
    union=unary_union([head,stem])
    assert union.is_valid and union.geom_type == 'Polygon'
    coords=list(union.exterior.coords)[:-1]
    return (cq.Workplane('XY').polyline(coords).close().extrude(length)
            .translate((0,0,-length/2)).val())

def board_reference(s):
    # Translucent PCB physical ENVELOPE only. NOT an exact MB PCB CAD model.
    x=s.pcb_width/2
    # Both board interfaces + lens height are unverified; model as an envelope.
    b=block(-x,-92,8,s.pcb_width,1.6,s.pcb_length)
    mb=block(-x,-91,8,s.pcb_width,s.cam_mb_stack_depth-3, s.pcb_length)
    lens=cyl_y(3,5,0,-77,29)
    return b.fuse(mb).fuse(lens)

def export_step_stl(shape, name, output):
    (output/'stl').mkdir(parents=True,exist_ok=True)
    (output/'step').mkdir(parents=True,exist_ok=True)
    cq.exporters.export(shape,str(output/'step'/f'{name}.step'))
    cq.exporters.export(shape,str(output/'stl'/f'{name}.stl'),tolerance=0.09,angularTolerance=0.12)

def assembly(s,yaw,pitch):
    # Keep printable parts in original CAD coordinates; only STEP assembly is posed.
    base=rail_base(s)
    arm=swivel_arm(s)
    tray=camera_cradle(s)
    arm_pose=arm
    tray_pose=tray
    axis_a=(0,-17-s.arm_reach,9.5)
    axis_b=(1,-17-s.arm_reach,9.5)
    tray_pose=tray_pose.rotate(axis_a,axis_b,pitch)
    if yaw:
        arm_pose=arm_pose.rotate((0,-17,0),(0,-17,1),yaw)
        tray_pose=tray_pose.rotate((0,-17,0),(0,-17,1),yaw)
    a=cq.Assembly(name='ESP32_CAM_MB_FRAME_MONITOR_V001')
    a.add(base,name='stationary_m5_mount',color=cq.Color(0.29,0.37,0.43))
    a.add(arm_pose,name='yaw_swivel_arm_m4',color=cq.Color(0.9,0.47,0.16))
    a.add(tray_pose,name='camera_cradle_pitch_m4',color=cq.Color(0.22,0.64,0.82))
    return a, [('base',base),('arm',arm),('cradle',tray)]

def plot_preview(output,parts,s,yaw,pitch):
    # Real STL mesh projections, not synthetic imagery.
    import numpy as np
    import trimesh
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    colors={'base':'#60788a','arm':'#ea8b4a','cradle':'#43a7c6','key':'#e3b45e'}
    def plot_mesh(ax,mesh,color,opacity=1.0,faces_target=8500):
        import matplotlib.colors as mc
        V=mesh.vertices
        F=mesh.faces
        face_ids=np.arange(0,len(F),max(1,int(math.ceil(len(F)/faces_target))))
        F=F[face_ids]
        normal=mesh.face_normals[face_ids]
        light=np.array([0.5,-0.7,1.2]);light=light/np.linalg.norm(light)
        shade=np.clip(.48+.52*np.maximum(0,normal@light),.32,1.0)
        base_rgb=np.array(mc.to_rgb(color))
        rgba=np.column_stack((np.clip(base_rgb[None,:]*shade[:,None],0,1),
                              np.ones(len(F))*opacity))
        c=Poly3DCollection(V[F],facecolors=rgba,edgecolors='none')
        ax.add_collection3d(c)
    def fit(ax,bounds,span=1.12):
        # uniform extents per axis to avoid distortions
        minv,maxv=np.array(bounds)
        center=(minv+maxv)/2
        radius=max(maxv-minv)*span/2
        ax.set_xlim(center[0]-radius,center[0]+radius)
        ax.set_ylim(center[1]-radius,center[1]+radius)
        ax.set_zlim(center[2]-radius,center[2]+radius)
        ax.set_axis_off()
        ax.set_box_aspect([1,1,1])
    meshes={name:trimesh.load(output/'stl'/f'{name}.stl',force='mesh') for name,_ in parts}
    # STL exports contain printable unposed parts. Transform COPIES for assembled view.
    posed={name:m.copy() for name,m in meshes.items()}
    dist_y=-17-s.arm_reach
    pitchmat=trimesh.transformations.rotation_matrix(math.radians(pitch),[1,0,0],point=[0,dist_y,9.5])
    yawmat=trimesh.transformations.rotation_matrix(math.radians(yaw),[0,0,1],point=[0,-17,0])
    posed['cradle'].apply_transform(pitchmat)
    posed['cradle'].apply_transform(yawmat)
    posed['arm'].apply_transform(yawmat)
    arr=np.vstack([m.bounds for m in posed.values()]); bounds=[arr.min(0),arr.max(0)]
    fig=plt.figure(figsize=(14,7.5),facecolor='#f8fafc')
    for i,(azi,ele,title) in enumerate([(38,22,'FRONT CORNER / ASSEMBLED'),(-142,28,'REAR / MOUNT AND USB ACCESS')]):
        ax=fig.add_subplot(1,2,i+1,projection='3d')
        for name,m in posed.items():plot_mesh(ax,m,colors[name])
        fit(ax,bounds)
        ax.view_init(elev=ele,azim=azi,vertical_axis='z')
        ax.set_title(title,pad=2,fontweight='bold',fontsize=12,color='#273846')
    fig.suptitle('ESP32-CAM-MB | PARAMETRIC FRAME MONITOR V001',fontsize=16,fontweight='bold',color='#1f3240')
    fig.text(.5,.035, f'Assembled CAD-derived STL meshes  •  arm {s.arm_reach:.0f} mm  •  yaw {yaw:+g}°  •  pitch {pitch:+g}°  •  mm',ha='center',fontsize=10,color='#43576a')
    fig.tight_layout(rect=(0,.07,1,.95))
    fig.savefig(output/'previews'/'assembled.png',dpi=170)
    plt.close(fig)
    fig=plt.figure(figsize=(14,5.1),facecolor='#f8fafc')
    for i,(name,m) in enumerate(meshes.items()):
        ax=fig.add_subplot(1,3,i+1,projection='3d')
        plot_mesh(ax,m,colors[name]);fit(ax,m.bounds,1.20)
        ax.view_init(elev=25,azim=42)
        ax.set_title({'base':'01  FRAME PLATE / M5','arm':'02  YAW ARM / M4','cradle':'03  CAMERA CRADLE / M4'}[name],fontsize=10,fontweight='bold')
    fig.suptitle('EXPLODED PARTS — ACTUAL GEOMETRY',fontweight='bold',fontsize=15,color='#1f3240')
    fig.tight_layout(rect=(0,.02,1,.92))
    fig.savefig(output/'previews'/'individual_parts.png',dpi=170)
    plt.close(fig)
    # T-slot key profile and 4040 cavity from recovered V5
    key=v5_key(s,s.fit_key_test_length)
    export_step_stl(key,'tslot_4040_key_fit_coupon',output)
    km=trimesh.load(output/'stl'/'tslot_4040_key_fit_coupon.stl',force='mesh')
    fig=plt.figure(figsize=(8,6),facecolor='#f8fafc')
    ax=fig.add_subplot(111,projection='3d');plot_mesh(ax,km,colors['key']);fit(ax,km.bounds,1.35)
    ax.view_init(elev=26,azim=47)
    fig.suptitle('RECOVERED 4040 T-SLOT KEY — FIT COUPON',fontweight='bold',color='#1f3240')
    fig.text(.5,.06,f'Profile: 6.20 mouth / 10.50 internal / 6.80 deep  •  {s.slot_clearance:.2f} mm fit clearance per side  •  0.20 mm face recess',ha='center',fontsize=9,color='#43576a')
    fig.tight_layout(rect=(0,.10,1,.92))
    fig.savefig(output/'previews'/'tslot_fit_coupon.png',dpi=170)
    plt.close(fig)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--yaw',type=float,default=-20.0)
    parser.add_argument('--pitch',type=float,default=10.0)
    p=parser.parse_args();output=Path(p.out).resolve();(output/'previews').mkdir(parents=True,exist_ok=True)
    a,parts=assembly(S,p.yaw,p.pitch)
    for name,shape in parts:export_step_stl(shape,name,output)
    # 4040 reference's face has TWO slots on 20 mm centers, NOT a centered slot.
    for offset,name in ((-10,'base_4040_slot_left'),(10,'base_4040_slot_right')):
        export_step_stl(rail_base(replace(S,mount_slot_x=offset)),name,output)
    a4040,_=assembly(replace(S,mount_slot_x=10),p.yaw,p.pitch)
    a4040.save(str(output/'step'/'assembled_4040_rightslot.step'),exportType='STEP')
    a.save(str(output/'step'/'assembled_adjusted.step'),exportType='STEP')
    # Printable solids remain untransformed, regardless of assembly articulation.
    plot_preview(output,parts,S,p.yaw,p.pitch)
    with (output/'docs'/'parameters.json').open('w') as f:json.dump({'spec':asdict(S),'preview_yaw_deg':p.yaw,'preview_pitch_deg':p.pitch,'unit':'mm'},f,indent=2)
    for name,shape in parts:
        if not shape.isValid():raise RuntimeError(f'{name} invalid BREP')
        solids=shape.Solids()
        print(name,'valid=',shape.isValid(),'solids=',len(solids),'volume=',round(shape.Volume(),1))
    print('Created:',output)
if __name__=='__main__':main()
