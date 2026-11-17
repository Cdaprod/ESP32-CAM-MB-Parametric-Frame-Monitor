#!/usr/bin/env python3
"""Export all 23 V003 model components to a colored GLB and offline HTML viewer."""
import math
import numpy as np
import trimesh
import plotly.graph_objects as go
from build_v003 import assemble_components_v003,ROOT

def main():
    components=assemble_components_v003()
    scene=trimesh.Scene(base_frame='4040_ESP32_CAM_MB_V003')
    meshes=[]
    for name,solid,color,kind in components:
        vv,ff=solid.tessellate(0.2,0.16)
        xyz=np.array([[p.x,p.y,p.z] for p in vv],dtype=np.float32)
        f=np.array(ff,dtype=np.int32)
        tr=trimesh.Trimesh(vertices=xyz,faces=f,process=False)
        tr.visual.vertex_colors=np.array([*tuple(round(c*255) for c in color),255],dtype=np.uint8)
        scene.add_geometry(tr,node_name=name,geom_name=name)
        stride=max(1,math.ceil(len(f)/6500));sub=f[::stride]
        meshes.append(go.Mesh3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],i=sub[:,0],j=sub[:,1],k=sub[:,2],
          name=name,color=f'rgb({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)})',
          flatshading=True,opacity=0.87 if name=='4040_reference_extrusion' else 1,
          hovertemplate=name+'<extra></extra>',lighting=dict(ambient=.65,diffuse=.82,specular=.17)))
    glb=ROOT/'viewer'/'COMPLETE_ASSEMBLY_V003.glb'
    scene.export(glb)
    fig=go.Figure(data=meshes)
    fig.update_layout(title=dict(text='ESP32-CAM-MB 4040 | V003 captive top retainer',x=.5),
      paper_bgcolor='#e9edf1',margin=dict(l=0,r=0,t=65,b=0),height=860,
      legend=dict(x=0,y=.97,bgcolor='rgba(255,255,255,.8)',font=dict(size=10)),
      scene=dict(aspectmode='data',bgcolor='#eef3f7',
       xaxis=dict(title='X (mm)',gridcolor='#c7d3de'),yaxis=dict(title='Y (mm)',gridcolor='#c7d3de'),
       zaxis=dict(title='Z (mm)',gridcolor='#c7d3de'),camera=dict(eye=dict(x=1.75,y=-1.5,z=1.08))))
    out=ROOT/'viewer'/'OPEN_V003_OFFLINE.html'
    fig.write_html(str(out),full_html=True,include_plotlyjs=True)
    text=out.read_text()
    assert '<script src="https://cdn.plot.ly' not in text
    print('GLB',glb.stat().st_size,'HTML',out.stat().st_size)
if __name__=='__main__':main()
