"""Current assembly STEP/STL and machine-readable manifest, from one model."""
from pathlib import Path
import json
from dataclasses import asdict
import cadquery as cq
from .config import CONFIG
from .assembly import components
from .geometry import first_arm,second_arm
from . import parts as cad_parts,wrist


def printable_parts():
    """Every unique printed design used by the active assembly."""
    return [('V010_first_arm',first_arm()),('V010_second_arm',second_arm()),
            ('V010_scalloped_thumbwheel',cad_parts.thumbwheel()),
            ('V010_relieved_camera_shell',wrist.shell()),
            ('V010_wrist_adapter',wrist.adapter()),
            ('V004_removable_camera_bezel',cad_parts.camera_bezel()),
            ('V004_mount_plate',cad_parts.base_plate()),
            ('V004_recessed_alignment_key',cad_parts.alignment_key())]


def build(root:Path):
    root=Path(root)
    for folder in ('step','stl','docs','previews'):
        (root/folder).mkdir(exist_ok=True,parents=True)
    for name,shape in printable_parts():
        if not name.startswith("V010_"): continue
        assert shape.isValid() and len(shape.Solids())==1,name
        cq.exporters.export(shape,str(root/'step'/f'{name}.step'))
        cq.exporters.export(shape,str(root/'stl'/f'{name}.stl'),tolerance=.08,angularTolerance=.12)
    parts=components()
    assembly=cq.Assembly(name='ESP32_CAM_MB_4040_UNIFIED_V010')
    for name,shape,color,kind in parts:
        assert shape.isValid(),name
        assembly.add(shape,name=name,color=cq.Color(*color))
    assembly.save(str(root/'step'/'COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V010.step'),exportType='STEP')
    manifest={
      'revision':CONFIG.release,'generator':'src/build.py',
      'parameters':asdict(CONFIG),'component_count':len(parts),
      'components':[{'name':name,'kind':kind} for name,shape,color,kind in parts],
      'new_printable':['V010_first_arm','V010_second_arm','V010_scalloped_thumbwheel','V010_relieved_camera_shell','V010_wrist_adapter'],
      'base':'V006 four-joint articulated wrist; historical versioned scripts not imported'
    }
    (root/'docs'/'manifest_v010.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return parts
