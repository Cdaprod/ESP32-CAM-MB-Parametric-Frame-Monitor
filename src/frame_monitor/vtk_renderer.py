#!/usr/bin/env python3
"""Generate images from ACTUAL assembly BREP-tessellated triangles using VTK.
No generative image model is used. On Linux run under `xvfb-run -a python src/render_assembly.py`.
"""
from pathlib import Path
import math, json
import vtk
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from .rail import ROOT, assemble_components, A,V,slot_poly,slot_transform

size=(1760,1180)

def _font(size,bold=False):
    fn=('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
        else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(fn,size)

def vtk_actor(solid,color,opacity=1,wire=False):
    vertices,triangles=solid.tessellate(0.20,0.16)
    pts=vtk.vtkPoints();pts.SetNumberOfPoints(len(vertices))
    for i,v in enumerate(vertices): pts.SetPoint(i,v.x,v.y,v.z)
    cells=vtk.vtkCellArray()
    for tri in triangles:
        t=vtk.vtkTriangle()
        for j,k in enumerate(tri):t.GetPointIds().SetId(j,k)
        cells.InsertNextCell(t)
    poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SetFeatureAngle(65);normals.SplittingOff();normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    actor=vtk.vtkActor();actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color);actor.GetProperty().SetOpacity(opacity)
    actor.GetProperty().SetSpecular(.30 if color[0]>.5 else .17)
    actor.GetProperty().SetSpecularPower(27)
    actor.GetProperty().SetAmbient(.27);actor.GetProperty().SetDiffuse(.78)
    if wire:actor.GetProperty().EdgeVisibilityOn()
    return actor

def camera_scene(comps,where,title,subtitle,camera,look,opacity={},explode=False):
    ren=vtk.vtkRenderer();ren.GradientBackgroundOn()
    ren.SetBackground(0.955,0.968,0.982);ren.SetBackground2(0.790,0.832,0.883)
    win=vtk.vtkRenderWindow();win.AddRenderer(ren);win.SetSize(*size)
    win.SetMultiSamples(8);win.SetOffScreenRendering(1)
    named={}
    for n,shape,c,kind in comps:
        if explode:
            dx=0
            if 'profile_matched_key' in n:dx=14
            elif 'M5x8_' in n:dx=67
            elif '4040_reference_extrusion' in n:dx=0
            else:dx=38
            shape=shape.translate((dx,0,0))
        factor=opacity.get(n,1)
        if factor==0:continue
        a=vtk_actor(shape,c,factor)
        ren.AddActor(a);named[n]=a
    cam=ren.GetActiveCamera();cam.SetFocalPoint(*look);cam.SetPosition(*camera)
    cam.SetViewUp(0,0,1);cam.ParallelProjectionOn()
    cam.SetParallelScale(107 if explode else (107 if 'ASSEMBLY' in title else 54))
    light=vtk.vtkLight();light.SetPosition(160,-180,250);light.SetFocalPoint(35,0,0);light.SetIntensity(.8);ren.AddLight(light)
    light2=vtk.vtkLight();light2.SetPosition(-150,100,90);light2.SetFocalPoint(35,0,0);light2.SetIntensity(.5);ren.AddLight(light2)
    ren.SetUseDepthPeeling(True);ren.SetMaximumNumberOfPeels(40);ren.SetOcclusionRatio(.0)
    win.SetAlphaBitPlanes(True)
    win.Render()
    filt=vtk.vtkWindowToImageFilter();filt.SetInput(win);filt.SetInputBufferTypeToRGB();filt.ReadFrontBufferOff();filt.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(where));writer.SetInputConnection(filt.GetOutputPort());writer.Write()
    ren.RemoveAllViewProps();win.Finalize()
    annotate(where,title,subtitle)

