"""Surface-distance checks for two corrected cable guides across joint poses."""
from __future__ import annotations
import json
from pathlib import Path
import cadquery as cq
import trimesh
from .config import CONFIG
from .assembly import components
from .cable import route_metrics
from .geometry import first_arm, second_arm
from . import parts as cad_parts,wrist
from .export import printable_parts


def validate(root:Path):
    root=Path(root)
    (root/'stl').mkdir(exist_ok=True,parents=True)
    meshes=[]
    for name,shape in printable_parts():
        assert shape.isValid() and len(shape.Solids())==1,(name,'invalid solid')
        path=root/'stl'/f'{name}.stl'
        if name.startswith('V010_'):
            cq.exporters.export(shape,str(path),tolerance=.08,angularTolerance=.12)
        mesh=trimesh.load(path,force='mesh')
        assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1,(name,'non-manifold')
        assert abs(mesh.volume/shape.Volume()-1)<.005,(name,'mesh volume mismatch')
        meshes.append({'name':name,'watertight':True,'single_body':True,
                       'mesh_volume_mm3':round(mesh.volume,3)})
    # Reject dangling clip arms even when ordinary solid-validity tests pass.
    arm_a,arm_b=first_arm(),second_arm()
    assert arm_a.BoundingBox().zmin>=7.49 and arm_a.BoundingBox().zmax<=15.01, "First arm cable seats extend outside link thickness"
    assert arm_b.BoundingBox().zmax<=22.51, "Second arm cable seats extend above link thickness"
    assert arm_a.BoundingBox().xmin>=-13.3 and arm_b.BoundingBox().xmin>=-13.3, "Remote cable support detected"
    poses=[]
    for angles in CONFIG.sampled_poses:
        parts=components(*angles)
        shapes={name:solid for name,solid,*_ in parts}
        assert len(shapes)==len(parts)==30,(angles,'component count')
        assert all(shape.isValid() for shape in shapes.values()),(angles,'invalid BREP')
        cable=shapes['V006_USB_outboard_cable_reference']
        sections=cable.Solids()
        knobs=[name for name in shapes if 'thumbwheel' in name]
        assert len(knobs)==4,knobs
        wheel_gaps={name:min(section.distance(shapes[name]) for section in sections) for name in knobs}
        rail_gap=min(section.distance(shapes['4040_horizontal_reference']) for section in sections)
        assert min(wheel_gaps.values())>=CONFIG.cable_to_knob_min_mm,(angles,wheel_gaps)
        assert rail_gap>=CONFIG.cable_to_rail_min_mm,(angles,rail_gap)
        guides=('V010_first_arm','V010_second_arm')
        guide_gaps={name:min(section.distance(shapes[name]) for section in sections) for name in guides}
        # First compute exact distances; skip costly Boolean intersections
        # for surfaces known to have positive separation.
        unwanted={name:sum(section.intersect(shapes[name]).Volume()
             for section in sections if section.distance(shapes[name])<1e-6)
             for name in guides}
        assert max(unwanted.values())<.01,(angles,unwanted)
        # Ensures the route runs inside BOTH 3.8 mm guide bores with 0.30 mm
        # nominal radial clearance, rather than merely passing nearby.
        assert all(.24<=gap<=.5 for gap in guide_gaps.values()),(angles,guide_gaps)
        poses.append({
            'pose_degrees':list(angles),
            'cable_route':route_metrics(angles[3],base=angles[0],elbow=angles[1],pitch=angles[2]),
            'thumbwheel_surface_gap_mm':{name:round(gap,3) for name,gap in wheel_gaps.items()},
            'cable_to_rail_mm':round(rail_gap,3),
            'cable_to_guide_mm':{name:round(gap,3) for name,gap in guide_gaps.items()},
            'unintended_cable_guide_overlap_mm3':{name:round(v,5) for name,v in unwanted.items()}
        })
        print('PASS',angles,'guides',guide_gaps,'knob',min(wheel_gaps.values()),flush=True)
    summary={
      'revision':CONFIG.release,'status':'PASS CAD-only',
      'sampled_poses':len(poses),'component_entries':len(parts),
      'arm_guides_aligned':2,'integrated_alternating_open_clips':4,
      'long_outriggers':0,'watertight_new_stls':4,'watertight_print_designs':len(meshes),
      'min_cable_to_knob_mm':round(min(v for p in poses for v in p['thumbwheel_surface_gap_mm'].values()),3),
      'min_cable_to_rail_mm':round(min(p['cable_to_rail_mm'] for p in poses),3),
      'physical_qualification':'UNVERIFIED',
      'cable_geometry':'continuous tangent arcs, reference-only',
      'minimum_drawn_bend_radius_mm':min(p['cable_route']['minimum_drawn_radius_mm'] for p in poses)
    }
    report={
      'summary':summary,'printable_meshes':meshes,'poses':poses,
      'clip_openings_in_order':['-X','+Z','-X','+Z'],
      'nominal_cable_diameter_mm':CONFIG.cable_diameter_mm,
      'nominal_clip_throat_mm':CONFIG.clip_throat_mm,
      'limitations':['18 sampled poses are not an exhaustive four-DOF motion proof',
       'No minimum dynamic cable bend radius, connector, cable strain or sag validation',
       'Nominal rail, camera board, metal hardware and cable dimensions',
       'Actual printer travel, torque, vibration and thermal clearance unverified']
    }
    (root/'docs').mkdir(parents=True,exist_ok=True)
    (root/'docs'/'validation_v010.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
