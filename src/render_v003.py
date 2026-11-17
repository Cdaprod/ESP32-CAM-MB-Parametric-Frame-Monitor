#!/usr/bin/env python3
"""CAD-derived V003 preview set. Every pixel of geometry comes from VTK/BREP."""
from __future__ import annotations
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import render_assembly as renderer
from build_v003 import *

fontbold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fontplain='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def f(sz,bold=False):return ImageFont.truetype(fontbold if bold else fontplain,sz)

def annotate(where,title,subtitle):
    img=Image.open(where).convert('RGB')
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((38,30,1390,139),radius=16,fill=(18,35,49))
    d.text((64,43),title,font=f(29,True),fill=(248,250,253))
    d.text((64,101),subtitle,font=f(17),fill=(185,208,223))
    d.rounded_rectangle((40,1083,1720,1139),radius=12,fill=(19,35,47))
    d.text((60,1096),'V003 CAPTIVE RETAINER   •   ORIGINAL V002 PRESERVED   •   REAL CAD GEOMETRY   •   mm',
           font=f(17),fill=(227,235,242))
    img.save(where)

renderer.annotate=annotate

def scene(comps,file,title,subtitle,cam,look,hidden=None,exploded=False):
    renderer.camera_scene(comps,ROOT/'previews'/file,title,subtitle,cam,look,
                          opacity=hidden or {},explode=exploded)


def local_hardware(insert_offset=0,screw_offset=0):
    out=[]
    for sign,name in [(-1,'left'),(1,'right')]:
        x=sign*C.insert_x
        insert=insert_envelope().translate((x,C.insert_y,C.insert_top_z-C.insert_length+insert_offset))
        screw=cap_screw().translate((x,C.insert_y,C.cap_z_base+C.cap_thickness+screw_offset))
        out.extend([(f'brass_insert_{name}',insert,(0.86,0.65,.28),'hardware'),
                    (f'M2p5_socket_{name}',screw,(.73,.75,.8),'hardware')])
    return out


def local_group(explode=False,invert=False,old=False):
    if old:
        cr=upstream.v002_camera_cradle(V)
        comps=[('V002_unsecured_top',cr,(.13,.55,.70),'printed'),
               ('nominal_CAM_MB',upstream.board_envelope_v002(V),(.12,.44,.25),'reference')]
    else:
        cr,cap=new_parts_local()
        lift=12.0 if explode else 0
        comps=[('V003_captive_cradle',cr,(.08,.50,.66),'printed'),
               ('ESP32_CAM_MB_nominal_envelope',upstream.board_envelope_v002(V),(.10,.45,.23),'reference'),
               ('V003_removable_upper_bridge',cap.translate((0,0,lift)),(.97,.72,.22),'printed')]
        comps+=local_hardware(5.0 if explode else 0,21.0 if explode else 0)
    if invert:
        a=(0,-87,28);b=(1,-87,28)
        comps=[(name,s.rotate(a,b,180),col,kind) for name,s,col,kind in comps]
    return comps


def main():
    out=ROOT/'previews';out.mkdir(exist_ok=True)
    comps=assemble_components_v003()
    scene(comps,'assembled_oblique.png','V003  |  4040 FRAME + CAPTIVE CAMERA CRADLE',
        '23 positioned solids · bolted top bridge · 2 M2.5 inserts + 2 screws',
        (240,-180,160),(48,4,0))
    # Focus exclusively on the CAMERA for precision: hide rail/base and remote screws.
    hidden={n:0 for n,s,col,k in comps if n in {
       '4040_reference_extrusion','V5_profile_matched_key_M5_pilots'}}
    scene(comps,'captured_camera_closeup.png','V003  |  POSITIVE MECHANICAL CAPTURE',
        'Top bridge traps the PCB envelope · increased side lips · reinforced towers',
        (213,-110,112),(103,-20,30),hidden)
    scene(comps,'camera_front_and_retainer.png','CAMERA / RETAINER  |  FRONT OPTICS ACCESS',
        'Front lens zone stays open · no center-front upper strap',
        (195,73,108),(108,-16,31),hidden)
    scene(local_group(True),'exploded_retainer.png','REMOVABLE TOP RETAINER + INSERTS',
          'Separated for assembly illustration · M2.5 × 8 socket bolts · two insert seats',
          (107,-164,113),(0,-86,41))
    scene(local_group(invert=True),'upside_down_retention.png','UPSIDE-DOWN  |  NOMINAL BOARD IS CAPTIVE',
          'Local assembly rotated 180° as a demonstrator · retained via top bridge',
          (118,-164,85),(0,-86,28))
    scene(local_group(old=True),'v002_cradle_unsecured.png','V002  |  ORIGINAL OPEN-TOP CRADLE',
          'Unmodified reference · the nominal board could slide out along +Z',
          (105,-171,101),(0,-86,27))
    scene(local_group(),'v003_cradle_seated.png','V003  |  BOLTED ANTI-ESCAPE BRIDGE',
          '1.25 mm nominal top clearance · bridge obstructs +Z removal',
          (105,-171,101),(0,-86,27))
    # Side-by-side actual images. Source captures are saved separately too.
    originals=[Image.open(out/p).convert('RGB') for p in ('v002_cradle_unsecured.png','v003_cradle_seated.png')]
    w=originals[0].width
    composite=Image.new('RGB',(2*w,originals[0].height))
    for i,im in enumerate(originals):composite.paste(im,(i*w,0))
    composite.save(out/'v002_vs_v003_comparison.png')
    print('Rendered:',len(list(out.glob('*.png'))),'PNGs')

if __name__=='__main__':main()