def annotate(path,title,subtitle):
    im=Image.open(path).convert('RGB')
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((38,30,1180,137),radius=16,fill=(16,30,45))
    d.text((64,45),title,font=_font(32,True),fill=(246,249,253))
    d.text((64,98),subtitle,font=_font(18),fill=(176,201,218))
    d.rounded_rectangle((40,1083,1690,1139),radius=14,fill=(19,32,44))
    d.text((60,1097),'4040 PHOTO-DERIVED REFERENCE    •    V5 T-SLOT KEY    •    V001 MONITOR / V002 FIT CORRECTION    •    mm',
           font=_font(17,False),fill=(225,236,242))
    im.save(path)

def profile_figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as Patch,Rectangle,Circle
    from shapely.geometry import Polygon,box
    from shapely.ops import unary_union
    fig,axes=plt.subplots(1,2,figsize=(15,6.5),facecolor='#edf1f5')
    ax=axes[0];ax.set_facecolor('#edf1f5')
    ax.add_patch(Rectangle((-20,-20),40,40,facecolor='#798897',edgecolor='#36495b',linewidth=1.6))
    for face in ['right','left','top','bottom']:
      for c in [-10,10]:
        pts=[slot_transform(face,c,pt) for pt in slot_poly()]
        ax.add_patch(Patch(pts,closed=True,facecolor='#edf1f5',edgecolor='#37424a',lw=1))
    for x in [-10,10]:
      for y in [-10,10]:ax.add_patch(Circle((x,y),2.25,facecolor='#edf1f5',edgecolor='#36495b'))
    cross=[(-3,18),(3,18),(3,15),(6,12),(6,8),(8,6),(12,6),(15,3),
            (18,3),(18,-3),(15,-3),(12,-6),(8,-6),(6,-8),(6,-12),
            (3,-15),(3,-18),(-3,-18),(-3,-15),(-6,-12),(-6,-8),(-8,-6),
            (-12,-6),(-15,-3),(-18,-3),(-18,3),(-15,3),(-12,6),
            (-8,6),(-6,8),(-6,12),(-3,15)]
    ax.add_patch(Patch(cross,facecolor='#edf1f5',edgecolor='#36495b'))
    ax.plot([20],[10],'o',color='#f08a26',ms=8)
    ax.annotate('Active slot Y = +10',xy=(20,10),xytext=(36,14),color='#a75209',fontsize=12,
                arrowprops=dict(arrowstyle='->',color='#ce6a13',lw=2))
    ax.set_xlim(-27,71);ax.set_ylim(-31,31);ax.set_aspect('equal');ax.grid(alpha=.12)
    ax.set_title('RECOVERED 4040 SECTION  •  X-Y',fontsize=14,fontweight='bold',pad=18)
    ax.annotate('',xy=(-20,-24),xytext=(20,-24),arrowprops=dict(arrowstyle='<->',color='#303c49',lw=1.6))
    ax.text(0,-27,'40 mm',ha='center',fontsize=12,color='#303c49')
    ax=axes[1];ax.set_facecolor('#edf1f5')
    # x right-face -> global x = 20 - U; to simplify plot use U inward, V across slot.
    p=slot_poly()
    ax.add_patch(Rectangle((-3,-8),13,16,facecolor='#7c8996'))
    ax.add_patch(Patch(p,facecolor='#edf1f5',edgecolor='#222f39',lw=2))
    from .primitives import v5_key
    # V5 key polygon is captured parametrically; use XY face from extrusion projection
    from .rail import original_key_with_m5_pilots
    k=v5_key(V,V.key_length)
    # recover precise flat section from the BREP at z=0 by shapely key recipe
    pts=[(0,-V.slot_mouth/2),(V.slot_lip_depth,-V.slot_mouth/2),
         (V.slot_lip_depth,-V.slot_head_height/2),(V.slot_head_flat_end,-V.slot_head_height/2),
         (V.slot_depth,-V.slot_inner_flat/2),(V.slot_depth,V.slot_inner_flat/2),
         (V.slot_head_flat_end,V.slot_head_height/2),(V.slot_lip_depth,V.slot_head_height/2),
         (V.slot_lip_depth,V.slot_mouth/2),(0,V.slot_mouth/2)]
    head=Polygon(pts).buffer(-V.slide_fit,join_style=2)
    stem=box(V.tongue_recess,-(V.slot_mouth-2*V.slide_fit)/2,
             V.slot_lip_depth+V.slot_stem_overlap,(V.slot_mouth-2*V.slide_fit)/2)
    union=unary_union([head,stem])
    ax.add_patch(Patch(list(union.exterior.coords),facecolor='#ef872b',edgecolor='#ac4608',lw=2,alpha=.94))
    ax.axvline(0,color='#315aa5',lw=1.2,ls='--');ax.text(-.6,6.9,'Face',ha='right',color='#315aa5')
    ax.annotate('',xy=(0,-7),xytext=(6.8,-7),arrowprops=dict(arrowstyle='<->',color='#263442',lw=1.4))
    ax.text(3.4,-7.7,'6.80 mm',ha='center',fontsize=11)
    ax.annotate('',xy=(8.4,-5.25),xytext=(8.4,5.25),arrowprops=dict(arrowstyle='<->',color='#263442',lw=1.4))
    ax.text(9,0,'10.50 mm',rotation=90,va='center',fontsize=11)
    ax.text(-3.8,-11.3,'2 × M5 pilot at Z = ±12.7 mm  ·  Ø4.2 mm\n0.18 mm clearance per face  ·  0.20 mm tongue recess',
            fontsize=9.4,color='#303b48',bbox=dict(facecolor='#edf1f5',edgecolor='none',pad=1.5))
    ax.set_xlim(-4.2,12);ax.set_ylim(-12.5,9);ax.set_aspect('equal');ax.grid(alpha=.12)
    ax.set_title('FEMALE SLOT + CAPTURED PRINTED KEY',fontsize=14,fontweight='bold',pad=18)
    for aa in axes:
      for side in ['top','right']:aa.spines[side].set_visible(False)
      aa.tick_params(labelsize=9)
    fig.tight_layout(pad=3)
    fig.savefig(ROOT/'previews'/'4040_slot_fit_section.png',dpi=180,facecolor=fig.get_facecolor());plt.close(fig)

