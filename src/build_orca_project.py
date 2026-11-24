"""Build a native, arranged Orca project from the active printed-part BOM.

Uses installed profiles without modifying them. Never uploads or starts a print.
Run with the repository Python environment; OrcaSlicer must be installed.
"""
import json
from collections import Counter
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    ('V010_first_arm', 1), ('V010_second_arm', 1),
    ('V010_scalloped_thumbwheel', 4), ('V010_relieved_camera_shell', 1),
    ('V010_wrist_adapter', 1), ('V004_removable_camera_bezel', 1),
    ('V010_mount_plate', 1), ('V004_recessed_alignment_key', 1),
]
OUTPUT = ROOT / 'orca' / 'V010_printed_parts.3mf'


def installed_profiles():
    base = Path.home() / 'Library/Application Support/OrcaSlicer'
    if not base.is_dir():
        base = Path.home() / '.config/OrcaSlicer'
    profiles = {}
    for folder in ('system', 'user'):
        for path in (base / folder).rglob('*.json'):
            try:
                data = json.loads(path.read_text())
                profiles[data.get('name', path.stem)] = data
            except (ValueError, UnicodeError):
                continue

    def resolve(name, chain=()):
        if name in chain:
            raise ValueError(f'Circular profile inheritance: {name}')
        data = profiles[name]
        result = resolve(data['inherits'], chain + (name,)) if data.get('inherits') else {}
        result.update(data)
        result.pop('inherits', None)
        # No device connection credentials belong in a shareable print project.
        for key in list(result):
            if any(token in key.lower() for token in ('api_key', 'password', 'print_host', 'printhost')):
                result.pop(key)
        return result
    return resolve


def verify_project(path):
    """Check native settings, individual build items and actual transformed bounds."""
    import numpy as np
    import trimesh
    with zipfile.ZipFile(path) as archive:
        assert 'Metadata/project_settings.config' in archive.namelist()
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        # Guard against accidentally reintroducing a profile's aggressive
        # travel acceleration.  Orca expects these values in mm/s².
        def scalar(key):
            value = settings[key]
            return float(value[0] if isinstance(value, list) else value)
        assert scalar('travel_acceleration') <= scalar('machine_max_acceleration_travel')
        assert scalar('default_acceleration') <= scalar('machine_max_acceleration_extruding')
        model = ET.fromstring(archive.read('3D/3dmodel.model'))
        ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
        volume_names={}
        for filename in archive.namelist():
            if filename.startswith('3D/Objects/') and filename.endswith('.model'):
                part_name=Path(filename).name.split('.stl')[0]
                external=ET.fromstring(archive.read(filename))
                for obj in external.findall('m:resources/m:object',ns):
                    volume_names[obj.get('id')]=part_name
        items = model.findall('m:build/m:item', ns)
        assert len(items) == sum(qty for _, qty in PARTS), len(items)
    scene = trimesh.load(path, force='scene')
    from shapely.geometry import MultiPoint
    bounds = []
    footprints = []
    names=[]
    for node in scene.graph.nodes_geometry:
        transform, geometry = scene.graph[node]
        mesh = scene.geometry[geometry].copy()
        # The 3MF loader repeats shared-volume faces for cloned build items.
        mesh.process(validate=True)
        mesh.apply_transform(transform)
        assert mesh.is_watertight and mesh.is_volume, node
        name=volume_names[str(node).split('_')[0]]
        source=trimesh.load(ROOT / 'stl' / f'{name}.stl',force='mesh')
        assert abs(mesh.volume/source.volume-1)<.0005,(name,'Stale project mesh')
        names.append(name)
        low, high = mesh.bounds
        assert abs(low[2]) < .02, (node, 'not grounded', low)
        assert np.all(low[:2] >= 5) and np.all(high[:2] <= 230), (node, 'outside bed margin')
        bounds.append((low, high))
        footprints.append(MultiPoint(mesh.vertices[:, :2]).convex_hull)
    assert Counter(names)==Counter(dict(PARTS)),names
    assert len(bounds) == 11, len(bounds)
    heights=sorted(round(float(high[2]-low[2]),2) for low,high in bounds)
    expected=sorted([36,22.2,14,26,7.5,3,5.97,7,7,7,7])
    assert np.allclose(heights,expected,atol=.03),('Print orientation changed',heights)

    minimum = min(a.distance(b) for i,a in enumerate(footprints) for b in footprints[i+1:])
    assert minimum >= 5.9, ('Insufficient part spacing', minimum)
    print(f'Verified {len(bounds)} independent grounded objects; minimum projected-hull gap {minimum:.2f} mm')


