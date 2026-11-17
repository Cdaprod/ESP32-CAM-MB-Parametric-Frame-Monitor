"""Generate the current offline HTML and color-coded GLB from the canonical assembly.

Uses current config and assembled CAD solids; never imports a historical build.
Stable outputs: viewer/index.html, COMPLETE_ASSEMBLY.glb and release.json.
"""
from pathlib import Path
import hashlib, json, math, re
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import trimesh
from .assembly import components
from .config import CONFIG

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build_viewer(root):
    root = Path(root)
    out = root / "viewer"
    out.mkdir(parents=True, exist_ok=True)
    release = json.loads((root/"docs/CURRENT_RELEASE.json").read_text())
    version = CONFIG.release
    assert release["release"] == version
    parts = components()
    assert len(parts) == 30, "Expected the complete assembly"

    scene = trimesh.Scene(base_frame=f"ESP32_CAM_MB_{version}")
    traces, groups_seen = [], set()
    labels = {"reference":"Frame and references",
              "reference_cable":"Cable reference",
              "printed":"Printed parts", "hardware":"Metal hardware"}
    for name, shape, color, kind in parts:
        assert shape.isValid(), name
        vertices, triangles = shape.tessellate(.26, .18)
        v = np.asarray([(p.x,p.y,p.z) for p in vertices],dtype=np.float32)
        f = np.asarray(triangles,dtype=np.int32)
        assert len(v)>3 and len(f)>3
        mesh = trimesh.Trimesh(vertices=v,faces=f,process=False)
        rgba = np.array([*[round(float(c)*255) for c in color],255],dtype=np.uint8)
        mesh.visual.vertex_colors = np.tile(rgba,(len(v),1))
        scene.add_geometry(mesh,geom_name=name,node_name=name)
        # HTML viewing meshes decimated; GLB retains full CAD tessellation.
        stride=max(1,math.ceil(len(f)/2200))
        triangles_small=f[::stride]
        used, inv=np.unique(triangles_small.reshape(-1),return_inverse=True)
        vf=v[used]; ff=inv.reshape((-1,3))
        group=labels.get(kind,kind)
        rgb="rgb("+",".join(str(round(float(x)*255)) for x in color)+")"
        traces.append(go.Mesh3d(
            x=vf[:,0],y=vf[:,1],z=vf[:,2],
            i=ff[:,0],j=ff[:,1],k=ff[:,2],
            name=group,legendgroup=group,showlegend=group not in groups_seen,
            hovertemplate=name+"<extra></extra>",color=rgb,
            opacity=.68 if name=="ESP32_CAM_MB_provisional_envelope" else 1,
            lighting=dict(ambient=.62,diffuse=.76,specular=.17,roughness=.60)))
        groups_seen.add(group)
    glb=out/"COMPLETE_ASSEMBLY.glb"
    glb.write_bytes(scene.export(file_type="glb"))
    fig=go.Figure(data=traces)
    fig.update_layout(margin=dict(l=0,r=0,t=5,b=0),paper_bgcolor="#f0f3f6",
        scene=dict(aspectmode="data",dragmode="orbit",
                   camera=dict(eye=dict(x=1.65,y=-1.6,z=1.05)),
                   xaxis=dict(title="X (mm)"),yaxis=dict(title="Y (mm)"),
                   zaxis=dict(title="Z (mm)")),
        legend=dict(title="Tap a group to toggle",groupclick="togglegroup",
                    orientation="h",x=.02,y=.99,xanchor="left",yanchor="top"))
    html=pio.to_html(fig,include_plotlyjs=True,full_html=True,
        div_id="current-frame-monitor-viewer",default_width="100%",
        default_height="calc(100vh - 145px)",
        config={"responsive":True,"displaylogo":False,"scrollZoom":True})
    header=f'''<meta name="frame-monitor-release" content="{version}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{version} | ESP32-CAM-MB Interactive 3D Viewer</title>
<style>
html,body{{margin:0;padding:0;font-family:system-ui,sans-serif;background:#edf2f7}}
header{{padding:14px 20px;background:#122b3e;color:white}}
header h1{{font-size:clamp(16px,3vw,23px);margin:0 0 5px}}
header p{{font-size:12px;margin:0;color:#c9d7e3}}
.note{{padding:10px 20px;font-size:12px;background:#fff;border-top:1px solid #d5e0e8}}
</style>'''
    banner=(f'<header><h1>{version} · ESP32-CAM-MB · Interactive CAD Viewer</h1>'
            f'<p>{len(parts)} components · Horizontal 4040 · Four joints · '
            f'Four integrated cable clips · millimeters</p></header>')
    footer=('<div class="note"><b>Controls:</b> drag to orbit · pinch/scroll '
            'to zoom · click legend to show/hide groups. Fully offline. '
            '<b>CAD reference only:</b> physical fit and loads unverified.</div>')
    html=html.replace("</head>",header+"</head>",1)
    html=html.replace("<body>","<body>"+banner,1)
    html=html.replace("</body>",footer+"</body>",1)
    viewer=out/"index.html"
    viewer.write_text(html,encoding="utf-8")
    assert "Plotly.newPlot" in html
    assert not re.search(r'<script[^>]+src=["\x27]https?://',html,re.I)
    previews=release["previews"]
    for p in previews: assert (root/p).is_file(),p
    step=root/release["assembly_step"]
    assert step.is_file(),"STEP must be built before viewer"
    meta={"release":version,"canonical_viewer":"viewer/index.html",
          "viewer_glb":"viewer/COMPLETE_ASSEMBLY.glb",
          "source":"src/frame_monitor/assembly.py::components",
          "part_count":len(parts),"component_names":[n for n,*_ in parts],
          "fully_offline":True,"standalone_html":True,
          "previews_sha256":{p:sha(root/p) for p in previews},
          "assembly_step":release["assembly_step"],
          "assembly_step_sha256":sha(step),
          "html_sha256":sha(viewer),"glb_sha256":sha(glb),
          "status":"CAD reference only; physical load and fit unverified"}
    (out/"release.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(f"Generated current {version} 3D viewer, {len(parts)} components")
    return meta
