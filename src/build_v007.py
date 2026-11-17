#!/usr/bin/env python3
"""V007 candidate: align both arm cable saddles with the outboard USB route.

Keep V006 released exports immutable until STEP/STL/renders and pose checks are
regenerated. Coordinates are local before horizontal/left-face transforms.
"""
import cadquery as cq
import build_v004 as b4
import build_v006 as v6
from v001_mount import block, cyl_x, cyl_y, cyl_z

CABLE_X = -27.0
SADDLE_BORE_R = 1.9
SADDLE_WIDTH = 7.0
SADDLE_LENGTH = 8.0

def _outboard_saddle(arm, y, z):
    """Add a supported, through-bored cable guide on the knob-side link edge."""
    # Support extends from the arm's -X side to the outboard guide.
    # The cable center is aligned with V006's reference centerline at X=-27.
    support = block(CABLE_X-3.5, y, z-3.5, 24.0, SADDLE_LENGTH, 7.0)
    arm = arm.fuse(support)
    bore = cyl_y(SADDLE_BORE_R, SADDLE_LENGTH+2,
                 CABLE_X, y-1, z)
    return arm.cut(bore).clean()

def first_arm():
    # Identical primary link/joint geometry to V004; replace ONLY cable saddle.
    a=block(-7,-52,7.5,14,35,6)
    for y in (-17,-52):
        a=a.fuse(cyl_z(7.0,6,0,y,7.5))
        a=a.cut(cyl_z(2.15,9,0,y,6))
    a=a.cut(b4.hex_pocket(7.2,3.3,(0,-52,7.45)))
    return _outboard_saddle(a,-39,19)

def second_arm():
    a=block(-7,-87,15,14,35,6)
    a=a.fuse(cyl_z(7.0,6,0,-52,15))
    a=a.cut(cyl_z(2.15,8,0,-52,14))
    a=a.fuse(block(-6,-90,-12,12,8,31))
    a=a.fuse(cyl_x(7.5,12,-6,-87,-12))
    a=a.cut(cyl_x(2.15,14,-7,-87,-12))
    return _outboard_saddle(a,-74,27)

def components(*args,**kwargs):
    """Replace both inherited V004 links without disturbing the joint poses."""
    base=kwargs.get('base',args[0] if len(args)>0 else None)
    elbow=kwargs.get('elbow',args[1] if len(args)>1 else None)
    pitch=kwargs.get('pitch',args[2] if len(args)>2 else None)
    # Preserve the exact V006 transform chain.
    old=(b4.P.yaw_deg,b4.P.elbow_deg,b4.P.camera_pitch_deg)
    for k,val in [('yaw_deg',v6.S.base_yaw_deg if base is None else base),
                  ('elbow_deg',v6.S.elbow_deg if elbow is None else elbow),
                  ('camera_pitch_deg',v6.S.pitch_deg if pitch is None else pitch)]:
        object.__setattr__(b4.P,k,val)
    try:
        parts=v6.components(*args,**kwargs)
        replacements={'V004_first_arm':first_arm(),
                      'V004_second_arm':second_arm()}
        result=[]
        for name,solid,color,kind in parts:
            if name in replacements:
                pose=b4.pose_one if name=='V004_first_arm' else b4.pose_two
                solid=v6.install(replacements[name],pose)
                name=name.replace('V004_','V007_')
            result.append((name,solid,color,kind))
        return result
    finally:
        for k,val in zip(('yaw_deg','elbow_deg','camera_pitch_deg'),old):
            object.__setattr__(b4.P,k,val)

def build():
    root=v6.ROOT
    for folder in ('stl','step'):
        (root/folder).mkdir(parents=True,exist_ok=True)
    for name,shape in [('V007_first_arm',first_arm()),('V007_second_arm',second_arm())]:
        assert shape.isValid() and len(shape.Solids())==1, name
        cq.exporters.export(shape,str(root/'stl'/f'{name}.stl'),tolerance=.08,angularTolerance=.12)
        cq.exporters.export(shape,str(root/'step'/f'{name}.step'))
    assembly=cq.Assembly(name='ESP32_CAM_MB_V007_CABLE_GUIDES_CANDIDATE')
    for name,shape,color,kind in components():
        assert shape.isValid(),name
        assembly.add(shape,name=name,color=cq.Color(*color))
    assembly.save(str(root/'step'/'COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V007.step'),exportType='STEP')

if __name__=='__main__':
    build()
