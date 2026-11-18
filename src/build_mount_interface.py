#!/usr/bin/env python3
"""Rebuild the parametric 2020/4040 bracket family, STEP/STL, real PNGs and offline HTML."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
import numpy as np
import trimesh
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image,ImageDraw,ImageFont
from frame_monitor.mount_interface import (
    PRESETS,bracket,reference_extrusion,tnut_reference,screw_reference,feature_manifest)

ROOT=Path(__file__).resolve().parents[1]
NAMES=('2020_single_2xM5','4040_dual_4xM5','4040_dual_8xM5')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def models(s,with_rail=True,hardware=True):
    out=[]
    if with_rail:out.append(('Nominal extrusion / NOT printed',
                   reference_extrusion(s),(.56,.62,.70),'reference'))
    out.append(('One-piece printed bracket',bracket(s),(.98,.38,.14),'printed'))
    if hardware:
        out.extend((f'M5 metal T-nut {i}',n,(.65,.70,.73),'hardware')
                   for i,n in enumerate(tnut_reference(s),1))
        out.extend((f'M5 screw {i}',n,(.35,.40,.46),'hardware')
                   for i,n in enumerate(screw_reference(s),1))
    return out

def render_image(path,parts,title,description,camera,scale='default'):
    """Direct VTK render of actual tessellated BREP models, never generated art."""
    from frame_monitor import vtk_renderer as v
    def annotate(where,title,subtitle):
        im=Image.open(where).convert('RGB')
        draw=ImageDraw.Draw(im)
        font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        draw.rounded_rectangle((30,28,1720,148),radius=14,fill='#122b3e')
        draw.text((55,46),title,font=ImageFont.truetype(bold,30),fill='white')
        draw.text((55,109),subtitle,font=ImageFont.truetype(font,17),fill='#d4e5f0')
        draw.rounded_rectangle((30,1080,1730,1140),radius=10,fill='#122b3e')
        draw.text((53,1099),'REAL CAD | V5 PHOTO-DERIVED SLOT | NOMINAL FIT; PHYSICAL QUALIFICATION PENDING',
                  font=ImageFont.truetype(font,17),fill='white')
        im.save(where)
    v.annotate=annotate
    # 'ASSEMBLY' selects the wider VTK orthographic field for long rail variants.
    name='ASSEMBLY | '+title
    v.camera_scene(parts,path,name,description,camera,(0,0,0),
        opacity={'Nominal extrusion / NOT printed':.23})
    if not path.is_file():raise RuntimeError('Missing actual CAD preview: '+str(path))

def viewer(root):
    traces=[];choices=[];metadata={}
    for index,name in enumerate(NAMES):
        s=PRESETS[name]
        start=len(traces)
        for part,shape,color,kind in models(s):
            vertices,faces=shape.tessellate(.28,.18)
            v=np.asarray([p.toTuple() for p in vertices],dtype=np.float32)
            f=np.asarray(faces,dtype=np.int32)
            traces.append(go.Mesh3d(x=v[:,0],y=v[:,1],z=v[:,2],
                i=f[:,0],j=f[:,1],k=f[:,2],
                name=part,legendgroup=name,showlegend=(kind in ('reference','printed')),
                visible=(index==1),opacity=.35 if kind=='reference' else 1,
                color='rgb('+','.join(str(round(c*255)) for c in color)+')',
                hovertemplate=name+' | '+part+'<extra></extra>'))
        choices.append((start,len(traces)))
        metadata[name]=feature_manifest(s)
    buttons=[]
    for i,name in enumerate(NAMES):
        a,b=choices[i]
        buttons.append(dict(label=name.replace('_',' '),method='update',
            args=[{'visible':[a<=j<b for j in range(len(traces))]},
                  {'title':name.replace('_',' ')}]))
    figure=go.Figure(data=traces)
    figure.update_layout(title='Parametric 4040 dual-slot mounting bracket',
        paper_bgcolor='#edf2f7',margin=dict(l=0,r=0,t=80,b=0),
        scene=dict(aspectmode='data',
           xaxis=dict(title='X across face (mm)'),yaxis=dict(title='Y depth (mm)'),
           zaxis=dict(title='Z length (mm)'),
           camera=dict(eye=dict(x=1.6,y=-2,z=1.4))),
        updatemenus=[dict(buttons=buttons,x=.02,y=1.14,direction='down')],
        legend=dict(orientation='h',x=.02,y=1.02))
    html=pio.to_html(figure,include_plotlyjs=True,full_html=True,
       default_height='calc(100vh - 120px)',default_width='100%',
       config=dict(responsive=True,displaylogo=False,scrollZoom=True))
    html=html.replace('</head>',"<meta name='viewport' content='width=device-width,initial-scale=1'>"
         "<style>html,body{margin:0;background:#edf2f7;font-family:system-ui}"
         "header{background:#122b3e;color:#fff;padding:14px}"
         "header h1{font-size:22px;margin:0}"
         "header p{font-size:12px;color:#c7d9e5}</style></head>",1)
    html=html.replace('<body>',"<body><header><h1>Parametric 2020 / 4040 mounting interface</h1>"
         "<p>Choose a configuration. Orange bracket is printable; extrusion and hardware are reference only. CAD-only fit.</p></header>",1)
    path=root/'viewer'/'mount_interface.html'
    path.write_text(html,encoding='utf-8')
    info={'html':'viewer/mount_interface.html','html_sha256':sha(path),
          'fully_offline':True,'variants':metadata,
          'status':'Nominal geometry; 2020/4040 actual fit and printed strength UNVERIFIED'}
    (root/'viewer'/'mount_interface_release.json').write_text(json.dumps(info,indent=2)+'\n')
    return info

def build_suite(root=ROOT):
    root=Path(root)
    for folder in ('step','stl','previews','viewer','docs'):
        (root/folder).mkdir(exist_ok=True,parents=True)
    manifest={'feature':'Integrated locating tongues + metal M5 clamps; old V5 loose key excluded',
              'generator':'src/build_mount_interface.py','units':'mm','variants':{},
              'previews':[],'status':'CAD-only fit, not physically qualified'}
    for name in NAMES:
        s=PRESETS[name]
        solid=bracket(s)
        stem='MOUNT_'+name
        stl=root/'stl'/(stem+'.stl')
        step=root/'step'/(stem+'.step')
        cq.exporters.export(solid,str(step))
        cq.exporters.export(solid,str(stl),tolerance=.08,angularTolerance=.12)
        mesh=trimesh.load_mesh(stl,force='mesh')
        if not (mesh.is_watertight and mesh.is_volume and mesh.body_count==1):
            raise ValueError('Not a watertight single solid: '+name)
        if abs(mesh.volume/solid.Volume()-1)>.006:raise ValueError('STL volume mismatch')
        if solid.intersect(reference_extrusion(s)).Volume()>.01:
            raise ValueError('Bracket enters extrusion solid: '+name)
        if any(solid.intersect(n).Volume()>.01 for n in tnut_reference(s)):
            raise ValueError('T-nut and locating tongue collide: '+name)
        manifest['variants'][name]={**feature_manifest(s),'step':'step/'+step.name,
                       'stl':'stl/'+stl.name,'watertight':True,
                       'mesh_volume_mm3':round(mesh.volume,2)}
    for name in NAMES:
        s=PRESETS[name]
        path=root/'previews'/('mount_'+name+'.png')
        render_image(path,models(s),
           f'{s.extrusion_size_mm}{s.extrusion_size_mm} | {s.channel_count} slot(s) | {len(s.hole_centers_mm)} M5 screws',
           f'{s.plate_width_mm:g} x {s.plate_length_mm:g} x {s.plate_thickness_mm:g} mm | integral ribs, 0.18 mm fit clearance',
           (220,-190,170))
        manifest['previews'].append('previews/'+path.name)
    s=PRESETS['4040_dual_4xM5']
    path=root/'previews'/'mount_4040_tongue_detail.png'
    render_image(path,models(s,with_rail=False,hardware=False),
       'INTEGRAL INDEXING TONGUES | TWO 4040 SLOTS',
       'Ribs remain BETWEEN M5 T-nut stations; old loose V5 key omitted',
       (130,170,120))
    manifest['previews'].append('previews/'+path.name)
    meta=viewer(root)
    manifest['viewer']=meta['html']
    manifest['preview_sha256']={p:sha(root/p) for p in manifest['previews']}
    (root/'docs'/'mount_interface_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('PASS 2020 / 4040 parametric bracket family, real CAD models, previews and offline viewer')
    return manifest

if __name__=='__main__':
    build_suite(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