def build():
    executable = os.environ.get('ORCASLICER_PATH', '/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer')
    assert Path(executable).is_file(), executable
    OUTPUT.parent.mkdir(exist_ok=True)
    resolve = installed_profiles()
    with tempfile.TemporaryDirectory(prefix='frame-monitor-orca-') as temporary:
        temporary = Path(temporary)
        settings = []
        for kind, name in [('machine', 'Elegoo Neptune 2 0.4 nozzle - Copy'),
                           ('process', 'Elegoo Neptune 2 0.20 mm Balanced'),
                           ('filament', 'Panchroma PLA Matte - Neptune 2')]:
            data = resolve(name)
            if kind == 'process':
                data.update(wall_loops='5', sparse_infill_density='40%',
                            enable_support='1', support_type='normal(auto)',
                            support_on_build_plate_only='0', brim_type='no_brim',
                            duplicate_distance='8',
                            # Keep every generated motion command within the
                            # Neptune 2's 1000 mm/s² machine limit.  The
                            # inherited profile used 10000 for travel, which
                            # makes Orca warn about excessive acceleration.
                            default_acceleration=['500'],
                            initial_layer_acceleration=['300'],
                            initial_layer_travel_acceleration=['500'],
                            outer_wall_acceleration=['300'],
                            inner_wall_acceleration=['500'],
                            sparse_infill_acceleration=['500'],
                            internal_solid_infill_acceleration=['500'],
                            top_surface_acceleration=['300'],
                            bridge_acceleration=['300'],
                            travel_acceleration=['800'],
                            machine_max_acceleration_e=['1000', '1000'],
                            machine_max_acceleration_extruding=['1000', '1000'],
                            machine_max_acceleration_retracting=['1000', '1000'],
                            machine_max_acceleration_travel=['1000', '1000'],
                            machine_max_acceleration_x=['1000', '1000'],
                            machine_max_acceleration_y=['1000', '1000'],
                            machine_max_acceleration_z=['1000', '1000'])
            path = temporary / f'{kind}.json'
            path.write_text(json.dumps(data))
            settings.append(str(path))
        command = [executable, '--load-settings', ';'.join(settings[:2]),
                   '--load-filaments', settings[2], '--load-defaultfila',
                   '--clone-objects', ','.join(str(qty) for _, qty in PARTS),
                   '--orient', '0', '--arrange', '1',
                   '--allow-rotations', '--ensure-on-bed',
                   '--export-3mf', str(OUTPUT)]
        # Explicit axes, rather than convex-hull auto-orientation: put the
        # shell and pitch/wrist ears on a side so their load paths lie in XY.
        import trimesh
        import numpy as np
        oriented=[]
        rotations={
            'V010_relieved_camera_shell':(0,-90,0),
            'V010_second_arm':(0,90,0),
            'V010_wrist_adapter':(0,90,0),
            'V010_mount_plate':(-90,0,0),
            'V004_removable_camera_bezel':(90,0,0),
            'V004_recessed_alignment_key':(0,-90,0),
        }
        for name,_ in PARTS:
            mesh=trimesh.load(ROOT / 'stl' / f'{name}.stl',force='mesh')
            angles=np.radians(rotations.get(name,(0,0,0)))
            mesh.apply_transform(trimesh.transformations.euler_matrix(*angles))
            mesh.apply_translation(-mesh.bounds[0])
            path=temporary / f'{name}.stl'
            mesh.export(path)
            oriented.append(str(path))
        command.extend(oriented)
        subprocess.run(command, check=True, timeout=180)
    verify_project(OUTPUT)
    print(OUTPUT)


if __name__ == '__main__':
    build()
