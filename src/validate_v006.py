#!/usr/bin/env python3
"""V006 CAD regression: four thumbwheels, wrist and nominal cable surface gaps."""
from pathlib import Path
import json
import trimesh
import build_v006 as v

POSES=[
 (30,-30,12,0),(20,-30,12,-20),(20,-30,12,20),
 (40,-30,12,-20),(40,-30,12,20),
 (30,-40,12,-20),(30,-40,12,20),
 (30,-20,12,-20),(30,-20,12,20),
 (30,-30,0,-20),(30,-30,0,20),
 (30,-30,25,-20),(30,-30,25,20)
]

def validate():
    results=[]
    (v.ROOT/'docs').mkdir(parents=True,exist_ok=True)
    (v.ROOT/'stl').mkdir(parents=True,exist_ok=True)
    for name,shape in [('V006_wrist_adapter',v.adapter()),('V006_camera_shell',v.shell())]:
        assert shape.isValid() and len(shape.Solids())==1,name
        path=v.ROOT/'stl'/f'{name}.stl'
        if not path.exists():
            v.cq.exporters.export(shape,str(path),tolerance=.08,angularTolerance=.12)
        mesh=trimesh.load(path,force='mesh')
        assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1,name
        assert abs(mesh.volume/shape.Volume()-1)*100 < 0.5,name
    for base,elbow,pitch,wrist in POSES:
        parts=v.components(base,elbow,pitch,wrist)
        solids={n:sh for n,sh,col,kind in parts}
        assert len(parts)==len(solids)==30
        assert all(sh.isValid() for n,sh,col,kind in parts)
        cable=solids['V006_USB_outboard_cable_reference']
        knobs=[n for n in solids if 'thumbwheel' in n]
        assert len(knobs)==4,knobs
        gaps={n:min(section.distance(solids[n]) for section in cable.Solids()) for n in knobs}
        neighbors={
          '4040_rail':solids['4040_horizontal_reference'],
          'camera_shell':solids['V006_camera_shell'],
          'wrist_adapter':solids['V006_wrist_adapter'],
          'second_arm':solids['V004_second_arm'],
        }
        gaps_other={n:min(section.distance(sh) for section in cable.Solids())
                    for n,sh in neighbors.items()}
        assert min(gaps.values())>=v.S.min_knob_gap_mm,(base,elbow,pitch,wrist,gaps)
        assert min(gaps_other.values())>=v.S.min_rigid_gap_mm,(base,elbow,pitch,wrist,gaps_other)
        pairs=[
         ('4040_horizontal_reference','V006_camera_shell'),
         ('4040_horizontal_reference','V006_wrist_adapter'),
         ('V004_second_arm','V006_wrist_adapter'),
         ('V006_wrist_adapter','V006_camera_shell'),
         ('V006_camera_shell','V006_camera_bezel'),
         ('V006_camera_shell','ESP32_CAM_MB_provisional_envelope'),
         ('V006_camera_bezel','ESP32_CAM_MB_provisional_envelope'),
         ('M4_thumbwheel_wrist','V006_camera_shell')
        ]
        inter={a+' | '+b:solids[a].intersect(solids[b]).Volume() for a,b in pairs}
        assert max(inter.values())<0.01,(base,elbow,pitch,wrist,inter)
        results.append({'base_deg':base,'elbow_deg':elbow,'pitch_deg':pitch,'wrist_deg':wrist,
                        'thumbwheel_clearance_mm':{k:round(x,3) for k,x in gaps.items()},
                        'other_cable_clearance_mm':{k:round(x,3) for k,x in gaps_other.items()}})
        print('PASS pose',base,elbow,pitch,wrist,'knob mm',round(min(gaps.values()),3),flush=True)
    summary={'revision':'V006','result':'PASS CAD-only',
             'tested_poses':len(results),'assembly_components':30,
             'thumbwheel_count':4,'printable_new_STLs_watertight':2,
             'min_cable_to_knob_mm':round(min(x for r in results for x in r['thumbwheel_clearance_mm'].values()),3),
             'min_cable_to_rail_mm':round(min(r['other_cable_clearance_mm']['4040_rail'] for r in results),3),
             'physical_fit':'UNVERIFIED',
             'limitations':['Actual USB cable bend radius and connector boot unmeasured',
                            'No dynamic cable sag, strain relief or full-motion continuous sweep',
                            'Rail and ESP32-CAM-MB geometry provisional',
                            'No torque, heat, fatigue, printer travel or vibration qualification']}
    (v.ROOT/'docs'/'validation_v006.json').write_text(json.dumps({'summary':summary,'poses':results},indent=2))
    print(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__':validate()
