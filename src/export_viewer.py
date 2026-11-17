#!/usr/bin/env python3
"""Export colored glTF/GLB and a 100% offline Plotly HTML 3D viewer."""
import math
from pathlib import Path
import numpy as np
import trimesh
import plotly.graph_objects as go
from build_assembly import assemble_components, ROOT

def main():
    components=assemble_components()
    scene=trimesh.Scene(base_frame='4040_ESP32_CAM_MB')
    traces=[]
    for name,solid,color,kind in components:
        vv,ff=solid.tessellate(0.20,0.16)
        vertices=np.array([(p.x,p.y,p.z) for p in vv],dtype=np.float32)
        faces=np.array(ff,dtype=np.int32)
        tm=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
        tm.visual.vertex_colors=np.array([*tuple(round(v*255) for v in color),255],dtype=np.uint8)
        scene.add_geometry(tm,node_name=name,geom_name=name)
        # Large fixtures and hardware are decimated by sampling triangles for the offline viewer
        # ONLY; the GLB/STEP and original geometry remain unsimplified.
        step=max(1,math.ceil(len(faces)/7500))
        sub=faces[::step]
        rgb=f'rgb({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)})'
        traces.append(go.Mesh3d(x=vertices[:,0],y=vertices[:,1],z=vertices[:,2],
            i=sub[:,0],j=sub[:,1],k=sub[:,2],name=name,
            color=rgb,opacity=1.0,flatshading=True,lighting=dict(ambient=.63,diffuse=.8,specular=.19,roughness=.42),
            hovertemplate=name+'<extra></extra>'))
        print(name,len(faces))
    scene.export(ROOT/'viewer'/'COMPLETE_ASSEMBLY.glb')
    fig=go.Figure(data=traces)
    fig.update_layout(
      title={'text':'4040 + V5 T-slot + ESP32-CAM-MB | Parametric Frame Monitor V002', 'x':.5},
      scene=dict(
        xaxis=dict(title='X (mm)',showbackground=False,gridcolor='#d0d8e0'),
        yaxis=dict(title='Y (mm)',showbackground=False,gridcolor='#d0d8e0'),
        zaxis=dict(title='Z (mm)',showbackground=False,gridcolor='#d0d8e0'),
        aspectmode='data',
        camera=dict(eye=dict(x=1.8,y=-1.7,z=1.2)),
        bgcolor='#ecf1f5'),
      margin=dict(l=0,r=0,t=65,b=0),
      paper_bgcolor='#edf1f5',
      legend=dict(x=0,y=.96,font=dict(size=10),bgcolor='rgba(255,255,255,.85)'),
      height=840,
    )
    outfile=ROOT/'viewer'/'OPEN_IN_BROWSER_OFFLINE.html'
    fig.write_html(outfile,include_plotlyjs=True,full_html=True)
    text=outfile.read_text()
    assert 'plotly.js v' in text.lower() or 'plotly.js' in text.lower()
    assert '<script src="https://cdn.plot.ly' not in text
    print('Viewer:',outfile,round(outfile.stat().st_size/1e6,2),'MB')
    print('GLB:', (ROOT/'viewer'/'COMPLETE_ASSEMBLY.glb').stat().st_size)
if __name__=='__main__':main()
