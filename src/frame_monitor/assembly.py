"""Single active four-joint assembly, replacing BOTH old arm cable saddles."""
from . import parts as b4
from . import wrist as legacy
from .geometry import first_arm, second_arm
from .cable import cable_reference


def _install(shape,pose):
    routine=getattr(legacy,'installed',None) or legacy.install
    return routine(shape,pose)


def components(base=30,elbow=-30,pitch=12,wrist=0,with_cable=True):
    previous=(b4.P.yaw_deg,b4.P.elbow_deg,b4.P.camera_pitch_deg)
    try:
        if 'base_deg' in legacy.components.__code__.co_varnames:
            parts=legacy.components(base_deg=base,elbow_deg=elbow,
                                    pitch_deg=pitch,wrist_deg=wrist,with_cable=with_cable)
        else:
            parts=legacy.components(base,elbow,pitch,wrist)
        for key,value in zip(('yaw_deg','elbow_deg','camera_pitch_deg'),(base,elbow,pitch)):
            object.__setattr__(b4.P,key,value)
        replacements={'V004_first_arm':('V009_first_arm',first_arm(),b4.pose_one),
                      'V004_second_arm':('V009_second_arm',second_arm(),b4.pose_two)}
        result=[]
        for name,shape,color,kind in parts:
            if name=='V006_USB_outboard_cable_reference':
                shape=cable_reference(wrist)
            if name in replacements:
                name,local,pose=replacements[name]
                shape=_install(local,pose)
            result.append((name,shape,color,kind))
        return result
    finally:
        for key,value in zip(('yaw_deg','elbow_deg','camera_pitch_deg'),previous):
            object.__setattr__(b4.P,key,value)