def main():
    comps=assemble_components()
    where=ROOT/'previews'
    camera_scene(comps,where/'assembled_oblique.png',
      'ESP32-CAM-MB  |  COMPLETE 4040 ASSEMBLY',
      '18 solid components · 2 × M5 fasteners · 2 × M4 pivot joints',
      (240,-180,160),(45,4,0))
    translucent={'4040_reference_extrusion':0.28}
    camera_scene(comps,where/'key_and_screws_detail.png',
      '4040 UNDERCUT KEY + M5 FASTENERS',
      'Printed V5 sliding key; Ø4.2 pilot; modelled M5 × 8 cap screws',
      (141,-140,88),(24,7,0),opacity=translucent)
    camera_scene(comps,where/'exploded_assembly.png',
      'COMPONENT PLACEMENT  |  EXPLODED VIEW',
      'Exploded for identification only; assembled STEP retains actual positions',
      (255,-180,170),(53,4,0),explode=True)
    camera_scene(comps,where/'camera_and_pivots.png',
      'DUAL M4 ADJUSTABLE JOINTS + CAMERA CRADLE',
      'M4 × 25 socket bolts · six washers · two hex-locknut envelopes',
      (160,-154,105),(85,7,16),opacity={'4040_reference_extrusion':0})
    camera_scene(comps,where/'camera_front_optics.png',
      'CAMERA FRONT / OPTICAL AXIS  |  NOMINAL ENVELOPE',
      'ESP32-CAM-MB is a simplified reference model; actual hardware fit pending',
      (-130,-60,90),(85,10,17),opacity={'4040_reference_extrusion':0})
    profile_figure()
    print('Renders written to',where)
if __name__=='__main__':main()
