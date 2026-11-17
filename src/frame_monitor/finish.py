"""Selective, fail-fast V010 print geometry finishing. Dimensions in millimeters.

Functional M4/M5 contact faces, T-slot datums and cable U-clip throats excluded.
"""
from math import isclose

def _blend(s,label,edges,kind,r,count):
    if len(edges)!=count:
        raise ValueError(f'{label}: expected {count} edges, got {len(edges)}')
    out=s.fillet(r,edges) if kind=='fillet' else s.chamfer(r,None,edges)
    if not out.isValid() or len(out.Solids())!=1:
        raise ValueError(f'{label}: invalid {kind} with {r} mm')
    return out.clean()

def finish_arm(s):
    e=[x for x in s.Edges() if x.geomType()=='LINE'
       and 7.49<x.BoundingBox().zlen<7.51
       and any(isclose(abs(x.Center().x),q,abs_tol=.005) for q in (5.0,2.2))]
    s=_blend(s,'six triangular web corners',e,'fillet',.70,6)
    e=[x for x in s.Edges() if x.geomType()=='LINE'
       and 7.49<x.BoundingBox().zlen<7.51 and 8.99<x.Center().x<9.01]
    return _blend(s,'two tapered external corners',e,'fillet',1.0,2)

def finish_knob(s):
    e=[x for x in s.Edges() if x.geomType()=='LINE'
       and abs(x.Center().z-7)<.001 and x.BoundingBox().zlen<.001
       and x.Length()<3.4 and x.Center().x**2+x.Center().y**2>100]
    return _blend(s,'twelve grip-facet edges',e,'chamfer',.80,12)

def finish_shell(s):
    e=[x for x in s.Edges() if x.geomType()=='LINE'
       and x.BoundingBox().zlen>50.9 and abs(x.Center().x)>17.9
       and x.BoundingBox().xlen<.001 and x.BoundingBox().ylen<.001]
    return _blend(s,'four shell exterior corners',e,'fillet',.90,4)

def finish_bezel(s):
    e=[x for x in s.Edges() if x.geomType()=='LINE'
       and x.BoundingBox().zlen>50.9 and abs(x.Center().x)>17.9
       and abs(x.Center().y+89)<.001]
    return _blend(s,'front bezel edges',e,'chamfer',.30,2)

def finish_mount(s):
    e=[x for x in s.Edges() if x.geomType()=='LINE'
       and x.BoundingBox().zlen>45 and x.BoundingBox().xlen<.001
       and x.BoundingBox().ylen<.001]
    return _blend(s,'mounting plate external edges',e,'chamfer',.30,4)

def finish_wrist(s):
    e=[x for x in s.Edges() if x.geomType()=='LINE'
       and x.BoundingBox().ylen>30 and x.BoundingBox().xlen<.001
       and x.BoundingBox().zlen<.001 and -6.01<x.Center().z<-5.99]
    return _blend(s,'wrist bridge upper edges',e,'fillet',.70,2)
